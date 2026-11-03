from __future__ import annotations

from pathlib import Path

import pytest

from pricemon.witness import (
    is_products_payload,
    jsonld_currencies,
    jsonld_offers,
    price_to_cents,
    shopify_active_currency,
)

FIXTURES = Path(__file__).parent / "fixtures" / "recon"


@pytest.mark.parametrize(
    ("raw", "cents"),
    [("19.99", 1999), ("20", 2000), ("0.10", 10), (1999, 199900), ("19.995", None), ("x", None)],
)
def test_price_to_cents(raw: str | int, cents: int | None) -> None:
    assert price_to_cents(raw) == cents


def test_price_to_cents_rejects_none_and_bool() -> None:
    assert price_to_cents(None) is None
    assert price_to_cents(True) is None


def test_jsonld_from_product_group() -> None:
    html = (FIXTURES / "product_page.html").read_text()
    assert len(jsonld_offers(html)) == 2
    assert jsonld_currencies(html) == {"USD"}
    assert shopify_active_currency(html) == "USD"


def test_no_jsonld() -> None:
    assert jsonld_currencies("<html></html>") == set()
    assert shopify_active_currency("<html></html>") is None


def test_products_payload_shape() -> None:
    assert is_products_payload({"products": []})
    assert not is_products_payload({"product": {}})
    assert not is_products_payload([])
