# MX Holiday Calendar

## What this skill does

Consulta los **días feriados oficiales de México** (del año actual, de un año específico o los próximos) con la API pública **Nager.Date** (`date.nager.at`), sin API key. Incluye el tipo de cada día (oficial, bancario, escolar, conmemorativo) y cuántos días faltan.

## When to use

- "¿Cuándo es el próximo día feriado en México?"
- "Días festivos de 2027"
- "¿El 16 de noviembre es puente?"

## When not to use

- Para puentes y descansos escolares específicos de una escuela o empresa (cada calendario es distinto).
- Para trámites que dependen de días hábiles oficiales: confirma con la autoridad correspondiente.

## Prerequisites

- Internet y `python3` (solo biblioteca estándar).
- Sin API key.

## Inputs

- `--year`: año a consultar (por defecto el actual).
- `--next`: solo los próximos días feriados a partir de hoy.
- `--json`: salida JSON (por defecto es un resumen en español).

## Workflow

```bash
npx -y @nomadamas/k-skill@0 exec mx-holiday-calendar scripts/mx_holidays.py --
npx -y @nomadamas/k-skill@0 exec mx-holiday-calendar scripts/mx_holidays.py -- --year 2027
npx -y @nomadamas/k-skill@0 exec mx-holiday-calendar scripts/mx_holidays.py -- --next --json
```

## Output

- `modo`: `year` o `next`.
- `year`: año consultado (cuando aplica).
- `today`: fecha de referencia usada para calcular los días faltantes.
- `results[]`: `fecha`, `nombre`, `nombre_local`, `tipos` y `dias_faltantes`.

## Done when

- Se listaron los días feriados con fecha y nombre.
- Cuando aplica, se indicó cuántos días faltan para cada feriado.

## Failure modes

- Nager.Date está caído o con 5xx (reintentar más tarde).
- Año fuera del rango soportado por el upstream (usar el año actual o próximos).
- El calendario refleja los feriados federales; los estatales/municipales pueden variar.

## Notes

- Skill de solo consulta. Los feriados federales de México coinciden con la Ley Federal del Trabajo; Nager.Date los publica y actualiza de forma agregada.
- Para efectos legales o laborales, verifica con la autoridad oficial correspondiente.
