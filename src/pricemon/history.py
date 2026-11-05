"""SCD2 price history with DuckDB.

State between runs is the set of **open versions** (``valid_to IS NULL``),
committed as ``data/latest/snapshot.csv``. Each run:

1. loads the snapshot into DuckDB (``prev``) and the run's observations (``obs``);
2. full-outer-joins them for the stores fetched completely in this run;
3. keeps unchanged versions (titles refreshed in place), closes changed and
   removed versions at the run time, opens versions for changed and new variants;
4. carries over the open versions of every store not fetched completely;
5. writes the new snapshot and the month's Parquet file (every version valid at
   any time in the month).

Tracked attributes: ``price_cents``, ``compare_at_cents``, ``available``.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass, field, replace
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

import duckdb
import pyarrow as pa

from pricemon.changes import ChangeEvent, Ident, State, diff
from pricemon.models import VariantRow

VERSION_SCHEMA = pa.schema(
    [
        ("store_id", pa.string()),
        ("product_id", pa.int64()),
        ("variant_id", pa.int64()),
        ("handle", pa.string()),
        ("product_title", pa.string()),
        ("variant_title", pa.string()),
        ("price_cents", pa.int64()),
        ("compare_at_cents", pa.int64()),
        ("available", pa.bool_()),
        ("valid_from", pa.timestamp("us", tz="UTC")),
        ("valid_to", pa.timestamp("us", tz="UTC")),
    ]
)
SNAPSHOT_COLUMNS = [f.name for f in VERSION_SCHEMA if f.name != "valid_to"]

# SQL is built only from these constants; values and paths go in as parameters.
_PREV_DDL = """
CREATE OR REPLACE TABLE prev (
    store_id VARCHAR, product_id BIGINT, variant_id BIGINT, handle VARCHAR,
    product_title VARCHAR, variant_title VARCHAR, price_cents BIGINT,
    compare_at_cents BIGINT, available BOOLEAN, valid_from TIMESTAMPTZ,
    valid_to TIMESTAMPTZ
)
"""
_PREV_LOAD = """
INSERT INTO prev
SELECT *, NULL::TIMESTAMPTZ FROM read_csv(?, header = true, columns = {
    'store_id': 'VARCHAR', 'product_id': 'BIGINT', 'variant_id': 'BIGINT',
    'handle': 'VARCHAR', 'product_title': 'VARCHAR', 'variant_title': 'VARCHAR',
    'price_cents': 'BIGINT', 'compare_at_cents': 'BIGINT', 'available': 'BOOLEAN',
    'valid_from': 'TIMESTAMPTZ'
})
"""
_CARRIED = """
SELECT store_id, product_id, variant_id, handle, product_title, variant_title,
       price_cents, compare_at_cents, available, epoch_us(valid_from)
FROM prev WHERE store_id NOT IN (SELECT store_id FROM complete)
"""
_CARRIED_COLUMNS = [c for c in SNAPSHOT_COLUMNS if c != "valid_from"]
_SNAPSHOT_SELECT = """
SELECT store_id, product_id, variant_id, handle, product_title, variant_title,
       price_cents, compare_at_cents, available,
       strftime(valid_from, '%Y-%m-%dT%H:%M:%SZ') AS valid_from
FROM open_arrow
ORDER BY store_id, product_id, variant_id, valid_from
"""
_MONTH_PREV_EMPTY = "CREATE OR REPLACE TABLE month_prev AS SELECT * FROM closed_arrow LIMIT 0"
_MONTH_PREV_LOAD = """
CREATE OR REPLACE TABLE month_prev AS
SELECT store_id, product_id, variant_id, handle, product_title, variant_title,
       price_cents, compare_at_cents, available, valid_from, valid_to
FROM read_parquet(?)
"""
_MONTH_BUILD = """
CREATE OR REPLACE TABLE month_out AS
SELECT store_id, product_id, variant_id, handle, product_title, variant_title,
       price_cents, compare_at_cents, available, valid_from, valid_to,
       ?::TIMESTAMPTZ AS exported_at
FROM (
    SELECT *, row_number() OVER (
        PARTITION BY store_id, variant_id, valid_from
        ORDER BY valid_to IS NULL, valid_to DESC
    ) AS rn
    FROM (
        SELECT * FROM open_arrow
        UNION ALL SELECT * FROM closed_arrow
        UNION ALL SELECT * FROM month_prev
    )
)
WHERE rn = 1 AND (valid_to IS NULL OR valid_to >= ?::TIMESTAMPTZ)
ORDER BY store_id, product_id, variant_id, valid_from
"""


EPOCH = datetime(1970, 1, 1, tzinfo=UTC)


def from_epoch_us(value: int) -> datetime:
    """DuckDB TIMESTAMPTZ as epoch microseconds to an aware UTC datetime (no pytz needed)."""
    return EPOCH + timedelta(microseconds=int(value))


@dataclass(frozen=True)
class Version:
    store_id: str
    product_id: int
    variant_id: int
    handle: str
    product_title: str
    variant_title: str
    price_cents: int
    compare_at_cents: int | None
    available: bool
    valid_from: datetime
    valid_to: datetime | None = None

    @property
    def state(self) -> State:
        return State(self.price_cents, self.compare_at_cents, self.available)


@dataclass
class MergeResult:
    open_versions: list[Version]
    closed_versions: list[Version]
    events: list[ChangeEvent] = field(default_factory=list)


def connect() -> duckdb.DuckDBPyConnection:
    con = duckdb.connect(":memory:")
    con.execute("SET TimeZone = 'UTC'")
    return con


def _versions_table(versions: Iterable[Version]) -> pa.Table:
    rows = [v.__dict__ for v in versions]
    return pa.Table.from_pylist(rows, schema=VERSION_SCHEMA)


def load_snapshot(con: duckdb.DuckDBPyConnection, path: Path | None) -> None:
    """Create table ``prev`` from the committed snapshot (empty when there is none)."""
    con.execute(_PREV_DDL)
    if path is not None and path.exists():
        con.execute(_PREV_LOAD, [str(path)])


def previous_versions(
    con: duckdb.DuckDBPyConnection,
) -> dict[str, dict[int, tuple[int, int | None]]]:
    """``{store_id: {variant_id: (price_cents, compare_at_cents)}}`` of the open versions."""
    out: dict[str, dict[int, tuple[int, int | None]]] = {}
    rows = con.execute(
        "SELECT store_id, variant_id, price_cents, compare_at_cents FROM prev"
    ).fetchall()
    for store_id, variant_id, price, compare in rows:
        out.setdefault(store_id, {})[int(variant_id)] = (
            int(price),
            None if compare is None else int(compare),
        )
    return out


def _obs_table(rows: Iterable[VariantRow]) -> pa.Table:
    data = [
        {
            "store_id": r.store_id,
            "product_id": r.product_id,
            "variant_id": r.variant_id,
            "handle": r.handle,
            "product_title": r.product_title,
            "variant_title": r.variant_title,
            "price_cents": r.price_cents,
            "compare_at_cents": r.compare_at_cents,
            "available": r.available,
        }
        for r in rows
    ]
    schema = pa.schema([f for f in VERSION_SCHEMA if f.name not in ("valid_from", "valid_to")])
    return pa.Table.from_pylist(data, schema=schema)


def _version(row: dict[str, Any], prefix: str, valid_from: datetime) -> Version:
    return Version(
        store_id=row["store_id"],
        product_id=int(row[f"{prefix}product_id"]),
        variant_id=int(row["variant_id"]),
        handle=row[f"{prefix}handle"],
        product_title=row[f"{prefix}product_title"],
        variant_title=row[f"{prefix}variant_title"],
        price_cents=int(row[f"{prefix}price_cents"]),
        compare_at_cents=(
            None
            if row[f"{prefix}compare_at_cents"] is None
            else int(row[f"{prefix}compare_at_cents"])
        ),
        available=bool(row[f"{prefix}available"]),
        valid_from=valid_from,
    )


def merge(
    con: duckdb.DuckDBPyConnection,
    rows: Iterable[VariantRow],
    complete_stores: set[str],
    run_at: datetime,
) -> MergeResult:
    """SCD2 merge of the run's observations into ``prev``. See module docstring."""
    obs = _obs_table(rows)
    con.register("obs_arrow", obs)
    con.execute("CREATE OR REPLACE TABLE obs AS SELECT * FROM obs_arrow")
    con.unregister("obs_arrow")
    con.execute("CREATE OR REPLACE TABLE complete (store_id VARCHAR)")
    if complete_stores:
        con.executemany("INSERT INTO complete VALUES (?)", [[s] for s in sorted(complete_stores)])

    cur = con.execute(
        """
        SELECT
            coalesce(p.store_id, o.store_id) AS store_id,
            coalesce(p.variant_id, o.variant_id) AS variant_id,
            p.store_id IS NOT NULL AS has_prev,
            o.store_id IS NOT NULL AS has_obs,
            p.product_id AS p_product_id, p.handle AS p_handle,
            p.product_title AS p_product_title, p.variant_title AS p_variant_title,
            p.price_cents AS p_price_cents, p.compare_at_cents AS p_compare_at_cents,
            p.available AS p_available, epoch_us(p.valid_from) AS p_valid_from_us,
            o.product_id AS o_product_id, o.handle AS o_handle,
            o.product_title AS o_product_title, o.variant_title AS o_variant_title,
            o.price_cents AS o_price_cents, o.compare_at_cents AS o_compare_at_cents,
            o.available AS o_available
        FROM (SELECT * FROM prev WHERE store_id IN (SELECT store_id FROM complete)) AS p
        FULL OUTER JOIN obs AS o
            ON p.store_id = o.store_id AND p.variant_id = o.variant_id
        ORDER BY 1, 2
        """
    )
    names = [d[0] for d in cur.description]
    open_versions: list[Version] = []
    closed: list[Version] = []
    events: list[ChangeEvent] = []
    for values in cur.fetchall():
        row = dict(zip(names, values, strict=True))
        old = (
            _version(row, "p_", from_epoch_us(row["p_valid_from_us"])) if row["has_prev"] else None
        )
        new = _version(row, "o_", run_at) if row["has_obs"] else None
        ident_src = new or old
        assert ident_src is not None
        ident = Ident(
            ident_src.store_id,
            ident_src.product_id,
            ident_src.variant_id,
            ident_src.handle,
            ident_src.product_title,
            ident_src.variant_title,
        )
        events += diff(ident, old.state if old else None, new.state if new else None, run_at)
        if old is not None and new is not None and old.state == new.state:
            # Unchanged: keep the version, refresh identifying text in place.
            open_versions.append(replace(new, valid_from=old.valid_from))
            continue
        if old is not None:
            closed.append(replace(old, valid_to=run_at))
        if new is not None:
            open_versions.append(new)

    for values in con.execute(_CARRIED).fetchall():
        r = dict(zip(_CARRIED_COLUMNS, values[:-1], strict=True))
        open_versions.append(Version(**r, valid_from=from_epoch_us(values[-1])))
    open_versions.sort(key=lambda v: (v.store_id, v.product_id, v.variant_id))
    return MergeResult(open_versions=open_versions, closed_versions=closed, events=events)


def write_snapshot(con: duckdb.DuckDBPyConnection, versions: list[Version], path: Path) -> None:
    """Write open versions as a deterministic CSV (sorted, UTC ISO timestamps)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    con.register("open_arrow", _versions_table(versions))
    try:
        con.sql(_SNAPSHOT_SELECT).write_csv(str(path), header=True)
    finally:
        con.unregister("open_arrow")


def _revert_uncommitted(con: duckdb.DuckDBPyConnection, known: list[datetime]) -> None:
    con.execute("CREATE OR REPLACE TABLE known_runs (t TIMESTAMPTZ)")
    con.executemany("INSERT INTO known_runs VALUES (?)", [[t] for t in known])
    dropped = con.execute(
        "SELECT count(*) FROM month_prev WHERE valid_from NOT IN (SELECT t FROM known_runs)"
    ).fetchone()
    reopened = con.execute(
        "SELECT count(*) FROM month_prev WHERE valid_to IS NOT NULL "
        "AND valid_to NOT IN (SELECT t FROM known_runs)"
    ).fetchone()
    con.execute("DELETE FROM month_prev WHERE valid_from NOT IN (SELECT t FROM known_runs)")
    con.execute(
        "UPDATE month_prev SET valid_to = NULL "
        "WHERE valid_to IS NOT NULL AND valid_to NOT IN (SELECT t FROM known_runs)"
    )
    if (dropped and dropped[0]) or (reopened and reopened[0]):
        print(
            f"history repair: dropped {dropped[0] if dropped else 0} versions and re-opened "
            f"{reopened[0] if reopened else 0} from runs whose commit did not land",
            flush=True,
        )


def update_month_parquet(
    con: duckdb.DuckDBPyConnection,
    existing: Path | None,
    open_versions: list[Version],
    closed_versions: list[Version],
    month_start: datetime,
    exported_at: datetime,
    out: Path,
    committed_runs: Iterable[datetime] | None = None,
) -> int:
    """Rewrite the month file: every version valid at any time in the month.

    Union of the existing month file, versions closed in this run and the current
    open versions; on a duplicate key ``(store_id, variant_id, valid_from)`` a
    closed row wins over an open one. Returns the number of rows written.

    ``committed_runs``: start times of the runs whose data commit landed
    (``runs.jsonl``). A run can upload this file and then fail to commit its
    snapshot (INC-006); its traces are reverted here: versions it opened are
    dropped and versions it closed are re-opened, so the file agrees with the
    committed snapshot again.
    """
    out.parent.mkdir(parents=True, exist_ok=True)
    con.register("open_arrow", _versions_table(open_versions))
    con.register("closed_arrow", _versions_table(closed_versions))
    try:
        if existing is not None and existing.exists():
            con.execute(_MONTH_PREV_LOAD, [str(existing)])
            if committed_runs is not None:
                _revert_uncommitted(con, [*committed_runs, exported_at])
        else:
            con.execute(_MONTH_PREV_EMPTY)
        con.execute(_MONTH_BUILD, [exported_at, month_start])
    finally:
        con.unregister("open_arrow")
        con.unregister("closed_arrow")
    tmp = out.with_name(out.name + ".tmp")
    con.table("month_out").write_parquet(str(tmp), compression="zstd")
    tmp.replace(out)
    count = con.execute("SELECT count(*) FROM month_out").fetchone()
    return int(count[0]) if count else 0
