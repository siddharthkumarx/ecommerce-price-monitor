"""Publish the latest data to a Google Sheet.

    python -m pricemon.sheets --data data

Needs the Actions secret ``GOOGLE_SA_JSON`` (a service-account key JSON) and the
variable ``GOOGLE_SHEET_ID`` (the sheet shared with that service account as
editor). When either is missing it prints why and exits 0, so forks and the
private phase run cleanly without them.

Tabs (created when missing, replaced on every publish):

* ``latest``: the live snapshot, one row per variant, prices in USD
* ``changes_30d``: change events of the last 30 days
* ``runs``: one row per run from runs.jsonl
"""

from __future__ import annotations

import argparse
import csv
import json
import os
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

from pricemon.outputs import parse_iso, read_runs

CHUNK_ROWS = 5000
Table = list[list[Any]]


def _usd(cents: str) -> str:
    return "" if cents == "" else f"{int(cents) / 100:.2f}"


def latest_table(snapshot: Path, stores: dict[str, tuple[str, str]]) -> Table:
    """``stores`` maps store id to ``(name, host)``."""
    header = [
        "store",
        "product",
        "variant",
        "price_usd",
        "compare_at_usd",
        "available",
        "url",
        "since_utc",
    ]
    rows: Table = [header]
    if not snapshot.exists():
        return rows
    with snapshot.open(encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            name, host = stores.get(r["store_id"], (r["store_id"], ""))
            rows.append(
                [
                    name,
                    r["product_title"],
                    r["variant_title"],
                    _usd(r["price_cents"]),
                    _usd(r["compare_at_cents"]),
                    r["available"],
                    f"https://{host}/products/{r['handle']}" if host else r["handle"],
                    r["valid_from"],
                ]
            )
    return rows


def changes_table(data: Path, now: datetime, days: int = 30) -> Table:
    header = [
        "observed_utc",
        "store_id",
        "product",
        "variant",
        "event",
        "old_usd",
        "new_usd",
        "change_pct",
    ]
    rows: Table = [header]
    cutoff = now - timedelta(days=days)
    for path in sorted((data / "changes").glob("*/*.csv")):
        with path.open(encoding="utf-8") as fh:
            for r in csv.DictReader(fh):
                if parse_iso(r["observed_at"]) < cutoff:
                    continue
                rows.append(
                    [
                        r["observed_at"],
                        r["store_id"],
                        r["product_title"],
                        r["variant_title"],
                        r["event"],
                        _usd(r["old_price_cents"]),
                        _usd(r["new_price_cents"]),
                        r["price_change_pct"],
                    ]
                )
    return rows


def runs_table(data: Path) -> Table:
    header = [
        "run_id",
        "started_utc",
        "status",
        "duration_s",
        "stores_ok",
        "stores_total",
        "rows_observed",
        "rows_live",
        "events",
        "holds",
    ]
    rows: Table = [header]
    for r in read_runs(data):
        rows.append(
            [
                r["run_id"],
                r["started_at"],
                r["status"],
                r.get("duration_s", ""),
                r.get("stores_ok", ""),
                r.get("stores_total", ""),
                r.get("rows_observed", ""),
                r.get("rows_live", ""),
                json.dumps(r.get("events", {}), sort_keys=True),
                "; ".join(h["message"] for h in r.get("guard", {}).get("holds", [])),
            ]
        )
    return rows


def publish(tables: dict[str, Table], sa_info: dict[str, Any], sheet_id: str) -> None:
    import gspread  # imported here so the pipeline never needs it
    from gspread.utils import ValueInputOption

    client = gspread.service_account_from_dict(sa_info)
    sheet = client.open_by_key(sheet_id)
    existing = {ws.title: ws for ws in sheet.worksheets()}
    for title, table in tables.items():
        cols = len(table[0])
        ws = existing.get(title) or sheet.add_worksheet(title, rows=len(table) + 10, cols=cols)
        ws.clear()
        ws.resize(rows=max(len(table), 2), cols=cols)
        for start in range(0, len(table), CHUNK_ROWS):
            chunk = table[start : start + CHUNK_ROWS]
            ws.update(chunk, f"A{start + 1}", value_input_option=ValueInputOption.user_entered)
        print(f"sheet tab {title}: {len(table) - 1} rows")


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
    p.add_argument("--data", type=Path, default=Path("data"))
    p.add_argument("--stores", type=Path, default=Path("config/stores.yml"))
    a = p.parse_args(argv)
    sa_json = os.environ.get("GOOGLE_SA_JSON", "").strip()
    sheet_id = os.environ.get("GOOGLE_SHEET_ID", "").strip()
    if not sa_json or not sheet_id:
        missing = [
            n for n, v in (("GOOGLE_SA_JSON", sa_json), ("GOOGLE_SHEET_ID", sheet_id)) if not v
        ]
        print(f"Google Sheet publish skipped: {', '.join(missing)} not set")
        return 0
    stores: dict[str, tuple[str, str]] = {}
    if a.stores.exists():
        from pricemon.stores import load_stores

        stores = {s.id: (s.name, s.host) for s in load_stores(a.stores)}
    now = datetime.now(UTC)
    tables = {
        "latest": latest_table(a.data / "latest" / "snapshot.csv", stores),
        "changes_30d": changes_table(a.data, now),
        "runs": runs_table(a.data),
    }
    try:
        publish(tables, json.loads(sa_json), sheet_id)
    except Exception as exc:  # report, never print the credential
        print(f"Google Sheet publish failed: {type(exc).__name__}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
