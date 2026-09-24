#!/usr/bin/env python3
"""Información de los Programas para el Bienestar de México.

Fuente: portal oficial https://www.programasparaelbienestar.gob.mx/.
Este helper mantiene un catálogo curado de los programas federales vigentes
(nombre, perfil, requisitos, tipo de apoyo y enlace oficial) para responder
rápido sin depender de scraping. Los montos y requisitos pueden cambiar con las
reglas de operación vigentes: el enlace oficial es la fuente de verdad.

Uso:
  python3 beneficios_programas.py "pensión"
  python3 beneficios_programas.py --list
  python3 beneficios_programas.py "beca" --categoria jóvenes --json
"""

import argparse
import json
import unicodedata

PORTAL = "https://www.programasparaelbienestar.gob.mx"

CATALOG = [
    {
        "nombre": "Pensión para el Bienestar de las Personas Adultas Mayores",
        "categoria": "adultos mayores",
        "perfil": "Personas de 65 años o más que residen en México",
        "requisitos": ["Tener 65 años en adelante", "Residir en México"],
        "apoyo": "Apoyo económico bimestral entregado de forma directa a la tarjeta del Banco del Bienestar.",
        "monto": "Consultar monto vigente en el enlace oficial.",
        "convocatoria": False,
        "enlace": PORTAL + "/programas/adultos-mayores/pension-para-personas-adultas-mayores/",
    },
    {
        "nombre": "Pensión Mujeres Bienestar",
        "categoria": "mujeres",
        "perfil": "Mujeres de 60 a 64 años, mexicanas",
        "requisitos": ["Tener entre 60 y 64 años", "Ser mexicana"],
        "apoyo": "Apoyo económico bimestral para mujeres de 60 a 64 años.",
        "monto": "Consultar monto vigente en el enlace oficial.",
        "convocatoria": False,
        "enlace": PORTAL + "/programas/mujeres/pension-mujeres-bienestar/",
    },
    {
        "nombre": "Pensión para Personas con Discapacidad",
        "categoria": "personas con discapacidad",
        "perfil": "Personas con discapacidad permanente",
        "requisitos": ["Tener discapacidad permanente", "Presentar certificado o constancia médica"],
        "apoyo": "Apoyo económico para personas con discapacidad permanente.",
        "monto": "Consultar monto vigente en el enlace oficial.",
        "convocatoria": False,
        "enlace": PORTAL + "/programas/personas-con-discapacidad/pension-para-personas-con-discapacidad/",
    },
    {
        "nombre": "Programa de Madres Trabajadoras",
        "categoria": "mujeres",
        "perfil": "Madres, padres o tutores de niñas y niños menores de 4 años",
        "requisitos": [
            "Ser madre, padre o tutor de una niña o niño menor de 4 años",
            "Presentar en el hogar ausencia temporal o permanente de uno o ambos padres",
        ],
        "apoyo": "Apoyo económico para el cuidado de niñas y niños.",
        "monto": "Consultar monto vigente en el enlace oficial.",
        "convocatoria": False,
        "enlace": PORTAL + "/programas/mujeres/programa-de-madres-trabajadoras/",
    },
    {
        "nombre": "Beca Rita Cetina",
        "categoria": "infancias",
        "perfil": "Familias con niñas o niños en educación básica pública",
        "requisitos": [
            "Tener a una niña o niño en un plantel público de educación básica",
            "No recibir otra beca de algún programa federal",
        ],
        "apoyo": "Beca de educación básica.",
        "monto": "Consultar monto vigente en el enlace oficial.",
        "convocatoria": False,
        "enlace": PORTAL + "/programas/infancias/beca-rita-cetina/",
    },
    {
        "nombre": "Beca Benito Juárez",
        "categoria": "jóvenes",
        "perfil": "Estudiantes de bachillerato público",
        "requisitos": [
            "Estudiar en una escuela pública de bachillerato",
            "No recibir otra beca de algún programa federal",
        ],
        "apoyo": "Beca universal de educación media superior.",
        "monto": "Consultar monto vigente en el enlace oficial.",
        "convocatoria": True,
        "enlace": PORTAL + "/programas/jovenes/beca-benito-juarez/",
    },
    {
        "nombre": "Beca Jóvenes Escribiendo el Futuro",
        "categoria": "jóvenes",
        "perfil": "Estudiantes de educación superior en instituciones prioritarias",
        "requisitos": [
            "Ser estudiante de licenciatura, técnico superior universitario o profesional asociado",
            "Estar inscrito en una institución pública prioritaria o susceptible de atención",
        ],
        "apoyo": "Beca de educación superior.",
        "monto": "Consultar monto vigente en el enlace oficial.",
        "convocatoria": True,
        "enlace": PORTAL + "/programas/jovenes/beca-jovenes-escribiendo-el-futuro/",
    },
    {
        "nombre": "Beca Gertrudis Bocanegra",
        "categoria": "jóvenes",
        "perfil": "Estudiantes de educación superior en estados participantes",
        "requisitos": [
            "Estar inscrita o inscrito en una institución pública de educación superior en Michoacán, Chiapas, Campeche, Sonora o Zacatecas",
            "Tener hasta 29 años cumplidos",
        ],
        "apoyo": "Apoyo para transporte universitario.",
        "monto": "Consultar monto vigente en el enlace oficial.",
        "convocatoria": True,
        "enlace": PORTAL + "/programas/jovenes/beca-gertrudis-bocanegra/",
    },
    {
        "nombre": "Jóvenes Construyendo el Futuro",
        "categoria": "jóvenes",
        "perfil": "Personas de 18 a 29 años que no estudian ni trabajan",
        "requisitos": ["Tener entre 18 y 29 años de edad", "No estar estudiando ni trabajando"],
        "apoyo": "Beca mensual durante capacitación en un centro de trabajo.",
        "monto": "Consultar monto vigente en el enlace oficial.",
        "convocatoria": False,
        "enlace": PORTAL + "/programas/jovenes/jovenes-construyendo-el-futuro/",
    },
    {
        "nombre": "La Escuela Es Nuestra",
        "categoria": "infancias",
        "perfil": "Planteles públicos de educación básica",
        "requisitos": [
            "Cumplir con los criterios de selección del plantel",
            "Constituir un Comité Escolar de Administración Participativa",
        ],
        "apoyo": "Recurso para mejorar la infraestructura del plantel.",
        "monto": "Consultar monto vigente en el enlace oficial.",
        "convocatoria": False,
        "enlace": PORTAL + "/programas/infancias/la-escuela-es-nuestra/",
    },
    {
        "nombre": "Sembrando Vida",
        "categoria": "campo y pesca",
        "perfil": "Personas en municipios rurales con rezago social",
        "requisitos": [
            "Vivir en un municipio o localidad rural con rezago social",
            "Tener disponibles 2.5 hectáreas para un proyecto agroforestal",
        ],
        "apoyo": "Apoyo económico y acompañamiento técnico para proyecto agroforestal.",
        "monto": "Consultar monto vigente en el enlace oficial.",
        "convocatoria": False,
        "enlace": PORTAL + "/programas/campo-y-pesca/sembrando-vida/",
    },
    {
        "nombre": "Producción para el Bienestar",
        "categoria": "campo y pesca",
        "perfil": "Productoras y productores de pequeña o mediana escala",
        "requisitos": [
            "Mantener en producción la superficie registrada con al menos un cultivo elegible o colmenas",
            "Estar registrado o registrarse en el Padrón de Productores de la Secretaría de Agricultura",
        ],
        "apoyo": "Apoyo económico anual directo a productoras y productores.",
        "monto": "De $7,300 a $24,000 anuales (2026, según cultivo y superficie).",
        "convocatoria": False,
        "enlace": PORTAL + "/programas/campo-y-pesca/produccion-para-el-bienestar/",
    },
    {
        "nombre": "Fertilizantes para el Bienestar",
        "categoria": "campo y pesca",
        "perfil": "Productoras y productores de pequeña escala de cultivos prioritarios",
        "requisitos": [
            "Ser productora o productor de pequeña escala de cultivos prioritarios",
            "Estar en el Padrón de Productores de la Secretaría de Agricultura",
        ],
        "apoyo": "Entrega de fertilizantes a pequeña escala.",
        "monto": "Apoyo en especie (fertilizante).",
        "convocatoria": False,
        "enlace": PORTAL + "/programas/campo-y-pesca/fertilizantes-para-el-bienestar/",
    },
    {
        "nombre": "Bienpesca",
        "categoria": "campo y pesca",
        "perfil": "Personas con actividad pesquera o acuícola de pequeña escala",
        "requisitos": [
            "Acreditar actividad pesquera o acuícola de pequeña escala",
            "Estar en el Padrón de Productores de Pesca y Acuacultura",
        ],
        "apoyo": "Apoyo económico para el sector pesquero y acuícola.",
        "monto": "Consultar monto vigente en el enlace oficial.",
        "convocatoria": False,
        "enlace": PORTAL + "/programas/campo-y-pesca/bienpesca/",
    },
    {
        "nombre": "Mejoramiento de Vivienda para el Bienestar",
        "categoria": "vivienda",
        "perfil": "Personas que habitan en municipios prioritarios",
        "requisitos": [
            "Habitar en un municipio prioritario de atención",
            "Tener vivienda propia para las obras de mejora",
        ],
        "apoyo": "Obras de mejora en la vivienda.",
        "monto": "Consultar monto vigente en el enlace oficial.",
        "convocatoria": False,
        "enlace": PORTAL + "/programas/mujeres/mejoramiento-de-vivienda-para-el-bienestar/",
    },
    {
        "nombre": "Salud Casa por Casa",
        "categoria": "adultos mayores",
        "perfil": "Derechohabientes de la pensión de adultos mayores o de discapacidad",
        "requisitos": [
            "Ser derechohabiente de la Pensión de Adultos Mayores o de la Pensión para Personas con Discapacidad",
        ],
        "apoyo": "Visitas de personal de salud a domicilio.",
        "monto": "Servicio de salud (sin pago).",
        "convocatoria": False,
        "enlace": PORTAL + "/programas/adultos-mayores/salud-casa-por-casa/",
    },
]

NOTE = (
    "Los montos y requisitos pueden cambiar con las reglas de operación vigentes. "
    "El registro es gratuito y se realiza por canales oficiales; no hay intermediarios."
)


def strip_accents(text):
    return "".join(c for c in unicodedata.normalize("NFKD", text) if not unicodedata.combining(c))


def search_programs(query, categoria=None, catalog=None):
    catalog = catalog if catalog is not None else CATALOG
    needle = strip_accents(query.lower())
    category = strip_accents(categoria.lower()) if categoria else None
    results = []
    for program in catalog:
        if category and strip_accents(program["categoria"].lower()) != category:
            continue
        haystack = strip_accents(
            " ".join([program["nombre"], program["categoria"], program["perfil"]] + program["requisitos"]).lower()
        )
        if needle in haystack:
            results.append(program)
    return results


def build_payload(results, query=None, list_all=False):
    return {
        "source": "Portal oficial Programas para el Bienestar",
        "portal": PORTAL,
        "modo": "lista" if list_all else "busqueda",
        "query": query,
        "note": NOTE,
        "results": results,
    }


def format_text(payload):
    results = payload.get("results") or []
    if not results:
        return f"No se encontraron programas para '{payload.get('query')}'. Consulta {PORTAL}"
    lines = []
    for program in results:
        requisitos = "\n".join(f"   - {r}" for r in program["requisitos"])
        lines.append(
            f"• {program['nombre']} [{program['categoria']}]\n"
            f"   Perfil: {program['perfil']}\n"
            f"   Apoyo: {program['apoyo']}\n"
            f"   Monto: {program['monto']}\n"
            f"   Requisitos:\n{requisitos}\n"
            f"   Enlace: {program['enlace']}"
        )
    lines.append("")
    lines.append(payload.get("note", ""))
    return "\n".join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Programas para el Bienestar de México")
    parser.add_argument("query", nargs="?", help="Palabra clave (pensión, beca, jóvenes, campo...)")
    parser.add_argument("--query", dest="query_opt", help="Palabra clave (alternativa posicional)")
    parser.add_argument("--categoria", default=None, help="Filtrar por categoría")
    parser.add_argument("--list", action="store_true", help="Listar todos los programas")
    parser.add_argument("--json", action="store_true", help="Salida JSON cruda")
    args = parser.parse_args(argv)

    if args.list:
        results = search_programs("", categoria=args.categoria)
        payload = build_payload(results, list_all=True)
    else:
        query = (args.query_opt or args.query or "").strip()
        if not query and not args.categoria:
            parser.error("Proporciona una palabra clave o usa --list.")
        results = search_programs(query, categoria=args.categoria)
        payload = build_payload(results, query=query or None)

    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(format_text(payload))


if __name__ == "__main__":
    main()
