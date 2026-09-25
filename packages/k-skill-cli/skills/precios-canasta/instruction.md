# Precios Canasta (PROFECO)

## What this skill does

Consulta los **precios de la canasta básica en México** (por tienda, estado y zona) usando el reporte semanal oficial **"Productos de Primera Necesidad"** del programa **Quién es Quién en los Precios** de **PROFECO**, publicado como PDF en `qqph.profeco.gob.mx`. Sin API key.

El reporte lista, por zona geográfica, los 5 establecimientos con el costo de canasta (24 productos) más alto y los 5 más bajo.

## When to use

- "¿Dónde está la canasta básica más barata en Jalisco?"
- "Precios de la canasta en la CDMX"
- "¿Cuánto cuesta la canasta básica en Soriana/Walmart?"

## When not to use

- Para precios por producto individual (no es un catálogo de precios por artículo).

## Prerequisites

- Internet y `python3` (solo biblioteca estándar).
- Sin API key.

## Inputs

- `--top N`: mostrar las N canastas más baratas (por defecto 10).
- `--estado`: filtrar por estado (opcional; acepta alias como `CDMX`, `Edomex` o `NL`).

## Workflow

```bash
npx -y @nomadamas/k-skill@0 exec precios-canasta scripts/precios_canasta.py -- --top 10
npx -y @nomadamas/k-skill@0 exec precios-canasta scripts/precios_canasta.py -- --estado "Jalisco"
```

## Official surface

- Reporte semanal (PDF): `https://qqph.profeco.gob.mx` (categoría "PRIMERA NECESIDAD").
- Índice de reportes por año: `https://qqph.profeco.gob.mx/api/archivos/<año>`.
- Portal oficial PROFECO "Quién es Quién en los Precios": `https://www.profeco.gob.mx/precios/canasta/home.aspx`.

## Done when

- Se listaron las tiendas con el costo de la canasta básica, ordenadas de menor a mayor.
- Se indicó la fecha del reporte (semana de precios vigentes) y la zona/estado.

## Failure modes

- La antigua API `api.datos.gob.mx/v1/precio.canasta.basica` fue retirada junto con la plataforma datos.gob.mx v1; por eso se usa el PDF oficial.
- Si PROFECO responde HTTP no-200 o no responde, el helper sale con un mensaje que remite al portal.
- Si el diseño del PDF cambia y no se pueden extraer filas, el helper falla indicando la URL del PDF para revisión manual en `precios_canasta.py`.

## Notes

- Skill de solo consulta. No compra ni reserva.
- El reporte solo publica los 5 precios más altos y 5 más bajos por zona; no es el universo completo de tiendas.
- Los precios corresponden a la canasta de 24 productos de primera necesidad y varían por región y semana.
