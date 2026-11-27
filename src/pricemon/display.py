"""How a store is named on public surfaces (README, dashboard, feed, media).

One setting, ``anonymise_terms`` in ``config/public.yml`` (D-031): a monitored store
whose recon ``terms`` value is listed there is shown as ``Store #<n> (<category>)``,
without its name, host or product links, and with its name taken out of product
titles. Its numbers still count in every total. ``n`` follows the order of
``config/stores.yml`` among the anonymised stores. Retired stores keep their name
and are labelled "retired on <date>".
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

import yaml

from pricemon.stores import RetiredStore, Store, category_title, load_retired, load_stores

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_ANONYMISE = ("ban",)


def anonymise_setting(public_path: Path | None = None) -> tuple[str, ...]:
    path = public_path or ROOT / "config" / "public.yml"
    if not path.exists():
        return DEFAULT_ANONYMISE
    raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    value = raw.get("anonymise_terms", list(DEFAULT_ANONYMISE))
    return tuple(str(v) for v in value or ())


@dataclass
class Display:
    stores: list[Store]
    retired: list[RetiredStore] = field(default_factory=list)
    anonymise: tuple[str, ...] = DEFAULT_ANONYMISE

    def __post_init__(self) -> None:
        self._by_id = {s.id: s for s in self.stores}
        self._retired = {r.id: r for r in self.retired}
        self._alias: dict[str, str] = {}
        hidden = [s for s in self.stores if s.terms in self.anonymise]
        for n, s in enumerate(hidden, start=1):
            self._alias[s.id] = f"Store #{n} ({category_title(s.category)})"
        self._scrub: dict[str, re.Pattern[str]] = {}
        for s in hidden:
            words = {s.name, s.host.removeprefix("www.").split(".")[0]}
            words = {w for w in words if len(w) >= 3}
            alt = "|".join(re.escape(w) for w in sorted(words, key=len, reverse=True))
            self._scrub[s.id] = re.compile(rf"(?i)\b(?:{alt})\b")

    @property
    def anonymised_ids(self) -> set[str]:
        return set(self._alias)

    def is_anonymised(self, store_id: str) -> bool:
        return store_id in self._alias

    def retired_store(self, store_id: str) -> RetiredStore | None:
        return self._retired.get(store_id)

    def name(self, store_id: str) -> str:
        if store_id in self._alias:
            return self._alias[store_id]
        if store_id in self._by_id:
            return self._by_id[store_id].name
        if store_id in self._retired:
            return self._retired[store_id].name
        return store_id

    def host(self, store_id: str) -> str:
        """The store's host, or "" when it must not be shown (anonymised, retired, unknown)."""
        s = self._by_id.get(store_id)
        return "" if s is None or store_id in self._alias else s.host

    def store_url(self, store_id: str) -> str:
        host = self.host(store_id)
        return f"https://{host}" if host else ""

    def product_url(self, store_id: str, handle: str) -> str:
        host = self.host(store_id)
        return f"https://{host}/products/{handle}" if host and handle else ""

    def title(self, store_id: str, title: str) -> str:
        """A product title, with an anonymised store's own name taken out."""
        pattern = self._scrub.get(store_id)
        if pattern is None:
            return title
        cleaned = re.sub(r"\s{2,}", " ", pattern.sub("", title)).strip(" -\u2013|:")
        return cleaned or "Product"


def load_display(stores_path: Path, public_path: Path | None = None) -> Display:
    stores = load_stores(stores_path) if stores_path.exists() else []
    return Display(stores, load_retired(stores_path), anonymise_setting(public_path))
