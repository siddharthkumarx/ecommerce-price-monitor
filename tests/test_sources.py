from __future__ import annotations

from typing import Any

from pricemon.sources import merge, render, select


def _row(
    store: str, category: str, passed: bool, variants: int | None, country: str = "US"
) -> dict[str, Any]:
    return {
        "store": store,
        "domain": f"{store.lower()}.example",
        "host": f"www.{store.lower()}.example",
        "category": category,
        "passed": passed,
        "fail_reasons": [] if passed else ["blocked"],
        "robots_status": "ok",
        "robots_products_json": True,
        "robots_product_js": True,
        "crawl_delay_s": None,
        "reachable": passed,
        "stopped_reason": None if passed else "blocked: http 403",
        "variants": variants,
        "variants_capped": False,
        "available_share": 0.5 if passed else None,
        "js_crosscheck": "match" if passed else None,
        "jsonld_currency": ["USD"] if passed else [],
        "shopify_currency": "USD" if passed else None,
        "meta_country": country,
    }


def test_select_prefers_us_then_larger_catalogs() -> None:
    rows = [
        _row("Big", "audio", True, 2000),
        _row("Small", "audio", True, 100),
        _row("Abroad", "audio", True, 50, country="CN"),
        _row("Gone", "audio", False, None),
    ]
    status = select(rows, per_category=2)
    assert status == {
        "Small": "selected",
        "Big": "selected",
        "Abroad": "reserve",
        "Gone": "rejected",
    }


def test_render_contains_every_store() -> None:
    rows = [_row("Alpha", "audio", True, 120), _row("Beta", "outdoor", False, None)]
    meta = {"id": "recon-x", "finished_utc": "2026-11-03T00:00:00+00:00", "run_url": "https://x"}
    md = render([("checks/results/recon-x/recon.json", {"meta": meta, "results": rows})])
    assert "| Alpha | Audio |" in md
    assert "| Beta | Outdoor |" in md
    assert "rejected: blocked" in md


def test_merge_later_run_wins() -> None:
    first = {"meta": {"id": "r1"}, "results": [_row("Alpha", "audio", False, None)]}
    second = {"meta": {"id": "r2"}, "results": [_row("Alpha", "audio", True, 10)]}
    (row,) = merge([first, second])
    assert row["passed"]
    assert row["recon_id"] == "r2"
