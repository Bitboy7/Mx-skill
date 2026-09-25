#!/usr/bin/env python3
"""Busqueda y comparacion de precios de productos en tiendas mexicanas.

Fuentes publicas, sin API key ni sesion:
  - Liverpool: HTML server-rendered con tarjetas de producto.
  - Chedraui y OfficeMax: API publica de catalogo VTEX
    (`/api/catalog_system/pub/products/search/`).

Mercado Libre dejo de permitir busqueda publica (HTTP 403) y otras tiendas
(Walmart, Soriana, Sanborns, Amazon) bloquean el scraping automatizado; por eso
solo se incluyen las tiendas con endpoints publicos estables.

Uso:
  python3 mx_product_search.py --q "audifonos bluetooth" --limit 5
  python3 mx_product_search.py --q "iphone" --tiendas Liverpool,Chedraui
"""

import argparse
import html as html_lib
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
)
HEADERS = {
    "User-Agent": USER_AGENT,
    "Accept": "text/html,application/xhtml+xml,application/json",
    "Accept-Language": "es-MX,es;q=0.9",
}

LIVERPOOL_BASE = "https://www.liverpool.com.mx"
LIVERPOOL_SEARCH = LIVERPOOL_BASE + "/tienda"

# name -> (tipo, base). "liverpool" usa HTML; "vtex" usa la API publica VTEX.
STORES = {
    "liverpool": {"name": "Liverpool", "kind": "liverpool", "base": LIVERPOOL_BASE},
    "chedraui": {"name": "Chedraui", "kind": "vtex", "base": "https://www.chedraui.com.mx"},
    "officemax": {"name": "OfficeMax", "kind": "vtex", "base": "https://www.officemax.com.mx"},
}
DEFAULT_STORES = list(STORES)

CARD_ID_RE = re.compile(r'data-testid="(\d+)-card"')
PRICE_RE = re.compile(r"\$\s*([\d,]+)(?:\.\d+)?")
TAG_RE = re.compile(r"<[^>]+>")
COMMENT_RE = re.compile(r"<!--.*?-->")
WS_RE = re.compile(r"\s+")


def http_get_text(url, timeout=30):
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as exc:
        raise RuntimeError(f"HTTP {exc.code}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"sin conexion ({exc.reason})") from exc


def http_get_json(url, timeout=30):
    return json.loads(http_get_text(url, timeout=timeout))


def _clean(fragment):
    text = COMMENT_RE.sub(" ", fragment or "")
    text = TAG_RE.sub(" ", text)
    text = html_lib.unescape(text)
    return WS_RE.sub(" ", text).strip()


def _first_match(pattern, block):
    match = re.search(pattern, block, re.S)
    return _clean(match.group(1)) if match else None


def build_url(query):
    return LIVERPOOL_SEARCH + "?" + urllib.parse.urlencode({"s": query})


def extract_products(html, limit):
    """Extrae productos de la pagina de resultados de Liverpool."""
    ids = list(dict.fromkeys(CARD_ID_RE.findall(html)))
    products = []
    for product_id in ids:
        start = html.find(f'data-testid="{product_id}-card"')
        if start < 0:
            continue
        end = html.find("</section>", start)
        block = html[start : end if end > 0 else start + 8000]

        link_match = re.search(rf'data-testid="{product_id}-card-card-link"[^>]*href="([^"]+)"', html)
        href = html_lib.unescape(link_match.group(1)) if link_match else None

        nombre = _first_match(r"<h3[^>]*>(.*?)</h3>", block)
        if not nombre:
            nombre = _first_match(r'alt="([^"]+)"', block)
        marca = _first_match(r"<h4[^>]*>(.*?)</h4>", block)

        price_anchor = re.search(rf'data-testid="{product_id}-price"', block)
        precio = precio_original = None
        if price_anchor:
            rest = block[price_anchor.end():]
            rating_idx = rest.find(f'data-testid="{product_id}-rating"')
            segment = rest[:rating_idx] if rating_idx >= 0 else rest[:600]
            original_idx = segment.find('data-testid="original"')
            current_html = segment[:original_idx] if original_idx >= 0 else segment
            original_html = segment[original_idx:] if original_idx >= 0 else ""
            current_amounts = PRICE_RE.findall(_clean(current_html))
            original_amounts = PRICE_RE.findall(_clean(original_html))
            if current_amounts:
                precio = int(current_amounts[0].replace(",", ""))
            if original_amounts:
                precio_original = int(original_amounts[0].replace(",", ""))
        descuento = None
        if precio and precio_original and precio_original > precio:
            descuento = round((1 - precio / precio_original) * 100)

        rating_match = re.search(rf'data-testid="{product_id}-rating".*?aria-label="([\d.]+)', block, re.S)
        rating = float(rating_match.group(1)) if rating_match else None

        products.append(
            {
                "tienda": STORES["liverpool"]["name"],
                "titulo": nombre,
                "marca": marca,
                "precio_mxn": precio,
                "precio_original_mxn": precio_original,
                "descuento_pct": descuento,
                "rating": rating,
                "link": (LIVERPOOL_BASE + href) if href and href.startswith("/") else href,
            }
        )
        if len(products) >= limit:
            break
    return products, len(ids)


def search_liverpool(query, limit):
    html = http_get_text(build_url(query))
    products, total = extract_products(html, limit)
    return products, total


def _vtex_price(product):
    """Precio mas bajo positivo entre los vendedores de un producto VTEX."""
    best = None
    for item in product.get("items") or []:
        for seller in item.get("sellers") or []:
            offer = seller.get("commertialOffer") or {}
            price = offer.get("Price")
            if price and price > 0 and (best is None or price < best["precio"]):
                best = {"precio": price, "lista": offer.get("ListPrice"), "vendedor": seller.get("sellerName")}
    return best


def search_vtex(store, query, limit):
    base = store["base"]
    url = (
        f"{base}/api/catalog_system/pub/products/search/?"
        + urllib.parse.urlencode(
            {"ft": query, "_from": 0, "_to": max(limit - 1, 0)}, quote_via=urllib.parse.quote
        )
    )
    data = http_get_json(url)
    products = []
    for product in data or []:
        offer = _vtex_price(product)
        if not offer:
            continue
        link = product.get("link")
        if link and link.startswith("/"):
            link = base + link
        original = offer.get("lista")
        precio = round(float(offer["precio"]), 2)
        original = round(float(original), 2) if original else None
        descuento = None
        if original and original > precio:
            descuento = round((1 - precio / original) * 100)
        products.append(
            {
                "tienda": store["name"],
                "titulo": html_lib.unescape(product.get("productName") or "").strip() or None,
                "marca": (product.get("brand") or "").strip() or None,
                "precio_mxn": precio,
                "precio_original_mxn": original if (original and original > precio) else None,
                "descuento_pct": descuento,
                "rating": None,
                "link": link,
                "vendedor": offer.get("vendedor"),
            }
        )
        if len(products) >= limit:
            break
    return products, len(data or [])


def search_store(key, query, limit):
    store = STORES[key]
    if store["kind"] == "vtex":
        return search_vtex(store, query, limit)
    return search_liverpool(query, limit)


def resolve_stores(selection):
    if not selection:
        return list(DEFAULT_STORES)
    chosen = []
    for raw in selection.split(","):
        key = raw.strip().lower()
        if key in STORES and key not in chosen:
            chosen.append(key)
    return chosen


def main(argv=None):
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except (ValueError, OSError):
            pass

    parser = argparse.ArgumentParser(description="Busqueda y comparacion de precios en tiendas mexicanas")
    parser.add_argument("--q", required=True, help="Busqueda (ej. 'audifonos bluetooth')")
    parser.add_argument("--limit", type=int, default=5, help="Resultados por tienda")
    parser.add_argument("--tiendas", help="Tiendas separadas por coma (Liverpool, Chedraui, OfficeMax)")
    args = parser.parse_args(argv)

    limit = max(1, min(args.limit, 20))
    keys = resolve_stores(args.tiendas)
    if not keys:
        raise SystemExit(
            "No hay tiendas validas. Opciones: " + ", ".join(s["name"] for s in STORES.values())
        )

    por_tienda = {}
    errores = {}
    total = {}
    for key in keys:
        store = STORES[key]
        try:
            products, found = search_store(key, args.q, limit)
            por_tienda[store["name"]] = products
            total[store["name"]] = found
        except (RuntimeError, ValueError, json.JSONDecodeError) as exc:
            por_tienda[store["name"]] = []
            errores[store["name"]] = str(exc)

    flat = [item for name in por_tienda for item in por_tienda[name]]
    if not flat:
        detail = "; ".join(f"{name}: {msg}" for name, msg in errores.items()) or "sin resultados"
        raise SystemExit(f"No se encontraron productos para '{args.q}' ({detail}).")

    print(
        json.dumps(
            {
                "source": "Busqueda de precios multi-tienda (Mexico)",
                "query": args.q,
                "tiendas": [STORES[key]["name"] for key in keys],
                "resultados_por_tienda": total,
                "results": flat,
                "por_tienda": por_tienda,
                "errores": errores,
                "nota": "Precios publicados al momento de la busqueda; la compra se hace en cada tienda.",
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
