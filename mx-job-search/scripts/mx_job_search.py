#!/usr/bin/env python3
"""Vacantes de empleo en Mexico y LATAM.

Fuente publica: API de Vacantes Digitales (https://vacantesdigitales.com/api),
sin autenticacion ni API key. Enfocada en empleos de tecnologia e IA en LATAM
(incluye Mexico).

Uso:
  python3 mx_job_search.py "python"
  python3 mx_job_search.py "desarrollador" --limit 5 --json
  python3 mx_job_search.py "data" --category data --experience senior
"""

import argparse
import json
import urllib.parse
import urllib.request

API_URL = "https://vacantesdigitales.com/api/vacancies"
USER_AGENT = "k-skill-mx-job-search/1.0 (+https://github.com/Bitboy7/Mx-skill)"
SOURCE = "mx-job-search"

OFFICIAL_LINKS = {
    "vacantes_digitales": "https://vacantesdigitales.com/vacantes",
    "portal_del_empleo": "https://www.empleo.gob.mx/",
    "occ": "https://www.occ.com.mx/empleos/",
    "computrabajo": "https://www.computrabajo.com.mx/",
}

LOCATION_LABELS = {
    "REMOTE": "Remoto",
    "TELECOMMUTE": "Remoto",
    "TELEWORK": "Remoto",
    "HYBRID": "Híbrido",
    "ONSITE": "Presencial",
}

EMPLOYMENT_LABELS = {
    "FULL_TIME": "Tiempo completo",
    "PART_TIME": "Medio tiempo",
    "CONTRACT": "Contrato",
    "CONTRACTOR": "Contrato",
    "TEMPORARY": "Temporal",
    "INTERN": "Prácticas",
    "INTERNSHIP": "Prácticas",
}


def http_get_json(url, timeout=30):
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.load(resp)


def translate(mapping, value):
    if not value:
        return None
    return mapping.get(str(value).upper(), value)


def build_params(query, limit, page=1, category=None, experience=None, location_type=None):
    params = {"q": query, "limit": limit, "page": page, "source": SOURCE}
    if category:
        params["category"] = category
    if experience:
        params["experience"] = experience
    if location_type:
        params["location_type"] = location_type
    return params


def normalize_item(item):
    company = item.get("company") or {}
    return {
        "puesto": item.get("position") or item.get("title"),
        "empresa": company.get("name"),
        "categoria": item.get("job_category"),
        "experiencia": item.get("experience"),
        "modalidad": translate(LOCATION_LABELS, item.get("job_location_type")),
        "tipo_empleo": translate(EMPLOYMENT_LABELS, item.get("employment_type")),
        "ubicacion": item.get("address_locality") or item.get("address_country"),
        "salario": item.get("salary"),
        "publicado": item.get("date_posted_iso") or item.get("post_date"),
        "habilidades": item.get("skills") or [],
        "url": item.get("post_url"),
    }


def fetch_jobs(query, limit, page=1, category=None, experience=None, location_type=None):
    params = build_params(query, limit, page, category, experience, location_type)
    url = API_URL + "?" + urllib.parse.urlencode(params)
    payload = http_get_json(url)
    return [normalize_item(item) for item in (payload.get("data") or [])]


def build_payload(query, results, error=None):
    payload = {
        "source": "Vacantes Digitales (API pública, sin API key)",
        "query": query,
        "results": results,
        "official_links": OFFICIAL_LINKS,
    }
    if error:
        payload["notice"] = (
            "No se pudo consultar la API pública de vacantes; usa los portales oficiales. "
            f"Detalle: {error}"
        )
    return payload


def format_text(payload):
    lines = [f"Vacantes para '{payload.get('query')}':"]
    results = payload.get("results") or []
    if not results:
        lines.append("• Sin resultados en la API pública.")
    for row in results:
        details = " · ".join(str(d) for d in (row.get("modalidad"), row.get("tipo_empleo"), row.get("ubicacion")) if d)
        lines.append(
            f"• {row.get('puesto')} — {row.get('empresa') or 'N/D'}\n"
            f"  {details}\n"
            f"  {row.get('url') or OFFICIAL_LINKS['vacantes_digitales']}"
        )
    lines.append("")
    lines.append("Fuente: " + payload.get("source", ""))
    lines.append("Más vacantes: " + OFFICIAL_LINKS["vacantes_digitales"])
    if payload.get("notice"):
        lines.append(payload["notice"])
    return "\n".join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Vacantes de empleo en México/LATAM (Vacantes Digitales)")
    parser.add_argument("query", nargs="?", help="Puesto, skill o empresa a buscar")
    parser.add_argument("--query", dest="query_opt", help="Palabra clave (alternativa posicional)")
    parser.add_argument("--limit", type=int, default=5, help="Número de resultados (1-50)")
    parser.add_argument("--page", type=int, default=1, help="Página de resultados")
    parser.add_argument("--category", default=None, help="Categoría (ej. desarrollo, data, devops)")
    parser.add_argument("--experience", default=None, help="Nivel (junior, mid, senior, lead)")
    parser.add_argument("--location-type", default=None, help="Modalidad (remoto, hibrido, presencial)")
    parser.add_argument("--json", action="store_true", help="Salida JSON cruda")
    args = parser.parse_args(argv)

    query = (args.query_opt or args.query or "").strip()
    if not query:
        parser.error("Proporciona una palabra clave (posicional o --query).")
    if not 1 <= args.limit <= 50:
        parser.error("--limit debe estar entre 1 y 50")
    if args.page < 1:
        parser.error("--page debe ser mayor o igual a 1")

    try:
        results = fetch_jobs(
            query, args.limit, args.page, args.category, args.experience, args.location_type
        )
        payload = build_payload(query, results)
    except Exception as exc:  # noqa: BLE001
        payload = build_payload(query, [], error=str(exc))

    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(format_text(payload))


if __name__ == "__main__":
    main()
