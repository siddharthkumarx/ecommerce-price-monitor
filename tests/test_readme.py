"""README and dataset card rendering, internal links, and the generated visuals."""

from __future__ import annotations

import re
import time
from pathlib import Path

import pytest

from pricemon.readme import ROOT, context, render
from pricemon.report import collect
from pricemon.run import RunConfig, process
from pricemon.visuals import hero, hero_square, maintenance, pipeline
from tests.test_outputs import DAY1, DAY2, catalog, fetched

SECTIONS = [
    "# Shopify price monitor",
    "## What you get",
    "### What changed today",
    "## Why you can trust this data",
    "## How it works",
    "## What broke and how I fixed it",
    "## Who uses data like this",
    "## Want this for your own sites?",
    "## FAQ",
    "## Data dictionary",
    "<summary><strong>For engineers</strong></summary>",
    "## Data use and compliance",
    "## License",
]


def _stores(path: Path) -> Path:
    path.write_text(
        "stores:\n"
        '  - {id: a, name: "Alpha | Co", category: outdoor, host: alpha.example}\n'
        "  - {id: b, name: Beta, category: audio, host: beta.example}\n"
    )
    return path


@pytest.fixture
def two_runs(tmp_path: Path) -> tuple[Path, Path]:
    stores = _stores(tmp_path / "stores.yml")
    cfg = RunConfig(stores=stores, data=tmp_path / "data")
    process(
        cfg,
        [fetched("a", catalog(30), DAY1), fetched("b", catalog(4), DAY1)],
        DAY1,
        time.monotonic(),
    )
    sale = catalog(30, "40.00", "50.00")
    process(cfg, [fetched("a", sale, DAY2), fetched("b", catalog(4), DAY2)], DAY2, time.monotonic())
    return cfg.data, stores


def test_readme_renders_clean_and_in_order(two_runs: tuple[Path, Path]) -> None:
    data, stores = two_runs
    ctx = context(data, stores, ROOT / "config" / "public.yml")
    text = render(ROOT / "templates" / "README.md.j2", ctx)
    for bad in ("{{", "{%", "{#", "<!--", "TODO", "TBD", "placeholder", "lorem"):
        assert bad not in text, bad
    positions = [text.index(s) for s in SECTIONS]
    assert positions == sorted(positions)
    assert "Alpha \\| Co" in text  # table cells escaped
    assert "30 price drops, 30 sales started" in text  # What changed today, from the run
    assert all(alt.strip() for alt in re.findall(r'alt="([^"]*)"', text))
    assert "hello@siddharthkumar.com" in text


def test_dataset_card_renders(two_runs: tuple[Path, Path]) -> None:
    data, stores = two_runs
    ctx = context(data, stores, ROOT / "config" / "public.yml")
    text = render(ROOT / "templates" / "DATASET_CARD.md.j2", ctx)
    assert text.startswith("---\npretty_name:")
    assert "license: cc-by-4.0" in text
    assert "{{" not in text


def test_first_run_says_so(tmp_path: Path) -> None:
    stores = _stores(tmp_path / "stores.yml")
    cfg = RunConfig(stores=stores, data=tmp_path / "data")
    process(cfg, [fetched("a", catalog(3), DAY1)], DAY1, time.monotonic())
    text = render(
        ROOT / "templates" / "README.md.j2",
        context(cfg.data, stores, ROOT / "config" / "public.yml"),
    )
    assert "was the first one: it recorded 3 prices" in text


# -- visuals --------------------------------------------------------------------------
def _font_sizes(svg: str) -> list[float]:
    return [float(x) for x in re.findall(r'font-size="([\d.]+)"', svg)]


def test_visuals_follow_the_rules(two_runs: tuple[Path, Path]) -> None:
    data, stores = two_runs
    f = collect(data, stores)
    for svg in (hero(f), pipeline(), maintenance(f), hero_square(f)):
        assert len(svg.encode()) < 1_000_000
        assert "<script" not in svg
        assert not re.search(r'(?:href|src|url\()\s*=?\s*"?https?:', svg)  # no external loads
        assert "prefers-reduced-motion" in svg
        assert " 9s infinite" in svg
        assert "<title" in svg
        assert "<desc" in svg
    for svg in (hero(f), pipeline(), maintenance(f)):
        assert min(_font_sizes(svg)) >= 22
    assert min(_font_sizes(hero_square(f))) >= 40
    assert "EXAMPLE" in maintenance(f)  # drawn timeline is labelled


# -- internal links -------------------------------------------------------------------
def _slug(heading: str) -> str:
    s = heading.strip().lower()
    s = re.sub(r"[^\w\- ]", "", s)
    return s.replace(" ", "-")


def _anchors(path: Path) -> set[str]:
    heads = re.findall(r"^#{1,6} (.+)$", path.read_text(encoding="utf-8"), flags=re.M)
    return {_slug(h) for h in heads}


MARKDOWN = [
    p
    for p in ROOT.rglob("*.md")
    if not any(part in {".venv", "node_modules", ".git", "results"} for part in p.parts)
]


@pytest.mark.parametrize("path", MARKDOWN, ids=lambda p: str(p.relative_to(ROOT)))
def test_internal_links_resolve(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    links = re.findall(r"\]\(([^)\s]+)\)", text) + re.findall(r'src="([^"]+)"', text)
    for link in links:
        if re.match(r"^(https?:|mailto:)", link):
            continue
        target, _, anchor = link.partition("#")
        dest = (path.parent / target).resolve() if target else path
        assert dest.exists(), f"{path.name}: broken link {link}"
        if anchor and dest.suffix == ".md":
            assert anchor in _anchors(dest), f"{path.name}: missing anchor {link}"
