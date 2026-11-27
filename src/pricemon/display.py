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


def alias_id(public_no: int) -> str:
    """The public id of a store shown without its name: ``store-017``."""
    return f"store-{public_no:03d}"


@dataclass
class Display:
    """Names, ids and links of stores on public surfaces and in public data files.

    Every public data file (snapshot, change log, Parquet history, run log) keys an
    anonymised store by its alias id (``store-017``), never by its config id, with an
    empty handle and its name taken out of product titles (D-034). ``data_id`` gives
    that key; every lookup here accepts either id.
    """

    stores: list[Store]
    retired: list[RetiredStore] = field(default_factory=list)
    anonymise: tuple[str, ...] = DEFAULT_ANONYMISE

    def __post_init__(self) -> None:
        self._by_id = {s.id: s for s in self.stores}
        self._retired = {r.id: r for r in self.retired}
        self._alias: dict[str, str] = {}
        self._data_id: dict[str, str] = {}
        self._scrub: dict[str, re.Pattern[str]] = {}
        for s in self.stores:
            if s.terms not in self.anonymise:
                self._data_id[s.id] = s.id
                continue
            if s.public_no is None:
                raise ValueError(
                    f"store {s.id} is shown without its name but has no public_no "
                    "(regenerate config/stores.yml, D-034)"
                )
            self._alias[s.id] = f"Store #{s.public_no} ({category_title(s.category)})"
            self._data_id[s.id] = alias_id(s.public_no)
            words = {s.name, s.host.removeprefix("www.").split(".")[0], s.id}
            words = {w for w in words if len(w) >= 3}
            alt = "|".join(re.escape(w) for w in sorted(words, key=len, reverse=True))
            self._scrub[s.id] = re.compile(rf"(?i)\b(?:{alt})\b")
        self._from_data = {v: k for k, v in self._data_id.items()}

    def _raw(self, store_id: str) -> str:
        """The config id for a config id or an alias id."""
        return self._from_data.get(store_id, store_id)

    @property
    def anonymised_ids(self) -> set[str]:
        return set(self._alias)

    def is_anonymised(self, store_id: str) -> bool:
        return self._raw(store_id) in self._alias

    def data_id(self, store_id: str) -> str:
        """The store's key in public data files (its alias id when anonymised)."""
        return self._data_id.get(self._raw(store_id), store_id)

    def rekey(self) -> dict[str, str]:
        """Old key -> new key for every monitored store whose data key differs from
        one of its ids (a store that became anonymised, or stopped being)."""
        out: dict[str, str] = {}
        for s in self.stores:
            target = self._data_id[s.id]
            if s.id != target:
                out[s.id] = target
            elif s.public_no is not None and alias_id(s.public_no) != target:
                out[alias_id(s.public_no)] = target
        return out

    def store(self, store_id: str) -> Store | None:
        return self._by_id.get(self._raw(store_id))

    def retired_store(self, store_id: str) -> RetiredStore | None:
        return self._retired.get(store_id)

    def name(self, store_id: str) -> str:
        raw = self._raw(store_id)
        if raw in self._alias:
            return self._alias[raw]
        if raw in self._by_id:
            return self._by_id[raw].name
        if raw in self._retired:
            return self._retired[raw].name
        return store_id

    def host(self, store_id: str) -> str:
        """The store's host, or "" when it must not be shown (anonymised, retired, unknown)."""
        raw = self._raw(store_id)
        s = self._by_id.get(raw)
        return "" if s is None or raw in self._alias else s.host

    def store_url(self, store_id: str) -> str:
        host = self.host(store_id)
        return f"https://{host}" if host else ""

    def product_url(self, store_id: str, handle: str) -> str:
        host = self.host(store_id)
        return f"https://{host}/products/{handle}" if host and handle else ""

    def title(self, store_id: str, title: str) -> str:
        """A product title, with an anonymised store's own name taken out."""
        pattern = self._scrub.get(self._raw(store_id))
        if pattern is None:
            return title
        cleaned = re.sub(r"\s{2,}", " ", pattern.sub("", title)).strip(" -\u2013|:")
        return cleaned or "Product"


def load_display(stores_path: Path, public_path: Path | None = None) -> Display:
    stores = load_stores(stores_path) if stores_path.exists() else []
    return Display(stores, load_retired(stores_path), anonymise_setting(public_path))
