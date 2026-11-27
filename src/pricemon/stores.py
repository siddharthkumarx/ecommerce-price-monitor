"""The monitored store list (config/stores.yml, generated from recon evidence).

``stores`` are the stores every run reads. ``retired`` are stores that left the
list on purpose (``config/retired.yml``, copied into stores.yml by
``python -m pricemon.sources --stores-yml``): no run reads them any more, their
history stays in ``data/`` as written, and every public surface shows them as
"retired on <date>", never as sold out or removed.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any

import yaml

# Display titles of the category ids, in display order.
CATEGORY_TITLES = {
    "audio": "Audio",
    "apparel": "Apparel",
    "beauty": "Beauty",
    "home_kitchen": "Home & kitchen",
    "outdoor": "Outdoor",
    "coffee_tea": "Coffee & tea",
    "fitness": "Fitness",
    "pet": "Pet",
    "tech_accessories": "Tech accessories",
    "toys_kids": "Toys & kids",
}
# Terms of Service field from recon (pricemon.terms).
TERMS_VALUES = ("ban", "no_ban", "none_found")


def category_title(category: str) -> str:
    return CATEGORY_TITLES.get(category, category.replace("_", " ").capitalize())


@dataclass(frozen=True)
class Store:
    id: str
    name: str
    category: str
    host: str
    screen_reviewed: frozenset[str] = frozenset()
    terms: str = "none_found"

    @property
    def base_url(self) -> str:
        return f"https://{self.host}"


@dataclass(frozen=True)
class RetiredStore:
    id: str
    name: str
    category: str
    retired_on: date

    @property
    def label(self) -> str:
        return f"retired on {self.retired_on.day} {self.retired_on:%b %Y}"


def _raw(path: Path) -> dict[str, Any]:
    loaded = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return dict(loaded)


def load_stores(path: Path) -> list[Store]:
    raw = _raw(path)
    stores = [
        Store(
            id=str(s["id"]),
            name=str(s["name"]),
            category=str(s["category"]),
            host=str(s["host"]),
            screen_reviewed=frozenset(str(t) for t in s.get("screen_reviewed") or []),
            terms=str(s.get("terms") or "none_found"),
        )
        for s in raw["stores"]
    ]
    ids = [s.id for s in stores]
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate store ids in stores.yml")
    bad = sorted({s.terms for s in stores} - set(TERMS_VALUES))
    if bad:
        raise ValueError(f"unknown terms values in stores.yml: {bad}")
    retired = {r.id for r in load_retired(path)}
    if retired & set(ids):
        raise ValueError(f"stores both monitored and retired: {sorted(retired & set(ids))}")
    return stores


def load_retired(path: Path) -> list[RetiredStore]:
    """The ``retired`` list of stores.yml (or of config/retired.yml); empty when absent."""
    if not path.exists():
        return []
    out: list[RetiredStore] = []
    for r in _raw(path).get("retired") or []:
        on = r["retired_on"]
        out.append(
            RetiredStore(
                id=str(r["id"]),
                name=str(r["name"]),
                category=str(r["category"]),
                retired_on=on if isinstance(on, date) else date.fromisoformat(str(on)),
            )
        )
    return out
