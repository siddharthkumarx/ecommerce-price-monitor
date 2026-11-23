"""Render README.md and the dataset card from templates and the latest real run.

    python -m pricemon.readme [--data data] [--stores config/stores.yml]

Run by the daily workflow after every run, so the README's numbers, sample rows
and "What changed today" always match the newest data. Templates live in
``templates/``; the rendered files must never contain template syntax, HTML
comments or placeholders (tests/test_readme.py).
"""

from __future__ import annotations

import argparse
import csv
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml
from jinja2 import Environment, FileSystemLoader, StrictUndefined

from pricemon.outputs import on_time_text
from pricemon.report import EVENT_WORDS, Facts, collect
from pricemon.stores import CATEGORY_TITLES, PLATFORM_TITLES
from pricemon.summary import SINCE, delivery, read_summary

ROOT = Path(__file__).resolve().parents[2]

SUMMARY_FIELDS = [
    ("date", "date", "UTC date"),
    ("stores_counted", "integer", "Stores in the public numbers that day"),
    ("prices", "integer", "Live prices after the day's last good run"),
    ("price_drops / price_rises", "integer", "Price changes that day"),
    ("sales_started", "integer", "Sales that started that day"),
    ("out_of_stock / back_in_stock", "integer", "Stock changes that day"),
    ("delivered / on_time", "yes/no", "Every due run delivered; every due run started within 2 h"),
    ("rows_held", "integer", "Rows read but held back by a check that day"),
]
SNAPSHOT_FIELDS = [
    ("store_id", "text", "Store, as listed in `config/stores.yml`"),
    ("product_id", "integer", "The store's product id"),
    ("variant_id", "integer", "The store's id for this option (size, colour); unique per store"),
    (
        "handle",
        "text",
        "Product address: Shopify `https://<store>/products/<handle>`; WooCommerce and "
        "BigCommerce `https://<store>/<handle>/`",
    ),
    ("product_title", "text", "Product name as shown by the store"),
    ("variant_title", "text", "Option name (`Default Title` when there is only one)"),
    ("price_cents", "integer", "Current price in US cents"),
    ("compare_at_cents", "integer or empty", '"Was" price in US cents when on sale, else empty'),
    ("available", "true/false", "In stock"),
    ("valid_from", "UTC time", "When this price and stock state was first seen"),
]
CHANGE_FIELDS = [
    ("observed_at", "UTC time", "Run that saw the change"),
    ("store_id", "text", "Store"),
    ("variant_id", "integer", "Product option"),
    ("product_title", "text", "Product name"),
    ("event", "text", "One of: " + ", ".join(f"`{k}`" for k in EVENT_WORDS)),
    ("old_price_cents", "integer or empty", "Price before, US cents"),
    ("new_price_cents", "integer or empty", "Price after, US cents"),
    ("old_compare_at_cents", "integer or empty", '"Was" price before'),
    ("new_compare_at_cents", "integer or empty", '"Was" price after'),
    ("price_change_pct", "number or empty", "Price change in percent, for price events"),
]
PLURAL = {
    "price_down": ("price drop", "price drops"),
    "price_up": ("price rise", "price rises"),
    "discount_start": ("sale started", "sales started"),
    "discount_end": ("sale ended", "sales ended"),
    "out_of_stock": ("item sold out", "items sold out"),
    "back_in_stock": ("item back in stock", "items back in stock"),
    "new": ("new product option", "new product options"),
    "removed": ("product option removed", "product options removed"),
}


def change_summary(counts: dict[str, int]) -> str:
    parts = []
    for key, (one, many) in PLURAL.items():
        n = counts.get(key, 0)
        if n:
            parts.append(f"{n:,} {one if n == 1 else many}")
    return ", ".join(parts) if parts else "no changes"


def _latest_change_row(data: Path) -> dict[str, str]:
    files = sorted((data / "changes").glob("*/*.csv"))
    if not files:
        return {}
    with files[-1].open(encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    preferred = [r for r in rows if r["event"] in ("price_down", "discount_start")]
    return (preferred or rows or [{}])[0]


def dictionary(f: Facts, data: Path) -> dict[str, list[dict[str, str]]]:
    snap = f.sample[0].raw if f.sample else {}
    change = _latest_change_row(data)

    def table(fields: list[tuple[str, str, str]], example: dict[str, str]) -> list[dict[str, str]]:
        return [
            {
                "field": name,
                "type": typ,
                "meaning": meaning,
                "example": example.get(name) or "(empty)",
            }
            for name, typ, meaning in fields
        ]

    return {"snapshot": table(SNAPSHOT_FIELDS, snap), "changes": table(CHANGE_FIELDS, change)}


def context(data: Path, stores: Path, public: Path, now: datetime | None = None) -> dict[str, Any]:
    f = collect(data, stores, now or datetime.now(UTC))
    pub = yaml.safe_load(public.read_text(encoding="utf-8"))
    repo_url = f"https://github.com/{pub['repo']}"
    summary = list(read_summary(data / "history" / "daily-summary.csv").values())
    run = f.run or {}
    reads = run.get("second_reads") or {}
    used = {s.platform for s in f.stores}
    return {
        "delivery": delivery(summary, f.status),
        "since_text": f"{SINCE.day} {SINCE:%b %Y}",
        "summary_days": len(summary),
        "summary_fields": SUMMARY_FIELDS,
        "platforms": [PLATFORM_TITLES[p] for p in PLATFORM_TITLES if p in used],
        "category_titles": [CATEGORY_TITLES[c] for c in CATEGORY_TITLES if c in f.categories],
        "second": {
            "reads": int(reads.get("reads") or 0),
            "confirmed": int(reads.get("confirmed") or 0),
            "held": int(run.get("rows_held_back") or 0),
        },
        "f": f,
        "q": f.quality,
        "sched": f.status["schedule"],
        "on_time": dict(zip(("label", "value"), on_time_text(f.status["schedule"]), strict=True)),
        "stores": f.stores,
        "pub": pub,
        "repo_url": repo_url,
        "raw": f"https://raw.githubusercontent.com/{pub['repo']}/{pub['branch']}",
        "change_summary": change_summary(f.change_counts),
        "dictionary": dictionary(f, data),
        "categories": f.categories,
        "bfcm_runs": _bfcm_runs(),
    }


def _bfcm_runs() -> int:
    """The BFCM_RUNS_PER_DAY flag of the daily workflow (D-021)."""
    wf = yaml.safe_load((ROOT / ".github" / "workflows" / "daily.yml").read_text(encoding="utf-8"))
    return int(wf["env"]["BFCM_RUNS_PER_DAY"])


def render(template: Path, ctx: dict[str, Any]) -> str:
    # Markdown output, not HTML: autoescaping would corrupt it. Table cells are
    # escaped with the `md` filter.
    env = Environment(
        loader=FileSystemLoader(str(template.parent)),
        undefined=StrictUndefined,
        keep_trailing_newline=True,
        autoescape=False,  # noqa: S701  (Markdown, see above)
    )
    env.filters["md"] = lambda v: str(v).replace("|", "\\|")
    text = env.get_template(template.name).render(**ctx)
    return "\n".join(line.rstrip() for line in text.splitlines()).strip() + "\n"


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
    p.add_argument("--data", type=Path, default=ROOT / "data")
    p.add_argument("--stores", type=Path, default=ROOT / "config" / "stores.yml")
    p.add_argument("--public", type=Path, default=ROOT / "config" / "public.yml")
    p.add_argument("--templates", type=Path, default=ROOT / "templates")
    p.add_argument("--out", type=Path, default=ROOT)
    a = p.parse_args(argv)
    ctx = context(a.data, a.stores, a.public)
    targets = {"README.md.j2": a.out / "README.md", "DATASET_CARD.md.j2": a.data / "README.md"}
    for name, target in targets.items():
        source = a.templates / name
        if source.exists():
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(render(source, ctx), encoding="utf-8")
            print(target)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
