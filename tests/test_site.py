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
    external = re.findall(r'(?:src|href)="(https?:[^"]+)"', text)
    assert all(not u.endswith((".css", ".js", ".woff2")) for u in external)  # no external assets
    assert "Alpha &amp; Co" in text  # escaped
    assert ">34<" in text  # variants live (30 + 4)
    assert ">88%<" in text  # discounted: 30 of 34
    assert "Last run 2026-11-05 06:17 UTC: ok" in text
    assert 'Price down</span> · <span class="amber">Discount start' in text  # one row per sale
    assert (tmp_path / "site" / "fonts" / "instrument-sans-latin-400-normal.woff2").exists()


def test_dashboard_empty_state(tmp_path: Path) -> None:
    page = build(tmp_path / "nodata", tmp_path / "missing.yml", tmp_path / "site")
    text = page.read_text()
    assert "No runs yet" in text
    assert "No changes recorded yet." in text


def test_pct_never_rounds_a_real_share_to_zero_or_all() -> None:
    from pricemon.site import pct

    assert pct(0, 100) == "0%"
    assert pct(5, 1436) == "<1%"
    assert pct(1435, 1436) == ">99%"
    assert pct(100, 100) == "100%"
    assert pct(1, 0) == "-"
