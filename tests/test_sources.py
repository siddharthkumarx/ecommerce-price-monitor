from __future__ import annotations

from typing import Any

from pricemon.sources import classify, collect, render, render_stores_yml


def _row(
    store: str,
    category: str = "audio",
    *,
    passed: bool = True,
    variants: int | None = 100,
    country: str = "US",
    **extra: Any,
) -> dict[str, Any]:
    row: dict[str, Any] = {
        "store": store,
        "domain": f"{store.lower()}.example",
        "host": f"www.{store.lower()}.example",
        "category": category,
        "passed": passed,
        "fail_reasons": [] if passed else ["not shopify"],
        "robots_status": "ok",
        "robots_products_json": True,
        "robots_product_js": True,
        "robots_product_page": True,
        "crawl_delay_s": None,
        "reachable": True,
        "stopped_reason": None,
        "products": 50,
        "variants": variants,
        "variants_capped": False,
        "available_share": 0.5,
        "js_crosscheck": "match",
        "jsonld_currency": ["USD"],
        "shopify_currency": "USD",
        "meta_country": country,
        "retries": 0,
    }
    row.update(extra)
    return row


def _run(rid: str, *rows: dict[str, Any]) -> tuple[str, dict[str, Any]]:
    meta = {"id": rid, "finished_utc": "2026-11-03T00:00:00+00:00", "run_url": "https://x"}
    return (f"checks/results/{rid}/recon.json", {"meta": meta, "results": list(rows)})


def test_challenge_in_an_earlier_run_drops_the_store() -> None:
    sources = [
        _run("recon-001", _row("Alpha", stopped_reason="blocked: cloudflare challenge (http 429)")),
        _run("recon-002", _row("Alpha")),
    ]
    (rec,) = collect(sources)
    assert rec.drop_reasons() == ["recon-001: blocked: cloudflare challenge (http 429)"]


def test_unrecorded_retries_count_as_429_but_recorded_5xx_do_not() -> None:
    old = _row("Old", retries=1)
    new_5xx = _row("New", retries=1, retry_causes=["http 502"])
    new_429 = _row("Hot", retries=2, retry_causes=["http 429", "http 429"])
    records = {
        r.store: r for r in collect([_run("recon-003", old), _run("recon-004", new_5xx, new_429)])
    }
    assert records["Old"].drop_reasons() == [
        "recon-003: 1 retry (status not recorded, treated as 429)"
    ]
    assert records["New"].drop_reasons() == []
    assert records["Hot"].drop_reasons() == ["recon-004: 2 retries on 429"]


def test_robots_and_content_flags_drop() -> None:
    rows = [
        _row("Paged", robots_product_page=False),
        _row("Smoke", content_flags={"tobacco/vape": ["Mini Vape Pen"]}),
    ]
    records = {r.store: r for r in collect([_run("recon-004", *rows)])}
    assert records["Paged"].drop_reasons() == ["recon-004: robots.txt disallows /products/<handle>"]
    assert records["Smoke"].drop_reasons() == [
        "recon-004: excluded category tobacco/vape (e.g. Mini Vape Pen)"
    ]


def test_selection_prefers_us_then_larger_catalogs() -> None:
    rows = [
        _row("Big", variants=2000),
        _row("Small", variants=100),
        _row("Abroad", variants=50, country="CN"),
        _row("Gone", passed=False, variants=None),
    ]
    groups = classify(collect([_run("recon-004", *rows)]), per_category=2)
    assert [r.store for r in groups["selected"]] == ["Big", "Small"]
    assert [r.store for r in groups["reserve"]] == ["Abroad"]
    assert [r.store for r in groups["dropped"]] == ["Gone"]


def test_render_lists_selected_and_dropped_with_reasons() -> None:
    sources = [_run("recon-004", _row("Alpha"), _row("Beta", "outdoor", passed=False))]
    md = render(sources)
    assert "| Alpha | Audio |" in md
    assert "| Beta | Outdoor | `www.beta.example` | recon-004: not shopify |" in md


def test_stores_yml() -> None:
    yml = render_stores_yml([_run("recon-004", _row("Master & Dynamic"))])
    assert "  - id: master-dynamic\n" in yml
    assert '    name: "Master & Dynamic"\n' in yml


def test_reviewed_false_positive_does_not_drop_but_new_titles_do() -> None:
    from pricemon.sources import ScreenReview

    review = {
        "Shade": [
            ScreenReview(
                "Shade", "alcohol", frozenset({"Contour - Whiskey"}), "false_positive", "shade name"
            )
        ]
    }
    ok = _row("Shade", content_flags={"alcohol": ["Contour - Whiskey"]})
    (rec,) = collect([_run("recon-004", ok)], review)
    assert rec.drop_reasons() == []
    assert rec.reviewed_titles() == ["Contour - Whiskey"]
    yml = render_stores_yml([_run("recon-004", ok)], review)
    assert '    screen_reviewed: ["Contour - Whiskey"]' in yml

    new = _row("Shade", content_flags={"alcohol": ["Contour - Whiskey", "Bourbon Barrel"]})
    (rec,) = collect([_run("recon-005", new)], review)
    assert rec.drop_reasons()


def test_committed_review_file_loads() -> None:
    from pathlib import Path

    from pricemon.sources import load_reviews

    reviews = load_reviews(Path(__file__).resolve().parents[1] / "config" / "screen-review.yml")
    assert reviews
    assert all(
        r.verdict == "false_positive" and r.titles and r.reason for v in reviews.values() for r in v
    )


def test_trim_to_max_keeps_minimum_per_category_and_drops_weakest_first() -> None:
    from pricemon.sources import ScreenReview

    rows = [_row(f"A{i}", "audio", variants=100 + i) for i in range(5)]
    rows += [_row(f"O{i}", "outdoor", variants=500 + i) for i in range(5)]
    rows.append(_row("Themey", "outdoor", variants=9000, jsonld_currency=[]))
    review = {
        "Flagged": [ScreenReview("Flagged", "alcohol", frozenset({"x"}), "false_positive", "r")]
    }
    rows.append(_row("Flagged", "audio", variants=9000))
    groups = classify(collect([_run("recon-004", *rows)], review), max_stores=8)
    selected = {r.store for r in groups["selected"]}
    reserve = {r.store: r.reserve_reason for r in groups["reserve"]}
    assert len(selected) == 8
    assert {"Themey", "Flagged"} <= set(reserve)  # caveats go first, despite big catalogs
    assert sum(1 for r in groups["selected"] if r.category == "audio") >= 4
    assert sum(1 for r in groups["selected"] if r.category == "outdoor") >= 4
    assert all(reason and "trimmed to 8 stores" in reason for reason in reserve.values())
