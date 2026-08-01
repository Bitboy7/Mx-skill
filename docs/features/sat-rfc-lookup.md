# Guía de validación de RFC (SAT)

## Qué puedes hacer

- Determinar si un RFC es de persona física o moral.
- Validar la estructura y la fecha AAMMDD (día real).
- Desglosar los componentes del RFC.

## Entradas

- `--rfc`: el RFC (13 caracteres).

## Ejemplos

```bash
npx -y @nomadamas/k-skill@0 exec sat-rfc-lookup scripts/sat_rfc_lookup.py -- --rfc GODE561231GR8
```

## Precauciones

- La homoclave la asigna el SAT con un algoritmo confidencial; **no** es verificable offline.
- La constancia de situación fiscal requiere el portal SAT con e.firma (trámite manual del usuario).
- No sustituye la verificación oficial del SAT.
