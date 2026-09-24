# MX Air Quality

## What this skill does

Consulta la **calidad del aire** de una ciudad de México con la fuente pública **Open-Meteo Air Quality API** (sin API key): PM10, PM2.5, índice **US AQI** y otros contaminantes. Referencia oficial de México: **SEDEMA** (Sistema de Monitoreo Atmosférico, `aire.cdmx.gob.mx`) y **SEMARNAT**.

## When to use

- "¿Cómo está la calidad del aire en la Ciudad de México?"
- "¿Hay contingencia ambiental hoy en Monterrey?"
- "Nivel de PM2.5 en Guadalajara"

## When not to use

- Para decretos oficiales de contingencia ambiental: usa los avisos de la SEDEMA/SEMARNAT o del gobierno de tu estado.
- Para salud personal (asma, alergias): consulta a un profesional; esta skill solo informa valores públicos.

## Prerequisites

- Internet y `python3` (solo biblioteca estándar).
- Sin API key.

## Inputs

- `--place`: ciudad o localidad en México, o `--lat`/`--lon` para coordenadas directas.
- `--json`: salida JSON (por defecto es un resumen en español).

## Workflow

```bash
npx -y @nomadamas/k-skill@0 exec mx-air-quality scripts/mx_air_quality.py -- --place "Ciudad de Mexico"
npx -y @nomadamas/k-skill@0 exec mx-air-quality scripts/mx_air_quality.py -- --lat 19.43 --lon -99.13 --json
```

La ciudad se resuelve con la geocodificación pública de Open-Meteo (restringida a `countryCode=MX`) y la calidad del aire se consulta al endpoint público de Open-Meteo Air Quality.

## Output

- `place`: ciudad resuelta (nombre, estado, coordenadas).
- `medido_en`: marca de tiempo de la medición.
- `calidad.indice_us_aqi`, `calidad.categoria`, `calidad.recomendacion`.
- `calidad.pm10_ug_m3`, `calidad.pm2_5_ug_m3` y demás contaminantes (`monoxido_carbono_ug_m3`, `dioxido_nitrogeno_ug_m3`, `ozono_ug_m3`, `dioxido_azufre_ug_m3`).

## Done when

- Se resolvió la ciudad (o se usaron coordenadas) y se mostró el índice y la categoría.
- Se listaron al menos PM2.5 y PM10 con su unidad.
- Se indicó la hora de medición y que es una fuente pública agregada.

## Failure modes

- La ciudad no se encuentra en el geocodificador público (probar otro nombre o coordenadas).
- Open-Meteo está caído o con 5xx (reintentar más tarde).
- `indice_us_aqi` puede venir vacío en zonas sin cobertura; en ese caso se reporta "Sin dato".

## Notes

- Skill de solo consulta. Las categorías usan los cortes US EPA del índice US AQI que expone Open-Meteo.
- Open-Meteo es una fuente pública agregada; para mediciones oficiales de la Ciudad de México se remite a la SEDEMA y para el resto del país a SEMARNAT/estados.
