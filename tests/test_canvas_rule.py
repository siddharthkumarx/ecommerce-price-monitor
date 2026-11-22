"""Canvas rule (owner decision, 22 Nov 2026): every image's outermost background is
#F3F8F7. scripts/check_canvas.cjs checks the edge pixels of every tracked PNG and the
first <rect> fill of every SVG (exceptions listed there). Needs Node (no packages)."""

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def test_every_image_sits_on_the_canvas() -> None:
    if not shutil.which("node"):
        if os.environ.get("REQUIRE_PLAYWRIGHT"):
            pytest.fail("Node is required here but not installed")
        pytest.skip("Node not installed")
    result = subprocess.run(
        ["node", "scripts/check_canvas.cjs"], cwd=ROOT, capture_output=True, text=True, check=False
    )
    assert result.returncode == 0, result.stdout + result.stderr
