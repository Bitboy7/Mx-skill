import contextlib
import importlib.util
import io
import json
import pathlib
import unittest
from unittest import mock

ROOT = pathlib.Path(__file__).resolve().parents[2]
MODULE_PATH = ROOT / "mx-real-estate" / "scripts" / "mx_real_estate.py"
SPEC = importlib.util.spec_from_file_location("mx_real_estate", MODULE_PATH)
mx_real_estate = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(mx_real_estate)

POSTING = {
    "postingId": "1",
    "title": "Departamento en Polanco",
    "realEstateType": {"name": "Departamentos"},
    "priceOperationTypes": [
        {
            "operationType": {"name": "Venta"},
            "prices": [{"currency": "MN", "amount": 9000000, "formattedAmount": "9,000,000"}],
        }
    ],
    "mainFeatures": {
        "CFT2": {"featureId": "CFT2", "label": "Recámaras", "value": "3", "measure": None},
        "CFT3": {"featureId": "CFT3", "label": "Baños", "value": "2", "measure": None},
        "CFT101": {"featureId": "CFT101", "label": "Superficie construida", "value": "264", "measure": "m²"},
    },
    "generalFeatures": {},
    "postingLocation": {
        "location": {
            "name": "Polanco",
            "parent": {"name": "Miguel Hidalgo", "parent": {"name": "Ciudad de México"}},
        }
    },
    "house": {"address": {"name": "Calle X, Polanco"}},
    "publisher": {"name": "Inmobiliaria X"},
    "expenses": {"amount": 8245, "formattedAmount": "8,245", "currency": "MN"},
    "url": "/propiedades/clasificado/abc-1.html",
}


def html_with_state(state):
    return "<html><script>window.__PRELOADED_STATE__ = " + json.dumps(state, ensure_ascii=False) + ";</script></html>"


class ParseQueryTests(unittest.TestCase):
    def test_detects_type_operation_and_zone(self):
        self.assertEqual(mx_real_estate.parse_query("departamento polanco", "venta"), ("departamentos", "venta", "polanco"))

    def test_query_operation_overrides_flag(self):
        tipo, operacion, zona = mx_real_estate.parse_query("renta departamento roma", "venta")
        self.assertEqual((tipo, operacion, zona), ("departamentos", "renta", "roma"))

    def test_applies_zone_alias(self):
        self.assertEqual(mx_real_estate.parse_query("casa acapulco", "venta"), ("casas", "venta", "acapulco-de-juarez"))

    def test_defaults_to_generic_type(self):
        self.assertEqual(mx_real_estate.parse_query("polanco", "renta"), ("inmuebles", "renta", "polanco"))

    def test_build_url_with_and_without_zone(self):
        self.assertEqual(
            mx_real_estate.build_url("departamentos", "venta", "polanco"),
            "https://www.inmuebles24.com/departamentos-en-venta-en-polanco.html",
        )
        self.assertEqual(
            mx_real_estate.build_url("inmuebles", "renta", ""),
            "https://www.inmuebles24.com/inmuebles-en-renta.html",
        )


class ExtractStateTests(unittest.TestCase):
    def test_extracts_embedded_state(self):
        state = {"listStore": {"listPostings": [POSTING]}}
        parsed = mx_real_estate.extract_preloaded_state(html_with_state(state))
        self.assertIsNotNone(parsed)
        self.assertEqual(len(parsed["listStore"]["listPostings"]), 1)

    def test_returns_none_without_state(self):
        self.assertIsNone(mx_real_estate.extract_preloaded_state("<html></html>"))


class SummarizeTests(unittest.TestCase):
    def test_maps_fields(self):
        item = mx_real_estate.summarize(POSTING)
        self.assertEqual(item["titulo"], "Departamento en Polanco")
        self.assertEqual(item["tipo"], "Departamentos")
        self.assertEqual(item["operacion"], "Venta")
        self.assertEqual(item["precio"], "$9,000,000 MXN")
        self.assertEqual(item["moneda"], "MXN")
        self.assertEqual(item["dormitorios"], "3")
        self.assertEqual(item["banos"], "2")
        self.assertEqual(item["superficie_m2"], "264 m²")
        self.assertEqual(item["ubicacion"], "Polanco, Miguel Hidalgo, Ciudad de México")
        self.assertEqual(item["mantenimiento"], "$8,245 MN")
        self.assertEqual(item["link"], "https://www.inmuebles24.com/propiedades/clasificado/abc-1.html")

    def test_missing_features_are_none(self):
        item = mx_real_estate.summarize({"title": "X", "url": "/x"})
        self.assertIsNone(item["precio"])
        self.assertIsNone(item["dormitorios"])


class BuscarTests(unittest.TestCase):
    def test_falls_back_to_generic_when_type_empty(self):
        def fake_fetch(url):
            if "departamentos-en-venta" in url:
                return [], url
            return [POSTING], url

        with mock.patch.object(mx_real_estate, "fetch_listings", side_effect=fake_fetch):
            payload = mx_real_estate.buscar("departamento polanco", "venta", 5)

        self.assertEqual(len(payload["results"]), 1)
        self.assertIn("inmuebles", payload["url_busqueda"])
        self.assertIn("nota", payload)

    def test_returns_none_without_results(self):
        with mock.patch.object(mx_real_estate, "fetch_listings", return_value=([], "u")):
            self.assertIsNone(mx_real_estate.buscar("departamento polanco", "venta", 5))

    def test_notes_unrecognized_zone_redirect(self):
        requested = mx_real_estate.build_url(*mx_real_estate.parse_query("departamento polanco", "venta"))
        with mock.patch.object(mx_real_estate, "fetch_listings", return_value=([POSTING], "https://www.inmuebles24.com/inmuebles-en-venta.html")):
            payload = mx_real_estate.buscar("departamento polanco", "venta", 5)
        self.assertIn("no se reconocio", payload["nota"])
        self.assertEqual(payload["url_busqueda"], requested)


class MainTests(unittest.TestCase):
    def test_main_prints_json(self):
        requested = mx_real_estate.build_url(*mx_real_estate.parse_query("departamento polanco", "venta"))
        stdout = io.StringIO()
        with (
            contextlib.redirect_stdout(stdout),
            mock.patch.object(mx_real_estate, "fetch_listings", return_value=([POSTING], requested)),
        ):
            mx_real_estate.main(["--q", "departamento polanco", "--tipo", "venta", "--limit", "5"])

        rendered = json.loads(stdout.getvalue())
        self.assertEqual(rendered["results"][0]["titulo"], "Departamento en Polanco")
        self.assertEqual(rendered["tipo"], "venta")

    def test_main_exits_when_no_results(self):
        with mock.patch.object(mx_real_estate, "fetch_listings", return_value=([], "u")):
            with self.assertRaises(SystemExit):
                mx_real_estate.main(["--q", "departamento polanco"])


if __name__ == "__main__":
    unittest.main()
