"""The 100-store expansion (D-032): platforms, second read on big moves, canary
warm-up, daily summary kept forever and the 30-day raw window."""

from __future__ import annotations

import asyncio
import csv
import json
import time
from collections.abc import Callable
from datetime import UTC, date, datetime, timedelta
from pathlib import Path
from typing import Any

import httpx
import pytest

from pricemon import platforms, warmup
from pricemon.fetch import PLACEHOLDER_CENTS, StoreFetch, fetch_store, second_reads
from pricemon.normalize import normalize_products
from pricemon.polite import PoliteConfig
from pricemon.run import RunConfig, process
from pricemon.stores import Store, load_stores, product_url
from pricemon.summary import COLUMNS, build_rows, prune_raw, refresh
from tests.fakes import session_for
from tests.test_outputs import catalog, fetched

DAY = date(2026, 11, 23)
ROBOTS = "User-agent: *\nDisallow: /cart\n"
JSON = {"content-type": "application/json"}


def at(d: int, hour: int = 6, minute: int = 17) -> datetime:
    return datetime(2026, 11, d, hour, minute, tzinfo=UTC)


# -- stores and links -------------------------------------------------------------


def test_product_url_per_platform() -> None:
    assert product_url("a.example", "tee", "shopify") == "https://a.example/products/tee"
    assert (
        product_url("b.example", "product/tee", "woocommerce") == "https://b.example/product/tee/"
    )
    assert product_url("c.example", "gear/tee", "bigcommerce") == "https://c.example/gear/tee/"
    assert product_url("", "tee") == ""


def test_load_stores_reads_platform_and_rejects_unknown(tmp_path: Path) -> None:
    p = tmp_path / "stores.yml"
    p.write_text(
        "stores:\n"
        "  - {id: a, name: A, category: pets, host: a.example}\n"
        "  - {id: b, name: B, category: pets, host: b.example, platform: woocommerce}\n"
    )
    a, b = load_stores(p)
    assert (a.platform, b.platform) == ("shopify", "woocommerce")
    p.write_text("stores:\n  - {id: a, name: A, category: pets, host: a.example, platform: x}\n")
    with pytest.raises(ValueError, match="unknown platform"):
        load_stores(p)


# -- WooCommerce ------------------------------------------------------------------


def woo_item(pid: int, price: str, regular: str, stock: bool = True, **kw: Any) -> dict[str, Any]:
    return {
        "id": pid,
        "name": kw.get("name", f"Item {pid}"),
        "type": kw.get("type", "simple"),
        "parent": kw.get("parent", 0),
        "variation": kw.get("variation", ""),
        "permalink": f"https://w.example/product/item-{pid}/",
        "is_in_stock": stock,
        "categories": [{"name": "Bottles"}],
        "tags": [],
        "prices": {
            "price": price,
            "regular_price": regular,
            "currency_code": "USD",
            "currency_minor_unit": 2,
        },
    }


PARENTS = [
    woo_item(1, "1899", "1899"),
    woo_item(2, "0", "0", type="variable", name="Bottle &amp; Cap"),
    woo_item(3, "500", "500", type="external"),
]
VARIATIONS = [
    woo_item(21, "2400", "3000", parent=2, type="variation", variation="Colour: Blue"),
    woo_item(22, "2400", "2400", False, parent=2, type="variation", variation="Colour: Red"),
]


def woo_shop(
    parents: list[dict[str, Any]] = PARENTS, variations: list[dict[str, Any]] = VARIATIONS
) -> Callable[[httpx.Request], httpx.Response]:
    def handler(request: httpx.Request) -> httpx.Response:
        path, q = request.url.path, request.url.params
        if path == "/robots.txt":
            return httpx.Response(200, text=ROBOTS)
        if path == platforms.WOO_PATH:
            if q.get("type") == "variation":
                items = [
                    v for v in variations if not q.get("parent") or str(v["parent"]) == q["parent"]
                ]
            else:
                items = parents
            return httpx.Response(200, json=items, headers={"x-wp-totalpages": "1", **JSON})
        if path.startswith(platforms.WOO_PATH + "/"):
            pid = int(path.rsplit("/", 1)[1])
            item = next((i for i in parents + variations if i["id"] == pid), None)
            return httpx.Response(200, json=item) if item else httpx.Response(404)
        if path.startswith("/product/"):
            pid = int(path.strip("/").rsplit("-", 1)[1])
            item = next(i for i in parents if i["id"] == pid)
            price = int(item["prices"]["price"]) / 100
            ld = {
                "@type": "Product",
                "offers": [
                    {
                        "@type": "Offer",
                        "priceSpecification": {"price": f"{price:.2f}", "priceCurrency": "USD"},
                    }
                ],
            }
            return httpx.Response(
                200, text=f'<script type="application/ld+json">{json.dumps(ld)}</script>'
            )
        return httpx.Response(404)

    return handler


def run_store(
    store: Store,
    handler: Callable[[httpx.Request], httpx.Response],
    prev: dict[int, int] | None = None,
) -> tuple[StoreFetch, list[httpx.Request]]:
    session, _, seen = session_for(
        handler, base_url=store.base_url, config=PoliteConfig(delay_s=1, jitter_s=0)
    )
    return asyncio.run(fetch_store(session, store, DAY, prev)), seen


def test_woocommerce_catalog_one_row_per_variation_and_usd() -> None:
    store = Store("w", "W", "outdoor", "w.example", platform="woocommerce")
    f, _ = run_store(store, woo_shop())
    assert f.status == "ok", f.reason
    assert f.currencies == {"USD"}
    rows, stats = normalize_products("w", f.products, f.observed_at)
    by_id = {r.variant_id: r for r in rows}
    assert set(by_id) == {1, 21, 22}  # external product left out, variable parent split
    assert by_id[21].compare_at_cents == 3000
    assert by_id[21].price_cents == 2400
    assert by_id[22].availability == "out_of_stock"
    assert by_id[21].product_title == "Bottle & Cap"
    assert by_id[21].variant_title == "Colour: Blue"
    assert by_id[1].handle == "product/item-1"
    assert stats.rejected == 0


def test_woocommerce_witness_reread_mismatch_marks_store() -> None:
    store = Store("w", "W", "outdoor", "w.example", platform="woocommerce")
    parents = [woo_item(1, "1899", "1899")]
    base = woo_shop(parents, [])

    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == f"{platforms.WOO_PATH}/1":
            return httpx.Response(200, json=woo_item(1, "2099", "2099"))
        return base(request)

    f, _ = run_store(store, handler)
    assert f.status == "mismatch"


def test_minor_units_to_cents() -> None:
    assert platforms.minor_to_cents("1899", 2) == 1899
    assert platforms.minor_to_cents("19", 0) == 1900
    assert platforms.minor_to_cents("18990", 3) == 1899
    assert platforms.minor_to_cents("18995", 3) is None  # not a whole cent
    assert platforms.minor_to_cents("", 2) is None


# -- BigCommerce ------------------------------------------------------------------


def bc_page(
    pid: int, ld: str, data: float, stock: bool = True, sale_from: float | None = None
) -> str:
    ldj = {
        "@type": "Product",
        "name": f"Bike {pid}",
        "offers": {
            "@type": "Offer",
            "priceCurrency": "USD",
            "price": ld,
            "availability": "https://schema.org/InStock"
            if stock
            else "https://schema.org/OutOfStock",
        },
    }
    price: dict[str, Any] = {"without_tax": {"value": data, "currency": "USD"}}
    if sale_from:
        price["non_sale_price_without_tax"] = {"value": sale_from}
    bc = {"product_attributes": {"price": price, "instock": stock}}
    return (
        f'<script type="application/ld+json">{json.dumps(ldj)}</script>'
        f'<input type="hidden" name="product_id" value="{pid}">'
        f"<script>var BCData = {json.dumps(bc)};</script>"
    )


def bc_shop(pages: dict[str, str]) -> Callable[[httpx.Request], httpx.Response]:
    def handler(request: httpx.Request) -> httpx.Response:
        path = request.url.path
        if path == "/robots.txt":
            return httpx.Response(200, text=ROBOTS)
        if path == platforms.BC_SITEMAP:
            if request.url.params["page"] != "1":
                return httpx.Response(404)
            locs = "".join(f"<url><loc>https://b.example/{p}/</loc></url>" for p in pages)
            return httpx.Response(200, text=f"<urlset>{locs}</urlset>")
        key = path.strip("/")
        return httpx.Response(200, text=pages[key]) if key in pages else httpx.Response(404)

    return handler


def test_bigcommerce_two_sources_per_page_and_held_back_disagreement() -> None:
    store = Store("b", "B", "bikes", "b.example", platform="bigcommerce")
    pages = {
        "bike-1": bc_page(1, "120.00", 120.0, sale_from=150.0),
        "bike-2": bc_page(2, "80.00", 80.0, stock=False),
        "bike-3": bc_page(3, "99.00", 90.0),  # JSON-LD and theme disagree
    }
    f, _ = run_store(store, bc_shop(pages))
    assert f.status in ("ok", "mismatch")
    rows, _ = normalize_products("b", f.products, f.observed_at)
    by_id = {r.variant_id: r for r in rows}
    assert by_id[1].price_cents == 12000
    assert by_id[1].compare_at_cents == 15000
    assert by_id[2].availability == "out_of_stock"
    assert f.held_variants == {3: "second source: JSON-LD 9900 vs theme 9000 cents"}
    assert f.currencies == {"USD"}


# -- second read on big moves -----------------------------------------------------


def shopify_product(price: str) -> dict[str, Any]:
    return {
        "id": 7,
        "handle": "lamp",
        "title": "Lamp",
        "product_type": "",
        "tags": [],
        "variants": [
            {
                "id": 70,
                "title": "Default Title",
                "price": price,
                "compare_at_price": None,
                "available": True,
            }
        ],
    }


def reread_with(js_price: int | None) -> Any:
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/robots.txt":
            return httpx.Response(200, text=ROBOTS)
        if js_price is None:
            return httpx.Response(404)
        return httpx.Response(200, json={"variants": [{"id": 70, "price": js_price}]})

    session, _, seen = session_for(handler, config=PoliteConfig(delay_s=1, jitter_s=0))
    asyncio.run(session.load_robots())
    return session, seen


def test_big_move_confirmed_by_second_read_is_kept() -> None:
    store = Store("s", "S", "audio", "shop.example")
    session, seen = reread_with(900)
    out = fetched("s", [shopify_product("9.00")], at(23))
    asyncio.run(second_reads(session, store, out, {70: 10000}))
    assert out.held_variants == {}
    assert out.second_reads[0]["verdict"] == "confirmed"
    assert seen[-1].url.path == "/products/lamp.js"


def test_big_move_not_confirmed_is_held_back_and_keeps_last_price(tmp_path: Path) -> None:
    store = Store("s", "S", "audio", "shop.example")
    session, _ = reread_with(None)
    out = fetched("s", [shopify_product("9.00")], at(23))
    asyncio.run(second_reads(session, store, out, {70: 10000}))
    assert out.held_variants == {70: "big move: second read did not confirm"}
    # Through the pipeline: the row keeps $100.00, no price event, counted as held.
    cfg = RunConfig(stores=tmp_path / "stores.yml", data=tmp_path / "data")
    process(cfg, [fetched("s", [shopify_product("100.00")], at(22))], at(22), time.monotonic())
    _code, rec = process(cfg, [out], at(23), time.monotonic())
    assert rec["events"].get("price_down", 0) == 0
    assert rec["rows_held_back"] == 1
    snap = list(csv.DictReader((cfg.data / "latest" / "snapshot.csv").open()))
    assert snap[0]["price_cents"] == "10000"


def test_placeholder_price_is_always_held_back() -> None:
    store = Store("s", "S", "audio", "shop.example")
    session, seen = reread_with(999999999)
    out = fetched("s", [shopify_product(f"{PLACEHOLDER_CENTS / 100:.2f}")], at(23))
    n = len(seen)
    asyncio.run(second_reads(session, store, out, {70: 7999}))
    assert out.held_variants == {70: "placeholder price"}
    assert len(seen) == n  # no request needed


def test_normal_moves_need_no_second_read() -> None:
    store = Store("s", "S", "audio", "shop.example")
    session, seen = reread_with(900)
    out = fetched("s", [shopify_product("80.00")], at(23))
    n = len(seen)
    asyncio.run(second_reads(session, store, out, {70: 10000}))
    assert out.second_reads == []
    assert len(seen) == n


# -- canary warm-up ---------------------------------------------------------------


def test_new_store_warms_up_three_clean_days_then_counts_without_new_events(
    tmp_path: Path,
) -> None:
    cfg = RunConfig(stores=tmp_path / "stores.yml", data=tmp_path / "data")
    # Day 1: the monitor's first run, every store is the baseline.
    process(cfg, [fetched("a", catalog(30), at(20))], at(20), time.monotonic())
    records = []
    for d in (21, 22, 23):
        _code, rec = process(
            cfg,
            [fetched("a", catalog(30), at(d)), fetched("n", catalog(12), at(d))],
            at(d),
            time.monotonic(),
        )
        records.append(rec)
    d21, d22, d23 = records
    for rec in (d21, d22):
        assert rec["stores_total"] == 1
        assert rec["stores_warming"] == 1
        assert rec["rows_live"] == 30
        assert rec["warming"][0]["clean"]
        assert not rec["warming"][0]["promoted"]
    assert [r["warming"][0]["streak"] for r in records] == [1, 2, 3]
    assert d23["stores_promoted"] == ["n"]
    assert d23["stores_total"] == 2
    assert d23["rows_live"] == 42
    assert d23["events"].get("new", 0) == 0  # baseline, not 12 new products
    feed = json.loads((cfg.data / "public" / "feed.json").read_text())
    assert feed["monitor"]["stores_total"] == 2


def test_warming_failure_resets_streak_and_never_makes_a_run_partial(tmp_path: Path) -> None:
    cfg = RunConfig(stores=tmp_path / "stores.yml", data=tmp_path / "data")
    process(cfg, [fetched("a", catalog(30), at(19))], at(19), time.monotonic())
    process(
        cfg,
        [fetched("a", catalog(30), at(20)), fetched("n", catalog(5), at(20))],
        at(20),
        time.monotonic(),
    )
    code, rec = process(
        cfg,
        [fetched("a", catalog(30), at(21)), fetched("n", [], at(21), status="failed")],
        at(21),
        time.monotonic(),
    )
    assert code == 0
    assert rec["status"] == "ok"
    assert rec["warming"][0]["clean"] is False
    assert rec["warming"][0]["streak"] == 0
    assert "failed" in rec["warming"][0]["why"]
    state = json.loads((cfg.data / "warmup.json").read_text())
    assert list(state["warming"]) == ["n"]
    assert warmup.public_stores([Store("n", "N", "pets", "n.example")], cfg.data) == []


def test_streak_needs_consecutive_dates() -> None:
    runs = [
        {"started_at": "2026-11-20T06:17:00Z", "warming": [{"store_id": "n", "clean": True}]},
        {"started_at": "2026-11-22T06:17:00Z", "warming": [{"store_id": "n", "clean": True}]},
    ]
    assert warmup.streak("n", runs, date(2026, 11, 23), True) == 2  # 21 Nov missing
    assert warmup.streak("n", runs, date(2026, 11, 23), False) == 0


def test_judge_flags_429_rejects_and_row_drop() -> None:
    runs = [
        {
            "started_at": "2026-11-22T06:17:00Z",
            "warming": [{"store_id": "n", "clean": True, "rows": 100}],
        }
    ]
    ok = warmup.judge("n", "ok", None, 90, 0, [], {"USD"}, runs)
    assert ok.clean
    bad = warmup.judge("n", "ok", None, 40, 5, ["http 429"], {"USD"}, runs)
    assert not bad.clean
    assert "429" in bad.why
    assert "rejected" in bad.why
    assert "fell" in bad.why


# -- daily summary and raw window -------------------------------------------------


def run_rec(d: int, status: str = "ok", **kw: Any) -> dict[str, Any]:
    return {
        "run_id": f"202611{d:02d}T061700Z",
        "started_at": f"2026-11-{d:02d}T06:17:30Z",
        "status": status,
        "stores_total": 25,
        "stores_ok": 25,
        "rows_live": 1000 + d,
        "rows_observed": 1000,
        "rows_rejected": kw.get("rejected", 0),
        "events": {
            "price_down": d,
            "price_up": 1,
            "discount_start": 2,
            "out_of_stock": 3,
            "back_in_stock": 4,
        },
        "stores": kw.get("stores", []),
    }


def test_summary_from_runs_since_5_nov(tmp_path: Path) -> None:
    runs = [run_rec(4), run_rec(5), run_rec(6, rejected=3), run_rec(7, "held")]
    rows = build_rows(runs, datetime(2026, 11, 9, 1, 0, tzinfo=UTC))  # 8 Nov has ended
    assert sorted(rows) == ["2026-11-05", "2026-11-06", "2026-11-07", "2026-11-08"]
    r5, r6, r7, r8 = (rows[d] for d in sorted(rows))
    assert (r5["stores_counted"], r5["prices"], r5["price_drops"]) == (25, 1005, 5)
    assert (r5["delivered"], r5["on_time"], r5["rows_held"]) == ("yes", "yes", 0)
    assert r6["rows_held"] == 3
    assert r7["delivered"] == "no"
    assert r7["rows_held"] == 1000
    assert r7["prices"] == ""
    assert r8["runs_due"] == 1
    assert r8["delivered"] == "no"
    assert set(r5) == set(COLUMNS)


def test_summary_keeps_rows_no_longer_in_the_log(tmp_path: Path) -> None:
    data = tmp_path / "data"
    (data / "history").mkdir(parents=True)
    old = dict.fromkeys(COLUMNS, "")
    old.update(
        date="2026-11-05",
        prices="999",
        delivered="yes",
        on_time="no",
        runs_due="1",
        runs_delivered="1",
    )
    with (data / "history" / "daily-summary.csv").open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=COLUMNS)
        w.writeheader()
        w.writerow(old)
    (data / "runs.jsonl").write_text(json.dumps(run_rec(6)) + "\n")
    rows = refresh(data, datetime(2026, 11, 6, 12, 0, tzinfo=UTC))
    assert [r["date"] for r in rows] == ["2026-11-05", "2026-11-06"]
    assert rows[0]["prices"] == "999"
    doc = json.loads((data / "public" / "history.json").read_text())
    assert doc["schema"] == "steadydata.history/v1"
    assert doc["delivery"]["runs_due"] == 2
    assert doc["delivery"]["runs_delivered"] == 2
    assert doc["days"][1][0] == "2026-11-06"


def test_prune_keeps_30_days_of_raw_change_logs(tmp_path: Path) -> None:
    data = tmp_path / "data"
    today = date(2026, 12, 20)
    for i in range(40):
        d = today - timedelta(days=i)
        f = data / "changes" / f"{d:%Y}" / f"{d.isoformat()}.csv"
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text("x\n")
    removed = prune_raw(data, today)
    kept = sorted(p.stem for p in (data / "changes").glob("*/*.csv"))
    assert len(kept) == 30
    assert kept[0] == (today - timedelta(days=29)).isoformat()
    assert len(removed) == 10
