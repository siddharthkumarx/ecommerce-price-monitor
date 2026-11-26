"""Canary for new stores: a store counts in public numbers only after 3 clean days in a row.

A store is **counted** once it has rows in the last good snapshot: the original
stores, and every store promoted since. Any other store in ``config/stores.yml`` is
**warming up**: the daily run fetches and checks it like every store, but its rows
stay out of the snapshot, change log, history, feed, README and dashboard, and its
problems never make a run partial or held. Each run records the result per warming
store in ``runs.jsonl`` (``warming``: store id, clean yes/no and why, rows) and the
state in ``data/warmup.json`` (internal).

A warming store's day is **clean** when its fetch finished completely (status
``ok``: robots allowed, second source matched, USD proven, content screen passed),
needed no retry on HTTP 429, validation rejected at most 2 % of its rows, and its
row count did not fall by more than half since its previous warming day.

On the run that completes 3 clean UTC days in a row (consecutive dates, today
included), the store is promoted: its rows enter the snapshot as a **baseline**
(no ``new`` events in the change log, like the monitor's first run) and it counts
from then on. A failed or unclean day resets the count.
"""

from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path
from typing import Any

WARMUP_DAYS = 3
REJECT_SHARE = 0.02
ROWS_DROP = 0.50


@dataclass(frozen=True)
class WarmDay:
    store_id: str
    clean: bool
    rows: int
    why: str = ""

    def record(self) -> dict[str, Any]:
        return {"store_id": self.store_id, "clean": self.clean, "rows": self.rows, "why": self.why}


def split(store_ids: list[str], counted_in_snapshot: set[str]) -> tuple[list[str], list[str]]:
    """(counted, warming) in stores.yml order.

    With an empty snapshot (the monitor's first run) every store is the baseline.
    """
    if not counted_in_snapshot:
        return list(store_ids), []
    counted = [s for s in store_ids if s in counted_in_snapshot]
    return counted, [s for s in store_ids if s not in counted_in_snapshot]


def last_rows(store_id: str, runs: list[dict[str, Any]]) -> int | None:
    for r in reversed(runs):
        for w in r.get("warming") or []:
            if w.get("store_id") == store_id and w.get("rows"):
                return int(w["rows"])
    return None


def judge(
    store_id: str,
    status: str,
    reason: str | None,
    rows: int,
    rejected: int,
    retry_causes: list[str],
    currencies: set[str],
    runs: list[dict[str, Any]],
) -> WarmDay:
    """Was today clean for a warming store?"""
    why: list[str] = []
    if status != "ok":
        why.append(f"{status}: {reason or 'not complete'}")
    if any(c.startswith("http 429") for c in retry_causes):
        why.append("needed a retry on 429")
    seen = rows + rejected
    if seen and rejected / seen > REJECT_SHARE:
        why.append(f"validation rejected {rejected} of {seen} rows")
    if status == "ok" and not rows:
        why.append("no rows")
    if status == "ok" and currencies and currencies != {"USD"}:
        why.append(f"currency {sorted(currencies)}")
    before = last_rows(store_id, runs)
    if before and rows < before * (1 - ROWS_DROP):
        why.append(f"rows fell from {before} to {rows}")
    return WarmDay(store_id, not why, rows, "; ".join(why))


def streak(store_id: str, runs: list[dict[str, Any]], today: date, today_clean: bool) -> int:
    """Clean UTC days in a row for ``store_id``, ending today (0 if today is not clean).

    A date counts as clean when every warming record of the store on that date is
    clean; a date with no record (no run, or the store not yet listed) breaks the run.
    """
    by_date: dict[str, bool] = {}
    for r in runs:
        for w in r.get("warming") or []:
            if w.get("store_id") == store_id:
                d = str(r["started_at"])[:10]
                by_date[d] = by_date.get(d, True) and bool(w.get("clean"))
    key = today.isoformat()
    by_date[key] = by_date.get(key, True) and today_clean
    n, day = 0, today
    while by_date.get(day.isoformat()):
        n += 1
        day -= timedelta(days=1)
    return n


def write_state(data: Path, state: dict[str, Any]) -> Path:
    out = data / "warmup.json"
    out.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return out


def counted_ids(data: Path) -> set[str]:
    """Stores with rows in the last good snapshot: the ones in public numbers.

    The same rule the run uses (:func:`split`); it holds before the first run with
    this module too, when ``data/warmup.json`` does not exist yet.
    """
    snapshot = data / "latest" / "snapshot.csv"
    if not snapshot.exists():
        return set()
    with snapshot.open(newline="", encoding="utf-8") as fh:
        return {row["store_id"] for row in csv.DictReader(fh)}


def public_stores(stores: list[Any], data: Path) -> list[Any]:
    """The stores that count in public numbers (warming-up stores left out).

    With an empty snapshot (before the monitor's first run) every store counts.
    """
    counted = counted_ids(data)
    if not counted:
        return list(stores)
    return [s for s in stores if s.id in counted]
