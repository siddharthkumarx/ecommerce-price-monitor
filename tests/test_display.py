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

BEFORE = (
    "stores:\n"
    '  - {id: alpha, name: "Alphacorp", category: outdoor, host: www.alphacorp.example, '
    "terms: ban}\n"
    "  - {id: beta, name: Beta, category: audio, host: beta.example, terms: no_ban}\n"
    "  - {id: gamma, name: Gamma, category: audio, host: gamma.example, terms: none_found}\n"
)
AFTER = (
    "stores:\n"
    '  - {id: alpha, name: "Alphacorp", category: outdoor, host: www.alphacorp.example, '
    "terms: ban}\n"
    "  - {id: beta, name: Beta, category: audio, host: beta.example, terms: no_ban}\n"
    "retired:\n"
    "  - {id: gamma, name: Gamma, category: audio, retired_on: 2026-11-05}\n"
)


def _alpha_catalog(price: str) -> list[dict[str, object]]:
    items = catalog(6, price)
    for p in items:
        p["title"] = f"Alphacorp {p['title']}"
    return items


@pytest.fixture
def published(tmp_path: Path) -> tuple[Path, Path]:
    stores = tmp_path / "stores.yml"
    stores.write_text(BEFORE)
    cfg = RunConfig(stores=stores, data=tmp_path / "data")
    process(
        cfg,
        [
            fetched("alpha", _alpha_catalog("50.00"), DAY1),
            fetched("beta", catalog(4), DAY1),
            fetched("gamma", catalog(3), DAY1),
        ],
        DAY1,
        time.monotonic(),
    )
    stores.write_text(AFTER)
    process(
        cfg,
        [fetched("alpha", _alpha_catalog("40.00"), DAY2), fetched("beta", catalog(4), DAY2)],
        DAY2,
        time.monotonic(),
    )
    return stores, cfg.data


def test_names_hosts_and_titles(tmp_path: Path) -> None:
    stores = [
        Store("a", "Alphacorp", "outdoor", "www.alphacorp.example", terms="ban"),
        Store("b", "Beta", "audio", "beta.example", terms="none_found"),
        Store("c", "Gear Co", "pet", "gear.example", terms="ban"),
    ]
    retired = [RetiredStore("old", "Oldie", "audio", date(2026, 11, 27))]
    d = Display(stores, retired, ("ban",))
    assert d.name("a") == "Store #1 (Outdoor)"
    assert d.name("c") == "Store #2 (Pet)"
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
    assert Display(stores, [], ("ban", "none_found")).name("b") == "Store #2 (Audio)"


def test_the_setting_is_one_line_in_public_yml(tmp_path: Path) -> None:
    assert anonymise_setting(ROOT / "config" / "public.yml") == ("ban",)
    path = tmp_path / "public.yml"
    path.write_text("anonymise_terms: []\n")
    assert anonymise_setting(path) == ()


def test_retired_store_leaves_the_snapshot_without_events(published: tuple[Path, Path]) -> None:
    _, data = published
    with (data / "latest" / "snapshot.csv").open() as fh:
        assert {r["store_id"] for r in csv.DictReader(fh)} == {"alpha", "beta"}
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
    for name, text in {
        "site": site,
        "readme": readme,
        "card": card,
        "feed": feed,
        "visuals": svgs,
    }.items():
        assert "alphacorp" not in text.lower(), name
    assert "Store #1 (Outdoor)" in site
    assert "Store #1 (Outdoor)" in readme
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
