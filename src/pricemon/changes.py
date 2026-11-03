"""Change events between a variant's previous open version and its new observation."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any, Literal

EventType = Literal[
    "new",
    "removed",
    "price_up",
    "price_down",
    "discount_start",
    "discount_end",
    "out_of_stock",
    "back_in_stock",
]
EVENT_TYPES: tuple[EventType, ...] = (
    "new",
    "removed",
    "price_up",
    "price_down",
    "discount_start",
    "discount_end",
    "out_of_stock",
    "back_in_stock",
)


@dataclass(frozen=True)
class State:
    """The tracked attributes of a variant at one point in time."""

    price_cents: int
    compare_at_cents: int | None
    available: bool

    @property
    def discounted(self) -> bool:
        return self.compare_at_cents is not None and self.compare_at_cents > self.price_cents


@dataclass(frozen=True)
class Ident:
    store_id: str
    product_id: int
    variant_id: int
    handle: str
    product_title: str
    variant_title: str


@dataclass(frozen=True)
class ChangeEvent:
    observed_at: datetime
    store_id: str
    product_id: int
    variant_id: int
    handle: str
    product_title: str
    variant_title: str
    event: EventType
    old_price_cents: int | None
    new_price_cents: int | None
    old_compare_at_cents: int | None
    new_compare_at_cents: int | None
    price_change_pct: float | None

    def to_row(self) -> dict[str, Any]:
        row = asdict(self)
        row["observed_at"] = self.observed_at.isoformat().replace("+00:00", "Z")
        return row


def _pct(old: int, new: int) -> float:
    return round((new - old) / old * 100, 1)


def diff(ident: Ident, old: State | None, new: State | None, at: datetime) -> list[ChangeEvent]:
    """Events for one variant. ``old``/``new`` is None when the variant is new/removed."""
    kinds: list[EventType] = []
    if old is None and new is None:
        return []
    if old is None:
        kinds.append("new")
    elif new is None:
        kinds.append("removed")
    else:
        if new.price_cents > old.price_cents:
            kinds.append("price_up")
        elif new.price_cents < old.price_cents:
            kinds.append("price_down")
        if new.discounted and not old.discounted:
            kinds.append("discount_start")
        elif old.discounted and not new.discounted:
            kinds.append("discount_end")
        if old.available and not new.available:
            kinds.append("out_of_stock")
        elif new.available and not old.available:
            kinds.append("back_in_stock")
    pct = _pct(old.price_cents, new.price_cents) if old and new else None
    return [
        ChangeEvent(
            observed_at=at,
            store_id=ident.store_id,
            product_id=ident.product_id,
            variant_id=ident.variant_id,
            handle=ident.handle,
            product_title=ident.product_title,
            variant_title=ident.variant_title,
            event=kind,
            old_price_cents=old.price_cents if old else None,
            new_price_cents=new.price_cents if new else None,
            old_compare_at_cents=old.compare_at_cents if old else None,
            new_compare_at_cents=new.compare_at_cents if new else None,
            price_change_pct=pct if kind in ("price_up", "price_down") else None,
        )
        for kind in kinds
    ]
