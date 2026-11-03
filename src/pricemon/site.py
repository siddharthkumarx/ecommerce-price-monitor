"""Build the static dashboard into ``site/`` from the committed data.

    python -m pricemon.site --data data --stores config/stores.yml --out site

No JavaScript, no external requests: one HTML file with inline CSS and two
self-hosted font families (OFL). Every number on the page is read from
``data/status.json``, ``data/runs.jsonl``, ``data/latest/snapshot.csv`` and
``data/changes/``.
"""

from __future__ import annotations

import argparse
import html
import shutil
from collections import defaultdict
from datetime import UTC, datetime
from pathlib import Path

from pricemon.outputs import build_status, parse_iso, read_runs, recent_events, snapshot_summary
from pricemon.stores import Store, load_stores

ASSETS = Path(__file__).parent / "site_assets"
CATEGORY_TITLES = {
    "audio": "Audio",
    "apparel": "Apparel",
    "beauty": "Beauty",
    "home_kitchen": "Home & kitchen",
    "outdoor": "Outdoor",
}
EVENT_LABELS = {
    "price_down": "Price down",
    "price_up": "Price up",
    "discount_start": "Discount start",
    "discount_end": "Discount end",
    "out_of_stock": "Out of stock",
    "back_in_stock": "Back in stock",
    "new": "New",
    "removed": "Removed",
}
# teal = good / in stock; amber = look here / out of stock / price change
EVENT_TONE = {
    "price_down": "amber",
    "price_up": "amber",
    "discount_start": "amber",
    "discount_end": "amber",
    "out_of_stock": "amber",
    "back_in_stock": "teal",
    "new": "teal",
    "removed": "quiet",
}
REPO_URL = "https://github.com/siddharthkumarx/ecommerce-price-monitor"

CSS = (ASSETS / "style.css").read_text(encoding="utf-8")


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def usd(cents: object) -> str:
    if cents in (None, ""):
        return ""
    return f"${int(str(cents)) / 100:,.2f}"


def pct(part: int, whole: int) -> str:
    return f"{part / whole:.0%}" if whole else "-"


def _kpi(label: str, value: str, tone: str = "") -> str:
    return (
        f'<li class="panel kpi"><span class="label">{esc(label)}</span>'
        f'<span class="value {tone}">{esc(value)}</span></li>'
    )


def _table(caption: str, head: list[tuple[str, bool]], rows: list[list[str]], label: str) -> str:
    ths = "".join(f'<th scope="col"{" class=num" if num else ""}>{esc(h)}</th>' for h, num in head)
    body = "".join("<tr>" + "".join(r) + "</tr>" for r in rows)
    return (
        f'<div class="scroll" role="region" aria-label="{esc(label)}" tabindex="0">'
        f"<table><caption>{esc(caption)}</caption><thead><tr>{ths}</tr></thead>"
        f"<tbody>{body}</tbody></table></div>"
    )


def td(value: object, num: bool = False, cls: str = "") -> str:
    classes = " ".join(c for c in ("num" if num else "", cls) if c)
    return f'<td class="{classes}">{esc(value)}</td>' if classes else f"<td>{esc(value)}</td>"


def render(data: Path, stores: list[Store], now: datetime) -> str:
    runs = read_runs(data)
    status = build_status(runs, now)
    summary = {s["store_id"]: s for s in snapshot_summary(data / "latest" / "snapshot.csv")}
    events = recent_events(data)
    last = status["last_run"]
    good_runs = [r for r in runs if r["status"] in ("ok", "partial")]
    last_good = good_runs[-1] if good_runs else None

    variants = sum(int(s["variants"]) for s in summary.values())
    in_stock = sum(int(s["in_stock"]) for s in summary.values())
    discounted = sum(int(s["discounted"]) for s in summary.values())

    if last:
        tone = "teal" if last["status"] == "ok" else "amber"
        when = parse_iso(last["started_at"]).strftime("%Y-%m-%d %H:%M UTC")
        pill = f'<span class="dot {tone}" aria-hidden="true"></span>Last run {esc(when)}: {esc(last["status"])}'
    else:
        pill = '<span class="dot" aria-hidden="true"></span>No runs yet'

    kpis = "".join(
        [
            _kpi("Stores", str(len(stores))),
            _kpi("Variants live", f"{variants:,}"),
            _kpi("In stock", pct(in_stock, variants), "teal"),
            _kpi("Discounted", pct(discounted, variants), "amber"),
            _kpi("Days running", str(status["days_running"])),
            _kpi(
                "Missed runs",
                str(status["missed_runs"]),
                "teal" if not status["missed_runs"] else "amber",
            ),
        ]
    )

    counts = (last_good or {}).get("events") or {}
    event_items = "".join(
        f'<li><span>{esc(EVENT_LABELS[k])}</span><b class="{EVENT_TONE[k]}">{int(counts.get(k, 0)):,}</b></li>'
        for k in EVENT_LABELS
    )
    when_good = (
        parse_iso(last_good["started_at"]).strftime("%Y-%m-%d %H:%M UTC")
        if last_good
        else "no run yet"
    )

    by_cat: dict[str, list[Store]] = defaultdict(list)
    for s in stores:
        by_cat[s.category].append(s)
    not_updated = {s["store_id"]: s for s in (last or {}).get("stores_not_updated") or []}
    store_rows: list[list[str]] = []
    for cat in CATEGORY_TITLES:
        for s in sorted(by_cat.get(cat, []), key=lambda x: x.name.lower()):
            agg = summary.get(s.id, {})
            v = int(agg.get("variants", 0))
            state = not_updated.get(s.id)
            store_rows.append(
                [
                    f'<td><a href="https://{esc(s.host)}" rel="nofollow noopener">{esc(s.name)}</a></td>',
                    td(CATEGORY_TITLES[cat], cls="cat"),
                    td(f"{v:,}", num=True),
                    td(pct(int(agg.get("in_stock", 0)), v), num=True, cls="teal"),
                    td(pct(int(agg.get("discounted", 0)), v), num=True, cls="amber"),
                    td(
                        f"{agg['avg_discount_pct']}%"
                        if agg.get("avg_discount_pct") is not None
                        else "-",
                        num=True,
                    ),
                    td(usd(agg.get("median_price_cents")), num=True),
                    td(
                        state["status"] if state else ("ok" if last else "-"),
                        cls="amber" if state else "teal",
                    ),
                ]
            )
    store_table = _table(
        "Live snapshot per store. Discounted: compare-at price above price.",
        [
            ("Store", False),
            ("Category", False),
            ("Variants", True),
            ("In stock", True),
            ("Discounted", True),
            ("Avg discount", True),
            ("Median price", True),
            ("Last run", False),
        ],
        store_rows,
        "Stores table",
    )

    names = {s.id: s.name for s in stores}
    hosts = {s.id: s.host for s in stores}
    # One row per variant and run: a sale is "Price down · Discount start".
    grouped: dict[tuple[str, str, str], list[dict[str, str]]] = {}
    for e in events:
        grouped.setdefault((e["observed_at"], e["store_id"], e["variant_id"]), []).append(e)
    latest_groups = list(reversed(list(grouped.values())))[:60]

    def event_cell(group: list[dict[str, str]]) -> str:
        parts = [
            f'<span class="{EVENT_TONE.get(g["event"], "")}">{esc(EVENT_LABELS.get(g["event"], g["event"]))}</span>'
            for g in group
        ]
        return "<td>" + " · ".join(parts) + "</td>"

    event_rows = []
    for group in latest_groups:
        e = group[0]
        pct_values = [g["price_change_pct"] for g in group if g["price_change_pct"]]
        event_rows.append(
            [
                td(e["observed_at"][:16].replace("T", " ")),
                td(names.get(e["store_id"], e["store_id"])),
                f'<td class="wrap-cell"><a href="https://{esc(hosts.get(e["store_id"], ""))}/products/{esc(e["handle"])}"'
                f' rel="nofollow noopener">{esc(e["product_title"])}</a>'
                + (
                    f' <span class="quiet">{esc(e["variant_title"])}</span>'
                    if e["variant_title"] not in ("", "Default Title")
                    else ""
                )
                + "</td>",
                event_cell(group),
                td(usd(e["old_price_cents"]), num=True),
                td(usd(e["new_price_cents"]), num=True),
                td(f"{pct_values[0]}%" if pct_values else "", num=True),
            ]
        )
    events_table = (
        _table(
            f"Latest {len(event_rows)} changed variants (newest first).",
            [
                ("UTC", False),
                ("Store", False),
                ("Product", False),
                ("Event", False),
                ("Old", True),
                ("New", True),
                ("Change", True),
            ],
            event_rows,
            "Recent changes table",
        )
        if event_rows
        else '<p class="note">No changes recorded yet.</p>'
    )

    run_rows = [
        [
            td(r["started_at"][:16].replace("T", " ")),
            td(r["status"], cls="teal" if r["status"] == "ok" else "amber"),
            td(f"{r.get('duration_s', 0) / 60:.1f} min", num=True),
            td(f"{r.get('stores_ok', '-')}/{r.get('stores_total', '-')}", num=True),
            td(f"{r.get('rows_live', 0):,}", num=True),
            td(f"{sum((r.get('events') or {}).values()):,}", num=True),
        ]
        for r in list(reversed(runs))[:14]
    ]
    runs_table = (
        _table(
            "Most recent runs.",
            [
                ("Started UTC", False),
                ("Status", False),
                ("Duration", True),
                ("Stores", True),
                ("Variants", True),
                ("Changes", True),
            ],
            run_rows,
            "Runs table",
        )
        if run_rows
        else '<p class="note">No runs yet.</p>'
    )

    description = f"Daily price, discount and stock monitor for {len(stores)} US direct-to-consumer brands on Shopify."
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Shopify price monitor</title>
<meta name="description" content="{esc(description)}">
<meta name="theme-color" content="#0B1416">
<link rel="preload" href="fonts/instrument-sans-latin-400-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="fonts/ibm-plex-mono-latin-500-normal.woff2" as="font" type="font/woff2" crossorigin>
<style>{CSS}</style>
</head>
<body>
<div class="wrap">
<header>
<h1>Shopify price monitor</h1>
<p class="lede">{esc(description)} Prices, compare-at prices and stock are read once a day from each
store's public catalog, politely, and every change is logged.</p>
<p class="status" role="status">{pill}</p>
</header>
<main>
<h2 class="sr-only">Key figures</h2>
<ul class="kpis">{kpis}</ul>
<section class="panel" aria-labelledby="changes-h">
<h2 id="changes-h">Changes in the last good run <span class="quiet">({esc(when_good)})</span></h2>
<ul class="events">{event_items}</ul>
</section>
<section aria-labelledby="stores-h">
<h2 id="stores-h">Stores</h2>
{store_table}
</section>
<section aria-labelledby="recent-h">
<h2 id="recent-h">Recent changes</h2>
{events_table}
</section>
<section aria-labelledby="runs-h">
<h2 id="runs-h">Runs</h2>
{runs_table}
</section>
</main>
<footer>
<p class="note">Method: robots.txt respected, one store request every few seconds with jitter, one pace for the
whole run, Retry-After honoured, a store stops on any block page. Prices are checked against three witnesses
(catalog JSON, product JS, JSON-LD) and proven to be USD on every run; a run that looks wrong is held and the
last good data stays live.</p>
<p class="note">Data: <a href="{REPO_URL}/blob/main/data/latest/snapshot.csv">latest snapshot (CSV)</a>,
<a href="{REPO_URL}/tree/main/data/changes">daily change logs</a>,
<a href="{REPO_URL}/releases">monthly history (Parquet)</a>. Built {esc(now.strftime("%Y-%m-%d %H:%M UTC"))}.</p>
</footer>
</div>
</body>
</html>
"""


def build(data: Path, stores_path: Path, out: Path, now: datetime | None = None) -> Path:
    stores = load_stores(stores_path) if stores_path.exists() else []
    out.mkdir(parents=True, exist_ok=True)
    fonts = out / "fonts"
    fonts.mkdir(exist_ok=True)
    for f in (ASSETS / "fonts").iterdir():
        shutil.copy2(f, fonts / f.name)
    page = out / "index.html"
    page.write_text(render(data, stores, now or datetime.now(UTC)), encoding="utf-8")
    return page


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
    p.add_argument("--data", type=Path, default=Path("data"))
    p.add_argument("--stores", type=Path, default=Path("config/stores.yml"))
    p.add_argument("--out", type=Path, default=Path("site"))
    a = p.parse_args(argv)
    print(build(a.data, a.stores, a.out))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
