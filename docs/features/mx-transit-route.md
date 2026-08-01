# Guía de rutas de transporte en México

## Qué puedes hacer

- Ruta (auto/caminando/bici) entre dos puntos en México.
- Distancia y duración estimada.

## Entradas

- `--from` / `--to`: lugar o coordenadas `lon,lat`.
- `--mode`: `driving`, `walking`, `cycling`.

## Ejemplos

```bash
npx -y @nomadamas/k-skill@0 exec mx-transit-route scripts/mx_transit_route.py -- --from "Polanco, CDMX" --to "Zocalo, CDMX"
```

## Fuentes

- OSRM público: https://router.project-osrm.org/
- Geocodificación Open-Meteo.

## Precauciones

- El Metro CDMX no tiene API pública de rutas; la ruta es por calles.
- Nombres ambiguos ("Zócalo") pueden resolver a otra localidad; usar coordenadas si es necesario.
- No incluye horarios de transporte público.
