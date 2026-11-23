"""Catalog readers for the non-Shopify platforms (WooCommerce, BigCommerce).

Each reader returns the same *slim product* shape as
:func:`pricemon.normalize.slim_product`, so validation, the batch guard, history
and outputs are shared by every platform::

    {"id", "handle", "title", "product_type", "tags",
     "variants": [{"id", "title", "price", "compare_at_price", "available"}]}

``price`` and ``compare_at_price`` are decimal strings in US dollars, as on Shopify.
``handle`` is the product page path (``product/<slug>``), see
:func:`pricemon.stores.product_url`.

WooCommerce (public Store API, no key, the API the store's own pages use):

* catalog: ``/wp-json/wc/store/v1/products`` pages (parents and simple products)
  plus ``?type=variation`` pages (one row per variation, prices in minor units);
* second source for the daily sample: the same product re-read on its own
  (``/products/<id>`` or ``?type=variation&parent=<id>``), and the product page's
  JSON-LD offers (currency proof).

BigCommerce (no public catalog API): the product sitemap lists product pages; each
page is read once, politely. Every page carries two price sources rendered by
different parts of the theme: the JSON-LD ``Offer`` (catalog row) and the theme's
``BCData`` product attributes (second source, compared on **every** product). A
product whose two sources disagree is held back. One row per product (the price
shown before an option is chosen).
"""

from __future__ import annotations

import html as htmllib
import json
import re
from collections import defaultdict
from decimal import Decimal, InvalidOperation
from typing import TYPE_CHECKING, Any
from urllib.parse import urlsplit

import httpx

from pricemon.polite import RobotsDisallowed, StoreSession
from pricemon.witness import jsonld_blocks, offer_availability, price_to_cents

if TYPE_CHECKING:  # pragma: no cover
    from pricemon.fetch import StoreFetch, WitnessResult

WOO_PATH = "/wp-json/wc/store/v1/products"
WOO_PER_PAGE = 100
WOO_MAX_PAGES = 80
# Product types without a price of their own, or not sold by the store itself.
WOO_SKIP_TYPES = frozenset({"grouped", "external"})

BC_SITEMAP = "/xmlsitemap.php"
BC_MAX_SITEMAP_PAGES = 10
# Daily safety cap: one page per product, so the catalog size is the request count.
BC_MAX_PRODUCTS = 400

_LOC = re.compile(r"<loc>\s*([^<\s]+)\s*</loc>", re.IGNORECASE)
_BC_PRODUCT_ID = re.compile(r"name=[\"']product_id[\"']\s+value=[\"'](\d+)[\"']", re.IGNORECASE)
_BCDATA = "var BCData = "


def _json(resp: httpx.Response) -> Any:
    try:
        return json.loads(resp.content)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return None


def _text(value: Any) -> str:
    return htmllib.unescape(value).strip() if isinstance(value, str) else ""


def cents_to_decimal(cents: int | None) -> str | None:
    if cents is None:
        return None
    sign = "-" if cents < 0 else ""
    cents = abs(cents)
    return f"{sign}{cents // 100}.{cents % 100:02d}"


def minor_to_cents(value: Any, minor_unit: Any) -> int | None:
    """A Store API amount (string of minor units) to US cents."""
    if value is None or value == "" or isinstance(value, bool):
        return None
    try:
        amount = Decimal(str(value))
        unit = int(minor_unit if minor_unit is not None else 2)
    except (InvalidOperation, ValueError, TypeError):
        return None
    cents = amount * Decimal(10) ** (2 - unit)
    if cents != cents.to_integral_value():
        return None
    return int(cents)


def page_path(url: Any) -> str:
    """``https://host/product/slug/?x=1`` -> ``product/slug`` (the row's handle)."""
    if not isinstance(url, str):
        return ""
    return urlsplit(url).path.strip("/")


# -- WooCommerce -----------------------------------------------------------------


def woo_prices(item: dict[str, Any]) -> tuple[int | None, int | None, str | None]:
    """(price, compare-at, currency) in cents for a Store API product or variation."""
    raw = item.get("prices")
    prices: dict[str, Any] = raw if isinstance(raw, dict) else {}
    unit = prices.get("currency_minor_unit", 2)
    price = minor_to_cents(prices.get("price"), unit)
    regular = minor_to_cents(prices.get("regular_price"), unit)
    compare = regular if regular is not None and price is not None and regular > price else None
    cur = prices.get("currency_code")
    return price, compare, cur if isinstance(cur, str) else None


def _woo_variant(item: dict[str, Any], title: str) -> dict[str, Any]:
    price, compare, _ = woo_prices(item)
    return {
        "id": item.get("id"),
        "title": title,
        "price": cents_to_decimal(price),
        "compare_at_price": cents_to_decimal(compare),
        "available": item.get("is_in_stock") if isinstance(item.get("is_in_stock"), bool) else None,
    }


def woo_products(
    parents: list[dict[str, Any]], variations: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    """Slim products from Store API product and variation pages."""
    by_parent: dict[Any, list[dict[str, Any]]] = defaultdict(list)
    for v in variations:
        by_parent[v.get("parent")].append(v)
    out: list[dict[str, Any]] = []
    for p in parents:
        kind = str(p.get("type") or "")
        if kind in WOO_SKIP_TYPES or "gift" in kind:
            continue
        cats = [c for c in p.get("categories") or [] if isinstance(c, dict)]
        tags = [
            _text(c.get("name"))
            for c in cats + [t for t in p.get("tags") or [] if isinstance(t, dict)]
        ]
        product = {
            "id": p.get("id"),
            "handle": page_path(p.get("permalink")),
            "title": _text(p.get("name")),
            "product_type": _text(cats[0].get("name")) if cats else "",
            "tags": [t for t in tags if t],
        }
        if kind == "variable":
            product["variants"] = [
                _woo_variant(v, _text(v.get("variation")) or "Default Title")
                for v in by_parent.get(p.get("id"), [])
            ]
        else:
            product["variants"] = [_woo_variant(p, "Default Title")]
        if product["variants"]:
            out.append(product)
    return out


def woo_currencies(items: list[dict[str, Any]]) -> set[str]:
    return {c for c in (woo_prices(i)[2] for i in items) if c}


async def _woo_pages(
    session: StoreSession, params: dict[str, str | int], out: StoreFetch
) -> list[dict[str, Any]] | None:
    items: list[dict[str, Any]] = []
    for page in range(1, WOO_MAX_PAGES + 1):
        resp = await session.get(WOO_PATH, {**params, "per_page": WOO_PER_PAGE, "page": page})
        out.pages += 1
        data = _json(resp)
        if resp.status_code != 200 or not isinstance(data, list):
            out.reason = f"store api page {page}: http {resp.status_code}, not a catalog"
            return None
        items += [d for d in data if isinstance(d, dict)]
        total = resp.headers.get("x-wp-totalpages")
        if not data or (total and total.isdigit() and page >= int(total)):
            return items
        if not total and len(data) < WOO_PER_PAGE:
            return items
    out.reason = f"store api has more than {WOO_MAX_PAGES} pages"
    return None


async def woo_catalog(session: StoreSession, out: StoreFetch) -> bool:
    parents = await _woo_pages(session, {}, out)
    if parents is None:
        return False
    has_variable = any(p.get("type") == "variable" for p in parents)
    variations = await _woo_pages(session, {"type": "variation"}, out) if has_variable else []
    if variations is None:
        return False
    out.api_currencies = woo_currencies(parents + variations)
    out.products = woo_products(parents, variations)
    return True


async def woo_reread(
    session: StoreSession, product: dict[str, Any]
) -> dict[int, tuple[int | None, bool | None]]:
    """The sample product read on its own: variant id -> (price cents, in stock)."""
    many = len(product["variants"]) > 1 or product["variants"][0]["id"] != product["id"]
    if many:
        resp = await session.get(
            WOO_PATH, {"type": "variation", "parent": product["id"], "per_page": WOO_PER_PAGE}
        )
        data = _json(resp)
        items = data if resp.status_code == 200 and isinstance(data, list) else []
    else:
        resp = await session.get(f"{WOO_PATH}/{product['id']}")
        data = _json(resp)
        items = [data] if resp.status_code == 200 and isinstance(data, dict) else []
    return {
        int(i["id"]): (woo_prices(i)[0], i.get("is_in_stock"))
        for i in items
        if isinstance(i, dict) and isinstance(i.get("id"), int)
    }


async def woo_witness_api(session: StoreSession, product: dict[str, Any], w: WitnessResult) -> None:
    seen = await woo_reread(session, product)
    for v in product["variants"]:
        vid = v.get("id")
        if not isinstance(vid, int) or vid not in seen:
            continue
        w.js_compared += 1
        price, stock = seen[vid]
        if price != price_to_cents(v.get("price")):
            w.js_price_diffs += 1
            w.first_diff = w.first_diff or f"variant {vid}: re-read {price} vs catalog cents"
        if stock is not v.get("available"):
            w.js_stock_diffs += 1
    w.js = "match" if w.js_compared and not (w.js_price_diffs or w.js_stock_diffs) else "mismatch"
    if not seen:
        w.js = "missing"


async def woo_variant_price(session: StoreSession, variant_id: int) -> int | None:
    """Second read of one product or variation (for a big price move)."""
    resp = await session.get(f"{WOO_PATH}/{variant_id}")
    data = _json(resp)
    if resp.status_code != 200 or not isinstance(data, dict):
        return None
    return woo_prices(data)[0]


# -- BigCommerce -----------------------------------------------------------------


def bc_sitemap_paths(xml: str) -> list[str]:
    return [p for p in (page_path(u) for u in _LOC.findall(xml)) if p]


def bcdata(html: str) -> dict[str, Any] | None:
    """The theme's ``var BCData = {...};`` object, or None."""
    at = html.find(_BCDATA)
    if at < 0:
        return None
    try:
        data, _ = json.JSONDecoder().raw_decode(html, at + len(_BCDATA))
    except json.JSONDecodeError:
        return None
    return data if isinstance(data, dict) else None


def _value(node: Any, *path: str) -> Any:
    for key in path:
        if not isinstance(node, dict):
            return None
        node = node.get(key)
    return node


def _bc_cents(value: Any) -> int | None:
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return price_to_cents(str(Decimal(str(value)).quantize(Decimal("0.01"))))
    return price_to_cents(value) if isinstance(value, str) else None


def bc_page(html: str) -> dict[str, Any] | None:
    """Read one BigCommerce product page.

    Returns ``id``, ``title``, JSON-LD ``ld_price`` / ``ld_stock`` / ``currency`` and
    the theme's ``data_price`` / ``data_stock`` / ``compare`` (all prices in cents),
    or None when the page is not a priced product page.
    """
    pid = _BC_PRODUCT_ID.search(html)
    product: dict[str, Any] | None = None
    for block in jsonld_blocks(html):
        for node in block if isinstance(block, list) else [block]:
            if isinstance(node, dict) and node.get("@type") in ("Product", ["Product"]):
                product = node
                break
        if product:
            break
    if not pid or product is None:
        return None
    offers = product.get("offers")
    offer = offers[0] if isinstance(offers, list) and offers else offers
    if not isinstance(offer, dict):
        return None
    ld_price = next(
        (
            c
            for c in (_bc_cents(offer.get(k)) for k in ("price", "minPrice", "lowPrice"))
            if c is not None
        ),
        None,
    )
    attrs = _value(bcdata(html), "product_attributes") or {}
    data_price = _bc_cents(
        _value(attrs, "price", "price_range", "min", "without_tax", "value")
        if _value(attrs, "price", "price_range", "min") is not None
        else _value(attrs, "price", "without_tax", "value")
    )
    compare = None
    for key in ("non_sale_price_without_tax", "rrp_without_tax"):
        c = _bc_cents(_value(attrs, "price", key, "value"))
        if c is not None and ld_price is not None and c > ld_price:
            compare = c
            break
    stock = offer_availability(offer)
    cur = offer.get("priceCurrency")
    data_cur = _value(attrs, "price", "without_tax", "currency")
    return {
        "id": int(pid.group(1)),
        "title": _text(product.get("name")),
        "ld_price": ld_price,
        "ld_stock": None if stock is None else stock == "in_stock",
        "data_price": data_price,
        "data_stock": attrs.get("instock") if isinstance(attrs.get("instock"), bool) else None,
        "compare": compare,
        "currencies": {c.upper() for c in (cur, data_cur) if isinstance(c, str) and len(c) == 3},
    }


def bc_agree(page: dict[str, Any]) -> str | None:
    """None when the two sources on the page agree, else what differs."""
    if page["data_price"] is None:
        return "no theme price"
    if page["ld_price"] != page["data_price"]:
        return f"JSON-LD {page['ld_price']} vs theme {page['data_price']} cents"
    if (
        page["ld_stock"] is not None
        and page["data_stock"] is not None
        and page["ld_stock"] != page["data_stock"]
    ):
        return "stock differs between JSON-LD and theme"
    return None


async def bc_sitemap(session: StoreSession, out: StoreFetch) -> list[str] | None:
    paths: list[str] = []
    for page in range(1, BC_MAX_SITEMAP_PAGES + 1):
        resp = await session.get(BC_SITEMAP, {"type": "products", "page": page}, expect="text")
        out.pages += 1
        if resp.status_code == 404 and page > 1:
            break  # past the last sitemap page
        if resp.status_code != 200:
            out.reason = f"product sitemap page {page}: http {resp.status_code}"
            return None
        found = bc_sitemap_paths(resp.text)
        if not found:
            break
        paths += [p for p in found if p not in paths]
    if not paths:
        out.reason = "product sitemap is empty"
        return None
    return paths


async def bc_read(session: StoreSession, path: str) -> dict[str, Any] | None:
    resp = await session.get(f"/{path}/", expect="html")
    return bc_page(resp.text) if resp.status_code == 200 else None


async def bc_catalog(session: StoreSession, out: StoreFetch) -> bool:
    paths = await bc_sitemap(session, out)
    if paths is None:
        return False
    if len(paths) > BC_MAX_PRODUCTS:
        out.reason = f"product sitemap lists {len(paths)} products, over {BC_MAX_PRODUCTS}"
        return False
    seen: set[int] = set()
    for path in paths:
        try:
            page = await bc_read(session, path)
        except RobotsDisallowed:
            continue
        if page is None or page["id"] in seen:
            continue
        seen.add(page["id"])
        out.api_currencies |= page["currencies"]
        disagree = bc_agree(page)
        if disagree:
            out.held_variants[page["id"]] = f"second source: {disagree}"
        available = page["ld_stock"] if page["ld_stock"] is not None else page["data_stock"]
        out.products.append(
            {
                "id": page["id"],
                "handle": path,
                "title": page["title"],
                "product_type": "",
                "tags": [],
                "variants": [
                    {
                        "id": page["id"],
                        "title": "Default Title",
                        "price": cents_to_decimal(page["ld_price"]),
                        "compare_at_price": cents_to_decimal(page["compare"]),
                        "available": available,
                        "_data_price": page["data_price"],
                        "_data_stock": page["data_stock"],
                    }
                ],
            }
        )
    if not out.products:
        out.reason = "no priced product pages"
        return False
    return True


def bc_witness(product: dict[str, Any], w: WitnessResult) -> None:
    """The daily sample: the theme's own price data against the JSON-LD row."""
    v = product["variants"][0]
    w.js_compared = 1
    if v.get("_data_price") != price_to_cents(v.get("price")):
        w.js_price_diffs = 1
        w.first_diff = f"theme {v.get('_data_price')} vs JSON-LD {v.get('price')}"
    if (
        v.get("_data_stock") is not None
        and v.get("available") is not None
        and v["_data_stock"] is not v["available"]
    ):
        w.js_stock_diffs = 1
    w.js = "mismatch" if (w.js_price_diffs or w.js_stock_diffs) else "match"
    w.jsonld = "match"
    w.jsonld_compared = 1
