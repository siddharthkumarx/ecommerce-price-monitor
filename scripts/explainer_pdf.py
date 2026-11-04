"""Build docs/private/explainer.pdf from explainer.md (Markdown -> HTML -> Chromium PDF).

    uv run python scripts/explainer_pdf.py && node scripts/html_to_pdf.cjs \
        docs/private/explainer.html docs/private/explainer.pdf
"""

from __future__ import annotations

import base64
from pathlib import Path

import markdown

ROOT = Path(__file__).resolve().parents[1]
FONTS = ROOT / "src" / "pricemon" / "site_assets" / "fonts"


def font(name: str) -> str:
    return "data:font/woff2;base64," + base64.b64encode((FONTS / name).read_bytes()).decode()


def main() -> None:
    src = ROOT / "docs" / "private" / "explainer.md"
    body = markdown.markdown(src.read_text(encoding="utf-8"))
    css = f"""
    @font-face{{font-family:IS;font-weight:400;src:url({font("instrument-sans-latin-400-normal.woff2")})}}
    @font-face{{font-family:IS;font-weight:600;src:url({font("instrument-sans-latin-600-normal.woff2")})}}
    @page{{size:A4;margin:18mm 18mm 20mm}}
    body{{font:400 11pt/1.5 IS,sans-serif;color:#1b2a2d}}
    h1{{font-size:20pt;margin:0 0 6pt;color:#0B1416}}
    h2{{font-size:13pt;margin:16pt 0 4pt;color:#0B1416;
        border-bottom:1.5pt solid #2FBFAE;padding-bottom:2pt}}
    p,li{{margin:4pt 0}} code{{font-size:9.5pt}} strong{{color:#0B1416}}
    """
    head = f'<head><meta charset="utf-8"><style>{css}</style></head>'
    html = f'<!doctype html><html lang="en">{head}<body>{body}</body></html>'
    (ROOT / "docs" / "private" / "explainer.html").write_text(html, encoding="utf-8")


if __name__ == "__main__":
    main()
