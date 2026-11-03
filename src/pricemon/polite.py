"""Polite HTTP access to a single store.

Rules enforced here (see docs/maintainers.md, "Scraping rules"):

* robots.txt is fetched first and every request is checked against it
  (RFC 9309 semantics via Protego, including ``*`` and ``$`` wildcards).
* Requests to one store are spaced by a base delay plus random jitter; a larger
  ``Crawl-delay`` from robots.txt wins.
* Retries happen only for HTTP 429, HTTP 5xx and network errors, with
  exponential backoff. ``Retry-After`` is honoured; if it asks for longer than
  ``max_retry_after_s`` the store is stopped instead of waiting.
* A block or challenge page stops the store for the rest of the run: every
  later call raises :class:`StoreStopped` without touching the network.
"""

from __future__ import annotations

import asyncio
import email.utils
import random
import time
from collections.abc import Awaitable, Callable, Mapping
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Literal
from urllib.parse import urlencode, urlsplit

import httpx
from protego import Protego

USER_AGENT = "ecommerce-price-monitor/0.1 (+https://siddharthkumar.com)"
ROBOTS_AGENT = "ecommerce-price-monitor"

Expect = Literal["json", "html", "text"]

# Markers that only appear on challenge / interstitial pages, never on a normal
# storefront page. Checked against the first 32 KiB of the body, lower-cased.
# Deliberately excludes passive bot-management scripts that ship on normal pages
# (for example Cloudflare's /cdn-cgi/challenge-platform/scripts/jsd/main.js).
_CHALLENGE_MARKERS: tuple[tuple[str, str], ...] = (
    ("window._cf_chl_opt", "cloudflare challenge"),
    ("<title>just a moment...</title>", "cloudflare challenge"),
    ("<title>attention required! | cloudflare</title>", "cloudflare block"),
    ("px-captcha", "perimeterx captcha"),
    ("captcha-delivery.com", "datadome captcha"),
    ("_incapsula_resource", "imperva challenge"),
    ("sgcaptcha", "siteground captcha"),
)
_BLOCK_PATHS: tuple[tuple[str, str], ...] = (
    ("/challenge", "shopify bot challenge"),
    ("/password", "storefront password page"),
)


class StoreStopped(Exception):
    """The store is stopped for this run (block, challenge or exhausted retries)."""

    def __init__(self, reason: str) -> None:
        super().__init__(reason)
        self.reason = reason


class RobotsDisallowed(Exception):
    """robots.txt disallows the requested URL for our user agent."""


def detect_block(status: int, final_url: str, body_head: str) -> str | None:
    """Return a reason if the response is a block or challenge page, else ``None``."""
    path = urlsplit(final_url).path.rstrip("/")
    for prefix, reason in _BLOCK_PATHS:
        if path == prefix or path.startswith(prefix + "/"):
            return reason
    lowered = body_head[:32_768].lower()
    for marker, reason in _CHALLENGE_MARKERS:
        if marker in lowered:
            return reason
    if status in (401, 403):
        return f"http {status}"
    return None


def parse_retry_after(value: str | None, now: datetime | None = None) -> float | None:
    """Parse a ``Retry-After`` header (delta-seconds or HTTP-date) into seconds."""
    if value is None:
        return None
    value = value.strip()
    if value.isdigit():
        return float(value)
    try:
        when = email.utils.parsedate_to_datetime(value)
    except (TypeError, ValueError):
        return None
    if when.tzinfo is None:
        when = when.replace(tzinfo=UTC)
    now = now or datetime.now(UTC)
    return max(0.0, (when - now).total_seconds())


@dataclass(frozen=True)
class PoliteConfig:
    delay_s: float = 3.0
    jitter_s: float = 2.0
    max_attempts: int = 4
    backoff_base_s: float = 2.0
    max_retry_after_s: float = 120.0
    country: str = "US"


@dataclass
class RobotsInfo:
    status: str = "not-fetched"  # ok | missing-4xx | unreachable | not-fetched
    http_status: int | None = None
    crawl_delay_s: float | None = None
    parser: Protego | None = None

    def allows(self, url: str) -> bool:
        if self.status == "missing-4xx":
            return True
        if self.status != "ok" or self.parser is None:
            return False
        return bool(self.parser.can_fetch(url, ROBOTS_AGENT))


Sleep = Callable[[float], Awaitable[None]]


@dataclass
class EdgeGuard:
    """Run-wide pacing and circuit breaker shared by every store session.

    Shopify throttles per client IP across all shops on its edge, so per-store
    delays alone let the run as a whole go too fast (docs/incidents.md, INC-001).
    """

    interval_s: float = 2.0
    jitter_s: float = 1.0
    trip_after: int = 4
    window_s: float = 120.0
    sleep: Sleep = asyncio.sleep
    clock: Callable[[], float] = time.monotonic
    rng: random.Random = field(default_factory=random.Random)

    halted_reason: str | None = None
    _next_at: float = 0.0
    _blocks: list[tuple[float, str]] = field(default_factory=list)
    _lock: asyncio.Lock = field(default_factory=asyncio.Lock)

    async def wait_turn(self) -> None:
        async with self._lock:
            wait = self._next_at - self.clock()
            if wait > 0:
                await self.sleep(wait)
            self._next_at = self.clock() + self.interval_s + self.rng.uniform(0.0, self.jitter_s)

    def record_block(self, host: str) -> None:
        now = self.clock()
        self._blocks = [(t, h) for t, h in self._blocks if now - t <= self.window_s]
        self._blocks.append((now, host))
        hosts = {h for _, h in self._blocks}
        if len(hosts) >= self.trip_after and self.halted_reason is None:
            self.halted_reason = (
                f"run halted: {len(hosts)} stores blocked within {self.window_s:.0f}s "
                "(edge throttling)"
            )


@dataclass
class StoreSession:
    """Sequential, rate-limited access to one store."""

    client: httpx.AsyncClient
    base_url: str
    config: PoliteConfig = field(default_factory=PoliteConfig)
    sleep: Sleep = asyncio.sleep
    clock: Callable[[], float] = time.monotonic
    rng: random.Random = field(default_factory=random.Random)
    edge: EdgeGuard | None = None

    robots: RobotsInfo = field(default_factory=RobotsInfo)
    stopped_reason: str | None = None
    requests_made: int = 0
    retries_made: int = 0
    _next_at: float = 0.0

    def __post_init__(self) -> None:
        self.base_url = self.base_url.rstrip("/")

    @property
    def host(self) -> str:
        return urlsplit(self.base_url).netloc

    # -- pacing -----------------------------------------------------------
    def _gap(self) -> float:
        base = max(self.config.delay_s, self.robots.crawl_delay_s or 0.0)
        return base + self.rng.uniform(0.0, self.config.jitter_s)

    async def _wait_turn(self) -> None:
        wait = self._next_at - self.clock()
        if wait > 0:
            await self.sleep(wait)

    def _stop(self, reason: str) -> StoreStopped:
        self.stopped_reason = reason
        if self.edge is not None and reason.startswith("blocked"):
            self.edge.record_block(self.host)
        return StoreStopped(reason)

    # -- low level ----------------------------------------------------------
    async def _send(self, url: str, accept: str) -> httpx.Response:
        """Send one GET with retry rules applied. Raises StoreStopped."""
        last_problem = "no attempt"
        for attempt in range(1, self.config.max_attempts + 1):
            if self.edge is not None and self.edge.halted_reason:
                raise self._stop(self.edge.halted_reason)
            await self._wait_turn()
            if self.edge is not None:
                await self.edge.wait_turn()
            self.requests_made += 1
            try:
                resp = await self.client.get(url, headers={"Accept": accept})
            except httpx.TransportError as exc:
                last_problem = f"network error: {type(exc).__name__}"
                wait = self.config.backoff_base_s * 2 ** (attempt - 1)
            else:
                if resp.status_code != 429 and resp.status_code < 500:
                    self._next_at = self.clock() + self._gap()
                    return resp
                last_problem = f"http {resp.status_code}"
                # A challenge served with 429/503 is a block, not a rate limit: never retry it.
                body_reason = detect_block(resp.status_code, str(resp.url), resp.text)
                if body_reason and body_reason != f"http {resp.status_code}":
                    raise self._stop(f"blocked: {body_reason} ({last_problem})")
                retry_after = parse_retry_after(resp.headers.get("Retry-After"))
                if retry_after is not None and retry_after > self.config.max_retry_after_s:
                    raise self._stop(f"{last_problem}, Retry-After {retry_after:.0f}s too long")
                backoff = self.config.backoff_base_s * 2 ** (attempt - 1)
                wait = max(backoff, retry_after or 0.0)
            if attempt < self.config.max_attempts:
                self.retries_made += 1
                self._next_at = self.clock() + wait + self.rng.uniform(0.0, self.config.jitter_s)
        raise self._stop(f"retries exhausted: {last_problem}")

    # -- public API ---------------------------------------------------------
    async def load_robots(self) -> RobotsInfo:
        """Fetch robots.txt (following redirects to the canonical host)."""
        url = f"{self.base_url}/robots.txt"
        try:
            resp = await self._send(url, "text/plain")
        except StoreStopped as exc:
            # RFC 9309 section 2.3.1.4: unreachable robots.txt means full disallow.
            self.robots = RobotsInfo(status="unreachable")
            if exc.reason.startswith(("blocked", "run halted")):
                self.stopped_reason = f"{exc.reason} (robots.txt)"
            else:
                self.stopped_reason = f"robots.txt unreachable: {exc.reason}"
            return self.robots
        final = urlsplit(str(resp.url))
        self.base_url = f"{final.scheme}://{final.netloc}"
        reason = detect_block(resp.status_code, str(resp.url), resp.text)
        if reason and reason not in ("http 401", "http 403"):
            self.robots = RobotsInfo(status="unreachable", http_status=resp.status_code)
            self._stop(f"blocked: {reason} (robots.txt)")
            return self.robots
        if 400 <= resp.status_code < 500:
            # RFC 9309 section 2.3.1.3: 4xx means no restrictions.
            self.robots = RobotsInfo(status="missing-4xx", http_status=resp.status_code)
            return self.robots
        parser = Protego.parse(resp.text)
        delay = parser.crawl_delay(ROBOTS_AGENT)
        self.robots = RobotsInfo(
            status="ok",
            http_status=resp.status_code,
            crawl_delay_s=float(delay) if delay is not None else None,
            parser=parser,
        )
        # The gap after this request must respect a Crawl-delay we only just learnt.
        self._next_at = self.clock() + self._gap()
        return self.robots

    def url_for(self, path: str, params: Mapping[str, str | int] | None = None) -> str:
        query: dict[str, str | int] = dict(params or {})
        query["country"] = self.config.country
        return f"{self.base_url}{path}?{urlencode(query)}"

    def allowed(self, path: str, params: Mapping[str, str | int] | None = None) -> bool:
        return self.robots.allows(self.url_for(path, params))

    async def get(
        self,
        path: str,
        params: Mapping[str, str | int] | None = None,
        expect: Expect = "json",
    ) -> httpx.Response:
        """GET ``path`` with ``country`` added. Raises RobotsDisallowed / StoreStopped."""
        if self.stopped_reason:
            raise StoreStopped(self.stopped_reason)
        url = self.url_for(path, params)
        if not self.robots.allows(url):
            raise RobotsDisallowed(url)
        accept = {
            "json": "application/json",
            "html": "text/html,application/xhtml+xml",
            "text": "text/plain",
        }[expect]
        resp = await self._send(url, accept)
        reason = detect_block(resp.status_code, str(resp.url), resp.text)
        if reason:
            raise self._stop(f"blocked: {reason}")
        return resp


def make_client(timeout_s: float = 30.0) -> httpx.AsyncClient:
    return httpx.AsyncClient(
        headers={"User-Agent": USER_AGENT, "Accept-Language": "en-US,en;q=0.8"},
        timeout=httpx.Timeout(timeout_s),
        follow_redirects=True,
        max_redirects=5,
        limits=httpx.Limits(max_connections=32, max_keepalive_connections=16),
    )
