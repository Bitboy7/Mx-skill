import contextlib
import datetime as dt
import importlib.util
import io
import json
import pathlib
import unittest
from unittest import mock


ROOT = pathlib.Path(__file__).resolve().parents[2]
MODULE_PATH = ROOT / "mx-holiday-calendar" / "scripts" / "mx_holidays.py"
SPEC = importlib.util.spec_from_file_location("mx_holidays", MODULE_PATH)
mx_holidays = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(mx_holidays)


TODAY = dt.date(2026, 9, 23)

SAMPLE = [
    {
        "date": "2026-11-16",
        "localName": "Dia de la Revolucion",
        "name": "Revolution Day",
        "countryCode": "MX",
        "types": ["Public"],
    },
    {
        "date": "2026-01-01",
        "localName": "Ano Nuevo",
        "name": "New Year's Day",
        "countryCode": "MX",
        "types": ["Public"],
    },
    {
        "date": "2026-04-03",
        "localName": "Viernes Santo",
        "name": "Good Friday",
        "countryCode": "MX",
        "types": ["Bank", "School"],
    },
]


class HolidaysHelperTests(unittest.TestCase):
    def test_days_until_uses_injected_today(self):
        self.assertEqual(mx_holidays.days_until("2026-09-24", TODAY), 1)
        self.assertEqual(mx_holidays.days_until("2026-09-23", TODAY), 0)
        self.assertEqual(mx_holidays.days_until("2026-09-01", TODAY), -22)

    def test_translate_type_known_and_unknown(self):
        self.assertEqual(mx_holidays.translate_type("Public"), "Oficial")
        self.assertEqual(mx_holidays.translate_type("Bank"), "Bancario")
        self.assertEqual(mx_holidays.translate_type("Otro"), "Otro")

    def test_normalize_sorts_by_date_and_translates_types(self):
        rows = mx_holidays.normalize(SAMPLE, today=TODAY)
        self.assertEqual([row["fecha"] for row in rows], ["2026-01-01", "2026-04-03", "2026-11-16"])
        self.assertEqual(rows[0]["tipos"], ["Oficial"])
        self.assertEqual(rows[1]["tipos"], ["Bancario", "Escolar"])
        self.assertEqual(rows[0]["nombre_local"], "Ano Nuevo")

    def test_normalize_skips_items_without_date(self):
        rows = mx_holidays.normalize([{"name": "sin fecha"}], today=TODAY)
        self.assertEqual(rows, [])

    def test_build_payload_reports_mode_and_today(self):
        payload = mx_holidays.build_payload(SAMPLE, mode="year", year=2026, today=TODAY)
        self.assertEqual(payload["modo"], "year")
        self.assertEqual(payload["year"], 2026)
        self.assertEqual(payload["today"], "2026-09-23")
        self.assertEqual(len(payload["results"]), 3)

    def test_format_text_shows_dates_and_countdown(self):
        payload = mx_holidays.build_payload(SAMPLE, mode="year", year=2026, today=TODAY)
        text = mx_holidays.format_text(payload)
        self.assertIn("Dias feriados 2026", text)
        self.assertIn("2026-11-16", text)
        self.assertIn("Dia de la Revolucion", text)

    def test_fetch_holidays_uses_mexico_country_code(self):
        captured = {}

        def fake(url):
            captured["url"] = url
            return SAMPLE

        with mock.patch.object(mx_holidays, "http_get_json", side_effect=fake):
            mx_holidays.fetch_holidays(2027)

        self.assertTrue(captured["url"].endswith("/PublicHolidays/2027/MX"))

    def test_main_year_mode_prints_json(self):
        stdout = io.StringIO()
        with (
            contextlib.redirect_stdout(stdout),
            mock.patch.object(mx_holidays, "fetch_holidays", return_value=SAMPLE),
        ):
            mx_holidays.main(["--year", "2026", "--json"])

        rendered = json.loads(stdout.getvalue())
        self.assertEqual(rendered["modo"], "year")
        self.assertEqual(rendered["results"][0]["fecha"], "2026-01-01")

    def test_main_next_mode_uses_next_endpoint(self):
        stdout = io.StringIO()
        with (
            contextlib.redirect_stdout(stdout),
            mock.patch.object(mx_holidays, "fetch_next_holidays", return_value=SAMPLE) as mocked,
        ):
            mx_holidays.main(["--next", "--json"])

        mocked.assert_called_once()
        rendered = json.loads(stdout.getvalue())
        self.assertEqual(rendered["modo"], "next")


if __name__ == "__main__":
    unittest.main()
