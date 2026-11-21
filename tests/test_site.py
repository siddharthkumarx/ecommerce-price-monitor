from __future__ import annotations

import re
import time
from datetime import UTC, datetime
from pathlib import Path

from pricemon.run import RunConfig, process
from pricemon.site import build
from tests.test_outputs import DAY1, DAY2, catalog, fetched


def _stores_yml(path: Path) -> Path:
    path.write_text(
        "stores:\n"
        '  - {id: a, name: "Alpha & Co", category: outdoor, host: alpha.example}\n'
        "  - {id: b, name: Beta, category: audio, host: beta.example}\n"
    )
    return path


def test_dashboard_from_real_pipeline_outputs(tmp_path: Path) -> None:
    stores = _stores_yml(tmp_path / "stores.yml")
    cfg = RunConfig(stores=stores, data=tmp_path / "data")
    process(
        cfg,
        [fetched("a", catalog(30), DAY1), fetched("b", catalog(4), DAY1)],
        DAY1,
        time.monotonic(),
    )
    process(
        cfg,
        [fetched("a", catalog(30, "40.00", "50.00"), DAY2), fetched("b", catalog(4), DAY2)],
        DAY2,
        time.monotonic(),
    )
    page = build(cfg.data, stores, tmp_path / "site", now=datetime(2026, 11, 5, 7, 0, tzinfo=UTC))
    text = page.read_text()

    assert "<script" not in text  # no JavaScript at all
    # The SteadyData icon set, served next to the page (no /favicon.ico 404).
    assert '<link rel="icon" href="favicon.ico" sizes="32x32">' in text
    assert '<link rel="manifest" href="site.webmanifest">' in text
    for name in ("favicon.ico", "icon.svg", "apple-touch-icon.png", "site.webmanifest"):
        assert (tmp_path / "site" / name).exists()
    assert 'stop-color="#5FE8D6"' in text  # the SteadyData mark in the top bar
    external = re.findall(r'(?:src|href)="(https?:[^"]+)"', text)
    assert all(not u.endswith((".css", ".js", ".woff2")) for u in external)  # no external assets
    assert "Alpha &amp; Co" in text  # escaped
    assert ">34<" in text  # variants live (30 + 4)
    assert ">88%<" in text  # discounted: 30 of 34
    assert "Latest run 5 Nov 2026, 06:17 UTC: ok" in text
    assert 'Price down</span> · <span class="tag">' in text  # one row per sale
    assert (tmp_path / "site" / "fonts" / "plus-jakarta-sans-latin-400-normal.woff2").exists()
    assert not list((tmp_path / "site" / "fonts").glob("instrument-sans*"))
    # Light theme, the SteadyData link and the author line.
    assert '<meta name="theme-color" content="#FFFFFF">' in text
    assert (
        'Built by SteadyData · <a href="https://steadydata.co/contact/">Get a free sample</a>'
        in text
    )
    assert "Built and maintained by Siddharth Kumar, founder of SteadyData" in text
    # The daily charts: the second run's 30 drops and 30 sale starts, numbers also in a table.
    assert "5 Nov: <b>0 price rises</b>, <b>30 price drops</b>" in text
    assert "<b>30 sales started</b>" in text
    assert text.count("<summary>Numbers by day</summary>") == 3
    assert "on time" in text  # the 5 Nov run started at its 06:17 slot
    # Headline: delivery; the on-time count waits for the on-time trigger (INC-009).
    assert 'Daily runs delivered</span><span class="value">2 of 2</span>' in text
    assert "on time: from next run" in text
    assert "Runs on time" not in text


def test_dashboard_empty_state(tmp_path: Path) -> None:
    page = build(tmp_path / "nodata", tmp_path / "missing.yml", tmp_path / "site")
    text = page.read_text()
    assert "No runs yet" in text
    assert "No changes recorded yet." in text
    assert "Shown from the second run on" in text


def test_pct_never_rounds_a_real_share_to_zero_or_all() -> None:
    from pricemon.site import pct

    assert pct(0, 100) == "0%"
    assert pct(5, 1436) == "<1%"
    assert pct(1435, 1436) == ">99%"
    assert pct(100, 100) == "100%"
    assert pct(1, 0) == "-"


def test_reduced_motion_shows_the_final_state() -> None:
    from pricemon.site import CSS

    assert "@media (prefers-reduced-motion:reduce){*{animation:none!important" in CSS
    # The bars' default style is their final height; the animation only starts from 0.
    assert "@keyframes grow{from{transform:scaleY(0)}}" in CSS
    assert "height:var(--h)" in CSS


def test_text_colours_meet_wcag_aa_on_white_and_alt() -> None:
    def lum(hex_: str) -> float:
        rgb = [int(hex_[i : i + 2], 16) / 255 for i in (1, 3, 5)]
        lin = [c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4 for c in rgb]
        return 0.2126 * lin[0] + 0.7152 * lin[1] + 0.0722 * lin[2]

    def ratio(a: str, b: str) -> float:
        hi, lo = sorted((lum(a), lum(b)), reverse=True)
        return (hi + 0.05) / (lo + 0.05)

    for text in ("#0B1416", "#3D4B49", "#5F716E", "#0B7468", "#095E55"):
        for bg in ("#FFFFFF", "#F3F8F7", "#E3F3F0"):
            assert ratio(text, bg) >= 4.5, (text, bg)
    assert ratio("#FFFFFF", "#0B7468") >= 4.5  # button text
