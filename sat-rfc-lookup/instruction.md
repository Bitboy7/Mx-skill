# SAT RFC Lookup

## What this skill does

Analiza y valida la **estructura del RFC (Registro Federal de Contribuyentes)** de México de forma **local y determinista** (sin red): persona física o moral, fecha AAMMDD real, y desglose de los componentes. Ayuda a detectar errores de captura.

## When to use

- "Valida este RFC: GODE561231GR8"
- "¿Este RFC es de persona física o moral?"
- "¿La fecha de este RFC es válida?"

## When not to use

- Para obtener la **Constancia de Situación Fiscal** o verificar la vigencia: eso requiere el portal del SAT con e.firma (el usuario lo hace manualmente; el skill no puede ni debe hacerlo).
- Para verificar la homoclave: el SAT la asigna con un algoritmo confidencial (Regla 8) que no es verificable offline.

## Prerequisites

- `python3` (solo biblioteca estándar). No requiere internet.

## Inputs

- `--rfc`: el RFC a validar (13 caracteres).

## Workflow

```bash
npx -y @nomadamas/k-skill@0 exec sat-rfc-lookup scripts/sat_rfc_lookup.py -- --rfc GODE561231GR8
```

## Done when

- Se determinó si la estructura es de persona física o moral.
- Se validó la fecha AAMMDD (día real).
- Se explicó claramente qué se puede y qué no se puede verificar offline.

## Failure modes

- Formato inválido (longitud, caracteres): se reporta con la estructura esperada.
- Fecha imposible (p. ej. 15/13/2020): se reporta como inválida.

## Notes

- No almacena ningún RFC.
- No sustituye la verificación oficial del SAT (constancia con e.firma).
