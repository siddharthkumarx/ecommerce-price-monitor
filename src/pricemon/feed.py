"""The public feed, ``data/public/feed.json`` (schema ``steadydata.feed/v1``).

    python -m pricemon.feed [--data data] [--stores config/stores.yml]

A small, stable summary of the monitor for other sites to read: what is
monitored, the latest good run, what its checks did, totals, up to 60 days of
change counts, and the delivery record since 5 Nov 2026 (``delivery``). The full
daily history, kept forever, is ``data/public/history.json`` (``history_url``).
Stores still warming up (:mod:`pricemon.warmup`) are not in any number here.
It is built only from committed run outputs (``data/runs.jsonl``,
``data/status.json``) and ``config/stores.yml``, and it never contains product
names or prices.

The daily pipeline rewrites it atomically at the end of every ok or partial run.
A held or crashed run never writes it, so its ``generated_at`` age shows how stale
the published data is. Field definitions: the dataset card, ``data/README.md``.

Contract: fields may be added, never removed or renamed.
"""

from __future__ import annotations

import argparse
import json
import os
import tempfile
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml

from pricemon.outputs import build_status, iso, read_runs
from pricemon.stores import CATEGORY_TITLES, PLATFORM_TITLES, load_stores
from pricemon.summary import delivery, read_summary

SCHEMA = "steadydata.feed/v1"
MONITOR_ID = "ecommerce-price-monitor"
DAILY_DAYS = 60
MAX_BYTES = 30_000
GOOD = ("ok", "partial")
# The order of the contract's daily rows.
DAILY_EVENTS = (
    "price_down",
    "price_up",
    "discount_start",
    "discount_end",
    "out_of_stock",
    "back_in_stock",
    "new",
    "removed",
)
ROOT = Path(__file__).resolve().parents[2]


def checks(run: dict[str, Any]) -> dict[str, Any]:
    """What validation, the batch guard and the second-source re-reads did in ``run``.

    - ``rows_validated``: catalog rows checked by row validation (accepted + rejected).
    - ``rows_rejected``: rows that broke a validation rule and were set aside.
    - ``held_back``: rows read but not published because a check stopped them: the
      rows of stores whose ``.js`` re-read disagreed with ``/products.json``, plus
      every row of a run the batch guard held.
    - ``second_source_checks``: re-reads of the daily sample product that were
      compared with ``/products.json`` (one ``.js`` re-read and one product-page
      JSON-LD re-read per store; a page without offers is not a comparison).
    - ``second_source_matches``: those comparisons that agreed exactly.
    """
    stores = run.get("stores") or []
    witnesses = [w for s in stores for w in s.get("witnesses") or []]
    js_checked = sum(1 for w in witnesses if w.get("js") in ("match", "mismatch"))
    js_matches = sum(1 for w in witnesses if w.get("js") == "match")
    ld_checked = sum(1 for w in witnesses if w.get("jsonld") in ("match", "mismatch"))
    ld_matches = sum(1 for w in witnesses if w.get("jsonld") == "match")
    held_back = sum(int(s.get("variants") or 0) for s in stores if s.get("status") == "mismatch")
    if run.get("status") == "held":
        held_back += int(run.get("rows_observed") or 0)
    guard = run.get("guard") or {}
    rows_observed = int(run.get("rows_observed") or 0)
    rows_rejected = int(run.get("rows_rejected") or 0)
    return {
        "rows_validated": rows_observed + rows_rejected,
        "rows_rejected": rows_rejected,
        "held_back": held_back,
        "second_source_checks": js_checked + ld_checked,
        "second_source_matches": js_matches + ld_matches,
        "second_source": {
            "js_checked": js_checked,
            "js_matches": js_matches,
            "jsonld_checked": ld_checked,
            "jsonld_matches": ld_matches,
        },
        "rows_compared_with_last_run": int(guard.get("matched") or 0),
        "suspicious_price_moves": int(guard.get("suspicious") or 0),
        "guard_holds": len(guard.get("holds") or []),
    }


def daily(runs: list[dict[str, Any]], days: int = DAILY_DAYS) -> list[dict[str, Any]]:
    """Change counts per UTC date of good runs, oldest first, the baseline run excluded.

    The baseline is the first good run: it records every row as ``new``, which is a
    starting point, not a change. Several good runs on one date are summed;
    ``rows_live`` is that of the date's last good run.
    """
    good = [r for r in runs if r.get("status") in GOOD]
    by_date: dict[str, dict[str, Any]] = {}
    for r in good[1:]:
        date = str(r["started_at"])[:10]
        row = by_date.setdefault(
            date, {"date": date, "runs": 0, "rows_live": 0, **dict.fromkeys(DAILY_EVENTS, 0)}
        )
        row["runs"] += 1
        row["rows_live"] = int(r.get("rows_live") or 0)
        events = r.get("events") or {}
        for key in DAILY_EVENTS:
            row[key] += int(events.get(key) or 0)
    return [by_date[d] for d in sorted(by_date)][-days:]


def _schedule(sched: dict[str, Any]) -> dict[str, Any]:
    """Delivery for every slot; the on-time count only from the on-time trigger's first slot.

    All-time on-time counts stay in status.json: before the trigger, GitHub's late
    scheduler decided them (INC-009), so they are not a percentage to show.
    """
    since = sched.get("since") or {}
    return {
        "slots": int(sched.get("slots") or 0),
        "delivered": int(sched.get("delivered") or 0),
        "missed": int(sched.get("missed") or 0),
        "on_time_window_h": int(sched.get("on_time_window_h") or 2),
        "on_time_since": sched.get("on_time_since"),
        "on_time_slots": int(since.get("slots") or 0),
        "on_time": int(since.get("on_time") or 0),
        "on_time_pct": sched.get("on_time_pct"),
        "note": sched.get("note") or "",
    }


def _public(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    loaded = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return dict(loaded)


def build_feed(
    runs: list[dict[str, Any]],
    status: dict[str, Any],
    now: datetime,
    stores_path: Path | None = None,
    public_path: Path | None = None,
    summary_rows: list[dict[str, Any]] | None = None,
) -> dict[str, Any] | None:
    """The feed, or None when there is no good run yet."""
    good = [r for r in runs if r.get("status") in GOOD]
    if not good:
        return None
    last = good[-1]
    stores_path = stores_path or ROOT / "config" / "stores.yml"
    stores = load_stores(stores_path) if stores_path.exists() else []
    # Warming-up stores are internal: only counted stores are described.
    warming = {w.get("store_id") for w in last.get("warming") or [] if not w.get("promoted")}
    stores = [s for s in stores if s.id not in warming]
    pub = _public(public_path or ROOT / "config" / "public.yml")
    repo = pub.get("repo", f"siddharthkumarx/{MONITOR_ID}")
    branch = pub.get("branch", "main")
    stores_total = int(last.get("stores_total") or 0) or len(stores)
    category_ids = sorted({s.category for s in stores})
    return {
        "schema": SCHEMA,
        "generated_at": iso(now),
        "monitor": {
            "id": MONITOR_ID,
            "title": f"Daily price monitor, {stores_total} US online stores",
            "repo": f"https://github.com/{repo}",
            "dashboard": pub.get("dashboard", ""),
            "first_run": status.get("first_run") or good[0]["started_at"],
            "stores_total": stores_total,
            "categories": [CATEGORY_TITLES.get(c, c) for c in category_ids],
            "category_ids": category_ids,
            "platforms": [
                PLATFORM_TITLES[p] for p in PLATFORM_TITLES if p in {s.platform for s in stores}
            ],
            "cadence": "daily at 06:17 UTC",
        },
        "last_run": {
            "run_id": last["run_id"],
            "started_at": last["started_at"],
            "finished_at": last.get("finished_at") or last["started_at"],
            "status": last["status"],
            "stores_ok": int(last.get("stores_ok") or 0),
            "stores_total": int(last.get("stores_total") or 0),
            "rows_live": int(last.get("rows_live") or 0),
            "run_url": last.get("run_url") or "",
        },
        "checks": checks(last),
        "totals": {
            "days_running": int(status.get("days_running") or 0),
            "runs_total": int(status.get("runs_total") or len(runs)),
            "runs_good": int(status.get("runs_good") or len(good)),
            "runs_held": int(status.get("runs_held") or 0),
        },
        "schedule": _schedule(status.get("schedule") or {}),
        "delivery": delivery(summary_rows or [], status),
        "history_url": (
            f"https://raw.githubusercontent.com/{repo}/{branch}/data/public/history.json"
        ),
        "daily": daily(runs),
    }


def dumps(feed: dict[str, Any]) -> str:
    """Readable JSON with one line per daily row (keeps 60 days well under 30 KB)."""
    rows = feed.get("daily") or []
    head = json.dumps({**feed, "daily": []}, indent=2, ensure_ascii=False)
    if not rows:
        return head + "\n"
    body = ",\n".join("    " + json.dumps(r, separators=(",", ":")) for r in rows)
    return head.replace('"daily": []', '"daily": [\n' + body + "\n  ]") + "\n"


def write_feed(data: Path, feed: dict[str, Any]) -> Path:
    """Write ``data/public/feed.json`` atomically (temp file in the same folder, rename)."""
    text = dumps(feed)
    if len(text.encode("utf-8")) > MAX_BYTES:
        raise ValueError(f"feed is {len(text.encode())} bytes, over {MAX_BYTES}")
    out = data / "public" / "feed.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=".feed-", suffix=".json", dir=out.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            fh.write(text)
            fh.flush()
            os.fsync(fh.fileno())
        Path(tmp).chmod(0o644)
        Path(tmp).replace(out)
    except BaseException:
        Path(tmp).unlink(missing_ok=True)
        raise
    return out


def publish(
    data: Path,
    now: datetime,
    stores_path: Path | None = None,
    public_path: Path | None = None,
) -> Path | None:
    """Build the feed from ``data/`` and write it; None when there is nothing to publish."""
    runs = read_runs(data)
    status_file = data / "status.json"
    status = (
        json.loads(status_file.read_text(encoding="utf-8"))
        if status_file.exists()
        else build_status(runs, now)
    )
    rows = list(read_summary(data / "history" / "daily-summary.csv").values())
    feed = build_feed(runs, status, now, stores_path, public_path, rows)
    return write_feed(data, feed) if feed else None


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
    p.add_argument("--data", type=Path, default=ROOT / "data")
    p.add_argument("--stores", type=Path, default=ROOT / "config" / "stores.yml")
    p.add_argument("--public", type=Path, default=ROOT / "config" / "public.yml")
    a = p.parse_args(argv)
    out = publish(a.data, datetime.now(UTC).replace(microsecond=0), a.stores, a.public)
    print(out or "no good run yet: feed not written")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
