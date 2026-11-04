from __future__ import annotations

import asyncio
from collections.abc import Coroutine
from datetime import UTC, datetime
from typing import Any

import httpx
import pytest

from pricemon.polite import (
    EdgeGuard,
    PoliteConfig,
    RobotsDisallowed,
    StoreStopped,
    detect_block,
    parse_retry_after,
)
from tests.fakes import ROBOTS_SHOPIFY, Handler, session_for


def run[T](coro: Coroutine[Any, Any, T]) -> T:
    return asyncio.run(coro)


def robots_then(handler: Handler, robots: str = ROBOTS_SHOPIFY) -> Handler:
    def inner(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/robots.txt":
            return httpx.Response(200, text=robots)
        return handler(request)

    return inner


# -- detect_block ---------------------------------------------------------------
@pytest.mark.parametrize(
    ("status", "url", "body", "expected"),
    [
        (200, "https://s.example/products.json", '{"products": []}', None),
        (403, "https://s.example/products.json", "nope", "http 403"),
        (503, "https://s.example/x", "<title>Just a moment...</title>", "cloudflare challenge"),
        (200, "https://s.example/challenge", "", "shopify bot challenge"),
        (200, "https://s.example/password", "", "storefront password page"),
        (200, "https://s.example/x", "<div id='px-captcha'>", "perimeterx captcha"),
        # Passive bot-management script on a normal page is not a block.
        (200, "https://s.example/x", "/cdn-cgi/challenge-platform/scripts/jsd/main.js", None),
        (200, "https://s.example/challenges-guide", "", None),
    ],
)
def test_detect_block(status: int, url: str, body: str, expected: str | None) -> None:
    assert detect_block(status, url, body) == expected


def test_parse_retry_after() -> None:
    now = datetime(2026, 11, 3, 12, 0, 0, tzinfo=UTC)
    assert parse_retry_after("30") == 30.0
    assert parse_retry_after("Tue, 03 Nov 2026 12:01:00 GMT", now=now) == 60.0
    assert parse_retry_after("garbage") is None
    assert parse_retry_after(None) is None


# -- robots -------------------------------------------------------------------
def test_robots_rules_and_country_param() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"products": []})

    session, _, seen = session_for(robots_then(handler))
    run(session.load_robots())
    assert session.robots.status == "ok"
    assert session.allowed("/products.json", {"limit": 250, "page": 1})
    assert session.allowed("/products/tee.js")
    assert not session.allowed("/products/tee-remote")
    assert not session.allowed("/collections/all", {"sort_by": "price"})
    run(session.get("/products.json", {"limit": 250}))
    assert seen[-1].url.params["country"] == "US"
    with pytest.raises(RobotsDisallowed):
        run(session.get("/cart"))


def test_robots_404_allows_everything() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(404, text="not found")

    session, _, _ = session_for(handler)
    run(session.load_robots())
    assert session.robots.status == "missing-4xx"
    assert session.allowed("/anything")


def test_robots_5xx_disallows_everything() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(500, text="boom")

    session, _, _ = session_for(handler, config=PoliteConfig(delay_s=0, jitter_s=0))
    run(session.load_robots())
    assert session.robots.status == "unreachable"
    assert not session.allowed("/products.json")


def test_crawl_delay_raises_spacing() -> None:
    robots = "User-agent: *\nCrawl-delay: 10\nDisallow: /cart\n"

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"products": []})

    session, fake, _ = session_for(robots_then(handler, robots))
    run(session.load_robots())
    run(session.get("/products.json"))
    run(session.get("/products.json"))
    assert session.robots.crawl_delay_s == 10.0
    assert fake.sleeps
    assert min(fake.sleeps) >= 10.0


# -- pacing, retries, stops -----------------------------------------------------
def test_requests_are_spaced_with_jitter() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"products": []})

    cfg = PoliteConfig(delay_s=3.0, jitter_s=2.0)
    session, fake, _ = session_for(robots_then(handler), config=cfg)
    run(session.load_robots())
    for _ in range(3):
        run(session.get("/products.json"))
    assert len(fake.sleeps) == 3
    assert all(3.0 <= s <= 5.0 for s in fake.sleeps)


def test_retry_after_is_honoured_then_succeeds() -> None:
    calls = {"n": 0}

    def handler(request: httpx.Request) -> httpx.Response:
        calls["n"] += 1
        if calls["n"] == 1:
            return httpx.Response(429, headers={"Retry-After": "17"})
        return httpx.Response(200, json={"products": []})

    session, fake, _ = session_for(robots_then(handler))
    run(session.load_robots())
    resp = run(session.get("/products.json"))
    assert resp.status_code == 200
    assert session.retries_made == 1
    assert any(s >= 17.0 for s in fake.sleeps)


def test_long_retry_after_stops_store() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(429, headers={"Retry-After": "3600"})

    session, _, seen = session_for(robots_then(handler))
    run(session.load_robots())
    with pytest.raises(StoreStopped, match="too long"):
        run(session.get("/products.json"))
    n = len(seen)
    with pytest.raises(StoreStopped):
        run(session.get("/products.json"))
    assert len(seen) == n  # a stopped store makes no further requests


def test_no_retry_on_404() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(404)

    session, _, _ = session_for(robots_then(handler))
    run(session.load_robots())
    resp = run(session.get("/products/missing.js"))
    assert resp.status_code == 404
    assert session.retries_made == 0


def test_5xx_retries_are_bounded() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(502)

    cfg = PoliteConfig(delay_s=1.0, jitter_s=0.0, max_attempts=3)
    session, _, seen = session_for(robots_then(handler), config=cfg)
    run(session.load_robots())
    with pytest.raises(StoreStopped, match="retries exhausted: http 502"):
        run(session.get("/products.json"))
    assert len([r for r in seen if r.url.path == "/products.json"]) == 3


def test_network_errors_are_retried() -> None:
    calls = {"n": 0}

    def handler(request: httpx.Request) -> httpx.Response:
        calls["n"] += 1
        if calls["n"] == 1:
            raise httpx.ConnectError("reset", request=request)
        return httpx.Response(200, json={"products": []})

    session, _, _ = session_for(robots_then(handler))
    run(session.load_robots())
    assert run(session.get("/products.json")).status_code == 200


def test_challenge_page_stops_store() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(403, text="<script>window._cf_chl_opt={}</script>")

    session, _, _ = session_for(robots_then(handler))
    run(session.load_robots())
    with pytest.raises(StoreStopped, match="cloudflare challenge"):
        run(session.get("/products.json"))
    assert session.stopped_reason


def test_redirect_to_canonical_host() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.host == "shop.example":
            return httpx.Response(301, headers={"Location": "https://www.shop.example/robots.txt"})
        return httpx.Response(200, text=ROBOTS_SHOPIFY)

    session, _, _ = session_for(handler)
    run(session.load_robots())
    assert session.base_url == "https://www.shop.example"


# -- edge guard ---------------------------------------------------------------
def test_edge_guard_paces_all_stores_together() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"products": []})

    a, fake, _ = session_for(robots_then(handler), base_url="https://a.example")
    edge = EdgeGuard(interval_s=2.0, jitter_s=0.0, sleep=fake.sleep, clock=fake.clock)
    b, _, _ = session_for(robots_then(handler), base_url="https://b.example")
    b.clock, b.sleep = fake.clock, fake.sleep
    a.edge = b.edge = edge
    run(a.load_robots())
    run(b.load_robots())  # different store, but must still wait for the edge
    assert fake.sleeps == [2.0]


def test_edge_guard_trips_after_blocks_on_several_stores() -> None:
    def blocked(request: httpx.Request) -> httpx.Response:
        return httpx.Response(429, text="<title>Just a moment...</title>")

    fake_edge = EdgeGuard(interval_s=0.0, jitter_s=0.0, trip_after=3)
    sessions = []
    for host in ("a", "b", "c"):
        s, _, _ = session_for(blocked, base_url=f"https://{host}.example")
        s.edge = fake_edge
        run(s.load_robots())
        assert s.stopped_reason is not None
        assert s.stopped_reason.startswith("blocked: cloudflare challenge")
        sessions.append(s)
    assert fake_edge.halted_reason is not None

    def ok(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, text="User-agent: *\nDisallow: /cart\n")

    fresh, _, seen = session_for(ok, base_url="https://d.example")
    fresh.edge = fake_edge
    run(fresh.load_robots())
    assert seen == []  # halted run sends nothing more
    assert fresh.stopped_reason is not None
    assert fresh.stopped_reason.startswith("run halted")


def test_challenge_with_long_retry_after_counts_as_block() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            429, headers={"Retry-After": "3600"}, text="<script>window._cf_chl_opt={}</script>"
        )

    session, _, _ = session_for(robots_then(handler))
    run(session.load_robots())
    with pytest.raises(StoreStopped, match="blocked: cloudflare challenge"):
        run(session.get("/products.json"))


def test_retry_details_name_the_request_kind_and_retry_after() -> None:
    calls = {"n": 0}

    def handler(request: httpx.Request) -> httpx.Response:
        calls["n"] += 1
        if calls["n"] == 1:
            return httpx.Response(429, headers={"Retry-After": "7"})
        return httpx.Response(200, json={})

    session, _, _ = session_for(robots_then(handler))
    run(session.load_robots())
    run(session.get("/products/tee.js"))
    assert session.retry_causes == ["http 429"]
    assert session.retry_details == ["http 429 on product .js, retry-after 7s"]


def test_a_429_at_one_store_pauses_every_store() -> None:
    calls = {"a": 0}

    def a_handler(request: httpx.Request) -> httpx.Response:
        calls["a"] += 1
        if calls["a"] == 1:
            return httpx.Response(429, headers={"Retry-After": "60"})
        return httpx.Response(200, json={})

    def b_handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={})

    a, fake, _ = session_for(robots_then(a_handler), base_url="https://a.example")
    b, _, _ = session_for(robots_then(b_handler), base_url="https://b.example")
    b.clock, b.sleep = fake.clock, fake.sleep
    edge = EdgeGuard(interval_s=2.0, jitter_s=0.0, sleep=fake.sleep, clock=fake.clock)
    a.edge = b.edge = edge
    run(a.load_robots())
    run(b.load_robots())

    async def both() -> None:
        await a.get("/products.json")  # 429, Retry-After 60, then succeeds
        before = fake.now
        await b.get("/products.json")  # must also wait out the cooldown
        assert fake.now >= before

    t0 = fake.now
    run(both())
    assert edge.throttle_events == 1
    assert edge.current_interval_s == 3.0  # 2.0 x 1.5
    assert fake.now - t0 >= 60.0
    assert edge.cooldown_s >= 55.0


def test_edge_interval_eases_back_after_successes() -> None:
    fake_now = {"t": 0.0}
    edge = EdgeGuard(interval_s=2.0, ease_after=3, clock=lambda: fake_now["t"])
    edge.throttled(10.0)
    edge.throttled(10.0)
    assert edge.current_interval_s == 4.5
    for _ in range(3):
        edge.succeeded()
    assert edge.current_interval_s == 3.0
    for _ in range(6):
        edge.succeeded()
    assert edge.current_interval_s == 2.0  # never below the base


def test_time_budget_stops_new_requests() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={})

    session, fake, seen = session_for(robots_then(handler))
    session.edge = EdgeGuard(
        interval_s=0.0, jitter_s=0.0, deadline=fake.now + 5, sleep=fake.sleep, clock=fake.clock
    )
    run(session.load_robots())
    fake.now += 10
    with pytest.raises(StoreStopped, match="time budget"):
        run(session.get("/products.json"))
    assert len(seen) == 1  # only robots.txt
