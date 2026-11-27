"""Facts about the latest real run, for the README, the visuals and the dataset card.

Everything here is read from the committed outputs of real runs
(``data/runs.jsonl``, ``data/status.json`` inputs, ``data/latest/snapshot.csv``,
``data/changes/``) and ``config/stores.yml``. Nothing is typed by hand.
"""

from __future__ import annotations

import csv
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from pricemon.display import Display, load_display
from pricemon.outputs import build_status, parse_iso, read_runs
from pricemon.stores import CATEGORY_TITLES, RetiredStore, Store, category_title

ROOT = Path(__file__).resolve().parents[2]
EVENT_WORDS = {
    "price_down": "Price down",
    "price_up": "Price up",
    "discount_start": "Sale started",
    "discount_end": "Sale ended",
    "out_of_stock": "Sold out",
    "back_in_stock": "Back in stock",
    "new": "New product",
    "removed": "Removed",
}
GOOD = ("ok", "partial")


def usd(cents: int | str | None) -> str:
    if cents in (None, ""):
        return ""
    return f"${int(str(cents)) / 100:,.2f}"


@dataclass
class SampleRow:
    store: str
    category: str
    product: str
    variant: str
    price: str
    compare_at: str
    discount_pct: int | None
    in_stock: bool
    url: str
    raw: dict[str, str]


@dataclass
class Change:
    store: str
    product: str
    variant: str
    events: list[str]
    old_price: str
    new_price: str
    pct: float | None
    url: str


@dataclass
class CategoryRow:
    title: str
    count: int
    names: list[str]


@dataclass
class Facts:
    now: datetime
    stores: list[Store]
    status: dict[str, Any]
    run: dict[str, Any] | None
    display: Display = field(default_factory=lambda: Display([]))
    snapshot_rows: int = 0
    categories: dict[str, int] = field(default_factory=dict)
    in_stock_share: float | None = None
    discounted_share: float | None = None
    sample: list[SampleRow] = field(default_factory=list)
    changes: list[Change] = field(default_factory=list)
    change_counts: dict[str, int] = field(default_factory=dict)
    first_run: bool = False
    quality: dict[str, Any] = field(default_factory=dict)

    @property
    def retired(self) -> list[RetiredStore]:
        return self.display.retired

    @property
    def store_table(self) -> list[CategoryRow]:
        """One row per category: the stores as every public surface names them."""
        order = {c: i for i, c in enumerate(CATEGORY_TITLES)}
        cats = sorted({s.category for s in self.stores}, key=lambda c: (order.get(c, 99), c))
        rows = []
        for c in cats:
            members = [s for s in self.stores if s.category == c]
            named = sorted(
                (self.display.name(s.id) for s in members if not self.display.is_anonymised(s.id)),
                key=str.lower,
            )
            hidden = [self.display.name(s.id) for s in members if self.display.is_anonymised(s.id)]
            rows.append(CategoryRow(category_title(c), len(members), named + hidden))
        return rows

    @property
    def anonymised(self) -> int:
        return len(self.display.anonymised_ids)

    @property
    def run_date(self) -> str:
        return parse_iso(self.run["started_at"]).strftime("%-d %B %Y") if self.run else ""

    @property
    def run_time(self) -> str:
        return parse_iso(self.run["started_at"]).strftime("%H:%M UTC") if self.run else ""


def _snapshot(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def _pick_sample(
    rows: list[dict[str, str]], stores: dict[str, Store], display: Display, n: int = 5
) -> list[SampleRow]:
    """Real rows that show what the data looks like: in stock, one per store and
    category, discounted ones first, deterministic."""

    def disc(r: dict[str, str]) -> int:
        if r["compare_at_cents"] and int(r["compare_at_cents"]) > int(r["price_cents"]):
            return round(100 * (1 - int(r["price_cents"]) / int(r["compare_at_cents"])))
        return 0

    # Ordinary sale prices first (10-50 % off, $10 or more): typical, not outliers.
    # Named stores first: the sample shows what the data looks like, with links.
    candidates = sorted(
        (r for r in rows if r["available"] == "true" and display.store(r["store_id"])),
        key=lambda r: (
            display.is_anonymised(r["store_id"]),
            not (10 <= disc(r) <= 50 and int(r["price_cents"]) >= 1000),
            -disc(r),
            r["store_id"],
            r["product_title"],
            r["variant_id"],
        ),
    )
    out: list[SampleRow] = []
    seen_store: set[str] = set()
    seen_cat: set[str] = set()
    for strict in (True, False):
        for r in candidates:
            s = display.store(r["store_id"])
            assert s is not None
            if s.id in seen_store or (strict and s.category in seen_cat):
                continue
            d = disc(r)
            variant = "" if r["variant_title"] in ("", "Default Title") else r["variant_title"]
            out.append(
                SampleRow(
                    store=display.name(s.id),
                    category=category_title(s.category),
                    product=display.title(s.id, r["product_title"]),
                    variant=variant,
                    price=usd(r["price_cents"]),
                    compare_at=usd(r["compare_at_cents"]) if d else "",
                    discount_pct=d or None,
                    in_stock=True,
                    url=display.product_url(s.id, r["handle"]),
                    raw=r,
                )
            )
            seen_store.add(s.id)
            seen_cat.add(s.category)
            if len(out) == n:
                return out
    return out


def _changes(
    data: Path, run: dict[str, Any], display: Display
) -> tuple[list[Change], dict[str, int]]:
    started = run["started_at"]
    path = data / "changes" / started[:4] / f"{started[:10]}.csv"
    if not path.exists():
        return [], {}
    with path.open(encoding="utf-8") as fh:
        rows = [r for r in csv.DictReader(fh) if r["observed_at"] == started]
    counts = Counter(r["event"] for r in rows)
    grouped: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for r in rows:
        if r["event"] != "new":
            grouped[(r["store_id"], r["variant_id"])].append(r)
    changes: list[Change] = []
    for group in grouped.values():
        r = group[0]
        sid = r["store_id"]
        pct = next((float(g["price_change_pct"]) for g in group if g["price_change_pct"]), None)
        removed = all(g["event"] == "removed" for g in group)
        changes.append(
            Change(
                store=display.name(sid),
                product=display.title(sid, r["product_title"]),
                variant="" if r["variant_title"] in ("", "Default Title") else r["variant_title"],
                events=[EVENT_WORDS.get(g["event"], g["event"]) for g in group],
                old_price=usd(r["old_price_cents"]),
                new_price=usd(r["new_price_cents"]),
                pct=pct,
                # A removed product's page is gone from the store: no link.
                url="" if removed else display.product_url(sid, r["handle"]),
            )
        )
    # Biggest price moves first, then sales and stock flips.
    changes.sort(key=lambda c: (-(abs(c.pct) if c.pct is not None else -1), c.store, c.product))
    return changes, dict(counts)


def _quality(run: dict[str, Any]) -> dict[str, Any]:
    stores = run.get("stores") or []
    witnesses = [w for s in stores for w in s.get("witnesses") or []]
    js_checked = sum(1 for w in witnesses if w.get("js") in ("match", "mismatch"))
    js_match = sum(1 for w in witnesses if w.get("js") == "match")
    usd_stores = sum(1 for s in stores if s.get("currencies") == ["USD"])
    blocked = sum(1 for s in stores if (s.get("reason") or "").startswith("blocked"))
    return {
        "stores_total": run.get("stores_total", 0),
        "stores_ok": run.get("stores_ok", 0),
        "not_updated": run.get("stores_not_updated") or [],
        "rows_observed": run.get("rows_observed", 0),
        "rows_rejected": run.get("rows_rejected", 0),
        "free_variants": run.get("free_variants", 0),
        "compare_at_ignored": run.get("compare_at_ignored", 0),
        "js_checked": js_checked,
        "js_match": js_match,
        "usd_stores": usd_stores,
        "blocked": blocked,
        "held": run.get("status") == "held",
        "hold_reasons": [h["message"] for h in run.get("guard", {}).get("holds", [])],
        "requests": run.get("requests", 0),
        "stores_added": len(run.get("stores_added") or []),
        "baseline_rows": run.get("baseline_rows", 0),
        "throttle_events": (run.get("edge") or {}).get("throttle_events", 0),
        "duration_min": round((run.get("duration_s") or 0) / 60, 1),
        "status": run.get("status"),
    }


def collect(
    data: Path, stores_path: Path, now: datetime | None = None, public_path: Path | None = None
) -> Facts:
    now = now or datetime.now(UTC)
    display = load_display(stores_path, public_path or ROOT / "config" / "public.yml")
    stores = display.stores
    by_id = {s.id: s for s in stores}
    runs = read_runs(data)
    good = [r for r in runs if r["status"] in GOOD]
    run = good[-1] if good else None
    facts = Facts(now=now, stores=stores, status=build_status(runs, now), run=run, display=display)
    # Rows of monitored stores only: a retired store's rows leave the snapshot in its
    # first run after the retirement (history.merge), and are not live prices before.
    rows = [
        r
        for r in _snapshot(data / "latest" / "snapshot.csv")
        if display.store(r["store_id"]) is not None
    ]
    facts.snapshot_rows = len(rows)
    facts.categories = dict(Counter(s.category for s in stores))
    if rows:
        facts.in_stock_share = sum(r["available"] == "true" for r in rows) / len(rows)
        facts.discounted_share = sum(
            bool(r["compare_at_cents"]) and int(r["compare_at_cents"]) > int(r["price_cents"])
            for r in rows
        ) / len(rows)
    facts.sample = _pick_sample(rows, by_id, display)
    if run:
        facts.changes, facts.change_counts = _changes(data, run, display)
        events = run.get("events") or {}
        facts.first_run = bool(events) and {k for k, v in events.items() if v} <= {"new"}
        facts.quality = _quality(run)
    return facts
