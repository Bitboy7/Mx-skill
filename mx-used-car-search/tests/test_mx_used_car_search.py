"""Pruebas offline del helper mx-used-car-search (sin red real).

Se ejecuta con cualquier Python 3.10+:
  python -m unittest discover -s mx-used-car-search/tests -p "test_*.py"
"""

import contextlib
import importlib.util
import io
import json
import pathlib
import unittest
from unittest import mock

ROOT = pathlib.Path(__file__).resolve().parents[2]
MODULE_PATH = ROOT / "mx-used-car-search" / "scripts" / "mx_used_car_search.py"
SPEC = importlib.util.spec_from_file_location("mx_used_car_search", MODULE_PATH)
mx = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(mx)


def _card(href, titulo, ubicacion, anio, marca, modelo, version, km, trans, precio):
    return (
        '<div class="group block"><div class="relative mb-4">'
        f'<a class="block" aria-label="Ver {titulo}" href="{href}">'
        '<div class="relative aspect-[4/3]"></div>'
        '<span class="truncate">' + ubicacion + "</span>"
        f'<p class="text-sm font-bold text-foreground leading-tight">{anio}</p>'
        f"<h3>{marca}<!-- --> \u00b7 <!-- -->{modelo}</h3>"
        f'<p class="text-xs text-muted-foreground line-clamp-1 leading-tight" title="{version}">{version}</p>'
        "<p><span>" + f"{km:,}" + ' kms.</span>'
        '<span class="text-muted-foreground/80">\u00b7</span>'
        f"<span>{trans}</span></p>"
        f'<div class="pt-1.5"><span class="text-lg font-semibold text-foreground">${precio:,}</span></div>'
        "</a></div></div>"
    )


PAGE_HTML = "".join(
    [
        _card("/vehicle/autos-nissan-sentra-monterrey-2023/111", "Nissan Sentra 2023", "Monterrey",
              2023, "Nissan", "Sentra", "1.8 Advance At", 21000, "Autom\u00e1tica", 299000),
        _card("/vehicle/autos-nissan-sentra-cdmx-2014/222", "Nissan Sentra 2014", "Miguel Hidalgo",
              2014, "Nissan", "Sentra", "2.0 Mt", 180000, "Manual", 120000),
        _card("/vehicle/autos-nissan-sentra-monterrey-2023/111", "Nissan Sentra 2023", "Monterrey",
              2023, "Nissan", "Sentra", "1.8 Advance At", 21000, "Autom\u00e1tica", 299000),
    ]
)


class UsedCarHelperTests(unittest.TestCase):
    def test_slugify_and_estado(self):
        self.assertEqual(mx.slugify("Nuevo León"), "nuevo+leon")
        self.assertEqual(mx.normalize_estado("CDMX"), "ciudad+de+mexico")
        self.assertEqual(mx.normalize_estado("Jalisco"), "jalisco")

    def test_build_search_url_dealer_and_page(self):
        url = mx.build_search_url("nissan", "sentra", "nuevo leon", "dealer", 2)
        self.assertEqual(
            url,
            "https://www.seminuevos.com/usados/nuevo+leon/autos/-/nissan/sentra?seller=DEALER&page=2",
        )

    def test_build_search_url_todos_sin_estado(self):
        url = mx.build_search_url("toyota", "corolla", None, "todos", 1)
        self.assertEqual(url, "https://www.seminuevos.com/usados/-/autos/-/toyota/corolla")

    def test_parse_listings_fields_and_dedupe(self):
        listings = mx.parse_listings(PAGE_HTML)
        self.assertEqual(len(listings), 2)  # se deduplica el anuncio repetido
        first = listings[0]
        self.assertEqual(first["titulo"], "Nissan Sentra 2023")
        self.assertEqual(first["anio"], 2023)
        self.assertEqual(first["km"], 21000)
        self.assertEqual(first["precio_mxn"], 299000)
        self.assertEqual(first["ubicacion"], "Monterrey")
        self.assertEqual(first["version"], "1.8 Advance At")
        self.assertEqual(first["transmision"], "Autom\u00e1tica")
        self.assertTrue(first["url"].endswith("/vehicle/autos-nissan-sentra-monterrey-2023/111"))

    def test_median(self):
        self.assertEqual(mx.median([100, 200, 300]), 200.0)
        self.assertEqual(mx.median([100, 200]), 150.0)
        self.assertIsNone(mx.median([None, None]))

    def test_score_recent_low_km_is_high(self):
        listing = {"anio": 2024, "km": 20000, "precio_mxn": 300000}
        score, nivel, notas = mx.score_listing(listing, 310000, 2026, dealer=True)
        self.assertGreaterEqual(score, 75)
        self.assertEqual(nivel, "Alta")
        self.assertEqual(notas, [])

    def test_score_old_high_km_has_notes(self):
        listing = {"anio": 2005, "km": 250000, "precio_mxn": 90000}
        score, nivel, notas = mx.score_listing(listing, 200000, 2026, dealer=False)
        self.assertLess(score, 55)
        self.assertEqual(nivel, "Baja")
        self.assertTrue(any("15 a" in n for n in notas))

    def test_score_very_cheap_flags_price(self):
        listing = {"anio": 2019, "km": 80000, "precio_mxn": 50000}
        _, _, notas = mx.score_listing(listing, 200000, 2026, dealer=True)
        self.assertTrue(any("por debajo del mercado" in n for n in notas))

    def test_build_payload_sorted_and_median(self):
        listings = mx.parse_listings(PAGE_HTML)
        payload = mx.build_payload(listings, url="http://x", query={"marca": "nissan"}, page=1, limit=10, dealer=True)
        self.assertEqual(payload["total_analizados"], 2)
        self.assertEqual(payload["precio_mediana_mxn"], 209500)
        self.assertIn("repuve", payload["official_links"])
        scores = [r["confianza"] for r in payload["results"]]
        self.assertEqual(scores, sorted(scores, reverse=True))

    def test_main_requires_marca(self):
        with self.assertRaises(SystemExit):
            mx.main([])

    def test_main_prints_json_with_mocked_get(self):
        stdout = io.StringIO()
        with (
            contextlib.redirect_stdout(stdout),
            mock.patch.object(mx, "http_get", return_value=PAGE_HTML),
        ):
            mx.main(["--marca", "nissan", "--modelo", "sentra", "--json"])
        rendered = json.loads(stdout.getvalue())
        self.assertEqual(rendered["query"]["marca"], "nissan")
        self.assertEqual(len(rendered["results"]), 2)

    def test_main_query_text_splits_brand_and_model(self):
        stdout = io.StringIO()
        with (
            contextlib.redirect_stdout(stdout),
            mock.patch.object(mx, "http_get", return_value=PAGE_HTML),
        ):
            mx.main(["--query", "toyota corolla", "--json"])
        rendered = json.loads(stdout.getvalue())
        self.assertEqual(rendered["query"]["marca"], "toyota")
        self.assertEqual(rendered["query"]["modelo"], "corolla")


if __name__ == "__main__":
    unittest.main()
