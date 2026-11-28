"""Source recon: decide which candidate stores can be monitored.

For each candidate the recon records, without keeping any product content:

* robots.txt status and whether ``/products.json`` and ``/products/*.js`` are allowed
* whether the store answers without a block or challenge page
* whether it is a Shopify storefront (``/products.json`` payload shape)
* product and variant counts (pagination stops once the variant cap is passed)
* a sample cross-check of ``/products/<handle>.js`` against ``/products.json``
* the presentment currency with ``country=US`` (JSON-LD ``priceCurrency`` and
  ``Shopify.currency``) and the shop's own country / currency from ``/meta.json``
* when the request asks for it (``terms: true``, from ``recon-005`` on), the
  Terms of Service page: ``terms`` is ``ban``, ``no_ban`` or ``none_found``, with
  the first matching sentence as evidence (``pricemon.terms``)
"""

from __future__ import annotations

import asyncio
import json
import time
from dataclasses import asdict, dataclass, field
from typing import Any

import httpx

from pricemon.polite import (
    EdgeGuard,
    PoliteConfig,
    RobotsDisallowed,
    StoreSession,
    StoreStopped,
    make_client,
)
from pricemon.screen import SCREEN_VERSION, screen_content, screen_evidence
from pricemon.terms import TERMS_PATHS, TermsResult, classify, is_terms_path
from pricemon.witness import (
    is_products_payload,
    jsonld_currencies,
    price_to_cents,
    shopify_active_currency,
)

PAGE_LIMIT = 250
VARIANT_CAP = 3000
MAX_PAGES = 20


@dataclass(frozen=True)
class Candidate:
    store: str
    domain: str
    category: str


@dataclass
class ReconResult:
    store: str
    domain: str
    category: str
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
    requests: int = 0
    retries: int = 0
    retry_causes: list[str] = field(default_factory=list)
    content_flags: dict[str, list[str]] = field(default_factory=dict)
    # Field and word that fired for each content_flags example; the screen version
    # that read the catalog (None when it was not read). D-039.
    content_evidence: dict[str, list[str]] = field(default_factory=dict)
    screen_version: int | None = None
    # Terms of Service (recon-005 on; None when the run did not read terms).
    terms: str | None = None
    terms_source: str | None = None
    terms_sentence: str | None = None
    terms_page: str | None = None
    terms_requests: int = 0
    elapsed_s: float = 0.0
    notes: list[str] = field(default_factory=list)

    @property
    def currency_usd(self) -> bool:
        seen = set(self.jsonld_currency)
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
            fails.append("not shopify")
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


async def recon_store(
    session: StoreSession, cand: Candidate, *, terms: bool = False
) -> ReconResult:
    """Recon one store through ``session`` (already pointed at the candidate domain).

    ``terms``: also read the Terms of Service page, last, after the catalog checks.
    """
    started = time.monotonic()
    res = ReconResult(store=cand.store, domain=cand.domain, category=cand.category)
    try:
        await _recon(session, res)
        if terms and res.shopify and not session.stopped_reason:
            await _terms(session, res)
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
    res.content_evidence = screen_evidence(products)
    res.screen_version = SCREEN_VERSION
    variants = [v for p in products for v in p.get("variants") or []]
    res.products = len(products)
    res.variants = len(variants)
    if res.variants > VARIANT_CAP and len(batch) == PAGE_LIMIT:
        res.variants_capped = True
    if variants:
        available = sum(1 for v in variants if v.get("available") is True)
        res.available_share = round(available / len(variants), 3)


TERMS_BUDGET = 2


async def _terms(session: StoreSession, res: ReconResult) -> None:
    """Search ``TERMS_PATHS`` for the store's terms: at most ``TERMS_BUDGET`` requests
    per page, stopping at the first page with policy text (D-043).

    robots.txt is respected: a disallowed page is not fetched. A redirect is followed
    once, only on the same host and only inside the page's budget. No page with
    policy text means ``none_found``.
    """
    before = session.requests_made
    try:
        result = await _read_terms(session, before)
    finally:
        res.terms_requests = session.requests_made - before
    res.terms, res.terms_source, res.terms_sentence = result.terms, result.source, result.sentence
    res.terms_page = result.page


async def _read_terms(session: StoreSession, before: int) -> TermsResult:
    """The first page in ``TERMS_PATHS`` with policy text, classified (D-043).

    When no page has policy text, the answer of the first page is kept as the
    reason (``robots.txt disallows ...``, ``http 404``, ``no policy text``).
    """
    first: TermsResult | None = None
    for path in TERMS_PATHS:
        result = await _read_terms_page(session, path)
        if result.terms != "none_found":
            return result
        first = first or result
    assert first is not None
    return first


async def _read_terms_page(session: StoreSession, path: str) -> TermsResult:
    if not session.allowed(path):
        return TermsResult("none_found", f"robots.txt disallows {path}")
    start = session.requests_made
    resp = await session.get(path, expect="html", follow_redirects=False, max_attempts=TERMS_BUDGET)
    if resp.is_redirect and session.requests_made - start < TERMS_BUDGET:
        target = resp.url.join(resp.headers.get("location", ""))
        if target.host != resp.url.host:
            return TermsResult("none_found", f"redirects off the store ({target.host})")
        path = target.path
        if not is_terms_path(path):
            # A missing page that redirects to the home page or a collection is not
            # the store's terms (terms-001: JOOLA, "/").
            return TermsResult("none_found", f"redirects to {path or '/'}")
        if not session.allowed(path):
            return TermsResult("none_found", f"robots.txt disallows {path}")
        resp = await session.get(path, expect="html", follow_redirects=False, max_attempts=1)
    if resp.status_code != 200:
        return TermsResult("none_found", f"http {resp.status_code}")
    result = classify(resp.text)
    return TermsResult(result.terms, result.source, result.sentence, page=path)


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
    *,
    terms: bool = False,
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
                result = await recon_store(session, cand, terms=terms)
                passed, fails = result.verdict()
                print(
                    f"{cand.store:<26} {'PASS' if passed else 'fail':<4} "
                    f"variants={result.variants} reqs={result.requests} "
                    f"terms={result.terms or '-'} {', '.join(fails)}",
                    flush=True,
                )
                return result

        return list(await asyncio.gather(*(one(c) for c in candidates)))


async def read_terms_only(session: StoreSession, cand: Candidate) -> dict[str, Any]:
    """The Terms check (``check: terms``, D-043): robots.txt, then the Terms search,
    nothing else. ``terms`` is None when the store could not be read to the end
    (blocked, a 429 that outlasted its retries, robots.txt unreachable)."""
    started = time.monotonic()
    res = ReconResult(store=cand.store, domain=cand.domain, category=cand.category)
    try:
        robots = await session.load_robots()
        res.robots_status = robots.status
        if not session.stopped_reason:
            await _terms(session, res)
    except StoreStopped as exc:
        res.stopped_reason = exc.reason
    except Exception as exc:  # one store must never crash the whole check
        res.notes.append(f"error: {type(exc).__name__}: {exc}"[:300])
    stopped = res.stopped_reason or session.stopped_reason
    unread = bool(stopped) or bool(res.notes)
    return {
        "check": "terms",
        "store": cand.store,
        "category": cand.category,
        "host": session.host,
        "robots_status": res.robots_status,
        "terms": None if unread else res.terms,
        "terms_source": None if unread else res.terms_source,
        "terms_sentence": None if unread else res.terms_sentence,
        "terms_page": None if unread else res.terms_page,
        "requests": session.requests_made,
        "retries": session.retries_made,
        "retry_causes": list(session.retry_causes),
        "stopped_reason": stopped,
        "notes": res.notes,
        "elapsed_s": round(time.monotonic() - started, 1),
    }


async def run_terms_check(
    candidates: list[Candidate], config: PoliteConfig, edge: EdgeGuard, concurrency: int = 4
) -> list[dict[str, Any]]:
    """The Terms check for every candidate, at the recon pace (one shared ``edge``)."""
    gate = asyncio.Semaphore(concurrency)

    async with make_client() as client:

        async def one(cand: Candidate) -> dict[str, Any]:
            async with gate:
                session = StoreSession(
                    client=client, base_url=f"https://{cand.domain}", config=config, edge=edge
                )
                row = await read_terms_only(session, cand)
                print(f"{cand.store:<26} terms={row['terms'] or 'unread'}", flush=True)
                return row

        return list(await asyncio.gather(*(one(c) for c in candidates)))
