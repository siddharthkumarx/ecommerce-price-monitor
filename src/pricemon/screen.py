"""Content screen: keep adult, tobacco/vape, alcohol, cannabis/CBD and weapons stores out.

Runs over the catalog fields recon already has in memory (title, product_type,
tags) and returns, per excluded category, up to three matching product titles as
evidence. Matching is on whole words, minus a short allow-list of harmless
phrases ("wine glass"). One match is enough to flag a store.
"""

from __future__ import annotations

import re
from collections.abc import Iterable
from typing import Any

EXCLUDED: dict[str, tuple[str, ...]] = {
    "adult": ("sex toy", "vibrator", "dildo", "adult toy", "erotic"),
    "tobacco/vape": ("vape", "vaping", "e-liquid", "nicotine", "tobacco", "cigar", "cigarette"),
    "alcohol": (
        "wine",
        "beer",
        "whiskey",
        "whisky",
        "bourbon",
        "vodka",
        "tequila",
        "mezcal",
        "gin",
        "rum",
        "liquor",
        "spirits",
        "hard seltzer",
    ),
    "cannabis/cbd": ("cbd", "thc", "cannabis", "hemp extract", "delta-8", "delta 8", "marijuana"),
    "weapons": (
        "firearm",
        "handgun",
        "rifle",
        "shotgun",
        "ammo",
        "ammunition",
        "holster",
        "pepper spray",
        "stun gun",
        "switchblade",
        "brass knuckles",
    ),
}

# Phrases that contain an excluded word but are not excluded products.
ALLOWED_PHRASES: tuple[str, ...] = (
    "wine glass",
    "wine glasses",
    "wine tumbler",
    "wine opener",
    "wine red",
    "rum raisin",
    "gin gingham",
    "beer koozie",
    "spirits up",
)

_PATTERNS = {
    cat: re.compile(r"\b(" + "|".join(re.escape(w) for w in words) + r")\b", re.IGNORECASE)
    for cat, words in EXCLUDED.items()
}


def _texts(product: dict[str, Any]) -> Iterable[str]:
    for key in ("title", "product_type"):
        value = product.get(key)
        if isinstance(value, str):
            yield value
    tags = product.get("tags")
    if isinstance(tags, list):
        yield from (t for t in tags if isinstance(t, str))
    elif isinstance(tags, str):
        yield tags


def _clean(text: str) -> str:
    lowered = text.lower()
    for phrase in ALLOWED_PHRASES:
        lowered = lowered.replace(phrase, " ")
    return lowered


def screen_content(
    products: list[dict[str, Any]],
    max_examples: int = 3,
    reviewed_titles: frozenset[str] = frozenset(),
) -> dict[str, list[str]]:
    """Excluded categories with at least one matching product, with example titles.

    ``reviewed_titles``: exact product titles a person reviewed as false positives
    (config/screen-review.yml); only those exact titles are skipped.
    """
    found: dict[str, list[str]] = {}
    for product in products:
        if product.get("title") in reviewed_titles:
            continue
        text = " | ".join(_clean(t) for t in _texts(product))
        for cat, pattern in _PATTERNS.items():
            if pattern.search(text):
                examples = found.setdefault(cat, [])
                if len(examples) < max_examples:
                    examples.append(str(product.get("title", "?"))[:80])
    return found
