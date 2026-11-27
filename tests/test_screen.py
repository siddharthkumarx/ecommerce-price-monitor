from __future__ import annotations

from typing import Any

import pytest

from pricemon.screen import screen_content, screen_evidence


def _p(title: str, product_type: str = "", tags: Any = None) -> dict[str, Any]:
    return {"title": title, "product_type": product_type, "tags": tags or []}


def test_flags_excluded_categories_with_examples() -> None:
    products = [
        _p("CBD Body Balm", "Skincare", ["calm"]),
        _p("Mini Vape Pen", "Device"),
        _p("Cooling Gel", "Skincare", "hemp extract, calm"),  # tags are not read (D-039)
    ]
    assert screen_content(products) == {
        "cannabis/cbd": ["CBD Body Balm"],
        "tobacco/vape": ["Mini Vape Pen"],
    }
    assert screen_evidence(products) == {
        "cannabis/cbd": ["title: cbd"],
        "tobacco/vape": ["title: vape"],
    }


def test_harmless_phrases_and_partial_words_do_not_flag() -> None:
    products = [
        _p("Stemless Wine Glass Set", "Glassware"),
        _p("Ginger Lip Balm", "Lip", ["rumpled"]),
        _p("Rumpl Original Puffy Blanket", "Blanket"),
        _p("Chef Knife 8 inch", "Cutlery", ["kitchen"]),
    ]
    assert screen_content(products) == {}


def test_reviewed_titles_are_skipped_exactly() -> None:
    products = [
        _p("6mm Output Female Cigarette Adapter", "Cable"),
        _p("Cigarette Rolling Papers", "Smoking"),
    ]
    flags = screen_content(
        products, reviewed_titles=frozenset({"6mm Output Female Cigarette Adapter"})
    )
    assert flags == {"tobacco/vape": ["Cigarette Rolling Papers"]}


# Real titles that excluded safe-Terms stores under screen v1 (recon-005, recon-006).
# The tags these stores use (colour filters, "CBD-free") would have flagged them too.
FALSE_POSITIVES = [
    ("Bandolier", _p("Avery AirPods Clip-On Pouch - Wine/Gold", "", ["Wine", "Gold"])),
    ("Bandolier", _p("Donna Crossbody Phone Case - Wine/Gold")),
    ("OluKai", _p("Hiapo - Rum / Dark Wood", "", ["color_Rum"])),
    ("Kassatex", _p("Juliska Graham Wine Coaster")),
    ("P.L.A.Y.", _p("Clive & Bacon x Play Barking Beer", "Dog Toys")),
    ("Sabrent", _p("2 USB Plug And 2 Cigarette Lighter Socket Splitter")),
    ("Derma E", _p("Ultra Hydrating Day Cream (2oz)", "Moisturizer", ["CBD-free", "THC"])),
    ("Derma E", _p("Ultra Lift Firming DMAE Moisturizer", "Moisturizer", ["cbd"])),
    ("Scotch Porter", _p("Leave-In Beard Conditioner 6-Pack", "Beard", ["Bay Rum"])),
    ("Scotch Porter", _p("Intense Anti-Dry Body Lotion | Sandalwood & Tobacco Musk")),
    ("Kiel James Patrick", _p("Goslings x KJP Black Seal Rum T-Shirt in Grey")),
    ("Kiel James Patrick", _p("Goslings x KJP Black Seal Rum Hat in Red")),
    ("Bear KompleX", _p("No Weak Shit American Flag Rifle Patch Original Ripstop Snapback Hat")),
    ("Bear KompleX", _p("Beer Launcher Party TactiDuck PVC Patch")),
    ("Jeffree Star Cosmetics", _p("Hi, How Are Ya? THC Black Tee")),
    ("FrictionLabs", _p("Climbskin Silicium Gel (Non-CBD)")),
    ("Koio", _p("Monza Leather in Tobacco")),
    ("Hari Mari", _p("Men's Dunes | Tobacco")),
    ("Case-Mate", _p("Pelican Voyager Black with Holster and Magnet - Pixel 11 Pro", "Phone Case")),
    ("Onyx Coffee Lab", _p("Colombia Juan Jimenez Pink Bourbon", "Coffee")),
    ("Paddywax", _p("Tobacco Vanilla - Lustre Candle 10 oz")),
    ("KINTO USA", _p("CAST double wall beer glass 340ml")),
]


@pytest.mark.parametrize(("store", "product"), FALSE_POSITIVES)
def test_words_in_colours_scents_merch_and_objects_do_not_flag(
    store: str, product: dict[str, Any]
) -> None:
    assert screen_content([product]) == {}, store


TRUE_POSITIVES = [
    ("alcohol", _p("Cabernet Sauvignon 2019", "Wine")),
    ("alcohol", _p("Kentucky Straight Bourbon Whiskey 750ml", "Spirits")),
    ("alcohol", _p("Josh Cellars - Rose Wine 750 ml")),  # a quantity: not a colourway
    ("alcohol", _p("London Dry Gin")),
    ("alcohol", _p("Hazy IPA Beer 6-Pack")),
    ("tobacco/vape", _p("Disposable Vape Pen 5000 Puffs", "Vape")),
    ("tobacco/vape", _p("Mango Ice - Disposable Vape")),  # strict words count anywhere
    ("tobacco/vape", _p("Nicotine Pouches Mint 6mg", "Pouch")),
    ("tobacco/vape", _p("Premium Cigars Sampler")),
    ("tobacco/vape", _p("Pipe Tobacco 50g")),
    ("tobacco/vape", _p("Strawberry E-Liquid 60ml")),
    ("cannabis/cbd", _p("Full Spectrum CBD Oil 1000mg", "Tincture")),
    ("cannabis/cbd", _p("CBD Body Lotion", "Lotion")),  # an object does not excuse CBD
    ("cannabis/cbd", _p("Delta 8 THC Gummies")),
    ("weapons", _p("AR-15 Rifle")),
    ("weapons", _p("Concealed Carry Holster")),
    ("weapons", _p("Pepper Spray Keychain")),  # "spray" is part of the phrase
    ("weapons", _p("12 Gauge Pump Shotgun")),
    ("adult", _p("Personal Massager Vibrator")),
    ("adult", _p("Couples Sex Toy Kit", "Toy")),  # merch never excuses adult phrases
]


@pytest.mark.parametrize(("category", "product"), TRUE_POSITIVES)
def test_real_excluded_products_still_flag(category: str, product: dict[str, Any]) -> None:
    assert category in screen_content([product])


def test_one_real_product_flags_a_store_with_false_positives_around_it() -> None:
    products = [
        _p("Juliska Graham Wine Coaster"),
        _p("Hiapo - Rum / Dark Wood"),
        _p("Reserve Pinot Noir", "Wine"),
    ]
    assert screen_content(products) == {"alcohol": ["Reserve Pinot Noir"]}
    assert screen_evidence(products) == {"alcohol": ["product_type: wine"]}
