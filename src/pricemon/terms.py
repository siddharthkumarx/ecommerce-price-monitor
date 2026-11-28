"""Read a store's Terms of Service page for a ban on automated access (recon only).

Recon and the Terms check (``check: terms``) read Shopify's
``/policies/terms-of-service`` first and, when that page is missing or empty, the
usual store pages in ``TERMS_PATHS`` (D-043), each with a budget of 2 requests (one
retry, or one same-host redirect), and only where robots.txt allows it. The search
stops at the first page with policy text. The result is one field:

* ``ban``: the page names automated access anywhere (robots, spiders, scrapers,
  crawlers, bots, data mining, automated means and the like), unless that sentence
  clearly permits it; or a sentence forbids commercial reuse of the site's content;
* ``no_ban``: the page was read and names no automated access at all;
* ``none_found``: no terms page could be read (robots.txt disallows it, it does
  not exist, or it has no policy text).

The rule fails closed (D-040): a prohibition and its list items ("You agree not
to:" followed by a bullet "use any robot, spider, scraper") are split into
separate lines by the markup, so the prohibition word is not required next to the
automation word. A sentence that names automated access counts as permission only
when it says it is allowed ("is permitted", "you may", ...), forbids nothing, and is
not about search engines. Liability, warranty, purchase-for-personal-use and privacy
lines are not reuse bans. The first matching sentence is kept as evidence, at most
``MAX_SENTENCE`` characters; a list item is shown after the line that introduces it.
"""

from __future__ import annotations

import html as html_lib
import re
from dataclasses import dataclass

TERMS_PATH = "/policies/terms-of-service"
# The full search (D-043): the Shopify policy page, then the pages stores use instead.
TERMS_PATHS = (
    TERMS_PATH,
    "/pages/terms-of-service",
    "/pages/terms-and-conditions",
    "/pages/terms-conditions",
    "/pages/terms",
    "/pages/tos",
)
TERMS_VALUES = ("ban", "no_ban", "none_found")
MAX_SENTENCE = 300
# A terms page shorter than this (after stripping markup) has no policy text.
MIN_POLICY_CHARS = 200

# Words that name automated access themselves: one of them anywhere on the page
# makes it a ban unless its sentence clearly permits it (D-040).
_EXPLICIT = re.compile(
    r"\b(?:robots?|spiders?|spidering|scrap(?:e|es|er|ers|ing)|screen[- ]scrap\w*"
    r"|crawl(?:s|er|ers|ing)?|data[- ](?:min(?:e|es|ing)|harvest\w*)"
    r"|harvest(?:s|ing)?\s+(?:data|information|content)|bots?)\b",
    re.IGNORECASE,
)
# "Automated access" in other words; counted wherever it appears, as above.
_AUTOMATED = re.compile(
    r"\bautomat(?:ed|ic)\s+(?:means|access|systems?|tools?|programs?|scripts?|software|devices?"
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


def is_terms_path(path: str) -> bool:
    """Whether a redirect target can be a terms page (a policy page, or a page whose
    handle names terms); the home page and other pages are not."""
    p = path.lower().rstrip("/")
    return p.startswith("/policies/") or p.split("/")[-1] in {"tos"} or "terms" in p


# A sentence that allows the automated access it names.
_PERMIT = re.compile(
    r"\b(?:you\s+may|(?:is|are)\s+(?:expressly\s+)?(?:permitted|allowed|welcome)"
    r"|we\s+(?:permit|allow|welcome))\b",
    re.IGNORECASE,
)
_SEARCH_ENGINES = re.compile(r"\bsearch[- ]engines?\b", re.IGNORECASE)

_DROP = re.compile(r"<(script|style|noscript|svg|template)\b[^>]*>.*?</\1\s*>", re.S | re.I)
_BREAKS = re.compile(r"<\s*(?:br|/p|/li|/div|/h[1-6]|/tr|li|p|h[1-6])\b[^>]*>", re.I)
_TAGS = re.compile(r"<[^>]+>")
_POLICY_BODY = re.compile(r'<div[^>]+class="[^"]*shopify-policy__body[^"]*"[^>]*>(.*)', re.S | re.I)
# A store page (/pages/...): its main element, without the menus and the footer.
_MAIN = re.compile(r"<main\b[^>]*>(.*?)</main\s*>", re.S | re.I)
_SENTENCE_END = re.compile(r"(?<=[.!?])\s+(?=[\"'(A-Z0-9])")


@dataclass(frozen=True)
class TermsResult:
    terms: str  # ban | no_ban | none_found
    source: str  # read | robots.txt disallows ... | http 404 | no policy text | ...
    sentence: str | None = None
    page: str | None = None  # the path that was classified (None: no page read)


def policy_text(page: str) -> str:
    """The policy's visible text: the Shopify policy body, else the page's main
    element, else the whole page."""
    m = _POLICY_BODY.search(page) or _MAIN.search(page)
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


def automation(sentence: str) -> re.Match[str] | None:
    """The first word or phrase in ``sentence`` that names automated access."""
    return _EXPLICIT.search(sentence) or _AUTOMATED.search(sentence)


def permits(sentence: str) -> bool:
    """Whether ``sentence`` clearly allows the automated access it names."""
    return (
        bool(_PERMIT.search(sentence))
        and not _PROHIBIT.search(sentence)
        and not _SEARCH_ENGINES.search(sentence)
    )


def reuse_ban(sentence: str) -> re.Match[str] | None:
    """A prohibition of commercial reuse of the site's content, or None."""
    if not _PROHIBIT.search(sentence) or _NOT_REUSE.search(sentence):
        return None
    reuse = _REUSE.search(sentence)
    return reuse if reuse and _CONTENT.search(sentence) else None


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
    """Classify a terms page that answered 200 (fails closed, D-040)."""
    text = policy_text(page)
    if len(text) < MIN_POLICY_CHARS:
        return TermsResult("none_found", "no policy text")
    found: tuple[str, re.Match[str]] | None = None
    previous = ""
    for sentence in sentences(text):
        m = automation(sentence)
        if m and not permits(sentence):
            if previous.endswith(":") and not _PROHIBIT.search(sentence):
                # A list item: show the line that introduces it ("You agree not to:").
                joined = f"{previous} {sentence}"
                m = automation(joined)
                assert m is not None
                sentence = joined
            if _PROHIBIT.search(sentence):
                return TermsResult("ban", "read", clip(sentence, m))
            found = found or (sentence, m)
        elif not m:
            r = reuse_ban(sentence)
            if r:
                return TermsResult("ban", "read", clip(sentence, r))
        previous = sentence
    if found:
        return TermsResult("ban", "read", clip(*found))
    return TermsResult("no_ban", "read")
