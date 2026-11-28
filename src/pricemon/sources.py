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

Stores listed in ``config/retired.yml`` are never selected, whatever their evidence;
the list is copied into ``config/stores.yml`` (D-031).

Each store's ``terms`` field (``ban``, ``no_ban`` or ``none_found``) is that of its
latest recon run that read the Terms of Service page (``recon-005`` on); a store no
such run read is ``none_found``. A store whose terms are ``ban`` is dropped and never
monitored (owner decision D-036).

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

from pricemon.stores import (
    ALIASES_PATH,
    CATEGORY_TITLES,
    RetiredStore,
    assign_aliases,
    dump_aliases,
    load_alias_next,
    load_aliases,
    load_retired,
)

# Owner decision (F1-EXPAND addendum): 10-12 categories of 20-25 stores, each a demo
# competitor set; at most PER_CATEGORY per category, MAX_STORES in all.
PER_CATEGORY = 25
MIN_PER_CATEGORY = 4
# Owner decisions: D-020 (one daily run on a single runner, inside the job budget,
# never by spreading requests over several runners at once) and D-031 (at least 100
# stores from 27 Nov 2026).
MAX_STORES = 300
# Selection order inside a category (HQ review A4): stores whose terms do not ban
# automated access first, unknown terms next. A store whose terms ban robots is
# dropped since D-036 (owner, 27 Nov 2026); its rank stays for the trimming key.
TERMS_RANK = {"no_ban": 0, "none_found": 1, "ban": 2}
RETIRED_PATH = Path("config/retired.yml")
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

    def terms_record(self) -> dict[str, Any] | None:
        """The recon result that decides the store's terms value.

        The latest run that looked at the Terms page, except that a proven ``ban``
        stands until a later run read the page and found no ban: a later run that
        could not read it (robots.txt, http error, no policy text) is ``none_found``
        and does not lift a ban (D-036).
        """
        current: dict[str, Any] | None = None
        for _, r in self.history:
            if r.get("terms") is None:
                continue
            lifted = r.get("terms_source") == "read" and r.get("terms") == "no_ban"
            if current is not None and current.get("terms") == "ban" and not lifted:
                continue
            current = r
        return current

    @property
    def terms(self) -> str:
        rec = self.terms_record()
        return str(rec["terms"]) if rec else "none_found"

    def terms_note(self) -> str:
        rec = self.terms_record()
        if rec is None:
            return "terms none_found (not checked)"
        return f"terms {rec['terms']} ({rec.get('terms_source') or '-'})"

    def review_notes(self) -> list[str]:
        return [f"screen hit reviewed ({r.category}): {r.reason}" for r in self.reviews]

    @property
    def recon(self) -> list[tuple[str, dict[str, Any]]]:
        """The recon rows; a Terms check row (``check: terms``) only feeds ``terms``."""
        return [(rid, r) for rid, r in self.history if r.get("check") != "terms"]

    @property
    def latest(self) -> dict[str, Any]:
        return self.recon[-1][1]

    @property
    def latest_id(self) -> str:
        return self.recon[-1][0]

    def drop_reasons(self) -> list[str]:
        reasons: list[str] = []
        # A later row screened with a newer content screen supersedes the content
        # flags of earlier rows (D-039); rows before screen versions were recorded are v1.
        recon = self.recon
        screens = [r.get("screen_version") or 1 for _, r in recon]
        for i, (rid, r) in enumerate(recon):
            superseded = any(v > screens[i] for v in screens[i + 1 :])
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
                if not superseded and self._reviewed(cat, examples) is None:
                    reasons.append(f"{rid}: excluded category {cat} (e.g. {'; '.join(examples)})")
        terms = self.terms_record()
        if terms is not None and terms["terms"] == "ban":
            # Owner decision D-036: a store whose terms ban robots is not monitored.
            rid = next(i for i, r in self.history if r is terms)
            reasons.append(f"{rid}: terms ban, not monitored (D-036)")
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
    """One record per store, its rows in the order the runs started (a Terms check
    reads stores already listed, so it never creates a record)."""
    reviews = reviews or {}
    records: dict[str, StoreRecord] = {}
    ordered = sorted(sources, key=lambda s: str(s[1]["meta"].get("started_utc") or ""))
    for _, payload in ordered:
        rid = payload["meta"]["id"]
        for r in payload["results"]:
            if r.get("check") == "terms" and r["store"] not in records:
                continue
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
    retired: set[str] | None = None,
    keep: set[str] | None = None,
) -> dict[str, list[StoreRecord]]:
    """Split records into selected, reserve and dropped.

    Ranking inside a category: terms ``no_ban``, then ``none_found`` (a ``ban`` is
    dropped, D-036);
    then a store selected before (its id in ``keep``, the fixed-number registry) over
    a new one, so a list that grows does not push monitored stores out; then US shops
    first, fewest recon caveats, larger catalogs. At most
    ``per_category`` per category; then, while more than ``max_stores`` are selected,
    a store moves to reserve from the largest category (a ban first, then most
    caveats, smallest catalog), never leaving a category with fewer than
    ``min_per_category``.
    """
    groups: dict[str, list[StoreRecord]] = {
        "selected": [],
        "reserve": [],
        "dropped": [],
        "retired": [],
    }
    keep = keep or set()
    by_cat: dict[str, list[StoreRecord]] = defaultdict(list)
    for rec in records:
        if rec.store in (retired or set()):
            groups["retired"].append(rec)
        elif rec.drop_reasons():
            groups["dropped"].append(rec)
        else:
            by_cat[rec.category].append(rec)
    chosen: dict[str, list[StoreRecord]] = {}
    for cat, rows in by_cat.items():
        rows.sort(
            key=lambda x: (
                TERMS_RANK.get(x.terms, 1),
                store_slug(x.store) not in keep,
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
        # Fair shares: trim the largest category first, a ban first, then caveats.
        options = [
            (
                len(rows),
                TERMS_RANK.get(rec.terms, 1),
                store_slug(rec.store) not in keep,
                len(rec.caveats()),
                -int(rec.latest["variants"]),
                rec.store,
                cat,
                rec,
            )
            for cat, rows in chosen.items()
            if len(rows) > min_per_category
            for rec in rows
        ]
        if not options:
            break
        *_, cat, weakest = max(options, key=lambda o: o[:6])
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
    bits.append(rec.terms_note())
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
    retired: list[RetiredStore] | None = None,
    max_stores: int = MAX_STORES,
    keep: set[str] | None = None,
) -> str:
    """Render the register from ``(path, payload)`` pairs, oldest run first."""
    records = collect(sources, reviews)
    retired = retired or []
    groups = classify(records, max_stores=max_stores, retired={r.name for r in retired}, keep=keep)
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
        "- terms of the selected stores: "
        + ", ".join(
            f"{v} {sum(1 for rec in selected if rec.terms == v)}"
            for v in ("ban", "no_ban", "none_found")
        ),
        f"- reserve: {len(groups['reserve'])}",
        f"- dropped: {len(groups['dropped'])}",
        f"- retired: {len(retired)}",
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
    if retired:
        lines += [
            "",
            "## Retired (left the monitor on purpose, `config/retired.yml`)",
            "",
            "| store | category | retired on |",
            "|---|---|---|",
            *(
                f"| {r.name} | {CATEGORY_TITLES.get(r.category, r.category)} "
                f"| {r.retired_on.isoformat()} |"
                for r in retired
            ),
        ]
    lines += [
        "",
        "## Dropped",
        "",
        "| store | category | host | reasons (run: evidence) |",
        "|---|---|---|---|",
        *(_dropped_row(rec) for rec in sorted(groups["dropped"], key=_order)),
    ]
    return "\n".join(lines) + "\n"


def store_slug(name: str) -> str:
    """The store id in config/stores.yml, from the store's name."""
    slug = "".join(ch if ch.isalnum() else "-" for ch in name.lower()).strip("-")
    while "--" in slug:
        slug = slug.replace("--", "-")
    return slug


def selected_aliases(
    sources: list[tuple[str, dict[str, Any]]],
    reviews: dict[str, list[ScreenReview]] | None,
    retired: list[RetiredStore] | None,
    max_stores: int,
    aliases: dict[str, int],
    next_no: int = 1,
) -> tuple[dict[str, int], int]:
    """The registry of the selected stores (existing numbers kept, new ones from
    ``next_no``) and the next number never given. Stores that left are not in it
    (D-036); their numbers are not given again."""
    groups = classify(
        collect(sources, reviews),
        max_stores=max_stores,
        retired={r.name for r in retired or []},
        keep=set(aliases),
    )
    chosen = [store_slug(rec.store) for rec in sorted(groups["selected"], key=_order)]
    full = assign_aliases(aliases, chosen, next_no)
    nxt = max(next_no, max(full.values(), default=0) + 1)
    return {sid: full[sid] for sid in chosen}, nxt


def render_stores_yml(
    sources: list[tuple[str, dict[str, Any]]],
    reviews: dict[str, list[ScreenReview]] | None = None,
    retired: list[RetiredStore] | None = None,
    max_stores: int = MAX_STORES,
    aliases: dict[str, int] | None = None,
    keep: set[str] | None = None,
) -> str:
    """The monitored store list consumed by the daily run (config/stores.yml).

    ``aliases`` is the fixed-number registry (config/aliases.yml); stores without a
    number get the next one (see :func:`selected_aliases` to update the registry).
    """
    retired = retired or []
    groups = classify(
        collect(sources, reviews),
        max_stores=max_stores,
        retired={r.name for r in retired},
        keep=set(keep if keep is not None else aliases or {}),
    )
    ids = ", ".join(p["meta"]["id"] for _, p in sources)
    lines = [
        "# Monitored stores. Generated by `python -m pricemon.sources --stores-yml` from",
        f"# recon runs {ids}. Do not edit by hand: change the recon evidence instead.",
        "stores:",
    ]
    chosen = sorted(groups["selected"], key=_order)
    numbers = assign_aliases(aliases or {}, [store_slug(rec.store) for rec in chosen])
    for rec in chosen:
        r = rec.latest
        slug = store_slug(rec.store)
        lines += [
            f"  - id: {slug}",
            f"    name: {json.dumps(rec.store)}",
            f"    category: {rec.category}",
            f"    host: {_host(r)}",
            f"    recon_variants: {r['variants']}",
            f"    recon_products: {r['products']}",
            f"    terms: {rec.terms}",
            f"    public_no: {numbers[slug]}",
        ]
        if rec.reviewed_titles():
            lines.append(f"    screen_reviewed: {json.dumps(rec.reviewed_titles())}")
    if retired:
        lines.append("# Left the monitor on purpose (config/retired.yml); not read by any run.")
        lines.append("retired:")
        for ret in retired:
            lines += [
                f"  - id: {ret.id}",
                f"    name: {json.dumps(ret.name)}",
                f"    category: {ret.category}",
                f"    retired_on: {ret.retired_on.isoformat()}",
            ]
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("recon_json", type=Path, nargs="+")
    parser.add_argument("--stores-yml", action="store_true", help="emit config/stores.yml")
    parser.add_argument("--reviews", type=Path, default=REVIEW_PATH, help="screen-review file")
    parser.add_argument("--retired", type=Path, default=RETIRED_PATH, help="retired stores")
    parser.add_argument(
        "--max-stores", type=int, default=MAX_STORES, help="store-list size (default MAX_STORES)"
    )
    parser.add_argument(
        "--aliases", type=Path, default=ALIASES_PATH, help="fixed public numbers (updated)"
    )
    args = parser.parse_args(argv)
    paths = sorted(args.recon_json, key=lambda p: p.parent.name)
    sources = [(p.as_posix(), json.loads(p.read_text(encoding="utf-8"))) for p in paths]
    reviews = load_reviews(args.reviews)
    retired = load_retired(args.retired)
    # Stores selected before (they have a fixed number) keep their place (D-031).
    before = load_aliases(args.aliases)
    if args.stores_yml:
        # Numbers never change and are never given twice (D-034, D-036).
        aliases, nxt = selected_aliases(
            sources, reviews, retired, args.max_stores, before, load_alias_next(args.aliases)
        )
        args.aliases.write_text(dump_aliases(aliases, nxt), encoding="utf-8")
        out = render_stores_yml(
            sources, reviews, retired, args.max_stores, aliases, keep=set(before)
        )
    else:
        out = render(sources, reviews, retired, args.max_stores, keep=set(before))
    print(out, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
