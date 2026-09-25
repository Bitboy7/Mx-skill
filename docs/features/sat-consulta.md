# Guía: consultas públicas del SAT

Skill `sat-consulta`. Consulta servicios **públicos** del SAT (México) que **no
requieren e.firma**. Disponible en el bot como submenú **`/sat`**.

## Qué puedes hacer

- **Estatus de un CFDI**: saber si una factura está **Vigente** o **Cancelada**.
- **Listado 69-B (EFOS/EDOS)**: saber si un RFC aparece como Presunto, Definitivo,
  Desvirtuado o Sentencia Favorable.
- **Constancia de Situación Fiscal por QR**: leer los datos del contribuyente a
  partir del RFC y el folio (`id_cif`) impresos en el QR de la constancia.
- **Catálogos oficiales**: clave de producto/servicio, unidad, régimen fiscal,
  uso del CFDI, forma/método de pago, moneda, país y tipo de comprobante.

## Requisitos

- Python 3.10+ y la librería `satcfdi`:

```bash
pip install satcfdi
```

## Entradas

- `--action`: `factura` | `69b` | `constancia` | `catalogo`.
- `factura`: `--uuid`, `--rfc-emisor`, `--rfc-receptor`, `--total`.
- `69b`: `--rfc`.
- `constancia`: `--rfc`, `--id-cif`.
- `catalogo`: `--tipo` y (`--clave` o `--buscar`).

## Comandos del bot

| Comando | Qué hace |
| --- | --- |
| `/sat` | Muestra el submenú SAT |
| `/sat_factura <UUID> <RFC emisor> <RFC receptor> <total>` | Estatus del CFDI |
| `/sat_69b <RFC>` | Busca el RFC en el listado 69-B |
| `/sat_constancia <RFC> <id_cif>` (o URL del QR) | Constancia por QR |
| `/sat_catalogo <tipo> <clave\|texto>` | Catálogo del SAT |

## Ejemplos

```bash
npx -y @nomadamas/k-skill@0 exec sat-consulta scripts/sat_consulta.py -- \
  --action factura --uuid 11111111-1111-1111-1111-111111111111 \
  --rfc-emisor AAA010101AAA --rfc-receptor BBB010101BBB --total 1250.30

npx -y @nomadamas/k-skill@0 exec sat-consulta scripts/sat_consulta.py -- \
  --action 69b --rfc AAA010101AAA

npx -y @nomadamas/k-skill@0 exec sat-consulta scripts/sat_consulta.py -- \
  --action constancia --rfc AAA010101AAA --id-cif 012345678

npx -y @nomadamas/k-skill@0 exec sat-consulta scripts/sat_consulta.py -- \
  --action catalogo --tipo regimen --clave 601
```

## Precauciones y límites

- El `--total` de `factura` debe coincidir **exactamente** con el del CFDI; si no,
  el SAT responde "No Encontrado".
- El 69-B es informativo: confirma contra la publicación oficial del SAT antes de
  tomar decisiones.
- La lectura de la constancia por QR depende de la página HTML del validador del
  SAT; si cambia su estructura puede fallar.
- **Fuera de alcance** (requieren e.firma/CSD o credenciales de PAC): descarga
  masiva, opinión de cumplimiento 32-D, constancia con FIEL, portal de factura
  electrónica, DIOT/PLD/contabilidad y timbrado/cancelación con PAC.
- No sustituye la verificación oficial del SAT. No se piden ni almacenan
  credenciales.
