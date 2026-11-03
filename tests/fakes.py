"""Test doubles: a fake clock/sleep pair and a scripted HTTP transport."""

from __future__ import annotations

import random
from collections.abc import Callable
from dataclasses import dataclass, field

import httpx

from pricemon.polite import PoliteConfig, StoreSession

Handler = Callable[[httpx.Request], httpx.Response]


@dataclass
class FakeTime:
    now: float = 1000.0
    sleeps: list[float] = field(default_factory=list)

    def clock(self) -> float:
        return self.now

    async def sleep(self, seconds: float) -> None:
        self.sleeps.append(seconds)
        self.now += seconds


def session_for(
    handler: Handler, base_url: str = "https://shop.example", config: PoliteConfig | None = None
) -> tuple[StoreSession, FakeTime, list[httpx.Request]]:
    seen: list[httpx.Request] = []

    def record(request: httpx.Request) -> httpx.Response:
        seen.append(request)
        return handler(request)

    client = httpx.AsyncClient(transport=httpx.MockTransport(record), follow_redirects=True)
    fake = FakeTime()
    session = StoreSession(
        client=client,
        base_url=base_url,
        config=config or PoliteConfig(delay_s=3.0, jitter_s=0.0),
        sleep=fake.sleep,
        clock=fake.clock,
        rng=random.Random(7),
    )
    return session, fake, seen


ROBOTS_SHOPIFY = """\
User-agent: *
Disallow: /admin
Disallow: /cart
Disallow: /checkout
Disallow: /collections/*sort_by*
Disallow: /search
Disallow: /products/*-remote

User-agent: Nutch
Disallow: /
"""
