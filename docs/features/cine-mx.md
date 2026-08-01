# Guía de cartelera de cine en México

## Qué puedes hacer

- Cartelera actual de **Cinemex** (API pública verificada).
- Funciones por cine/película en Cinemex.
- Cartelera de **Cinepolis** vía su portal oficial (sin API pública estable).

## Entradas

- `movies`, `movies --area <id>`, `functions --cinema <id> --movie <id>`, `areas`.

## Ejemplos

```bash
npx -y @nomadamas/k-skill@0 exec cine-mx scripts/cine_mx.py -- movies
npx -y @nomadamas/k-skill@0 exec cine-mx scripts/cine_mx.py -- functions --cinema 1 --movie 71994
```

## Superficies

- Cinemex API: https://api.cinemex.com/rest/v2.37.2
- Cinepolis cartelera: https://www.cinepolis.com/cartelera

## Precauciones

- La API de Cinemex puede cambiar de versión.
- La compra de boletos se hace en el sitio oficial.
