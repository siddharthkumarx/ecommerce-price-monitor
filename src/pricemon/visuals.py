"""Animated SVG visuals for the README, generated from real run data.

    python -m pricemon.visuals --data data --stores config/stores.yml --out assets

Writes ``hero.svg``, ``pipeline.svg`` and ``maintenance-loop.svg``, and a still
copy of each (``*-still.svg``, the final frame, no animation). Rules
(docs/decisions.md, D-022 and D-025):

* An SVG in a README loads as an image: no external fonts or scripts. Fonts are
  embedded as base64 WOFF2 (the self-hosted Latin subsets of the dashboard).
* CSS animation only, a 9 s loop whose last 2.4 s hold the final frame.
* Every element's final-frame state is its default style, so a renderer without
  animation shows the result. Under ``prefers-reduced-motion`` the animations stop
  and the final-state styles are forced with ``!important``. Browsers do not pass
  the viewer's motion preference into an SVG loaded as ``<img>``, so the README
  also switches to the still copy with ``<picture><source media=...>``.
* Text readable on a phone: in the 1000 px viewBox, headings at least 36 px and
  row text at least 30 px (the small EXAMPLE label excepted). At most three lines
  of text per beat.
* Every number and row comes from the latest real run. A drawn illustration
  carries a small EXAMPLE label.
"""

from __future__ import annotations

import argparse
import base64
import html
import re
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

from pricemon.report import Facts, collect

ASSETS = Path(__file__).parent / "site_assets"
ICONS = Path(__file__).resolve().parents[2] / "assets" / "icons"

BG, PANEL, BORDER = "#0B1416", "#0F1C1E", "#1D3331"
TEXT, BODY, QUIET, TEAL, AMBER = "#EAF2F0", "#C9D8D5", "#7E9996", "#2FBFAE", "#E9A93C"
LOOP_S = 9
MIN_HEADING_PX = 36
MIN_TEXT_PX = 30

FONT_FILES = {
    ("IS", 400): "instrument-sans-latin-400-normal.woff2",
    ("IS", 600): "instrument-sans-latin-600-normal.woff2",
    ("PM", 500): "ibm-plex-mono-latin-500-normal.woff2",
}

BASE_CSS = f"""
.sans{{font-family:IS,"Instrument Sans",system-ui,sans-serif}}
.mono{{font-family:PM,"IBM Plex Mono",ui-monospace,monospace;font-weight:500}}
.t{{fill:{TEXT}}}.b{{fill:{BODY}}}.q{{fill:{QUIET}}}.teal{{fill:{TEAL}}}.amber{{fill:{AMBER}}}
.w6{{font-weight:600}}
"""


@dataclass(frozen=True)
class Visual:
    """One drawing: its markup, its animation, and the styles of its final frame."""

    width: int
    height: int
    title: str
    desc: str
    body: str
    animation: str
    final: str  # declarations that describe the final frame, e.g. ".b1{opacity:0}"

    def render(self, animated: bool = True) -> str:
        css = BASE_CSS + self.final  # the default state IS the final frame
        if animated:
            forced = re.sub(r"([^;{}]+:[^;{}]+)(?=[;}])", r"\1!important", self.final)
            css += (
                self.animation
                + "@media (prefers-reduced-motion:reduce){*{animation:none!important}"
                + forced
                + "}"
            )
        return (
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {self.width} {self.height}" '
            f'width="{self.width}" height="{self.height}" role="img" '
            f'aria-labelledby="title desc">'
            f'<title id="title">{esc(self.title)}</title><desc id="desc">{esc(self.desc)}</desc>'
            f"<style>{fonts_css()}{css}</style>"
            f'<rect width="{self.width}" height="{self.height}" rx="20" fill="{BG}"/>'
            f"{self.body}</svg>\n"
        )


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


def animate(selector: str, name: str) -> str:
    return f"{selector}{{animation:{name} {LOOP_S}s infinite}}"


def icon(name: str, x: float, y: float, size: float, cls: str = "b") -> str:
    """A Simple Icons glyph (24x24 path data, CC0) placed at x, y."""
    raw = (ICONS / f"{name}.svg").read_text()
    paths = re.findall(r'<path d="([^"]+)"', raw)
    scale = size / 24
    inner = "".join(f'<path d="{d}"/>' for d in paths)
    return f'<g class="{cls}" transform="translate({x:g} {y:g}) scale({scale:g})">{inner}</g>'


def clip(text: str, n: int) -> str:
    return text if len(text) <= n else text[: n - 1].rstrip() + "…"


def short(text: str, n: int) -> str:
    """The first whole words of ``text`` that fit in ``n`` characters."""
    words = text.split()
    kept: list[str] = []
    for word in words:
        if len(" ".join([*kept, word])) > n:
            break
        kept.append(word)
    # Never end on a connector ("All Day &", "Cup with").
    while kept and kept[-1].lower() in {"&", "-", "+", "·", "and", "with", "of", "for", "the"}:
        kept.pop()
    return " ".join(kept) or clip(text, n)


def row_label(store: str, product: str, chars: int) -> str:
    """'Store · short product' in at most ``chars`` characters."""
    store = clip(store, max(6, chars // 2))
    room = chars - len(store) - 3
    return f"{store} · {short(product, room)}" if room >= 4 else store


HERO_ANIMATION = (
    keyframes("k1", 0, 26)
    + keyframes("k2", 29, 66)
    + keyframes("kr1", 33, 66)
    + keyframes("kr2", 38, 66)
    + keyframes("kr3", 43, 66)
    + keyframes("k3", 70, None)
    + "@keyframes kf{0%,30%{stroke-dasharray:0 400}40%,100%{stroke-dasharray:400 0}}"
    + animate(".b1", "k1")
    + animate(".b2", "k2")
    + animate(".r1", "kr1")
    + animate(".r2", "kr2")
    + animate(".r3", "kr3")
    + animate(".b3", "k3")
    + animate(".flow", "kf")
)
HERO_FINAL = ".b1{opacity:0}.b2{opacity:0}.b3{opacity:1}.flow{stroke-dasharray:none}"


# -- hero ---------------------------------------------------------------------------
def hero(f: Facts, width: int = 1000, height: int = 460) -> Visual:
    """Three beats: the problem, the run with real rows, the result as one number."""
    cx = width / 2
    stores = len(f.stores)
    b1 = (
        f'<g class="b1"><text class="sans t w6" x="{cx:g}" y="214" font-size="48" '
        f'text-anchor="middle">Competitor prices change every day.</text>'
        f'<text class="sans b" x="{cx:g}" y="276" font-size="36" text-anchor="middle">'
        f"Nobody can check them all by hand.</text></g>"
    )
    beat2 = [
        f'<rect x="40" y="120" width="250" height="170" rx="16" fill="{PANEL}" '
        f'stroke="{BORDER}" stroke-width="2"/>',
        icon("shopify", 64, 144, 48, "teal"),
        f'<text class="mono t" x="64" y="252" font-size="36">{stores} stores</text>',
        f'<path class="flow" d="M304 205 h52" stroke="{TEAL}" stroke-width="5" '
        f'stroke-linecap="round" fill="none"/>',
    ]
    tx, tw, fs = 370, width - 370 - 40, MIN_TEXT_PX
    chars = int((tw - 48) / (fs * 0.6))
    for i, r in enumerate(f.sample[:3]):
        y = 96 + i * 82
        label = row_label(r.store, r.product, chars - len(r.price) - 2)
        beat2.append(
            f'<g class="r{i + 1}"><rect x="{tx}" y="{y}" width="{tw}" height="68" rx="12" '
            f'fill="{PANEL}" stroke="{BORDER}" stroke-width="2"/>'
            f'<text class="mono b" x="{tx + 24}" y="{y + 44}" font-size="{fs}">{esc(label)}</text>'
            f'<text class="mono {"amber" if r.discount_pct else "t"}" x="{tx + tw - 24}" '
            f'y="{y + 44}" font-size="{fs}" text-anchor="end">{esc(r.price)}</text></g>'
        )
    beat2.append(
        f'<text class="sans q" x="{tx}" y="380" font-size="{fs}">'
        f"Real rows, run of {esc(f.run_date)}</text>"
    )
    b2 = f'<g class="b2">{"".join(beat2)}</g>'
    b3 = (
        f'<g class="b3"><text class="mono teal" x="{cx:g}" y="248" font-size="110" '
        f'text-anchor="middle">{f.snapshot_rows:,} prices</text>'
        f'<text class="sans b" x="{cx:g}" y="318" font-size="36" text-anchor="middle">'
        f"from {stores} US online stores, checked every day</text></g>"
    )
    desc = (
        f"Competitor prices change every day. Each day one run reads {stores} US online stores; "
        f"the latest run recorded {f.snapshot_rows:,} prices."
    )
    return Visual(
        width, height, "Shopify price monitor", desc, b1 + b2 + b3, HERO_ANIMATION, HERO_FINAL
    )


def hero_square(f: Facts, size: int = 1080) -> Visual:
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
    fs = 44
    for i, r in enumerate(f.sample[:3]):
        y = 400 + i * 130
        parts.append(
            f'<g class="r{i + 1}"><rect x="40" y="{y}" width="{size - 80}" height="110" rx="18" '
            f'fill="{PANEL}" stroke="{BORDER}" stroke-width="3"/>'
            f'<text class="mono b" x="70" y="{y + 50}" font-size="{fs}">{esc(clip(r.store, 34))}</text>'
            f'<text class="mono b" x="70" y="{y + 96}" font-size="{fs}">{esc(short(r.product, 22))}</text>'
            f'<text class="mono {"amber" if r.discount_pct else "t"}" x="{size - 70}" y="{y + 96}" '
            f'font-size="{fs}" text-anchor="end">{esc(r.price)}</text></g>'
        )
    parts.append(
        f'<text class="sans q" x="{cx}" y="{400 + 3 * 130 + 44}" font-size="40" '
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
    desc = f"{f.snapshot_rows:,} prices from {stores} US online stores, checked every day."
    return Visual(
        size, size, "Shopify price monitor", desc, b1 + b2 + b3, HERO_ANIMATION, HERO_FINAL
    )


# -- pipeline -------------------------------------------------------------------------
STAGES = (
    ("Stores", ("shopify",)),
    ("Collect", ("python", "githubactions")),
    ("Check", ("pydantic",)),
    ("Store", ("duckdb", "apacheparquet")),
    ("Deliver", ("googlesheets",)),
)


def pipeline(width: int = 1000, height: int = 340) -> Visual:
    n = len(STAGES)
    box_w, box_h = 156, 140
    gap = (width - 80 - n * box_w) / (n - 1)
    y = 108
    body = [
        '<text class="sans t w6" x="40" y="68" font-size="36">One run a day, from store page '
        "to your spreadsheet.</text>",
    ]
    for i in range(n - 1):
        x1 = 40 + (i + 1) * box_w + i * gap
        body.append(
            f'<path d="M{x1 + 6:g} {y + box_h / 2:g} h{gap - 12:g}" stroke="{BORDER}" '
            f'stroke-width="4" stroke-linecap="round"/>'
            f'<path class="conn c{i}" d="M{x1 + 6:g} {y + box_h / 2:g} h{gap - 12:g}" '
            f'stroke="{TEAL}" stroke-width="4" stroke-linecap="round"/>'
        )
    for i, (label, icons) in enumerate(STAGES):
        x = 40 + i * (box_w + gap)
        body.append(
            f'<g class="s{i}"><rect x="{x:g}" y="{y}" width="{box_w}" height="{box_h}" rx="16" '
            f'fill="{PANEL}" stroke="{BORDER}" stroke-width="2"/>'
            f'<rect class="lit" x="{x:g}" y="{y}" width="{box_w}" height="{box_h}" rx="16" '
            f'fill="none" stroke="{TEAL}" stroke-width="3"/>'
        )
        size = 44
        total = len(icons) * size + (len(icons) - 1) * 16
        ix = x + (box_w - total) / 2
        for name in icons:
            body.append(icon(name, ix, y + 22, size, "t"))
            ix += size + 16
        body.append(
            f'<text class="sans t" x="{x + box_w / 2:g}" y="{y + 114}" font-size="{MIN_TEXT_PX}" '
            f'text-anchor="middle">{label}</text></g>'
        )
    body.append(
        f'<text class="sans q" x="40" y="{height - 30}" font-size="{MIN_TEXT_PX}">'
        "Python · Actions · Pydantic · DuckDB · Parquet · Sheets</text>"
    )
    animation = []
    for i in range(n):
        start = 6 + i * 13
        animation.append(keyframes(f"ks{i}", start, None, 4) + animate(f".s{i} .lit", f"ks{i}"))
        if i < n - 1:
            animation.append(
                f"@keyframes kc{i}{{0%,{start + 4:g}%{{stroke-dasharray:0 400}}"
                f"{start + 13:g}%,100%{{stroke-dasharray:400 0}}}}" + animate(f".c{i}", f"kc{i}")
            )
    desc = (
        "Five steps: read public store catalogs, collect politely once a day, check every "
        "price against a second source, keep the full history, deliver CSV, Parquet, a Google "
        "Sheet and a dashboard."
    )
    final = ".lit{opacity:1}.conn{stroke-dasharray:none}"
    return Visual(
        width, height, "How the price monitor works", desc, "".join(body), "".join(animation), final
    )


# -- maintenance loop -----------------------------------------------------------------
def maintenance(f: Facts, width: int = 1000, height: int = 390) -> Visual:
    """Daily runs, one real incident (INC-004), the fix, data keeps arriving."""
    runs_good = f.status.get("runs_good", 0)
    total = 14
    xs = [80 + i * (width - 160) / (total - 1) for i in range(total)]
    y = 226
    incident = 5
    body = [
        f'<text class="sans q" x="{width - 40}" y="48" font-size="22" text-anchor="end">EXAMPLE</text>',
        f'<path d="M{xs[0]:g} {y} H{xs[-1]:g}" stroke="{BORDER}" stroke-width="4"/>',
    ]
    for i, x in enumerate(xs):
        cls = "amber" if i == incident else "teal"
        body.append(f'<circle class="dot d{i} {cls}" cx="{x:g}" cy="{y}" r="13"/>')
    ix = xs[incident]
    body += [
        f'<g class="inc"><path d="M{ix:g} {y - 22} V{y - 50}" stroke="{AMBER}" stroke-width="3"/>'
        f'<text class="sans t" x="40" y="{y - 64}" font-size="32">'
        "Shopify asked the whole run to slow down.</text></g>",
        f'<g class="fix"><path d="M{xs[incident + 1]:g} {y + 22} V{y + 52}" stroke="{TEAL}" '
        f'stroke-width="3"/><text class="sans t" x="40" y="{y + 94}" font-size="32">'
        "Fixed: every store pauses together, then a gentler pace.</text></g>",
        f'<g class="num"><text class="mono teal" x="40" y="88" font-size="52">'
        f"{runs_good:,} daily run{'s' if runs_good != 1 else ''} delivered</text></g>",
    ]
    animation = []
    for i in range(total):
        start = 4 + i * 4.2
        animation.append(keyframes(f"kd{i}", start, None, 2) + animate(f".d{i}", f"kd{i}"))
    inc_start = 4 + incident * 4.2
    animation.append(keyframes("kinc", inc_start + 1, None, 3) + animate(".inc", "kinc"))
    animation.append(keyframes("kfix", inc_start + 9, None, 3) + animate(".fix", "kfix"))
    animation.append(keyframes("knum", 70, None, 4) + animate(".num", "knum"))
    desc = (
        "Example timeline of daily runs. One real incident: Shopify asked the whole run to slow "
        f"down; the fix pauses every store together. Daily runs delivered so far: {runs_good}."
    )
    final = ".dot{opacity:1}.inc{opacity:1}.fix{opacity:1}.num{opacity:1}"
    return Visual(
        width,
        height,
        "What broke and how it was fixed",
        desc,
        "".join(body),
        "".join(animation),
        final,
    )


def write_all(data: Path, stores: Path, out: Path, now: datetime | None = None) -> list[Path]:
    """Write each visual animated (``name.svg``) and as its final frame (``name-still.svg``)."""
    f = collect(data, stores, now or datetime.now(UTC))
    out.mkdir(parents=True, exist_ok=True)
    visuals = {"hero": hero(f), "pipeline": pipeline(), "maintenance-loop": maintenance(f)}
    written = []
    for name, visual in visuals.items():
        for suffix, animated in (("", True), ("-still", False)):
            path = out / f"{name}{suffix}.svg"
            path.write_text(visual.render(animated), encoding="utf-8")
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
