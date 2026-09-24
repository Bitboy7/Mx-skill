# CompraNet Search

## What this skill does

Busca **licitaciones y contrataciones públicas de México**. CompraNet ahora es **Compras MX**, y sus datos se publican en el portal oficial. No existe una API pública oficial estable para todo el catálogo, así que el helper usa la API pública de sólo lectura **LicitIA Abierto** (`api.licitia.com.mx`), que normaliza lo que publica Compras MX, y recurre a los **enlaces oficiales** cuando la API no responde.

## When to use

- "¿Qué licitaciones hay para software?"
- "Busca contrataciones de obra pública de 2026"
- "¿Cómo busco una contratación en Compras MX?"

## When not to use

- Para participar en una licitación (requiere alta en Compras MX y, en su caso, e.firma): el usuario completa ese trámite manualmente.
- Para datos históricos masivos: usar los conjuntos de Datos Abiertos de Compras MX.

## Prerequisites

- Internet y `python3` (solo biblioteca estándar).
- Sin API key ni cuenta.

## Inputs

- `query` (posicional) o `--query`: palabra clave.
- `--limit`: número de resultados (1–50, por defecto 5).
- `--year`: año de ejercicio.
- `--tipo`: tipo de procedimiento.
- `--estatus`: estatus (p. ej. `VIGENTE`, `ADJUDICADO`).
- `--json`: salida JSON.

## Workflow

```bash
npx -y @nomadamas/k-skill@0 exec compranet-search scripts/compranet_search.py -- "software" --limit 5
npx -y @nomadamas/k-skill@0 exec compranet-search scripts/compranet_search.py -- "obra publica" --year 2026 --json
npx -y @nomadamas/k-skill@0 exec compranet-search scripts/compranet_search.py -- "medicamentos" --estatus VIGENTE
```

La API consultada es `GET https://api.licitia.com.mx/api/open/v1/licitaciones?q=<query>&limit=<n>` (parámetros opcionales `anio`, `tipo`, `estatus`). Cada resultado incluye `url_oficial`, que apunta al detalle en Compras MX.

## Output

- `source`: atribución (`LicitIA Abierto`, CC BY 4.0, sobre datos de Compras MX).
- `results[]`: `numero`, `nombre`, `dependencia`, `tipo`, `estatus`, `anio`, `fecha_publicacion`, `adjudicaciones`, `url_oficial`, `url_fuente`.
- `official_links`: buscador de Compras MX, Datos Abiertos y archivo histórico.
- `notice`: aparece si la API pública falló (se muestran solo los enlaces oficiales).

## Done when

- Se mostraron las contrataciones relevantes con su número y enlace oficial.
- Se dejó claro que la participación es un trámite oficial del usuario.

## Failure modes

- API pública caída o con timeout: el helper degrada a los enlaces oficiales (`notice`).
- Sin resultados para la palabra clave.
- Los datos normalizados pueden tener desfase respecto a Compras MX; el enlace oficial es la fuente primaria.

## Notes

- Skill de solo consulta/guía. No inscribe ni presenta ofertas.
- Atribución obligatoria: datos de LicitIA Abierto (CC BY 4.0) sobre Compras MX.
