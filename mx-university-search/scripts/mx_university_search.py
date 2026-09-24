#!/usr/bin/env python3
"""Universidades de Mexico y sus carreras.

Catalogo curado de las principales instituciones de educacion superior de
Mexico (publicas y privadas) con carreras representativas y el enlace oficial
de cada institucion. No existe una API publica estable de toda la oferta
educativa, por lo que este helper mantiene un catalogo de referencia; el enlace
oficial es la fuente de verdad.

Uso:
  python3 mx_university_search.py "medicina"
  python3 mx_university_search.py "UNAM" --json
  python3 mx_university_search.py "ingenieria" --tipo publica --estado Jalisco
  python3 mx_university_search.py --list
"""

import argparse
import json
import unicodedata

CATALOG = [
    {
        "nombre": "Universidad Nacional Autónoma de México (UNAM)",
        "tipo": "pública",
        "estado": "Ciudad de México",
        "ciudad": "Ciudad de México",
        "sitio": "https://www.unam.mx",
        "carreras": [
            "Medicina", "Derecho", "Ingeniería en Computación", "Administración",
            "Arquitectura", "Psicología", "Contaduría", "Economía", "Biología", "Letras Hispánicas",
        ],
    },
    {
        "nombre": "Instituto Politécnico Nacional (IPN)",
        "tipo": "pública",
        "estado": "Ciudad de México",
        "ciudad": "Ciudad de México",
        "sitio": "https://www.ipn.mx",
        "carreras": [
            "Ingeniería en Sistemas Computacionales", "Medicina", "Ingeniería Civil",
            "Administración", "Contador Público", "Arquitectura", "Ingeniería en Inteligencia Artificial",
            "Ingeniería Mecánica",
        ],
    },
    {
        "nombre": "Universidad Autónoma Metropolitana (UAM)",
        "tipo": "pública",
        "estado": "Ciudad de México",
        "ciudad": "Ciudad de México",
        "sitio": "https://www.uam.mx",
        "carreras": [
            "Medicina", "Ingeniería en Computación", "Administración", "Derecho",
            "Diseño", "Psicología", "Economía", "Biología",
        ],
    },
    {
        "nombre": "Universidad Autónoma de Nuevo León (UANL)",
        "tipo": "pública",
        "estado": "Nuevo León",
        "ciudad": "Monterrey",
        "sitio": "https://www.uanl.mx",
        "carreras": [
            "Medicina", "Derecho", "Ingeniería Mecánica Eléctrica", "Administración",
            "Contador Público", "Arquitectura", "Psicología",
        ],
    },
    {
        "nombre": "Universidad de Guadalajara (UdeG)",
        "tipo": "pública",
        "estado": "Jalisco",
        "ciudad": "Guadalajara",
        "sitio": "https://www.udg.mx",
        "carreras": [
            "Medicina", "Derecho", "Ingeniería en Computación", "Administración",
            "Psicología", "Arquitectura", "Contaduría",
        ],
    },
    {
        "nombre": "Benemérita Universidad Autónoma de Puebla (BUAP)",
        "tipo": "pública",
        "estado": "Puebla",
        "ciudad": "Puebla",
        "sitio": "https://www.buap.mx",
        "carreras": [
            "Medicina", "Derecho", "Ingeniería en Computación", "Administración",
            "Contaduría", "Arquitectura",
        ],
    },
    {
        "nombre": "Universidad Veracruzana (UV)",
        "tipo": "pública",
        "estado": "Veracruz",
        "ciudad": "Xalapa",
        "sitio": "https://www.uv.mx",
        "carreras": [
            "Medicina", "Derecho", "Ingeniería en Sistemas Computacionales",
            "Administración", "Psicología", "Contaduría",
        ],
    },
    {
        "nombre": "Universidad Autónoma de Yucatán (UADY)",
        "tipo": "pública",
        "estado": "Yucatán",
        "ciudad": "Mérida",
        "sitio": "https://www.uady.mx",
        "carreras": [
            "Medicina", "Derecho", "Ingeniería en Software", "Administración",
            "Contaduría", "Psicología",
        ],
    },
    {
        "nombre": "Universidad Autónoma de Querétaro (UAQ)",
        "tipo": "pública",
        "estado": "Querétaro",
        "ciudad": "Santiago de Querétaro",
        "sitio": "https://www.uaq.mx",
        "carreras": ["Medicina", "Derecho", "Ingeniería en Software", "Administración", "Contaduría"],
    },
    {
        "nombre": "Universidad Autónoma de Baja California (UABC)",
        "tipo": "pública",
        "estado": "Baja California",
        "ciudad": "Mexicali",
        "sitio": "https://www.uabc.mx",
        "carreras": ["Medicina", "Derecho", "Ingeniería en Computación", "Administración", "Contaduría"],
    },
    {
        "nombre": "Universidad de Sonora (UNISON)",
        "tipo": "pública",
        "estado": "Sonora",
        "ciudad": "Hermosillo",
        "sitio": "https://www.unison.mx",
        "carreras": ["Medicina", "Derecho", "Ingeniería en Sistemas", "Administración", "Contaduría"],
    },
    {
        "nombre": "Universidad Autónoma del Estado de México (UAEMéx)",
        "tipo": "pública",
        "estado": "Estado de México",
        "ciudad": "Toluca",
        "sitio": "https://www.uaemex.mx",
        "carreras": ["Medicina", "Derecho", "Ingeniería en Computación", "Contaduría", "Administración"],
    },
    {
        "nombre": "Universidad Autónoma de Chihuahua (UACH)",
        "tipo": "pública",
        "estado": "Chihuahua",
        "ciudad": "Chihuahua",
        "sitio": "https://www.uach.mx",
        "carreras": ["Medicina", "Derecho", "Ingeniería en Software", "Administración"],
    },
    {
        "nombre": "Universidad Michoacana de San Nicolás de Hidalgo (UMSNH)",
        "tipo": "pública",
        "estado": "Michoacán",
        "ciudad": "Morelia",
        "sitio": "https://www.umich.mx",
        "carreras": ["Medicina", "Derecho", "Ingeniería en Computación", "Contaduría"],
    },
    {
        "nombre": "Universidad Autónoma de San Luis Potosí (UASLP)",
        "tipo": "pública",
        "estado": "San Luis Potosí",
        "ciudad": "San Luis Potosí",
        "sitio": "https://www.uaslp.mx",
        "carreras": ["Medicina", "Derecho", "Ingeniería en Computación", "Administración"],
    },
    {
        "nombre": "Universidad Autónoma de Sinaloa (UAS)",
        "tipo": "pública",
        "estado": "Sinaloa",
        "ciudad": "Culiacán",
        "sitio": "https://www.uas.edu.mx",
        "carreras": ["Medicina", "Derecho", "Ingeniería en Software", "Contaduría"],
    },
    {
        "nombre": "Universidad Autónoma de Tamaulipas (UAT)",
        "tipo": "pública",
        "estado": "Tamaulipas",
        "ciudad": "Ciudad Victoria",
        "sitio": "https://www.uat.edu.mx",
        "carreras": ["Medicina", "Derecho", "Ingeniería en Computación", "Administración"],
    },
    {
        "nombre": "Universidad Autónoma de Aguascalientes (UAA)",
        "tipo": "pública",
        "estado": "Aguascalientes",
        "ciudad": "Aguascalientes",
        "sitio": "https://www.uaa.mx",
        "carreras": ["Medicina", "Derecho", "Ingeniería en Computación", "Contaduría"],
    },
    {
        "nombre": "Universidad de Colima (UdeC)",
        "tipo": "pública",
        "estado": "Colima",
        "ciudad": "Colima",
        "sitio": "https://www.ucol.mx",
        "carreras": ["Medicina", "Derecho", "Ingeniería en Computación", "Administración"],
    },
    {
        "nombre": "Universidad Autónoma de Campeche (UACam)",
        "tipo": "pública",
        "estado": "Campeche",
        "ciudad": "San Francisco de Campeche",
        "sitio": "https://www.uacam.mx",
        "carreras": ["Medicina", "Derecho", "Ingeniería en Sistemas", "Contaduría"],
    },
    {
        "nombre": "Tecnológico Nacional de México (TecNM)",
        "tipo": "pública",
        "estado": "Nacional",
        "ciudad": "Varias sedes",
        "sitio": "https://www.tecnm.mx",
        "carreras": [
            "Ingeniería en Sistemas Computacionales", "Ingeniería Industrial",
            "Ingeniería Mecánica", "Ingeniería Electrónica", "Administración",
        ],
    },
    {
        "nombre": "Universidad Nacional Abierta y a Distancia de México (UnADM)",
        "tipo": "pública",
        "estado": "Nacional",
        "ciudad": "A distancia",
        "sitio": "https://www.unadmexico.mx",
        "carreras": [
            "Ingeniería en Desarrollo de Software", "Administración de Empresas",
            "Derecho", "Mercadotecnia", "Gestión de Servicios de Salud",
        ],
    },
    {
        "nombre": "Universidad Autónoma de la Ciudad de México (UACM)",
        "tipo": "pública",
        "estado": "Ciudad de México",
        "ciudad": "Ciudad de México",
        "sitio": "https://www.uacm.edu.mx",
        "carreras": ["Medicina", "Derecho", "Ingeniería en Sistemas", "Ciencias Sociales"],
    },
    {
        "nombre": "Universidad Pedagógica Nacional (UPN)",
        "tipo": "pública",
        "estado": "Ciudad de México",
        "ciudad": "Ciudad de México",
        "sitio": "https://www.upn.mx",
        "carreras": ["Pedagogía", "Psicología Educativa", "Educación"],
    },
    {
        "nombre": "Instituto Tecnológico y de Estudios Superiores de Monterrey (ITESM / Tec de Monterrey)",
        "tipo": "privada",
        "estado": "Nuevo León",
        "ciudad": "Monterrey",
        "sitio": "https://www.tec.mx",
        "carreras": [
            "Ingeniería en Sistemas Computacionales", "Medicina", "Administración de Empresas",
            "Ingeniería Mecatrónica", "Derecho", "Arquitectura", "Ciencia de Datos",
        ],
    },
    {
        "nombre": "Instituto Tecnológico Autónomo de México (ITAM)",
        "tipo": "privada",
        "estado": "Ciudad de México",
        "ciudad": "Ciudad de México",
        "sitio": "https://www.itam.mx",
        "carreras": [
            "Economía", "Derecho", "Administración", "Ciencia de Datos",
            "Matemáticas Aplicadas", "Ingeniería en Computación", "Finanzas",
        ],
    },
    {
        "nombre": "Universidad Iberoamericana (IBERO)",
        "tipo": "privada",
        "estado": "Ciudad de México",
        "ciudad": "Ciudad de México",
        "sitio": "https://www.ibero.mx",
        "carreras": [
            "Derecho", "Psicología", "Administración", "Diseño",
            "Comunicación", "Ingeniería en Sistemas",
        ],
    },
    {
        "nombre": "Universidad Anáhuac",
        "tipo": "privada",
        "estado": "Ciudad de México",
        "ciudad": "Ciudad de México",
        "sitio": "https://www.anahuac.mx",
        "carreras": ["Medicina", "Derecho", "Administración", "Comunicación", "Ingeniería en Sistemas"],
    },
    {
        "nombre": "Universidad Panamericana (UP)",
        "tipo": "privada",
        "estado": "Ciudad de México",
        "ciudad": "Ciudad de México",
        "sitio": "https://www.up.edu.mx",
        "carreras": ["Medicina", "Derecho", "Administración", "Ingeniería en Computación", "Filosofía"],
    },
    {
        "nombre": "Universidad La Salle",
        "tipo": "privada",
        "estado": "Ciudad de México",
        "ciudad": "Ciudad de México",
        "sitio": "https://lasalle.mx",
        "carreras": ["Medicina", "Derecho", "Administración", "Ingeniería en Software", "Diseño"],
    },
    {
        "nombre": "Universidad de las Américas Puebla (UDLAP)",
        "tipo": "privada",
        "estado": "Puebla",
        "ciudad": "San Andrés Cholula",
        "sitio": "https://www.udlap.mx",
        "carreras": [
            "Ingeniería en Sistemas", "Administración", "Derecho",
            "Relaciones Internacionales", "Arquitectura",
        ],
    },
    {
        "nombre": "Instituto Tecnológico y de Estudios Superiores de Occidente (ITESO)",
        "tipo": "privada",
        "estado": "Jalisco",
        "ciudad": "Guadalajara",
        "sitio": "https://www.iteso.mx",
        "carreras": ["Ingeniería en Sistemas", "Administración", "Psicología", "Comunicación", "Diseño"],
    },
    {
        "nombre": "Universidad del Valle de México (UVM)",
        "tipo": "privada",
        "estado": "Nacional",
        "ciudad": "Varias sedes",
        "sitio": "https://www.uvm.mx",
        "carreras": ["Medicina", "Derecho", "Administración", "Ingeniería en Sistemas"],
    },
    {
        "nombre": "Universidad Tecnológica de México (UNITEC)",
        "tipo": "privada",
        "estado": "Nacional",
        "ciudad": "Varias sedes",
        "sitio": "https://www.unitec.mx",
        "carreras": ["Administración", "Ingeniería en Sistemas", "Contaduría", "Mercadotecnia"],
    },
]

NOTE = (
    "Catálogo de referencia de las principales instituciones; no es exhaustivo. "
    "Cada universidad puede ofrecer más carreras: consulta el enlace oficial (oferta educativa)."
)


def strip_accents(text):
    return "".join(c for c in unicodedata.normalize("NFKD", text) if not unicodedata.combining(c))


def search_universities(query, tipo=None, estado=None, catalog=None):
    catalog = catalog if catalog is not None else CATALOG
    needle = strip_accents(query.lower())
    tipo_norm = strip_accents(tipo.lower()) if tipo else None
    estado_norm = strip_accents(estado.lower()) if estado else None
    results = []
    for uni in catalog:
        if tipo_norm and strip_accents(uni["tipo"].lower()) != tipo_norm:
            continue
        if estado_norm and estado_norm not in strip_accents(uni["estado"].lower()):
            continue
        haystack = strip_accents(
            " ".join([uni["nombre"], uni["tipo"], uni["estado"], uni["ciudad"]] + uni["carreras"]).lower()
        )
        if needle in haystack:
            results.append(uni)
    return results


def build_payload(results, query=None, list_all=False):
    return {
        "source": "Catálogo curado de universidades de México (enlaces oficiales)",
        "modo": "lista" if list_all else "busqueda",
        "query": query,
        "note": NOTE,
        "results": results,
    }


def format_text(payload):
    results = payload.get("results") or []
    if not results:
        return f"No se encontraron universidades para '{payload.get('query')}'. Prueba otra carrera o universidad."
    lines = []
    for uni in results:
        carreras = ", ".join(uni["carreras"])
        lines.append(
            f"• {uni['nombre']} [{uni['tipo']}] — {uni['ciudad']}, {uni['estado']}\n"
            f"   Carreras: {carreras}\n"
            f"   Sitio: {uni['sitio']}"
        )
    lines.append("")
    lines.append(payload.get("note", ""))
    return "\n".join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Universidades de México y sus carreras")
    parser.add_argument("query", nargs="?", help="Universidad o carrera (ej. UNAM, medicina)")
    parser.add_argument("--query", dest="query_opt", help="Palabra clave (alternativa posicional)")
    parser.add_argument("--tipo", default=None, help="Tipo de institución: pública o privada")
    parser.add_argument("--estado", default=None, help="Estado (ej. Jalisco)")
    parser.add_argument("--list", action="store_true", help="Listar todas las universidades")
    parser.add_argument("--json", action="store_true", help="Salida JSON cruda")
    args = parser.parse_args(argv)

    if args.list:
        results = search_universities("", tipo=args.tipo, estado=args.estado)
        payload = build_payload(results, list_all=True)
    else:
        query = (args.query_opt or args.query or "").strip()
        if not query and not args.tipo and not args.estado:
            parser.error("Proporciona una universidad/carrera o usa --list.")
        results = search_universities(query, tipo=args.tipo, estado=args.estado)
        payload = build_payload(results, query=query or None)

    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(format_text(payload))


if __name__ == "__main__":
    main()
