#!/usr/bin/env python3
"""Busqueda de inmuebles en Mexico (renta/venta) via Inmuebles24.

Fuente publica: Inmuebles24 (Navent) sirve la busqueda como HTML con el estado
de la aplicacion embebido en `window.__PRELOADED_STATE__` (`listStore.listPostings`).
No requiere API key ni sesion. Mercado Libre Inmuebles dejo de permitir busqueda
publica (HTTP 403 desde abril de 2025), por eso se usa Inmuebles24.

Uso:
  python3 mx_real_estate.py --q "departamento polanco" --tipo venta --limit 5
  python3 mx_real_estate.py --q "casa acapulco" --tipo renta
"""

import argparse
import json
import re
import sys
import unicodedata
import urllib.error
import urllib.parse
import urllib.request

BASE_URL = "https://www.inmuebles24.com"
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
)
HEADERS = {
    "User-Agent": USER_AGENT,
    "Accept": "text/html,application/xhtml+xml",
    "Accept-Language": "es-MX,es;q=0.9",
}

# Palabra clave -> slug de tipo de inmueble usado por Inmuebles24.
TIPO_SLUGS = {
    "departamento": "departamentos",
    "depto": "departamentos",
    "depa": "departamentos",
    "casa": "casas",
    "terreno": "terrenos",
    "oficina": "oficinas",
    "local": "locales-comerciales",
    "bodega": "bodegas",
    "ph": "phs",
    "cochera": "cocheras",
    "estacionamiento": "cocheras",
    "edificio": "edificios",
    "consultorio": "consultorios",
}
OPERACION_RENTA = {"renta", "rentar", "rento", "alquiler", "alquilar", "alquilo"}
OPERACION_VENTA = {"venta", "vender", "vendo", "comprar", "compra"}

PORTALES_ALTERNATIVOS = [
    "https://www.inmuebles24.com/",
    "https://www.vivanuncios.com.mx/",
    "https://www.propiedades.com/",
]

# Inmuebles24 resuelve el slug de zona de forma literal; algunos nombres comunes
# caen en otra localidad homonima (p. ej. "acapulco" -> Acapulco, B.C.). Este
# mapa corrige los casos mas frecuentes a su slug canonico en el portal.
ZONA_ALIASES = {
    "acapulco": "acapulco-de-juarez",
    "cdmx": "ciudad-de-mexico",
    "df": "distrito-federal",
    "valle-de-mexico": "ciudad-de-mexico",
    "edomex": "estado-de-mexico",
    "riviera-maya": "playa-del-carmen",
}

FEATURE_LABELS = {
    "recamaras": ("recamara", "recamaras", "dormitorio", "dormitorios"),
    "banos": ("banos", "bano"),
    "superficie_construida": ("superficie construida", "superficie construccion", "construidos"),
    "superficie_terreno": ("terreno", "superficie total", "superficie del terreno"),
    "estacionamientos": ("estacionamientos", "estacionamiento", "cocheras"),
    "antiguedad": ("antiguedad",),
}


def http_get_text(url):
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return resp.read().decode("utf-8", "replace"), resp.geturl()
    except urllib.error.HTTPError as exc:
        raise SystemExit(
            f"Inmuebles24 respondio HTTP {exc.code}. Intenta de nuevo o usa los portales: "
            f"{', '.join(PORTALES_ALTERNATIVOS)}"
        ) from exc
    except urllib.error.URLError as exc:
        raise SystemExit(f"No se pudo consultar Inmuebles24: {exc.reason}") from exc


def strip_accents(text):
    normalized = unicodedata.normalize("NFKD", text or "")
    return "".join(ch for ch in normalized if not unicodedata.combining(ch))


def slugify(text):
    ascii_text = strip_accents(text or "").lower()
    ascii_text = re.sub(r"[^a-z0-9]+", "-", ascii_text)
    return ascii_text.strip("-")


def extract_preloaded_state(html):
    """Extrae y parsea el objeto JSON de `window.__PRELOADED_STATE__`."""
    marker = "__PRELOADED_STATE__"
    start = html.find(marker)
    if start < 0:
        return None
    equals = html.find("=", start)
    if equals < 0:
        return None
    i = equals + 1
    while i < len(html) and html[i] in " \t\r\n":
        i += 1
    if i >= len(html) or html[i] != "{":
        return None
    depth = 0
    in_string = False
    escaped = False
    j = i
    while j < len(html):
        ch = html[j]
        if in_string:
            if escaped:
                escaped = False
            elif ch == "\\":
                escaped = True
            elif ch == '"':
                in_string = False
        else:
            if ch == '"':
                in_string = True
            elif ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    try:
                        return json.loads(html[i : j + 1])
                    except json.JSONDecodeError:
                        return None
        j += 1
    return None


def parse_query(query, tipo):
    """Deriva (tipo_slug, operacion, zona_slug) de una busqueda libre."""
    words = [w for w in re.split(r"[^0-9A-Za-zÁÉÍÓÚÜÑáéíóúüñ]+", query or "") if w]
    tipo_slug = "inmuebles"
    operacion = tipo if tipo in ("venta", "renta") else "venta"
    zona_words = []
    for word in words:
        key = strip_accents(word).lower()
        if key in OPERACION_RENTA:
            operacion = "renta"
            continue
        if key in OPERACION_VENTA:
            operacion = "venta"
            continue
        if key in TIPO_SLUGS:
            tipo_slug = TIPO_SLUGS[key]
            continue
        zona_words.append(word)
    zona = slugify(" ".join(zona_words))
    zona = ZONA_ALIASES.get(zona, zona)
    return tipo_slug, operacion, zona


def build_url(tipo_slug, operacion, zona):
    if zona:
        return f"{BASE_URL}/{tipo_slug}-en-{operacion}-en-{zona}.html"
    return f"{BASE_URL}/{tipo_slug}-en-{operacion}.html"


def fetch_listings(url):
    html, final_url = http_get_text(url)
    state = extract_preloaded_state(html)
    postings = (((state or {}).get("listStore") or {}).get("listPostings")) or []
    return postings, final_url


def _feature_map(posting):
    features = {}
    for group in (posting.get("mainFeatures"), posting.get("generalFeatures"), posting.get("features")):
        if not isinstance(group, dict):
            continue
        for feat in group.values():
            if isinstance(feat, dict) and feat.get("label"):
                features[strip_accents(str(feat["label"])).lower()] = feat
    return features


def _feature_value(features, keys):
    for key in keys:
        if key in features:
            value = features[key].get("value")
            measure = features[key].get("measure")
            if value in (None, ""):
                continue
            return f"{value} {measure}".strip() if measure else str(value)
    return None


def _price_info(posting):
    for entry in posting.get("priceOperationTypes") or []:
        prices = entry.get("prices") or []
        if not prices:
            continue
        price = prices[0]
        currency = price.get("currency") or price.get("currencyId")
        moneda = {"MN": "MXN", "MXN": "MXN", "USD": "USD"}.get(currency, currency)
        formatted = price.get("formattedAmount")
        amount = price.get("amount")
        if formatted:
            precio = f"${formatted} {moneda}".strip()
        elif amount is not None:
            precio = f"${amount:,.2f} {moneda}".strip()
        else:
            precio = None
        return {
            "operacion": ((entry.get("operationType") or {}).get("name")),
            "precio": precio,
            "precio_valor": amount,
            "moneda": moneda,
        }
    return {"operacion": None, "precio": None, "precio_valor": None, "moneda": None}


def _location_chain(posting):
    location = ((posting.get("postingLocation") or {}).get("location")) or {}
    names = []
    current = location
    while isinstance(current, dict):
        if current.get("name"):
            names.append(current["name"])
        current = current.get("parent")
    return names


def summarize(posting):
    features = _feature_map(posting)
    price = _price_info(posting)
    names = _location_chain(posting)
    address = ((posting.get("house") or {}).get("address") or {}).get("name")
    expenses = posting.get("expenses") or {}
    mantenimiento = None
    if expenses.get("amount"):
        mantenimiento = f"${expenses.get('formattedAmount') or expenses.get('amount')} {expenses.get('currency') or ''}".strip()
    url = posting.get("url")
    link = url if (url or "").startswith("http") else (BASE_URL + url if url else None)
    return {
        "titulo": posting.get("title"),
        "tipo": ((posting.get("realEstateType") or {}).get("name")),
        "operacion": price["operacion"],
        "precio": price["precio"],
        "precio_valor": price["precio_valor"],
        "moneda": price["moneda"],
        "dormitorios": _feature_value(features, FEATURE_LABELS["recamaras"]),
        "banos": _feature_value(features, FEATURE_LABELS["banos"]),
        "superficie_m2": _feature_value(features, FEATURE_LABELS["superficie_construida"]),
        "superficie_terreno_m2": _feature_value(features, FEATURE_LABELS["superficie_terreno"]),
        "estacionamientos": _feature_value(features, FEATURE_LABELS["estacionamientos"]),
        "antiguedad": _feature_value(features, FEATURE_LABELS["antiguedad"]),
        "ubicacion": ", ".join(names) or None,
        "direccion": address,
        "inmobiliaria": ((posting.get("publisher") or {}).get("name")),
        "mantenimiento": mantenimiento,
        "link": link,
    }


def build_payload(query, tipo, url, final_url, postings, limit, nota=None):
    results = [summarize(p) for p in postings[:limit]]
    notas = []
    if nota:
        notas.append(nota)
    if final_url.rstrip("/") != url.rstrip("/"):
        notas.append(
            "La zona no se reconocio como filtro de Inmuebles24; se muestran resultados generales. "
            "Prueba con el nombre de la ciudad o colonia tal como aparece en el portal."
        )
    payload = {
        "source": "Inmuebles24 (datos publicos de los anuncios)",
        "query": query,
        "tipo": tipo,
        "url_busqueda": url,
        "resultados_en_pagina": len(postings),
        "results": results,
        "portales_alternativos": PORTALES_ALTERNATIVOS,
    }
    if notas:
        payload["nota"] = " ".join(notas)
    return payload


def buscar(query, tipo, limit):
    """Resuelve la busqueda y devuelve el payload, o None si no hay resultados."""
    tipo_slug, operacion, zona = parse_query(query, tipo)
    url = build_url(tipo_slug, operacion, zona)
    postings, final_url = fetch_listings(url)
    nota = None
    if not postings and tipo_slug != "inmuebles":
        url = build_url("inmuebles", operacion, zona)
        postings, final_url = fetch_listings(url)
        nota = f"No hubo resultados de '{tipo_slug}'; se muestran inmuebles en general en la zona."
    if not postings:
        return None
    return build_payload(query, tipo, url, final_url, postings, limit, nota)


def main(argv=None):
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except (ValueError, OSError):
            pass

    parser = argparse.ArgumentParser(description="Busqueda de inmuebles en Mexico (Inmuebles24)")
    parser.add_argument("--q", required=True, help="Busqueda (ej. 'departamento polanco')")
    parser.add_argument("--tipo", choices=["venta", "renta"], default="venta")
    parser.add_argument("--limit", type=int, default=5)
    args = parser.parse_args(argv)

    payload = buscar(args.q, args.tipo, args.limit)
    if payload is None:
        raise SystemExit(
            "No se encontraron inmuebles para esa busqueda. Prueba otra zona o revisa los portales: "
            f"{', '.join(PORTALES_ALTERNATIVOS)}"
        )

    print(json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
