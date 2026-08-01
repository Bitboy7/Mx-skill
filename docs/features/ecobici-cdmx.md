# Guía de Ecobici CDMX

## Qué puedes hacer

- Estaciones de Ecobici con bicicletas disponibles cerca de una ubicación.
- Espacios libres, capacidad y distancia.

## Entradas

- `--place` o `--lat/--lon`, `--limit`, `--radius-km`.

## Ejemplos

```bash
npx -y @nomadamas/k-skill@0 exec ecobici-cdmx scripts/ecobici_cdmx.py -- --place "Roma Norte" --limit 5
```

## Fuente

- Feed GBFS oficial: https://gbfs.mex.lyftbikes.com/gbfs/gbfs.json

## Precauciones

- Solo aplica a Ecobici CDMX.
- La renta se hace en la app/sitio oficial.
- El estado de estaciones se actualiza cada pocos segundos.
