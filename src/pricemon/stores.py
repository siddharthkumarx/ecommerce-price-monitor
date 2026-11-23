"""The monitored store list (config/stores.yml, generated from recon evidence)."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Literal

import yaml

Platform = Literal["shopify", "woocommerce", "bigcommerce"]
PLATFORMS: tuple[Platform, ...] = ("shopify", "woocommerce", "bigcommerce")

# One table for every renderer (feed, README, dashboard, register). Order = display order.
CATEGORY_TITLES: dict[str, str] = {
    "audio": "Audio",
    "apparel": "Apparel",
    "beauty": "Beauty",
    "home_kitchen": "Home & kitchen",
    "outdoor": "Outdoor",
    "pets": "Pets",
    "coffee_tea": "Coffee & tea",
    "toys_baby": "Toys & baby",
    "fitness": "Fitness",
    "bikes": "Cycling",
    "stationery_edc": "Stationery & everyday carry",
}

PLATFORM_TITLES: dict[str, str] = {
    "shopify": "Shopify",
    "woocommerce": "WooCommerce",
    "bigcommerce": "BigCommerce",
}


def product_url(host: str, handle: str, platform: str = "shopify") -> str:
    """The public product page for a row.

    Shopify rows carry the product handle (``/products/<handle>``); WooCommerce and
    BigCommerce rows carry the product page path itself (``product/<slug>``,
    ``<slug>``), because those platforms let each store choose its URL shape.
    """
    if not host:
        return ""
    if platform == "shopify":
        return f"https://{host}/products/{handle}"
    return f"https://{host}/{handle.strip('/')}/"


@dataclass(frozen=True)
class Store:
    id: str
    name: str
    category: str
    host: str
    screen_reviewed: frozenset[str] = frozenset()
    platform: Platform = "shopify"

    @property
    def base_url(self) -> str:
        return f"https://{self.host}"

    def product_url(self, handle: str) -> str:
        return product_url(self.host, handle, self.platform)


def load_stores(path: Path) -> list[Store]:
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    stores = []
    for s in raw["stores"]:
        platform: Platform = s.get("platform") or "shopify"
        if platform not in PLATFORMS:
            raise ValueError(f"{s['id']}: unknown platform {platform!r}")
        stores.append(
            Store(
                id=str(s["id"]),
                name=str(s["name"]),
                category=str(s["category"]),
                host=str(s["host"]),
                screen_reviewed=frozenset(str(t) for t in s.get("screen_reviewed") or []),
                platform=platform,
            )
        )
    ids = [s.id for s in stores]
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate store ids in stores.yml")
    return stores
