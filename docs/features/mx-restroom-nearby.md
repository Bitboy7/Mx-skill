# Guía de baños públicos cerca (OpenStreetMap/Overpass)

## Qué puedes hacer

- Encontrar baños públicos o abiertos al público cerca de una ubicación en México.
- Ordenar por distancia (haversine recalculado) y ver costo, acceso y horario.
- Consulta por lugar (`--place`) o por coordenadas (`--lat`/`--lon`).

## Entradas

- `--place`: lugar de referencia (ej. "Roma Norte").
- `--lat` / `--lon`: coordenadas directas.
- `--radius`: radio en metros (50–10000, por defecto 1000).
- `--limit`: número máximo de resultados (por defecto 5).
- `--json`: salida JSON.

## Salida

- `place`: lugar resuelto.
- `radio_m`: radio usado.
- `results[]`: `nombre`, `distancia_km`, `direccion`, `costo`, `acceso`, `horario`, `accesible_silla_ruedas`, `osm`, `mapa`.

## Ejemplos

```bash
npx -y @nomadamas/k-skill@0 exec mx-restroom-nearby scripts/mx_restroom_nearby.py -- --place "Roma Norte" --limit 5
npx -y @nomadamas/k-skill@0 exec mx-restroom-nearby scripts/mx_restroom_nearby.py -- --lat 19.4326 --lon -99.1332 --json
```

## Fuentes

- OpenStreetMap (© OpenStreetMap contributors, ODbL): https://www.openstreetmap.org/
- Overpass API: https://overpass-api.de/
- Geocodificación: Open-Meteo https://open-meteo.com/en/docs/geocoding-api

## Precauciones

- OpenStreetMap no tiene estado en tiempo real (ocupación, cierre), solo datos mapeados.
- La cobertura en México es desigual; un resultado vacío no implica que no existan baños.
- El geocodificador puede no reconocer puntos de referencia muy específicos; usa colonia/ciudad.
