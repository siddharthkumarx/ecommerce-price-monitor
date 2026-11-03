"""Parsers for the three price witnesses a Shopify storefront exposes.

* ``/products.json`` - the catalog (prices as decimal strings).
* ``/products/<handle>.js`` - one product (prices as integer cents).
* JSON-LD ``Product`` / ``ProductGroup`` on the product page (``priceCurrency``).

Only prices, availability and identifiers are read. Descriptions and images are
never kept.
"""

from __future__ import annotations

import json
import re
from collections.abc import Iterator
from decimal import Decimal, InvalidOperation
from typing import Any

_LD_JSON = re.compile(
    r"<script[^>]*type\s*=\s*[\"']application/ld\+json[\"'][^>]*>(.*?)</script>",
    re.IGNORECASE | re.DOTALL,
)
_SHOPIFY_CURRENCY = re.compile(r"Shopify\.currency\s*=\s*\{[^}]*\"active\"\s*:\s*\"([A-Z]{3})\"")


def price_to_cents(value: str | int | float | None) -> int | None:
    """Convert a Shopify decimal price string ("19.99") to integer cents."""
    if value is None or isinstance(value, bool):
        return None
    try:
        dec = Decimal(str(value))
    except InvalidOperation:
        return None
    cents = dec * 100
    if cents != cents.to_integral_value():
        return None
    return int(cents)


def _walk(node: Any) -> Iterator[dict[str, Any]]:
    if isinstance(node, dict):
        yield node
        for value in node.values():
            yield from _walk(value)
    elif isinstance(node, list):
        for item in node:
            yield from _walk(item)


def _types(node: dict[str, Any]) -> set[str]:
    raw = node.get("@type")
    if isinstance(raw, str):
        return {raw}
    if isinstance(raw, list):
        return {t for t in raw if isinstance(t, str)}
    return set()


def jsonld_blocks(html: str) -> list[Any]:
    """Return every parseable JSON-LD block in ``html``."""
    blocks: list[Any] = []
    for raw in _LD_JSON.findall(html):
        try:
            blocks.append(json.loads(raw, strict=False))
        except json.JSONDecodeError:
            continue
    return blocks


def jsonld_offers(html: str) -> list[dict[str, Any]]:
    """Return every ``Offer`` / ``AggregateOffer`` reachable from a Product node."""
    offers: list[dict[str, Any]] = []
    for block in jsonld_blocks(html):
        for node in _walk(block):
            if _types(node) & {"Offer", "AggregateOffer"}:
                offers.append(node)
    return offers


def jsonld_currencies(html: str) -> set[str]:
    """Currencies declared by JSON-LD offers on the page."""
    currencies: set[str] = set()
    for offer in jsonld_offers(html):
        cur = offer.get("priceCurrency")
        if isinstance(cur, str) and len(cur.strip()) == 3:
            currencies.add(cur.strip().upper())
    return currencies


def shopify_active_currency(html: str) -> str | None:
    """The presentment currency from the theme's ``Shopify.currency`` object."""
    match = _SHOPIFY_CURRENCY.search(html)
    return match.group(1) if match else None


def is_products_payload(data: Any) -> bool:
    return isinstance(data, dict) and isinstance(data.get("products"), list)


_VARIANT_IN_URL = re.compile(r"[?&]variant=(\d+)")
JSONLD_AVAILABILITY = {
    "instock": "in_stock",
    "limitedavailability": "in_stock",
    "onlineonly": "in_stock",
    "outofstock": "out_of_stock",
    "soldout": "out_of_stock",
    "discontinued": "out_of_stock",
}


def offer_variant_id(offer: dict[str, Any]) -> int | None:
    """Shopify themes put ``?variant=<id>`` in each offer's ``url``."""
    url = offer.get("url")
    if isinstance(url, str):
        match = _VARIANT_IN_URL.search(url)
        if match:
            return int(match.group(1))
    return None


def offer_availability(offer: dict[str, Any]) -> str | None:
    """Map a schema.org availability URI to our fixed values; None when not comparable."""
    raw = offer.get("availability")
    if not isinstance(raw, str):
        return None
    return JSONLD_AVAILABILITY.get(raw.rstrip("/").rsplit("/", 1)[-1].lower())
