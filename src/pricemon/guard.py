"""Batch guard: decide whether a run's data is trustworthy enough to publish.

A held run keeps the last good data live (docs/architecture.md, "Validation and
batch guard"; docs/decisions.md D-006, D-008). Every hold reason has a stable
``key`` so that a hold repeating for the same reason in the next run can be
accepted as a real change instead of holding the monitor forever.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field

from pricemon.models import VariantRow

RUN_ROWS_DROP = 0.20
STORE_ROWS_DROP = 0.50
STORE_ROWS_MIN = 20
SUSPICIOUS_LOW = 0.2
SUSPICIOUS_HIGH = 5.0
RUN_SUSPICIOUS_SHARE = 0.05
STORE_SUSPICIOUS_SHARE = 0.20
STORE_SUSPICIOUS_MIN = 10
MASS_CHANGE_SHARE = 0.90
RUN_MATCHED_MIN = 200
REJECT_SHARE = 0.02


@dataclass(frozen=True)
class PrevVersion:
    """The fields of a previous open version the guard needs."""

    price_cents: int
    compare_at_cents: int | None = None

    @property
    def discounted(self) -> bool:
        return self.compare_at_cents is not None and self.compare_at_cents > self.price_cents


@dataclass(frozen=True)
class Hold:
    key: str
    message: str


@dataclass
class StoreGuardStats:
    rows_before: int
    rows_now: int
    matched: int = 0
    price_changed: int = 0
    unexplained: int = 0
    suspicious: int = 0


@dataclass
class GuardResult:
    holds: list[Hold] = field(default_factory=list)
    stores: dict[str, StoreGuardStats] = field(default_factory=dict)
    matched: int = 0
    price_changed: int = 0
    unexplained: int = 0
    suspicious: int = 0

    @property
    def held(self) -> bool:
        return bool(self.holds)

    @property
    def keys(self) -> list[str]:
        return sorted(h.key for h in self.holds)


def _suspicious(old: int, new: int) -> bool:
    ratio = new / old
    return ratio < SUSPICIOUS_LOW or ratio > SUSPICIOUS_HIGH


def check_batch(
    current: Mapping[str, list[VariantRow]],
    previous: Mapping[str, Mapping[int, PrevVersion]],
    rejected: Mapping[str, int],
    non_usd: Mapping[str, list[str]],
) -> GuardResult:
    """Compare complete store fetches with the last good open versions.

    ``current``: rows per store for stores fetched completely in this run.
    ``previous``: last good open versions per store, keyed by variant id.
    ``rejected``: rows rejected by validation per store.
    ``non_usd``: currencies other than USD seen in a store's currency proof.
    """
    result = GuardResult()
    for store_id, currencies in sorted(non_usd.items()):
        result.holds.append(
            Hold(f"currency:{store_id}", f"{store_id}: currency proof shows {currencies}")
        )

    before_total = now_total = 0
    for store_id, rows in sorted(current.items()):
        prev = previous.get(store_id, {})
        stats = StoreGuardStats(rows_before=len(prev), rows_now=len(rows))
        result.stores[store_id] = stats
        before_total += len(prev)
        now_total += len(rows)

        n_rejected = rejected.get(store_id, 0)
        seen = len(rows) + n_rejected
        if seen and n_rejected / seen > REJECT_SHARE:
            result.holds.append(
                Hold(
                    f"rejects:{store_id}",
                    f"{store_id}: validation rejected {n_rejected} of {seen} rows",
                )
            )

        if stats.rows_before >= STORE_ROWS_MIN and stats.rows_now < stats.rows_before * (
            1 - STORE_ROWS_DROP
        ):
            result.holds.append(
                Hold(
                    f"rows_drop:{store_id}",
                    f"{store_id}: rows fell from {stats.rows_before} to {stats.rows_now}",
                )
            )

        for row in rows:
            old = prev.get(row.variant_id)
            if old is None:
                continue
            stats.matched += 1
            if row.price_cents != old.price_cents:
                stats.price_changed += 1
                # A sale sets a compare-at price (and its end removes it): explained.
                if not (row.discounted or old.discounted):
                    stats.unexplained += 1
                if _suspicious(old.price_cents, row.price_cents):
                    stats.suspicious += 1
        result.matched += stats.matched
        result.price_changed += stats.price_changed
        result.unexplained += stats.unexplained
        result.suspicious += stats.suspicious
        if (
            stats.matched >= STORE_SUSPICIOUS_MIN
            and stats.suspicious / stats.matched > STORE_SUSPICIOUS_SHARE
        ):
            result.holds.append(
                Hold(
                    f"suspicious:{store_id}",
                    f"{store_id}: {stats.suspicious} of {stats.matched} prices moved below "
                    f"{SUSPICIOUS_LOW}x or above {SUSPICIOUS_HIGH}x",
                )
            )

    if before_total and now_total < before_total * (1 - RUN_ROWS_DROP):
        result.holds.append(
            Hold("rows_drop:run", f"run rows fell from {before_total} to {now_total}")
        )
    if result.matched >= RUN_MATCHED_MIN:
        if result.suspicious / result.matched > RUN_SUSPICIOUS_SHARE:
            result.holds.append(
                Hold(
                    "suspicious:run",
                    f"{result.suspicious} of {result.matched} matched prices moved by a "
                    "suspicious factor",
                )
            )
        if result.unexplained / result.matched > MASS_CHANGE_SHARE:
            result.holds.append(
                Hold(
                    "mass_change:run",
                    f"{result.unexplained} of {result.matched} matched prices changed "
                    "without a compare-at price",
                )
            )
    return result


def accept_repeat(
    current_keys: list[str], previous_status: str | None, previous_keys: list[str]
) -> bool:
    """A hold is accepted when the previous run was held for the same (or wider) reasons."""
    return (
        bool(current_keys) and previous_status == "held" and set(current_keys) <= set(previous_keys)
    )
