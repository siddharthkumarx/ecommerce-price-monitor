from __future__ import annotations

from datetime import date
from pathlib import Path

import duckdb

from pricemon.releases import plan

GOLDEN = Path(__file__).parent / "fixtures" / "golden"
HEADER = (
    "observed_at,store_id,product_id,variant_id,handle,product_title,variant_title,event,"
    "old_price_cents,new_price_cents,old_compare_at_cents,new_compare_at_cents,price_change_pct\n"
)


def _day(data: Path, day: str, *rows: str) -> None:
    path = data / "changes" / day[:4] / f"{day}.csv"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(HEADER + "".join(r + "\n" for r in rows))


def _snapshot(month: str, work: Path) -> Path | None:
    return GOLDEN / "snapshot_after_run2.csv" if month == "2026-11" else None


def test_days_are_uploaded_once_after_they_end_and_months_once_after_they_end(
    tmp_path: Path,
) -> None:
    data = tmp_path / "data"
    row = "2026-11-29T06:17:00Z,a,1,11,tee,Tee,V1,price_down,2800,2240,,2800,-20.0"
    _day(data, "2026-11-29", row)
    _day(data, "2026-11-30", row.replace("11-29", "11-30"))
    _day(data, "2026-12-01", row.replace("11-29", "12-01"))
    out = tmp_path / "out"
    todo = plan(data, {}, date(2026, 12, 1), out, month_snapshot=_snapshot)
    assert [(t, p.name) for t, p in todo] == [
        ("history-2026-11", "events-2026-11-29.parquet"),
        ("history-2026-11", "events-2026-11-30.parquet"),
        ("history-2026-11", "snapshot-2026-11.parquet"),
    ]
    # Today (2026-12-01) is not over: its file waits; nothing already uploaded again.
    done = {"history-2026-11": {p.name for _, p in todo}}
    assert plan(data, done, date(2026, 12, 1), out, month_snapshot=_snapshot) == []
    later = plan(data, done, date(2026, 12, 2), out, month_snapshot=_snapshot)
    assert [(t, p.name) for t, p in later] == [("history-2026-12", "events-2026-12-01.parquet")]


def test_files_are_typed_parquet_with_the_committed_rows(tmp_path: Path) -> None:
    data = tmp_path / "data"
    _day(data, "2026-11-29", "2026-11-29T06:17:00Z,a,1,11,tee,Tee,V1,new,,2800,,,")
    (_, events), (_, snap) = plan(data, {}, date(2026, 12, 1), tmp_path, _snapshot)
    con = duckdb.connect()
    row = con.execute(
        "SELECT store_id, variant_id, event, new_price_cents, typeof(observed_at) "
        "FROM read_parquet(?)",
        [str(events)],
    ).fetchone()
    assert row == ("a", 11, "new", 2800, "TIMESTAMP WITH TIME ZONE")
    n = con.execute("SELECT count(*) FROM read_parquet(?)", [str(snap)]).fetchone()
    assert n is not None
    assert n[0] == len((GOLDEN / "snapshot_after_run2.csv").read_text().splitlines()) - 1
