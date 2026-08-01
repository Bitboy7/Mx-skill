# Ecobici CDMX

## What this skill does

Encuentra **estaciones de Ecobici CDMX** con bicicletas disponibles cerca de una ubicación, usando el **feed GBFS oficial** de Ecobici (Lyft Bikes). Sin API key.

## When to use

- "¿Dónde hay una Ecobici cerca de la Roma Norte?"
- "Estaciones de bici con espacios libres cerca de mí"
- "¿Hay bicis disponibles en el Centro?"

## When not to use

- Para rentar una bici o crear cuenta: eso se hace en la app/sitio oficial de Ecobici.

## Prerequisites

- Internet y `python3` (solo biblioteca estándar).
- Sin API key.

## Inputs

- `--place`: colonia o punto en CDMX, o `--lat/--lon`.
- `--limit`: estaciones (por defecto 5).
- `--radius-km`: radio (por defecto 3 km).

## Workflow

```bash
npx -y @nomadamas/k-skill@0 exec ecobici-cdmx scripts/ecobici_cdmx.py -- --place "Roma Norte" --limit 5
npx -y @nomadamas/k-skill@0 exec ecobici-cdmx scripts/ecobici_cdmx.py -- --lat 19.4194 --lon -99.16 --radius-km 2
```

## Official surface

- Feed GBFS: `https://gbfs.mex.lyftbikes.com/gbfs/gbfs.json`
- Ecobici: `https://www.ecobici.cdmx.gob.mx/`

## Done when

- Se listaron las estaciones cercanas con bicis disponibles y espacios libres.
- Se indicó la distancia aproximada.

## Failure modes

- El feed GBFS está caído o responde 5xx (reintentar).
- La ubicación no se encuentra en el geocodificador (usar coordenadas).
- El radio es muy pequeño y no hay estaciones (ampliar radio).

## Notes

- Skill de solo consulta; el estado de estaciones se actualiza cada pocos segundos en el feed.
- Solo aplica a Ecobici CDMX (no a otros sistemas de bici compartida).
