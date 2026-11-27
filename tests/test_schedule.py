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
    dispatch_slot,
    gate,
    latest_slot,
    main,
    past_extra_slots,
    slot_states,
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
    assert latest_slot(at(7, 6, 16), active_crons()) == at(6, 6, 17)
    assert latest_slot(at(7, 6, 17), active_crons()) == at(7, 6, 17)
    assert latest_slot(at(7, 8, 47), active_crons()) == at(7, 6, 17)
    # One slot a day after the Black Friday runs: the 16:47 watchdog looks at 06:17.
    assert latest_slot(at(27, 16, 47), active_crons()) == at(27, 6, 17)


def test_a_slot_with_no_run_since_it_is_not_covered() -> None:
    runs = [run("2026-11-06T09:46:16Z")]  # yesterday's manual run
    assert check_slot(runs, at(7, 8, 47), active_crons()) == {
        "slot": "2026-11-07T06:17:00Z",
        "covered": "false",
        "run_id": "",
    }


def test_a_manual_run_covers_the_slot_so_a_late_scheduled_run_skips() -> None:
    # 4 Nov: GitHub started the 06:17 slot at 14:35. With a run at 09:46 it skips.
    runs = [run("2026-11-07T09:46:16Z", run_id="20261107T094616Z")]
    got = check_slot(runs, at(7, 14, 35), active_crons())
    assert got["covered"] == "true"
    assert got["run_id"] == "20261107T094616Z"


@pytest.mark.parametrize(
    ("status", "covered"), [("partial", "true"), ("held", "true"), ("crashed", "false")]
)
def test_statuses_that_cover_a_slot(status: str, covered: str) -> None:
    runs = [run("2026-11-07T06:20:00Z", status)]
    assert check_slot(runs, at(7, 8, 47), active_crons())["covered"] == covered


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
    # Every job that reads stores or writes outputs waits for the gate.
    assert daily["jobs"]["fetch"]["needs"] == "slot"
    assert daily["jobs"]["run"]["needs"] == ["slot", "fetch"]
    for job in ("fetch", "run"):
        assert "needs.slot.outputs.run == 'true'" in daily["jobs"][job]["if"]
    watchdog = yaml.safe_load((WF / "watchdog.yml").read_text())
    assert watchdog["permissions"] == {"contents": "read", "actions": "write", "issues": "write"}
    steps = watchdog["jobs"]["check"]["steps"]
    rescue = next(s for s in steps if s.get("id") == "rescue")
    assert "gh workflow run daily.yml" in rescue["run"]
    assert "steps.busy.outputs.busy == 'false'" in rescue["if"]


# -- the daily gate (INC-009) -------------------------------------------------------
def test_on_time_dispatch_runs_and_the_late_schedule_event_then_skips() -> None:
    crons = active_crons()
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
    got = gate("schedule", [], at(22, 14, 21), cron="17 6 * * *", crons=active_crons())
    assert got["run"] == "true"


def test_late_events_of_the_removed_black_friday_crons_skip() -> None:
    crons = active_crons()
    runs = [run("2026-11-27T06:18:00Z", run_id="r6")]
    # GitHub may still deliver a late event of a cron the workflow no longer has.
    for cron in ("17 0,12 26-30 11 *", "17 18 26-30 11 *"):
        assert gate("schedule", runs, at(27, 20, 30), cron=cron, crons=crons)["run"] == "false"


def test_black_friday_extra_slots_end_at_the_lift() -> None:
    got = past_extra_slots(at(25, 0), at(3, 0, month=12))
    # The lift reached main after the 18:17 slot of 27 Nov had run (BFCM_2026_END).
    assert got == [
        at(26, 0, 17),
        at(26, 12, 17),
        at(26, 18, 17),
        at(27, 0, 17),
        at(27, 12, 17),
        at(27, 18, 17),
    ]


def test_dispatch_slot_rules() -> None:
    crons = active_crons()
    # A slot that is not in the schedule, a stale slot and a malformed value never run.
    assert (
        gate("workflow_dispatch", [], at(22, 7), slot="2026-11-22T07:17Z", crons=crons)["run"]
        == "false"
    )
    stale = gate("workflow_dispatch", [], at(23, 6, 20), slot="2026-11-22T06:17Z", crons=crons)
    assert stale["run"] == "false"
    assert "no longer the current slot" in stale["reason"]
    assert gate("workflow_dispatch", [], at(22, 6), slot="tomorrow", crons=crons)["run"] == "false"
    # The Black Friday extra slots are gone.
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
    states = slot_states(runs, at(10, 7), active_crons())
    assert [(s.slot.day, s.state) for s in states] == [
        (4, "late"),
        (5, "on_time"),
        (6, "late"),
        (7, "missed"),
        (8, "held"),
        (9, "missed"),
        (10, "pending"),
    ]
    acc = accounting(runs, at(10, 7), active_crons())
    assert (acc["slots"], acc["on_time"], acc["late"], acc["held"], acc["missed"]) == (
        6,
        1,
        2,
        1,
        2,
    )
    assert acc["pending"] == 1


def test_past_black_friday_slots_stay_in_the_accounting() -> None:
    # 26 Nov and 27 Nov had four due slots each before the lift; from then on one a
    # day. A run at 19:00 on 27 Nov belongs to 18:17.
    runs = [run(f"2026-11-26T{h:02d}:18:00Z", run_id=f"a{h}") for h in (0, 6, 12, 18)]
    runs += [run("2026-11-27T00:18:00Z", run_id="b0"), run("2026-11-27T06:18:00Z", run_id="b6")]
    runs += [run("2026-11-27T12:18:00Z", run_id="b12"), run("2026-11-27T19:00:00Z", run_id="x")]
    runs += [run("2026-11-27T21:00:00Z", run_id="y")]
    runs += [run("2026-11-28T06:18:00Z")]
    states = [(s.slot, s.state, s.run_id) for s in slot_states(runs, at(28, 9), active_crons())]
    assert [(t.day, t.hour) for t, _, _ in states] == [
        (26, 0),
        (26, 6),
        (26, 12),
        (26, 18),
        (27, 0),
        (27, 6),
        (27, 12),
        (27, 18),
        (28, 6),
    ]
    assert {state for _, state, _ in states} == {"on_time"}
    assert states[5][2] == "b6"


def test_accounting_of_the_real_history_counts_late_runs_not_missed_runs() -> None:
    # The committed run log (4-20 Nov): every slot got a good run, none within 2 h.
    lines = (ROOT / "data" / "runs.jsonl").read_text().splitlines()
    runs = [json.loads(line) for line in lines if line.strip()]
    cutoff = [r for r in runs if r["started_at"] < "2026-11-21"]
    acc = accounting(cutoff, at(21, 0, 0), active_crons())
    assert (acc["slots"], acc["on_time"], acc["late"], acc["missed"]) == (17, 0, 17, 0)


# -- the on-time count starts with the on-time trigger (INC-009) ----------------------
def dispatched(
    started: str, slot: str, by: str = "trigger", status: str = "ok"
) -> dict[str, object]:
    r = run(started, status, run_id=started)
    r["trigger"] = "workflow_dispatch"
    r["dispatch"] = {"slot": slot, "by": by}
    return r


def scheduled(started: str) -> dict[str, object]:
    r = run(started, run_id=started)
    r["trigger"] = "schedule"
    return r


HISTORY = [
    scheduled("2026-11-19T15:49:25Z"),  # 9 h 32 late
    scheduled("2026-11-20T15:30:59Z"),  # 9 h 13 late
    scheduled("2026-11-21T13:29:00Z"),  # 7 h 12 late
]


def test_before_the_trigger_every_slot_is_kept_but_no_on_time_count_is_shown() -> None:
    runs = [*HISTORY, dispatched("2026-11-21T20:00:00Z", "2026-11-21T06:17Z", by="watchdog")]
    acc = accounting(runs, at(22, 5), active_crons())
    assert (acc["slots"], acc["delivered"], acc["late"], acc["on_time"]) == (3, 3, 3, 0)
    assert acc["on_time_since"] is None  # a watchdog dispatch is not the on-time trigger
    assert acc["on_time_pct"] is None
    assert acc["note"] == (
        "So far GitHub started the scheduled run 7-9 h late; "
        "every day was still delivered (INC-009)."
    )


def test_on_time_count_and_percentage_start_at_the_first_dispatched_slot() -> None:
    runs = [
        *HISTORY,
        dispatched("2026-11-22T06:18:10Z", "2026-11-22T06:17Z"),
        dispatched("2026-11-23T06:18:05Z", "2026-11-23T06:17Z"),
        # 24 Nov: the dispatch failed; GitHub's late schedule event filled the slot.
        scheduled("2026-11-24T14:02:00Z"),
    ]
    acc = accounting(runs, at(25, 5), active_crons())
    assert acc["on_time_since"] == "2026-11-22T06:17:00Z"
    assert acc["since"] == {"slots": 3, "on_time": 2, "late": 1, "held": 0, "missed": 0}
    assert acc["on_time_pct"] == 66.7  # only slots from 22 Nov on
    # Every earlier slot stays in the counts.
    assert (acc["slots"], acc["delivered"], acc["on_time"], acc["late"]) == (6, 6, 2, 4)
    assert acc["note"] == (
        "Before 22 Nov 2026, GitHub started the scheduled run 7-9 h late; "
        "every day was still delivered (INC-009)."
    )


def test_note_says_how_many_were_delivered_when_a_day_was_missed() -> None:
    runs = [HISTORY[0], HISTORY[2], dispatched("2026-11-22T06:18:00Z", "2026-11-22T06:17Z")]
    acc = accounting(runs, at(22, 9), active_crons())
    assert str(acc["note"]).endswith("; 2 of 3 due runs were still delivered (INC-009).")


def test_dispatch_slot_is_normalised_and_check_is_not_a_slot() -> None:
    assert dispatch_slot("2026-11-22T06:17Z") == "2026-11-22T06:17:00Z"
    assert dispatch_slot("check") == ""
    assert dispatch_slot("auto") == ""  # resolved by the gate, not by the run
    assert dispatch_slot("") == ""
    assert dispatch_slot("not a time") == ""


def test_runs_record_who_dispatched_their_slot(monkeypatch: pytest.MonkeyPatch) -> None:
    from pricemon.run import _env_run_meta

    monkeypatch.setenv("GITHUB_EVENT_NAME", "workflow_dispatch")
    monkeypatch.setenv("DISPATCH_SLOT", "2026-11-22T06:17Z")
    monkeypatch.setenv("DISPATCH_BY", "")
    assert _env_run_meta()["dispatch"] == {"slot": "2026-11-22T06:17:00Z", "by": "trigger"}
    monkeypatch.setenv("DISPATCH_BY", "watchdog")
    assert _env_run_meta()["dispatch"]["by"] == "watchdog"
    monkeypatch.setenv("DISPATCH_SLOT", "")
    assert "dispatch" not in _env_run_meta()  # a manual run
    monkeypatch.setenv("GITHUB_EVENT_NAME", "schedule")
    monkeypatch.setenv("DISPATCH_SLOT", "2026-11-22T06:17Z")
    assert "dispatch" not in _env_run_meta()


def test_workflows_pass_the_dispatch_to_the_run_record() -> None:
    daily = yaml.safe_load((WF / "daily.yml").read_text())
    assert "by" in _on(WF / "daily.yml")["workflow_dispatch"]["inputs"]
    step = next(s for s in daily["jobs"]["run"]["steps"] if s.get("id") == "run")
    # The gate's resolved slot, so `slot: auto` is recorded as the slot it filled.
    assert step["env"] == {
        "DISPATCH_SLOT": "${{ inputs.slot && (needs.slot.outputs.slot || inputs.slot) || '' }}",
        "DISPATCH_BY": "${{ inputs.by }}",
        "RUN_AT": "${{ needs.slot.outputs.run_at }}",
    }
    assert daily["jobs"]["slot"]["outputs"]["slot"] == "${{ steps.decide.outputs.slot }}"
    watchdog = yaml.safe_load((WF / "watchdog.yml").read_text())
    rescue = next(s for s in watchdog["jobs"]["check"]["steps"] if s.get("id") == "rescue")
    assert "-f by=watchdog" in rescue["run"]


# -- slot: auto, for a scheduler with a fixed request body (D-030) -------------------
@pytest.mark.parametrize(("hour", "minute", "wait"), [(6, 15, "120"), (6, 17, "0"), (6, 25, "0")])
def test_auto_fills_the_slot_within_ten_minutes(hour: int, minute: int, wait: str) -> None:
    got = gate("workflow_dispatch", [], at(22, hour, minute), slot="auto", crons=active_crons())
    assert (got["run"], got["slot"], got["wait_s"]) == ("true", "2026-11-22T06:17:00Z", wait)


@pytest.mark.parametrize(("hour", "minute"), [(9, 0), (6, 6), (6, 28), (18, 17)])
def test_auto_away_from_any_active_slot_skips_with_one_line(hour: int, minute: int) -> None:
    got = gate("workflow_dispatch", [], at(22, hour, minute), slot="auto", crons=active_crons())
    assert (got["run"], got["slot"]) == ("false", "")
    assert "no active slot within 10 minutes" in got["reason"]
    assert "\n" not in got["reason"]


def test_auto_at_the_old_black_friday_times_skips() -> None:
    for day, hour in ((27, 18), (28, 0), (28, 12), (1, 0)):
        month = 12 if day == 1 else 11
        got = gate("workflow_dispatch", [], at(day, hour, 17, month), slot="auto")
        assert got["run"] == "false"
        assert "no active slot" in got["reason"]


def test_a_second_auto_and_the_late_schedule_event_skip_after_an_auto_run() -> None:
    crons = active_crons()
    assert gate("workflow_dispatch", [], at(22, 6, 17), slot="auto", crons=crons)["run"] == "true"
    runs = [run("2026-11-22T06:17:40Z", run_id="20261122T061740Z")]
    again = gate("workflow_dispatch", runs, at(22, 6, 20), slot="auto", crons=crons)
    assert again["run"] == "false"
    assert "already filled by run 20261122T061740Z" in again["reason"]
    late = gate("schedule", runs, at(22, 14, 21), cron="17 6 * * *", crons=crons)
    assert late["run"] == "false"


def test_an_auto_run_counts_as_the_on_time_trigger() -> None:
    # The run records the slot the gate resolved, dispatched by "" (the trigger).
    runs = [*HISTORY, dispatched("2026-11-22T06:17:40Z", "2026-11-22T06:17:00Z", by="trigger")]
    acc = accounting(runs, at(22, 9), active_crons())
    assert acc["on_time_since"] == "2026-11-22T06:17:00Z"
    assert acc["since"] == {"slots": 1, "on_time": 1, "late": 0, "held": 0, "missed": 0}


def test_auto_gate_cli(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    args = ["gate", "--runs", str(tmp_path / "none.jsonl"), "--event", "workflow_dispatch"]
    assert main([*args, "--slot", "auto", "--now", "2026-11-22T06:15:00Z"]) == 0
    assert capsys.readouterr().out.splitlines() == [
        "run=true",
        "slot=2026-11-22T06:17:00Z",
        "wait_s=120",
        "reason=auto: dispatch for slot 2026-11-22T06:17:00Z: runs",
    ]


def test_daily_workflow_documents_auto() -> None:
    inputs = _on(WF / "daily.yml")["workflow_dispatch"]["inputs"]
    assert "auto" in inputs["slot"]["description"]
