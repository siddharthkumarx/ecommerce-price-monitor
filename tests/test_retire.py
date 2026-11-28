from __future__ import annotations

import csv
import json
import time
from pathlib import Path

from pricemon.retire import hide_store, leftovers, main, name_words
from pricemon.run import RunConfig, process
from pricemon.stores import load_retired
from tests.test_outputs import DAY1, DAY2, catalog, fetched

STORES = (
    "stores:\n"
    '  - {id: alphacorp, name: "Alphacorp", category: outdoor, host: www.alphacorp.example, '
    "terms: no_ban, public_no: 17}\n"
    "  - {id: beta, name: Beta, category: audio, host: beta.example, terms: no_ban, public_no: 2}\n"
)


def _alpha(price: str) -> list[dict[str, object]]:
    items = catalog(4, price)
    for p in items:
        p["title"] = f"Alphacorp {p['title']}"
        p["handle"] = f"alpha-tent-{p['id']}"
    return items


def _published(tmp_path: Path) -> tuple[Path, Path]:
    stores = tmp_path / "stores.yml"
    stores.write_text(STORES)
    cfg = RunConfig(stores=stores, data=tmp_path / "data")
    process(
        cfg,
        [fetched("alphacorp", _alpha("50.00"), DAY1), fetched("beta", catalog(3), DAY1)],
        DAY1,
        time.monotonic(),
    )
    process(
        cfg,
        [fetched("alphacorp", _alpha("40.00"), DAY2), fetched("beta", catalog(3), DAY2)],
        DAY2,
        time.monotonic(),
    )
    return stores, cfg.data


def test_hide_store_keys_every_data_file_by_number_without_the_name(tmp_path: Path) -> None:
    _, data = _published(tmp_path)
    words = name_words("alphacorp", "Alphacorp", "www.alphacorp.example")
    assert leftovers(data, words)
    changed = hide_store(data, "alphacorp", "store-017", words)
    assert data / "runs.jsonl" in changed
    assert leftovers(data, words) == []
    with (data / "latest" / "snapshot.csv").open() as fh:
        rows = [r for r in csv.DictReader(fh) if r["store_id"] == "store-017"]
    assert len(rows) == 4
    assert {r["handle"] for r in rows} == {""}
    assert rows[0]["product_title"].startswith("Product ")
    # Idempotent: a second pass changes nothing.
    assert hide_store(data, "alphacorp", "store-017", words) == []


def test_retire_hide_name_adds_the_retired_entry_and_the_next_run_closes_its_rows(
    tmp_path: Path,
) -> None:
    stores, data = _published(tmp_path)
    retired = tmp_path / "retired.yml"
    retired.write_text("retired:\n")
    code = main(
        [
            "--id", "alphacorp", "--reason", "Terms of Service ban robots (terms-001)",
            "--hide-name", "--on", "2026-11-06", "--stores", str(stores),
            "--retired", str(retired), "--data", str(data),
        ]
    )  # fmt: skip
    assert code == 0
    (entry,) = load_retired(retired)
    assert (entry.id, entry.name, entry.reason) == (
        "store-017",
        "Store #17",
        "Terms of Service ban robots (terms-001)",
    )
    # The list without the store, the retired entry with it: the next run closes its rows.
    stores.write_text(
        "stores:\n  - {id: beta, name: Beta, category: audio, host: beta.example, "
        "terms: no_ban, public_no: 2}\n" + retired.read_text()
    )
    day3 = DAY2.replace(day=6)
    cfg = RunConfig(stores=stores, data=data)
    code, rec = process(cfg, [fetched("beta", catalog(3), day3)], day3, time.monotonic())
    assert rec["retired_rows_closed"] == 4
    assert rec["events"]["removed"] == 0
    words = name_words("alphacorp", "Alphacorp", "www.alphacorp.example")
    assert leftovers(data, words) == []
    history = (data / "changes" / "2026" / "2026-11-05.csv").read_text()
    assert "store-017" in history  # the history stays, by number
    assert json.loads((data / "runs.jsonl").read_text().splitlines()[0])["stores_total"] == 2


def test_name_words_cover_a_bracketed_name_and_the_host() -> None:
    words = name_words("soundcore-us", "Soundcore (US)", "us.soundcore.com")
    assert {"Soundcore", "soundcore", "soundcore-us"} <= words
    assert "us" not in words
    words = name_words("bluelounge", "Bluelounge", "shopadvantus.com")
    assert "advantus" in words
    assert "Equator" in name_words("equator-coffees", "Equator Coffees", "equatorcoffees.com")
