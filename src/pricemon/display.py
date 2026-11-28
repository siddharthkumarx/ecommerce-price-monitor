"""How a store is named and linked on public surfaces (README, dashboard, feed, media).

Every listed store is shown by name: no store whose terms ban robots is ever listed
(``stores.load_stores`` refuses one, D-042), so there is nothing to hide (D-046).
Retired stores are labelled "retired on <date>"; one retired because its Terms ban
robots carries a number for a name ("Store #17") and its data was keyed by that
number once, when it was retired (``pricemon.retire``, D-044).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from pricemon.stores import RetiredStore, Store, load_retired, load_stores


@dataclass
class Display:
    """Names and links of the listed and retired stores."""

    stores: list[Store]
    retired: list[RetiredStore] = field(default_factory=list)

    def __post_init__(self) -> None:
        self._by_id = {s.id: s for s in self.stores}
        self._retired = {r.id: r for r in self.retired}

    @property
    def public_ids(self) -> set[str]:
        """The keys public data may hold: listed stores and retired stores."""
        return set(self._by_id) | set(self._retired)

    def store(self, store_id: str) -> Store | None:
        return self._by_id.get(store_id)

    def retired_store(self, store_id: str) -> RetiredStore | None:
        return self._retired.get(store_id)

    def name(self, store_id: str) -> str:
        if store_id in self._by_id:
            return self._by_id[store_id].name
        if store_id in self._retired:
            return self._retired[store_id].name
        return store_id

    def host(self, store_id: str) -> str:
        """The store's host, or "" for a store that is not listed (retired, unknown)."""
        s = self._by_id.get(store_id)
        return s.host if s else ""

    def store_url(self, store_id: str) -> str:
        host = self.host(store_id)
        return f"https://{host}" if host else ""

    def product_url(self, store_id: str, handle: str) -> str:
        host = self.host(store_id)
        return f"https://{host}/products/{handle}" if host and handle else ""


def load_display(stores_path: Path) -> Display:
    stores = load_stores(stores_path) if stores_path.exists() else []
    return Display(stores, load_retired(stores_path))
