"""Content screen: keep adult, tobacco/vape, alcohol, cannabis/CBD and weapons stores out.

Runs over the catalog fields recon already has in memory and returns, per excluded
category, up to three matching product titles as evidence. One real match is
enough to flag a store. Screen v2 (D-039) counts a match only when the product
*is* the excluded thing, not when the word names a colour, a scent, a slogan or an
object around it:

* Fields: the product ``title`` and ``product_type``. Tags are read for
  cannabis/CBD only: elsewhere they hold colour filters ("Tobacco" for brown suede)
  and flagged stores that sell none of it, while a CBD seller may name CBD only in
  a tag ("Hemp Calming Chews" tagged "CBD").
* Negations never count: "CBD-free", "non-alcoholic", "Non-CBD".
* Colourway: a word only in the short variant part of a title ("Pouch -
  Wine/Gold", "Dunes | Tobacco", "Leather in Tobacco") does not count, unless that
  part names a quantity such as "750 ml" or "40%".
* Merch: a tee, hat, sticker, toy and the like carrying the word does not count.
* Objects: a coaster, glass, candle, charger, socket, coffee, boot and the like
  does not count for alcohol, tobacco and weapons words.

Adult phrases always count. Cannabis/CBD words and the strict words (nicotine,
e-liquid, vape, vaping) count on any object ("CBD Lotion" is a CBD product); only
merch and negations exempt them. The object or merch noun must sit outside the
matched phrase ("Pepper Spray" is not exempted by "spray").
"""

from __future__ import annotations

import re
from collections.abc import Iterable
from dataclasses import dataclass
from typing import Any

# Bump when the rule changes: a later recon row with a newer screen supersedes the
# content flags of earlier rows (sources.StoreRecord.drop_reasons).
SCREEN_VERSION = 2

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

# Words that name the product itself whatever object they sit on.
STRICT_WORDS = frozenset({"nicotine", "e-liquid", "vape", "vaping"})
# Categories whose words an object noun can exempt (cannabis/CBD and adult: never).
OBJECT_CATEGORIES = frozenset({"alcohol", "tobacco/vape", "weapons"})

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

_ALL_WORDS = sorted({w for words in EXCLUDED.values() for w in words}, key=len, reverse=True)
_NEGATION = re.compile(
    r"\b(?:non[- ]?(?:" + "|".join(re.escape(w) for w in _ALL_WORDS) + r"|alcoholic)"
    r"|(?:" + "|".join(re.escape(w) for w in _ALL_WORDS) + r"|alcohol)[- ]free)\b",
    re.IGNORECASE,
)

# Wearables, prints and novelties that carry a word as a slogan or a licence.
MERCH = (
    "tee",
    "t-shirt",
    "shirt",
    "tank",
    "hoodie",
    "sweatshirt",
    "crewneck",
    "sweater",
    "hat",
    "cap",
    "snapback",
    "beanie",
    "sticker",
    "patch",
    "pin",
    "poster",
    "print",
    "toy",
    "plush",
)
# Things that are not the drink, the smoke or the weapon (alcohol, tobacco, weapons).
OBJECTS = (
    "coaster",
    "glass",
    "glasses",
    "glassware",
    "stemware",
    "drinkware",
    "tumbler",
    "flask",
    "carafe",
    "decanter",
    "stopper",
    "opener",
    "koozie",
    "cup",
    "mug",
    "stein",
    "tote",
    "bag",
    "pouch",
    "basket",
    "table",
    "rack",
    "napkin",
    "candle",
    "diffuser",
    "freshener",
    "spray",
    "musk",
    "scent",
    "fragrance",
    "cologne",
    "perfume",
    "parfum",
    "soap",
    "lotion",
    "balm",
    "conditioner",
    "toner",
    "blush",
    "gloss",
    "polish",
    "vinegar",
    "chocolate",
    "coffee",
    "tea",
    "charger",
    "socket",
    "splitter",
    "adapter",
    "plug",
    "cable",
    "keyboard",
    "switch",
    "case",
    "strap",
    "cage",
    "goggle",
    "boot",
    "shoe",
    "sandal",
    "sneaker",
    "footwear",
    "pant",
    "jacket",
    "leather",
    "suede",
    "bowl",
    "phone",
)


def _noun_pattern(nouns: Iterable[str]) -> re.Pattern[str]:
    body = "|".join(re.escape(n) for n in sorted(nouns, key=len, reverse=True))
    return re.compile(r"\b(?:" + body + r")(?:e?s)?\b", re.IGNORECASE)


_MERCH = _noun_pattern(MERCH)
_OBJECTS = _noun_pattern(OBJECTS)
_PATTERNS = {
    # Plurals too: "Premium Cigars", "Rifles".
    cat: re.compile(r"\b(" + "|".join(re.escape(w) for w in words) + r")s?\b", re.IGNORECASE)
    for cat, words in EXCLUDED.items()
}
# The variant part of a title: after the last " - ", " | ", "{" or " in ".
_VARIANT_SPLIT = re.compile(r"\s[-\u2013\u2014|]\s|\{|\s+in\s+", re.IGNORECASE)
_QUANTITY = re.compile(r"\d\s*(?:ml|cl|l|oz|%|proof)\b|\babv\b", re.IGNORECASE)


@dataclass(frozen=True)
class Match:
    category: str
    title: str
    field: str
    word: str

    def evidence(self) -> str:
        return f"{self.field}: {self.word}"


def _clean(text: str) -> str:
    lowered = text.lower()
    for phrase in ALLOWED_PHRASES:
        lowered = lowered.replace(phrase, " ")
    return _NEGATION.sub(" ", lowered)


def _split_variant(title: str) -> tuple[str, str]:
    """(head, variant): the variant is the short tail after the last separator."""
    cuts = list(_VARIANT_SPLIT.finditer(title))
    if not cuts:
        return title, ""
    tail = title[cuts[-1].end() :]
    if len(tail.split()) > 4 or _QUANTITY.search(tail):
        return title, ""
    return title[: cuts[-1].start()], tail


def _counts(cat: str, word: str, field: str, title: str, around: str) -> bool:
    """Whether one match of ``word`` names the excluded product."""
    if cat == "adult":
        return True
    # Merch and objects are looked for outside the matched phrase.
    others = around.replace(word, " ")
    if _MERCH.search(others):
        return False
    strict = cat == "cannabis/cbd" or word in STRICT_WORDS
    if strict or cat not in OBJECT_CATEGORIES:
        return True
    if _OBJECTS.search(others):
        return False
    if field == "title":
        head, variant = _split_variant(title)
        pattern = _PATTERNS[cat]
        if variant and pattern.search(_clean(variant)) and not pattern.search(_clean(head)):
            return False
    return True


def screen_matches(
    products: list[dict[str, Any]],
    reviewed_titles: frozenset[str] = frozenset(),
) -> list[Match]:
    """Every product match that counts, in catalog order (one per product and category)."""
    out: list[Match] = []
    for product in products:
        title = str(product.get("title") or "")
        if title in reviewed_titles:
            continue
        fields = {
            "title": _clean(title),
            "product_type": _clean(str(product.get("product_type") or "")),
        }
        around = " | ".join(fields.values())
        tags = product.get("tags")
        tag_text = _clean(" | ".join(tags) if isinstance(tags, list) else str(tags or ""))
        for cat, pattern in _PATTERNS.items():
            # Tags count for cannabis/CBD only: a CBD seller may say "Hemp" in the
            # title and "CBD" in a tag; colour filters never name cannabis.
            read = {**fields, "tags": tag_text} if cat == "cannabis/cbd" else fields
            for field, text in read.items():
                hit = next(
                    (
                        m.group(1)
                        for m in pattern.finditer(text)
                        if _counts(cat, m.group(1), field, title, around)
                    ),
                    None,
                )
                if hit is not None:
                    out.append(Match(cat, title[:80] or "?", field, hit))
                    break
    return out


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
    for match in screen_matches(products, reviewed_titles):
        examples = found.setdefault(match.category, [])
        if len(examples) < max_examples:
            examples.append(match.title)
    return found


def screen_evidence(
    products: list[dict[str, Any]],
    max_examples: int = 3,
    reviewed_titles: frozenset[str] = frozenset(),
) -> dict[str, list[str]]:
    """Which field and word fired for each example in ``screen_content``, same order."""
    found: dict[str, list[str]] = {}
    for match in screen_matches(products, reviewed_titles):
        examples = found.setdefault(match.category, [])
        if len(examples) < max_examples:
            examples.append(match.evidence())
    return found
