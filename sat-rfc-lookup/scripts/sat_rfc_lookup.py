#!/usr/bin/env python3
"""Analiza y valida la estructura del RFC (SAT, Mexico).

Validacion local y determinista (sin red):
- Estructura de persona fisica / moral (incluye la fecha real AAMMDD).
- Desglose de los componentes del RFC (ayuda a detectar errores de captura).

La homoclave (ultimos 3 caracteres) la asigna el SAT con un algoritmo
confidencial (Regla 8) y NO puede verificarse offline. La unica verificacion
oficial es via los servicios del SAT (constancia / e.firma).

Uso:
  python3 sat_rfc_lookup.py --rfc GODE561231GR8
"""

import argparse
import datetime
import json
import re
import sys

PHYSICAL_RE = re.compile(r"^([A-Z]{4})(\d{6})([A-Z0-9]{3})$")
MORAL_RE = re.compile(r"^([A-Z]{3})(\d{6})([A-Z0-9]{3})$")


def parse_date(yymmdd):
    try:
        year = int(yymmdd[:2])
        month = int(yymmdd[2:4])
        day = int(yymmdd[4:6])
        # AAMMDD: 00-49 → 2000-2049; 50-99 → 1950-1999
        year += 2000 if year < 50 else 1900
        datetime.date(year, month, day)
        return True
    except (ValueError, IndexError):
        return False


def validate(rfc):
    rfc = rfc.upper()
    if not re.fullmatch(r"[A-Z0-9]{12,13}", rfc):
        return {
            "rfc": rfc,
            "valido": False,
            "tipo": None,
            "detalle": "El RFC solo puede contener letras mayusculas y digitos (12 o 13 caracteres).",
        }

    m = PHYSICAL_RE.match(rfc)
    if m:
        tipo = "persona fisica"
        iniciales, fecha, homoclave = m.groups()
        detalle = "Iniciales (apellidos + nombre) + fecha de nacimiento + homoclave."
    else:
        m = MORAL_RE.match(rfc)
        if m:
            tipo = "persona moral"
            iniciales, fecha, homoclave = m.groups()
            detalle = "Tres letras (razon social) + fecha de creacion + homoclave."
        else:
            return {
                "rfc": rfc,
                "valido": False,
                "tipo": None,
                "detalle": "La estructura no corresponde a persona fisica (AAAA######XXX) ni persona moral (AAA######XXX).",
            }

    fecha_valida = parse_date(fecha)
    return {
        "rfc": rfc,
        "valido": fecha_valida,
        "tipo": tipo,
        "iniciales": iniciales,
        "fecha_aammdd": fecha,
        "fecha_valida": fecha_valida,
        "homoclave": homoclave,
        "detalle": detalle if fecha_valida else "La fecha AAMMDD no corresponde a un dia valido.",
        "nota": "La homoclave la asigna el SAT (algoritmo confidencial); no se puede verificar offline. "
                "La verificacion oficial requiere el portal SAT (e.firma).",
    }


def main():
    parser = argparse.ArgumentParser(description="Analiza y valida la estructura del RFC")
    parser.add_argument("--rfc", required=True, help="RFC a validar")
    args = parser.parse_args()

    result = validate(args.rfc)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if not result.get("valido"):
        sys.exit(2)


if __name__ == "__main__":
    main()
