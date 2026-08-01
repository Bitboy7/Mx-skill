# Cine MX

## What this skill does

Consulta la **cartelera de cine en México**:
- **Cinemex**: API pública verificada (`api.cinemex.com`) — cartelera, películas y funciones por cine.
- **Cinepolis**: sin API pública estable; se remite al portal oficial `cinepolis.com/cartelera`.

## When to use

- "¿Qué películas están en cartelera?"
- "Funciones de Minions en un cine de mi zona"
- "Cartelera de Cinemex hoy"

## When not to use

- Para comprar boletos: la compra se hace en el sitio oficial (el skill es de solo consulta).

## Prerequisites

- Internet y `python3` (solo biblioteca estándar).
- Sin API key (el header `X-API-Consumer-Key` de Cinemex es público del frontend).

## Inputs

- `movies` (cartelera), `movies --area <id>` (por zona), `functions --cinema <id> --movie <id>`, `areas`.

## Workflow

```bash
npx -y @nomadamas/k-skill@0 exec cine-mx scripts/cine_mx.py -- movies
npx -y @nomadamas/k-skill@0 exec cine-mx scripts/cine_mx.py -- functions --cinema 1 --movie 71994
```

## Official surfaces

- Cinemex API: `https://api.cinemex.com/rest/v2.37.2`
- Cinepolis cartelera: `https://www.cinepolis.com/cartelera`
- Cinemex web: `https://www.cinemex.com/`

## Done when

- Se listó la cartelera o las funciones con horario, pantalla y enlace.
- Se indicó que Cinepolis se consulta por su portal oficial.

## Failure modes

- La API de Cinemex cambia de versión (`v2.37.2`) o responde 5xx: actualizar la ruta en `cine_mx.py`.
- Cinepolis no expone API pública estable: no se automatiza, se da el portal.

## Notes

- Skill de solo consulta; no compra boletos.
- Los horarios varían; verificar en el sitio antes de ir.
