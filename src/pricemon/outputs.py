"""Small committed outputs: change log, run log, status, badges, site summary."""

from __future__ import annotations

import csv
import json
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import duckdb

from pricemon.changes import EVENT_TYPES, ChangeEvent
from pricemon.schedule import active_crons, missed_slots

TEAL = "2FBFAE"
AMBER = "E9A93C"
GOOD_STATUSES = ("ok", "partial")
CHANGE_COLUMNS = [
    "observed_at",
    "store_id",
    "product_id",
    "variant_id",
    "handle",
    "product_title",
    "variant_title",
    "event",
    "old_price_cents",
    "new_price_cents",
    "old_compare_at_cents",
    "new_compare_at_cents",
    "price_change_pct",
]


def iso(ts: datetime) -> str:
    return ts.astimezone(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def parse_iso(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(UTC)


def append_changes(data: Path, events: list[ChangeEvent], run_at: datetime) -> Path | None:
    """Append the run's events to ``data/changes/YYYY/YYYY-MM-DD.csv``."""
    if not events:
        return None
    path = data / "changes" / f"{run_at:%Y}" / f"{run_at:%Y-%m-%d}.csv"
    path.parent.mkdir(parents=True, exist_ok=True)
    new_file = not path.exists()
    with path.open("a", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=CHANGE_COLUMNS, lineterminator="\n")
        if new_file:
            writer.writeheader()
        for e in events:
            writer.writerow(e.to_row())
    return path


def read_runs(data: Path) -> list[dict[str, Any]]:
    path = data / "runs.jsonl"
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def append_run(data: Path, record: dict[str, Any]) -> None:
    data.mkdir(parents=True, exist_ok=True)
    with (data / "runs.jsonl").open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(record, sort_keys=True, separators=(",", ":")) + "\n")


def _badge(label: str, message: str, color: str) -> dict[str, Any]:
    return {"schemaVersion": 1, "label": label, "message": message, "color": color}


def build_status(
    runs: list[dict[str, Any]], now: datetime, crons: tuple[str, ...] | None = None
) -> dict[str, Any]:
    """status.json content, computed only from runs.jsonl."""
    good = [r for r in runs if r["status"] in GOOD_STATUSES]
    last = runs[-1] if runs else None
    first_good = parse_iso(good[0]["started_at"]) if good else None
    days_running = max(0, (now.date() - first_good.date()).days + 1) if first_good else 0
    missed = (
        missed_slots(
            [parse_iso(r["started_at"]) for r in good],
            first_good,
            now,
            crons if crons is not None else active_crons(),
        )
        if first_good
        else []
    )
    today = now.date().isoformat()
    todays = [r for r in good if r["started_at"].startswith(today)]
    return {
        "generated_at": iso(now),
        "first_run": iso(first_good) if first_good else None,
        "days_running": days_running,
        "runs_total": len(runs),
        "runs_good": len(good),
        "runs_held": sum(1 for r in runs if r["status"] == "held"),
        "missed_runs": len(missed),
        "missed_slots": [iso(m) for m in missed[-10:]],
        "last_run": (
            {
                "run_id": last["run_id"],
                "started_at": last["started_at"],
                "status": last["status"],
                "duration_s": last.get("duration_s"),
                "stores_ok": last.get("stores_ok"),
                "stores_total": last.get("stores_total"),
                "rows_live": last.get("rows_live"),
                "hold_reasons": [h["message"] for h in last.get("guard", {}).get("holds", [])],
            }
            if last
            else None
        ),
        "rows_today": todays[-1]["rows_observed"] if todays else 0,
    }


def write_status(data: Path, status: dict[str, Any]) -> None:
    """status.json plus one shields.io endpoint file per badge."""
    (data / "status.json").write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")
    badges = data / "badges"
    badges.mkdir(parents=True, exist_ok=True)
    last = status["last_run"]
    if last:
        when = parse_iso(last["started_at"]).strftime("%Y-%m-%d %H:%M UTC")
        last_badge = _badge(
            "last run", f"{when} {last['status']}", TEAL if last["status"] == "ok" else AMBER
        )
    else:
        last_badge = _badge("last run", "none yet", AMBER)
    files = {
        "days-running.json": _badge("days running", str(status["days_running"]), TEAL),
        "last-run.json": last_badge,
        "missed-runs.json": _badge(
            "missed runs", str(status["missed_runs"]), TEAL if status["missed_runs"] == 0 else AMBER
        ),
        "rows-today.json": _badge(
            "rows today", f"{status['rows_today']:,}", TEAL if status["rows_today"] else AMBER
        ),
    }
    for name, body in files.items():
        (badges / name).write_text(json.dumps(body) + "\n", encoding="utf-8")


_SUMMARY_SQL = """
SELECT s.store_id,
       count(*) AS variants,
       count(DISTINCT s.product_id) AS products,
       count(*) FILTER (WHERE s.available) AS in_stock,
       count(*) FILTER (WHERE s.compare_at_cents > s.price_cents) AS discounted,
       median(s.price_cents)::BIGINT AS median_price_cents,
       round(avg(CASE WHEN s.compare_at_cents > s.price_cents
                      THEN 100.0 * (s.compare_at_cents - s.price_cents)
                           / s.compare_at_cents END), 1) AS avg_discount_pct
FROM read_csv(?, header = true, columns = {
    'store_id': 'VARCHAR', 'product_id': 'BIGINT', 'variant_id': 'BIGINT',
    'handle': 'VARCHAR', 'product_title': 'VARCHAR', 'variant_title': 'VARCHAR',
    'price_cents': 'BIGINT', 'compare_at_cents': 'BIGINT', 'available': 'BOOLEAN',
    'valid_from': 'VARCHAR'
}) AS s
GROUP BY s.store_id
ORDER BY s.store_id
"""


def snapshot_summary(snapshot: Path) -> list[dict[str, Any]]:
    """Per-store aggregates of the live snapshot (DuckDB over the CSV)."""
    if not snapshot.exists():
        return []
    con = duckdb.connect()
    cur = con.execute(_SUMMARY_SQL, [str(snapshot)])
    names = [d[0] for d in cur.description]
    return [dict(zip(names, row, strict=True)) for row in cur.fetchall()]


def recent_events(data: Path, limit_days: int = 14) -> list[dict[str, str]]:
    files = sorted((data / "changes").glob("*/*.csv"))[-limit_days:]
    rows: list[dict[str, str]] = []
    for path in files:
        with path.open(encoding="utf-8") as fh:
            rows.extend(csv.DictReader(fh))
    return rows


def event_counts(events: list[ChangeEvent]) -> dict[str, int]:
    counts = Counter(e.event for e in events)
    return {k: counts.get(k, 0) for k in EVENT_TYPES}
