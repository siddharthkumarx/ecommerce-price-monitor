"""Source recon: decide which candidate stores can be monitored.

For each candidate the recon records, without keeping any product content:

* robots.txt status and whether ``/products.json`` and ``/products/*.js`` are allowed
* whether the store answers without a block or challenge page
* whether it is a Shopify storefront (``/products.json`` payload shape)
* product and variant counts (pagination stops once the variant cap is passed)
* a sample cross-check of ``/products/<handle>.js`` against ``/products.json``
* the presentment currency with ``country=US`` (JSON-LD ``priceCurrency`` and
  ``Shopify.currency``) and the shop's own country / currency from ``/meta.json``

A candidate marked ``platform: woocommerce`` or ``platform: bigcommerce`` is checked
the same way on that platform's public catalog (:mod:`pricemon.platforms`): robots
for the catalog, second-source and product-page paths, catalog size, a second-source
cross-check of one product, and the currency (Store API ``currency_code`` or the
page's JSON-LD / theme data).
"""

from __future__ import annotations

import asyncio
import json
import time
from dataclasses import asdict, dataclass, field
from typing import Any

import httpx

from pricemon import platforms
from pricemon.polite import (
    EdgeGuard,
    PoliteConfig,
    RobotsDisallowed,
    StoreSession,
    StoreStopped,
    make_client,
)
from pricemon.screen import screen_content
from pricemon.witness import (
    is_products_payload,
    jsonld_currencies,
    price_to_cents,
    shopify_active_currency,
)

PAGE_LIMIT = 250
VARIANT_CAP = 5000
MAX_PAGES = 20


@dataclass(frozen=True)
class Candidate:
    store: str
    domain: str
    category: str
    platform: str = "shopify"


@dataclass
class ReconResult:
    store: str
    domain: str
    category: str
    platform: str = "shopify"
    host: str = ""
    robots_status: str = "not-fetched"
    robots_products_json: bool | None = None
    robots_product_js: bool | None = None
    robots_product_page: bool | None = None
    crawl_delay_s: float | None = None
    reachable: bool = False
    stopped_reason: str | None = None
    shopify: bool = False
    products: int | None = None
    variants: int | None = None
    variants_capped: bool = False
    available_share: float | None = None
    sample_handle: str | None = None
    js_crosscheck: str | None = None  # match | mismatch | missing | skipped
    jsonld_currency: list[str] = field(default_factory=list)
    shopify_currency: str | None = None
    meta_country: str | None = None
    meta_currency: str | None = None
    api_currency: list[str] = field(default_factory=list)
    requests: int = 0
    retries: int = 0
    retry_causes: list[str] = field(default_factory=list)
    content_flags: dict[str, list[str]] = field(default_factory=dict)
    elapsed_s: float = 0.0
    notes: list[str] = field(default_factory=list)

    @property
    def currency_usd(self) -> bool:
        seen = set(self.jsonld_currency) | set(self.api_currency)
        if self.shopify_currency:
            seen.add(self.shopify_currency)
        return seen == {"USD"}

    def verdict(self) -> tuple[bool, list[str]]:
        """Whether the store passes recon, with the reasons it fails."""
        fails: list[str] = []
        if self.stopped_reason and self.stopped_reason.startswith("run halted"):
            fails.append("not checked (run halted)")
        elif self.stopped_reason and not self.reachable:
            fails.append("blocked")
        elif self.robots_status == "unreachable":
            fails.append("robots.txt unreachable")
        elif not (self.robots_products_json and self.robots_product_js):
            fails.append("robots disallows")
        elif not self.reachable:
            fails.append("unreachable")
        elif not self.shopify:
            fails.append("not shopify" if self.platform == "shopify" else f"not {self.platform}")
        else:
            if self.stopped_reason:
                fails.append("blocked mid-recon")
            if not self.variants:
                fails.append("empty catalog")
            elif self.variants_capped or self.variants > VARIANT_CAP:
                fails.append("catalog too large")
            if not self.currency_usd:
                fails.append("currency not proven USD")
            if self.js_crosscheck == "mismatch":
                fails.append("witness mismatch")
            elif self.js_crosscheck != "match":
                fails.append("product .js unavailable")
            if self.robots_product_page is False:
                fails.append("robots disallows product page")
            if self.content_flags:
                fails.append("excluded category: " + ", ".join(sorted(self.content_flags)))
        if any(cause.startswith("http 429") for cause in self.retry_causes):
            fails.append("needed 429 retries")
        return (not fails, fails)

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        passed, fails = self.verdict()
        data["passed"] = passed
        data["fail_reasons"] = fails
        return data


async def recon_store(session: StoreSession, cand: Candidate) -> ReconResult:
    """Recon one store through ``session`` (already pointed at the candidate domain)."""
    started = time.monotonic()
    res = ReconResult(
        store=cand.store, domain=cand.domain, category=cand.category, platform=cand.platform
    )
    try:
        if cand.platform == "woocommerce":
            await _recon_woo(session, res)
        elif cand.platform == "bigcommerce":
            await _recon_bc(session, res)
        else:
            await _recon(session, res)
    except StoreStopped as exc:
        res.stopped_reason = exc.reason
    except Exception as exc:  # recon must never crash the whole run
        res.notes.append(f"error: {type(exc).__name__}: {exc}"[:300])
    res.host = session.host
    res.requests = session.requests_made
    res.retries = session.retries_made
    res.retry_causes = list(session.retry_causes)
    res.elapsed_s = round(time.monotonic() - started, 1)
    if session.stopped_reason and not res.stopped_reason:
        res.stopped_reason = session.stopped_reason
    return res


async def _recon(session: StoreSession, res: ReconResult) -> None:
    robots = await session.load_robots()
    res.robots_status = robots.status
    res.crawl_delay_s = robots.crawl_delay_s
    if session.stopped_reason:
        res.stopped_reason = session.stopped_reason
        return
    res.robots_products_json = session.allowed("/products.json", {"limit": PAGE_LIMIT, "page": 1})
    res.robots_product_js = session.allowed("/products/sample-handle.js")
    res.robots_product_page = session.allowed("/products/sample-handle")
    if not res.robots_products_json:
        return

    # Page 1 of the catalog.
    resp = await session.get("/products.json", {"limit": PAGE_LIMIT, "page": 1})
    res.reachable = True
    payload = _json_or_none(resp)
    if resp.status_code != 200 or not is_products_payload(payload):
        res.notes.append(
            f"/products.json: http {resp.status_code}, {resp.headers.get('content-type', '?')}"
        )
        return
    assert isinstance(payload, dict)
    res.shopify = True
    products: list[dict[str, Any]] = list(payload["products"])

    sample = next((p for p in products if p.get("variants") and p.get("handle")), None)
    if sample is not None:
        res.sample_handle = str(sample["handle"])
        # Re-check robots with the real handle: rules can target specific products.
        res.robots_product_js = bool(
            res.robots_product_js and session.allowed(f"/products/{res.sample_handle}.js")
        )
        res.robots_product_page = bool(
            res.robots_product_page and session.allowed(f"/products/{res.sample_handle}")
        )
        await _crosscheck_js(session, res, sample)
        await _currency_from_page(session, res, res.sample_handle)
    await _meta(session, res)

    # Remaining pages until the catalog ends or the variant cap is passed.
    page = 1
    batch = list(payload["products"])
    while len(batch) == PAGE_LIMIT and _count_variants(products) <= VARIANT_CAP:
        page += 1
        if page > MAX_PAGES:
            res.variants_capped = True
            break
        try:
            resp = await session.get("/products.json", {"limit": PAGE_LIMIT, "page": page})
        except RobotsDisallowed:
            res.notes.append(f"robots disallows page {page}")
            break
        data = _json_or_none(resp)
        if resp.status_code != 200 or not is_products_payload(data):
            res.notes.append(f"page {page}: http {resp.status_code}")
            break
        assert isinstance(data, dict)
        batch = list(data["products"])
        products.extend(batch)

    res.content_flags = screen_content(products)
    variants = [v for p in products for v in p.get("variants") or []]
    res.products = len(products)
    res.variants = len(variants)
    if res.variants > VARIANT_CAP and len(batch) == PAGE_LIMIT:
        res.variants_capped = True
    if variants:
        available = sum(1 for v in variants if v.get("available") is True)
        res.available_share = round(available / len(variants), 3)


async def _robots_first(session: StoreSession, res: ReconResult) -> bool:
    robots = await session.load_robots()
    res.robots_status = robots.status
    res.crawl_delay_s = robots.crawl_delay_s
    if session.stopped_reason:
        res.stopped_reason = session.stopped_reason
        return False
    return True


async def _recon_woo(session: StoreSession, res: ReconResult) -> None:
    """WooCommerce: the public Store API (``shopify`` here means "platform confirmed")."""
    if not await _robots_first(session, res):
        return
    path = platforms.WOO_PATH
    res.robots_products_json = session.allowed(path, {"per_page": 100, "page": 1})
    res.robots_product_js = session.allowed(f"{path}/1")
    if not res.robots_products_json:
        return
    resp = await session.get(path, {"per_page": 100, "page": 1})
    res.reachable = True
    page1 = _json_or_none(resp)
    if resp.status_code != 200 or not isinstance(page1, list):
        res.notes.append(f"store api: http {resp.status_code}")
        return
    res.shopify = True
    total = resp.headers.get("x-wp-total", "")
    n_products = int(total) if total.isdigit() else len(page1)
    resp = await session.get(path, {"type": "variation", "per_page": 1, "page": 1})
    vtotal = resp.headers.get("x-wp-total", "")
    n_variations = int(vtotal) if resp.status_code == 200 and vtotal.isdigit() else 0
    items = [p for p in page1 if isinstance(p, dict)]
    simple_share = (
        sum(1 for p in items if p.get("type") != "variable") / len(items) if items else 0.0
    )
    res.products = n_products
    res.variants = round(n_products * simple_share) + n_variations
    res.api_currency = sorted(platforms.woo_currencies(items))
    slim = platforms.woo_products(items, [])
    res.content_flags = screen_content(slim)
    stock = [p.get("is_in_stock") is True for p in items]
    res.available_share = round(sum(stock) / len(stock), 3) if stock else None
    sample = next((p for p in slim if len(p["variants"]) == 1 and p["handle"]), None)
    if sample is None:
        res.js_crosscheck = "missing"
        return
    res.sample_handle = sample["handle"]
    res.robots_product_page = session.allowed(f"/{sample['handle']}/")
    seen = await platforms.woo_reread(session, sample)
    v = sample["variants"][0]
    again = seen.get(int(v["id"]))
    if again is None:
        res.js_crosscheck = "missing"
    else:
        same = again[0] == price_to_cents(v["price"]) and again[1] is v["available"]
        res.js_crosscheck = "match" if same else "mismatch"
    if res.robots_product_page:
        page = await session.get(f"/{sample['handle']}/", expect="html")
        if page.status_code == 200:
            res.jsonld_currency = sorted(jsonld_currencies(page.text))
    if res.variants > VARIANT_CAP:
        res.variants_capped = True


async def _recon_bc(session: StoreSession, res: ReconResult) -> None:
    """BigCommerce: the product sitemap and one product page (two price sources)."""
    if not await _robots_first(session, res):
        return
    res.robots_products_json = session.allowed(platforms.BC_SITEMAP, {"type": "products"})
    if not res.robots_products_json:
        return
    paths: list[str] = []
    for page in range(1, platforms.BC_MAX_SITEMAP_PAGES + 1):
        resp = await session.get(
            platforms.BC_SITEMAP, {"type": "products", "page": page}, expect="text"
        )
        res.reachable = True
        if resp.status_code == 404 and page > 1:
            break
        found = platforms.bc_sitemap_paths(resp.text) if resp.status_code == 200 else []
        if not found:
            break
        paths += [p for p in found if p not in paths]
    if not paths:
        res.notes.append("empty product sitemap")
        return
    res.products = res.variants = len(paths)
    res.content_flags = screen_content(
        [{"title": p.replace("-", " "), "variants": []} for p in paths]
    )
    res.sample_handle = paths[0]
    res.robots_product_page = res.robots_product_js = session.allowed(f"/{paths[0]}/")
    if not res.robots_product_page:
        return
    page_data = await platforms.bc_read(session, paths[0])
    if page_data is None:
        res.js_crosscheck = "missing"
        res.notes.append("sample page is not a priced BigCommerce product page")
        return
    res.shopify = True
    res.jsonld_currency = sorted(page_data["currencies"])
    res.js_crosscheck = "match" if platforms.bc_agree(page_data) is None else "mismatch"
    res.available_share = None
    if res.variants > platforms.BC_MAX_PRODUCTS:
        res.variants_capped = True


def _count_variants(products: list[dict[str, Any]]) -> int:
    return sum(len(p.get("variants") or []) for p in products)


def _json_or_none(resp: httpx.Response, *, any_type: bool = False) -> Any:
    """Decode a JSON body; ``any_type`` also accepts product ``.js`` (served as JavaScript)."""
    if not any_type and "json" not in resp.headers.get("content-type", ""):
        return None
    try:
        return resp.json()
    except (json.JSONDecodeError, UnicodeDecodeError):
        return None


async def _crosscheck_js(session: StoreSession, res: ReconResult, sample: dict[str, Any]) -> None:
    handle = str(sample["handle"])
    if not res.robots_product_js:
        res.js_crosscheck = "skipped"
        return
    resp = await session.get(f"/products/{handle}.js")
    data = _json_or_none(resp, any_type=True)
    if resp.status_code != 200 or not isinstance(data, dict):
        res.js_crosscheck = "missing"
        res.notes.append(f"product .js: http {resp.status_code}")
        return
    json_prices = {
        int(v["id"]): price_to_cents(v.get("price")) for v in sample["variants"] if "id" in v
    }
    js_prices = {int(v["id"]): v.get("price") for v in data.get("variants") or [] if "id" in v}
    shared = json_prices.keys() & js_prices.keys()
    if not shared:
        res.js_crosscheck = "mismatch"
        res.notes.append("product .js shares no variant ids with products.json")
        return
    diffs = [vid for vid in shared if json_prices[vid] != js_prices[vid]]
    res.js_crosscheck = "match" if not diffs else "mismatch"
    if diffs:
        res.notes.append(f"product .js price differs on {len(diffs)}/{len(shared)} variants")


async def _currency_from_page(session: StoreSession, res: ReconResult, handle: str) -> None:
    if not res.robots_product_page:
        res.notes.append("robots disallows product page; no JSON-LD currency")
        return
    resp = await session.get(f"/products/{handle}", expect="html")
    if resp.status_code != 200:
        res.notes.append(f"product page: http {resp.status_code}")
        return
    html = resp.text
    res.jsonld_currency = sorted(jsonld_currencies(html))
    res.shopify_currency = shopify_active_currency(html)
    if not res.jsonld_currency:
        res.notes.append("no JSON-LD offer currency on product page")


async def _meta(session: StoreSession, res: ReconResult) -> None:
    try:
        resp = await session.get("/meta.json")
    except RobotsDisallowed:
        return
    data = _json_or_none(resp)
    if resp.status_code == 200 and isinstance(data, dict):
        country = data.get("country")
        currency = data.get("currency")
        res.meta_country = country if isinstance(country, str) else None
        res.meta_currency = currency if isinstance(currency, str) else None


async def run_recon(
    candidates: list[Candidate],
    config: PoliteConfig,
    edge: EdgeGuard,
    concurrency: int = 4,
) -> list[ReconResult]:
    """Recon all candidates.

    Stores overlap only to hide latency: requests within a store are sequential and
    every request in the run passes the shared ``edge`` pacer.
    """
    gate = asyncio.Semaphore(concurrency)

    async with make_client() as client:

        async def one(cand: Candidate) -> ReconResult:
            async with gate:
                session = StoreSession(
                    client=client, base_url=f"https://{cand.domain}", config=config, edge=edge
                )
                result = await recon_store(session, cand)
                passed, fails = result.verdict()
                print(
                    f"{cand.store:<26} {'PASS' if passed else 'fail':<4} "
                    f"variants={result.variants} reqs={result.requests} {', '.join(fails)}",
                    flush=True,
                )
                return result

        return list(await asyncio.gather(*(one(c) for c in candidates)))
