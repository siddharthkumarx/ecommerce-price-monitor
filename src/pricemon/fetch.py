"""Fetch one store: the full catalog plus the daily witness sample.

Witnesses (docs/architecture.md, "Fetch and witnesses"):

1. ``/products.json`` pages: every row.
2. ``/products/<handle>.js`` for the sample: integer-cent prices and availability
   must equal ``/products.json`` for every shared variant.
3. The product page's JSON-LD offers for the sample: prices must equal
   ``/products.json``; ``priceCurrency`` (or the theme's ``Shopify.currency``) is
   the currency proof.

Raw bodies are parsed and dropped; only slim product dicts survive
(:func:`pricemon.normalize.slim_product`).
"""

from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass, field
from datetime import UTC, date, datetime
from typing import Any, Literal

import httpx

from pricemon.normalize import slim_product
from pricemon.polite import RobotsDisallowed, StoreSession, StoreStopped
from pricemon.screen import screen_content
from pricemon.stores import Store
from pricemon.witness import (
    is_products_payload,
    jsonld_currencies,
    jsonld_offers,
    offer_availability,
    offer_variant_id,
    price_to_cents,
    shopify_active_currency,
)

PAGE_LIMIT = 250
MAX_PAGES = 40
SAMPLE_PER_STORE = 1

FetchStatus = Literal["ok", "failed", "mismatch", "excluded"]


@dataclass
class WitnessResult:
    product_id: int
    handle: str
    js: str = "missing"  # match | mismatch | missing
    js_compared: int = 0
    js_price_diffs: int = 0
    js_stock_diffs: int = 0
    jsonld: str = "missing"  # match | mismatch | no_offers | missing
    jsonld_compared: int = 0
    jsonld_price_diffs: int = 0
    jsonld_stock_diffs: int = 0
    first_diff: str | None = None
    currencies: list[str] = field(default_factory=list)
    theme_currency: str | None = None


@dataclass
class StoreFetch:
    store_id: str
    host: str
    observed_at: datetime
    status: FetchStatus = "failed"
    reason: str | None = None
    products: list[dict[str, Any]] = field(default_factory=list)
    pages: int = 0
    requests: int = 0
    retries: int = 0
    retry_causes: list[str] = field(default_factory=list)
    retry_details: list[str] = field(default_factory=list)
    elapsed_s: float = 0.0
    witnesses: list[WitnessResult] = field(default_factory=list)
    content_flags: dict[str, list[str]] = field(default_factory=dict)

    @property
    def complete(self) -> bool:
        return self.status == "ok"

    @property
    def currencies(self) -> set[str]:
        seen: set[str] = set()
        for w in self.witnesses:
            seen.update(w.currencies)
            if w.theme_currency:
                seen.add(w.theme_currency)
        return seen

    def report(self) -> dict[str, Any]:
        """Summary for runs.jsonl (no catalog content)."""
        return {
            "store_id": self.store_id,
            "host": self.host,
            "status": self.status,
            "reason": self.reason,
            "products": len(self.products),
            "variants": sum(len(p["variants"]) for p in self.products),
            "pages": self.pages,
            "requests": self.requests,
            "retries": self.retries,
            "retry_causes": self.retry_causes,
            "retry_details": self.retry_details,
            "elapsed_s": self.elapsed_s,
            "currencies": sorted(self.currencies),
            "witnesses": [w.__dict__ for w in self.witnesses],
            "content_flags": self.content_flags,
        }


def sample_products(
    products: list[dict[str, Any]], store_id: str, day: date, n: int = SAMPLE_PER_STORE
) -> list[dict[str, Any]]:
    """Stable daily sample: rotates every day, reproducible for a given day."""

    def key(p: dict[str, Any]) -> str:
        return hashlib.sha256(f"{day.isoformat()}|{store_id}|{p['id']}".encode()).hexdigest()

    eligible = [p for p in products if p.get("variants") and p.get("handle") and p.get("id")]
    return sorted(eligible, key=key)[:n]


def _json(resp: httpx.Response) -> Any:
    try:
        return json.loads(resp.content)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return None


async def _catalog(session: StoreSession, out: StoreFetch) -> bool:
    for page in range(1, MAX_PAGES + 1):
        resp = await session.get("/products.json", {"limit": PAGE_LIMIT, "page": page})
        out.pages = page
        data = _json(resp)
        if resp.status_code != 200 or not is_products_payload(data):
            out.reason = f"/products.json page {page}: http {resp.status_code}, not a catalog"
            return False
        batch = data["products"]
        out.products.extend(slim_product(p) for p in batch if isinstance(p, dict))
        if len(batch) < PAGE_LIMIT:
            return True
    out.reason = f"/products.json has more than {MAX_PAGES} pages"
    return False


def _variant_map(product: dict[str, Any]) -> dict[int, dict[str, Any]]:
    return {int(v["id"]): v for v in product["variants"] if isinstance(v.get("id"), int)}


async def _witness_js(session: StoreSession, product: dict[str, Any], w: WitnessResult) -> None:
    resp = await session.get(f"/products/{w.handle}.js")
    data = _json(resp)
    if resp.status_code != 200 or not isinstance(data, dict):
        w.js = "missing"
        return
    catalog = _variant_map(product)
    for v in data.get("variants") or []:
        vid = v.get("id")
        if not isinstance(vid, int) or vid not in catalog:
            continue
        w.js_compared += 1
        if v.get("price") != price_to_cents(catalog[vid].get("price")):
            w.js_price_diffs += 1
        if v.get("available") is not catalog[vid].get("available"):
            w.js_stock_diffs += 1
    if not w.js_compared or w.js_price_diffs or w.js_stock_diffs:
        w.js = "mismatch"
    else:
        w.js = "match"


async def _witness_page(session: StoreSession, product: dict[str, Any], w: WitnessResult) -> None:
    resp = await session.get(f"/products/{w.handle}", expect="html")
    if resp.status_code != 200:
        w.jsonld = "missing"
        return
    html = resp.text
    w.currencies = sorted(jsonld_currencies(html))
    w.theme_currency = shopify_active_currency(html)
    offers = jsonld_offers(html)
    catalog = _variant_map(product)
    catalog_prices = {price_to_cents(v.get("price")) for v in catalog.values()}
    for offer in offers:
        price = price_to_cents(offer.get("price"))
        if price is None:
            low, high = (
                price_to_cents(offer.get("lowPrice")),
                price_to_cents(offer.get("highPrice")),
            )
            if low is not None and high is not None:
                w.jsonld_compared += 1
                if low not in catalog_prices or high not in catalog_prices:
                    w.jsonld_price_diffs += 1
            continue
        vid = offer_variant_id(offer)
        w.jsonld_compared += 1
        if vid is not None and vid in catalog:
            expected_price = price_to_cents(catalog[vid].get("price"))
            if price != expected_price:
                w.jsonld_price_diffs += 1
                w.first_diff = w.first_diff or (
                    f"variant {vid}: JSON-LD {price} vs catalog {expected_price} cents"
                )
            stock = offer_availability(offer)
            expected = "in_stock" if catalog[vid].get("available") else "out_of_stock"
            if stock is not None and stock != expected:
                # Some themes cache availability in JSON-LD; counted, not a mismatch.
                w.jsonld_stock_diffs += 1
        elif price not in catalog_prices:
            w.jsonld_price_diffs += 1
            w.first_diff = w.first_diff or (
                f"offer {vid or 'without variant id'}: JSON-LD {price} cents not in catalog prices"
            )
    if not offers:
        w.jsonld = "no_offers"
    elif w.jsonld_price_diffs:
        w.jsonld = "mismatch"
    else:
        w.jsonld = "match"


async def fetch_store(session: StoreSession, store: Store, day: date) -> StoreFetch:
    """Fetch one store completely or report why not. Never raises for store problems."""
    started = time.monotonic()
    out = StoreFetch(store_id=store.id, host=store.host, observed_at=datetime.now(UTC))
    try:
        await _fetch(session, store, day, out)
    except StoreStopped as exc:
        out.status, out.reason = "failed", exc.reason
    except RobotsDisallowed as exc:
        out.status, out.reason = "failed", f"robots.txt disallows {exc}"
    except httpx.HTTPError as exc:  # pragma: no cover - transport errors become StoreStopped
        out.status, out.reason = "failed", f"http error: {type(exc).__name__}"
    out.requests = session.requests_made
    out.retries = session.retries_made
    out.retry_causes = list(session.retry_causes)
    out.retry_details = list(session.retry_details)
    out.elapsed_s = round(time.monotonic() - started, 1)
    if out.status != "ok":
        out.products = [] if out.status == "failed" else out.products
    return out


async def _fetch(session: StoreSession, store: Store, day: date, out: StoreFetch) -> None:
    await session.load_robots()
    if session.stopped_reason:
        out.status, out.reason = "failed", session.stopped_reason
        return
    if not await _catalog(session, out):
        out.status = "failed"
        return
    out.content_flags = screen_content(out.products, reviewed_titles=store.screen_reviewed)
    if out.content_flags:
        out.status = "excluded"
        out.reason = "excluded category: " + ", ".join(sorted(out.content_flags))
        return
    for product in sample_products(out.products, store.id, day):
        w = WitnessResult(product_id=int(product["id"]), handle=str(product["handle"]))
        out.witnesses.append(w)
        await _witness_js(session, product, w)
        await _witness_page(session, product, w)
    if not out.currencies:
        out.status, out.reason = "failed", "no currency proof on sampled product pages"
        return
    bad = [f"{w.handle}: .js {w.js}" for w in out.witnesses if w.js != "match"] + [
        f"{w.handle}: JSON-LD {w.jsonld}" for w in out.witnesses if w.jsonld == "mismatch"
    ]
    if bad:
        out.status, out.reason = "mismatch", "; ".join(bad)
        return
    out.status = "ok"
