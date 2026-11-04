from __future__ import annotations

from datetime import UTC, datetime, timedelta, timezone

import pytest
from pydantic import ValidationError

from pricemon.guard import PrevVersion, accept_repeat, check_batch
from pricemon.models import VariantRow
from pricemon.normalize import normalize_products, slim_product

T0 = datetime(2026, 11, 4, 6, 17, tzinfo=UTC)


def _row(variant_id: int, price: int, store: str = "s", **kw: object) -> VariantRow:
    data: dict[str, object] = {
        "store_id": store,
        "product_id": 1,
        "variant_id": variant_id,
        "handle": "tee",
        "product_title": "Tee",
        "variant_title": "S",
        "price_cents": price,
        "compare_at_cents": None,
        "availability": "in_stock",
        "observed_at": T0,
    }
    data.update(kw)
    return VariantRow.model_validate(data)


# -- model ----------------------------------------------------------------------
def test_model_rules() -> None:
    assert _row(1, 2800, compare_at_cents=3500).discounted
    assert not _row(1, 2800, compare_at_cents=2800).discounted
    with pytest.raises(ValidationError, match="compare_at_cents must be >= price_cents"):
        _row(1, 2800, compare_at_cents=2000)
    with pytest.raises(ValidationError):
        _row(1, 0)
    with pytest.raises(ValidationError):
        _row(1, 2800, availability="preorder")
    with pytest.raises(ValidationError, match="UTC"):
        _row(1, 2800, observed_at=T0.astimezone(timezone(timedelta(hours=-5))))
    with pytest.raises(ValidationError):
        _row(1, 2800, observed_at=datetime(2026, 11, 4, 6, 17))  # naive
    with pytest.raises(ValidationError):
        _row(1, 28.00)  # type: ignore[arg-type]  # strict: no floats


# -- normalize --------------------------------------------------------------------
def test_slim_product_drops_descriptions_and_images() -> None:
    raw = {
        "id": 1,
        "handle": "tee",
        "title": "Tee",
        "body_html": "<p>long description</p>",
        "images": [{"src": "https://cdn.example/x.jpg"}],
        "product_type": "Shirt",
        "tags": ["cotton"],
        "variants": [{"id": 9, "title": "S", "price": "28.00", "featured_image": {"src": "x"}}],
    }
    slim = slim_product(raw)
    assert "body_html" not in slim
    assert "images" not in slim
    assert "featured_image" not in slim["variants"][0]


def test_normalize_cents_compare_at_and_rejects() -> None:
    products = [
        {
            "id": 1,
            "handle": "tee",
            "title": " Tee ",
            "variants": [
                {
                    "id": 11,
                    "title": "S",
                    "price": "28.00",
                    "compare_at_price": "35.00",
                    "available": True,
                },
                {
                    "id": 12,
                    "title": "M",
                    "price": "28.00",
                    "compare_at_price": "20.00",
                    "available": False,
                },
                {
                    "id": 13,
                    "title": "L",
                    "price": "0.00",
                    "compare_at_price": None,
                    "available": True,
                },
                {
                    "id": 14,
                    "title": "XL",
                    "price": "28.00",
                    "compare_at_price": "",
                    "available": None,
                },
                {
                    "id": 11,
                    "title": "dup",
                    "price": "28.00",
                    "compare_at_price": None,
                    "available": True,
                },
            ],
        }
    ]
    rows, stats = normalize_products("s", products, T0)
    assert [(r.variant_id, r.price_cents, r.compare_at_cents, r.availability) for r in rows] == [
        (11, 2800, 3500, "in_stock"),
        (12, 2800, None, "out_of_stock"),
    ]
    assert rows[0].product_title == "Tee"
    assert stats.compare_at_ignored == 1
    assert stats.free == 1  # the $0.00 variant: out of scope, not an error
    assert stats.rejected == 2
    assert any("duplicate" in e for e in stats.examples)


# -- guard ------------------------------------------------------------------------
def _prev(prices: dict[int, int]) -> dict[int, PrevVersion]:
    return {vid: PrevVersion(price_cents=p) for vid, p in prices.items()}


def test_black_friday_sale_passes() -> None:
    prev = {"s": _prev(dict.fromkeys(range(1, 101), 5000))}
    cur = {
        "s": [_row(i, 3500, compare_at_cents=5000) for i in range(1, 81)]
        + [_row(i, 5000) for i in range(81, 101)]
    }
    result = check_batch(cur, prev, {}, {})
    assert not result.held
    assert result.price_changed == 80


def test_unit_error_holds() -> None:
    prev = {"s": _prev(dict.fromkeys(range(1, 251), 5000))}
    cur = {"s": [_row(i, 50) for i in range(1, 251)]}  # dollars read as cents
    result = check_batch(cur, prev, {}, {})
    assert "suspicious:s" in result.keys
    assert "suspicious:run" in result.keys
    assert "mass_change:run" in result.keys


def test_sitewide_sale_with_compare_at_is_not_a_mass_change() -> None:
    prev = {"s": _prev(dict.fromkeys(range(1, 251), 5000))}
    cur = {"s": [_row(i, 3000, compare_at_cents=5000) for i in range(1, 251)]}
    result = check_batch(cur, prev, {}, {})
    assert result.price_changed == 250
    assert result.unexplained == 0
    assert not result.held


def test_run_wide_shares_need_a_minimum_sample() -> None:
    prev = {"s": _prev(dict.fromkeys(range(1, 6), 5000))}
    cur = {"s": [_row(i, 4000) for i in range(1, 6)]}
    assert check_batch(cur, prev, {}, {}).keys == []


def test_row_drop_currency_and_rejects_hold() -> None:
    prev = {"a": _prev(dict.fromkeys(range(1, 41), 1000)), "b": _prev({1: 1000})}
    cur = {"a": [_row(i, 1000, store="a") for i in range(1, 11)], "b": [_row(1, 1000, store="b")]}
    result = check_batch(cur, prev, {"b": 1}, {"b": ["CAD"]})
    assert result.keys == ["currency:b", "rejects:b", "rows_drop:a", "rows_drop:run"]


def test_small_store_drop_is_not_a_hold() -> None:
    prev = {"s": _prev(dict.fromkeys(range(1, 11), 1000))}
    cur = {"s": [_row(1, 1000)]}
    keys = check_batch(cur, prev, {}, {}).keys
    assert "rows_drop:s" not in keys


def test_repeat_acceptance() -> None:
    assert accept_repeat(["rows_drop:a"], "held", ["rows_drop:a", "currency:b"])
    assert not accept_repeat(["rows_drop:a"], "ok", [])
    assert not accept_repeat(["rows_drop:a", "rows_drop:c"], "held", ["rows_drop:a"])
    assert not accept_repeat([], "held", ["rows_drop:a"])
