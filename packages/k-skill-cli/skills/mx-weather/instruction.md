# MX Weather

## What this skill does

Consulta el **clima actual y el pronóstico** de una ciudad de México usando la fuente pública **Open-Meteo** (sin API key). Referencia oficial de México: **CONAGUA / Servicio Meteorológico Nacional** (SMN), a la que se remite para alertas oficiales.

## When to use

- "¿Cómo está el clima en Guadalajara?"
- "¿Lloverá mañana en Monterrey?"
- "Pronóstico de 5 días para la Ciudad de México"

## When not to use

- Para alertas meteorológicas oficiales (huracanes, tormentas severas): usa los avisos del SMN (`smn.conagua.gob.mx`).

## Prerequisites

- Internet y `python3` (solo biblioteca estándar).
- Sin API key.

## Inputs

- `--place`: ciudad o localidad en México, o `--lat/--lon` para usar coordenadas directas.
- `--days`: días de pronóstico (1–7, por defecto 3).

## Workflow

```bash
npx -y @nomadamas/k-skill@0 exec mx-weather scripts/mx_weather.py -- --place "Guadalajara" --days 3
npx -y @nomadamas/k-skill@0 exec mx-weather scripts/mx_weather.py -- --lat 19.43 --lon -99.13 --days 5
```

La ciudad se resuelve con geocodificación pública (Open-Meteo) y el pronóstico usa el endpoint público de Open-Meteo.

## Done when

- Se resolvió la ciudad y se mostró el clima actual (temp, humedad, viento, descripción).
- Se mostró el pronóstico diario (máx/mín, probabilidad de lluvia, descripción).

## Failure modes

- La ciudad no se encuentra en el geocodificador público (probar otro nombre o coordenadas).
- Open-Meteo está caído o con 5xx (reintentar).
- Puntos de referencia muy específicos pueden resolverse a otra zona; usar un nombre de colonia/ciudad conocido.

## Notes

- Skill de solo consulta. Los códigos WMO se traducen a descripciones en español.
- Open-Meteo es una fuente pública agregada; para pronósticos oficiales del gobierno mexicano se remite al SMN.
