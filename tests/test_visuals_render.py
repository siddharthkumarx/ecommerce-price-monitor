"""Render the visuals in Chromium (Playwright for Node) and check the reduced-motion
final frame. Skipped where Node or Playwright is not installed; the `visuals` CI
workflow installs both and runs it."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import time
from pathlib import Path

import pytest

from pricemon.run import RunConfig, process
from pricemon.visuals import write_all
from tests.test_outputs import DAY1, DAY2, catalog, fetched

ROOT = Path(__file__).resolve().parents[1]


def _playwright_available() -> bool:
    if not shutil.which("node"):
        return False
    probe = subprocess.run(
        ["node", "-e", "require('playwright')"], cwd=ROOT, capture_output=True, check=False
    )
    return probe.returncode == 0


def test_reduced_motion_and_still_show_the_final_frame(tmp_path: Path) -> None:
    if not _playwright_available():
        if os.environ.get("REQUIRE_PLAYWRIGHT"):
            pytest.fail("Node Playwright is required here but not installed")
        pytest.skip("Node Playwright not installed")
    stores = tmp_path / "stores.yml"
    stores.write_text(
        "stores:\n"
        "  - {id: a, name: Alpha Outdoor, category: outdoor, host: alpha.example}\n"
        "  - {id: b, name: Beta Audio, category: audio, host: beta.example}\n"
    )
    cfg = RunConfig(stores=stores, data=tmp_path / "data")
    process(
        cfg,
        [fetched("a", catalog(30), DAY1), fetched("b", catalog(4), DAY1)],
        DAY1,
        time.monotonic(),
    )
    sale = catalog(30, "40.00", "50.00")
    process(cfg, [fetched("a", sale, DAY2), fetched("b", catalog(4), DAY2)], DAY2, time.monotonic())
    out = tmp_path / "assets"
    write_all(cfg.data, stores, out)
    result = subprocess.run(
        ["node", str(ROOT / "scripts" / "check_visuals.cjs"), str(out)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
        timeout=180,
    )
    report = json.loads(result.stdout)
    assert result.returncode == 0, json.dumps(report, indent=2)
    assert {r["name"] for r in report} == {"hero", "pipeline", "maintenance-loop"}
