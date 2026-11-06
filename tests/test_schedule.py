"""The slot check shared by the daily gate and the watchdog (INC-007)."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pytest
import yaml

from pricemon.schedule import (
    CRONS,
    WATCHDOG_CRONS,
    active_crons,
    check_slot,
    latest_slot,
    main,
    workflow_flag,
)

ROOT = Path(__file__).resolve().parents[1]
WF = ROOT / ".github" / "workflows"


def at(day: int, hour: int, minute: int = 0, month: int = 11) -> datetime:
    return datetime(2026, month, day, hour, minute, tzinfo=UTC)


def run(started: str, status: str = "ok", run_id: str = "r") -> dict[str, object]:
    return {"run_id": run_id, "started_at": started, "status": status}


def _on(path: Path) -> dict[str, Any]:
    wf: dict[Any, Any] = yaml.safe_load(path.read_text())
    on: dict[str, Any] = wf["on" if "on" in wf else True]  # PyYAML reads the key `on` as True
    return on


def test_watchdog_crons_match_its_workflow_and_are_not_run_slots() -> None:
    assert tuple(s["cron"] for s in _on(WF / "watchdog.yml")["schedule"]) == WATCHDOG_CRONS
    assert not set(WATCHDOG_CRONS) & set(CRONS)


def test_latest_slot() -> None:
    assert latest_slot(at(7, 6, 16), active_crons(2)) == at(6, 6, 17)
    assert latest_slot(at(7, 6, 17), active_crons(2)) == at(7, 6, 17)
    assert latest_slot(at(7, 8, 47), active_crons(2)) == at(7, 6, 17)
    # BFCM at 4 a day: the 16:47 watchdog looks at the 12:17 slot.
    assert latest_slot(at(27, 16, 47), active_crons(4)) == at(27, 12, 17)
    assert latest_slot(at(27, 16, 47), active_crons(2)) == at(27, 6, 17)


def test_a_slot_with_no_run_since_it_is_not_covered() -> None:
    runs = [run("2026-11-06T09:46:16Z")]  # yesterday's manual run
    assert check_slot(runs, at(7, 8, 47), active_crons(2)) == {
        "slot": "2026-11-07T06:17:00Z",
        "covered": "false",
        "run_id": "",
    }


def test_a_manual_run_covers_the_slot_so_a_late_scheduled_run_skips() -> None:
    # 4 Nov: GitHub started the 06:17 slot at 14:35. With a run at 09:46 it skips.
    runs = [run("2026-11-07T09:46:16Z", run_id="20261107T094616Z")]
    got = check_slot(runs, at(7, 14, 35), active_crons(2))
    assert got["covered"] == "true"
    assert got["run_id"] == "20261107T094616Z"


@pytest.mark.parametrize(
    ("status", "covered"), [("partial", "true"), ("held", "true"), ("crashed", "false")]
)
def test_statuses_that_cover_a_slot(status: str, covered: str) -> None:
    runs = [run("2026-11-07T06:20:00Z", status)]
    assert check_slot(runs, at(7, 8, 47), active_crons(2))["covered"] == covered


def test_flag_is_read_from_the_daily_workflow() -> None:
    text = (WF / "daily.yml").read_text()
    assert workflow_flag(text) == int(yaml.safe_load(text)["env"]["BFCM_RUNS_PER_DAY"])
    with pytest.raises(ValueError, match="BFCM_RUNS_PER_DAY"):
        workflow_flag("env: {}\n")


def test_cli_prints_github_output_lines(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    runs = tmp_path / "runs.jsonl"
    runs.write_text(json.dumps(run("2026-11-07T06:25:00Z", run_id="a")) + "\n")
    assert (
        main(
            [
                "check",
                "--runs",
                str(runs),
                "--now",
                "2026-11-07T08:47:00Z",
                "--workflow",
                str(WF / "daily.yml"),
            ]
        )
        == 0
    )
    assert capsys.readouterr().out.splitlines() == [
        "slot=2026-11-07T06:17:00Z",
        "covered=true",
        "run_id=a",
    ]
    assert (
        main(["check", "--runs", str(tmp_path / "missing.jsonl"), "--now", "2026-11-07T08:47:00Z"])
        == 0
    )
    assert "covered=false" in capsys.readouterr().out


def test_daily_gate_decides_every_trigger_and_watchdog_is_least_privilege() -> None:
    daily = yaml.safe_load((WF / "daily.yml").read_text())
    assert "if" not in daily["jobs"]["slot"]  # the gate sees every trigger
    assert daily["jobs"]["run"]["needs"] == "slot"
    assert "needs.slot.outputs.run == 'true'" in daily["jobs"]["run"]["if"]
    watchdog = yaml.safe_load((WF / "watchdog.yml").read_text())
    assert watchdog["permissions"] == {"contents": "read", "actions": "write", "issues": "write"}
    steps = watchdog["jobs"]["check"]["steps"]
    rescue = next(s for s in steps if s.get("id") == "rescue")
    assert "gh workflow run daily.yml" in rescue["run"]
    assert "steps.busy.outputs.busy == 'false'" in rescue["if"]
