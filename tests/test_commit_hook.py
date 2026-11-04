"""Commit-message policy: no trailers except Signed-off-by, no "Generated with" footer."""

from __future__ import annotations

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HOOK = ROOT / ".githooks" / "commit-msg"
CHECK = ROOT / "scripts" / "check-commit-messages.sh"


def _hook(tmp_path: Path, text: str) -> str:
    msg = tmp_path / "MSG"
    msg.write_text(text)
    subprocess.run([str(HOOK), str(msg)], check=True, cwd=ROOT)
    return msg.read_text()


def test_hook_removes_trailers_and_footer_but_keeps_signed_off_by(tmp_path: Path) -> None:
    out = _hook(
        tmp_path,
        "fetch: add products.json witness\n\nKeeps prices in cents.\n\n---\n"
        "Generated with Some Tool (https://example.com)\n\n"
        "Reviewed-by: A <a@example.com>\n"
        "Helped-by: B <b@example.com>\n"
        "Signed-off-by: C <c@example.com>\n",
    )
    assert out == (
        "fetch: add products.json witness\n\nKeeps prices in cents.\n\n"
        "Signed-off-by: C <c@example.com>\n"
    )


def test_hook_removes_a_trailer_only_block(tmp_path: Path) -> None:
    out = _hook(tmp_path, "docs: fix typo\n\nReviewed-by: A <a@example.com>\n")
    assert out == "docs: fix typo\n"


def test_hook_keeps_clean_message_and_body_colons(tmp_path: Path) -> None:
    body = "docs: add sources register\n\nRanking inside a category: US shops first.\n"
    assert _hook(tmp_path, body) == body


def _repo(tmp_path: Path, *messages: str) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir(parents=True)
    env_cmd = ["git", "-c", "user.name=T", "-c", "user.email=t@example.com"]
    subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
    (repo / ".githooks").mkdir()
    (repo / ".githooks" / "forbidden-footer").write_text("generated with\n")
    for i, message in enumerate(messages):
        (repo / f"f{i}").write_text(str(i))
        subprocess.run(["git", "add", "."], cwd=repo, check=True)
        subprocess.run(
            [*env_cmd, "commit", "-q", "--no-verify", "-m", message], cwd=repo, check=True
        )
    return repo


def test_check_passes_signed_off_by_and_fails_other_trailers(tmp_path: Path) -> None:
    ok = _repo(tmp_path, "a: one\n\nSigned-off-by: C <c@example.com>")
    assert subprocess.run([str(CHECK)], cwd=ok, capture_output=True, check=False).returncode == 0
    bad = _repo(tmp_path / "x", "a: one", "b: two\n\nReviewed-by: A <a@example.com>")
    result = subprocess.run([str(CHECK)], cwd=bad, capture_output=True, text=True, check=False)
    assert result.returncode == 1
    assert "Reviewed-by" in result.stdout


def test_check_fails_generated_with_footer(tmp_path: Path) -> None:
    bad = _repo(tmp_path, "a: one\n\nGenerated with Some Tool")
    assert subprocess.run([str(CHECK)], cwd=bad, capture_output=True, check=False).returncode == 1


def test_check_sees_trailers_after_a_separator(tmp_path: Path) -> None:
    bad = _repo(tmp_path, "a: one\n\n---\n\nReviewed-by: A <a@example.com>")
    assert subprocess.run([str(CHECK)], cwd=bad, capture_output=True, check=False).returncode == 1
