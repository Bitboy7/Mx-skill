# Guía de días feriados de México (Nager.Date)

## Qué puedes hacer

- Listar los días feriados oficiales de un año (por defecto el actual).
- Ver los próximos días feriados con los días que faltan.
- Conocer el tipo de cada día (oficial, bancario, escolar, conmemorativo).

## Entradas

- `--year`: año a consultar (ej. `2027`).
- `--next`: solo los próximos feriados a partir de hoy.
- `--json`: salida JSON.

## Salida

- `modo`: `year` o `next`.
- `year`: año consultado (cuando aplica).
- `today`: fecha de referencia para los días faltantes.
- `results[]`: `fecha`, `nombre`, `nombre_local`, `tipos`, `dias_faltantes`.

## Ejemplos

```bash
npx -y @nomadamas/k-skill@0 exec mx-holiday-calendar scripts/mx_holidays.py --
npx -y @nomadamas/k-skill@0 exec mx-holiday-calendar scripts/mx_holidays.py -- --year 2027 --json
npx -y @nomadamas/k-skill@0 exec mx-holiday-calendar scripts/mx_holidays.py -- --next
```

## Fuentes

- Nager.Date (pública, sin clave): https://date.nager.at/
- API de México: https://date.nager.at/api/v3/PublicHolidays/2026/MX

## Precauciones

- Refleja feriados federales; los estatales/municipales pueden variar.
- Para efectos laborales o legales, verifica con la autoridad oficial correspondiente.
