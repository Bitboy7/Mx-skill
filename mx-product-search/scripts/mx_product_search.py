#!/usr/bin/env python3
"""Busqueda de productos y precios en Liverpool Mexico.

Fuente publica: el buscador de Liverpool (www.liverpool.com.mx/tienda?s=...)
sirve HTML server-rendered con tarjetas de producto (`data-testid="<id>-card"`).
No requiere API key ni sesion. Mercado Libre dejo de permitir busqueda publica
(HTTP 403 desde abril de 2025), por eso se usa Liverpool.

Uso:
  python3 mx_product_search.py --q "audifonos bluetooth" --limit 5
"""

import argparse
import html as html_lib
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

BASE_URL = "https://www.liverpool.com.mx"
SEARCH_URL = BASE_URL + "/tienda"
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
)
HEADERS = {
    "User-Agent": USER_AGENT,
    "Accept": "text/html,application/xhtml+xml",
    "Accept-Language": "es-MX,es;q=0.9",
}

CARD_ID_RE = re.compile(r'data-testid="(\d+)-card"')
PRICE_RE = re.compile(r"\$\s*([\d,]+)(?:\.\d+)?")
TAG_RE = re.compile(r"<[^>]+>")
COMMENT_RE = re.compile(r"<!--.*?-->")
WS_RE = re.compile(r"\s+")


def http_get_text(url):
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return resp.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as exc:
        raise SystemExit(
            f"Liverpool respondio HTTP {exc.code}. Intenta de nuevo o busca en el portal: {SEARCH_URL}"
        ) from exc
    except urllib.error.URLError as exc:
        raise SystemExit(f"No se pudo consultar Liverpool: {exc.reason}") from exc


def build_url(query):
    return SEARCH_URL + "?" + urllib.parse.urlencode({"s": query})


def _clean(fragment):
    text = COMMENT_RE.sub(" ", fragment or "")
    text = TAG_RE.sub(" ", text)
    text = html_lib.unescape(text)
    return WS_RE.sub(" ", text).strip()


def _first_match(pattern, block):
    match = re.search(pattern, block, re.S)
    return _clean(match.group(1)) if match else None


def extract_products(html, limit):
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
                "titulo": nombre,
                "marca": marca,
                "precio_mxn": precio,
                "precio_original_mxn": precio_original,
                "descuento_pct": descuento,
                "rating": rating,
                "link": (BASE_URL + href) if href and href.startswith("/") else href,
            }
        )
        if len(products) >= limit:
            break
    return products, len(ids)


def build_payload(query, url, products, total_en_pagina):
    return {
        "source": "Liverpool Mexico (datos publicos del buscador)",
        "query": query,
        "url_busqueda": url,
        "resultados_en_pagina": total_en_pagina,
        "results": products,
        "nota": "Precios y disponibilidad pueden cambiar; la compra se hace en liverpool.com.mx.",
    }


def main(argv=None):
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except (ValueError, OSError):
            pass

    parser = argparse.ArgumentParser(description="Busqueda de productos en Liverpool Mexico")
    parser.add_argument("--q", required=True, help="Busqueda (ej. 'audifonos bluetooth')")
    parser.add_argument("--limit", type=int, default=5)
    args = parser.parse_args(argv)

    url = build_url(args.q)
    html = http_get_text(url)
    products, total = extract_products(html, args.limit)

    if not products:
        raise SystemExit(
            "No se encontraron productos para esa busqueda. Intenta con otras palabras o revisa el portal: "
            f"{SEARCH_URL}?s={urllib.parse.quote(args.q)}"
        )

    print(json.dumps(build_payload(args.q, url, products, total), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
