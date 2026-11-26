"""The daily summary, kept forever, and the 30-day window for raw daily files.

    python -m pricemon.summary [--data data]      rebuild the summary (backfill)

``data/history/daily-summary.csv``: one row per UTC date since ``SINCE``
(5 Nov 2026, the first day after the baseline run), never pruned:

| column | meaning |
|---|---|
| ``date`` | UTC date |
| ``stores_counted`` | stores in the public numbers that day (warming-up stores excluded) |
| ``stores_updated`` | counted stores read completely in the day's last good run |
| ``prices`` | live prices after the day's last good run |
| ``price_drops`` / ``price_rises`` | price events that day (all good runs) |
| ``sales_started`` | ``discount_start`` events |
| ``out_of_stock`` / ``back_in_stock`` | stock events |
| ``runs_due`` | the day's schedule slots |
| ``runs_delivered`` | slots that got a good run that day |
| ``runs_on_time`` | slots whose good run started within 2 h |
| ``delivered`` | yes when every due run of the day was delivered (empty until a slot is judged) |
| ``on_time`` | yes when every due run of the day started within 2 h of its slot (empty likewise) |
| ``rows_held`` | rows read but not published that day (see :func:`rows_held`) |

The file is rebuilt from ``data/runs.jsonl`` after every run; a date that is no
longer in the run log keeps its existing row, so the summary survives any pruning.

``data/public/history.json`` (``steadydata.history/v1``) is the same table in a
compact form for other sites (the steadydata.co range chart). Aggregates only.

Raw daily files (``data/changes/YYYY/YYYY-MM-DD.csv``) are kept for
``RAW_DAYS`` days; :func:`prune_raw` deletes older ones. Nothing is lost: every
version of every price stays in the monthly Parquet history in the releases.
"""

from __future__ import annotations

import argparse
import csv
import io
import json
import os
import tempfile
from collections import defaultdict
from datetime import UTC, date, datetime, timedelta
from pathlib import Path
from typing import Any

from pricemon.outputs import iso, read_runs
from pricemon.schedule import slot_states

SINCE = date(2026, 11, 5)
RAW_DAYS = 30
GOOD = ("ok", "partial")
SCHEMA = "steadydata.history/v1"
COLUMNS = (
    "date",
    "stores_counted",
    "stores_updated",
    "prices",
    "price_drops",
    "price_rises",
    "sales_started",
    "out_of_stock",
    "back_in_stock",
    "runs_due",
    "runs_delivered",
    "runs_on_time",
    "delivered",
    "on_time",
    "rows_held",
)
EVENT_COLUMNS = {
    "price_drops": "price_down",
    "price_rises": "price_up",
    "sales_started": "discount_start",
    "out_of_stock": "out_of_stock",
    "back_in_stock": "back_in_stock",
}
ROOT = Path(__file__).resolve().parents[2]


def rows_held(run: dict[str, Any]) -> int:
    """Rows of ``run`` read but not published: validation rejects, rows of stores whose
    second source disagreed, big moves the second read did not confirm, placeholder
    prices, and every row of a held run."""
    if run.get("status") == "held":
        return int(run.get("rows_observed") or 0) + int(run.get("rows_rejected") or 0)
    stores = run.get("stores") or []
    warming = {w.get("store_id") for w in run.get("warming") or []}
    counted = [s for s in stores if s.get("store_id") not in warming]
    mismatch = sum(int(s.get("variants") or 0) for s in counted if s.get("status") == "mismatch")
    second = sum(int(s.get("held_back") or 0) for s in counted if s.get("status") == "ok")
    return int(run.get("rows_rejected") or 0) + mismatch + second


def build_rows(runs: list[dict[str, Any]], now: datetime) -> dict[str, dict[str, Any]]:
    """Summary rows per date, computed from the run log."""
    states = slot_states(runs, now)
    slots_by_day: dict[str, list[str]] = defaultdict(list)
    for s in states:
        if s.state != "pending":
            slots_by_day[s.slot.date().isoformat()].append(s.state)
    by_day: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for r in runs:
        if r.get("status") in ("ok", "partial", "held"):
            by_day[str(r["started_at"])[:10]].append(r)
    out: dict[str, dict[str, Any]] = {}
    for day in sorted(set(by_day) | set(slots_by_day)):
        if day < SINCE.isoformat():
            continue
        day_runs = by_day.get(day, [])
        good = [r for r in day_runs if r.get("status") in GOOD]
        last = good[-1] if good else None
        due = slots_by_day.get(day, [])
        delivered = sum(1 for s in due if s in ("on_time", "late"))
        on_time = sum(1 for s in due if s == "on_time")
        row: dict[str, Any] = {
            "date": day,
            "stores_counted": int(last.get("stores_total") or 0) if last else "",
            "stores_updated": int(last.get("stores_ok") or 0) if last else "",
            "prices": int(last.get("rows_live") or 0) if last else "",
            "runs_due": len(due),
            "runs_delivered": delivered,
            "runs_on_time": on_time,
            # A day with no judged slot yet (its slot is still pending) is not a "no".
            "delivered": ("yes" if delivered == len(due) else "no") if due else "",
            "on_time": ("yes" if on_time == len(due) else "no") if due else "",
            "rows_held": sum(rows_held(r) for r in day_runs),
        }
        for col, event in EVENT_COLUMNS.items():
            row[col] = sum(int((r.get("events") or {}).get(event) or 0) for r in good)
        out[day] = row
    return out


def read_summary(path: Path) -> dict[str, dict[str, Any]]:
    if not path.exists():
        return {}
    with path.open(newline="", encoding="utf-8") as fh:
        return {r["date"]: dict(r) for r in csv.DictReader(fh)}


def _atomic_write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=f".{path.name}-", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as fh:
            fh.write(text)
        Path(tmp).chmod(0o644)
        Path(tmp).replace(path)
    except BaseException:
        Path(tmp).unlink(missing_ok=True)
        raise


def write_summary(data: Path, now: datetime) -> list[dict[str, Any]]:
    """Rebuild ``data/history/daily-summary.csv``; existing dates not in the log are kept."""
    path = data / "history" / "daily-summary.csv"
    rows = read_summary(path)
    rows.update(build_rows(read_runs(data), now))
    ordered = [rows[d] for d in sorted(rows)]
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=COLUMNS, extrasaction="ignore", lineterminator="\n")
    w.writeheader()
    w.writerows(ordered)
    _atomic_write(path, buf.getvalue())
    return ordered


def _int(v: Any) -> int | None:
    try:
        return int(v)
    except (TypeError, ValueError):
        return None


def delivery(rows: list[dict[str, Any]], status: dict[str, Any] | None = None) -> dict[str, Any]:
    """Headline counts: due runs delivered since ``SINCE``, and on time since the trigger."""
    due = sum(_int(r.get("runs_due")) or 0 for r in rows)
    delivered = sum(_int(r.get("runs_delivered")) or 0 for r in rows)
    sched = (status or {}).get("schedule") or {}
    since = sched.get("since") or {}
    return {
        "since": SINCE.isoformat(),
        "days": len(rows),
        "runs_due": due,
        "runs_delivered": delivered,
        "on_time_window_h": int(sched.get("on_time_window_h") or 2),
        "on_time_since": sched.get("on_time_since"),
        "on_time_runs_due": int(since.get("slots") or 0),
        "on_time_runs": int(since.get("on_time") or 0),
    }


def history_doc(
    rows: list[dict[str, Any]], now: datetime, status: dict[str, Any] | None = None
) -> dict[str, Any]:
    fields = [c for c in COLUMNS if c != "date"]
    days = []
    for r in rows:
        vals: list[Any] = [r["date"]]
        for c in fields:
            v = r.get(c)
            vals.append(v == "yes" if c in ("delivered", "on_time") else _int(v))
        days.append(vals)
    return {
        "schema": SCHEMA,
        "generated_at": iso(now),
        "fields": ["date", *fields],
        "delivery": delivery(rows, status),
        "days": days,
    }


def write_history_json(
    data: Path, rows: list[dict[str, Any]], now: datetime, status: dict[str, Any] | None = None
) -> Path:
    doc = history_doc(rows, now, status)
    body = ",\n".join("    " + json.dumps(d, separators=(",", ":")) for d in doc["days"])
    head = json.dumps({**doc, "days": []}, indent=2)
    text = (
        head.replace('"days": []', '"days": [\n' + body + "\n  ]" if body else '"days": []') + "\n"
    )
    path = data / "public" / "history.json"
    _atomic_write(path, text)
    return path


def prune_raw(data: Path, today: date, keep_days: int = RAW_DAYS) -> list[Path]:
    """Delete raw daily change logs older than ``keep_days`` (today counts as day 1)."""
    cutoff = today - timedelta(days=keep_days - 1)
    removed: list[Path] = []
    for f in sorted((data / "changes").glob("*/*.csv")):
        try:
            day = date.fromisoformat(f.stem)
        except ValueError:
            continue
        if day < cutoff:
            f.unlink()
            removed.append(f)
    for d in (data / "changes").glob("*"):
        if d.is_dir() and not any(d.iterdir()):
            d.rmdir()
    return removed


def refresh(data: Path, now: datetime) -> list[dict[str, Any]]:
    """Summary CSV + public history JSON + 30-day raw window. Called after every run."""
    rows = write_summary(data, now)
    status_file = data / "status.json"
    status = json.loads(status_file.read_text(encoding="utf-8")) if status_file.exists() else None
    write_history_json(data, rows, now, status)
    prune_raw(data, now.date())
    return rows


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
    p.add_argument("--data", type=Path, default=ROOT / "data")
    p.add_argument("--no-prune", action="store_true")
    a = p.parse_args(argv)
    now = datetime.now(UTC).replace(microsecond=0)
    rows = write_summary(a.data, now)
    status_file = a.data / "status.json"
    status = json.loads(status_file.read_text(encoding="utf-8")) if status_file.exists() else None
    write_history_json(a.data, rows, now, status)
    if not a.no_prune:
        prune_raw(a.data, now.date())
    d = delivery(rows, status)
    done, due = d["runs_delivered"], d["runs_due"]
    print(f"{len(rows)} days; {done} of {due} runs delivered since {d['since']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
