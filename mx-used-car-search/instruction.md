# MX Used Car Search

## What this skill does

Busca autos **usados/seminuevos** en anuncios públicos de México (Seminuevos.com) y
los ordena por un **índice de confianza** pensado para compra/reventa:

- Normaliza marca, modelo, año, kilometraje, transmisión, precio y ubicación.
- Prioriza anuncios de **agencia (dealer)** sobre particulares.
- Calcula confianza con antigüedad, km por año y **precio vs. la mediana** del mercado.
- Señala precios sospechosamente bajos y enlaza la verificación oficial (REPUVE/NIV).

## When to use

- "Busca autos usados confiables: Nissan Sentra".
- "Autos seminuevos en Jalisco hasta $200,000".
- "¿Qué Sentra 2019-2022 hay en Monterrey con menos de 80,000 km?".

## When not to use

- No verifica legalmente el vehículo (robo, adeudos, NIV alterado): eso es REPUVE y el
  registro estatal; la skill solo enlaza esas fuentes.
- No realiza compra, apartado, ni envío de pagos.
- No cubre autos nuevos de agencia ni motos.

## Prerequisites

- Python 3.10+ (solo biblioteca estándar). No requiere internet de pago ni API key.
- Conexión a internet.

## Inputs

- `--marca`: marca (obligatoria salvo que se use `--query`). Ej. `nissan`.
- `--modelo`: modelo. Ej. `sentra`.
- `--estado`: estado o ciudad. Ej. `jalisco`, `nuevo leon`, `monterrey`.
- `--precio-max`: precio máximo en MXN.
- `--anio-min`: año mínimo.
- `--km-max`: kilometraje máximo.
- `--vendedor`: `dealer` (default, agencias) o `todos`.
- `--limit`: número de resultados (default 12).
- `--query`: texto libre ("nissan sentra"); se interpreta como marca + modelo.

## Workflow

```bash
# Marca + modelo, solo agencias
npx -y @nomadamas/k-skill@0 exec mx-used-car-search scripts/mx_used_car_search.py -- \
  --marca nissan --modelo sentra --limit 8

# Estado + presupuesto
npx -y @nomadamas/k-skill@0 exec mx-used-car-search scripts/mx_used_car_search.py -- \
  --marca nissan --estado jalisco --precio-max 200000

# Texto libre
npx -y @nomadamas/k-skill@0 exec mx-used-car-search scripts/mx_used_car_search.py -- \
  --query "toyota corolla" --anio-min 2018
```

## Done when

- Se devolvió una lista normalizada y ordenada por confianza, con enlace al anuncio.
- Se indicó la mediana de precio del conjunto y se marcaron las anomalías.

## Failure modes

- Sin resultados para la marca/modelo/estado: se reporta explícitamente con la URL usada.
- La estructura del sitio puede cambiar: si no se parsean anuncios, se reporta como error.
- Bloqueo/anti-bot del sitio: se reporta como fallo de red, sin reintentos agresivos.
- Los precios y disponibilidad cambian; la verificación final es en el anuncio y en REPUVE.

## Notes

- Fuente: anuncios públicos de Seminuevos.com (páginas renderizadas en HTML).
- No almacena datos personales. Solo lectura.
- Enlaces oficiales: REPUVE (robo/NIV), PROFECO y AMIS (robo por modelo).
