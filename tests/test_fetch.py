"""fetch_store against static Shopify-shaped fixtures in tests/fixtures/shop/."""

from __future__ import annotations

import asyncio
import json
from collections.abc import Callable
from datetime import date
from pathlib import Path
from typing import Any

import httpx

from pricemon.fetch import SAMPLE_PER_STORE, StoreFetch, fetch_store, sample_products
from pricemon.normalize import normalize_products
from pricemon.polite import PoliteConfig
from pricemon.stores import Store
from tests.fakes import ROBOTS_SHOPIFY, session_for

SHOP = Path(__file__).parent / "fixtures" / "shop"
STORE = Store(id="example", name="Example", category="outdoor", host="shop.example")
DAY = date(2026, 11, 4)
Mutator = Callable[[str, str], str]


def shop(
    mutate: Mutator | None = None, status: dict[str, int] | None = None
) -> Callable[[httpx.Request], httpx.Response]:
    status = status or {}

    def handler(request: httpx.Request) -> httpx.Response:
        path = request.url.path
        if path in status:
            return httpx.Response(status[path])
        if path == "/robots.txt":
            return httpx.Response(200, text=ROBOTS_SHOPIFY)
        if path == "/products.json":
            body = (
                (SHOP / "products_page1.json").read_text()
                if request.url.params["page"] == "1"
                else '{"products": []}'
            )
            ctype = "application/json; charset=utf-8"
        elif path.endswith(".js"):
            body = (SHOP / f"{path.removeprefix('/products/')}").read_text()
            ctype = "text/javascript; charset=utf-8"
        elif path.startswith("/products/"):
            body = (SHOP / f"{path.removeprefix('/products/')}.html").read_text()
            ctype = "text/html; charset=utf-8"
        else:
            return httpx.Response(404)
        if mutate:
            body = mutate(path, body)
        return httpx.Response(200, content=body.encode(), headers={"content-type": ctype})

    return handler


def run(
    handler: Callable[[httpx.Request], httpx.Response],
) -> tuple[StoreFetch, list[httpx.Request]]:
    session, _, seen = session_for(
        handler, base_url=STORE.base_url, config=PoliteConfig(delay_s=1, jitter_s=0)
    )
    return asyncio.run(fetch_store(session, STORE, DAY)), seen


def test_full_fetch_with_witnesses() -> None:
    out, seen = run(shop())
    assert out.status == "ok", out.reason
    assert len(out.products) == 3
    assert out.pages == 1  # page 1 had fewer than 250 products
    assert len(out.witnesses) == SAMPLE_PER_STORE
    assert all(w.js == "match" and w.jsonld == "match" for w in out.witnesses)
    assert out.currencies == {"USD"}
    assert all(r.url.params.get("country") == "US" for r in seen if r.url.path != "/robots.txt")
    # Descriptions and images never survive the fetch.
    dumped = json.dumps(out.products)
    assert "description" not in dumped
    assert "cdn.shopify.com" not in dumped
    assert "must never be stored" not in json.dumps(out.report())


def test_rows_normalize_from_fixture() -> None:
    out, _ = run(shop())
    rows, stats = normalize_products(STORE.id, out.products, out.observed_at)
    assert stats.rows == 5
    assert stats.compare_at_ignored == 1  # Day Pack Sand: compare_at 100 < price 120
    tee = [r for r in rows if r.handle == "trail-tee"]
    assert [(r.price_cents, r.compare_at_cents, r.availability) for r in tee] == [
        (2800, 3500, "in_stock"),
        (2800, 3500, "out_of_stock"),
    ]


def test_js_price_mismatch_marks_store() -> None:
    def mutate(path: str, body: str) -> str:
        if path.endswith(".js"):
            data: dict[str, Any] = json.loads(body)
            for v in data["variants"]:
                v["price"] += 100
            return json.dumps(data)
        return body

    out, _ = run(shop(mutate))
    assert out.status == "mismatch"
    assert out.reason is not None
    assert ".js mismatch" in out.reason


def test_jsonld_price_difference_alone_is_recorded_not_blocking() -> None:
    def mutate(path: str, body: str) -> str:
        if path.startswith("/products/") and not path.endswith(".js"):
            return body.replace('"price": "', '"price": "1')
        return body

    out, _ = run(shop(mutate))
    assert out.status == "ok"  # products.json and .js agree (D-019)
    assert out.jsonld_disagrees
    assert "JSON-LD" in out.jsonld_disagrees[0]


def test_non_usd_currency_is_reported() -> None:
    def mutate(path: str, body: str) -> str:
        return body.replace("USD", "CAD") if path.startswith("/products/") else body

    out, _ = run(shop(mutate))
    assert out.status == "ok"
    assert out.currencies == {"CAD"}


def test_missing_currency_proof_fails_store() -> None:
    def mutate(path: str, body: str) -> str:
        if path.startswith("/products/") and not path.endswith(".js"):
            return "<html><body>no structured data</body></html>"
        return body

    out, _ = run(shop(mutate))
    assert out.status == "failed"
    assert out.reason == "no currency proof on sampled product pages"


def test_catalog_error_fails_store_and_keeps_no_rows() -> None:
    out, _ = run(shop(status={"/products.json": 404}))
    assert out.status == "failed"
    assert out.products == []


def test_excluded_category_stops_store() -> None:
    def mutate(path: str, body: str) -> str:
        return body.replace("Camp Mug", "Hemp CBD Tincture") if path == "/products.json" else body

    out, seen = run(shop(mutate))
    assert out.status == "excluded"
    assert out.content_flags == {"cannabis/cbd": ["Hemp CBD Tincture"]}
    assert not any(r.url.path.endswith(".js") for r in seen)  # no witness requests


def test_sample_rotates_by_day_and_is_stable() -> None:
    products = [{"id": i, "handle": f"p{i}", "variants": [{"id": i}]} for i in range(1, 50)]
    a = [p["id"] for p in sample_products(products, "s", date(2026, 11, 4))]
    b = [p["id"] for p in sample_products(products, "s", date(2026, 11, 4))]
    c = [p["id"] for p in sample_products(products, "s", date(2026, 11, 5))]
    assert a == b
    assert a != c
