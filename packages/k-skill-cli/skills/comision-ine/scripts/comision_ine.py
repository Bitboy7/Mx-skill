#!/usr/bin/env python3
"""Candidatas y candidatos del INE (Mexico).

Fuente publica: datos estaticos JSON de la plataforma "Candidatas y Candidatos,
Conoceles" (candidaturas.ine.mx), sin API key.

Uso:
  python3 comision_ine.py --name "Claudia"
  python3 comision_ine.py --name "Xochitl" --tipo presidente
  python3 comision_ine.py --all --tipo diputados
"""

import argparse
import json
import urllib.request

BASE_URL = "https://candidaturas.ine.mx/cycc/documentos/json"
USER_AGENT = "k-skill-comision-ine/1.0 (+https://github.com/NomaDamas/k-skill)"

FILES = {
    "presidente": "presidentes.json",
    "senadores": "senadoresRP.json",
    "senadores_mr": "senadoresMR.json",
    "diputados": "diputadosRP.json",
    "diputados_mr": "diputadosMR.json",
}


def fetch_json(relative):
    url = f"{BASE_URL}/{relative}"
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.load(resp)
    except urllib.error.HTTPError as exc:
        raise SystemExit(
            f"No se pudo obtener {relative} (HTTP {exc.code}). "
            "Algunos archivos solo existen en anos de eleccion; prueba otro tipo de candidatura."
        ) from exc


def summarize(candidate):
    return {
        "nombre": candidate.get("nombreCandidato"),
        "partido": candidate.get("nombreAsociacion"),
        "sexo": candidate.get("sexo"),
        "edad": candidate.get("edad"),
        "tipo": candidate.get("tipoCandidato"),
        "propuestas": [
            p for p in [candidate.get("propuesta1"), candidate.get("propuesta2"), candidate.get("propuesta3")] if p
        ],
        "correo": candidate.get("correoElecPublico"),
    }


def main():
    parser = argparse.ArgumentParser(description="Candidatas y candidatos del INE")
    parser.add_argument("--name", help="Buscar por nombre (parcial, sin acentos)")
    parser.add_argument(
        "--tipo",
        choices=list(FILES.keys()),
        help="Tipo de candidatura (presidente, senadores, diputados, ...)",
    )
    parser.add_argument("--all", action="store_true", help="Listar todos (sin filtro de nombre)")
    parser.add_argument("--limit", type=int, default=20)
    args = parser.parse_args()

    if not args.all and not args.name:
        parser.error("Proporciona --name o --all.")

    tipos = [args.tipo] if args.tipo else list(FILES.keys())
    matches = []

    for tipo in tipos:
        data = fetch_json(FILES[tipo])
        candidates = data.get("candidatos") or []
        for candidate in candidates:
            if args.name and args.name.lower() not in (candidate.get("nombreCandidato") or "").lower():
                continue
            item = summarize(candidate)
            item["tipo_archivo"] = tipo
            matches.append(item)

    matches.sort(key=lambda c: c["nombre"] or "")

    print(json.dumps(
        {
            "source": "candidaturas.ine.mx (Candidatas y Candidatos, Conoceles)",
            "query": args.name,
            "total": len(matches),
            "results": matches[: args.limit],
        },
        ensure_ascii=False,
        indent=2,
    ))


if __name__ == "__main__":
    main()
