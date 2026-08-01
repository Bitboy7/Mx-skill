"""Skill: rutas de transporte (mx-transit-route)."""

from .. import config, formatting, geo, runner
from .registry import SkillEntry, register

SEPARATORS = (" a ", " hasta ", " to ", " hacia ")
PREFIXES = ("a ", "hasta ", "to ", "hacia ")


def _split_route(text: str) -> tuple[str, str] | None:
    lower = text.lower()
    for sep in SEPARATORS:
        if sep in lower:
            idx = lower.index(sep)
            origin = text[:idx].strip()
            dest = text[idx + len(sep):].strip()
            if origin and dest:
                return origin, dest
    return None


async def ruta(update, context) -> str:
    text = " ".join(context.args).strip()
    coords = geo.effective(context)

    # /ruta a <destino>  → origen = ubicación compartida
    if coords and text:
        lower = text.lower()
        for prefix in PREFIXES:
            if lower.startswith(prefix):
                dest = text[len(prefix):].strip()
                if dest:
                    data = await runner.run_skill(
                        "mx-transit-route",
                        ["--from-lat", str(coords[0]), "--from-lon", str(coords[1]), "--to", dest],
                    )
                    return _format_route(data, "tu ubicación", dest)

    if not text:
        return "Uso: <code>/ruta &lt;origen&gt; a &lt;destino&gt;</code>  (o comparte 📍 y usa /ruta a &lt;destino&gt;)"

    origin_dest = _split_route(text)
    if not origin_dest:
        return "Uso: <code>/ruta &lt;origen&gt; a &lt;destino&gt;</code>"
    origin, dest = origin_dest

    data = await runner.run_skill("mx-transit-route", ["--from", origin, "--to", dest])
    return _format_route(data, origin, dest)


def _format_route(data: dict, origin_label: str, dest_label: str) -> str:
    o = data.get("origin") or {}
    d = data.get("destination") or {}
    lines = [
        formatting.bullet("De", o.get("name") or origin_label),
        formatting.bullet("A", d.get("name") or dest_label),
        formatting.bullet("Modo", data.get("mode")),
        formatting.bullet("Distancia", f"{data.get('distancia_km')} km"),
        formatting.bullet("Duración aprox.", f"{data.get('duracion_min')} min"),
    ]
    return formatting.section("Ruta", "\n".join(lines))


register(
    SkillEntry(
        command="ruta",
        description="Ruta auto/caminando/bici entre dos puntos en México",
        usage="/ruta <origen> a <destino>",
        handler=ruta,
        skill_id="mx-transit-route",
    )
)
