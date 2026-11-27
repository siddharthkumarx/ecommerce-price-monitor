"""Public data files never name a store that is shown without its name (D-034).

A store whose recon ``terms`` value is in ``anonymise_terms`` (``config/public.yml``)
is keyed in every public data file by its alias id (``store-017``) instead of its
config id, with an empty handle and its name taken out of product and variant
titles. That covers the shard files (Actions artifacts), the snapshot, the change
log, the run log (and so ``status.json`` and the badges, built from it), the monthly
Parquet history and the ``latest-prices.csv`` release asset (a copy of the snapshot).

* :func:`public_fetch` turns one store's fetch into that form before anything is
  written, so no raw copy of such a store reaches a public file.
* :func:`rekey_files` and :func:`rekey_month` move files written before a store was
  anonymised (or after it stopped being) to the right key. Both are idempotent: on
  an unchanged config they change nothing.
* Both also withdraw every store that is neither monitored nor retired (D-036): its
  rows leave the snapshot, the change logs and the Parquet history, and its entries
  leave the run log, whose totals are reduced by what that store contributed (store
  counts, requests and change events exactly; observed rows by its variant count).
  A store that leaves the list keeps its history only if it is retired.
"""

from __future__ import annotations

import csv
import io
import json
import re
from collections import Counter, defaultdict
from dataclasses import replace
from pathlib import Path
from typing import Any

import duckdb

from pricemon.display import Display
from pricemon.fetch import StoreFetch
from pricemon.models import VariantRow

HIDDEN = "(shown without its name)"
# A placeholder handle that passes row validation; replaced by "" after it.
PLACEHOLDER_HANDLE = "-"


def public_fetch(display: Display, fetch: StoreFetch) -> StoreFetch:
    """The fetch as public files may hold it: unchanged for a store shown by name."""
    sid = fetch.store_id
    if not display.is_anonymised(sid):
        return fetch
    products = []
    for p in fetch.products:
        variants = [
            {**v, "title": display.title(sid, str(v.get("title") or ""))}
            for v in p.get("variants") or []
        ]
        products.append(
            {
                **p,
                "handle": PLACEHOLDER_HANDLE,
                "title": display.title(sid, str(p.get("title") or "")),
                "product_type": "",
                "tags": [],
                "variants": variants,
            }
        )
    return replace(
        fetch,
        store_id=display.data_id(sid),
        host="",
        reason=display.reason(sid, fetch.reason),
        products=products,
        witnesses=[replace(w, handle="") for w in fetch.witnesses],
        content_flags={k: [HIDDEN] * len(v) for k, v in fetch.content_flags.items()},
        jsonld_disagrees=[HIDDEN for _ in fetch.jsonld_disagrees],
    )


def public_rows(display: Display, rows: list[VariantRow]) -> list[VariantRow]:
    """Rows of an anonymised store get an empty handle (titles are already scrubbed)."""
    return [
        r.model_copy(update={"handle": ""}) if display.is_anonymised(r.store_id) else r
        for r in rows
    ]


def public_examples(display: Display, store_id: str, examples: list[str]) -> list[str]:
    return [HIDDEN for _ in examples] if display.is_anonymised(store_id) else examples


# -- files written before the current config --------------------------------------
def _rekey_row(display: Display, mapping: dict[str, str], row: dict[str, str]) -> dict[str, str]:
    sid = row.get("store_id", "")
    new = mapping.get(sid, sid)
    if new == sid and not display.is_anonymised(sid):
        return row
    out = dict(row)
    out["store_id"] = new
    if display.is_anonymised(new):
        if "handle" in out:
            out["handle"] = ""
        for key in ("product_title", "variant_title"):
            if key in out:
                out[key] = display.title(new, out[key])
    return out


def _read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    reader = csv.DictReader(io.StringIO(path.read_text(encoding="utf-8")))
    return list(reader.fieldnames or []), list(reader)


def _rewrite_csv(
    path: Path, display: Display, mapping: dict[str, str], known: set[str] | None
) -> bool:
    fields, rows = _read_csv(path)
    new_rows = [_rekey_row(display, mapping, r) for r in rows]
    if known:
        new_rows = [r for r in new_rows if r.get("store_id", "") in known]
    if new_rows == rows:
        return False
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=fields, lineterminator="\n")
    writer.writeheader()
    writer.writerows(new_rows)
    path.write_text(buf.getvalue(), encoding="utf-8")
    return True


def _rekey_store_entry(display: Display, mapping: dict[str, str], s: dict[str, Any]) -> None:
    sid = str(s.get("store_id") or "")
    s["store_id"] = mapping.get(sid, sid)
    if display.is_anonymised(s["store_id"]):
        if "host" in s:
            s["host"] = ""
        if s.get("reason"):
            s["reason"] = display.reason(s["store_id"], str(s["reason"]))
        for w in s.get("witnesses") or []:
            w["handle"] = ""
        if s.get("content_flags"):
            s["content_flags"] = {k: [HIDDEN] * len(v) for k, v in s["content_flags"].items()}
        if s.get("jsonld_disagrees"):
            s["jsonld_disagrees"] = [HIDDEN for _ in s["jsonld_disagrees"]]


def _rekey_run(display: Display, mapping: dict[str, str], record: dict[str, Any]) -> None:
    for s in record.get("stores") or []:
        _rekey_store_entry(display, mapping, s)
    for s in record.get("stores_not_updated") or []:
        sid = str(s.get("store_id") or "")
        s["store_id"] = mapping.get(sid, sid)
        if s.get("reason") and display.is_anonymised(s["store_id"]):
            s["reason"] = display.reason(s["store_id"], str(s["reason"]))
    if record.get("stores_added"):
        record["stores_added"] = [mapping.get(x, x) for x in record["stores_added"]]
    if record.get("reject_examples"):
        examples: dict[str, list[str]] = {}
        for sid, items in record["reject_examples"].items():
            new = mapping.get(sid, sid)
            examples[new] = public_examples(display, new, list(items))
        record["reject_examples"] = examples


def _mentions(value: Any, ids: set[str]) -> bool:
    text = json.dumps(value, ensure_ascii=False)
    return any(re.search(rf"(?<![\w-]){re.escape(i)}(?![\w-])", text) for i in ids)


def _withdraw_run(record: dict[str, Any], known: set[str], events: dict[Any, Counter[str]]) -> None:
    """Take the entries of stores that left (neither monitored nor retired) out of one
    run record and reduce its totals by what they contributed (D-036)."""
    stores = record.get("stores") or []
    not_updated = record.get("stores_not_updated") or []
    gone = [s for s in stores if str(s.get("store_id") or "") not in known]
    gone_nu = [s for s in not_updated if str(s.get("store_id") or "") not in known]
    gone_ids = {str(s.get("store_id") or "") for s in gone + gone_nu}
    gone_ids |= {x for x in record.get("stores_added") or [] if x not in known}
    gone_ids |= {x for x in record.get("reject_examples") or {} if x not in known}
    if not gone_ids:
        return
    record["stores"] = [s for s in stores if s not in gone]
    record["stores_not_updated"] = [s for s in not_updated if s not in gone_nu]
    if "stores_total" in record:
        # A failed store is in both lists: count each store once.
        listed = {str(s.get("store_id") or "") for s in gone + gone_nu}
        record["stores_total"] = max(0, int(record["stores_total"]) - len(listed))
    if "stores_ok" in record:
        ok = sum(1 for s in gone if s.get("status") == "ok")
        record["stores_ok"] = max(0, int(record["stores_ok"]) - ok)
    if "requests" in record:
        req = sum(int(s.get("requests") or 0) for s in gone)
        record["requests"] = max(0, int(record["requests"]) - req)
    rows = sum(int(s.get("variants") or 0) for s in gone if s.get("status") == "ok")
    for key in ("rows_observed", "rows_live"):
        if key in record:
            record[key] = max(0, int(record[key]) - rows)
    counts: Counter[str] = Counter()
    for sid in gone_ids:
        counts += events.get((record.get("started_at"), sid), Counter())
    for event, n in counts.items():
        if event in (record.get("events") or {}):
            record["events"][event] = max(0, int(record["events"][event]) - n)
    if record.get("stores_added"):
        record["stores_added"] = [x for x in record["stores_added"] if x in known]
    if record.get("reject_examples"):
        record["reject_examples"] = {
            k: v for k, v in record["reject_examples"].items() if k in known
        }
    guard = record.get("guard") or {}
    for key in ("holds", "keys"):
        if guard.get(key):
            guard[key] = [h for h in guard[key] if not _mentions(h, gone_ids)]
    record["withdrawn_stores"] = int(record.get("withdrawn_stores") or 0) + len(gone_ids)


def withdraw_ids(display: Display, present: set[str]) -> set[str] | None:
    """The store keys public data keeps, or None when nothing may be withdrawn (D-036).

    Withdrawing deletes data, so it happens only with a store list (at least one
    monitored store; retired stores alone do not count) and never for more stores
    than are listed: a wrong or truncated store list then leaves the data alone.
    """
    if not display.stores:
        return None
    known = display.public_ids
    leaving = present - known
    if len(leaving) > len(display.stores):
        print(
            f"public data: {len(leaving)} stores would be withdrawn with only "
            f"{len(display.stores)} listed; nothing withdrawn (check config/stores.yml)",
            flush=True,
        )
        return None
    return known


def rekey_files(data: Path, display: Display) -> list[Path]:
    """Bring the snapshot, the change logs and the run log to the current keys, and
    withdraw every store that is neither monitored nor retired (D-036)."""
    mapping = display.rekey()
    changed: list[Path] = []
    csvs = [data / "latest" / "snapshot.csv", *sorted((data / "changes").glob("*/*.csv"))]
    snapshot_ids: set[str] = set()
    if csvs[0].exists():
        snapshot_ids = {
            mapping.get(r.get("store_id", ""), r.get("store_id", "")) for r in _read_csv(csvs[0])[1]
        }
    known = withdraw_ids(display, snapshot_ids)
    # Change events of stores that left, by run time, to reduce the run totals once.
    events: dict[Any, Counter[str]] = defaultdict(Counter)
    for path in csvs[1:]:
        if known and path.exists():
            for r in _read_csv(path)[1]:
                sid = mapping.get(r.get("store_id", ""), r.get("store_id", ""))
                if sid not in known:
                    events[(r.get("observed_at"), sid)][r.get("event", "")] += 1
    runs = data / "runs.jsonl"
    # The run log first: it needs the change events that the CSV pass takes out.
    if runs.exists():
        lines = [line for line in runs.read_text(encoding="utf-8").splitlines() if line.strip()]
        out = []
        dirty = False
        for line in lines:
            record = json.loads(line)
            before = json.dumps(record, sort_keys=True)
            _rekey_run(display, mapping, record)
            if known:
                _withdraw_run(record, known, events)
            if json.dumps(record, sort_keys=True) != before:
                dirty = True
                line = json.dumps(record, sort_keys=True, separators=(",", ":"))
            out.append(line)
        # Only lines whose keys changed are rewritten; the others keep their bytes.
        if dirty:
            runs.write_text("\n".join(out) + "\n", encoding="utf-8")
            changed.append(runs)
    for path in csvs:
        if path.exists() and _rewrite_csv(path, display, mapping, known):
            changed.append(path)
    return changed


def rekey_month(con: duckdb.DuckDBPyConnection, display: Display) -> int:
    """Rekey the month's Parquet history, loaded as table ``month_prev``; rows changed."""
    changed = 0
    for old, new in display.rekey().items():
        res = con.execute("UPDATE month_prev SET store_id = ? WHERE store_id = ?", [new, old])
        changed += int((res.fetchone() or [0])[0])
    present = {
        str(r[0]) for r in con.execute("SELECT DISTINCT store_id FROM month_prev").fetchall()
    }
    allowed = withdraw_ids(display, present)
    known = sorted(allowed or ())
    if known:
        # Stores that are neither monitored nor retired leave the history (D-036).
        con.execute("CREATE OR REPLACE TEMP TABLE known_ids (store_id VARCHAR)")
        con.executemany("INSERT INTO known_ids VALUES (?)", [[k] for k in known])
        res = con.execute(
            "DELETE FROM month_prev WHERE store_id NOT IN (SELECT store_id FROM known_ids)"
        )
        changed += int((res.fetchone() or [0])[0])
    hidden = sorted({display.data_id(s) for s in display.anonymised_ids})
    if not hidden:
        return changed
    con.execute("CREATE OR REPLACE TEMP TABLE hidden_ids (store_id VARCHAR)")
    con.executemany("INSERT INTO hidden_ids VALUES (?)", [[h] for h in hidden])
    res = con.execute(
        "UPDATE month_prev SET handle = '' "
        "WHERE handle <> '' AND store_id IN (SELECT store_id FROM hidden_ids)"
    )
    changed += int((res.fetchone() or [0])[0])
    titles = con.execute(
        "SELECT DISTINCT store_id, product_title, variant_title FROM month_prev "
        "WHERE store_id IN (SELECT store_id FROM hidden_ids)"
    ).fetchall()
    for sid, product, variant in titles:
        p2, v2 = display.title(sid, product or ""), display.title(sid, variant or "")
        if (p2, v2) != (product, variant):
            res = con.execute(
                "UPDATE month_prev SET product_title = ?, variant_title = ? "
                "WHERE store_id = ? AND product_title = ? AND variant_title = ?",
                [p2, v2, sid, product, variant],
            )
            changed += int((res.fetchone() or [0])[0])
    return changed


# -- earlier months ---------------------------------------------------------------
def rekey_month_file(parquet: Path, display: Display) -> int:
    """Rekey and withdraw an earlier month's Parquet file in place; rows changed.

    The daily run rewrites only the current month (``rekey_month``); earlier release
    assets are brought to the same keys by this step of the workflow (D-036).
    """
    con = duckdb.connect()
    con.execute(
        "CREATE TABLE month_prev AS SELECT * FROM read_parquet(?) "
        "ORDER BY store_id, product_id, variant_id, valid_from",
        [str(parquet)],
    )
    changed = rekey_month(con, display)
    if changed:
        tmp = parquet.with_name(parquet.name + ".tmp")
        con.table("month_prev").order("store_id, product_id, variant_id, valid_from").write_parquet(
            str(tmp), compression="zstd"
        )
        tmp.replace(parquet)
    return changed


def rekey_csv_file(path: Path, display: Display) -> bool:
    """Rekey and withdraw an earlier month's ``latest-prices.csv`` in place."""
    mapping = display.rekey()
    ids = {mapping.get(r.get("store_id", ""), r.get("store_id", "")) for r in _read_csv(path)[1]}
    return _rewrite_csv(path, display, mapping, withdraw_ids(display, ids))


def main(argv: list[str] | None = None) -> int:
    import argparse

    from pricemon.display import load_display

    p = argparse.ArgumentParser(
        description="Bring an earlier month's release files to the keys of the current store list."
    )
    p.add_argument("--stores", type=Path, default=Path("config/stores.yml"))
    p.add_argument("--public", type=Path, default=Path("config/public.yml"))
    p.add_argument("--parquet", type=Path)
    p.add_argument("--csv", type=Path)
    a = p.parse_args(argv)
    display = load_display(a.stores, a.public)
    changed = 0
    if a.parquet and a.parquet.exists():
        rows = rekey_month_file(a.parquet, display)
        print(f"{a.parquet.name}: {rows} rows changed")
        changed += rows
    if a.csv and a.csv.exists():
        dirty = rekey_csv_file(a.csv, display)
        print(f"{a.csv.name}: {'changed' if dirty else 'unchanged'}")
        changed += int(dirty)
    # Exit 3 tells the workflow there is something to upload.
    return 3 if changed else 0


if __name__ == "__main__":
    raise SystemExit(main())
