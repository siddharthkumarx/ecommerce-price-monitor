"""Retire a store, once, by hand (D-044).

    python -m pricemon.retire --id <store-id> --reason "<why>" [--hide-name]

A store that leaves the monitor on purpose is retired: it gets an entry in
``config/retired.yml`` with the date and the reason, no run reads it again, its rows
leave the live snapshot in the next run and its history stays in ``data/``.

``--hide-name`` is for a store whose Terms of Service turned out to ban robots
(D-040): it is retired under a new number (``store-309``, never given twice) and
this command rewrites the committed public data once, so no
data file names it: the snapshot, the change logs and the run log are keyed by the
number, product handles and the store's host are emptied, and the store's name is
taken out of product titles and failure reasons. The command ends by searching
``data/`` for the name and prints every file that still holds it.
"""

from __future__ import annotations

import argparse
import csv
import io
import json
import re
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Any

import yaml

HIDDEN = "(shown without its name)"


def alias_id(public_no: int) -> str:
    return f"store-{public_no:03d}"


_HOST_AFFIXES = ("shop", "store", "get", "try", "the", "my", "usa", "hq", "co")


def name_words(store_id: str, name: str, host: str) -> set[str]:
    """The words that name a store: its name (also without a bracketed suffix such as
    "(US)") and its first word, its id, and its host labels with and without a
    shop-style prefix or suffix ("shopadvantus" -> "advantus"), 3 letters or more.
    Scrubbing is applied to the hidden store's own rows only, so a common first word
    ("Yoga") is taken out of its titles too: an accepted cost (D-044)."""
    plain = re.sub(r"\s*\(.*?\)\s*", " ", name).strip()
    words = {name, plain, store_id}
    first = plain.split()[0] if plain.split() else ""
    if len(first) >= 4:
        words.add(first)
    for label in host.lower().split(".")[:-1]:
        if label in {"www", "shop", "store", "us", "en"}:
            continue
        words.add(label)
        for affix in _HOST_AFFIXES:
            if label.startswith(affix) and len(label) - len(affix) >= 4:
                words.add(label[len(affix) :])
            if label.endswith(affix) and len(label) - len(affix) >= 4:
                words.add(label[: -len(affix)])
    return {w for w in words if len(w) >= 3}


def _pattern(words: set[str]) -> re.Pattern[str]:
    alt = "|".join(re.escape(w) for w in sorted(words, key=len, reverse=True))
    return re.compile(rf"(?i)\b(?:{alt})\b")


def scrub(text: str, pattern: re.Pattern[str], fallback: str = "Product") -> str:
    """``text`` without the store's own name."""
    if not text:
        return text
    cleaned = re.sub(r"\s{2,}", " ", pattern.sub("", text)).strip(" -\u2013|:")
    return cleaned or fallback


def _rewrite_csv(path: Path, old: str, new: str, pattern: re.Pattern[str]) -> bool:
    reader = csv.DictReader(io.StringIO(path.read_text(encoding="utf-8")))
    fields = list(reader.fieldnames or [])
    rows = list(reader)
    dirty = False
    for row in rows:
        if row.get("store_id") != old:
            continue
        dirty = True
        row["store_id"] = new
        if "handle" in row:
            row["handle"] = ""
        for key in ("product_title", "variant_title"):
            if key in row:
                row[key] = scrub(
                    row[key], pattern, "Default" if key == "variant_title" else "Product"
                )
    if not dirty:
        return False
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=fields, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    path.write_text(buf.getvalue(), encoding="utf-8")
    return True


def _hide_entry(entry: dict[str, Any], new: str, pattern: re.Pattern[str]) -> None:
    entry["store_id"] = new
    if "host" in entry:
        entry["host"] = ""
    if entry.get("reason"):
        text = re.sub(r"https?://\S+", "a store URL", str(entry["reason"]))
        entry["reason"] = scrub(
            re.sub(r"(^|; )[a-z0-9][a-z0-9-]*: ", r"\1a product: ", text), pattern
        )
    for w in entry.get("witnesses") or []:
        w["handle"] = ""
    if entry.get("content_flags"):
        entry["content_flags"] = {k: [HIDDEN] * len(v) for k, v in entry["content_flags"].items()}
    if entry.get("jsonld_disagrees"):
        entry["jsonld_disagrees"] = [HIDDEN for _ in entry["jsonld_disagrees"]]


def _hide_run(record: dict[str, Any], old: str, new: str, pattern: re.Pattern[str]) -> None:
    for key in ("stores", "stores_not_updated"):
        for entry in record.get(key) or []:
            if entry.get("store_id") == old:
                _hide_entry(entry, new, pattern)
    if record.get("stores_added"):
        record["stores_added"] = [new if x == old else x for x in record["stores_added"]]
    if old in (record.get("reject_examples") or {}):
        examples = record["reject_examples"].pop(old)
        record["reject_examples"][new] = [HIDDEN for _ in examples]
    guard = record.get("guard") or {}
    if guard.get("keys"):
        guard["keys"] = [re.sub(rf":{re.escape(old)}$", f":{new}", k) for k in guard["keys"]]
    for hold in guard.get("holds") or []:
        if isinstance(hold, dict):
            hold["key"] = re.sub(rf":{re.escape(old)}$", f":{new}", str(hold.get("key", "")))
            if hold.get("message", "").startswith(f"{old}:"):
                hold["message"] = new + scrub(hold["message"][len(old) :], pattern, "")


def hide_store(data: Path, old: str, new: str, words: set[str]) -> list[Path]:
    """Key every committed public data file by ``new`` instead of ``old``, without
    the store's name, host or product handles; the files changed."""
    pattern = _pattern(words)
    changed: list[Path] = []
    csvs = [data / "latest" / "snapshot.csv", *sorted((data / "changes").glob("*/*.csv"))]
    for path in csvs:
        if path.exists() and _rewrite_csv(path, old, new, pattern):
            changed.append(path)
    runs = data / "runs.jsonl"
    if runs.exists():
        out: list[str] = []
        dirty = False
        for line in runs.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            record = json.loads(line)
            before = json.dumps(record, sort_keys=True)
            _hide_run(record, old, new, pattern)
            if json.dumps(record, sort_keys=True) != before:
                dirty = True
                line = json.dumps(record, sort_keys=True, separators=(",", ":"))
            out.append(line)
        if dirty:
            runs.write_text("\n".join(out) + "\n", encoding="utf-8")
            changed.append(runs)
    return changed


def leftovers(data: Path, words: set[str]) -> list[Path]:
    """Files under ``data`` that still hold one of ``words``."""
    pattern = _pattern(words)
    return [
        p
        for p in sorted(data.rglob("*"))
        if p.is_file()
        and p.suffix in (".csv", ".json", ".jsonl")
        and pattern.search(p.read_text(encoding="utf-8"))
    ]


def retired_entry(store_id: str, name: str, category: str, on: date, reason: str) -> str:
    return (
        f"  - id: {store_id}\n"
        f"    name: {json.dumps(name)}\n"
        f"    category: {category}\n"
        f"    retired_on: {on.isoformat()}\n"
        f"    reason: {json.dumps(reason)}\n"
    )


def next_number(retired: Path) -> int:
    """The next number for a store retired by number: above every number given so far
    (the retired ``store-NNN`` ids, and 308, the highest number of the old alias
    registry, D-034, deleted in D-046), so a number is never given twice."""
    used = [308]
    if retired.exists():
        for r in (yaml.safe_load(retired.read_text(encoding="utf-8")) or {}).get("retired") or []:
            m = re.fullmatch(r"store-(\d+)", str(r["id"]))
            if m:
                used.append(int(m.group(1)))
    return max(used) + 1


def withdraw_store(data: Path, store_id: str) -> list[Path]:
    """Take one store out of the committed public data, once, by hand (D-049): its
    rows leave the snapshot and the change logs, its entries leave the run log. Run
    totals stay as they were measured; each run record it left says so in
    ``withdrawn_stores``."""
    changed: list[Path] = []
    for path in [data / "latest" / "snapshot.csv", *sorted((data / "changes").glob("*/*.csv"))]:
        if not path.exists():
            continue
        reader = csv.DictReader(io.StringIO(path.read_text(encoding="utf-8")))
        rows = list(reader)
        keep = [r for r in rows if r.get("store_id") != store_id]
        if len(keep) != len(rows):
            buf = io.StringIO()
            writer = csv.DictWriter(
                buf, fieldnames=list(reader.fieldnames or []), lineterminator="\n"
            )
            writer.writeheader()
            writer.writerows(keep)
            path.write_text(buf.getvalue(), encoding="utf-8")
            changed.append(path)
    runs = data / "runs.jsonl"
    if runs.exists():
        out: list[str] = []
        dirty = False
        for line in runs.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            record = json.loads(line)
            hit = False
            for key in ("stores", "stores_not_updated"):
                entries = record.get(key) or []
                kept = [s for s in entries if s.get("store_id") != store_id]
                if len(kept) != len(entries):
                    record[key] = kept
                    hit = True
            if store_id in (record.get("stores_added") or []):
                record["stores_added"] = [x for x in record["stores_added"] if x != store_id]
                hit = True
            if store_id in (record.get("reject_examples") or {}):
                del record["reject_examples"][store_id]
                hit = True
            if hit:
                record["withdrawn_stores"] = int(record.get("withdrawn_stores") or 0) + 1
                line = json.dumps(record, sort_keys=True, separators=(",", ":"))
                dirty = True
            out.append(line)
        if dirty:
            runs.write_text("\n".join(out) + "\n", encoding="utf-8")
            changed.append(runs)
    return changed


def restore_store(data: Path, hidden_id: str, store_id: str) -> list[Path]:
    """Undo ``--hide-name`` once (D-055): key the committed data by ``store_id`` again.
    Handles and product titles stay as they were written (the scrubbed words cannot
    be put back); the store's next run refreshes its rows."""
    changed: list[Path] = []
    for path in [data / "latest" / "snapshot.csv", *sorted((data / "changes").glob("*/*.csv"))]:
        if not path.exists():
            continue
        reader = csv.DictReader(io.StringIO(path.read_text(encoding="utf-8")))
        rows = list(reader)
        if not any(r.get("store_id") == hidden_id for r in rows):
            continue
        for r in rows:
            if r.get("store_id") == hidden_id:
                r["store_id"] = store_id
        buf = io.StringIO()
        writer = csv.DictWriter(buf, fieldnames=list(reader.fieldnames or []), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
        path.write_text(buf.getvalue(), encoding="utf-8")
        changed.append(path)
    runs = data / "runs.jsonl"
    if runs.exists():
        out: list[str] = []
        dirty = False
        for line in runs.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            if hidden_id not in line:
                out.append(line)
                continue
            record = json.loads(line)
            for key in ("stores", "stores_not_updated"):
                for entry in record.get(key) or []:
                    if entry.get("store_id") == hidden_id:
                        entry["store_id"] = store_id
            if record.get("stores_added"):
                record["stores_added"] = [
                    store_id if x == hidden_id else x for x in record["stores_added"]
                ]
            if hidden_id in (record.get("reject_examples") or {}):
                record["reject_examples"][store_id] = record["reject_examples"].pop(hidden_id)
            guard = record.get("guard") or {}
            suffix = re.compile(rf":{re.escape(hidden_id)}$")
            guard["keys"] = [suffix.sub(f":{store_id}", k) for k in guard.get("keys") or []]
            for hold in guard.get("holds") or []:
                if isinstance(hold, dict):
                    hold["key"] = suffix.sub(f":{store_id}", str(hold.get("key", "")))
            out.append(json.dumps(record, sort_keys=True, separators=(",", ":")))
            dirty = True
        if dirty:
            runs.write_text("\n".join(out) + "\n", encoding="utf-8")
            changed.append(runs)
    return changed


def drop_retired_entry(retired: Path, store_id: str) -> bool:
    """Take the entry of ``store_id`` out of the retired list, keeping every other line."""
    lines = retired.read_text(encoding="utf-8").splitlines(keepends=True)
    start = next((i for i, x in enumerate(lines) if x.strip() == f"- id: {store_id}"), None)
    if start is None:
        return False
    end = start + 1
    while end < len(lines) and lines[end].startswith("    "):
        end += 1
    retired.write_text("".join(lines[:start] + lines[end:]), encoding="utf-8")
    return True


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    p.add_argument("--id", required=True, help="the store's id in config/stores.yml (or data)")
    p.add_argument("--reason", help="why it leaves (required to retire)")
    mode = p.add_mutually_exclusive_group()
    mode.add_argument("--hide-name", action="store_true", help="retire under a number (Terms ban)")
    mode.add_argument(
        "--withdraw", action="store_true", help="take it out of the public data instead"
    )
    mode.add_argument(
        "--restore", metavar="STORE_NNN", help="bring back a store retired by number as --id"
    )
    p.add_argument("--on", type=date.fromisoformat, default=datetime.now(UTC).date())
    p.add_argument("--stores", type=Path, default=Path("config/stores.yml"))
    p.add_argument("--retired", type=Path, default=Path("config/retired.yml"))
    p.add_argument("--data", type=Path, default=Path("data"))
    a = p.parse_args(argv)
    if a.restore:
        if not drop_retired_entry(a.retired, a.restore):
            p.error(f"{a.restore} is not in {a.retired}")
        for path in restore_store(a.data, a.restore, a.id):
            print(f"rewritten: {path}")
        print(f"restored {a.restore} as {a.id}; regenerate config/stores.yml next")
        return 0
    if a.withdraw:
        for path in withdraw_store(a.data, a.id):
            print(f"rewritten: {path}")
        print(f"withdrew {a.id} from {a.data}")
        return 0
    if not a.reason:
        p.error("--reason is required to retire a store")
    raw = yaml.safe_load(a.stores.read_text(encoding="utf-8")) or {}
    store = next((s for s in raw.get("stores") or [] if str(s["id"]) == a.id), None)
    if store is None:
        p.error(f"{a.id} is not in {a.stores}")
    name, category, host = str(store["name"]), str(store["category"]), str(store["host"])
    if a.hide_name:
        number = next_number(a.retired)
        new_id, shown = alias_id(number), f"Store #{number}"
        words = name_words(a.id, name, host)
        for path in hide_store(a.data, a.id, new_id, words):
            print(f"rewritten: {path}")
        left = leftovers(a.data, words)
        for path in left:
            print(f"still names the store: {path}")
    else:
        new_id, shown, left = a.id, name, []
    with a.retired.open("a", encoding="utf-8") as fh:
        fh.write(retired_entry(new_id, shown, category, a.on, a.reason))
    print(f"retired {a.id} as {new_id} on {a.on}; regenerate config/stores.yml next")
    return 1 if left else 0


if __name__ == "__main__":
    raise SystemExit(main())
