"""Golden two-run scenario for the SCD2 merge, snapshot CSV, events and Parquet.

Set UPDATE_GOLDEN=1 to rewrite the expected files after an intended change, then
review the diff by hand.
"""

from __future__ import annotations

import csv
import json
import os
from datetime import UTC, datetime
from pathlib import Path

import duckdb

from pricemon.history import (
    connect,
    from_epoch_us,
    load_snapshot,
    merge,
    update_month_parquet,
    write_snapshot,
)
from pricemon.models import VariantRow

GOLDEN = Path(__file__).parent / "fixtures" / "golden"
RUN1 = datetime(2026, 11, 4, 6, 17, tzinfo=UTC)
RUN2 = datetime(2026, 11, 5, 6, 17, tzinfo=UTC)
NOV = datetime(2026, 11, 1, tzinfo=UTC)


def row(
    store: str,
    vid: int,
    price: int,
    at: datetime,
    compare: int | None = None,
    avail: bool = True,
    title: str = "Tee",
) -> VariantRow:
    return VariantRow.model_validate(
        {
            "store_id": store,
            "product_id": 100 + vid // 10,
            "variant_id": vid,
            "handle": "tee",
            "product_title": title,
            "variant_title": f"V{vid}",
            "price_cents": price,
            "compare_at_cents": compare,
            "availability": "in_stock" if avail else "out_of_stock",
            "observed_at": at,
        }
    )


def golden(name: str, actual: str) -> None:
    path = GOLDEN / name
    if os.environ.get("UPDATE_GOLDEN"):
        path.write_text(actual)
    assert actual == path.read_text(), f"{name} differs from golden file"


def test_two_runs(tmp_path: Path) -> None:
    snap = tmp_path / "snapshot.csv"
    month = tmp_path / "price_history_2026-11.parquet"

    # Run 1: both stores fetched completely; everything is new.
    con = connect()
    load_snapshot(con, snap)
    run1 = [
        row("a", 1, 2800, RUN1),
        row("a", 2, 2800, RUN1, avail=False),
        row("a", 3, 5000, RUN1, compare=6000),
        row("b", 10, 1000, RUN1),
    ]
    r1 = merge(con, run1, {"a", "b"}, RUN1)
    assert [e.event for e in r1.events] == ["new"] * 4
    write_snapshot(con, r1.open_versions, snap)
    assert (
        update_month_parquet(con, None, r1.open_versions, r1.closed_versions, NOV, RUN1, month) == 4
    )

    # Run 2: store a changes, store b fails (not complete) and is carried over.
    con = connect()
    load_snapshot(con, snap)
    run2 = [
        row("a", 1, 2240, RUN2, compare=2800, title="Tee (organic)"),
        row("a", 2, 2800, RUN2),
        row("a", 4, 1500, RUN2),
    ]
    r2 = merge(con, run2, {"a"}, RUN2)
    write_snapshot(con, r2.open_versions, snap)
    n = update_month_parquet(con, month, r2.open_versions, r2.closed_versions, NOV, RUN2, month)

    golden("snapshot_after_run2.csv", snap.read_text())
    events = "\n".join(json.dumps(e.to_row(), sort_keys=True) for e in r2.events) + "\n"
    golden("events_run2.jsonl", events)

    # 4 open (a1, a2, a4 new versions; b10 carried) + 3 closed (a1, a2, a3 old versions).
    assert n == 7
    closed = (
        duckdb.connect()
        .execute(
            "SELECT store_id, variant_id, epoch_us(valid_to) FROM read_parquet(?) "
            "WHERE valid_to IS NOT NULL ORDER BY variant_id",
            [str(month)],
        )
        .fetchall()
    )
    assert [(s, v) for s, v, _ in closed] == [("a", 1), ("a", 2), ("a", 3)]
    assert all(from_epoch_us(t) == RUN2 for _, _, t in closed)

    with snap.open() as fh:
        rows = {(r["store_id"], r["variant_id"]): r for r in csv.DictReader(fh)}
    assert rows[("b", "10")]["valid_from"] == "2026-11-04T06:17:00Z"  # carried, untouched
    assert rows[("a", "1")]["product_title"] == "Tee (organic)"


def test_unchanged_variant_keeps_valid_from_and_refreshes_title(tmp_path: Path) -> None:
    snap = tmp_path / "snapshot.csv"
    con = connect()
    load_snapshot(con, snap)
    write_snapshot(con, merge(con, [row("a", 1, 2800, RUN1)], {"a"}, RUN1).open_versions, snap)
    con = connect()
    load_snapshot(con, snap)
    result = merge(con, [row("a", 1, 2800, RUN2, title="Renamed")], {"a"}, RUN2)
    assert result.events == []
    assert result.closed_versions == []
    (only,) = result.open_versions
    assert only.valid_from == RUN1
    assert only.product_title == "Renamed"
