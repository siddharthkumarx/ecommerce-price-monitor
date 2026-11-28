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
    jobs = _load(path)["jobs"]
    ids = {s["id"] for job in jobs.values() for s in job["steps"] if "id" in s}
    for name, job in jobs.items():
        assert "timeout-minutes" in job, f"{path.name}:{name} has no timeout"
    for ref in re.findall(r"steps\.([\w-]+)\.", text):
        assert ref in ids, f"{path.name}: steps.{ref} is not a step id"


def test_daily_mirrors_history_to_releases_from_main_only_after_the_commit() -> None:
    daily = _load(WORKFLOWS[[p.name for p in WORKFLOWS].index("daily.yml")])
    steps = daily["jobs"]["run"]["steps"]
    names = [s.get("name") for s in steps]
    mirror = steps[names.index("Mirror the history to Releases")]
    assert names.index("Commit data") < names.index("Mirror the history to Releases")
    # From main only (a branch run uploads nothing) and only after the data commit.
    assert "github.ref == 'refs/heads/main'" in mirror["if"]
    assert "steps.commit.outcome == 'success'" in mirror["if"]
    # Immutable files: an asset is uploaded once, never replaced or deleted (D-047).
    text = (Path(__file__).resolve().parents[1] / ".github" / "workflows" / "daily.yml").read_text()
    assert "--clobber" not in text
    assert "gh release delete" not in text
    assert "price_history_" not in text  # the monthly Parquet is gone
    checkout = next(s for s in steps if "actions/checkout" in s.get("uses", ""))
    assert checkout["with"]["fetch-depth"] == 0  # the month-end snapshot comes from git
    assert daily["concurrency"] == {"group": "daily", "cancel-in-progress": False}
    assert daily["jobs"]["run"]["timeout-minutes"] <= 45  # owner limit (D-020)


def test_pages_deploy_is_gated_and_least_privilege() -> None:
    daily = _load(WORKFLOWS[[p.name for p in WORKFLOWS].index("daily.yml")])
    pages = daily["jobs"]["pages"]
    assert "vars.PAGES_ENABLED == 'true'" in pages["if"]
    assert pages["permissions"] == {"pages": "write", "id-token": "write"}
    assert pages["environment"]["name"] == "github-pages"
    upload = next(s for s in daily["jobs"]["run"]["steps"] if s.get("id") == "pages_artifact")
    assert "vars.PAGES_ENABLED == 'true'" in upload["if"]


def test_live_checks_start_by_hand_only() -> None:
    checks = _load(WORKFLOWS[[p.name for p in WORKFLOWS].index("checks.yml")])
    triggers: dict[Any, Any] = checks
    on = triggers["on" if "on" in triggers else True]  # PyYAML reads `on` as True
    # Pushing checks/request.yml (or a tag, INC-008) starts nothing (D-051).
    assert set(on) == {"workflow_dispatch"}


def test_a_live_check_runs_once_even_when_main_is_fast_forwarded() -> None:
    checks = _load(WORKFLOWS[[p.name for p in WORKFLOWS].index("checks.yml")])
    assert checks["permissions"]["actions"] == "read"
    steps = checks["jobs"]["run"]["steps"]
    names = [s.get("id") or s.get("name") or s.get("uses") for s in steps]
    dup = steps[names.index("dup")]
    assert names.index("dup") == 1  # right after checkout, before anything that reads a store
    assert "checks/results/$id" in dup["run"]  # results already committed (INC-010)
    assert "status=$status" in dup["run"]
    # A run held by its branch's concurrency group is "pending", not "queued".
    assert "requested queued pending waiting in_progress" in dup["run"]
    assert "select(.id < $RUN_ID)" in dup["run"]
    for step in steps[2:]:
        # Fail closed: an error in the guard leaves `skip` empty and nothing runs.
        assert "steps.dup.outputs.skip == 'false'" in step["if"]


def test_pages_deploy_runs_on_main_only() -> None:
    daily = _load(WORKFLOWS[[p.name for p in WORKFLOWS].index("daily.yml")])
    cond = daily["jobs"]["pages"]["if"]
    # A branch run skips Pages instead of failing on the environment rule (INC-011).
    assert "github.ref == 'refs/heads/main'" in cond
    assert "!cancelled()" in cond
    assert "needs.run.outputs.pages == 'success'" in cond
