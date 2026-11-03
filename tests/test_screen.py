from __future__ import annotations

from typing import Any

from pricemon.screen import screen_content


def test_flags_excluded_categories_with_examples() -> None:
    products: list[dict[str, Any]] = [
        {"title": "CBD Body Balm", "product_type": "Skincare", "tags": ["calm"]},
        {"title": "Mini Vape Pen", "product_type": "Device", "tags": []},
        {"title": "Cooling Gel", "product_type": "Skincare", "tags": "hemp extract, calm"},
    ]
    flags = screen_content(products)
    assert flags == {
        "cannabis/cbd": ["CBD Body Balm", "Cooling Gel"],
        "tobacco/vape": ["Mini Vape Pen"],
    }


def test_harmless_phrases_and_partial_words_do_not_flag() -> None:
    products: list[dict[str, Any]] = [
        {"title": "Stemless Wine Glass Set", "product_type": "Glassware", "tags": []},
        {"title": "Ginger Lip Balm", "product_type": "Lip", "tags": ["rumpled"]},
        {"title": "Rumpl Original Puffy Blanket", "product_type": "Blanket", "tags": []},
        {"title": "Chef Knife 8 inch", "product_type": "Cutlery", "tags": ["kitchen"]},
    ]
    assert screen_content(products) == {}
