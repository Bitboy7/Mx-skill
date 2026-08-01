# MX Transit Route

## What this skill does

Calcula **rutas de transporte en México** (auto, caminando, bicicleta) entre dos puntos usando el **routing público OSRM** y **geocodificación Open-Meteo**. Sin API key.

**Límite honesto**: el Metro CDMX y otros sistemas de transporte no exponen una API pública de rutas en tiempo real; esta skill da la ruta por calles y distancia/duración, y remite a los sitios oficiales del STC para conexiones de Metro/Metrobús.

## When to use

- "¿Cómo llego de Polanco al Zócalo?"
- "Ruta caminando de mi casa al trabajo en CDMX"
- "Distancia y tiempo entre dos puntos en Guadalajara"

## When not to use

- Para horarios en tiempo real de Metro/Metrobús: usar las apps/sitios oficiales del STC.
- Para transporte público multimodal (combi/metro) con horarios: no hay fuente pública confiable.

## Prerequisites

- Internet y `python3` (solo biblioteca estándar).
- Sin API key.

## Inputs

- `--from` / `--to`: lugar (colonia/ciudad) o coordenadas `lon,lat`.
- `--mode`: `driving` (por defecto), `walking`, `cycling`.

## Workflow

```bash
npx -y @nomadamas/k-skill@0 exec mx-transit-route scripts/mx_transit_route.py -- --from "Polanco, CDMX" --to "Zocalo, CDMX" --mode driving
npx -y @nomadamas/k-skill@0 exec mx-transit-route scripts/mx_transit_route.py -- --from "-99.19,19.43" --to "-99.13,19.43" --mode walking
```

## Done when

- Se geocodificaron origen y destino.
- Se reportó distancia y duración estimada de la ruta.
- Se aclaró el límite del transporte público en tiempo real.

## Failure modes

- El geocodificador no encuentra un punto de referencia (usar coordenadas o un lugar conocido).
- Ambigüedad: un nombre como "Zócalo" puede resolver a otra localidad; se prefiere CDMX si el query lo menciona, pero conviene confirmar.
- OSRM fuera de servicio o sin ruta (puntos muy lejanos/aislados).

## Notes

- Skill de solo consulta. La ruta es por carretera/camino público, no incluye horarios de transporte público.
