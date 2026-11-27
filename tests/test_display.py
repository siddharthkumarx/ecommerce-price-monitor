"""The public display rule (D-031): stores whose terms ban robots are shown by number,
and retired stores are labelled, on every public surface."""

from __future__ import annotations

import csv
import json
import time
from datetime import UTC, date, datetime
from pathlib import Path

import pytest

from pricemon.display import Display, anonymise_setting
from pricemon.feed import publish
from pricemon.readme import context, render
from pricemon.run import RunConfig, process
from pricemon.site import build
from pricemon.stores import RetiredStore, Store, load_retired, load_stores
from pricemon.visuals import write_all
from tests.test_outputs import DAY1, DAY2, catalog, fetched

ROOT = Path(__file__).resolve().parents[1]
NOW = datetime(2026, 11, 5, 7, 0, tzinfo=UTC)

# Day 1: Alphacorp's terms were not read yet (shown by name); day 2: recon found a
# ban, so from then on every public file keys it as store-017 (D-034).
BEFORE = (
    "stores:\n"
    '  - {id: alphacorp, name: "Alphacorp", category: outdoor, host: www.alphacorp.example, '
    "terms: none_found, public_no: 17}\n"
    "  - {id: beta, name: Beta, category: audio, host: beta.example, terms: no_ban, public_no: 2}\n"
    "  - {id: gamma, name: Gamma, category: audio, host: gamma.example, terms: none_found, "
    "public_no: 3}\n"
)
AFTER = (
    "stores:\n"
    '  - {id: alphacorp, name: "Alphacorp", category: outdoor, host: www.alphacorp.example, '
    "terms: ban, public_no: 17}\n"
    "  - {id: beta, name: Beta, category: audio, host: beta.example, terms: no_ban, public_no: 2}\n"
    "retired:\n"
    "  - {id: gamma, name: Gamma, category: audio, retired_on: 2026-11-05}\n"
)
SECRETS = ("alphacorp", "alpha-tent")  # name and slug, host, and the product handle


def _alpha_catalog(price: str) -> list[dict[str, object]]:
    items = catalog(6, price)
    for p in items:
        p["title"] = f"Alphacorp {p['title']}"
        p["handle"] = f"alpha-tent-{p['id']}"
        p["tags"] = ["Alphacorp"]
    return items


@pytest.fixture
def published(tmp_path: Path) -> tuple[Path, Path]:
    stores = tmp_path / "stores.yml"
    stores.write_text(BEFORE)
    cfg = RunConfig(
        stores=stores, data=tmp_path / "data", history_out=tmp_path / "release" / "month.parquet"
    )
    process(
        cfg,
        [
            fetched("alphacorp", _alpha_catalog("50.00"), DAY1),
            fetched("beta", catalog(4), DAY1),
            fetched("gamma", catalog(3), DAY1),
        ],
        DAY1,
        time.monotonic(),
    )
    stores.write_text(AFTER)
    cfg = RunConfig(
        stores=stores,
        data=tmp_path / "data",
        history_in=tmp_path / "release" / "month.parquet",
        history_out=tmp_path / "release" / "month.parquet",
    )
    process(
        cfg,
        [fetched("alphacorp", _alpha_catalog("40.00"), DAY2), fetched("beta", catalog(4), DAY2)],
        DAY2,
        time.monotonic(),
    )
    return stores, cfg.data


def test_names_hosts_and_titles(tmp_path: Path) -> None:
    stores = [
        Store("a", "Alphacorp", "outdoor", "www.alphacorp.example", terms="ban", public_no=7),
        Store("b", "Beta", "audio", "beta.example", terms="none_found", public_no=8),
        Store("c", "Gear Co", "pet", "gear.example", terms="ban", public_no=21),
    ]
    retired = [RetiredStore("old", "Oldie", "audio", date(2026, 11, 27))]
    d = Display(stores, retired, ("ban",))
    assert d.name("a") == "Store #7 (Outdoor)"
    assert d.name("store-007") == "Store #7 (Outdoor)"
    assert d.data_id("a") == "store-007"
    assert d.data_id("b") == "b"
    assert d.name("c") == "Store #21 (Pet)"
    assert d.name("b") == "Beta"
    assert d.name("old") == "Oldie"
    assert retired[0].label == "retired on 27 Nov 2026"
    assert (d.host("a"), d.product_url("a", "x")) == ("", "")
    assert d.product_url("b", "x") == "https://beta.example/products/x"
    assert d.title("a", "Alphacorp Trail Tent - 2P") == "Trail Tent - 2P"
    assert d.title("a", "ALPHACORP") == "Product"
    assert d.title("b", "Beta Buds") == "Beta Buds"
    # The setting can name nothing (everyone by name) or more values.
    assert Display(stores, [], ()).name("a") == "Alphacorp"
    assert Display(stores, [], ("ban", "none_found")).name("b") == "Store #8 (Audio)"
    # A store that must be hidden but has no fixed number is a config error.
    with pytest.raises(ValueError, match="public_no"):
        Display([Store("x", "X", "pet", "x.example", terms="ban")], [], ("ban",))


def test_aliases_survive_reordering_and_removal() -> None:
    from pricemon.stores import assign_aliases

    registry = assign_aliases({}, ["a", "b", "c"])
    assert registry == {"a": 1, "b": 2, "c": 3}
    # Reordered, one store gone and one new: existing numbers stay, none is reused.
    again = assign_aliases(registry, ["c", "d", "a"])
    assert again == {"a": 1, "b": 2, "c": 3, "d": 4}
    stores = [
        Store(sid, sid.upper(), "pet", f"{sid}.example", terms="ban", public_no=n)
        for sid, n in again.items()
    ]
    names = {s.id: Display(stores).name(s.id) for s in stores}
    names_reordered = {s.id: Display(list(reversed(stores[1:]))).name(s.id) for s in stores[1:]}
    assert all(names[k] == v for k, v in names_reordered.items())


def test_the_setting_is_one_line_in_public_yml(tmp_path: Path) -> None:
    assert anonymise_setting(ROOT / "config" / "public.yml") == ("ban",)
    path = tmp_path / "public.yml"
    path.write_text("anonymise_terms: []\n")
    assert anonymise_setting(path) == ()


def test_retired_store_leaves_the_snapshot_without_events(published: tuple[Path, Path]) -> None:
    _, data = published
    with (data / "latest" / "snapshot.csv").open() as fh:
        assert {r["store_id"] for r in csv.DictReader(fh)} == {"store-017", "beta"}
    changes = (data / "changes" / "2026" / "2026-11-05.csv").read_text()
    assert "gamma" not in changes
    last = json.loads((data / "runs.jsonl").read_text().splitlines()[-1])
    assert last["retired_rows_closed"] == 3
    assert last["events"]["removed"] == 0
    assert last["stores_added"] == []


def test_every_public_surface_hides_a_banned_store(
    published: tuple[Path, Path], tmp_path: Path
) -> None:
    stores, data = published
    site = build(data, stores, tmp_path / "site", now=NOW).read_text()
    ctx = context(data, stores, ROOT / "config" / "public.yml", now=NOW)
    readme = render(ROOT / "templates" / "README.md.j2", ctx)
    card = render(ROOT / "templates" / "DATASET_CARD.md.j2", ctx)
    feed_path = publish(data, NOW, stores, ROOT / "config" / "public.yml")
    assert feed_path is not None
    feed = feed_path.read_text()
    svgs = " ".join(p.read_text() for p in write_all(data, stores, tmp_path / "assets", NOW))
    texts = {
        "site": site,
        "readme": readme,
        "card": card,
        "feed": feed,
        "visuals": svgs,
        **{str(p): p.read_text() for p in data.rglob("*") if p.is_file()},
    }
    import duckdb

    parquet = tmp_path / "release" / "month.parquet"
    rows = duckdb.connect().execute(
        "SELECT store_id, handle, product_title, variant_title FROM read_parquet(?)",
        [str(parquet)],
    )
    texts["parquet"] = str(rows.fetchall())
    for name, text in texts.items():
        for secret in SECRETS:
            assert secret not in text.lower(), (name, secret)
    assert "store-017" in texts["parquet"]
    assert "Store #17 (Outdoor)" in site
    assert "Store #17 (Outdoor)" in readme
    assert "beta.example" in site  # a store without a ban keeps its name and link
    # The retired store is labelled, never shown as sold out or removed.
    assert "retired on 5 Nov 2026" in site
    assert "Gamma (retired on 5 Nov 2026)" in readme
    monitor = json.loads(feed)["monitor"]
    assert monitor["stores_total"] == 2
    assert monitor["stores_shown_without_name"] == 1
    assert monitor["stores_retired"][0]["label"] == "retired on 5 Nov 2026"


def test_stores_yml_loads_terms_and_retired(published: tuple[Path, Path]) -> None:
    stores, _ = published
    assert [s.terms for s in load_stores(stores)] == ["ban", "no_ban"]
    assert [s.public_no for s in load_stores(stores)] == [17, 2]
    assert [r.id for r in load_retired(stores)] == ["gamma"]


def test_a_store_cannot_be_monitored_and_retired(tmp_path: Path) -> None:
    path = tmp_path / "stores.yml"
    path.write_text(
        "stores:\n  - {id: a, name: A, category: audio, host: a.example}\n"
        "retired:\n  - {id: a, name: A, category: audio, retired_on: 2026-11-27}\n"
    )
    with pytest.raises(ValueError, match="both monitored and retired"):
        load_stores(path)


def test_unknown_terms_value_is_refused(tmp_path: Path) -> None:
    path = tmp_path / "stores.yml"
    path.write_text("stores:\n  - {id: a, name: A, category: audio, host: a.example, terms: x}\n")
    with pytest.raises(ValueError, match="unknown terms"):
        load_stores(path)


def test_committed_config_retires_jlab() -> None:
    retired = load_retired(ROOT / "config" / "retired.yml")
    assert [(r.id, r.retired_on) for r in retired] == [("jlab", date(2026, 11, 27))]
    assert "jlab" not in {s.id for s in load_stores(ROOT / "config" / "stores.yml")}


def test_committed_stores_have_registered_fixed_numbers() -> None:
    from pricemon.stores import load_aliases

    registry = load_aliases(ROOT / "config" / "aliases.yml")
    for s in load_stores(ROOT / "config" / "stores.yml"):
        assert s.public_no is not None
        assert registry[s.id] == s.public_no


def test_a_store_that_leaves_without_being_retired_is_withdrawn_everywhere(
    published: tuple[Path, Path], tmp_path: Path
) -> None:
    """D-036: public data holds only monitored and retired stores. Alphacorp (a ban)
    leaves the list; its rows, run-log entries and history go, and the run totals
    shrink by what it contributed."""
    stores, data = published
    runs_before = [json.loads(x) for x in (data / "runs.jsonl").read_text().splitlines()]
    stores.write_text(
        "stores:\n"
        "  - {id: beta, name: Beta, category: audio, host: beta.example, terms: no_ban, "
        "public_no: 2}\n"
        "retired:\n  - {id: gamma, name: Gamma, category: audio, retired_on: 2026-11-05}\n"
    )
    parquet = tmp_path / "release" / "month.parquet"
    cfg = RunConfig(stores=stores, data=data, history_in=parquet, history_out=parquet)
    day3 = datetime(2026, 11, 6, 6, 17, tzinfo=UTC)
    code, rec = process(cfg, [fetched("beta", catalog(4), day3)], day3, time.monotonic())
    assert code == 0
    assert rec["stores_total"] == 1
    assert rec["events"]["removed"] == 0  # leaving is not a removal
    import duckdb

    ids = {
        r[0]
        for r in duckdb.connect()
        .execute("SELECT DISTINCT store_id FROM read_parquet(?)", [str(parquet)])
        .fetchall()
    }
    assert ids == {"beta", "gamma"}
    for p in data.rglob("*"):
        if p.is_file():
            text = p.read_text().lower()
            for secret in (*SECRETS, "store-017"):
                assert secret not in text, (p, secret)
    runs_after = [json.loads(x) for x in (data / "runs.jsonl").read_text().splitlines()]
    day1_before, day1_after = runs_before[0], runs_after[0]
    assert day1_before["stores_total"] == 3
    assert day1_after["stores_total"] == 2  # beta, and gamma (retired, kept)
    assert day1_after["withdrawn_stores"] == 1
    assert day1_after["rows_observed"] == day1_before["rows_observed"] - 6
    assert day1_after["events"]["new"] == day1_before["events"]["new"] - 6
    # A second run changes nothing more (idempotent).
    from pricemon.display import load_display
    from pricemon.publicdata import rekey_files

    assert rekey_files(data, load_display(stores, ROOT / "config" / "public.yml")) == []


def test_without_a_store_list_nothing_is_withdrawn(tmp_path: Path) -> None:
    from pricemon.publicdata import rekey_files

    data = tmp_path / "data"
    (data / "latest").mkdir(parents=True)
    snap = data / "latest" / "snapshot.csv"
    snap.write_text("store_id,handle,product_title,variant_title\nx,h,T,V\n")
    assert rekey_files(data, Display([], [])) == []
    assert "x,h,T,V" in snap.read_text()


def test_the_registry_holds_listed_stores_and_never_gives_a_number_twice(tmp_path: Path) -> None:
    from pricemon.stores import assign_aliases, dump_aliases, load_alias_next, load_aliases

    path = tmp_path / "aliases.yml"
    # Store c (number 3) left the list: it leaves the file, its number stays used.
    path.write_text(dump_aliases({"a": 1, "b": 2}, next_no=4))
    assert load_aliases(path) == {"a": 1, "b": 2}
    assert load_alias_next(path) == 4
    assert assign_aliases(load_aliases(path), ["a", "d"], load_alias_next(path))["d"] == 4
    committed = ROOT / "config" / "aliases.yml"
    listed = {s.id for s in load_stores(ROOT / "config" / "stores.yml")}
    assert set(load_aliases(committed)) == listed
    assert load_alias_next(committed) > max(load_aliases(committed).values())


def test_the_committed_list_has_no_store_whose_terms_ban_robots() -> None:
    assert {s.terms for s in load_stores(ROOT / "config" / "stores.yml")} <= {
        "no_ban",
        "none_found",
    }
