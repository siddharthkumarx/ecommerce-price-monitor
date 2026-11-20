"""The daily workflow's schedule, as data.

``CRONS`` must equal the ``schedule`` entries of .github/workflows/daily.yml
(tests/test_outputs.py checks this). Only the cron subset used there is
supported: fixed minute, hour lists, day-of-month ranges or lists, month lists.

``WATCHDOG_CRONS`` must equal the ``schedule`` entries of
.github/workflows/watchdog.yml. They are not run slots: the watchdog only checks
that the latest slot was run, and starts it if not (INC-007).

    python -m pricemon.schedule check --runs data/runs.jsonl \\
        --workflow .github/workflows/daily.yml

prints ``slot=``, ``covered=`` and ``run_id=`` lines for $GITHUB_OUTPUT.

    python -m pricemon.schedule gate --event schedule --cron "17 6 * * *" \\
        --runs data/runs.jsonl
    python -m pricemon.schedule gate --event workflow_dispatch \\
        --slot 2026-11-26T06:17Z --runs data/runs.jsonl

is the daily workflow's gate: it prints ``run=``, ``slot=``, ``wait_s=`` and
``reason=``. A dispatch that names its slot (the on-time external trigger, or the
watchdog) fills that slot exactly like the scheduled run would; GitHub's own
schedule event, which often arrives hours late, then finds the slot filled and
skips (INC-009).
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from collections.abc import Iterator
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path

CRONS: tuple[str, ...] = (
    "17 6 * * *",
    "17 18 26-30 11 *",
    "17 18 1 12 *",
    "17 0,12 26-30 11 *",
    "17 0,12 1 12 *",
)
# The two extra Black Friday / Cyber Monday slots run only when the workflow flag
# BFCM_RUNS_PER_DAY is "4" (owner decision D-021: 4 a day only if the repo is
# public by 26 Nov 2026, otherwise 2).
BFCM_EXTRA_CRONS: frozenset[str] = frozenset({"17 0,12 26-30 11 *", "17 0,12 1 12 *"})


def active_crons(bfcm_runs_per_day: int | None = None) -> tuple[str, ...]:
    """The cron slots that are meant to run, given the BFCM flag (env by default)."""
    if bfcm_runs_per_day is None:
        bfcm_runs_per_day = int(os.environ.get("BFCM_RUNS_PER_DAY", "2"))
    if bfcm_runs_per_day not in (2, 4):
        raise ValueError("BFCM_RUNS_PER_DAY must be 2 or 4")
    if bfcm_runs_per_day == 4:
        return CRONS
    return tuple(c for c in CRONS if c not in BFCM_EXTRA_CRONS)


# Same-day guard (INC-007): 2.5 h after the 06:17 slot, and again after the 12:17
# BFCM slot. Off the hour and the half hour, like every cron here.
WATCHDOG_CRONS: tuple[str, ...] = ("47 8 * * *", "47 16 * * *")

# Honest accounting (INC-009): a slot is on time when a good run started within
# ON_TIME after it, late when the first good run started later the same UTC day
# (and before the next slot), missed when no run started in that window.
ON_TIME = timedelta(hours=2)
GOOD_STATUSES = frozenset({"ok", "partial"})

# A dispatch that names its slot may arrive this much before it (a caller clock
# skew); the gate then waits until the slot so the run starts at or after it.
EARLY = timedelta(minutes=10)
# The slot value of a dispatch that only proves the trigger works: never runs.
CHECK_SLOT = "check"

# A slot counts as run once a run record with one of these statuses started at or
# after it. "held" counts: the pipeline ran, and running it again sooner would
# accept the hold before the owner looked at it. "crashed" does not count.
COVERING_STATUSES = frozenset({"ok", "partial", "held"})


def _field(spec: str, lo: int, hi: int) -> set[int]:
    if spec == "*":
        return set(range(lo, hi + 1))
    out: set[int] = set()
    for part in spec.split(","):
        if "-" in part:
            a, b = part.split("-")
            out.update(range(int(a), int(b) + 1))
        else:
            out.add(int(part))
    return out


def slots(start: datetime, end: datetime, crons: tuple[str, ...] = CRONS) -> Iterator[datetime]:
    """Scheduled run times in ``[start, end)``, UTC, sorted, de-duplicated."""
    times: set[datetime] = set()
    for expr in crons:
        minute, hour, dom, month, dow = expr.split()
        if dow != "*":
            raise ValueError(f"day-of-week not supported: {expr}")
        minutes, hours = _field(minute, 0, 59), _field(hour, 0, 23)
        days, months = _field(dom, 1, 31), _field(month, 1, 12)
        day = start.astimezone(UTC).replace(hour=0, minute=0, second=0, microsecond=0)
        while day < end:
            if day.day in days and day.month in months:
                for h in hours:
                    for m in minutes:
                        t = day.replace(hour=h, minute=m)
                        if start <= t < end:
                            times.add(t)
            day += timedelta(days=1)
    yield from sorted(times)


def latest_slot(now: datetime, crons: tuple[str, ...] | None = None) -> datetime | None:
    """The most recent active slot at or before ``now`` (looking back two days)."""
    found = list(
        slots(now - timedelta(days=2), now + timedelta(seconds=1), crons or active_crons())
    )
    return found[-1] if found else None


def _parse(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(UTC)


def check_slot(
    runs: list[dict[str, object]], now: datetime, crons: tuple[str, ...] | None = None
) -> dict[str, str]:
    """Has the latest slot been run? A late scheduled run and the watchdog both ask."""
    slot = latest_slot(now, crons)
    covering = [
        r
        for r in runs
        if slot is not None
        and r.get("status") in COVERING_STATUSES
        and _parse(str(r["started_at"])) >= slot
    ]
    return {
        "slot": slot.strftime("%Y-%m-%dT%H:%M:%SZ") if slot else "",
        "covered": "true" if covering or slot is None else "false",
        "run_id": str(covering[-1]["run_id"]) if covering else "",
    }


@dataclass(frozen=True)
class SlotState:
    slot: datetime
    state: str  # on_time | late | held | missed | pending
    run_id: str = ""
    started_at: str = ""


def slot_states(
    runs: list[dict[str, object]], now: datetime, crons: tuple[str, ...] | None = None
) -> list[SlotState]:
    """Every slot from the day of the first good run up to ``now``, judged from runs.

    A run belongs to the latest slot at or before its start (the slot the daily gate
    would let it fill). A slot's window ends at the next slot or at the end of its UTC
    day, whichever is first; an empty window is ``pending`` until it ends, then
    ``missed``. A slot whose only runs were held is ``held``.
    """
    crons = crons or active_crons()
    good = sorted(
        (_parse(str(r["started_at"])), str(r["run_id"]), str(r["started_at"]))
        for r in runs
        if r.get("status") in GOOD_STATUSES
    )
    held = sorted(
        (_parse(str(r["started_at"])), str(r["run_id"]), str(r["started_at"]))
        for r in runs
        if r.get("status") == "held"
    )
    if not good and not held:
        return []
    first = min(x[0] for x in good + held)
    day0 = first.replace(hour=0, minute=0, second=0, microsecond=0)
    times = list(slots(day0, now + timedelta(seconds=1), crons))
    later = list(slots(now + timedelta(seconds=1), now + timedelta(days=3), crons))
    out: list[SlotState] = []
    for i, slot in enumerate(times):
        nxt = times[i + 1] if i + 1 < len(times) else (later[0] if later else None)
        day_end = slot.replace(hour=0, minute=0, second=0) + timedelta(days=1)
        end = min(nxt, day_end) if nxt else day_end
        filled = [g for g in good if slot <= g[0] < end]
        if filled:
            t, run_id, started = filled[0]
            state = "on_time" if t - slot <= ON_TIME else "late"
            out.append(SlotState(slot, state, run_id, started))
            continue
        held_here = [h for h in held if slot <= h[0] < end]
        if held_here:
            out.append(SlotState(slot, "held", held_here[0][1], held_here[0][2]))
        elif now < end:
            out.append(SlotState(slot, "pending"))
        else:
            out.append(SlotState(slot, "missed"))
    return out


def dispatch_slot(value: str) -> str:
    """The slot a dispatch named, as ``YYYY-MM-DDTHH:MM:SSZ``; "" for none, ``check`` or junk."""
    value = (value or "").strip()
    if not value or value == CHECK_SLOT:
        return ""
    try:
        return _parse(value).replace(second=0, microsecond=0).strftime("%Y-%m-%dT%H:%M:%SZ")
    except ValueError:
        return ""


def trigger_since(runs: list[dict[str, object]]) -> datetime | None:
    """The first slot the on-time trigger dispatched (a run record with ``dispatch.by``
    "trigger"); None until it has started one. Watchdog dispatches do not count."""
    slots_seen = []
    for r in runs:
        d = r.get("dispatch")
        if isinstance(d, dict) and d.get("by") == "trigger" and d.get("slot"):
            slots_seen.append(_parse(str(d["slot"])))
    return min(slots_seen) if slots_seen else None


def _day(t: datetime) -> str:
    return f"{t.day} {t:%b %Y}"


def schedule_note(
    runs: list[dict[str, object]], states: list[SlotState], since: datetime | None
) -> str:
    """One plain sentence on the slots before the on-time trigger (INC-009).

    The lateness range is that of the scheduled (``schedule``) runs before ``since``,
    from the run log; the delivery part counts those slots' good runs.
    """
    before = [s for s in states if s.state != "pending" and (since is None or s.slot < since)]
    if not before:
        return ""
    trig = {str(r["run_id"]): r.get("trigger") for r in runs}
    hours = [
        (_parse(s.started_at) - s.slot).total_seconds() / 3600
        for s in before
        if s.run_id and s.started_at and trig.get(s.run_id) == "schedule"
    ]
    if hours:
        lo, hi = int(min(hours)), int(max(hours))
        span = f"{lo} h" if lo == hi else f"{lo}-{hi} h"
        late = f"GitHub started the scheduled run {span} late"
    else:
        late = "GitHub's scheduler often started runs late"
    delivered = sum(1 for s in before if s.state in ("on_time", "late"))
    if delivered == len(before):
        kept = "every day was still delivered"
    else:
        kept = f"{delivered} of {len(before)} due runs were still delivered"
    if since is None:
        return f"So far {late}; {kept} (INC-009)."
    return f"Before {_day(since)}, {late}; {kept} (INC-009)."


def accounting(
    runs: list[dict[str, object]], now: datetime, crons: tuple[str, ...] | None = None
) -> dict[str, object]:
    """Slot counts for status.json, the badges and the dashboard.

    Every slot is kept (``slots``, ``on_time``, ``late``, ``held``, ``missed``), and
    ``delivered`` counts the slots that got a good run, late or not. The on-time count
    shown to readers starts at the first slot dispatched by the on-time trigger
    (``on_time_since``): ``since`` holds the counts from that slot on, and
    ``on_time_pct`` is computed only from those slots (None before).
    """
    states = slot_states(runs, now, crons)
    since = trigger_since(runs)
    after = [s for s in states if since is not None and s.slot >= since and s.state != "pending"]
    since_on_time = sum(1 for s in after if s.state == "on_time")

    def of(kind: str) -> list[SlotState]:
        return [s for s in states if s.state == kind]

    def stamp(items: list[SlotState]) -> list[str]:
        return [s.slot.strftime("%Y-%m-%dT%H:%M:%SZ") for s in items[-10:]]

    judged = [s for s in states if s.state != "pending"]
    return {
        "on_time_window_h": int(ON_TIME.total_seconds() // 3600),
        "delivered": sum(1 for s in judged if s.state in ("on_time", "late")),
        "on_time_since": since.strftime("%Y-%m-%dT%H:%M:%SZ") if since else None,
        "since": {
            "slots": len(after),
            "on_time": since_on_time,
            "late": sum(1 for s in after if s.state == "late"),
            "held": sum(1 for s in after if s.state == "held"),
            "missed": sum(1 for s in after if s.state == "missed"),
        },
        "on_time_pct": round(100 * since_on_time / len(after), 1) if after else None,
        "note": schedule_note(runs, states, since),
        "slots": len(judged),
        "on_time": len(of("on_time")),
        "late": len(of("late")),
        "held": len(of("held")),
        "missed": len(of("missed")),
        "pending": len(of("pending")),
        "late_slots": stamp(of("late")),
        "missed_slots": stamp(of("missed")),
    }


def _is_slot(t: datetime, crons: tuple[str, ...]) -> bool:
    return t in set(slots(t, t + timedelta(minutes=1), crons))


def gate(
    event: str,
    runs: list[dict[str, object]],
    now: datetime,
    *,
    cron: str = "",
    slot: str = "",
    crons: tuple[str, ...] | None = None,
) -> dict[str, str]:
    """Should this trigger of the daily workflow run the pipeline?

    - A manual run (``workflow_dispatch`` without a slot) always runs.
    - A dispatch naming a slot (the external on-time trigger, the watchdog) runs only
      for the current slot and only if no run has filled it yet; it may arrive up to
      ``EARLY`` before the slot and then waits for it. ``slot=check`` never runs: it
      proves that the trigger and its token work.
    - A ``schedule`` event runs only if the latest slot is not filled yet; the two
      extra BFCM slots only with BFCM_RUNS_PER_DAY "4".
    """
    crons = crons or active_crons()

    def out(run: bool, reason: str, at: str = "", wait: int = 0) -> dict[str, str]:
        return {
            "run": "true" if run else "false",
            "slot": at,
            "wait_s": str(wait),
            "reason": reason,
        }

    if event == "schedule":
        if cron in BFCM_EXTRA_CRONS and cron not in crons:
            return out(False, f"extra BFCM slot '{cron}' is off (BFCM_RUNS_PER_DAY): skipped")
        c = check_slot(runs, now, crons)
        if c["covered"] == "true":
            return out(
                False, f"slot {c['slot']} already filled by run {c['run_id']}: skipped", c["slot"]
            )
        return out(True, f"slot {c['slot']} not filled yet: runs", c["slot"])
    if event != "workflow_dispatch" or not slot.strip():
        return out(True, f"{event} without a slot: manual run, runs")
    slot = slot.strip()
    if slot == CHECK_SLOT:
        return out(False, "check dispatch: the trigger works, nothing to run")
    try:
        want = _parse(slot).replace(second=0, microsecond=0)
    except ValueError:
        return out(False, f"slot '{slot[:40]}' is not an ISO time: skipped")
    at = want.strftime("%Y-%m-%dT%H:%M:%SZ")
    if not _is_slot(want, crons):
        return out(False, f"{at} is not an active daily slot: skipped", at)
    if now < want - EARLY:
        return out(False, f"{at} is more than {EARLY} away: skipped", at)
    wait = max(0, int((want - now).total_seconds()))
    effective = max(now, want)
    current = latest_slot(effective, crons)
    if current != want:
        cur = current.strftime("%Y-%m-%dT%H:%M:%SZ") if current else "none"
        return out(False, f"{at} is no longer the current slot ({cur}): skipped", at)
    c = check_slot(runs, effective, crons)
    if c["covered"] == "true":
        return out(False, f"slot {at} already filled by run {c['run_id']}: skipped", at)
    return out(True, f"dispatch for slot {at}: runs", at, wait)


def workflow_flag(text: str) -> int:
    """BFCM_RUNS_PER_DAY as set in the daily workflow's text."""
    m = re.search(r'^\s*BFCM_RUNS_PER_DAY:\s*"?([0-9]+)"?\s*$', text, re.MULTILINE)
    if not m:
        raise ValueError("BFCM_RUNS_PER_DAY not found in the workflow")
    return int(m.group(1))


def _read_runs(path: str) -> list[dict[str, object]]:
    try:
        text = Path(path).read_text(encoding="utf-8")
    except FileNotFoundError:
        return []
    return [json.loads(line) for line in text.splitlines() if line.strip()]


def main(argv: list[str] | None = None) -> int:
    # Standard library only, so the workflows run it with the runner's python3
    # without installing the project.
    p = argparse.ArgumentParser(description="Was the latest scheduled slot run?")
    sub = p.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("check")
    c.add_argument("--runs", default="data/runs.jsonl")
    c.add_argument("--workflow", help="read BFCM_RUNS_PER_DAY from this workflow file")
    c.add_argument("--now", help="ISO time, default now (UTC)")
    g = sub.add_parser("gate")
    g.add_argument("--event", required=True)
    g.add_argument("--cron", default="")
    g.add_argument("--slot", default="")
    g.add_argument("--runs", default="data/runs.jsonl")
    g.add_argument("--workflow", help="read BFCM_RUNS_PER_DAY from this workflow file")
    g.add_argument("--now", help="ISO time, default now (UTC)")
    a = p.parse_args(argv)
    flag = None
    if a.workflow:
        flag = workflow_flag(Path(a.workflow).read_text(encoding="utf-8"))
    now = _parse(a.now) if a.now else datetime.now(UTC).replace(microsecond=0)
    if a.cmd == "gate":
        result = gate(
            a.event, _read_runs(a.runs), now, cron=a.cron, slot=a.slot, crons=active_crons(flag)
        )
    else:
        result = check_slot(_read_runs(a.runs), now, active_crons(flag))
    for key, value in result.items():
        print(f"{key}={value}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
