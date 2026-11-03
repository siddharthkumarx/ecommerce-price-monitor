from __future__ import annotations

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HOOK = ROOT / ".githooks" / "commit-msg"


def test_hook_strips_attribution_lines(tmp_path: Path) -> None:
    msg = tmp_path / "MSG"
    msg.write_text(
        "fetch: add products.json witness\n\nKeeps prices in cents.\n\n---\n"
        "\N{ROBOT FACE} Generated with [Tool](https://example.com)\n\n"
        "Co-Authored-By: Someone <x@example.com>\n"
        "Claude-Session: https://example.com/s/1\n"
    )
    subprocess.run([str(HOOK), str(msg)], check=True, cwd=ROOT)
    assert msg.read_text() == "fetch: add products.json witness\n\nKeeps prices in cents.\n"


def test_hook_keeps_clean_message(tmp_path: Path) -> None:
    msg = tmp_path / "MSG"
    body = "docs: add sources register\n\nForty stores across five categories.\n"
    msg.write_text(body)
    subprocess.run([str(HOOK), str(msg)], check=True, cwd=ROOT)
    assert msg.read_text() == body
