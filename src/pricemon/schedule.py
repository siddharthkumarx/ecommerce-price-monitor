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
skips (INC-009). ``--slot auto`` (the on-time trigger, whose request body is fixed)
names the active slot within ``AUTO_WINDOW`` of now, or skips (D-030).
"""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Iterator
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path

CRONS: tuple[str, ...] = ("17 6 * * *",)

# Black Friday 2026: from 26 Nov the workflow also ran at 00:17, 12:17 and 18:17 UTC
# (D-021, D-026). The owner lifted that on 27 Nov 2026 (D-031): one run a day again.
# The extra slots that were due before the lift stay in the slot accounting, so past
# "delivered" and "missed" counts do not change; no cron line names them any more, so
# they never fire again (build-progress item 17).
BFCM_2026_START = datetime(2026, 11, 26, tzinfo=UTC)
BFCM_2026_END = datetime(2026, 11, 27, 18, 30, tzinfo=UTC)
BFCM_2026_CRONS: tuple[str, ...] = ("17 0,12,18 26-30 11 *",)


def active_crons() -> tuple[str, ...]:
    """The cron slots that are meant to run from now on."""
    return CRONS


# Same-day guard (INC-007): 2.5 h after the 06:17 slot, and a second look at 16:47.
# Off the hour and the half hour, like every cron here.
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
# The slot value of a scheduler that cannot put the time in its request body
# (the owner's own cron, D-030, D-035): the active slot within AUTO_WINDOW of now, before or after.
AUTO_SLOT = "auto"
AUTO_WINDOW = timedelta(minutes=10)

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


def past_extra_slots(start: datetime, end: datetime) -> list[datetime]:
    """The Black Friday 2026 extra slots in ``[start, end)`` that were due (before the lift)."""
    lo, hi = max(start, BFCM_2026_START), min(end, BFCM_2026_END)
    return list(slots(lo, hi, BFCM_2026_CRONS)) if lo < hi else []


def due_slots(start: datetime, end: datetime, crons: tuple[str, ...]) -> list[datetime]:
    """Every slot that was or is due in ``[start, end)``: the crons plus past extra slots."""
    return sorted(set(slots(start, end, crons)) | set(past_extra_slots(start, end)))


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
    times = due_slots(day0, now + timedelta(seconds=1), crons)
    later = due_slots(now + timedelta(seconds=1), now + timedelta(days=3), crons)
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
    if not value or value in (CHECK_SLOT, AUTO_SLOT):
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


def auto_slot(now: datetime, crons: tuple[str, ...] | None = None) -> datetime | None:
    """The active slot within ``AUTO_WINDOW`` of ``now`` (before or after), if any.

    Slots are hours apart, so there is at most one; the nearest wins regardless.
    """
    near = slots(
        (now - AUTO_WINDOW).replace(second=0, microsecond=0),
        now + AUTO_WINDOW + timedelta(seconds=1),
        crons or active_crons(),
    )
    found = [t for t in near if abs(t - now) <= AUTO_WINDOW]
    return min(found, key=lambda t: abs(t - now)) if found else None


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
      proves that the trigger and its token work. ``slot=auto`` names the active slot
      within ``AUTO_WINDOW`` of now and then follows the same rule; with no such slot
      it skips.
    - A ``schedule`` event runs only if the latest slot is not filled yet (a late
      event of a cron that was removed, such as a Black Friday slot, finds the
      latest daily slot filled and skips).
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
    if slot == AUTO_SLOT:
        found = auto_slot(now, crons)
        if found is None:
            mins = int(AUTO_WINDOW.total_seconds() // 60)
            return out(
                False,
                f"auto: no active slot within {mins} minutes of {now:%Y-%m-%dT%H:%M:%SZ}: skipped",
            )
        got = gate(event, runs, now, slot=found.strftime("%Y-%m-%dT%H:%M:%SZ"), crons=crons)
        return {**got, "reason": f"auto: {got['reason']}"}
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


def _read_runs(path: str) -> list[dict[str, object]]:
    try:
        text = Path(path).read_text(encoding="utf-8")
    except FileNotFoundError:
        return []
    return [json.loads(line) for line in text.splitlines() if line.strip()]


# Sequential shards of the daily run (D-033): one shard per this many stores, so the
# shard count follows the store list as it grows (D-036). At the unchanged pace 60
# stores take about 20 minutes, well inside a shard's 38-minute budget even with the
# run-wide 429 cooldowns that recon-005 and recon-006 met.
STORES_PER_SHARD = 60
MAX_SHARDS = 8


def monitored_count(stores_yml: str) -> int:
    """Stores listed under ``stores:`` in config/stores.yml (standard library only)."""
    n, inside = 0, False
    for line in stores_yml.splitlines():
        if line and not line.startswith((" ", "#")):
            inside = line.rstrip() == "stores:"
        elif inside and line.startswith("  - id:"):
            n += 1
    return n


def shard_plan(n_stores: int) -> list[int]:
    """The shard numbers for ``n_stores`` stores: 1..k, k = ceil(n / STORES_PER_SHARD)."""
    k = max(1, -(-n_stores // STORES_PER_SHARD))
    return list(range(1, min(k, MAX_SHARDS) + 1))


def main(argv: list[str] | None = None) -> int:
    # Standard library only, so the workflows run it with the runner's python3
    # without installing the project.
    p = argparse.ArgumentParser(description="Was the latest scheduled slot run?")
    sub = p.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("check")
    c.add_argument("--runs", default="data/runs.jsonl")
    c.add_argument("--now", help="ISO time, default now (UTC)")
    g = sub.add_parser("gate")
    g.add_argument("--event", required=True)
    g.add_argument("--cron", default="")
    g.add_argument("--slot", default="")
    g.add_argument("--runs", default="data/runs.jsonl")
    g.add_argument("--now", help="ISO time, default now (UTC)")
    s = sub.add_parser("shards", help="the shard list for the daily workflow's matrix")
    s.add_argument("--stores", default="config/stores.yml")
    a = p.parse_args(argv)
    if a.cmd == "shards":
        n = monitored_count(Path(a.stores).read_text(encoding="utf-8"))
        print(f"stores={n}")
        print(f"shards={json.dumps(shard_plan(n), separators=(',', ':'))}")
        return 0
    now = _parse(a.now) if a.now else datetime.now(UTC).replace(microsecond=0)
    if a.cmd == "gate":
        result = gate(
            a.event, _read_runs(a.runs), now, cron=a.cron, slot=a.slot, crons=active_crons()
        )
    else:
        result = check_slot(_read_runs(a.runs), now, active_crons())
    for key, value in result.items():
        print(f"{key}={value}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
