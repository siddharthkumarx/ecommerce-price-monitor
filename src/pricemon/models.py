"""Typed records shared by the pipeline stages."""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Literal

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field, field_validator, model_validator

Availability = Literal["in_stock", "out_of_stock"]
AVAILABILITY_VALUES: tuple[Availability, ...] = ("in_stock", "out_of_stock")


class VariantRow(BaseModel):
    """One variant as observed in one run. Prices are integer US cents."""

    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")

    store_id: str = Field(min_length=1, max_length=64)
    product_id: int = Field(gt=0)
    variant_id: int = Field(gt=0)
    handle: str = Field(min_length=1, max_length=255)
    product_title: str = Field(max_length=255)
    variant_title: str = Field(max_length=255)
    price_cents: int = Field(gt=0)
    compare_at_cents: int | None = Field(default=None, gt=0)
    availability: Availability
    observed_at: AwareDatetime

    @field_validator("observed_at")
    @classmethod
    def _utc(cls, value: datetime) -> datetime:
        if value.utcoffset() != timedelta(0):
            raise ValueError("observed_at must be UTC")
        return value

    @model_validator(mode="after")
    def _compare_at_not_below_price(self) -> VariantRow:
        if self.compare_at_cents is not None and self.compare_at_cents < self.price_cents:
            raise ValueError("compare_at_cents must be >= price_cents")
        return self

    @property
    def available(self) -> bool:
        return self.availability == "in_stock"

    @property
    def discounted(self) -> bool:
        return self.compare_at_cents is not None and self.compare_at_cents > self.price_cents
