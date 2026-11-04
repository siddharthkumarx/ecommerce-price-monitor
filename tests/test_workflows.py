"""Structural checks on the GitHub Actions workflows (run in CI with pytest)."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import pytest
import yaml

WORKFLOWS = sorted((Path(__file__).resolve().parents[1] / ".github" / "workflows").glob("*.yml"))


def _load(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text())
    assert isinstance(data, dict)
    return data


@pytest.mark.parametrize("path", WORKFLOWS, ids=lambda p: p.name)
def test_actions_are_pinned_to_commit_shas(path: Path) -> None:
    for job in _load(path)["jobs"].values():
        for step in job["steps"]:
            if "uses" in step:
                assert re.fullmatch(r"[\w.-]+/[\w.-]+@[0-9a-f]{40}", step["uses"]), step["uses"]


@pytest.mark.parametrize("path", WORKFLOWS, ids=lambda p: p.name)
def test_jobs_have_timeouts_and_step_refs_exist(path: Path) -> None:
    text = path.read_text()
    for name, job in _load(path)["jobs"].items():
        assert "timeout-minutes" in job, f"{path.name}:{name} has no timeout"
        ids = {s["id"] for s in job["steps"] if "id" in s}
        for ref in re.findall(r"steps\.([\w-]+)\.", text):
            assert ref in ids, f"{path.name}: steps.{ref} is not a step id"


def test_daily_commits_data_only_after_the_history_upload() -> None:
    daily = _load(WORKFLOWS[[p.name for p in WORKFLOWS].index("daily.yml")])
    steps = {s.get("id"): s for s in daily["jobs"]["run"]["steps"] if s.get("id")}
    assert "steps.upload.outcome" in steps["commit"]["if"]
    names = [s.get("name") for s in daily["jobs"]["run"]["steps"]]
    assert names.index("Upload history to release") < names.index("Commit data")
    assert daily["concurrency"] == {"group": "daily", "cancel-in-progress": False}
