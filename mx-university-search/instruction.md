# MX University Search

## What this skill does

Busca **universidades de México y sus carreras**. Mantiene un catálogo curado de las principales instituciones públicas y privadas con carreras representativas y el enlace oficial de cada una. Como no existe una API pública estable de toda la oferta educativa, el catálogo es de referencia y el enlace oficial es la fuente de verdad.

## When to use

- "¿Qué universidades tienen Medicina en Jalisco?"
- "Carreras de la UNAM"
- "Universidades privadas de ingeniería en Puebla"

## When not to use

- Para inscribirse o consultar fechas de admisión: el trámite lo hace el usuario en el sitio oficial.
- Para oferta educativa completa y vigente: consultar la página oficial de cada institución (y la DGESUI/SEP).

## Prerequisites

- Internet y `python3` (solo biblioteca estándar).
- Sin API key.

## Inputs

- `query` (posicional) o `--query`: universidad o carrera (ej. `UNAM`, `medicina`, `ingeniería`).
- `--tipo`: `pública` o `privada`.
- `--estado`: estado (ej. `Jalisco`).
- `--list`: listar todas las universidades del catálogo.
- `--json`: salida JSON.

## Workflow

```bash
npx -y @nomadamas/k-skill@0 exec mx-university-search scripts/mx_university_search.py -- "medicina"
npx -y @nomadamas/k-skill@0 exec mx-university-search scripts/mx_university_search.py -- "ingeniería" --tipo pública --estado Jalisco
npx -y @nomadamas/k-skill@0 exec mx-university-search scripts/mx_university_search.py -- --list --json
```

## Output

- `source`: catálogo curado con enlaces oficiales.
- `results[]`: `nombre`, `tipo`, `estado`, `ciudad`, `sitio`, `carreras`.
- `note`: recordatorio de que el catálogo es de referencia y no exhaustivo.

## Done when

- Se listaron universidades relevantes con su tipo, ubicación y carreras.
- Se dio el enlace oficial para consultar la oferta educativa completa.

## Failure modes

- Sin coincidencias para la carrera/universidad: probar otro término o `--list`.
- El catálogo puede no incluir instituciones nuevas o de nicho: remitir a la página oficial.
- Las carreras son representativas; la oferta vigente puede variar por plantel.

## Notes

- Skill informativo/de consulta. No inscribe ni gestiona trámites.
- Fuentes de referencia oficial: SEP / DGESUI (educación superior) y los sitios de cada institución.
