"""Store categories: one list for the register, the run report, the feed and the dashboard.

The first five are the original direct-to-consumer brand stores. The ``*_retail``
categories are multi-brand US retailers (several stores selling the same brands),
added in the F1 expansion; each new store passed a Terms check before it became a
recon candidate (the register of that check is kept privately, not in this repo).
"""

from __future__ import annotations

CATEGORY_TITLES: dict[str, str] = {
    "audio": "Audio",
    "apparel": "Apparel",
    "beauty": "Beauty",
    "home_kitchen": "Home & kitchen",
    "outdoor": "Outdoor",
    "outdoor_retail": "Outdoor retailers",
    "coffee_retail": "Coffee & espresso retailers",
    "pet_retail": "Pet supply retailers",
    "bike_retail": "Bike shops",
}

# Multi-brand retailers have larger catalogs than single-brand stores.
RETAIL_CATEGORIES: frozenset[str] = frozenset(c for c in CATEGORY_TITLES if c.endswith("_retail"))


def title(category: str) -> str:
    return CATEGORY_TITLES.get(category, category)
