"""Turn raw Shopify catalog JSON into validated :class:`VariantRow` objects.

* Prices: decimal strings to integer cents (no floats anywhere).
* Times: one UTC ``observed_at`` per store fetch.
* ``compare_at_price`` below the price is a stale merchant value: it is dropped
  and counted (docs/decisions.md, D-007).
* $0 variants (free gifts, samples, add-ons) are out of scope (price > 0) and
  counted as ``free``, not as rejects (D-018).
* A variant listed under several products (Shopify combined listings: one variant
  on a page per colour) is kept once when every copy is identical, and counted as
  a duplicate listing; copies that disagree are rejected.
* Rows that still fail validation are rejected and counted, never repaired.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from pydantic import ValidationError

from pricemon.models import VariantRow
from pricemon.witness import price_to_cents

MAX_EXAMPLES = 5

# Fields kept from /products.json. Everything else (body_html, images, options,
# vendor, timestamps) is discarded as soon as the page is parsed.
PRODUCT_FIELDS = ("id", "handle", "title", "product_type", "tags")
VARIANT_FIELDS = ("id", "title", "price", "compare_at_price", "available")


def slim_product(raw: dict[str, Any]) -> dict[str, Any]:
    """Keep only the fields the pipeline uses (no descriptions, no images)."""
    product = {k: raw.get(k) for k in PRODUCT_FIELDS}
    product["variants"] = [
        {k: v.get(k) for k in VARIANT_FIELDS}
        for v in raw.get("variants") or []
        if isinstance(v, dict)
    ]
    return product


@dataclass
class NormalizeStats:
    rows: int = 0
    free: int = 0
    rejected: int = 0
    compare_at_ignored: int = 0
    duplicate_listings: int = 0
    examples: list[str] = field(default_factory=list)

    def reject(self, message: str) -> None:
        self.rejected += 1
        if len(self.examples) < MAX_EXAMPLES:
            self.examples.append(message[:200])


_AVAILABILITY: dict[object, str] = {True: "in_stock", False: "out_of_stock"}


def _title(value: Any) -> str:
    return value.strip()[:255] if isinstance(value, str) else ""


def normalize_products(
    store_id: str, products: list[dict[str, Any]], observed_at: datetime
) -> tuple[list[VariantRow], NormalizeStats]:
    stats = NormalizeStats()
    rows: list[VariantRow] = []
    seen: dict[int, VariantRow] = {}
    for product in products:
        for variant in product.get("variants") or []:
            price = price_to_cents(variant.get("price"))
            if price == 0:
                # Free gifts, samples and add-ons: out of scope (price > 0), not an error.
                stats.free += 1
                continue
            compare_at = price_to_cents(variant.get("compare_at_price"))
            if compare_at is not None and price is not None and compare_at < price:
                compare_at = None
                stats.compare_at_ignored += 1
            if compare_at == 0:
                compare_at = None
            available = variant.get("available")
            try:
                row = VariantRow.model_validate(
                    {
                        "store_id": store_id,
                        "product_id": product.get("id"),
                        "variant_id": variant.get("id"),
                        "handle": product.get("handle"),
                        "product_title": _title(product.get("title")),
                        "variant_title": _title(variant.get("title")),
                        "price_cents": price,
                        "compare_at_cents": compare_at,
                        "availability": _AVAILABILITY.get(available, available),
                        "observed_at": observed_at,
                    }
                )
            except ValidationError as exc:
                first = exc.errors()[0]
                where = ".".join(str(p) for p in first["loc"]) or "row"
                stats.reject(f"variant {variant.get('id')}: {where}: {first['msg']}")
                continue
            kept = seen.get(row.variant_id)
            if kept is not None:
                same = (kept.price_cents, kept.compare_at_cents, kept.availability) == (
                    row.price_cents,
                    row.compare_at_cents,
                    row.availability,
                )
                if same:
                    stats.duplicate_listings += 1
                    if row.product_id < kept.product_id:  # stable: lowest product id wins
                        rows[rows.index(kept)] = row
                        seen[row.variant_id] = row
                else:
                    stats.reject(f"variant {row.variant_id}: duplicate variant id, values differ")
                continue
            seen[row.variant_id] = row
            rows.append(row)
    stats.rows = len(rows)
    return rows, stats
