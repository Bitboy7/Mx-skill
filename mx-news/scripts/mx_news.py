#!/usr/bin/env python3
"""Noticias de Mexico via Google News RSS (feed publico).

Uso:
  python3 mx_news.py top
  python3 mx_news.py search --q "economia mexico"
"""

import argparse
import html
import json
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

RSS_BASE = "https://news.google.com/rss"
USER_AGENT = "k-skill-mx-news/1.0 (+https://github.com/NomaDamas/k-skill)"
NS = {"atom": "http://www.w3.org/2005/Atom"}


def fetch_rss(url):
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read()


def parse_items(raw):
    root = ET.fromstring(raw)
    items = []
    for item in root.iter("item"):
        title = html.unescape((item.findtext("title") or "").strip())
        link = (item.findtext("link") or "").strip()
        source = item.find("source")
        source_name = html.unescape((source.text or "").strip()) if source is not None else ""
        pub_date = (item.findtext("pubDate") or "").strip()
        items.append(
            {
                "titulo": title,
                "fuente": source_name,
                "fecha": pub_date,
                "link": link,
            }
        )
    return items


def main():
    parser = argparse.ArgumentParser(description="Noticias de Mexico via Google News RSS")
    sub = parser.add_subparsers(dest="command")

    p_top = sub.add_parser("top", help="Noticias principales de Mexico")
    p_top.add_argument("--limit", type=int, default=15)

    p_search = sub.add_parser("search", help="Buscar noticias por palabra clave")
    p_search.add_argument("--q", required=True, help="Palabra clave en espanol")
    p_search.add_argument("--limit", type=int, default=15)

    args = parser.parse_args()
    command = args.command or "top"

    if command == "top":
        url = f"{RSS_BASE}?hl=es-MX&gl=MX&ceid=MX:es-419"
    elif command == "search":
        url = f"{RSS_BASE}/search?q={urllib.parse.quote(args.q)}&hl=es-MX&gl=MX&ceid=MX:es-419"
    else:
        parser.error(f"comando desconocido: {command}")

    items = parse_items(fetch_rss(url))
    if not items:
        raise SystemExit("No se encontraron noticias para esta consulta.")

    print(json.dumps(
        {
            "source": "Google News RSS (es-MX)",
            "query": args.q if command == "search" else "portada",
            "results": items[: args.limit],
        },
        ensure_ascii=False,
        indent=2,
    ))


if __name__ == "__main__":
    main()
