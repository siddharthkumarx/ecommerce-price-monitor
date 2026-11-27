from __future__ import annotations

import asyncio
from typing import Any

import httpx
import pytest

from pricemon.polite import PoliteConfig
from pricemon.recon import Candidate, ReconResult, recon_store
from pricemon.terms import MAX_SENTENCE, classify, is_ban, policy_text
from tests.fakes import session_for
from tests.test_recon import FakeShop

FILLER = "These terms govern your use of our store and the services we offer to you. " * 4
# The prohibited-uses item of Shopify's default terms template, as one sentence.
SHOPIFY_DEFAULT = (
    "In addition to other prohibitions as set forth in the Terms of Service, you are "
    "prohibited from using the site or its content: (a) for any unlawful purpose; (b) to "
    "solicit others to perform or participate in any unlawful acts; (c) to violate any "
    "international, federal, provincial or state regulations, rules, laws, or local "
    "ordinances; (j) to collect or track the personal information of others; (k) to spam, "
    "phish, pharm, pretext, spider, crawl, or scrape; (l) for any obscene or immoral purpose."
)


def page(*sentences: str) -> str:
    body = "".join(f"<p>{s}</p>" for s in (FILLER, *sentences))
    return (
        "<html><head><script>var robots = 'not a sentence';</script></head><body>"
        f'<div class="shopify-policy__body"><div class="rte">{body}</div></div></body></html>'
    )


@pytest.mark.parametrize(
    "sentence",
    [
        "You may not use any robot, spider or other automatic device to access the site.",
        "Scraping of this website is prohibited.",
        "You agree not to use data mining tools or similar data gathering methods.",
        "You shall not access the Services by automated means without our written permission.",
        "You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of "
        "the Service without express written permission by us.",
        "No content of the site may be used for any commercial purpose.",
    ],
)
def test_bans(sentence: str) -> None:
    got = classify(page(sentence))
    assert got.terms == "ban"
    assert got.source == "read"
    assert got.sentence == sentence


@pytest.mark.parametrize(
    "sentence",
    [
        # Liability, warranty, purchase-for-personal-use and privacy lines are not bans.
        "We are not liable for any loss caused by automated systems or the content of the site.",
        "We do not warrant that the information on the site is accurate or complete.",
        "Products are sold for personal use only and may not be resold for commercial purposes.",
        "We do not sell your personal information or data to third parties.",
        # Naming a robot without forbidding anything is not a ban.
        "Our robot vacuum ships in two colours.",
    ],
)
def test_not_bans(sentence: str) -> None:
    assert classify(page(sentence)).terms == "no_ban"


def test_shopify_default_template_is_a_ban_and_the_evidence_is_clipped() -> None:
    got = classify(page(SHOPIFY_DEFAULT))
    assert got.terms == "ban"
    assert got.sentence is not None
    assert len(got.sentence) <= MAX_SENTENCE
    assert got.sentence.startswith("In addition to other prohibitions")
    assert "spider, crawl, or scrape" in got.sentence


def test_script_text_is_not_policy_text() -> None:
    assert "robots" not in policy_text(page())


def test_a_page_without_policy_text_is_none_found() -> None:
    got = classify("<html><body><p>Page not found</p></body></html>")
    assert (got.terms, got.source) == ("none_found", "no policy text")


def test_is_ban_needs_a_prohibition() -> None:
    assert is_ban("Crawlers are welcome to index this page.") is None


CAND = Candidate(store="Example", domain="shop.example", category="apparel")


class TermsShop(FakeShop):
    def __init__(self, terms: Any = None, **kw: Any) -> None:
        super().__init__(**kw)
        self.terms = terms
        self.terms_hits = 0

    def __call__(self, request: httpx.Request) -> httpx.Response:
        path = request.url.path
        if path.startswith("/policies/") or path.startswith("/en-us/policies/"):
            self.terms_hits += 1
            if callable(self.terms):
                resp: httpx.Response = self.terms(request)
                return resp
            if self.terms is None:
                return httpx.Response(404)
            return httpx.Response(200, text=self.terms, headers={"content-type": "text/html"})
        return super().__call__(request)


def recon(shop: TermsShop, terms: bool = True) -> ReconResult:
    session, _, _ = session_for(
        shop, base_url=f"https://{CAND.domain}", config=PoliteConfig(delay_s=1, jitter_s=0)
    )
    return asyncio.run(recon_store(session, CAND, terms=terms))


def test_recon_reads_the_terms_page() -> None:
    shop = TermsShop(terms=page("Scraping of this website is prohibited."))
    res = recon(shop)
    assert (res.terms, res.terms_source) == ("ban", "read")
    assert res.terms_sentence == "Scraping of this website is prohibited."
    assert res.terms_requests == 1
    assert res.verdict() == (True, [])
    assert res.to_dict()["terms"] == "ban"
    assert res.screen_version == 3  # the catalog was read and screened (D-039)


def test_recon_without_terms_leaves_the_field_empty() -> None:
    shop = TermsShop(terms=page())
    res = recon(shop, terms=False)
    assert res.terms is None
    assert shop.terms_hits == 0


def test_robots_disallowing_policies_means_none_found_without_a_request() -> None:
    robots = "User-agent: *\nDisallow: /policies/\nDisallow: /cart\n"
    shop = TermsShop(terms=page(), robots=robots)
    res = recon(shop)
    assert res.terms == "none_found"
    assert res.terms_source == "robots.txt disallows /policies/terms-of-service"
    assert shop.terms_hits == 0
    assert res.terms_requests == 0
    assert res.verdict() == (True, [])


def test_a_missing_terms_page_is_none_found() -> None:
    res = recon(TermsShop(terms=None))
    assert (res.terms, res.terms_source) == ("none_found", "http 404")


def test_a_same_host_redirect_is_followed_once() -> None:
    def terms(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/policies/terms-of-service":
            return httpx.Response(301, headers={"location": "/en-us/policies/terms-of-service"})
        return httpx.Response(200, text=page(), headers={"content-type": "text/html"})

    shop = TermsShop(terms=terms)
    res = recon(shop)
    assert (res.terms, res.terms_source) == ("no_ban", "read")
    assert res.terms_requests == 2
    assert shop.terms_hits == 2


def test_a_redirect_loop_stops_at_two_requests() -> None:
    def terms(request: httpx.Request) -> httpx.Response:
        return httpx.Response(302, headers={"location": "/policies/terms-of-service?x=1"})

    shop = TermsShop(terms=terms)
    res = recon(shop)
    assert res.terms == "none_found"
    assert res.terms_source == "http 302"
    assert shop.terms_hits == 2


def test_an_off_site_redirect_is_not_followed() -> None:
    def terms(request: httpx.Request) -> httpx.Response:
        return httpx.Response(301, headers={"location": "https://legal.example.org/terms"})

    shop = TermsShop(terms=terms)
    res = recon(shop)
    assert res.terms == "none_found"
    assert res.terms_source == "redirects off the store (legal.example.org)"
    assert shop.terms_hits == 1


def test_a_429_on_the_terms_page_fails_the_store() -> None:
    hits = {"n": 0}

    def terms(request: httpx.Request) -> httpx.Response:
        hits["n"] += 1
        if hits["n"] == 1:
            return httpx.Response(429, headers={"Retry-After": "5"})
        return httpx.Response(200, text=page(), headers={"content-type": "text/html"})

    res = recon(TermsShop(terms=terms))
    assert res.retry_causes == ["http 429"]
    assert "needed 429 retries" in res.verdict()[1]
    assert res.terms_requests == 2


def test_the_committed_request_selects_new_candidates_and_earlier_passes(tmp_path: Any) -> None:
    from pathlib import Path

    import yaml

    from pricemon.checks import select_candidates

    request = yaml.safe_load(Path("checks/request.yml").read_text(encoding="utf-8"))
    chosen = select_candidates(request, Path("checks/candidates.yml"))
    names = [c.store for c in chosen]
    assert len(names) == len(set(names))
    assert "JLab" not in names
    assert request["terms"] is True
    if request.get("only"):
        # A re-check names its stores; every name must be a candidate.
        assert sorted(names) == sorted(request["only"])
    else:
        assert set(request.get("also") or []) <= set(names)
        new = {
            c.store
            for c in select_candidates({"since": request["since"]}, Path("checks/candidates.yml"))
        }
        assert set(names) == new | set(request.get("also") or [])
    bad = tmp_path / "c.yml"
    bad.write_text("categories:\n  audio:\n    - {store: A, domain: a.example}\n")
    with pytest.raises(ValueError, match="not in the candidates"):
        select_candidates({"since": "recon-005", "also": ["Nope"]}, bad)
