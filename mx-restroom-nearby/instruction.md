# MX Restroom Nearby

## What this skill does

Encuentra **baños públicos o abiertos al público cerca de una ubicación en México** usando datos de **OpenStreetMap** a través de la **Overpass API** (sin API key, datos ODbL). La ubicación se resuelve con la geocodificación pública de Open-Meteo.

- No estima tu ubicación: usa el lugar que indiques o coordenadas `--lat/--lon`.
- No muestra ocupación ni estado en tiempo real (OpenStreetMap no los tiene).
- Solo consulta; no reserva ni paga.

## When to use

- "¿Dónde hay baños públicos cerca del Zócalo?"
- "Baños en Roma Norte"
- "Baños cerca de mí" (comparte tu ubicación en el bot con 📍)

## When not to use

- Para baños de un establecimiento privado con requisitos de consumo (pueden no estar mapeados).
- Para accesibilidad garantizada: el campo `wheelchair` de OSM puede estar incompleto.

## Prerequisites

- Internet y `python3` (solo biblioteca estándar).
- Sin API key.

## Inputs

- `--place`: lugar de referencia en México, o `--lat`/`--lon` para coordenadas.
- `--radius`: radio de búsqueda en metros (50–10000, por defecto 1000).
- `--limit`: número máximo de resultados (por defecto 5).
- `--json`: salida JSON (por defecto es un resumen en español).

## Workflow

```bash
npx -y @nomadamas/k-skill@0 exec mx-restroom-nearby scripts/mx_restroom_nearby.py -- --place "Zocalo CDMX" --limit 5
npx -y @nomadamas/k-skill@0 exec mx-restroom-nearby scripts/mx_restroom_nearby.py -- --place "Roma Norte" --radius 1200 --json
npx -y @nomadamas/k-skill@0 exec mx-restroom-nearby scripts/mx_restroom_nearby.py -- --lat 19.4326 --lon -99.1332
```

La consulta es `nwr["amenity"="toilets"](around:radio,lat,lon); out center tags;` contra Overpass. El endpoint principal es `overpass-api.de` y el secundario `overpass.kumi.systems`.

## Output

- `place`: lugar resuelto (nombre, estado, coordenadas).
- `radio_m`: radio usado.
- `results[]`: `nombre`, `distancia_km` (haversine recalculado), `direccion`, `costo` (Gratis/De pago/No especificado), `acceso`, `horario`, `accesible_silla_ruedas`, `osm` y `mapa`.

## Done when

- Se resolvió el lugar y se listaron (si existen) los baños más cercanos con distancia.
- Se indicó que la fuente es OpenStreetMap y que no hay estado en tiempo real.

## Failure modes

- Overpass devuelve 429/504 o el radio es demasiado amplio: reducir `--radius` y reintentar.
- El lugar no se encuentra en el geocodificador público: usar otro nombre o `--lat/--lon`.
- Sin resultados: la zona puede no estar mapeada en OpenStreetMap.
- La cobertura de OSM en México es desigual; un resultado vacío no significa que no existan baños.

## Notes

- Skill de solo consulta sobre datos abiertos de OpenStreetMap (© OpenStreetMap contributors, ODbL).
- La dirección y el costo dependen de las etiquetas cargadas por la comunidad en OSM.
