#!/usr/bin/env python3
"""Busca autos usados/seminuevos en Mexico (Seminuevos.com).

Solo lectura y sin API key. Parsea los anuncios renderizados en HTML y calcula un
indice de confianza para compra/reventa (antiguedad, km/ano, precio vs. mediana).

Uso:
  python3 mx_used_car_search.py --marca nissan --modelo sentra --limit 8
  python3 mx_used_car_search.py --marca nissan --estado jalisco --precio-max 200000
  python3 mx_used_car_search.py --query "toyota corolla" --anio-min 2018
"""

import argparse
import datetime
import html
import json
import re
import sys
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request

BASE_URL = "https://www.seminuevos.com"
USER_AGENT = "mx-skill-used-car-search/1.0 (+https://github.com/Bitboy7/Mx-skill)"

OFFICIAL_LINKS = {
    "fuente": "https://www.seminuevos.com/usados",
    "repuve": "https://www2.repuve.gob.mx:8443/ciudadano/",
    "profeco": "https://www.profeco.gob.mx/",
    "amis_robo_vehiculos": "https://www.amis.org.mx/",
}

ESTADO_ALIASES = {
    "cdmx": "ciudad+de+mexico",
    "df": "ciudad+de+mexico",
    "edomex": "estado+de+mexico",
    "monterrey": "nuevo+leon-monterrey",
    "guadalajara": "jalisco-guadalajara",
    "zapopan": "jalisco-zapopan",
    "cancun": "quintana+roo-cancun",
    "merida": "yucatan-merida",
    "pachuca": "hidalgo-pachuca",
    "juarez": "chihuahua-juarez",
}

CARD_SPLIT = '<div class="group block">'
RE_ANCHOR = re.compile(r'aria-label="Ver ([^"]+)" href="(/vehicle/[^"]+)"')
RE_LOCATION = re.compile(r'<span class="truncate">([^<]+)</span>')
RE_YEAR = re.compile(r'class="text-sm font-bold text-foreground leading-tight">(\d{4})</p>')
RE_H3 = re.compile(r"<h3[^>]*>([^<]*)<!-- -->[^<]*<!-- -->([^<]*)</h3>")
RE_VERSION = re.compile(
    r'class="text-xs text-muted-foreground line-clamp-1 leading-tight" title="([^"]*)"'
)
RE_KM = re.compile(r"<span>([\d.,]+)\s*kms\.</span>")
RE_TRANS = re.compile(
    r'kms\.</span>.*?<span class="text-muted-foreground/80">[^<]*</span>\s*<span>([^<]+)</span>',
    re.DOTALL,
)
RE_PRICE = re.compile(
    r'<span class="text-lg font-semibold text-foreground">\$([\d.,]+)</span>'
)


# --------------------------------------------------------------------------- #
# Utilidades
# --------------------------------------------------------------------------- #
def slugify(text: str) -> str:
    """Convierte 'Nuevo León' en 'nuevo+leon' (formato de ruta del sitio)."""
    normalized = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    normalized = normalized.lower().strip()
    return re.sub(r"[^a-z0-9]+", "+", normalized).strip("+")


def normalize_estado(estado: str) -> str:
    alias = ESTADO_ALIASES.get(estado.strip().lower())
    return alias or slugify(estado)


def build_search_url(marca=None, modelo=None, estado=None, vendedor="dealer", page=1) -> str:
    segmentos = ["usados", normalize_estado(estado) if estado else "-", "autos", "-"]
    if marca:
        segmentos.append(slugify(marca))
    if modelo:
        segmentos.append(slugify(modelo))
    url = f"{BASE_URL}/" + "/".join(segmentos)
    params = []
    if vendedor == "dealer":
        params.append("seller=DEALER")
    if page and page > 1:
        params.append(f"page={page}")
    if params:
        url += "?" + "&".join(params)
    return url


def _to_int(value: str | None):
    if value is None:
        return None
    digits = re.sub(r"[^\d]", "", value)
    return int(digits) if digits else None


def _clean(text: str | None) -> str | None:
    if not text:
        return None
    return html.unescape(text).strip() or None


def parse_listings(page_html: str) -> list[dict]:
    """Extrae los anuncios del HTML renderizado (server-side), sin duplicados."""
    listings = []
    for card in page_html.split(CARD_SPLIT)[1:]:
        anchor = RE_ANCHOR.search(card)
        if not anchor:
            continue
        titulo, href = anchor.group(1), anchor.group(2)

        h3 = RE_H3.search(card)
        marca = _clean(h3.group(1)) if h3 else None
        modelo = _clean(h3.group(2)) if h3 else None

        year_m = RE_YEAR.search(card)
        km_m = RE_KM.search(card)
        price_m = RE_PRICE.search(card)
        location_m = RE_LOCATION.search(card)
        version_m = RE_VERSION.search(card)
        trans_m = RE_TRANS.search(card)

        listings.append(
            {
                "titulo": _clean(titulo),
                "marca": marca,
                "modelo": modelo,
                "version": _clean(version_m.group(1)) if version_m else None,
                "anio": int(year_m.group(1)) if year_m else None,
                "km": _to_int(km_m.group(1)) if km_m else None,
                "transmision": _clean(trans_m.group(1)) if trans_m else None,
                "precio_mxn": _to_int(price_m.group(1)) if price_m else None,
                "ubicacion": _clean(location_m.group(1)) if location_m else None,
                "url": f"{BASE_URL}{href}",
            }
        )
    return dedupe_listings(listings)


def dedupe_listings(listings: list[dict]) -> list[dict]:
    """El sitio repite un anuncio en varias secciones; conserva el registro más completo."""
    best: dict[str, dict] = {}
    order: list[str] = []
    for item in listings:
        url = item.get("url")
        if not url:
            continue
        if url not in best:
            best[url] = item
            order.append(url)
        elif _completeness(item) > _completeness(best[url]):
            best[url] = item
    return [best[url] for url in order]


def _completeness(item: dict) -> int:
    return sum(1 for value in item.values() if value not in (None, ""))


def median(values: list) -> float | None:
    clean = sorted(v for v in values if v is not None)
    if not clean:
        return None
    mid = len(clean) // 2
    if len(clean) % 2:
        return float(clean[mid])
    return (clean[mid - 1] + clean[mid]) / 2


def score_listing(listing: dict, mediana: float | None, current_year: int, dealer: bool):
    """Indice de confianza 0-100 con notas explicativas."""
    score = 40.0
    notas: list[str] = []

    anio = listing.get("anio")
    km = listing.get("km")
    precio = listing.get("precio_mxn")

    edad = None
    if anio:
        edad = max(1, current_year - anio)
        if edad <= 3:
            score += 20
        elif edad <= 6:
            score += 12
        elif edad <= 10:
            score += 5
        elif edad <= 15:
            score -= 8
        else:
            score -= 18
            notas.append("Más de 15 años: revisa refacciones, verificación y adeudos.")

    if km is not None and edad:
        km_por_anio = km / edad
        if km_por_anio <= 12000:
            score += 15
        elif km_por_anio <= 20000:
            score += 8
        elif km_por_anio <= 30000:
            pass
        else:
            score -= 12
            notas.append(f"Kilometraje alto para su edad (~{km_por_anio:,.0f} km/año).")

    if precio and mediana:
        ratio = precio / mediana
        if ratio < 0.7:
            score -= 10
            notas.append("Precio muy por debajo del mercado: verifica NIV, robo y adeudos.")
        elif ratio <= 1.15:
            score += 5
        elif ratio > 1.3:
            score -= 5
            notas.append("Precio por encima de la mediana del mercado.")

    if dealer:
        score += 10

    score = int(max(0, min(100, round(score))))
    nivel = "Alta" if score >= 75 else ("Media" if score >= 55 else "Baja")
    return score, nivel, notas


def build_payload(
    listings: list[dict],
    *,
    url: str,
    query: dict,
    page: int,
    limit: int,
    dealer: bool,
    error: str | None = None,
) -> dict:
    analizados = list(listings)
    mediana = median([item.get("precio_mxn") for item in analizados])
    current_year = datetime.date.today().year

    for item in analizados:
        score, nivel, notas = score_listing(item, mediana, current_year, dealer)
        item["confianza"] = score
        item["confianza_nivel"] = nivel
        item["notas"] = notas

    analizados.sort(key=lambda i: (-(i.get("confianza") or 0), i.get("precio_mxn") or 0))

    payload = {
        "source": "Seminuevos.com (anuncios publicos, sin API key)",
        "url": url,
        "query": query,
        "pagina": page,
        "vendedor": "dealer" if dealer else "todos",
        "total_analizados": len(analizados),
        "precio_mediana_mxn": int(mediana) if mediana else None,
        "results": analizados[:limit],
        "official_links": OFFICIAL_LINKS,
        "notas": [
            "Antes de comprar verifica el NIV en REPUVE y los adeudos de tenencia/refrendo.",
            "La confianza es una heuristica de anuncio (antiguedad, km/año, precio vs. mediana); no es una inspeccion mecanica.",
            "Confirma el precio y la disponibilidad en el anuncio original.",
        ],
    }
    if error:
        payload["notice"] = error
    return payload


# --------------------------------------------------------------------------- #
# HTTP
# --------------------------------------------------------------------------- #
def http_get(url: str, timeout: int = 20, attempts: int = 2) -> str:
    """Descarga la pagina con un reintento (el sitio es intermitentemente lento)."""
    last_error: Exception | None = None
    for attempt in range(attempts):
        request = urllib.request.Request(
            url,
            headers={
                "User-Agent": USER_AGENT,
                "Accept": "text/html,application/xhtml+xml",
                "Accept-Language": "es-MX,es;q=0.9",
            },
        )
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                return response.read().decode("utf-8", "ignore")
        except urllib.error.HTTPError:
            raise
        except (urllib.error.URLError, TimeoutError) as exc:
            last_error = exc
            if attempt + 1 < attempts:
                time.sleep(1.5)
    raise last_error if last_error else TimeoutError("sin respuesta")


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #
def build_parser():
    parser = argparse.ArgumentParser(description="Busca autos usados/seminuevos confiables en Mexico.")
    parser.add_argument("--marca", help="Marca (ej. nissan)")
    parser.add_argument("--modelo", help="Modelo (ej. sentra)")
    parser.add_argument("--estado", help="Estado o ciudad (ej. jalisco, monterrey)")
    parser.add_argument("--query", help="Texto libre: 'marca modelo'")
    parser.add_argument("--precio-max", dest="precio_max", type=int, help="Precio maximo MXN")
    parser.add_argument("--anio-min", dest="anio_min", type=int, help="Anio minimo")
    parser.add_argument("--km-max", dest="km_max", type=int, help="Kilometraje maximo")
    parser.add_argument("--vendedor", choices=["dealer", "todos"], default="dealer",
                        help="Agencias (dealer, default) o todos los vendedores")
    parser.add_argument("--pagina", type=int, default=1, help="Pagina de resultados")
    parser.add_argument("--limit", type=int, default=12, help="Numero de resultados")
    parser.add_argument("--json", action="store_true", help="Salida JSON (siempre activa)")
    return parser


def _resolve_query(args):
    marca = (args.marca or "").strip() or None
    modelo = (args.modelo or "").strip() or None
    if args.query and not marca:
        parts = args.query.split()
        marca = parts[0] if parts else None
        if len(parts) > 1 and not modelo:
            modelo = " ".join(parts[1:])
    return marca, modelo


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    marca, modelo = _resolve_query(args)

    if not marca:
        parser.error("indica --marca o --query (ej. --marca nissan --modelo sentra)")

    estado = args.estado
    query = {"marca": marca, "modelo": modelo, "estado": estado, "anio_min": args.anio_min,
             "km_max": args.km_max, "precio_max": args.precio_max}
    dealer = args.vendedor == "dealer"
    url = build_search_url(marca, modelo, estado, args.vendedor, args.pagina)

    try:
        page_html = http_get(url)
    except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError) as exc:
        print(f"No se pudo consultar Seminuevos.com: {exc}", file=sys.stderr)
        sys.exit(3)

    listings = parse_listings(page_html)

    if args.precio_max:
        listings = [i for i in listings if (i.get("precio_mxn") or 0) and i["precio_mxn"] <= args.precio_max]
    if args.anio_min:
        listings = [i for i in listings if (i.get("anio") or 0) >= args.anio_min]
    if args.km_max:
        listings = [i for i in listings if i.get("km") is not None and i["km"] <= args.km_max]

    error = None
    if not listings:
        if not parse_listings(page_html):
            error = "No se parsearon anuncios (posible cambio de estructura o bloqueo del sitio)."
        else:
            error = "Ningun anuncio cumple los filtros indicados."

    payload = build_payload(
        listings, url=url, query=query, page=args.pagina, limit=args.limit,
        dealer=dealer, error=error,
    )
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    if not payload["results"]:
        sys.exit(2)


if __name__ == "__main__":
    main()
