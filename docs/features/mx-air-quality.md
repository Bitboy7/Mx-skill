# Guía de calidad del aire en México (Open-Meteo Air Quality)

## Qué puedes hacer

- Calidad del aire actual de una ciudad de México: PM10, PM2.5, índice **US AQI** y categoría.
- Otros contaminantes: monóxido de carbono, dióxido de nitrógeno, ozono y dióxido de azufre.
- Consulta por ciudad (`--place`) o por coordenadas (`--lat`/`--lon`).

## Entradas

- `--place`: ciudad (ej. "Ciudad de Mexico").
- `--lat` / `--lon`: coordenadas directas.
- `--json`: salida JSON.

## Salida

- `place`: ciudad resuelta.
- `medido_en`: hora de la medición.
- `calidad.indice_us_aqi`, `calidad.categoria`, `calidad.recomendacion`.
- `calidad.pm2_5_ug_m3`, `calidad.pm10_ug_m3` y contaminantes adicionales.

## Ejemplos

```bash
npx -y @nomadamas/k-skill@0 exec mx-air-quality scripts/mx_air_quality.py -- --place "Ciudad de Mexico" --json
npx -y @nomadamas/k-skill@0 exec mx-air-quality scripts/mx_air_quality.py -- --lat 19.43 --lon -99.13
```

## Fuentes

- Open-Meteo Air Quality (pública, sin clave): https://open-meteo.com/en/docs/air-quality-api
- Referencia oficial de México: SEDEMA / Sistema de Monitoreo Atmosférico https://aire.cdmx.gob.mx/
- SEMARNAT: https://www.gob.mx/semarnat

## Precauciones

- Las categorías usan los cortes US EPA del índice US AQI que expone Open-Meteo.
- Para contingencias ambientales oficiales usa los avisos de SEDEMA/SEMARNAT.
- No es información médica; para temas de salud consulta a un profesional.
