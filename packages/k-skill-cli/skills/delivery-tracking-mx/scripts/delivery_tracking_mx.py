#!/usr/bin/env python3
"""Seguimiento de envios en Mexico.

Mensajeria primaria verificada: Estafeta (endpoint publico GET).
Correos de Mexico y 99 Minutos estan detras de challenges anti-bot JS y no son
accesibles por HTTP directo; se documentan como modos de fallo.

Uso:
  python3 delivery_tracking_mx.py --carrier estafeta --guia 0000000000000000000000
"""

import argparse
import html
import json
import re
import urllib.request

ESTAFETA_URL = (
    "https://cs.estafeta.com/es/Tracking/searchByGet"
    "?wayBill={guia}&wayBillType=0&isShipmentDetail=False"
)
USER_AGENT = "k-skill-delivery-tracking-mx/1.0 (+https://github.com/NomaDamas/k-skill)"
ESTAFETA_GUIA_RE = r"^\d{22}$"


def clean(raw):
    return " ".join(html.unescape(re.sub(r"<[^>]+>", " ", raw)).split())


def track_estafeta(guia):
    url = ESTAFETA_URL.format(guia=guia)
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=30) as resp:
        page = resp.read().decode("utf-8", "ignore")

    # The FAQ/no-information page is shown for invalid or not-found waybills.
    if "Qu" in page and "n\u00famero de gu\u00eda" in html.unescape(page).replace("\u00e9", "é"):
        if "Verifique que tenga el n" in page or "no hay informaci" in page:
            raise SystemExit("No se encontro informacion para esa guia de Estafeta.")

    events = []
    for row in re.findall(r'class="historyEventRow"(.*?)</div>\s*</div>', page, re.S):
        date = re.search(r'class="historyEventDate[^"]*">(.*?)<', row, re.S)
        detail = re.search(r'class="historyEventDetail[^"]*">(.*?)<', row, re.S)
        if date or detail:
            events.append(
                {
                    "fecha": clean(date.group(1)) if date else None,
                    "detalle": clean(detail.group(1)) if detail else None,
                }
            )

    header = re.search(r'class="shipmentHeader"(.*?)</div>', page, re.S)
    status = None
    if header:
        sm = re.search(r"Estado[:\s]*<[^>]*>([^<]+)", header.group(1), re.I)
        if sm:
            status = clean(sm.group(1))

    return {
        "carrier": "estafeta",
        "guia": guia,
        "status": status,
        "event_count": len(events),
        "recent_events": events[-min(3, len(events)):] if events else [],
        "note": "Correos de Mexico y 99 Minutos no exponen endpoint publico (anti-bot JS); usa sus portales.",
    }


def main():
    parser = argparse.ArgumentParser(description="Seguimiento de envios en Mexico")
    parser.add_argument("--carrier", choices=["estafeta"], default="estafeta")
    parser.add_argument("--guia", required=True, help="Numero de guia")
    args = parser.parse_args()

    guia = args.guia.strip()
    if not re.fullmatch(ESTAFETA_GUIA_RE, guia):
        raise SystemExit("Las guias de Estafeta tienen 22 digitos.")

    print(json.dumps(track_estafeta(guia), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
