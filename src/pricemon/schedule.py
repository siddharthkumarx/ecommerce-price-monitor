"""The daily workflow's schedule, as data.

``CRONS`` must equal the ``schedule`` entries of .github/workflows/daily.yml
(tests/test_outputs.py checks this). Only the cron subset used there is
supported: fixed minute, hour lists, day-of-month ranges or lists, month lists.
"""

from __future__ import annotations

from collections.abc import Iterator
from datetime import UTC, datetime, timedelta

CRONS: tuple[str, ...] = (
    "17 6 * * *",
    "17 0,12,18 26-30 11 *",
    "17 0,12,18 1 12 *",
)
GRACE = timedelta(hours=3)


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


def missed_slots(
    run_starts: list[datetime], first: datetime, now: datetime, crons: tuple[str, ...] = CRONS
) -> list[datetime]:
    """Slots since ``first`` (exclusive of the last ``GRACE``) with no good run within GRACE."""
    starts = sorted(run_starts)
    missed: list[datetime] = []
    for slot in slots(first, now - GRACE, crons):
        if not any(slot <= s <= slot + GRACE for s in starts):
            missed.append(slot)
    return missed
