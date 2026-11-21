"""Build the static dashboard into ``site/`` from the committed data.

    python -m pricemon.site --data data --stores config/stores.yml --out site

No JavaScript, no external requests: one HTML file with inline CSS, two
self-hosted font families (OFL): Plus Jakarta Sans (text, tabular numbers) and IBM
Plex Mono (run IDs), and the SteadyData icon set. The daily charts are plain HTML
and CSS bars with direct labels and their numbers in a table. Every number on the page is read from
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
from typing import Any

from pricemon.feed import daily
from pricemon.outputs import (
    build_status,
    on_time_text,
    parse_iso,
    read_runs,
    recent_events,
    snapshot_summary,
)
from pricemon.schedule import slot_states
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
    "discount_start": "Sale started",
    "discount_end": "Sale ended",
    "out_of_stock": "Sold out",
    "back_in_stock": "Back in stock",
    "new": "New",
    "removed": "Removed",
}
# good (#0E8A7D) = price drops, sales starting, back in stock; look (#D98E14) = price
# rises, sales ending, sold out. Colour is never the only cue: every mark has a label.
EVENT_TONE = {
    "price_down": "good",
    "price_up": "look",
    "discount_start": "good",
    "discount_end": "look",
    "out_of_stock": "look",
    "back_in_stock": "good",
    "new": "",
    "removed": "",
}
REPO_URL = "https://github.com/siddharthkumarx/ecommerce-price-monitor"
STEADYDATA_CONTACT = "https://steadydata.co/contact/"
AUTHOR_LINKS = (
    ("steadydata.co", "https://steadydata.co"),
    ("siddharthkumar.com", "https://siddharthkumar.com"),
)

CSS = (ASSETS / "style.css").read_text(encoding="utf-8")
# The SteadyData mark, the same icon set as steadydata.co (site_assets/icons/ is copied
# from that site's repo, not edited here).
MARK = (
    '<svg viewBox="10 7 44 50" width="24" height="28" aria-hidden="true" focusable="false">'
    '<defs><linearGradient id="sdm" x1="49" x2="15" y1="12" y2="52" gradientUnits="userSpaceOnUse">'
    '<stop offset="0" stop-color="#1A9486"/><stop offset="1" stop-color="#5FE8D6"/></linearGradient>'
    '</defs><path fill="none" stroke="url(#sdm)" stroke-linejoin="round" stroke-width="8" '
    'd="M41 14H22l-6.5 6.5v5L22 32h20l6.5 6.5v5L42 50H23"/><path fill="#D98E14" '
    'fill-rule="evenodd" d="M40.4 14a6.6 6.6 0 1 0 13.2 0 6.6 6.6 0 1 0-13.2 0m4.1 0a2.5 2.5 0 1 1 '
    '5 0 2.5 2.5 0 1 1-5 0"/><path fill="#5FE8D6" fill-rule="evenodd" d="M10.4 50a6.6 6.6 0 1 0 '
    '13.2 0 6.6 6.6 0 1 0-13.2 0m4.1 0a2.5 2.5 0 1 1 5 0 2.5 2.5 0 1 1-5 0"/></svg>'
)
ICON_LINKS = (
    '<link rel="icon" href="favicon.ico" sizes="32x32">\n'
    '<link rel="icon" href="icon.svg" type="image/svg+xml">\n'
    '<link rel="apple-touch-icon" href="apple-touch-icon.png">\n'
    '<link rel="manifest" href="site.webmanifest">'
)


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def usd(cents: object) -> str:
    if cents in (None, ""):
        return ""
    return f"${int(str(cents)) / 100:,.2f}"


def pct(part: int, whole: int) -> str:
    if not whole:
        return "-"
    share = part / whole
    if 0 < share < 0.01:
        return "<1%"
    if 0.99 < share < 1:
        return ">99%"
    return f"{share:.0%}"


def day_label(date: str) -> str:
    """'2026-11-17' -> '17 Nov'."""
    return datetime.strptime(date, "%Y-%m-%d").strftime("%-d %b")


def when_label(ts: str) -> str:
    """'2026-11-20T15:30:59Z' -> '20 Nov 2026, 15:30 UTC'."""
    return parse_iso(ts).strftime("%-d %b %Y, %H:%M UTC")


def _kpi(label: str, value: str, sub: str = "", small: bool = False) -> str:
    cls = "value small" if small else "value"
    sub_html = f'<span class="sub">{esc(sub)}</span>' if sub else ""
    return (
        f'<li class="card kpi"><span class="label">{esc(label)}</span>'
        f'<span class="{cls}">{esc(value)}</span>{sub_html}</li>'
    )


def _table(caption: str, head: list[tuple[str, bool]], rows: list[list[str]], label: str) -> str:
    def th(h: str, num: bool) -> str:
        classes = " ".join(
            c for c in ("num" if num else "", "hide-sm" if h == "Category" else "") if c
        )
        return (
            f'<th scope="col" class="{classes}">{esc(h)}</th>'
            if classes
            else f'<th scope="col">{esc(h)}</th>'
        )

    ths = "".join(th(h, num) for h, num in head)
    body = "".join("<tr>" + "".join(r) + "</tr>" for r in rows)
    return (
        f'<div class="scroll" role="region" aria-label="{esc(label)}" tabindex="0">'
        f"<table><caption>{esc(caption)}</caption><thead><tr>{ths}</tr></thead>"
        f"<tbody>{body}</tbody></table></div>"
    )


def td(value: object, num: bool = False, cls: str = "") -> str:
    classes = " ".join(c for c in ("num" if num else "", cls) if c)
    return f'<td class="{classes}">{esc(value)}</td>' if classes else f"<td>{esc(value)}</td>"


def tag(text: str, tone: str) -> str:
    return (
        f'<span class="tag"><span class="dot {tone}" aria-hidden="true"></span>{esc(text)}</span>'
    )


def _half(
    rows: list[dict[str, Any]], key: str, label: str, tone: str, top: float, direction: str
) -> str:
    """One side of a diverging bar chart, with its direct series label and value labels."""
    values = [int(r[key]) for r in rows]
    n = len(values)
    peak = max(range(n), key=lambda i: (values[i], i)) if n else -1
    labelled = {peak} if n and values[peak] else set()
    if n and values[-1] and (n - 1 - peak) >= 3:
        labelled.add(n - 1)
    cols = []
    for i, (r, v) in enumerate(zip(rows, values, strict=True)):
        h = 0.0 if not top else 100 * v / top
        title = f"{day_label(r['date'])}: {v:,} {label.lower()}"
        val = ""
        if i in labelled:
            edge = " start" if i < 2 else (" end" if i > n - 3 else "")
            val = f'<span class="val{edge}" aria-hidden="true">{v:,}</span>'
        cols.append(
            f'<span class="col" style="--h:{h:.1f}%;--i:{i}" title="{esc(title)}">'
            f'<span class="bar {tone}{" nz" if v else ""}"></span>{val}</span>'
        )
    arrow = "↑" if direction == "up" else "↓"
    series = (
        f'<span class="series"><span class="swatch {tone}" aria-hidden="true"></span>'
        f"{esc(label)} {arrow}</span>"
    )
    return f'<div class="half {direction}" aria-hidden="true">{series}{"".join(cols)}</div>'


def chart(
    cid: str,
    title: str,
    rows: list[dict[str, Any]],
    up: tuple[str, str, str],
    down: tuple[str, str, str],
) -> str:
    """A diverging daily bar chart (HTML and CSS, no script) with its numbers as a table.

    ``up`` and ``down`` are (key, label, tone). Both halves share one scale.
    """
    if not rows:
        return (
            f'<figure class="card chart" aria-labelledby="{cid}-h"><h3 id="{cid}-h">'
            f'{esc(title)}</h3><p class="takeaway">Shown from the second run on: the first run '
            "is the starting point.</p></figure>"
        )
    top = max(max(int(r[up[0]]) for r in rows), max(int(r[down[0]]) for r in rows), 1)
    last = rows[-1]

    def busiest(key: str) -> dict[str, Any]:
        return max(rows, key=lambda r: (int(r[key]), r["date"]))

    b_up, b_down = busiest(up[0]), busiest(down[0])
    takeaway = (
        f"{esc(day_label(last['date']))}: <b>{int(last[up[0]]):,} {esc(up[1].lower())}</b>, "
        f"<b>{int(last[down[0]]):,} {esc(down[1].lower())}</b>. Most in one day: "
        f"{int(b_up[up[0]]):,} {esc(up[1].lower())} ({esc(day_label(b_up['date']))}), "
        f"{int(b_down[down[0]]):,} {esc(down[1].lower())} ({esc(day_label(b_down['date']))})."
    )
    first, final = day_label(rows[0]["date"]), day_label(last["date"])
    table_rows = [
        [
            td(day_label(r["date"])),
            td(f"{int(r[up[0]]):,}", num=True),
            td(f"{int(r[down[0]]):,}", num=True),
        ]
        for r in reversed(rows)
    ]
    numbers = _table(
        f"{title}, newest first.",
        [("Day (UTC)", False), (up[1], True), (down[1], True)],
        table_rows,
        f"{title}: numbers by day",
    )
    return (
        f'<figure class="card chart" aria-labelledby="{cid}-h">'
        f'<h3 id="{cid}-h">{esc(title)}</h3><p class="takeaway">{takeaway}</p>'
        f'<div class="plot">{_half(rows, up[0], up[1], up[2], top, "up")}<div class="axis"></div>'
        f"{_half(rows, down[0], down[1], down[2], top, 'down')}</div>"
        f'<div class="xlabels" aria-hidden="true"><span>{esc(first)}</span>'
        f"<span>{esc(final)}</span></div>"
        f"<details><summary>Numbers by day</summary>{numbers}</details></figure>"
    )


def render(data: Path, stores: list[Store], now: datetime) -> str:
    runs = read_runs(data)
    status = build_status(runs, now)
    schedule = status.get("schedule") or {}
    summary = {s["store_id"]: s for s in snapshot_summary(data / "latest" / "snapshot.csv")}
    events = recent_events(data)
    last = status["last_run"]
    good_runs = [r for r in runs if r["status"] in ("ok", "partial")]
    last_good = good_runs[-1] if good_runs else None
    per_day = daily(runs)
    states = {s.run_id: s.state for s in slot_states(runs, now) if s.run_id}

    variants = sum(int(s["variants"]) for s in summary.values())
    in_stock = sum(int(s["in_stock"]) for s in summary.values())
    discounted = sum(int(s["discounted"]) for s in summary.values())

    if last:
        tone = "good" if last["status"] == "ok" else "look"
        pill = (
            f'<span class="dot {tone}" aria-hidden="true"></span>Latest run '
            f"{esc(when_label(last['started_at']))}: {esc(last['status'])}"
        )
    else:
        pill = '<span class="dot" aria-hidden="true"></span>No runs yet'

    first_run = status.get("first_run")
    slots_n = int(schedule.get("slots", 0))
    kpis = "".join(
        [
            _kpi(
                "Latest run",
                when_label(last["started_at"]) if last else "none yet",
                (
                    f"{last['status']} · {last.get('stores_ok', 0)} of "
                    f"{last.get('stores_total', 0)} stores · "
                    f"{(last.get('duration_s') or 0) / 60:.1f} min"
                )
                if last
                else "",
                small=True,
            ),
            _kpi("Prices live", f"{variants:,}", f"product options in {len(stores)} stores"),
            _kpi("In stock", pct(in_stock, variants), f"{in_stock:,} of {variants:,}"),
            _kpi("On sale", pct(discounted, variants), "below their “was” price"),
            _kpi(
                "Daily runs delivered",
                f"{schedule.get('delivered', 0)} of {slots_n}" if slots_n else "-",
                "{}: {}".format(*on_time_text(schedule)),
            ),
            _kpi(
                "Days running",
                str(status["days_running"]),
                f"since {parse_iso(first_run).strftime('%-d %b %Y')}" if first_run else "",
            ),
        ]
    )

    counts = (last_good or {}).get("events") or {}
    event_items = "".join(
        f'<li><span class="name"><span class="mark {EVENT_TONE[k] if counts.get(k) else ""}" '
        f'aria-hidden="true"></span>{esc(EVENT_LABELS[k])}</span>'
        f"<b>{int(counts.get(k, 0)):,}</b></li>"
        for k in EVENT_LABELS
    )
    when_good = when_label(last_good["started_at"]) if last_good else "no run yet"

    charts = "".join(
        [
            chart(
                "c-price",
                "Price drops and rises per day",
                per_day,
                ("price_up", "Price rises", "look"),
                ("price_down", "Price drops", "good"),
            ),
            chart(
                "c-sale",
                "Sales started and ended per day",
                per_day,
                ("discount_start", "Sales started", "good"),
                ("discount_end", "Sales ended", "look"),
            ),
            chart(
                "c-stock",
                "Stock changes per day",
                per_day,
                ("back_in_stock", "Back in stock", "good"),
                ("out_of_stock", "Sold out", "look"),
            ),
        ]
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
                    td(CATEGORY_TITLES[cat], cls="hide-sm"),
                    td(f"{v:,}", num=True),
                    td(pct(int(agg.get("in_stock", 0)), v), num=True),
                    td(pct(int(agg.get("discounted", 0)), v), num=True),
                    td(
                        f"{agg['avg_discount_pct']}%"
                        if agg.get("avg_discount_pct") is not None
                        else "-",
                        num=True,
                    ),
                    td(usd(agg.get("median_price_cents")), num=True),
                    "<td>"
                    + (
                        tag(state["status"], "look")
                        if state
                        else (tag("updated", "good") if last else "-")
                    )
                    + "</td>",
                ]
            )
    store_table = _table(
        "Live snapshot per store. On sale: a “was” (compare-at) price above the price.",
        [
            ("Store", False),
            ("Category", False),
            ("Options", True),
            ("In stock", True),
            ("On sale", True),
            ("Avg discount", True),
            ("Median price", True),
            ("Latest run", False),
        ],
        store_rows,
        "Stores table",
    )

    names = {s.id: s.name for s in stores}
    hosts = {s.id: s.host for s in stores}
    # One row per variant and run: a sale is "Price down · Sale started".
    grouped: dict[tuple[str, str, str], list[dict[str, str]]] = {}
    for e in events:
        grouped.setdefault((e["observed_at"], e["store_id"], e["variant_id"]), []).append(e)
    latest_groups = list(reversed(list(grouped.values())))[:60]

    def event_cell(group: list[dict[str, str]]) -> str:
        parts = [
            f'<span class="tag"><span class="mark {EVENT_TONE.get(g["event"], "")}" '
            f'aria-hidden="true"></span>{esc(EVENT_LABELS.get(g["event"], g["event"]))}</span>'
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
                    f' <span class="muted">{esc(e["variant_title"])}</span>'
                    if e["variant_title"] not in ("", "Default Title")
                    else ""
                )
                + "</td>",
                event_cell(group),
                td(usd(e["old_price_cents"]), num=True),
                td(usd(e["new_price_cents"]), num=True),
                td(f"{float(pct_values[0]):+.1f}%" if pct_values else "", num=True),
            ]
        )
    events_table = (
        _table(
            f"Latest {len(event_rows)} changed product options, newest first.",
            [
                ("UTC", False),
                ("Store", False),
                ("Product", False),
                ("What changed", False),
                ("Before", True),
                ("Now", True),
                ("Change", True),
            ],
            event_rows,
            "Recent changes table",
        )
        if event_rows
        else '<p class="note">No changes recorded yet.</p>'
    )

    state_words = {"on_time": "on time", "late": "late", "held": "held"}
    run_rows = []
    for r in list(reversed(runs))[:14]:
        run_id = esc(r["run_id"])
        id_cell = (
            f'<td><a class="mono" href="{esc(r["run_url"])}" rel="noopener">{run_id}</a></td>'
            if r.get("run_url")
            else f'<td class="mono">{run_id}</td>'
        )
        run_rows.append(
            [
                td(r["started_at"][:16].replace("T", " ")),
                "<td>" + tag(r["status"], "good" if r["status"] == "ok" else "look") + "</td>",
                td(state_words.get(states.get(r["run_id"], ""), "extra run")),
                td(f"{(r.get('duration_s') or 0) / 60:.1f} min", num=True),
                td(f"{r.get('stores_ok', '-')}/{r.get('stores_total', '-')}", num=True),
                td(f"{r.get('rows_live', 0):,}", num=True),
                td(f"{sum((r.get('events') or {}).values()):,}", num=True),
                id_cell,
            ]
        )
    runs_table = (
        _table(
            "Most recent runs. On time: started within 2 hours of its scheduled slot. "
            + str(schedule.get("note") or ""),
            [
                ("Started UTC", False),
                ("Status", False),
                ("Slot", False),
                ("Duration", True),
                ("Stores", True),
                ("Prices live", True),
                ("Changes", True),
                ("Run ID", False),
            ],
            run_rows,
            "Runs table",
        )
        if run_rows
        else '<p class="note">No runs yet.</p>'
    )

    author = " · ".join(f'<a href="{u}">{esc(t)}</a>' for t, u in AUTHOR_LINKS)
    description = (
        f"Daily price, sale and stock monitor for {len(stores)} US direct-to-consumer brands "
        "on Shopify."
    )
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Shopify price monitor</title>
<meta name="description" content="{esc(description)}">
<meta name="theme-color" content="#FFFFFF">
{ICON_LINKS}
<link rel="preload" href="fonts/plus-jakarta-sans-latin-400-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="fonts/plus-jakarta-sans-latin-700-normal.woff2" as="font" type="font/woff2" crossorigin>
<style>{CSS}</style>
</head>
<body>
<div class="wrap">
<div class="topbar">
<a class="brand" href="{REPO_URL}">{MARK}<span>Shopify price monitor</span></a>
<span class="by">Built by SteadyData · <a href="{STEADYDATA_CONTACT}">Get a free sample</a></span>
</div>
<header class="hero">
<h1>Every price, sale and stock change from {len(stores)} US online stores</h1>
<p class="lede">{esc(description)} Each run reads every store's public catalog, politely, checks
the prices against a second source and logs every change.</p>
<p class="status" role="status">{pill}</p>
</header>
<main>
<h2 class="sr-only">Key figures</h2>
<ul class="kpis">{kpis}</ul>
</main>
</div>
<div class="band">
<section class="wrap" aria-labelledby="trend-h">
<h2 id="trend-h">What changed, day by day</h2>
<p class="section-lede">Counts of changes found by each day's runs (UTC). The first run is the
starting point and is not counted.</p>
<div class="charts">{charts}</div>
</section>
</div>
<div class="wrap">
<section aria-labelledby="changes-h">
<h2 id="changes-h">Changes in the latest good run</h2>
<p class="section-lede muted">{esc(when_good)}</p>
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
<section aria-labelledby="cta-h">
<div class="card cta">
<div><h2 id="cta-h">Want this for your own stores?</h2>
<p>A free sample from your target sites first, then a fixed monthly price.</p></div>
<a class="button" href="{STEADYDATA_CONTACT}">Get a free sample</a>
</div>
</section>
</div>
<footer>
<div class="wrap">
<p class="note">Method: robots.txt respected, one store request every few seconds with jitter, one pace for
the whole run, Retry-After honoured, a store stops on any block page. Every day one product per store is
re-read from two more sources (its product JS and the page's JSON-LD), and every run proves the prices are in
US dollars; a run that looks wrong is held and the last good data stays live.</p>
<p class="note">Data: <a href="{REPO_URL}/blob/main/data/latest/snapshot.csv">latest snapshot (CSV)</a>,
<a href="{REPO_URL}/tree/main/data/changes">daily change logs</a>,
<a href="{REPO_URL}/releases">monthly history (Parquet)</a>,
<a href="{REPO_URL}/blob/main/data/public/feed.json">public feed (JSON)</a>. Built {esc(now.strftime("%Y-%m-%d %H:%M UTC"))}.</p>
<p class="author">Built and maintained by Siddharth Kumar, founder of SteadyData · {author}</p>
</div>
</footer>
</body>
</html>
"""


def build(data: Path, stores_path: Path, out: Path, now: datetime | None = None) -> Path:
    stores = load_stores(stores_path) if stores_path.exists() else []
    out.mkdir(parents=True, exist_ok=True)
    fonts = out / "fonts"
    fonts.mkdir(exist_ok=True)
    for f in (ASSETS / "fonts").iterdir():
        if f.name.startswith(("plus-jakarta-sans", "ibm-plex-mono-latin-400", "OFL")):
            shutil.copy2(f, fonts / f.name)
    for f in (ASSETS / "icons").iterdir():
        shutil.copy2(f, out / f.name)
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
