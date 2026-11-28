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


def test_terms_come_from_the_latest_run_that_read_them_and_retired_stores_stay_out() -> None:
    from datetime import date

    from pricemon.stores import RetiredStore

    sources = [
        _run("recon-004", _row("Alpha"), _row("Beta"), _row("Gone")),
        _run(
            "recon-005",
            _row("Alpha", terms="ban", terms_source="read", terms_sentence="No robots."),
            _row("Gamma", category="pet", terms="no_ban", terms_source="read"),
        ),
    ]
    retired = [RetiredStore("gone", "Gone", "audio", date(2026, 11, 27))]
    records = {r.store: r for r in collect(sources)}
    assert records["Alpha"].terms == "ban"
    assert records["Beta"].terms == "none_found"  # never read
    assert records["Gamma"].terms == "no_ban"
    groups = classify(list(records.values()), retired={"Gone"}, min_per_category=0)
    assert [r.store for r in groups["retired"]] == ["Gone"]
    assert "Gone" not in {r.store for r in groups["selected"]}
    yml = render_stores_yml(sources, retired=retired)
    assert "    terms: no_ban\n" in yml
    assert "id: alpha" not in yml  # a ban is never listed (D-036)
    assert "retired:\n  - id: gone\n" in yml
    assert "## Retired" in render(sources, retired=retired)


def test_terms_rank_first_and_a_ban_is_never_selected() -> None:
    rows = [
        _row("Banned", terms="ban", variants=900),
        _row("Unknown", terms="none_found", variants=500),
        _row("Clean", terms="no_ban", variants=100),
        _row("Later", terms="none_found", variants=900),
    ]
    records = collect([_run("recon-005", *rows)])
    groups = classify(records, per_category=2, min_per_category=0)
    assert [r.store for r in groups["selected"]] == ["Clean", "Later"]
    assert [r.store for r in groups["reserve"]] == ["Unknown"]
    # Even with room, a store whose terms ban robots is dropped (D-036).
    wide = classify(collect([_run("recon-005", *rows)]), per_category=10)
    assert "Banned" not in {r.store for r in wide["selected"]}
    (banned,) = wide["dropped"]
    assert banned.drop_reasons() == ["recon-005: terms ban, not monitored (D-036)"]


def test_a_monitored_store_keeps_its_place_over_a_new_one_with_the_same_terms() -> None:
    rows = [
        _row("Incumbent", terms="none_found", variants=100),
        _row("Newcomer", terms="none_found", variants=900),
        _row("Clean", terms="no_ban", variants=50),
    ]
    records = collect([_run("recon-005", *rows)])
    plain = classify(records, per_category=2)
    assert [r.store for r in plain["selected"]] == ["Clean", "Newcomer"]
    kept = classify(collect([_run("recon-005", *rows)]), per_category=2, keep={"incumbent"})
    # Terms still rank first: the incumbent beats only a new store with the same terms.
    assert [r.store for r in kept["selected"]] == ["Clean", "Incumbent"]
    assert [r.store for r in kept["reserve"]] == ["Newcomer"]
    full = classify(
        collect([_run("recon-005", *rows)]), per_category=1, keep={"incumbent", "newcomer"}
    )
    assert [r.store for r in full["selected"]] == ["Clean"]


def test_a_newer_content_screen_supersedes_earlier_flags_but_not_its_own() -> None:
    flagged = {"alcohol": ["Juliska Graham Wine Coaster"]}
    old = _row("Kassa", content_flags=flagged)  # recon-006, screen v1 (no version field)
    clean = _row("Kassa", screen_version=2)
    (rec,) = collect([_run("recon-006", old), _run("recon-009", clean)])
    assert rec.drop_reasons() == []  # D-039: the v2 re-check read the catalog again
    real = _row("Kassa", screen_version=2, content_flags={"alcohol": ["Reserve Pinot Noir"]})
    (rec,) = collect([_run("recon-006", old), _run("recon-009", real)])
    assert rec.drop_reasons() == ["recon-009: excluded category alcohol (e.g. Reserve Pinot Noir)"]
    # A v2 flag stands even when a later v2 run is clean: any run with the same screen drops.
    (rec,) = collect([_run("recon-009", real), _run("recon-010", clean)])
    assert rec.drop_reasons() == ["recon-009: excluded category alcohol (e.g. Reserve Pinot Noir)"]
    # A row that did not read the catalog (no version) supersedes nothing.
    (rec,) = collect([_run("recon-006", old), _run("recon-009", _row("Kassa"))])
    assert rec.drop_reasons()


def _terms_run(rid: str, started: str, *rows: dict[str, Any]) -> tuple[str, dict[str, Any]]:
    meta = {"id": rid, "check": "terms", "started_utc": started}
    return (f"checks/results/{rid}/terms.json", {"meta": meta, "results": list(rows)})


def _terms_row(store: str, terms: str | None, **extra: Any) -> dict[str, Any]:
    row: dict[str, Any] = {
        "check": "terms",
        "store": store,
        "category": "audio",
        "terms": terms,
        "terms_source": "read" if terms in ("ban", "no_ban") else None,
        "terms_sentence": None,
        "retry_causes": [],
        "stopped_reason": None,
    }
    row.update(extra)
    return row


def test_a_terms_check_decides_terms_only(  # D-043
) -> None:
    recon = _run("recon-005", _row("Alpha", terms="no_ban", terms_source="read"))
    recon[1]["meta"]["started_utc"] = "2026-11-20T00:00:00+00:00"
    recon[1]["results"].append(_row("Beta", terms="no_ban", terms_source="read"))
    recon[1]["results"].append(_row("Gamma", terms="none_found", terms_source="http 404"))
    check = _terms_run(
        "terms-001",
        "2026-11-28T10:00:00+00:00",
        _terms_row("Alpha", "ban", terms_sentence="You agree not to: use any robot"),
        # A 429 while reading the terms: the terms stay as recon read them, and the
        # 429 does not drop a listed store (the drop rules read recon rows only).
        _terms_row("Beta", None, retry_causes=["http 429"], stopped_reason="http 429"),
        _terms_row("Gamma", "none_found"),
        _terms_row("Nobody", "no_ban"),  # not a candidate: ignored
    )
    # The check sorts before recon-005 by name, but ran after it.
    records = {r.store: r for r in collect([check, recon])}
    assert set(records) == {"Alpha", "Beta", "Gamma"}
    assert records["Alpha"].terms == "ban"
    assert records["Alpha"].drop_reasons() == ["terms-001: terms ban, not monitored (D-036)"]
    assert records["Alpha"].latest_id == "recon-005"
    assert records["Beta"].terms == "no_ban"
    assert records["Beta"].drop_reasons() == []
    assert records["Gamma"].terms == "none_found"


def _timed(rid: str, started: str, *rows: dict[str, Any]) -> tuple[str, dict[str, Any]]:
    path, payload = _run(rid, *rows)
    payload["meta"]["started_utc"] = started
    return path, payload


def test_a_429_drop_is_lifted_by_one_clean_retry_a_day_later() -> None:  # D-052
    hot = _row(
        "Hot",
        retries=3,
        retry_causes=["http 429"] * 3,
        stopped_reason=("retries exhausted: http 429"),
    )
    early = _timed("recon-010", "2026-11-28T10:00:00+00:00", _row("Hot"))
    late = _timed("recon-011", "2026-11-29T00:00:00+00:00", _row("Hot"))
    first = _timed("recon-007", "2026-11-27T20:30:00+00:00", hot)
    # Too early (13.5 hours): not the retry, the 429 still drops the store.
    (rec,) = collect([first, early])
    assert rec.drop_reasons() == [
        "recon-007: retries exhausted: http 429",
        "recon-007: 3 retries on 429",
    ]
    # At least 24 hours later and clean: lifted.
    (rec,) = collect([first, late])
    assert rec.drop_reasons() == []


def test_a_429_in_the_one_retry_keeps_the_store_out_for_good() -> None:  # D-052
    first = _timed("recon-004", "2026-11-10T00:00:00+00:00", _row("Hot", retry_causes=["http 429"]))
    again = _timed("recon-010", "2026-11-28T23:00:00+00:00", _row("Hot", retry_causes=["http 429"]))
    clean = _timed("recon-012", "2026-12-05T00:00:00+00:00", _row("Hot", retry_causes=[]))
    (rec,) = collect([first, again, clean])
    assert rec.drop_reasons() == [
        "recon-004: 1 retry on 429",
        "recon-010: 429 again in the one retry, out for good (D-052)",
        "recon-010: 1 retry on 429",
    ]


def test_a_challenge_is_not_lifted_by_a_retry() -> None:
    first = _timed(
        "recon-001",
        "2026-11-01T00:00:00+00:00",
        _row("Cf", stopped_reason="blocked: cloudflare challenge (http 429)"),
    )
    later = _timed("recon-010", "2026-11-28T23:00:00+00:00", _row("Cf"))
    (rec,) = collect([first, later])
    assert rec.drop_reasons() == ["recon-001: blocked: cloudflare challenge (http 429)"]


def test_an_owner_verdict_replaces_one_terms_reading_only() -> None:  # D-055
    from pricemon.sources import TermsVerdict

    recon = _timed("recon-005", "2026-11-20T00:00:00+00:00", _row("Pup", terms="no_ban"))
    ban = _terms_run("terms-001", "2026-11-28T10:00:00+00:00", _terms_row("Pup", "ban"))
    verdict = {"Pup": TermsVerdict("Pup", "terms-001", "no_ban", "2026-11-28", "read by hand")}
    (rec,) = collect([recon, ban], verdicts=verdict)
    assert rec.terms == "no_ban"
    assert rec.drop_reasons() == []
    assert "owner review of terms-001" in rec.terms_note()
    # A later reading that is a ban again decides, fail closed, until reviewed too.
    again = _terms_run("terms-003", "2026-12-28T10:00:00+00:00", _terms_row("Pup", "ban"))
    (rec,) = collect([recon, ban, again], verdicts=verdict)
    assert rec.terms == "ban"
    # Without the verdict the reading stands.
    (rec,) = collect([recon, ban])
    assert rec.terms == "ban"


def test_the_committed_terms_verdicts_load() -> None:
    from pathlib import Path

    from pricemon.sources import load_terms_verdicts

    verdicts = load_terms_verdicts(Path("config/terms-review.yml"))
    assert {v.store: (v.of, v.verdict) for v in verdicts.values()} == {
        "Pupford": ("terms-001", "no_ban"),
        "Paddletek": ("terms-001", "no_ban"),
    }
