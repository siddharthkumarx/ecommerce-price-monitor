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
"""

from __future__ import annotations

import csv
import io
import json
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


def _rewrite_csv(path: Path, display: Display, mapping: dict[str, str]) -> bool:
    text = path.read_text(encoding="utf-8")
    reader = csv.DictReader(io.StringIO(text))
    fields = list(reader.fieldnames or [])
    rows = list(reader)
    new_rows = [_rekey_row(display, mapping, r) for r in rows]
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
    if record.get("stores_added"):
        record["stores_added"] = [mapping.get(x, x) for x in record["stores_added"]]
    if record.get("reject_examples"):
        examples: dict[str, list[str]] = {}
        for sid, items in record["reject_examples"].items():
            new = mapping.get(sid, sid)
            examples[new] = public_examples(display, new, list(items))
        record["reject_examples"] = examples


def rekey_files(data: Path, display: Display) -> list[Path]:
    """Bring the snapshot, the change logs and the run log to the current keys."""
    mapping = display.rekey()
    changed: list[Path] = []
    csvs = [data / "latest" / "snapshot.csv", *sorted((data / "changes").glob("*/*.csv"))]
    for path in csvs:
        if path.exists() and _rewrite_csv(path, display, mapping):
            changed.append(path)
    runs = data / "runs.jsonl"
    if runs.exists():
        lines = [line for line in runs.read_text(encoding="utf-8").splitlines() if line.strip()]
        out = []
        dirty = False
        for line in lines:
            record = json.loads(line)
            before = json.dumps(record, sort_keys=True)
            _rekey_run(display, mapping, record)
            if json.dumps(record, sort_keys=True) != before:
                dirty = True
                line = json.dumps(record, sort_keys=True, separators=(",", ":"))
            out.append(line)
        # Only lines whose keys changed are rewritten; the others keep their bytes.
        if dirty:
            runs.write_text("\n".join(out) + "\n", encoding="utf-8")
            changed.append(runs)
    return changed


def rekey_month(con: duckdb.DuckDBPyConnection, display: Display) -> int:
    """Rekey the month's Parquet history, loaded as table ``month_prev``; rows changed."""
    changed = 0
    for old, new in display.rekey().items():
        res = con.execute("UPDATE month_prev SET store_id = ? WHERE store_id = ?", [new, old])
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
