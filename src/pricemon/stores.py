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
    # Fixed public number (config/aliases.yml, D-034): assigned once, never reused.
    public_no: int | None = None

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
            public_no=int(s["public_no"]) if s.get("public_no") is not None else None,
        )
        for s in raw["stores"]
    ]
    numbers = [s.public_no for s in stores if s.public_no is not None]
    if len(numbers) != len(set(numbers)):
        raise ValueError("duplicate public_no in stores.yml")
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


ALIASES_PATH = Path("config/aliases.yml")
ALIASES_HEADER = (
    '# Fixed public numbers of the stores (D-034), used for "Store #<n>" and the alias\n'
    "# id store-<nnn> of a store shown without its name. Written by\n"
    "# `python -m pricemon.sources --stores-yml`: a store gets a number the first time it\n"
    "# is listed; a number is never changed, removed or reused, also after a store leaves.\n"
)


def load_aliases(path: Path = ALIASES_PATH) -> dict[str, int]:
    if not path.exists():
        return {}
    raw = _raw(path).get("numbers") or {}
    out = {str(k): int(v) for k, v in raw.items()}
    if len(set(out.values())) != len(out):
        raise ValueError(f"duplicate numbers in {path}")
    return out


def assign_aliases(registry: dict[str, int], store_ids: list[str]) -> dict[str, int]:
    """The registry with a new number for every id that has none; existing ones kept."""
    out = dict(registry)
    nxt = max(out.values(), default=0) + 1
    for sid in store_ids:
        if sid not in out:
            out[sid] = nxt
            nxt += 1
    return out


def dump_aliases(registry: dict[str, int]) -> str:
    lines = [ALIASES_HEADER.rstrip("\n"), "numbers:"]
    lines += [f"  {sid}: {n}" for sid, n in sorted(registry.items(), key=lambda kv: kv[1])]
    return "\n".join(lines) + "\n"
