"""Repository rules that CI enforces through pytest."""

from __future__ import annotations

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAX_BYTES = 50 * 1024 * 1024


def _tracked() -> list[Path]:
    out = subprocess.run(
        ["git", "ls-files", "-z"], cwd=ROOT, check=True, capture_output=True
    ).stdout.decode()
    return [ROOT / p for p in out.split("\0") if p]


def test_every_tracked_file_is_under_50_mb() -> None:
    big = [p for p in _tracked() if p.exists() and p.stat().st_size >= MAX_BYTES]
    assert big == [], f"files at or over 50 MB: {big}"


def test_committed_data_holds_no_descriptions_or_images() -> None:
    data = ROOT / "data"
    if not data.exists():
        return
    for path in data.rglob("*"):
        if path.is_file() and path.suffix in (".csv", ".json", ".jsonl"):
            text = path.read_text(encoding="utf-8", errors="replace")
            assert "body_html" not in text, path
            assert "cdn.shopify.com" not in text, path


def test_hook_path_is_configured() -> None:
    hook = ROOT / ".githooks" / "commit-msg"
    assert hook.exists()
    assert hook.stat().st_mode & 0o111, "commit-msg hook must be executable"
