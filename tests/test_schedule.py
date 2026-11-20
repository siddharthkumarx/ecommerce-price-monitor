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
    accounting,
    active_crons,
    check_slot,
    gate,
    latest_slot,
    main,
    slot_states,
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


# -- the daily gate (INC-009) -------------------------------------------------------
def test_on_time_dispatch_runs_and_the_late_schedule_event_then_skips() -> None:
    crons = active_crons(2)
    first = gate("workflow_dispatch", [], at(22, 6, 17), slot="2026-11-22T06:17Z", crons=crons)
    assert first["run"] == "true"
    assert first["slot"] == "2026-11-22T06:17:00Z"
    runs = [run("2026-11-22T06:18:30Z", run_id="20261122T061830Z")]
    # GitHub's own schedule event for the same slot arrives 8 hours late.
    late = gate("schedule", runs, at(22, 14, 21), cron="17 6 * * *", crons=crons)
    assert late["run"] == "false"
    assert "20261122T061830Z" in late["reason"]
    # A second dispatch for the same slot (a retry) does not load the stores again.
    again = gate("workflow_dispatch", runs, at(22, 6, 50), slot="2026-11-22T06:17Z", crons=crons)
    assert again["run"] == "false"


def test_late_schedule_event_still_runs_when_nothing_filled_the_slot() -> None:
    got = gate("schedule", [], at(22, 14, 21), cron="17 6 * * *", crons=active_crons(2))
    assert got["run"] == "true"


def test_bfcm_slots_are_filled_by_dispatch_and_late_events_skip() -> None:
    crons = active_crons(4)
    runs: list[dict[str, object]] = []
    for hour in (0, 6, 12, 18):
        slot = f"2026-11-27T{hour:02d}:17Z"
        assert (
            gate("workflow_dispatch", runs, at(27, hour, 17), slot=slot, crons=crons)["run"]
            == "true"
        )
        runs.append(run(f"2026-11-27T{hour:02d}:18:00Z", run_id=f"r{hour}"))
    # Each scheduled event arrives about 8 hours late and finds the newest slot filled.
    for hour, cron in ((8, "17 0,12 26-30 11 *"), (14, "17 6 * * *"), (20, "17 0,12 26-30 11 *")):
        assert gate("schedule", runs, at(27, hour, 30), cron=cron, crons=crons)["run"] == "false"


def test_dispatch_slot_rules() -> None:
    crons = active_crons(2)
    # A slot that is not in the schedule, a stale slot and a malformed value never run.
    assert (
        gate("workflow_dispatch", [], at(22, 7), slot="2026-11-22T07:17Z", crons=crons)["run"]
        == "false"
    )
    stale = gate("workflow_dispatch", [], at(23, 6, 20), slot="2026-11-22T06:17Z", crons=crons)
    assert stale["run"] == "false"
    assert "no longer the current slot" in stale["reason"]
    assert gate("workflow_dispatch", [], at(22, 6), slot="tomorrow", crons=crons)["run"] == "false"
    # The extra BFCM slots only with BFCM_RUNS_PER_DAY "4".
    assert (
        gate("workflow_dispatch", [], at(27, 12, 17), slot="2026-11-27T12:17Z", crons=crons)["run"]
        == "false"
    )
    # A caller clock a little fast: the gate waits for the slot.
    early = gate("workflow_dispatch", [], at(22, 6, 15), slot="2026-11-22T06:17Z", crons=crons)
    assert (early["run"], early["wait_s"]) == ("true", "120")
    assert (
        gate("workflow_dispatch", [], at(22, 6, 0), slot="2026-11-22T06:17Z", crons=crons)["run"]
        == "false"
    )
    # A trigger check never runs; a manual run without a slot always does.
    assert gate("workflow_dispatch", [], at(22, 6, 17), slot="check", crons=crons)["run"] == "false"
    manual = gate("workflow_dispatch", [run("2026-11-22T06:18:00Z")], at(22, 9), crons=crons)
    assert manual["run"] == "true"


def test_gate_cli(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    runs = tmp_path / "runs.jsonl"
    runs.write_text(json.dumps(run("2026-11-22T06:18:00Z", run_id="a")) + "\n")
    args = ["gate", "--runs", str(runs), "--now", "2026-11-22T14:00:00Z"]
    assert main([*args, "--event", "schedule", "--cron", "17 6 * * *"]) == 0
    out = capsys.readouterr().out.splitlines()
    assert out[0] == "run=false"
    assert out[1] == "slot=2026-11-22T06:17:00Z"


def test_daily_workflow_takes_a_slot_input_and_watchdog_passes_it() -> None:
    daily = yaml.safe_load((WF / "daily.yml").read_text())
    on = _on(WF / "daily.yml")
    assert on["workflow_dispatch"]["inputs"]["slot"]["required"] is False
    decide = next(s for s in daily["jobs"]["slot"]["steps"] if s.get("id") == "decide")
    assert decide["env"]["SLOT"] == "${{ inputs.slot }}"
    assert "$SLOT" in decide["run"]
    assert "${{" not in decide["run"]  # no expression injection
    watchdog = yaml.safe_load((WF / "watchdog.yml").read_text())
    rescue = next(s for s in watchdog["jobs"]["check"]["steps"] if s.get("id") == "rescue")
    assert '-f slot="$SLOT"' in rescue["run"]


# -- honest accounting (INC-009) -----------------------------------------------------
def test_slot_states_on_time_late_held_missed_pending() -> None:
    runs = [
        run("2026-11-04T08:46:55Z", run_id="first"),  # 2 h 30 after the slot: late
        run("2026-11-05T08:17:00Z", run_id="edge"),  # exactly 2 h: on time
        run("2026-11-06T23:59:00Z", run_id="late"),  # same day: late
        run("2026-11-08T07:00:00Z", status="held", run_id="h"),
        run("2026-11-09T07:00:00Z", status="crashed", run_id="c"),  # a crash fills nothing
        run("2026-11-10T03:00:00Z", run_id="early"),  # before the day's slot: fills nothing
    ]
    states = slot_states(runs, at(10, 7), active_crons(2))
    assert [(s.slot.day, s.state) for s in states] == [
        (4, "late"),
        (5, "on_time"),
        (6, "late"),
        (7, "missed"),
        (8, "held"),
        (9, "missed"),
        (10, "pending"),
    ]
    acc = accounting(runs, at(10, 7), active_crons(2))
    assert (acc["slots"], acc["on_time"], acc["late"], acc["held"], acc["missed"]) == (
        6,
        1,
        2,
        1,
        2,
    )
    assert acc["pending"] == 1


def test_a_late_run_fills_only_the_latest_slot_in_bfcm() -> None:
    # 27 Nov at 4 a day: a run at 08:00 is on time for 06:17, the 00:17 slot is missed.
    runs = [run("2026-11-26T23:00:00Z"), run("2026-11-27T08:00:00Z")]
    states = {
        s.slot.hour: s.state
        for s in slot_states(runs, at(28, 0, 30), active_crons(4))
        if s.slot.day == 27
    }
    assert states == {0: "missed", 6: "on_time", 12: "missed", 18: "missed"}


def test_accounting_of_the_real_history_counts_late_runs_not_missed_runs() -> None:
    # The committed run log (4-20 Nov): every slot got a good run, none within 2 h.
    lines = (ROOT / "data" / "runs.jsonl").read_text().splitlines()
    runs = [json.loads(line) for line in lines if line.strip()]
    cutoff = [r for r in runs if r["started_at"] < "2026-11-21"]
    acc = accounting(cutoff, at(21, 0, 0), active_crons(2))
    assert (acc["slots"], acc["on_time"], acc["late"], acc["missed"]) == (17, 0, 17, 0)
