from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Any

import httpx

from pricemon.polite import PoliteConfig
from pricemon.recon import Candidate, ReconResult, recon_store
from tests.fakes import ROBOTS_SHOPIFY, session_for

FIXTURES = Path(__file__).parent / "fixtures" / "recon"
CAND = Candidate(store="Example", domain="shop.example", category="apparel")


def _products(n: int, variants_each: int, start: int = 0) -> list[dict[str, Any]]:
    return [
        {
            "id": 1000 + i,
            "handle": f"item-{i}",
            "variants": [
                {"id": 50_000 + i * 10 + v, "price": "28.00", "available": v % 2 == 0}
                for v in range(variants_each)
            ],
        }
        for i in range(start, start + n)
    ]


class FakeShop:
    def __init__(self, total_products: int = 3, variants_each: int = 2, **overrides: Any) -> None:
        self.catalog = _products(total_products, variants_each)
        self.robots = overrides.get("robots", ROBOTS_SHOPIFY)
        self.page_html = overrides.get("page_html", (FIXTURES / "product_page.html").read_text())
        self.js_price_cents = overrides.get("js_price_cents", 2800)
        self.block_catalog = overrides.get("block_catalog", False)

    def __call__(self, request: httpx.Request) -> httpx.Response:
        path = request.url.path
        if path == "/robots.txt":
            return httpx.Response(200, text=self.robots)
        if path == "/products.json":
            if self.block_catalog:
                return httpx.Response(403, text="<title>Just a moment...</title>")
            page = int(request.url.params.get("page", "1"))
            limit = int(request.url.params.get("limit", "30"))
            chunk = self.catalog[(page - 1) * limit : page * limit]
            return httpx.Response(200, json={"products": chunk})
        if path == "/meta.json":
            return httpx.Response(200, json={"country": "US", "currency": "USD"})
        if path.endswith(".js"):
            handle = path.removeprefix("/products/").removesuffix(".js")
            prod = next(p for p in self.catalog if p["handle"] == handle)
            variants = [{"id": v["id"], "price": self.js_price_cents} for v in prod["variants"]]
            return httpx.Response(200, json={"handle": handle, "variants": variants})
        if path.startswith("/products/"):
            return httpx.Response(200, text=self.page_html, headers={"content-type": "text/html"})
        return httpx.Response(404)


def recon(shop: FakeShop) -> ReconResult:
    session, _, _ = session_for(
        shop, base_url=f"https://{CAND.domain}", config=PoliteConfig(delay_s=1, jitter_s=0)
    )
    return asyncio.run(recon_store(session, CAND))


def test_healthy_store_passes() -> None:
    res = recon(FakeShop())
    assert res.verdict() == (True, [])
    assert res.products == 3
    assert res.variants == 6
    assert res.available_share == 0.5
    assert res.js_crosscheck == "match"
    assert res.jsonld_currency == ["USD"]
    assert res.meta_country == "US"


def test_pagination_counts_all_pages() -> None:
    res = recon(FakeShop(total_products=600, variants_each=1))
    assert res.products == 600
    assert res.verdict()[0]


def test_large_catalog_fails_and_stops_early() -> None:
    res = recon(FakeShop(total_products=5000, variants_each=2))
    assert res.verdict() == (False, ["catalog too large"])
    assert res.products is not None
    assert res.products < 5000


def test_robots_disallow_products_json() -> None:
    robots = "User-agent: *\nDisallow: /products.json\n"
    res = recon(FakeShop(robots=robots))
    assert res.verdict() == (False, ["robots disallows"])
    assert res.requests == 1  # only robots.txt


def test_block_page_fails() -> None:
    res = recon(FakeShop(block_catalog=True))
    assert res.verdict() == (False, ["blocked"])
    assert res.stopped_reason
    assert "cloudflare" in res.stopped_reason


def test_non_usd_currency_fails() -> None:
    html = (FIXTURES / "product_page.html").read_text().replace("USD", "CAD")
    res = recon(FakeShop(page_html=html))
    assert res.verdict() == (False, ["currency not proven USD"])


def test_witness_mismatch_fails() -> None:
    res = recon(FakeShop(js_price_cents=2500))
    assert res.verdict() == (False, ["witness mismatch"])
