"""Stores on public surfaces (D-046): every listed store by name, retired stores
labelled, a store that leaves the list only by being retired."""

from __future__ import annotations

import csv
import json
import time
from datetime import UTC, date, datetime
from pathlib import Path

import pytest

from pricemon.display import Display
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
    "  - {id: beta, name: Beta, category: audio, host: beta.example, terms: no_ban}\n"
    "  - {id: gamma, name: Gamma, category: audio, host: gamma.example, terms: none_found}\n"
)
AFTER = (
    "stores:\n"
    "  - {id: beta, name: Beta, category: audio, host: beta.example, terms: no_ban}\n"
    "retired:\n"
    "  - {id: gamma, name: Gamma, category: audio, retired_on: 2026-11-05}\n"
    "  - {id: store-309, name: 'Store #309', category: outdoor, retired_on: 2026-11-05,\n"
    "     reason: Terms of Service ban robots}\n"
)


@pytest.fixture
def published(tmp_path: Path) -> tuple[Path, Path]:
    stores = tmp_path / "stores.yml"
    stores.write_text(BEFORE)
    cfg = RunConfig(stores=stores, data=tmp_path / "data")
    process(
        cfg,
        [fetched("beta", catalog(4), DAY1), fetched("gamma", catalog(3), DAY1)],
        DAY1,
        time.monotonic(),
    )
    stores.write_text(AFTER)
    process(cfg, [fetched("beta", catalog(4), DAY2)], DAY2, time.monotonic())
    return stores, cfg.data


def test_names_hosts_and_links() -> None:
    stores = [
        Store("a", "Alpha", "outdoor", "www.alpha.example", "no_ban"),
        Store("b", "Beta", "audio", "beta.example", "none_found"),
    ]
    retired = [RetiredStore("old", "Oldie", "audio", date(2026, 11, 27))]
    d = Display(stores, retired)
    assert (d.name("a"), d.name("b"), d.name("old"), d.name("?")) == ("Alpha", "Beta", "Oldie", "?")
    assert retired[0].label == "retired on 27 Nov 2026"
    assert d.product_url("b", "x") == "https://beta.example/products/x"
    assert (d.host("old"), d.product_url("old", "x")) == ("", "")  # a retired store has no links
    assert d.public_ids == {"a", "b", "old"}


def test_retired_store_leaves_the_snapshot_without_events(published: tuple[Path, Path]) -> None:
    _, data = published
    with (data / "latest" / "snapshot.csv").open() as fh:
        assert {r["store_id"] for r in csv.DictReader(fh)} == {"beta"}
    assert not (data / "changes" / "2026" / "2026-11-05.csv").exists()  # retiring is no event
    last = json.loads((data / "runs.jsonl").read_text().splitlines()[-1])
    assert last["retired_rows_closed"] == 3
    assert last["events"]["removed"] == 0
    # History stays: day 1 still names gamma, and its run totals are as measured.
    assert "gamma" in (data / "changes" / "2026" / "2026-11-04.csv").read_text()
    first = json.loads((data / "runs.jsonl").read_text().splitlines()[0])
    assert first["stores_total"] == 2


def test_every_public_surface_shows_listed_stores_by_name_and_retired_ones_labelled(
    published: tuple[Path, Path], tmp_path: Path
) -> None:
    stores, data = published
    site = build(data, stores, tmp_path / "site", now=NOW).read_text()
    ctx = context(data, stores, ROOT / "config" / "public.yml", now=NOW)
    readme = render(ROOT / "templates" / "README.md.j2", ctx)
    feed_path = publish(data, NOW, stores, ROOT / "config" / "public.yml")
    assert feed_path is not None
    write_all(data, stores, tmp_path / "assets", NOW)
    assert "beta.example" in site
    assert "retired on 5 Nov 2026" in site
    assert "Gamma (retired on 5 Nov 2026)" in readme
    assert "Store #309 (retired on 5 Nov 2026)" in readme
    assert "shown by number" not in readme + site
    monitor = json.loads(feed_path.read_text())["monitor"]
    assert monitor["stores_total"] == 1
    assert monitor["stores_shown_without_name"] == 0  # kept for feed readers (D-046)
    assert [r["label"] for r in monitor["stores_retired"]] == ["retired on 5 Nov 2026"] * 2


def test_a_store_that_vanishes_from_the_list_stops_the_run(published: tuple[Path, Path]) -> None:
    """D-049: a store leaves the data only by being retired, or by the one-off withdraw
    command; past run totals are never rewritten."""
    stores, data = published
    stores.write_text(
        "stores:\n  - {id: gamma2, name: G, category: audio, host: g.example, terms: no_ban}\n"
    )
    cfg = RunConfig(stores=stores, data=data)
    day3 = datetime(2026, 11, 6, 6, 17, tzinfo=UTC)
    with pytest.raises(ValueError, match=r"neither listed nor retired: \['beta'\]"):
        process(cfg, [fetched("gamma2", catalog(3), day3)], day3, time.monotonic())


def test_stores_yml_loads_terms_and_retired(published: tuple[Path, Path]) -> None:
    stores, _ = published
    assert [s.terms for s in load_stores(stores)] == ["no_ban"]
    assert [(r.id, r.reason) for r in load_retired(stores)] == [
        ("gamma", ""),
        ("store-309", "Terms of Service ban robots"),
    ]


@pytest.mark.parametrize(
    ("entry", "error"),
    [
        ("{id: a, name: A, category: audio, host: a.example, terms: x}", "unknown terms"),
        ("{id: a, name: A, category: audio, host: a.example}", "without a terms value"),
        ("{id: a, name: A, category: audio, host: a.example, terms: ban}", "ban robots"),
    ],
)
def test_the_loader_refuses_unknown_missing_and_ban_terms(
    tmp_path: Path, entry: str, error: str
) -> None:
    path = tmp_path / "stores.yml"
    path.write_text(f"stores:\n  - {entry}\n")
    with pytest.raises(ValueError, match=error):
        load_stores(path)


def test_a_store_cannot_be_monitored_and_retired(tmp_path: Path) -> None:
    path = tmp_path / "stores.yml"
    path.write_text(
        "stores:\n  - {id: a, name: A, category: audio, host: a.example, terms: no_ban}\n"
        "retired:\n  - {id: a, name: A, category: audio, retired_on: 2026-11-27}\n"
    )
    with pytest.raises(ValueError, match="both monitored and retired"):
        load_stores(path)


def test_committed_config_retires_jlab() -> None:
    retired = load_retired(ROOT / "config" / "retired.yml")
    assert (retired[0].id, retired[0].retired_on) == ("jlab", date(2026, 11, 27))
    assert "jlab" not in {s.id for s in load_stores(ROOT / "config" / "stores.yml")}
    # Stores whose Terms turned out to ban robots are retired by number only (D-044).
    hidden = [r for r in retired if r.id.startswith("store-")]
    assert len(hidden) == 15
    assert all(r.name == f"Store #{int(r.id[6:])}" and r.reason for r in hidden)


def test_the_committed_list_has_no_store_whose_terms_ban_robots() -> None:
    assert {s.terms for s in load_stores(ROOT / "config" / "stores.yml")} <= {
        "no_ban",
        "none_found",
    }
