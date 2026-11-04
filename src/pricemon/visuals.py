"""Animated SVG visuals for the README, generated from real run data.

    python -m pricemon.visuals --data data --stores config/stores.yml --out assets

Writes ``hero.svg``, ``pipeline.svg`` and ``maintenance-loop.svg``. Rules
(docs/decisions.md, D-022):

* An SVG in a README loads as an image: no external fonts or scripts. Fonts are
  embedded as base64 WOFF2 (the self-hosted Latin subsets of the dashboard).
* CSS animation only, a 9 s loop whose last 2.4 s hold the final frame. With no
  animation (still image, or ``prefers-reduced-motion``) the final frame shows.
* At most three lines of text per beat, at least 22 px in a 1000 px viewBox.
* Every number and row comes from the latest real run. A drawn illustration
  carries a small EXAMPLE label.
"""

from __future__ import annotations

import argparse
import base64
import html
import re
from datetime import UTC, datetime
from pathlib import Path

from pricemon.report import Facts, collect

ASSETS = Path(__file__).parent / "site_assets"
ICONS = Path(__file__).resolve().parents[2] / "assets" / "icons"

BG, PANEL, BORDER = "#0B1416", "#0F1C1E", "#1D3331"
TEXT, BODY, QUIET, TEAL, AMBER = "#EAF2F0", "#C9D8D5", "#7E9996", "#2FBFAE", "#E9A93C"
LOOP_S = 9

FONT_FILES = {
    ("IS", 400): "instrument-sans-latin-400-normal.woff2",
    ("IS", 600): "instrument-sans-latin-600-normal.woff2",
    ("PM", 500): "ibm-plex-mono-latin-500-normal.woff2",
}


def esc(text: object) -> str:
    return html.escape(str(text), quote=True)


def fonts_css(used: tuple[tuple[str, int], ...] = tuple(FONT_FILES)) -> str:
    rules = []
    for family, weight in used:
        data = (ASSETS / "fonts" / FONT_FILES[(family, weight)]).read_bytes()
        b64 = base64.b64encode(data).decode()
        rules.append(
            f"@font-face{{font-family:{family};font-weight:{weight};"
            f'src:url(data:font/woff2;base64,{b64}) format("woff2")}}'
        )
    return "".join(rules)


# Reduced motion: no animation at all, so every element shows its final-frame state.
REDUCED_MOTION = "@media (prefers-reduced-motion:reduce){*{animation:none!important}}"

BASE_CSS = f"""
.sans{{font-family:IS,"Instrument Sans",system-ui,sans-serif}}
.mono{{font-family:PM,"IBM Plex Mono",ui-monospace,monospace;font-weight:500}}
.t{{fill:{TEXT}}}.b{{fill:{BODY}}}.q{{fill:{QUIET}}}.teal{{fill:{TEAL}}}.amber{{fill:{AMBER}}}
.w6{{font-weight:600}}
"""


def keyframes(name: str, show: float, hide: float | None, fade: float = 3.0) -> str:
    """Opacity keyframes in percent of the loop: visible from ``show`` to ``hide``."""
    if hide is None:
        return (
            f"@keyframes {name}{{0%,{show:g}%{{opacity:0}}"
            f"{min(show + fade, 100):g}%,100%{{opacity:1}}}}"
        )
    return (
        f"@keyframes {name}{{0%,{show:g}%{{opacity:0}}{show + fade:g}%,{hide:g}%{{opacity:1}}"
        f"{hide + fade:g}%,100%{{opacity:0}}}}"
    )


def svg(width: int, height: int, title: str, desc: str, css: str, body: str) -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" '
        f'width="{width}" height="{height}" role="img" aria-labelledby="title desc">'
        f'<title id="title">{esc(title)}</title><desc id="desc">{esc(desc)}</desc>'
        f"<style>{fonts_css()}{BASE_CSS}{css}</style>"
        f'<rect width="{width}" height="{height}" rx="20" fill="{BG}"/>'
        f"{body}</svg>\n"
    )


def icon(name: str, x: float, y: float, size: float, cls: str = "b") -> str:
    """A Simple Icons glyph (24x24 path data, CC0) placed at x, y."""
    raw = (ICONS / f"{name}.svg").read_text()
    paths = re.findall(r'<path d="([^"]+)"', raw)
    scale = size / 24
    inner = "".join(f'<path d="{d}"/>' for d in paths)
    return f'<g class="{cls}" transform="translate({x:g} {y:g}) scale({scale:g})">{inner}</g>'


def clip(text: str, n: int) -> str:
    return text if len(text) <= n else text[: n - 1].rstrip() + "…"


def mono_width(chars: int, size: float) -> float:
    return chars * size * 0.6  # IBM Plex Mono advance is 600/1000 em


# -- hero ---------------------------------------------------------------------------
def hero(f: Facts, width: int = 1000, height: int = 460, scale: float = 1.0) -> str:
    """Three beats: the problem, the run with real rows, the result as one number."""
    s = scale
    cx = width / 2
    rows = f.sample[:3]
    stores = len(f.stores)
    prices = f"{f.snapshot_rows:,}"
    # Beat 1: the client's problem.
    b1 = (
        f'<g class="b1"><text class="sans t w6" x="{cx:g}" y="{height / 2 - 18 * s:g}" '
        f'font-size="{40 * s:g}" text-anchor="middle">Competitor prices change every day.</text>'
        f'<text class="sans b" x="{cx:g}" y="{height / 2 + 36 * s:g}" font-size="{30 * s:g}" '
        f'text-anchor="middle">Nobody can check them all by hand.</text></g>'
    )
    # Beat 2: the run, with real rows from the latest snapshot.
    top = height * 0.2
    src_w, src_h = 210 * s, 150 * s
    src_x, src_y = 40 * s, top + 40 * s
    beat2 = [
        f'<rect x="{src_x:g}" y="{src_y:g}" width="{src_w:g}" height="{src_h:g}" rx="{14 * s:g}" '
        f'fill="{PANEL}" stroke="{BORDER}" stroke-width="2"/>',
        icon("shopify", src_x + 24 * s, src_y + 24 * s, 44 * s, "teal"),
        f'<text class="mono t" x="{src_x + 24 * s:g}" y="{src_y + 108 * s:g}" '
        f'font-size="{30 * s:g}">{stores} stores</text>',
        f'<path class="flow" d="M{src_x + src_w + 10 * s:g} {src_y + src_h / 2:g} h{60 * s:g}" '
        f'stroke="{TEAL}" stroke-width="{4 * s:g}" stroke-linecap="round" fill="none"/>',
    ]
    tx = src_x + src_w + 90 * s
    tw = width - tx - 40 * s
    row_h = 58 * s
    fs = 22 * s
    max_chars = int(tw / (fs * 0.6))
    for i, r in enumerate(rows):
        y = top + 30 * s + i * row_h
        price = r.price + (f" -{r.discount_pct}%" if r.discount_pct else "")
        name_chars = max(8, max_chars - len(price) - 5)
        label = clip(f"{r.store} · {r.product}", name_chars)
        beat2.append(
            f'<g class="r{i + 1}"><rect x="{tx:g}" y="{y:g}" width="{tw:g}" height="{row_h - 10 * s:g}" '
            f'rx="{10 * s:g}" fill="{PANEL}" stroke="{BORDER}" stroke-width="2"/>'
            f'<text class="mono b" x="{tx + 16 * s:g}" y="{y + 31 * s:g}" font-size="{fs:g}">{esc(label)}</text>'
            f'<text class="mono {"amber" if r.discount_pct else "t"}" x="{tx + tw - 16 * s:g}" '
            f'y="{y + 31 * s:g}" font-size="{fs:g}" text-anchor="end">{esc(price)}</text></g>'
        )
    run_line = f"Run of {f.run_date}" if f.run else ""
    beat2.append(
        f'<text class="sans q" x="{tx:g}" y="{top + 30 * s + 3 * row_h + 26 * s:g}" '
        f'font-size="{22 * s:g}">{esc(run_line)} · real rows</text>'
    )
    b2 = f'<g class="b2">{"".join(beat2)}</g>'
    # Beat 3: one big number.
    b3 = (
        f'<g class="b3"><text class="mono teal" x="{cx:g}" y="{height / 2 + 4 * s:g}" '
        f'font-size="{92 * s:g}" text-anchor="middle">{prices} prices</text>'
        f'<text class="sans b" x="{cx:g}" y="{height / 2 + 62 * s:g}" font-size="{30 * s:g}" '
        f'text-anchor="middle">from {stores} US online stores, checked every day</text></g>'
    )
    css = (
        keyframes("k1", 0, 26)
        + keyframes("k2", 29, 66)
        + keyframes("kr1", 33, 66)
        + keyframes("kr2", 38, 66)
        + keyframes("kr3", 43, 66)
        + keyframes("k3", 70, None)
        + "@keyframes kf{0%,30%{stroke-dasharray:0 200}40%,100%{stroke-dasharray:200 0}}"
        # Default state = final frame (still image, no animation support).
        + ".b1,.b2{opacity:0}"
        + f".b1{{animation:k1 {LOOP_S}s infinite}}.b2{{animation:k2 {LOOP_S}s infinite}}"
        + f".r1{{animation:kr1 {LOOP_S}s infinite}}.r2{{animation:kr2 {LOOP_S}s infinite}}"
        + f".r3{{animation:kr3 {LOOP_S}s infinite}}.b3{{animation:k3 {LOOP_S}s infinite}}"
        + f".flow{{animation:kf {LOOP_S}s infinite}}"
        + REDUCED_MOTION
    )
    desc = (
        f"Competitor prices change every day. Each day one run reads {stores} US online stores; "
        f"the latest run recorded {prices} prices."
    )
    return svg(width, height, "Shopify price monitor", desc, css, b1 + b2 + b3)


def hero_square(f: Facts, size: int = 1080) -> str:
    """The hero as a square for social video: same beats, every text at least 40 px."""
    cx = size / 2
    stores = len(f.stores)
    b1 = (
        f'<g class="b1"><text class="sans t w6" x="{cx}" y="420" font-size="72" text-anchor="middle">'
        f'Competitor prices</text><text class="sans t w6" x="{cx}" y="510" font-size="72" '
        f'text-anchor="middle">change every day.</text><text class="sans b" x="{cx}" y="620" '
        f'font-size="48" text-anchor="middle">Nobody can check them all by hand.</text></g>'
    )
    parts = [
        f'<rect x="{cx - 230}" y="150" width="460" height="130" rx="20" fill="{PANEL}" '
        f'stroke="{BORDER}" stroke-width="3"/>',
        icon("shopify", cx - 200, 185, 60, "teal"),
        f'<text class="mono t" x="{cx - 120}" y="236" font-size="52">{stores} stores</text>',
        f'<path class="flow" d="M{cx} 300 v70" stroke="{TEAL}" stroke-width="6" '
        f'stroke-linecap="round" fill="none"/>',
    ]
    fs = 40
    for i, r in enumerate(f.sample[:3]):
        y = 400 + i * 130
        price = r.price + (f" -{r.discount_pct}%" if r.discount_pct else "")
        parts.append(
            f'<g class="r{i + 1}"><rect x="40" y="{y}" width="{size - 80}" height="110" rx="18" '
            f'fill="{PANEL}" stroke="{BORDER}" stroke-width="3"/>'
            f'<text class="mono b" x="70" y="{y + 48}" font-size="{fs}">{esc(clip(r.store, 36))}</text>'
            f'<text class="mono b" x="70" y="{y + 92}" font-size="{fs}">{esc(clip(r.product, 24))}</text>'
            f'<text class="mono {"amber" if r.discount_pct else "t"}" x="{size - 70}" y="{y + 92}" '
            f'font-size="{fs}" text-anchor="end">{esc(price)}</text></g>'
        )
    parts.append(
        f'<text class="sans q" x="{cx}" y="{400 + 3 * 130 + 40}" font-size="40" '
        f'text-anchor="middle">Real rows, run of {esc(f.run_date)}</text>'
    )
    b2 = f'<g class="b2">{"".join(parts)}</g>'
    b3 = (
        f'<g class="b3"><text class="mono teal" x="{cx}" y="470" font-size="150" '
        f'text-anchor="middle">{f.snapshot_rows:,}</text><text class="mono teal" x="{cx}" '
        f'y="580" font-size="80" text-anchor="middle">prices</text><text class="sans b" '
        f'x="{cx}" y="700" font-size="48" text-anchor="middle">from {stores} US online stores,'
        f'</text><text class="sans b" x="{cx}" y="770" font-size="48" text-anchor="middle">'
        f'checked every day</text><text class="sans q" x="{cx}" y="{size - 80}" font-size="40" '
        f'text-anchor="middle">siddharthkumar.com</text></g>'
    )
    css = (
        keyframes("k1", 0, 26)
        + keyframes("k2", 29, 66)
        + keyframes("kr1", 33, 66)
        + keyframes("kr2", 38, 66)
        + keyframes("kr3", 43, 66)
        + keyframes("k3", 70, None)
        + "@keyframes kf{0%,30%{stroke-dasharray:0 200}40%,100%{stroke-dasharray:200 0}}"
        + ".b1,.b2{opacity:0}"
        + f".b1{{animation:k1 {LOOP_S}s infinite}}.b2{{animation:k2 {LOOP_S}s infinite}}"
        + f".r1{{animation:kr1 {LOOP_S}s infinite}}.r2{{animation:kr2 {LOOP_S}s infinite}}"
        + f".r3{{animation:kr3 {LOOP_S}s infinite}}.b3{{animation:k3 {LOOP_S}s infinite}}"
        + f".flow{{animation:kf {LOOP_S}s infinite}}"
        + REDUCED_MOTION
    )
    desc = f"{f.snapshot_rows:,} prices from {stores} US online stores, checked every day."
    return svg(size, size, "Shopify price monitor", desc, css, b1 + b2 + b3)


# -- pipeline -------------------------------------------------------------------------
STAGES = (
    ("Stores", ("shopify",)),
    ("Collect", ("python", "githubactions")),
    ("Check", ("pydantic",)),
    ("Store", ("duckdb", "apacheparquet")),
    ("Deliver", ("googlesheets",)),
)


def pipeline(width: int = 1000, height: int = 320) -> str:
    n = len(STAGES)
    box_w, box_h = 150, 130
    gap = (width - 80 - n * box_w) / (n - 1)
    y = 110
    body = [
        '<text class="sans t w6" x="40" y="62" font-size="30">One run a day, from store page to '
        "your spreadsheet.</text>",
    ]
    for i in range(n - 1):
        x1 = 40 + (i + 1) * box_w + i * gap
        body.append(
            f'<path d="M{x1 + 6:g} {y + box_h / 2:g} h{gap - 12:g}" stroke="{BORDER}" '
            f'stroke-width="4" stroke-linecap="round"/>'
            f'<path class="c{i}" d="M{x1 + 6:g} {y + box_h / 2:g} h{gap - 12:g}" stroke="{TEAL}" '
            f'stroke-width="4" stroke-linecap="round"/>'
        )
    for i, (label, icons) in enumerate(STAGES):
        x = 40 + i * (box_w + gap)
        body.append(
            f'<g class="s{i}"><rect x="{x:g}" y="{y}" width="{box_w}" height="{box_h}" rx="16" '
            f'fill="{PANEL}" stroke="{BORDER}" stroke-width="2"/>'
            f'<rect class="lit" x="{x:g}" y="{y}" width="{box_w}" height="{box_h}" rx="16" '
            f'fill="none" stroke="{TEAL}" stroke-width="3"/>'
        )
        size = 40
        total = len(icons) * size + (len(icons) - 1) * 18
        ix = x + (box_w - total) / 2
        for name in icons:
            body.append(icon(name, ix, y + 26, size, "t"))
            ix += size + 18
        body.append(
            f'<text class="sans t" x="{x + box_w / 2:g}" y="{y + 106}" font-size="24" '
            f'text-anchor="middle">{label}</text></g>'
        )
    body.append(
        f'<text class="sans q" x="40" y="{height - 26}" font-size="22">'
        f"Python · GitHub Actions · Pydantic · DuckDB · Parquet · Google Sheets</text>"
    )
    css = []
    for i in range(n):
        start = 6 + i * 13
        css.append(
            keyframes(f"ks{i}", start, None, 4)
            + f".s{i} .lit{{animation:ks{i} {LOOP_S}s infinite}}"
        )
        if i < n - 1:
            css.append(
                f"@keyframes kc{i}{{0%,{start + 4:g}%{{stroke-dasharray:0 400}}"
                f"{start + 13:g}%,100%{{stroke-dasharray:400 0}}}}"
                f".c{i}{{animation:kc{i} {LOOP_S}s infinite}}"
            )
    css.append(REDUCED_MOTION)
    desc = (
        "Five steps: read public store catalogs, collect politely once a day, check every "
        "price against a second source, keep the full history, deliver CSV, Parquet, a Google "
        "Sheet and a dashboard."
    )
    return svg(width, height, "How the price monitor works", desc, "".join(css), "".join(body))


# -- maintenance loop -----------------------------------------------------------------
def maintenance(f: Facts, width: int = 1000, height: int = 380) -> str:
    """Daily runs, one real incident (INC-004), the fix, data keeps arriving."""
    runs_good = f.status.get("runs_good", 0)
    total = sum(1 for _ in range(14))
    xs = [80 + i * (width - 160) / (total - 1) for i in range(total)]
    y = 210
    incident = 5
    body = [
        f'<text class="sans q" x="{width - 40}" y="48" font-size="22" text-anchor="end">EXAMPLE</text>',
        f'<path d="M{xs[0]:g} {y} H{xs[-1]:g}" stroke="{BORDER}" stroke-width="4"/>',
    ]
    for i, x in enumerate(xs):
        start = 4 + i * 4.2
        cls = "amber" if i == incident else "teal"
        body.append(f'<circle class="d{i} {cls}" cx="{x:g}" cy="{y}" r="12"/>')
    ix = xs[incident]
    body += [
        f'<g class="inc"><path d="M{ix:g} {y - 20} V{y - 58}" stroke="{AMBER}" stroke-width="3"/>'
        f'<text class="sans t" x="40" y="{y - 72}" font-size="26">'
        f"Shopify asked the whole run to slow down.</text></g>",
        f'<g class="fix"><path d="M{xs[incident + 1]:g} {y + 20} V{y + 54}" stroke="{TEAL}" stroke-width="3"/>'
        f'<text class="sans t" x="40" y="{y + 92}" font-size="26">'
        f"Fixed: every store pauses together, then a gentler pace.</text></g>",
        f'<g class="num"><text class="mono teal" x="40" y="80" font-size="44">'
        f"{runs_good:,} daily run{'s' if runs_good != 1 else ''} delivered</text></g>",
    ]
    css = []
    for i in range(total):
        start = 4 + i * 4.2
        css.append(
            keyframes(f"kd{i}", start, None, 2) + f".d{i}{{animation:kd{i} {LOOP_S}s infinite}}"
        )
    inc_start = 4 + incident * 4.2
    css.append(
        keyframes("kinc", inc_start + 1, None, 3) + f".inc{{animation:kinc {LOOP_S}s infinite}}"
    )
    css.append(
        keyframes("kfix", inc_start + 9, None, 3) + f".fix{{animation:kfix {LOOP_S}s infinite}}"
    )
    css.append(keyframes("knum", 70, None, 4) + f".num{{animation:knum {LOOP_S}s infinite}}")
    css.append(REDUCED_MOTION)
    desc = (
        "Example timeline of daily runs. One real incident: Shopify asked the whole run to slow "
        f"down; the fix pauses every store together. Daily runs delivered so far: {runs_good}."
    )
    return svg(width, height, "What broke and how it was fixed", desc, "".join(css), "".join(body))


def write_all(data: Path, stores: Path, out: Path, now: datetime | None = None) -> list[Path]:
    f = collect(data, stores, now or datetime.now(UTC))
    out.mkdir(parents=True, exist_ok=True)
    files = {
        "hero.svg": hero(f),
        "pipeline.svg": pipeline(),
        "maintenance-loop.svg": maintenance(f),
    }
    written = []
    for name, content in files.items():
        path = out / name
        path.write_text(content, encoding="utf-8")
        written.append(path)
    return written


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
    p.add_argument("--data", type=Path, default=Path("data"))
    p.add_argument("--stores", type=Path, default=Path("config/stores.yml"))
    p.add_argument("--out", type=Path, default=Path("assets"))
    a = p.parse_args(argv)
    for path in write_all(a.data, a.stores, a.out):
        print(f"{path} {path.stat().st_size / 1024:.0f} KiB")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
