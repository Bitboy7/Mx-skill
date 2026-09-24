import contextlib
import importlib.util
import io
import json
import pathlib
import unittest
import urllib.parse
from unittest import mock


ROOT = pathlib.Path(__file__).resolve().parents[2]
MODULE_PATH = ROOT / "mx-air-quality" / "scripts" / "mx_air_quality.py"
SPEC = importlib.util.spec_from_file_location("mx_air_quality", MODULE_PATH)
mx_air_quality = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(mx_air_quality)


SAMPLE = {
    "latitude": 19.4,
    "longitude": -99.1,
    "timezone": "America/Mexico_City",
    "current": {
        "time": "2026-09-23T12:00",
        "pm10": 10.4,
        "pm2_5": 10.2,
        "us_aqi": 64,
        "carbon_monoxide": 469.0,
        "nitrogen_dioxide": 21.0,
        "ozone": 55.0,
        "sulphur_dioxide": 3.0,
    },
}

ANCHOR = {
    "query": "Ciudad de Mexico",
    "name": "Ciudad de Mexico",
    "admin1": "Ciudad de Mexico",
    "latitude": 19.43,
    "longitude": -99.13,
}


class AirQualityHelperTests(unittest.TestCase):
    def test_classify_us_aqi_boundaries(self):
        self.assertEqual(mx_air_quality.classify_us_aqi(0)[0], "Buena")
        self.assertEqual(mx_air_quality.classify_us_aqi(50)[0], "Buena")
        self.assertEqual(mx_air_quality.classify_us_aqi(51)[0], "Moderada")
        self.assertEqual(mx_air_quality.classify_us_aqi(150)[0], "Danina para grupos sensibles")
        self.assertEqual(mx_air_quality.classify_us_aqi(175)[0], "Danina")
        self.assertEqual(mx_air_quality.classify_us_aqi(250)[0], "Muy danina")
        self.assertEqual(mx_air_quality.classify_us_aqi(400)[0], "Peligrosa")
        self.assertEqual(mx_air_quality.classify_us_aqi(None)[0], "Sin dato")

    def test_geocode_restricts_to_mexico_and_uses_spanish(self):
        captured = {}

        def fake(url):
            captured["url"] = url
            return {"results": [{"name": "Monterrey", "admin1": "Nuevo Leon", "latitude": 25.67, "longitude": -100.31}]}

        with mock.patch.object(mx_air_quality, "http_get_json", side_effect=fake):
            anchor = mx_air_quality.geocode("Monterrey")

        params = urllib.parse.parse_qs(urllib.parse.urlparse(captured["url"]).query)
        self.assertEqual(params["countryCode"], ["MX"])
        self.assertEqual(params["language"], ["es"])
        self.assertEqual(anchor["name"], "Monterrey")
        self.assertEqual(anchor["latitude"], 25.67)

    def test_geocode_raises_for_unknown_place(self):
        with mock.patch.object(mx_air_quality, "http_get_json", return_value={"results": []}):
            with self.assertRaises(SystemExit):
                mx_air_quality.geocode("Lugar Inexistente")

    def test_fetch_air_quality_requests_expected_fields(self):
        captured = {}

        def fake(url):
            captured["url"] = url
            return SAMPLE

        with mock.patch.object(mx_air_quality, "http_get_json", side_effect=fake):
            mx_air_quality.fetch_air_quality(19.43, -99.13)

        params = urllib.parse.parse_qs(urllib.parse.urlparse(captured["url"]).query)
        self.assertTrue(captured["url"].startswith(mx_air_quality.AIR_QUALITY_URL))
        self.assertEqual(params["latitude"], ["19.43"])
        self.assertIn("pm2_5", params["current"][0])
        self.assertIn("us_aqi", params["current"][0])

    def test_build_payload_normalizes_current_block(self):
        payload = mx_air_quality.build_payload(ANCHOR, SAMPLE)
        self.assertEqual(payload["place"]["name"], "Ciudad de Mexico")
        self.assertEqual(payload["medido_en"], "2026-09-23T12:00")
        self.assertEqual(payload["calidad"]["indice_us_aqi"], 64)
        self.assertEqual(payload["calidad"]["categoria"], "Moderada")
        self.assertEqual(payload["calidad"]["pm2_5_ug_m3"], 10.2)

    def test_format_text_includes_index_and_pollutants(self):
        payload = mx_air_quality.build_payload(ANCHOR, SAMPLE)
        text = mx_air_quality.format_text(payload)
        self.assertIn("Ciudad de Mexico", text)
        self.assertIn("64 (Moderada)", text)
        self.assertIn("PM2.5: 10.2", text)

    def test_main_prints_json_with_mocked_network(self):
        stdout = io.StringIO()
        with (
            contextlib.redirect_stdout(stdout),
            mock.patch.object(mx_air_quality, "geocode", return_value=ANCHOR),
            mock.patch.object(mx_air_quality, "fetch_air_quality", return_value=SAMPLE),
        ):
            mx_air_quality.main(["--place", "Ciudad de Mexico", "--json"])

        rendered = json.loads(stdout.getvalue())
        self.assertEqual(rendered["calidad"]["indice_us_aqi"], 64)
        self.assertEqual(rendered["place"]["query"], "Ciudad de Mexico")

    def test_main_uses_coordinates_without_geocoding(self):
        stdout = io.StringIO()
        captured = {}

        def fake_fetch(lat, lon):
            captured["coords"] = (lat, lon)
            return SAMPLE

        with (
            contextlib.redirect_stdout(stdout),
            mock.patch.object(mx_air_quality, "geocode", side_effect=AssertionError("geocode should not run")),
            mock.patch.object(mx_air_quality, "fetch_air_quality", side_effect=fake_fetch),
        ):
            mx_air_quality.main(["--lat", "19.43", "--lon", "-99.13"])

        self.assertEqual(captured["coords"], (19.43, -99.13))
        self.assertIn("Calidad del aire", stdout.getvalue())


if __name__ == "__main__":
    unittest.main()
