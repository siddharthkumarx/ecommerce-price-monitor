"""The monitored store list (config/stores.yml, generated from recon evidence)."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml


@dataclass(frozen=True)
class Store:
    id: str
    name: str
    category: str
    host: str
    screen_reviewed: frozenset[str] = frozenset()

    @property
    def base_url(self) -> str:
        return f"https://{self.host}"


def load_stores(path: Path) -> list[Store]:
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    stores = [
        Store(
            id=str(s["id"]),
            name=str(s["name"]),
            category=str(s["category"]),
            host=str(s["host"]),
            screen_reviewed=frozenset(str(t) for t in s.get("screen_reviewed") or []),
        )
        for s in raw["stores"]
    ]
    ids = [s.id for s in stores]
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate store ids in stores.yml")
    return stores
