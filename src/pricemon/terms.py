"""Read a store's Terms of Service page for a ban on automated access (recon only).

Recon reads one page per store, Shopify's ``/policies/terms-of-service``, with a
budget of 2 requests (one retry, or one same-host redirect), and only when
robots.txt allows it. No other page is searched. The result is one field:

* ``ban``: a sentence forbids robots, spiders, scrapers, crawlers, automated
  access, data mining, or commercial reuse of the site's content;
* ``no_ban``: the page was read and no such sentence was found;
* ``none_found``: no terms page could be read (robots.txt disallows it, it does
  not exist, or it has no policy text).

Liability, warranty, purchase-for-personal-use and privacy lines are not bans.
The first matching sentence is kept as evidence, at most ``MAX_SENTENCE`` characters.
"""

from __future__ import annotations

import html as html_lib
import re
from dataclasses import dataclass

TERMS_PATH = "/policies/terms-of-service"
TERMS_VALUES = ("ban", "no_ban", "none_found")
MAX_SENTENCE = 300
# A terms page shorter than this (after stripping markup) has no policy text.
MIN_POLICY_CHARS = 200

# Words that name automated access themselves: any sentence that also forbids
# something and uses one of them is a ban.
_EXPLICIT = re.compile(
    r"\b(?:robots?|spiders?|spidering|scrap(?:e|es|er|ers|ing)|screen[- ]scrap\w*"
    r"|crawl(?:s|er|ers|ing)?|data[- ]min(?:e|es|ing)|bots?)\b",
    re.IGNORECASE,
)
# "Automated access" in other words; a liability, warranty, privacy or purchase
# line that mentions automated systems is not a ban.
_AUTOMATED = re.compile(
    r"\bautomated\s+(?:means|access|systems?|tools?|programs?|scripts?|software|devices?"
    r"|process(?:es)?|queries|data\s+collection|mechanisms?|methods?|technology|use)\b",
    re.IGNORECASE,
)
# Commercial reuse of the site's content: a reuse verb, a content noun and a
# prohibition in the same sentence, and nothing about buying products.
_REUSE = re.compile(
    r"\b(?:reproduce|duplicate|copy|sell|resell|exploit|republish|redistribute"
    r"|commercial(?:ly)?\s+(?:use|purpose|purposes|exploitation)|for\s+any\s+commercial)\b",
    re.IGNORECASE,
)
_CONTENT = re.compile(
    r"\b(?:content|materials?|information|data|the\s+site|this\s+site|the\s+website"
    r"|our\s+website|the\s+service|any\s+portion\s+of\s+the\s+service)\b",
    re.IGNORECASE,
)
_PROHIBIT = re.compile(
    r"\b(?:not|no|never|prohibit\w*|forbid\w*|restrict\w*|refrain|unauthori[sz]ed"
    r"|without\s+(?:our\s+|the\s+)?(?:prior\s+|express\s+)*(?:written\s+)?(?:consent|permission))\b",
    re.IGNORECASE,
)
# Lines about liability, warranties, buying products for personal use, or privacy
# are not bans of reuse, even when they name content and say "not".
_NOT_REUSE = re.compile(
    r"\b(?:liab\w*|warrant\w*|privacy|personal\s+information|personal\s+use"
    r"|household\s+use|purchas\w*|orders?|products?\s+(?:are|is)\s+(?:sold|intended))\b",
    re.IGNORECASE,
)

_DROP = re.compile(r"<(script|style|noscript|svg|template)\b[^>]*>.*?</\1\s*>", re.S | re.I)
_BREAKS = re.compile(r"<\s*(?:br|/p|/li|/div|/h[1-6]|/tr|li|p|h[1-6])\b[^>]*>", re.I)
_TAGS = re.compile(r"<[^>]+>")
_POLICY_BODY = re.compile(r'<div[^>]+class="[^"]*shopify-policy__body[^"]*"[^>]*>(.*)', re.S | re.I)
_SENTENCE_END = re.compile(r"(?<=[.!?])\s+(?=[\"'(A-Z0-9])")


@dataclass(frozen=True)
class TermsResult:
    terms: str  # ban | no_ban | none_found
    source: str  # read | robots.txt disallows ... | http 404 | no policy text | ...
    sentence: str | None = None


def policy_text(page: str) -> str:
    """The policy's visible text: the Shopify policy body when present, else the page."""
    m = _POLICY_BODY.search(page)
    body = m.group(1) if m else page
    body = _DROP.sub(" ", body)
    body = _BREAKS.sub("\n", body)
    body = _TAGS.sub(" ", body)
    body = html_lib.unescape(body)
    lines = [re.sub(r"[ \t\r\f\v\u00a0]+", " ", line).strip() for line in body.split("\n")]
    return "\n".join(line for line in lines if line)


def sentences(text: str) -> list[str]:
    out: list[str] = []
    for line in text.split("\n"):
        out += [s.strip() for s in _SENTENCE_END.split(line) if s.strip()]
    return out


def is_ban(sentence: str) -> re.Match[str] | None:
    """The match that makes ``sentence`` a ban, or None."""
    if not _PROHIBIT.search(sentence):
        return None
    m = _EXPLICIT.search(sentence)
    if m:
        return m
    if _NOT_REUSE.search(sentence):
        return None
    m = _AUTOMATED.search(sentence)
    if m:
        return m
    reuse = _REUSE.search(sentence)
    if reuse and _CONTENT.search(sentence):
        return reuse
    return None


def clip(sentence: str, match: re.Match[str], limit: int = MAX_SENTENCE) -> str:
    """At most ``limit`` characters: the sentence, or its start and the part around the match."""
    if len(sentence) <= limit:
        return sentence
    head = sentence[:100].rsplit(" ", 1)[0]
    room = limit - len(head) - 5  # " ... " between the two parts, as "…" plus spaces
    start = max(len(head), match.start() - room // 3)
    tail = sentence[start : start + room].strip()
    if start + room < len(sentence):
        tail = tail.rsplit(" ", 1)[0] + " …"
    return f"{head} … {tail}"[:limit]


def classify(page: str) -> TermsResult:
    """Classify a terms page that answered 200."""
    text = policy_text(page)
    if len(text) < MIN_POLICY_CHARS:
        return TermsResult("none_found", "no policy text")
    for sentence in sentences(text):
        m = is_ban(sentence)
        if m:
            return TermsResult("ban", "read", clip(sentence, m))
    return TermsResult("no_ban", "read")
