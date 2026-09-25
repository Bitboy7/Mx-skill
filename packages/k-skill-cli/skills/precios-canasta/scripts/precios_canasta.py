#!/usr/bin/env python3
"""Precios de la canasta basica en Mexico (PROFECO / Quien es Quien en los Precios).

Fuente oficial: reporte semanal "Productos de Primera Necesidad" del programa
Quien es Quien en los Precios (PROFECO), publicado como PDF en
https://qqph.profeco.gob.mx. La antigua API publica
`api.datos.gob.mx/v1/precio.canasta.basica` fue retirada junto con el resto de
la plataforma datos.gob.mx v1; el portal vigente solo publica el PDF semanal.

El reporte lista, por zona geografica, los 5 establecimientos con el precio de
canasta (24 productos) mas alto y los 5 mas bajo. Este helper descarga el PDF
mas reciente, extrae esas filas con la biblioteca estandar (zlib + expresiones
regulares sobre los content streams) y las expone como JSON.

Uso:
  python3 precios_canasta.py --top 10
  python3 precios_canasta.py --estado "Jalisco"
"""

import argparse
import datetime
import json
import re
import sys
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
import zlib

QQP_BASE = "https://qqph.profeco.gob.mx"
ANIOS_URL = QQP_BASE + "/api/anios"
ARCHIVOS_URL = QQP_BASE + "/api/archivos/{anio}"
PROFECO_PORTAL = "https://www.profeco.gob.mx/precios/canasta/home.aspx"
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
)

STREAM_RE = re.compile(rb"stream\r?\n(.*?)\r?\nendstream", re.S)
BT_RE = re.compile(rb"BT(.*?)ET", re.S)
TM_RE = re.compile(rb"1 0 0 1 ([\-\d.]+) ([\-\d.]+) Tm")
STR_RE = re.compile(rb"\((?:\\\\.|[^\\()])*\)")
OCTAL_RE = re.compile(rb"\\([0-7]{1,3})")
PRICE_RE = re.compile(r"^\$?\s*([\d,]+\.\d{2})$")
ARCHIVO_NAME_RE = re.compile(r"_(\d{2})(\d{2})(\d{2})\.pdf$", re.I)
MONTHS = {
    "enero": 1,
    "febrero": 2,
    "marzo": 3,
    "abril": 4,
    "mayo": 5,
    "junio": 6,
    "julio": 7,
    "agosto": 8,
    "septiembre": 9,
    "setiembre": 9,
    "octubre": 10,
    "noviembre": 11,
    "diciembre": 12,
}
SMALL_WORDS = {"de", "del", "la", "las", "los", "y"}


def http_get(url, timeout=40):
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "*/*"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.read()
    except urllib.error.HTTPError as exc:
        raise SystemExit(
            f"PROFECO respondio HTTP {exc.code} al consultar {url}. "
            f"Reintenta mas tarde o revisa el portal: {PROFECO_PORTAL}"
        ) from exc
    except urllib.error.URLError as exc:
        raise SystemExit(
            f"No se pudo contactar a PROFECO ({url}): {exc.reason}. "
            f"Revisa tu conexion o consulta el portal: {PROFECO_PORTAL}"
        ) from exc


def http_get_json(url, timeout=30):
    return json.loads(http_get(url, timeout=timeout).decode("utf-8", "replace"))


def normalize(value):
    """Minusculas sin acentos ni signos, para comparar estados."""
    text = unicodedata.normalize("NFKD", str(value or ""))
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    return re.sub(r"[^a-z0-9 ]+", " ", text.lower()).strip()


def nice_name(value):
    words = str(value or "").title().split()
    return " ".join(w.lower() if w.lower() in SMALL_WORDS else w for w in words)


def archivo_date(archivo):
    match = ARCHIVO_NAME_RE.search(archivo.get("nombre") or "")
    if match:
        mm, dd, yy = (int(part) for part in match.groups())
        return (2000 + yy, mm, dd)
    tokens = normalize(archivo.get("descripcion")).split()
    numbers = [int(token) for token in tokens if token.isdigit()]
    month = next((MONTHS[token] for token in tokens if token in MONTHS), 0)
    if numbers and month:
        return (numbers[-1], month, numbers[0])
    return (0, 0, 0)


def find_primeran_category(archivos):
    for categoria in archivos or []:
        if normalize(categoria.get("nombre")) == "primeran":
            return categoria
    for categoria in archivos or []:
        if "primera necesidad" in normalize(categoria.get("descripcion")):
            return categoria
    return None


def latest_report():
    """Devuelve (url_pdf, descripcion, anio) del reporte mas reciente."""
    try:
        anios = [int(a.get("anio")) for a in http_get_json(ANIOS_URL) if str(a.get("anio", "")).isdigit()]
    except (SystemExit, ValueError, TypeError, json.JSONDecodeError):
        anios = []
    anios.sort(reverse=True)
    if not anios:
        current = datetime.date.today().year
        anios = [current, current - 1, current - 2]
    for anio in anios:
        try:
            categorias = http_get_json(ARCHIVOS_URL.format(anio=anio))
        except SystemExit:
            raise
        except (ValueError, json.JSONDecodeError):
            continue
        categoria = find_primeran_category(categorias)
        if not categoria:
            continue
        archivos = [a for a in (categoria.get("archivos") or []) if a.get("ruta")]
        if not archivos:
            continue
        archivo = max(archivos, key=archivo_date)
        ruta = archivo["ruta"]
        url = ruta if ruta.startswith("http") else QQP_BASE + ruta
        return url, archivo.get("descripcion"), anio
    raise SystemExit(
        "No se encontro el reporte de canasta basica (Productos de Primera Necesidad) "
        f"en PROFECO. Consulta el portal: {PROFECO_PORTAL}"
    )


def decode_pdf_string(raw):
    raw = OCTAL_RE.sub(lambda m: bytes([int(m.group(1), 8) & 0xFF]), raw)
    out = bytearray()
    i = 0
    while i < len(raw):
        char = raw[i]
        if char == 0x5C and i + 1 < len(raw):
            nxt = raw[i + 1]
            if nxt in (0x6E, 0x72, 0x74, 0x62, 0x66):  # n r t b f
                out.append({0x6E: 10, 0x72: 13, 0x74: 9, 0x62: 8, 0x66: 12}[nxt])
                i += 2
                continue
            out.append(nxt)
            i += 2
            continue
        out.append(char)
        i += 1
    data = bytes(out)
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError:
        return data.decode("latin-1")


def parse_cells(stream):
    cells = []
    for block in BT_RE.finditer(stream):
        body = block.group(1)
        tm = TM_RE.search(body)
        if not tm:
            continue
        x = float(tm.group(1))
        y = float(tm.group(2))
        text = "".join(decode_pdf_string(m.group(0)[1:-1]) for m in STR_RE.finditer(body)).strip()
        if text:
            cells.append((y, x, text))
    return cells


def group_rows(cells, tol=3.0):
    rows = []
    for y, x, text in sorted(cells, key=lambda c: (-c[0], c[1])):
        if rows and abs(rows[-1][0] - y) < tol:
            rows[-1][1].append((x, text))
        else:
            rows.append((y, [(x, text)]))
    return rows


def find_column(cells, label):
    for _, x, text in cells:
        if text.strip().upper().strip("*").strip() == label:
            return x
    return None


def zone_of(cells):
    joined = " ".join(text for _, _, text in cells).upper()
    for name in ("ZONA CENTRO NORTE", "ZONA NORTE", "ZONA SUR", "ZONA CENTRO"):
        if name in joined:
            return name
    return None


def report_date(cells):
    for _, cols in group_rows(cells):
        for i, (_, text) in enumerate(cols):
            if text.strip().lower() == "precios vigentes" and i + 1 < len(cols):
                return cols[i + 1][1].strip().removeprefix("del ").strip()
    return None


def extract_records(pdf_bytes):
    records = []
    report_dates = []
    for stream in STREAM_RE.findall(pdf_bytes):
        try:
            data = zlib.decompress(stream)
        except zlib.error:
            continue
        cells = parse_cells(data)
        if not cells or not any("$" in text for _, _, text in cells):
            continue
        zone = zone_of(cells)
        if not zone:
            continue
        x_est = find_column(cells, "ESTABLECIMIENTO")
        x_ent = find_column(cells, "ENTIDAD")
        x_mun = find_column(cells, "MUNICIPIO")
        x_dom = find_column(cells, "DOMICILIO")
        x_pre = find_column(cells, "PRECIO")
        if None in (x_est, x_ent, x_mun, x_dom, x_pre):
            continue
        bounds = {
            "est": (0, x_ent - 40),
            "ent": (x_ent - 40, x_ent + 40),
            "mun": (x_ent + 40, x_mun + 60),
            "dom": (x_mun + 60, x_dom + 60),
            "pre": (x_pre - 40, x_pre + 70),
        }

        def column(lo, hi, y0, tol=8.0):
            return [text for y, x, text in cells if lo <= x < hi and abs(y - y0) <= tol]

        date = report_date(cells)
        if date and date not in report_dates:
            report_dates.append(date)

        for y, x, text in cells:
            match = PRICE_RE.match(text.strip())
            if not match or not (bounds["pre"][0] <= x <= bounds["pre"][1]):
                continue
            store = "".join(column(*bounds["est"], y)).strip().strip("*").strip()
            entidad = " ".join(column(*bounds["ent"], y)).strip()
            municipio = " ".join(column(*bounds["mun"], y)).strip()
            if not store or not entidad:
                continue
            records.append(
                {
                    "tienda": nice_name(store),
                    "estado": nice_name(entidad),
                    "municipio": nice_name(municipio) or None,
                    "region": nice_name(zone),
                    "costo_mxn": round(float(match.group(1).replace(",", "")), 2),
                }
            )

    unique = []
    seen = set()
    for record in records:
        key = (record["tienda"], record["estado"], record["costo_mxn"])
        if key in seen:
            continue
        seen.add(key)
        unique.append(record)
    return unique, (report_dates[0] if report_dates else None)


def main(argv=None):
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except (ValueError, OSError):
            pass

    parser = argparse.ArgumentParser(description="Precios de la canasta basica en Mexico (PROFECO)")
    parser.add_argument("--top", type=int, default=10, help="Mostrar las N canastas mas baratas")
    parser.add_argument("--estado", help="Filtrar por estado (ej. Jalisco, CDMX)")
    args = parser.parse_args(argv)

    pdf_url, publicado, anio = latest_report()
    pdf_bytes = http_get(pdf_url, timeout=40)
    records, fecha = extract_records(pdf_bytes)
    if not records:
        raise SystemExit(
            "No se pudieron extraer precios del reporte de PROFECO. "
            f"Revisa el PDF oficial ({anio}): {pdf_url}"
        )

    if args.estado:
        query = normalize(args.estado)
        aliases = {"cdmx": "ciudad de mexico", "edomex": "estado de mexico", "nl": "nuevo leon"}
        query = aliases.get(query, query)
        records = [
            record
            for record in records
            if query in normalize(record["estado"]) or normalize(record["estado"]) in query
        ]

    records.sort(key=lambda record: record["costo_mxn"])

    print(
        json.dumps(
            {
                "source": "PROFECO - Quien es Quien en los Precios (Productos de Primera Necesidad, canasta 24 productos)",
                "pdf": pdf_url,
                "publicado": publicado,
                "reporte": fecha,
                "portal": PROFECO_PORTAL,
                "filter": args.estado,
                "total": len(records),
                "results": records[: max(args.top, 0)],
                "nota": (
                    "El reporte oficial lista los 5 precios mas altos y los 5 mas bajos por zona; "
                    "el costo corresponde a la canasta de 24 productos de primera necesidad."
                ),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
