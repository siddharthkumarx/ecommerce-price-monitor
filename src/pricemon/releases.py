"""The history mirror on GitHub Releases: immutable files built from committed data (D-047).

    python -m pricemon.releases --data data --assets work/assets.json --today 2026-11-29 \\
        --out work/releases

Layout, one release per month (tag ``history-YYYY-MM``):

* ``events-YYYY-MM-DD.parquet``: every change event of that UTC day, the rows of
  ``data/changes/YYYY/YYYY-MM-DD.csv`` with typed columns. Written once, the first run
  after the day is over, so it holds every run of the day.
* ``snapshot-YYYY-MM.parquet``: every open price version at the end of the month, the
  ``data/latest/snapshot.csv`` of the last commit of the month. Written once, the
  first run of the next month.

A file is uploaded only when no asset of that name exists: nothing is ever replaced
or deleted (no ``--clobber``). Every file is derived from data committed on ``main``,
so a failed upload is repaired by the next run and an upload can never get ahead of
the committed data. Branch runs upload nothing (``daily.yml``). The plan is printed
as ``<tag> <file>`` lines for the workflow to upload.

Reading it cheaply: one day is one small file; a month is its snapshot plus its day
files. DuckDB reads them together (``read_parquet(['snapshot-2026-11.parquet',
'events-2026-12-*.parquet'])``). The dashboard does not read Parquet in the browser
(release downloads have no CORS); its history JSON is built in the run (D-050).
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
from collections.abc import Callable
from datetime import date
from pathlib import Path

import duckdb

EVENT_COLUMNS = {
    "observed_at": "TIMESTAMPTZ",
    "store_id": "VARCHAR",
    "product_id": "BIGINT",
    "variant_id": "BIGINT",
    "handle": "VARCHAR",
    "product_title": "VARCHAR",
    "variant_title": "VARCHAR",
    "event": "VARCHAR",
    "old_price_cents": "BIGINT",
    "new_price_cents": "BIGINT",
    "old_compare_at_cents": "BIGINT",
    "new_compare_at_cents": "BIGINT",
    "price_change_pct": "DOUBLE",
}
SNAPSHOT_COLUMNS = {
    "store_id": "VARCHAR",
    "product_id": "BIGINT",
    "variant_id": "BIGINT",
    "handle": "VARCHAR",
    "product_title": "VARCHAR",
    "variant_title": "VARCHAR",
    "price_cents": "BIGINT",
    "compare_at_cents": "BIGINT",
    "available": "BOOLEAN",
    "valid_from": "TIMESTAMPTZ",
}


def tag(month: str) -> str:
    return f"history-{month}"


def to_parquet(csv_path: Path, columns: dict[str, str], out: Path, order: str) -> Path:
    """``csv_path`` as Parquet with typed columns, rows in a fixed order."""
    out.parent.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect()
    cols = "{" + ", ".join(f"'{k}': '{v}'" for k, v in columns.items()) + "}"
    # Column types and the order come from the constants above, never from input.
    rel = con.sql(
        f"SELECT * FROM read_csv(?, header = true, columns = {cols}) ORDER BY {order}",  # noqa: S608
        params=[str(csv_path)],
    )
    tmp = out.with_name(out.name + ".tmp")
    rel.write_parquet(str(tmp), compression="zstd")
    tmp.replace(out)
    return out


def git_month_snapshot(month: str, work: Path) -> Path | None:
    """The committed snapshot at the end of ``month`` (YYYY-MM), from git history."""
    y, m = (int(x) for x in month.split("-"))
    end = date(y + (m == 12), m % 12 + 1, 1).isoformat()
    git = shutil.which("git") or "git"
    # Fixed arguments; ``month`` was parsed into integers above.
    sha = subprocess.run(  # noqa: S603
        [
            git,
            "log",
            "-1",
            "--format=%H",
            f"--before={end}T00:00:00Z",
            "--",
            "data/latest/snapshot.csv",
        ],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()
    if not sha:
        return None
    text = subprocess.run(  # noqa: S603
        [git, "show", f"{sha}:data/latest/snapshot.csv"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    path = work / f"snapshot-{month}.csv"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def plan(
    data: Path,
    assets: dict[str, set[str]],
    today: date,
    out: Path,
    month_snapshot: Callable[[str, Path], Path | None] = git_month_snapshot,
) -> list[tuple[str, Path]]:
    """The files to upload: ``(tag, path)``, each one missing from ``assets``
    (tag -> asset names). Days before ``today`` and months before this one only."""
    todo: list[tuple[str, Path]] = []
    months: set[str] = set()
    for csv_path in sorted((data / "changes").glob("*/*.csv")):
        day = date.fromisoformat(csv_path.stem)
        month = f"{day:%Y-%m}"
        months.add(month)
        name = f"events-{day.isoformat()}.parquet"
        if day >= today or name in assets.get(tag(month), set()):
            continue
        todo.append(
            (
                tag(month),
                to_parquet(csv_path, EVENT_COLUMNS, out / name, "store_id, variant_id, event"),
            )
        )
    for month in sorted(months):
        name = f"snapshot-{month}.parquet"
        if month >= f"{today:%Y-%m}" or name in assets.get(tag(month), set()):
            continue
        source = month_snapshot(month, out / "src")
        if source is not None:
            todo.append(
                (
                    tag(month),
                    to_parquet(source, SNAPSHOT_COLUMNS, out / name, "store_id, variant_id"),
                )
            )
    return todo


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    p.add_argument("--data", type=Path, default=Path("data"))
    p.add_argument("--assets", type=Path, help="JSON: release tag -> asset names already there")
    p.add_argument("--today", type=date.fromisoformat, required=True, help="UTC date of the run")
    p.add_argument("--out", type=Path, default=Path("work/releases"))
    a = p.parse_args(argv)
    raw = json.loads(a.assets.read_text(encoding="utf-8")) if a.assets and a.assets.exists() else {}
    assets = {str(k): set(v) for k, v in raw.items()}
    for release, path in plan(a.data, assets, a.today, a.out):
        print(f"{release} {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
