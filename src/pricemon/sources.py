"""Render the site register (docs/sources.md) from committed recon results.

Usage::

    python -m pricemon.sources checks/results/recon-00*/recon.json > docs/sources.md
    python -m pricemon.sources --stores-yml checks/results/recon-00*/recon.json > config/stores.yml

Every recon file is evidence. A store is dropped when **any** run shows one of
(docs/decisions.md, D-004):

* a challenge or block page, or retries exhausted on 429
* a 429 retry (runs before ``recon-004`` did not record retry statuses, so any
  retry there is treated as a 429)
* robots.txt disallowing a path the pipeline uses (``/products.json``,
  ``/products/<handle>.js``, ``/products/<handle>``), or robots.txt unreachable
* a product in an excluded category (adult, tobacco/vape, alcohol, cannabis/CBD,
  weapons) found by the content screen, unless a person reviewed exactly those
  titles as false positives in ``config/screen-review.yml``

and when its latest recon fails for any other reason (not Shopify, catalog over
3,000 variants, currency not proven USD, witness mismatch).

Among the stores left, at most ``PER_CATEGORY`` per category are *selected*,
ranked US shops first (``/meta.json`` country), then fewest recon caveats, then
larger catalogs; the list is then trimmed to ``MAX_STORES`` (owner decision D-020:
one run in 45 minutes on a single runner), never below ``MIN_PER_CATEGORY`` per
category. The rest are *reserve*.
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

PER_CATEGORY = 8
MIN_PER_CATEGORY = 4
# Owner decision (D-020): one daily run must finish in 45 minutes on a single runner,
# reached with a smaller list, never by spreading requests over several runners.
MAX_STORES = 25
CATEGORY_TITLES = {
    "audio": "Audio",
    "apparel": "Apparel",
    "beauty": "Beauty",
    "home_kitchen": "Home & kitchen",
    "outdoor": "Outdoor",
}
USED_PATHS = (
    ("robots_products_json", "/products.json"),
    ("robots_product_js", "/products/*.js"),
    ("robots_product_page", "/products/<handle>"),
)


REVIEW_PATH = Path("config/screen-review.yml")


@dataclass(frozen=True)
class ScreenReview:
    store: str
    category: str
    titles: frozenset[str]
    verdict: str
    reason: str


def load_reviews(path: Path = REVIEW_PATH) -> dict[str, list[ScreenReview]]:
    if not path.exists():
        return {}
    raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    out: dict[str, list[ScreenReview]] = defaultdict(list)
    for r in raw.get("reviews") or []:
        out[r["store"]].append(
            ScreenReview(
                r["store"], r["category"], frozenset(r["titles"]), r["verdict"], r["reason"]
            )
        )
    return dict(out)


@dataclass
class StoreRecord:
    store: str
    category: str
    history: list[tuple[str, dict[str, Any]]] = field(default_factory=list)
    reviews: list[ScreenReview] = field(default_factory=list)
    reserve_reason: str | None = None

    def _reviewed(self, category: str, examples: list[str]) -> ScreenReview | None:
        for review in self.reviews:
            if (
                review.category == category
                and review.verdict == "false_positive"
                and set(examples) <= review.titles
            ):
                return review
        return None

    def reviewed_titles(self) -> list[str]:
        return sorted(t for r in self.reviews if r.verdict == "false_positive" for t in r.titles)

    def caveats(self) -> list[str]:
        """Recon caveats used to rank otherwise equal stores (fewer is cleaner)."""
        r = self.latest
        out: list[str] = []
        if r.get("meta_country") != "US":
            out.append("shop not registered in the US")
        if not r.get("jsonld_currency"):
            out.append("USD proven by the theme only, no JSON-LD offer")
        if self.reviews:
            out.append("needed a reviewed content-screen hit")
        return out

    def review_notes(self) -> list[str]:
        return [f"screen hit reviewed ({r.category}): {r.reason}" for r in self.reviews]

    @property
    def latest(self) -> dict[str, Any]:
        return self.history[-1][1]

    @property
    def latest_id(self) -> str:
        return self.history[-1][0]

    def drop_reasons(self) -> list[str]:
        reasons: list[str] = []
        for rid, r in self.history:
            stopped = r.get("stopped_reason") or ""
            markers = ("blocked", "challenge", "http 429", "robots.txt unreachable")
            if any(m in stopped for m in markers):
                reasons.append(f"{rid}: {stopped}")
            if "retry_causes" in r:
                n429 = sum(1 for c in r["retry_causes"] if c.startswith("http 429"))
                if n429:
                    reasons.append(f"{rid}: {n429} retr{'y' if n429 == 1 else 'ies'} on 429")
            elif r.get("retries"):
                reasons.append(
                    f"{rid}: {r['retries']} retr{'y' if r['retries'] == 1 else 'ies'} "
                    "(status not recorded, treated as 429)"
                )
            for key, path in USED_PATHS:
                if r.get(key) is False:
                    reasons.append(f"{rid}: robots.txt disallows {path}")
            for cat, examples in (r.get("content_flags") or {}).items():
                if self._reviewed(cat, examples) is None:
                    reasons.append(f"{rid}: excluded category {cat} (e.g. {'; '.join(examples)})")
        latest = self.latest
        if not latest["passed"]:
            covered = ("blocked", "robots", "needed 429", "excluded category")
            other = [f for f in latest["fail_reasons"] if not f.startswith(covered)]
            if other:
                reasons.append(f"{self.latest_id}: " + ", ".join(other))
        # Keep order, drop exact duplicates.
        return list(dict.fromkeys(reasons))


def collect(
    sources: list[tuple[str, dict[str, Any]]],
    reviews: dict[str, list[ScreenReview]] | None = None,
) -> list[StoreRecord]:
    reviews = reviews or {}
    records: dict[str, StoreRecord] = {}
    for _, payload in sources:
        rid = payload["meta"]["id"]
        for r in payload["results"]:
            rec = records.setdefault(
                r["store"],
                StoreRecord(r["store"], r["category"], reviews=reviews.get(r["store"], [])),
            )
            rec.history.append((rid, r))
    return list(records.values())


def classify(
    records: list[StoreRecord],
    per_category: int = PER_CATEGORY,
    max_stores: int = MAX_STORES,
    min_per_category: int = MIN_PER_CATEGORY,
) -> dict[str, list[StoreRecord]]:
    """Split records into selected, reserve and dropped.

    Ranking inside a category: US shops first, then fewest recon caveats, then
    larger catalogs. At most ``per_category`` per category; then, while more than
    ``max_stores`` are selected, the weakest store (most caveats, from the largest
    category, smallest catalog) moves to reserve, never leaving a category with
    fewer than ``min_per_category``.
    """
    groups: dict[str, list[StoreRecord]] = {"selected": [], "reserve": [], "dropped": []}
    by_cat: dict[str, list[StoreRecord]] = defaultdict(list)
    for rec in records:
        if rec.drop_reasons():
            groups["dropped"].append(rec)
        else:
            by_cat[rec.category].append(rec)
    chosen: dict[str, list[StoreRecord]] = {}
    for cat, rows in by_cat.items():
        rows.sort(
            key=lambda x: (
                x.latest.get("meta_country") != "US",
                len(x.caveats()),
                -x.latest["variants"],
                x.store,
            )
        )
        chosen[cat] = rows[:per_category]
        for rec in rows[per_category:]:
            rec.reserve_reason = f"more than {per_category} in the category"
            groups["reserve"].append(rec)
    while sum(len(v) for v in chosen.values()) > max_stores:
        options = [
            (len(rec.caveats()), len(rows), -int(rec.latest["variants"]), rec.store, cat, rec)
            for cat, rows in chosen.items()
            if len(rows) > min_per_category
            for rec in rows
        ]
        if not options:
            break
        *_, cat, weakest = max(options, key=lambda o: o[:4])
        chosen[cat].remove(weakest)
        caveats = "; ".join(weakest.caveats()) or "no caveats"
        weakest.reserve_reason = f"trimmed to {max_stores} stores for the run budget ({caveats})"
        groups["reserve"].append(weakest)
    for rows in chosen.values():
        groups["selected"] += rows
    return groups


# The repository was renamed on 2026-11-05; recon evidence keeps the URLs it recorded
# (GitHub redirects them), the register links the current name.
RENAMED = (
    "/siddharthkumarx/ecommerce-price-monitor-wip/",
    "/siddharthkumarx/ecommerce-price-monitor/",
)


def current_url(url: str | None) -> str | None:
    return url.replace(*RENAMED) if url else url


def _order(rec: StoreRecord) -> tuple[int, str]:
    order = list(CATEGORY_TITLES)
    return (order.index(rec.category) if rec.category in order else 99, rec.store.lower())


def _robots(r: dict[str, Any]) -> str:
    if r["robots_status"] == "unreachable":
        return "unreachable"
    if r.get("robots_products_json") is None:
        return "-"
    parts = [
        f"{path} {'allow' if r.get(key) else 'disallow'}"
        for key, path in USED_PATHS
        if r.get(key) is not None
    ]
    if r.get("crawl_delay_s"):
        parts.append(f"crawl-delay {r['crawl_delay_s']:g}s")
    return ", ".join(parts)


def _currency(r: dict[str, Any]) -> str:
    jsonld: set[str] = set(r.get("jsonld_currency") or [])
    theme = r.get("shopify_currency")
    seen = sorted(jsonld | ({theme} if isinstance(theme, str) else set()))
    if not seen:
        return "-"
    label = ",".join(seen)
    return label if jsonld else f"{label} (theme only, no JSON-LD offer)"


def _base_domain(host: str) -> str:
    return host.removeprefix("www.")


def _host(r: dict[str, Any]) -> str:
    return str(r.get("host") or r["domain"])


def _notes(rec: StoreRecord) -> str:
    r = rec.latest
    bits: list[str] = []
    if r.get("host") and _base_domain(r["host"]) != _base_domain(r["domain"]):
        bits.append(f"`{r['domain']}` redirects here")
    if r.get("meta_country") and r["meta_country"] != "US":
        bits.append(f"shop country {r['meta_country']}")
    if r.get("available_share") is not None:
        bits.append(f"{r['available_share']:.0%} variants in stock")
    if r.get("js_crosscheck") == "match":
        bits.append(".js prices match")
    bits += rec.review_notes()
    if rec.reserve_reason:
        bits.append(f"reserve: {rec.reserve_reason}")
    bits.append("runs: " + ", ".join(rid for rid, _ in rec.history))
    return "; ".join(bits)


KEPT_HEADER = (
    "| store | category | host | products | variants | robots (paths used) "
    "| currency (country=US) | notes |\n|---|---|---|---:|---:|---|---|---|"
)


def _kept_row(rec: StoreRecord) -> str:
    r = rec.latest
    return (
        f"| {rec.store} | {CATEGORY_TITLES.get(rec.category, rec.category)} | `{_host(r)}` "
        f"| {r['products']:,} | {r['variants']:,} | {_robots(r)} | {_currency(r)} "
        f"| {_notes(rec)} |"
    )


def _dropped_row(rec: StoreRecord) -> str:
    r = rec.latest
    reasons = "<br>".join(rec.drop_reasons())
    return (
        f"| {rec.store} | {CATEGORY_TITLES.get(rec.category, rec.category)} "
        f"| `{_host(r)}` | {reasons} |"
    )


def render(
    sources: list[tuple[str, dict[str, Any]]],
    reviews: dict[str, list[ScreenReview]] | None = None,
) -> str:
    """Render the register from ``(path, payload)`` pairs, oldest run first."""
    records = collect(sources, reviews)
    groups = classify(records)
    selected = sorted(groups["selected"], key=_order)
    counts: dict[str, int] = defaultdict(int)
    variants: dict[str, int] = defaultdict(int)
    for rec in selected:
        counts[rec.category] += 1
        variants[rec.category] += int(rec.latest["variants"])
    short = [CATEGORY_TITLES[c] for c in CATEGORY_TITLES if counts[c] < MIN_PER_CATEGORY]
    lines = [
        "# Site register",
        "",
        "Generated by `python -m pricemon.sources "
        + " ".join(path for path, _ in sources)
        + "` from these recon runs on GitHub-hosted runners:",
        "",
        *(
            f"- `{p['meta']['id']}`: finished {p['meta']['finished_utc']}, "
            f"{len(p['results'])} stores, [Actions run]({current_url(p['meta']['run_url'])})"
            for _, p in sources
        ),
        "",
        "Every value below comes from those runs; nothing is typed by hand. Drop rules are in "
        "the module docstring of `src/pricemon/sources.py` and in `docs/decisions.md` (D-004).",
        "",
        f"- candidates: {len(records)}",
        f"- selected: {len(selected)} stores, {sum(variants.values()):,} variants",
        *(
            f"  - {CATEGORY_TITLES[c]}: {counts[c]} stores, {variants[c]:,} variants"
            for c in CATEGORY_TITLES
        ),
        f"- reserve: {len(groups['reserve'])}",
        f"- dropped: {len(groups['dropped'])}",
        f"- categories under {MIN_PER_CATEGORY} stores: {', '.join(short) or 'none'}",
        "",
        "## Selected",
        "",
        KEPT_HEADER,
        *(_kept_row(rec) for rec in selected),
    ]
    if groups["reserve"]:
        lines += ["", "## Reserve (pass every rule, not monitored yet)", "", KEPT_HEADER]
        lines += [_kept_row(rec) for rec in sorted(groups["reserve"], key=_order)]
    lines += [
        "",
        "## Dropped",
        "",
        "| store | category | host | reasons (run: evidence) |",
        "|---|---|---|---|",
        *(_dropped_row(rec) for rec in sorted(groups["dropped"], key=_order)),
    ]
    return "\n".join(lines) + "\n"


def render_stores_yml(
    sources: list[tuple[str, dict[str, Any]]],
    reviews: dict[str, list[ScreenReview]] | None = None,
) -> str:
    """The monitored store list consumed by the daily run (config/stores.yml)."""
    groups = classify(collect(sources, reviews))
    ids = ", ".join(p["meta"]["id"] for _, p in sources)
    lines = [
        "# Monitored stores. Generated by `python -m pricemon.sources --stores-yml` from",
        f"# recon runs {ids}. Do not edit by hand: change the recon evidence instead.",
        "stores:",
    ]
    for rec in sorted(groups["selected"], key=_order):
        r = rec.latest
        slug = "".join(ch if ch.isalnum() else "-" for ch in rec.store.lower()).strip("-")
        while "--" in slug:
            slug = slug.replace("--", "-")
        lines += [
            f"  - id: {slug}",
            f"    name: {json.dumps(rec.store)}",
            f"    category: {rec.category}",
            f"    host: {_host(r)}",
            f"    recon_variants: {r['variants']}",
            f"    recon_products: {r['products']}",
        ]
        if rec.reviewed_titles():
            lines.append(f"    screen_reviewed: {json.dumps(rec.reviewed_titles())}")
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("recon_json", type=Path, nargs="+")
    parser.add_argument("--stores-yml", action="store_true", help="emit config/stores.yml")
    parser.add_argument("--reviews", type=Path, default=REVIEW_PATH, help="screen-review file")
    args = parser.parse_args(argv)
    paths = sorted(args.recon_json, key=lambda p: p.parent.name)
    sources = [(p.as_posix(), json.loads(p.read_text(encoding="utf-8"))) for p in paths]
    reviews = load_reviews(args.reviews)
    out = render_stores_yml(sources, reviews) if args.stores_yml else render(sources, reviews)
    print(out, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
