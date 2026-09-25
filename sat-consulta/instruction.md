# SAT Consulta

## What this skill does

Consulta servicios **públicos** del SAT (México) que **no requieren e.firma**:

- **Estatus de un CFDI**: si una factura está Vigente o Cancelada (servicio de validación del SAT).
- **Listado 69-B** (EFOS/EDOS): si un RFC aparece como Presunto, Definitivo, Desvirtuado o Sentencia Favorable.
- **Constancia de Situación Fiscal por QR**: datos del contribuyente a partir del RFC y el folio (`id_cif`) impresos en el QR de la constancia.
- **Catálogos oficiales**: clave de producto/servicio, unidad, régimen fiscal, uso de CFDI, forma/método de pago, moneda, país y tipo de comprobante.

## When to use

- "¿Esta factura está vigente o cancelada?" / "Verifica el CFDI con UUID ...".
- "¿Este RFC está en el listado 69-B?" / "¿Es EFOS/EDOS?".
- "Lee la constancia con RFC ... y folio ...".
- "¿Qué régimen fiscal es 601?" / "¿Qué clave de producto es 84111506?".

## When not to use

- Para **descarga masiva** de CFDI, **opinión de cumplimiento (32-D)**, **constancia con FIEL**, facturación/cancelación con PAC, DIOT, PLD o contabilidad electrónica: requieren e.firma/CSD o credenciales del PAC y quedan **fuera del alcance** de esta skill.
- Para validar la **estructura** de un RFC sin red, usa `sat-rfc-lookup`.
- La homoclave del RFC no es verificable offline (algoritmo confidencial del SAT).

## Prerequisites

- Python 3.10+.
- `pip install satcfdi` (la skill usa la librería `python-satcfdi`).
- Conexión a internet. Sin login ni credenciales.

## Inputs

- `--action`: `factura` | `69b` | `constancia` | `catalogo` (obligatorio).
- `factura`: `--uuid <uuid>`, `--rfc-emisor <rfc>`, `--rfc-receptor <rfc>`, `--total <monto>`.
- `69b`: `--rfc <rfc>`.
- `constancia`: `--rfc <rfc>`, `--id-cif <folio>`.
- `catalogo`: `--tipo <tipo>` y `--clave <clave>` o `--buscar <texto>`.
  - Tipos: `producto`, `unidad`, `regimen`, `uso`, `forma-pago`, `metodo-pago`, `moneda`, `pais`, `comprobante`.

## Workflow

```bash
# Estatus de un CFDI (Vigente / Cancelado)
npx -y @nomadamas/k-skill@0 exec sat-consulta scripts/sat_consulta.py -- \
  --action factura --uuid 00000000-0000-0000-0000-000000000000 \
  --rfc-emisor AAA010101AAA --rfc-receptor BBB010101BBB --total 1250.30

# Listado 69-B
npx -y @nomadamas/k-skill@0 exec sat-consulta scripts/sat_consulta.py -- \
  --action 69b --rfc AAA010101AAA

# Constancia de situación fiscal por QR (RFC + folio id_cif)
npx -y @nomadamas/k-skill@0 exec sat-consulta scripts/sat_consulta.py -- \
  --action constancia --rfc AAA010101AAA --id-cif 012345678

# Catálogos
npx -y @nomadamas/k-skill@0 exec sat-consulta scripts/sat_consulta.py -- \
  --action catalogo --tipo regimen --clave 601
npx -y @nomadamas/k-skill@0 exec sat-consulta scripts/sat_consulta.py -- \
  --action catalogo --tipo producto --buscar software
```

Todas las acciones imprimen JSON por stdout.

## Done when

- Se consultó el servicio público correspondiente y se reportó el resultado con su significado.
- Se distingue claramente entre "no encontrado" (respuesta válida) y error de red/entrada.

## Failure modes

- `factura`: el servicio responde "No Encontrado" si el `--total` no coincide exactamente con el CFDI o los datos no corresponden.
- `69b`: si no se puede descargar el CSV del SAT, se intenta una descarga directa; si falla, se reporta el error.
- `constancia`: el validador QR es una página HTML; si cambia su estructura, el parseo puede fallar (se reporta como error).
- `catalogo`: clave inexistente se reporta como "no encontrado".
- Red/HTTP caídos se reportan como error con mensaje en español.

## Notes

- Solo servicios públicos: **nunca** se piden ni almacenan `.cer`, `.key`, contraseñas ni credenciales del PAC.
- No sustituye la verificación oficial del SAT; el estatus del CFDI y el 69-B se consultan contra los servicios públicos vigentes.
- Referencia de la librería: https://github.com/SAT-CFDI/python-satcfdi
