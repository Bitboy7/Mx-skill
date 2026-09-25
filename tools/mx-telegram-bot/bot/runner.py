"""Ejecuta los scripts de las skills MX como subprocesos y parsea su JSON.

Los helpers de las skills son scripts Python independientes (solo stdlib) que
imprimen JSON por stdout. El bot los invoca con el mismo intérprete en uso.
"""

from __future__ import annotations

import asyncio
import json
import logging
import sys
import time
from pathlib import Path

logger = logging.getLogger("mx-bot.runner")

REPO_ROOT = Path(__file__).resolve().parents[3]

# Map skill id -> ruta del helper dentro del repo (relativa a REPO_ROOT).
SKILL_SCRIPTS: dict[str, Path] = {
    "mx-weather": Path("mx-weather/scripts/mx_weather.py"),
    "mx-news": Path("mx-news/scripts/mx_news.py"),
    "melate-results": Path("melate-results/scripts/melate_results.py"),
    "mx-zipcode-search": Path("mx-zipcode-search/scripts/mx_zipcode_search.py"),
    "sat-rfc-lookup": Path("sat-rfc-lookup/scripts/sat_rfc_lookup.py"),
    "ecobici-cdmx": Path("ecobici-cdmx/scripts/ecobici_cdmx.py"),
    "cine-mx": Path("cine-mx/scripts/cine_mx.py"),
    "comision-ine": Path("comision-ine/scripts/comision_ine.py"),
    "precios-canasta": Path("precios-canasta/scripts/precios_canasta.py"),
    "mx-transit-route": Path("mx-transit-route/scripts/mx_transit_route.py"),
    "gas-prices-mx": Path("gas-prices-mx/scripts/gas_prices.py"),
    "mx-product-search": Path("mx-product-search/scripts/mx_product_search.py"),
    "mx-real-estate": Path("mx-real-estate/scripts/mx_real_estate.py"),
    "delivery-tracking-mx": Path("delivery-tracking-mx/scripts/delivery_tracking_mx.py"),
    "mx-sports-results": Path("mx-sports-results/scripts/mx_sports.py"),
    "mx-air-quality": Path("mx-air-quality/scripts/mx_air_quality.py"),
    "mx-holiday-calendar": Path("mx-holiday-calendar/scripts/mx_holidays.py"),
    "mx-restroom-nearby": Path("mx-restroom-nearby/scripts/mx_restroom_nearby.py"),
    "compranet-search": Path("compranet-search/scripts/compranet_search.py"),
    "beneficios-programas": Path("beneficios-programas/scripts/beneficios_programas.py"),
    "mx-job-search": Path("mx-job-search/scripts/mx_job_search.py"),
    "mx-university-search": Path("mx-university-search/scripts/mx_university_search.py"),
    "mx-used-car-search": Path("mx-used-car-search/scripts/mx_used_car_search.py"),
    "sat-consulta": Path("sat-consulta/scripts/sat_consulta.py"),
}


class SkillError(Exception):
    """Error controlado de una skill (mensaje ya en español)."""


def _summarize_args(args: list[str]) -> str:
    return " ".join(str(a)[:40] for a in args[:10])


def resolve_script(skill_id: str) -> Path:
    try:
        script = SKILL_SCRIPTS[skill_id]
    except KeyError as exc:
        logger.error("skill desconocida: %s", skill_id)
        raise SkillError(f"Skill desconocida: {skill_id}") from exc
    path = REPO_ROOT / script
    if not path.is_file():
        logger.error("helper no encontrado skill=%s path=%s", skill_id, path)
        raise SkillError(f"No se encontró el helper de la skill {skill_id}: {path}")
    return path


async def run_skill(skill_id: str, args: list[str], timeout: float = 45.0) -> dict:
    """Ejecuta la skill y devuelve su JSON. Lanza SkillError con mensaje amigable."""
    script = resolve_script(skill_id)
    logger.info("skill=%s ejecutando args=[%s]", skill_id, _summarize_args(args))
    started = time.perf_counter()
    proc = await asyncio.create_subprocess_exec(
        sys.executable,
        str(script),
        *args,
        cwd=REPO_ROOT,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    try:
        stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout)
    except asyncio.TimeoutError:
        proc.kill()
        await proc.wait()
        elapsed = (time.perf_counter() - started) * 1000
        logger.error("skill=%s timeout tras %.0f ms (> %.0fs)", skill_id, elapsed, timeout)
        raise SkillError(f"La skill {skill_id} tardó demasiado (> {timeout:.0f}s).")

    elapsed = (time.perf_counter() - started) * 1000
    out_text = stdout.decode("utf-8", "ignore").strip()
    err_text = stderr.decode("utf-8", "ignore").strip()

    # Algunas skills imprimen JSON en stdout y salen con código != 0 (p. ej.
    # sat-rfc-lookup sale con 2 en RFC inválidos). El JSON es la fuente de verdad.
    if out_text:
        try:
            data = json.loads(out_text)
            logger.info("skill=%s ok en %.0f ms (rc=%s)", skill_id, elapsed, proc.returncode)
            return data
        except json.JSONDecodeError:
            logger.warning(
                "skill=%s stdout no es JSON (%.0f ms, rc=%s): %.200s",
                skill_id,
                elapsed,
                proc.returncode,
                out_text,
            )

    if err_text:
        # SystemExit imprime su mensaje en stderr.
        last_line = err_text.strip().splitlines()[-1] if err_text.strip() else ""
        logger.warning("skill=%s falló (%.0f ms, rc=%s): %s", skill_id, elapsed, proc.returncode, last_line)
        raise SkillError(last_line or "Error desconocido de la skill.")

    logger.warning("skill=%s no devolvió resultados (%.0f ms, rc=%s)", skill_id, elapsed, proc.returncode)
    raise SkillError(f"La skill {skill_id} no devolvió resultados.")
