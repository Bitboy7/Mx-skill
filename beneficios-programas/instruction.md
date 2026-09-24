# Beneficios y Programas para el Bienestar

## What this skill does

Brinda **información oficial de los Programas para el Bienestar** del Gobierno de México: pensión para adultos mayores, pensión para personas con discapacidad, becas Benito Juárez, Jóvenes Construyendo el Futuro, Sembrando Vida, entre otros. El helper mantiene un catálogo curado (perfil, requisitos, tipo de apoyo y enlace oficial) para responder rápido, y el portal oficial es la fuente de verdad.

## When to use

- "¿Cuánto da la pensión del bienestar para adultos mayores?"
- "¿Cómo me registro a Jóvenes Construyendo el Futuro?"
- "Requisitos de la beca Benito Juárez"

## When not to use

- Para registrar a una persona o revisar un caso: la inscripción/baja se hace por los canales oficiales (el usuario lo completa manualmente).
- Para datos personales de beneficiarios: no existen ni deben consultarse.

## Prerequisites

- Internet y `python3` (solo biblioteca estándar).
- No requiere API key.

## Inputs

- `query` (posicional): palabra clave (pensión, beca, jóvenes, campo...).
- `--categoria`: filtrar por categoría (`adultos mayores`, `mujeres`, `infancias`, `jóvenes`, `personas con discapacidad`, `campo y pesca`, `vivienda`).
- `--list`: listar todos los programas.
- `--json`: salida JSON.

## Workflow

```bash
npx -y @nomadamas/k-skill@0 exec beneficios-programas scripts/beneficios_programas.py -- "pensión"
npx -y @nomadamas/k-skill@0 exec beneficios-programas scripts/beneficios_programas.py -- "beca" --categoria jóvenes --json
npx -y @nomadamas/k-skill@0 exec beneficios-programas scripts/beneficios_programas.py -- --list
```

## Output

- `source` / `portal`: portal oficial `programasparaelbienestar.gob.mx`.
- `results[]`: `nombre`, `categoria`, `perfil`, `requisitos`, `apoyo`, `monto`, `convocatoria`, `enlace`.
- `note`: recordatorio de que montos y requisitos cambian con las reglas de operación vigentes.

## Done when

- Se explicó el programa correcto para el perfil del usuario.
- Se dieron requisitos, tipo de apoyo y el canal oficial (enlace).
- Se dejó claro que el trámite lo realiza el usuario en la vía oficial.

## Failure modes

- Sin coincidencias para la palabra clave: probar otro término o `--list`.
- El catálogo puede no incluir un programa nuevo o local (estatal/municipal): remitir al portal oficial.
- Los montos son referenciales y cambian con las reglas de operación vigentes.

## Notes

- Skill informativo/de consulta. No solicita ni tramita apoyos ni guarda datos personales.
- El registro es gratuito y sin intermediarios; el portal oficial es la fuente de verdad.
