"""Pruebas offline del helper sat-consulta (sin red real).

Se ejecuta con cualquier Python 3.10+:
  python -m unittest discover -s sat-consulta/tests -p "test_*.py"
"""

import contextlib
import importlib.util
import io
import json
import pathlib
import sys
import types
import unittest
from unittest import mock

ROOT = pathlib.Path(__file__).resolve().parents[2]
MODULE_PATH = ROOT / "sat-consulta" / "scripts" / "sat_consulta.py"
SPEC = importlib.util.spec_from_file_location("sat_consulta", MODULE_PATH)
sat_consulta = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(sat_consulta)


SOAP_RESPONSE = b"""<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
  <soap:Body>
    <ConsultaResponse xmlns="http://tempuri.org/">
      <ConsultaResult>
        <CodigoEstatus>S - Comprobante obtenido satisfactoriamente.</CodigoEstatus>
        <EsCancelable>Cancelable sin aceptacion</EsCancelable>
        <Estado>Vigente</Estado>
        <EstatusCancelacion></EstatusCancelacion>
        <ValidacionEFOS>100</ValidacionEFOS>
      </ConsultaResult>
    </ConsultaResponse>
  </soap:Body>
</soap:Envelope>"""


class _FakeResponse:
    def __init__(self, body):
        self._body = body

    def read(self):
        return self._body

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False


def _fake_satcfdi_modules(situacion="Presunto", catalogo=None):
    """Inyecta modulos falsos de satcfdi para probar sin la dependencia."""
    catalogo = catalogo if catalogo is not None else {
        "601": "General de Ley Personas Morales",
        "602": "Personas Morales con Fines no Lucrativos",
    }

    pkg = types.ModuleType("satcfdi")
    pacs = types.ModuleType("satcfdi.pacs")
    sat = types.ModuleType("satcfdi.pacs.sat")
    catalogs = types.ModuleType("satcfdi.catalogs")

    class _FakeSAT:
        def list_69b(self, rfc):
            if situacion is None:
                return None

            class _Estado:
                value = situacion

            return _Estado()

    sat.SAT = _FakeSAT
    catalogs.select_all = lambda table: dict(catalogo)
    pkg.pacs = pacs
    pkg.catalogs = catalogs
    pacs.sat = sat

    return {
        "satcfdi": pkg,
        "satcfdi.pacs": pacs,
        "satcfdi.pacs.sat": sat,
        "satcfdi.catalogs": catalogs,
    }


class SatConsultaHelperTests(unittest.TestCase):
    def test_build_expresion(self):
        expresion = sat_consulta.build_expresion("AAA010101AAA", "BBB010101BBB", "1250.30", "uuid-1")
        self.assertIn("re=AAA010101AAA", expresion)
        self.assertIn("rr=BBB010101BBB", expresion)
        self.assertIn("tt=1250.30", expresion)
        self.assertIn("id=uuid-1", expresion)

    def test_parse_consulta_result(self):
        result = sat_consulta.parse_consulta_result(SOAP_RESPONSE)
        self.assertEqual(result["Estado"], "Vigente")
        self.assertEqual(result["CodigoEstatus"], "S - Comprobante obtenido satisfactoriamente.")

    def test_sanitize_dates(self):
        import datetime

        data = {"fecha": datetime.date(2020, 1, 2), "regimen": object()}
        clean = sat_consulta.sanitize(data)
        self.assertEqual(clean["fecha"], "2020-01-02")
        self.assertIsInstance(clean["regimen"], str)

    def test_consulta_factura_requires_fields(self):
        args = sat_consulta.build_parser().parse_args(["--action", "factura"])
        with self.assertRaises(ValueError):
            sat_consulta.consulta_factura(args)

    def test_consulta_factura_parses_response(self):
        args = sat_consulta.build_parser().parse_args([
            "--action", "factura",
            "--uuid", "abc",
            "--rfc-emisor", "aaa010101aaa",
            "--rfc-receptor", "bbb010101bbb",
            "--total", "1250.30",
        ])
        with mock.patch.object(
            sat_consulta.urllib.request, "urlopen", return_value=_FakeResponse(SOAP_RESPONSE)
        ):
            result = sat_consulta.consulta_factura(args)

        self.assertEqual(result["estado"], "Vigente")
        self.assertTrue(result["vigente"])
        self.assertEqual(result["rfc_emisor"], "AAA010101AAA")
        self.assertEqual(result["validacion_efos"], "100")

    def test_main_prints_json_for_factura(self):
        stdout = io.StringIO()
        with (
            contextlib.redirect_stdout(stdout),
            mock.patch.object(
                sat_consulta.urllib.request, "urlopen", return_value=_FakeResponse(SOAP_RESPONSE)
            ),
        ):
            sat_consulta.main([
                "--action", "factura", "--uuid", "abc",
                "--rfc-emisor", "AAA010101AAA", "--rfc-receptor", "BBB010101BBB",
                "--total", "1250.30", "--json",
            ])
        rendered = json.loads(stdout.getvalue())
        self.assertEqual(rendered["estado"], "Vigente")

    def test_consulta_69b_found(self):
        with mock.patch.dict(sys.modules, _fake_satcfdi_modules(situacion="Presunto")):
            args = sat_consulta.build_parser().parse_args(["--action", "69b", "--rfc", "aaa010101aaa"])
            result = sat_consulta.consulta_69b(args)
        self.assertTrue(result["encontrado"])
        self.assertEqual(result["situacion"], "Presunto")
        self.assertEqual(result["rfc"], "AAA010101AAA")

    def test_consulta_69b_not_found(self):
        with mock.patch.dict(sys.modules, _fake_satcfdi_modules(situacion=None)):
            args = sat_consulta.build_parser().parse_args(["--action", "69b", "--rfc", "aaa010101aaa"])
            result = sat_consulta.consulta_69b(args)
        self.assertFalse(result["encontrado"])
        self.assertIsNone(result["situacion"])

    def test_consulta_catalogo_exact_clave(self):
        with mock.patch.dict(sys.modules, _fake_satcfdi_modules()):
            args = sat_consulta.build_parser().parse_args([
                "--action", "catalogo", "--tipo", "regimen", "--clave", "601",
            ])
            result = sat_consulta.consulta_catalogo(args)
        self.assertTrue(result["encontrado"])
        self.assertEqual(result["descripcion"], "General de Ley Personas Morales")

    def test_consulta_catalogo_buscar(self):
        with mock.patch.dict(sys.modules, _fake_satcfdi_modules()):
            args = sat_consulta.build_parser().parse_args([
                "--action", "catalogo", "--tipo", "regimen", "--buscar", "morales",
            ])
            result = sat_consulta.consulta_catalogo(args)
        self.assertGreaterEqual(len(result["resultados"]), 1)

    def test_consulta_catalogo_requires_clave_or_buscar(self):
        args = sat_consulta.build_parser().parse_args(["--action", "catalogo", "--tipo", "regimen"])
        with self.assertRaises(ValueError):
            sat_consulta.consulta_catalogo(args)

    def test_consulta_catalogo_rejects_unknown_tipo(self):
        args = sat_consulta.build_parser().parse_args([
            "--action", "catalogo", "--tipo", "nope", "--clave", "1",
        ])
        with self.assertRaises(ValueError):
            sat_consulta.consulta_catalogo(args)

    def test_main_requires_action(self):
        with self.assertRaises(SystemExit):
            sat_consulta.main([])

    def test_main_accepts_args_used_by_the_bot(self):
        stdout = io.StringIO()
        with (
            contextlib.redirect_stdout(stdout),
            mock.patch.dict(sys.modules, _fake_satcfdi_modules(situacion="Definitivo")),
        ):
            sat_consulta.main(["--action", "69b", "--rfc", "AAA010101AAA", "--json"])
        rendered = json.loads(stdout.getvalue())
        self.assertEqual(rendered["situacion"], "Definitivo")


if __name__ == "__main__":
    unittest.main()
