"""Fetch one store: the full catalog plus the daily witness sample.

Shopify is described below; WooCommerce and BigCommerce read their catalog through
:mod:`pricemon.platforms` and keep the same rules (robots, pacing, a second source
for the daily sample, currency proof, content screen).

After the catalog is read, every **big price move** against the last good data
(new price below 0.2x or above 5x the old one) is read a second time on its own
(``.js``, the Store API product, or the product page). A move the second read
confirms is kept; one it does not confirm, or one beyond ``MAX_SECOND_READS``, is
**held back**: the row keeps its last good price for this run. A placeholder price
(``PLACEHOLDER_CENTS`` or more, such as $9,999,999.99 on an item that cannot be
bought) is always held back.

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

from pricemon import platforms
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
# Products tried for the daily sample when a sampled one is hidden from the storefront.
SAMPLE_TRIES = 3
# Second read on big moves (same factors as the batch guard's suspicious move).
BIG_MOVE_LOW = 0.2
BIG_MOVE_HIGH = 5.0
MAX_SECOND_READS = 10
# $100,000.00: no product in scope costs this; stores use such values as "not for sale".
PLACEHOLDER_CENTS = 10_000_000

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
    request_log: list[tuple[float, str, str]] = field(default_factory=list)
    elapsed_s: float = 0.0
    witnesses: list[WitnessResult] = field(default_factory=list)
    content_flags: dict[str, list[str]] = field(default_factory=dict)
    jsonld_disagrees: list[str] = field(default_factory=list)
    platform: str = "shopify"
    # Currencies declared by the platform's own catalog API (WooCommerce, BigCommerce).
    api_currencies: set[str] = field(default_factory=set)
    # Variant id -> why its new value is held back this run (it keeps the last good one).
    held_variants: dict[int, str] = field(default_factory=dict)
    second_reads: list[dict[str, Any]] = field(default_factory=list)
    # Sample products skipped because their own page could not be read (hidden).
    sample_skipped: list[str] = field(default_factory=list)

    @property
    def complete(self) -> bool:
        return self.status == "ok"

    @property
    def currencies(self) -> set[str]:
        seen: set[str] = set(self.api_currencies)
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
            "platform": self.platform,
            "status": self.status,
            "reason": self.reason,
            "products": len(self.products),
            "variants": sum(len(p["variants"]) for p in self.products),
            "pages": self.pages,
            "requests": self.requests,
            "retries": self.retries,
            "retry_causes": self.retry_causes,
            "retry_details": self.retry_details,
            "request_log": [list(entry) for entry in self.request_log],
            "elapsed_s": self.elapsed_s,
            "currencies": sorted(self.currencies),
            "witnesses": [w.__dict__ for w in self.witnesses],
            "content_flags": self.content_flags,
            "jsonld_disagrees": self.jsonld_disagrees,
            "held_back": len(self.held_variants),
            "held_reasons": sorted({r.split(":")[0] for r in self.held_variants.values()}),
            "second_reads": self.second_reads,
            "sample_skipped": self.sample_skipped,
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


async def _witness_page(
    session: StoreSession, product: dict[str, Any], w: WitnessResult, path: str | None = None
) -> None:
    resp = await session.get(path or f"/products/{w.handle}", expect="html")
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
    if not offers or not w.jsonld_compared:
        # A page whose offers carry no price is not a comparison.
        w.jsonld = "no_offers"
    elif w.jsonld_price_diffs:
        w.jsonld = "mismatch"
    else:
        w.jsonld = "match"


def big_move(old_cents: int, new_cents: int) -> bool:
    ratio = new_cents / old_cents
    return ratio < BIG_MOVE_LOW or ratio > BIG_MOVE_HIGH


async def _reread_price(
    session: StoreSession, store: Store, product: dict[str, Any], vid: int
) -> int | None:
    """One variant's price, read again on its own."""
    if store.platform == "woocommerce":
        return await platforms.woo_variant_price(session, vid)
    if store.platform == "bigcommerce":
        page = await platforms.bc_read(session, str(product["handle"]))
        return page["ld_price"] if page else None
    resp = await session.get(f"/products/{product['handle']}.js")
    data = _json(resp)
    if resp.status_code != 200 or not isinstance(data, dict):
        return None
    for v in data.get("variants") or []:
        if v.get("id") == vid and isinstance(v.get("price"), int):
            return int(v["price"])
    return None


async def second_reads(
    session: StoreSession, store: Store, out: StoreFetch, prev: dict[int, int]
) -> None:
    """Read every big price move again; hold back what the second read does not confirm."""
    reads = 0
    for product in out.products:
        for v in product["variants"]:
            vid, new = v.get("id"), price_to_cents(v.get("price"))
            if not isinstance(vid, int) or new is None or new <= 0:
                continue
            if new >= PLACEHOLDER_CENTS:
                out.held_variants[vid] = "placeholder price"
                continue
            old = prev.get(vid)
            if old is None or old <= 0 or not big_move(old, new) or vid in out.held_variants:
                continue
            record: dict[str, Any] = {"variant_id": vid, "old_cents": old, "new_cents": new}
            if reads >= MAX_SECOND_READS:
                record["verdict"] = "held: second-read budget used"
                out.held_variants[vid] = "big move: second-read budget used"
            else:
                reads += 1
                try:
                    again = await _reread_price(session, store, product, vid)
                except RobotsDisallowed:
                    again = None
                record["reread_cents"] = again
                if again == new:
                    record["verdict"] = "confirmed"
                else:
                    record["verdict"] = "held: not confirmed"
                    out.held_variants[vid] = "big move: second read did not confirm"
            out.second_reads.append(record)


async def fetch_store(
    session: StoreSession, store: Store, day: date, prev: dict[int, int] | None = None
) -> StoreFetch:
    """Fetch one store completely or report why not. Never raises for store problems.

    ``prev``: the store's last good prices (variant id -> cents), for the second read
    on big moves.
    """
    started = time.monotonic()
    out = StoreFetch(
        store_id=store.id, host=store.host, observed_at=datetime.now(UTC), platform=store.platform
    )
    try:
        await _fetch(session, store, day, out)
        if out.status == "ok":
            await second_reads(session, store, out, prev or {})
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
    out.request_log = list(session.request_log)
    out.elapsed_s = round(time.monotonic() - started, 1)
    if out.status != "ok":
        out.products = [] if out.status == "failed" else out.products
    return out


async def _fetch(session: StoreSession, store: Store, day: date, out: StoreFetch) -> None:
    await session.load_robots()
    if session.stopped_reason:
        out.status, out.reason = "failed", session.stopped_reason
        return
    catalog = {
        "shopify": _catalog,
        "woocommerce": platforms.woo_catalog,
        "bigcommerce": platforms.bc_catalog,
    }[store.platform]
    if not await catalog(session, out):
        out.status = "failed"
        return
    out.content_flags = screen_content(out.products, reviewed_titles=store.screen_reviewed)
    if out.content_flags:
        out.status = "excluded"
        out.reason = "excluded category: " + ", ".join(sorted(out.content_flags))
        return
    # The daily sample: the first product in the day's order whose own page can be
    # read. A product listed in the catalog but hidden from the storefront (its .js
    # and page are 404) is skipped, at most SAMPLE_TRIES products per store.
    for product in sample_products(out.products, store.id, day, n=SAMPLE_TRIES):
        w = WitnessResult(product_id=int(product["id"]), handle=str(product["handle"]))
        if store.platform == "woocommerce":
            await platforms.woo_witness_api(session, product, w)
            await _witness_page(session, product, w, path=f"/{w.handle}/")
        elif store.platform == "bigcommerce":
            platforms.bc_witness(product, w)
        else:
            await _witness_js(session, product, w)
            await _witness_page(session, product, w)
        if w.js == "missing" and w.jsonld == "missing" and not w.theme_currency:
            out.sample_skipped.append(w.handle)
            continue
        out.witnesses.append(w)
        if len(out.witnesses) >= SAMPLE_PER_STORE:
            break
    if not out.currencies:
        out.status, out.reason = "failed", "no currency proof on sampled product pages"
        return
    # products.json and .js come from the same backend: if they agree, a JSON-LD
    # price difference is a theme fault, recorded but not blocking (D-019).
    bad = [f"{w.handle}: .js {w.js}" for w in out.witnesses if w.js != "match"]
    if bad:
        out.status, out.reason = "mismatch", "; ".join(bad)
        return
    out.jsonld_disagrees = [
        f"{w.handle}: {w.first_diff}" for w in out.witnesses if w.jsonld == "mismatch"
    ]
    out.status = "ok"
