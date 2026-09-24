import contextlib
import importlib.util
import io
import json
import pathlib
import unittest
from unittest import mock


ROOT = pathlib.Path(__file__).resolve().parents[2]
MODULE_PATH = ROOT / "mx-restroom-nearby" / "scripts" / "mx_restroom_nearby.py"
SPEC = importlib.util.spec_from_file_location("mx_restroom_nearby", MODULE_PATH)
mx_restroom_nearby = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(mx_restroom_nearby)


LAT, LON = 19.4326, -99.1332

ANCHOR = {
    "query": "Zocalo CDMX",
    "name": "Zocalo",
    "admin1": "Ciudad de Mexico",
    "latitude": LAT,
    "longitude": LON,
}

OVERPASS_PAYLOAD = {
    "version": 0.6,
    "elements": [
        {
            "type": "node",
            "id": 1,
            "lat": 19.4330,
            "lon": -99.1330,
            "tags": {"amenity": "toilets", "name": "Sanitarios Publicos", "fee": "no", "access": "yes"},
        },
        {
            "type": "way",
            "id": 2,
            "center": {"lat": 19.4350, "lon": -99.1332},
            "tags": {"amenity": "toilets", "addr:street": "Calle 5", "addr:housenumber": "10", "fee": "yes", "access": "customers"},
        },
        {"type": "node", "id": 3, "tags": {"amenity": "toilets"}},
    ],
}


class RestroomHelperTests(unittest.TestCase):
    def test_haversine_km_is_zero_for_same_point(self):
        self.assertEqual(mx_restroom_nearby.haversine_km(LAT, LON, LAT, LON), 0)

    def test_haversine_km_matches_known_distance(self):
        # CDMX Zocalo to a point ~1.11 km north.
        distance = mx_restroom_nearby.haversine_km(19.4326, -99.1332, 19.4426, -99.1332)
        self.assertAlmostEqual(distance, 1.112, places=2)

    def test_build_overpass_query_targets_toilets_around_point(self):
        query = mx_restroom_nearby.build_overpass_query(19.43, -99.13, 800)
        self.assertIn('nwr["amenity"="toilets"]', query)
        self.assertIn("(around:800,19.43,-99.13)", query)
        self.assertIn("out center tags;", query)

    def test_element_coords_supports_nodes_and_way_centers(self):
        self.assertEqual(mx_restroom_nearby.element_coords({"lat": 1.0, "lon": 2.0}), (1.0, 2.0))
        self.assertEqual(
            mx_restroom_nearby.element_coords({"center": {"lat": 3.0, "lon": 4.0}}), (3.0, 4.0)
        )
        self.assertEqual(mx_restroom_nearby.element_coords({"tags": {}}), (None, None))

    def test_classify_fee_and_access(self):
        self.assertEqual(mx_restroom_nearby.classify_fee({"fee": "no"}), "Gratis")
        self.assertEqual(mx_restroom_nearby.classify_fee({"fee": "yes"}), "De pago")
        self.assertEqual(mx_restroom_nearby.classify_fee({}), "No especificado")
        self.assertEqual(mx_restroom_nearby.classify_access({"access": "customers"}), "Solo clientes")
        self.assertEqual(mx_restroom_nearby.classify_access({"access": "private"}), "Privado")
        self.assertEqual(mx_restroom_nearby.classify_access({}), "No especificado")

    def test_format_address_builds_street_and_locality(self):
        address = mx_restroom_nearby.format_address(
            {"addr:street": "Av. Juarez", "addr:housenumber": "12", "addr:postcode": "06000"}
        )
        self.assertEqual(address, "Av. Juarez 12, 06000")
        self.assertIsNone(mx_restroom_nearby.format_address({}))

    def test_select_results_sorts_by_distance_and_limits(self):
        results = mx_restroom_nearby.select_results(OVERPASS_PAYLOAD, LAT, LON, limit=5)
        self.assertEqual([row["osm"] for row in results], ["node/1", "way/2"])
        self.assertTrue(results[0]["distancia_km"] <= results[1]["distancia_km"])
        self.assertEqual(results[0]["costo"], "Gratis")
        self.assertEqual(results[1]["direccion"], "Calle 5 10")
        self.assertEqual(results[1]["mapa"], "https://www.openstreetmap.org/way/2")

    def test_select_results_respects_limit(self):
        results = mx_restroom_nearby.select_results(OVERPASS_PAYLOAD, LAT, LON, limit=1)
        self.assertEqual(len(results), 1)

    def test_fetch_overpass_falls_back_to_second_endpoint(self):
        calls = []

        def fake(url, timeout=45):
            calls.append(url)
            if "a.test" in url:
                raise OSError("down")
            return {"elements": []}

        with mock.patch.object(mx_restroom_nearby, "http_get_json", side_effect=fake):
            payload = mx_restroom_nearby.fetch_overpass(
                "query", endpoints=["https://a.test", "https://b.test"]
            )

        self.assertEqual(payload, {"elements": []})
        self.assertEqual(len(calls), 2)

    def test_fetch_overpass_raises_when_all_endpoints_fail(self):
        calls = []

        def fake(url, timeout=45):
            calls.append(url)
            raise OSError("down")

        with mock.patch.object(mx_restroom_nearby, "http_get_json", side_effect=fake):
            with self.assertRaises(SystemExit):
                mx_restroom_nearby.fetch_overpass("q", endpoints=["https://a.test"], attempts=2, pause=0)

        self.assertEqual(len(calls), 2)

    def test_fetch_overpass_retries_after_transient_failure(self):
        calls = []

        def fake(url, timeout=45):
            calls.append(url)
            if len(calls) == 1:
                raise OSError("timeout")
            return {"elements": [{"type": "node", "id": 1, "lat": 19.4, "lon": -99.1}]}

        with mock.patch.object(mx_restroom_nearby, "http_get_json", side_effect=fake):
            payload = mx_restroom_nearby.fetch_overpass(
                "q", endpoints=["https://a.test"], attempts=2, pause=0
            )

        self.assertEqual(len(payload["elements"]), 1)
        self.assertEqual(len(calls), 2)

    def test_main_prints_json_with_mocked_network(self):
        stdout = io.StringIO()
        with (
            contextlib.redirect_stdout(stdout),
            mock.patch.object(mx_restroom_nearby, "geocode", return_value=ANCHOR),
            mock.patch.object(mx_restroom_nearby, "fetch_overpass", return_value=OVERPASS_PAYLOAD),
        ):
            mx_restroom_nearby.main(["--place", "Zocalo CDMX", "--json"])

        rendered = json.loads(stdout.getvalue())
        self.assertEqual(rendered["radio_m"], 1000)
        self.assertEqual(len(rendered["results"]), 2)
        self.assertEqual(rendered["results"][0]["nombre"], "Sanitarios Publicos")

    def test_main_text_output_when_no_results(self):
        stdout = io.StringIO()
        with (
            contextlib.redirect_stdout(stdout),
            mock.patch.object(mx_restroom_nearby, "geocode", return_value=ANCHOR),
            mock.patch.object(mx_restroom_nearby, "fetch_overpass", return_value={"elements": []}),
        ):
            mx_restroom_nearby.main(["--place", "Zocalo CDMX"])

        self.assertIn("No se encontraron banos publicos", stdout.getvalue())


if __name__ == "__main__":
    unittest.main()
