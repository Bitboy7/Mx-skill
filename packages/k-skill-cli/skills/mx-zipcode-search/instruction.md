# MX Zipcode Search

## What this skill does

Consulta el **código postal de México (SEPOMEX)** y devuelve las colonias asociadas, municipio y estado, usando la fuente pública `api.zippopotam.us/mx` (sin API key). El catálogo oficial de referencia es el de Correos de México (SEPOMEX).

## When to use

- "¿A qué colonia pertenece el CP 06600?"
- "¿Qué estado y municipio es el 64000?"
- "¿Es válido el CP 01000?"
- "Necesito el código postal de una dirección en CDMX para un envío"

## When not to use

- Para buscar el CP a partir de una dirección/colonia (la fuente pública actual solo resuelve CP → colonias; el flujo inverso requiere el catálogo SEPOMEX completo o el servicio oficial de Correos de México).
- Para envíos de paquetería que exijan validar la dirección completa.

## Prerequisites

- Internet y `python3` (solo biblioteca estándar).
- Sin API key.

## Inputs

- Código postal de 5 dígitos (ej. `06600`).

## Workflow

### 1. Lookup a CP

```bash
npx -y @nomadamas/k-skill@0 exec mx-zipcode-search scripts/mx_zipcode_search.py -- 06600
```

Ejemplo de salida:

```json
{
  "cp": "06600",
  "pais": "Mexico",
  "colonia_principal": "Juarez",
  "estado": "Distrito Federal",
  "places": [
    {"colonia": "Juarez", "municipio": null, "estado": "Distrito Federal", "latitud": "19.385", "longitud": "-99.165"}
  ]
}
```

### 2. Validate a CP

Si el CP no existe, la fuente responde 404 y el script lo reporta (`No se encontro el codigo postal`). Se recomienda no inventar CPs: usar el resultado real de la consulta.

### 3. Reverse lookup (CP from an address)

No está disponible en la fuente pública. Para direcciones se remite al servicio oficial de Correos de México:
`https://www.correosdemexico.gob.mx/SSLServicios/ConsultaCP/ConsultaCP.aspx`
Nota: ese portal puede bloquear la automatización (respuestas vacías o HTTP 500); en ese caso se completa el paso manual del usuario enlazando la página oficial.

## Official surface

- Fuente pública usada: `https://api.zippopotam.us/mx/<cp>`
- Referencia oficial SEPOMEX: `https://www.correosdemexico.gob.mx/SSLServicios/ConsultaCP/ConsultaCP.aspx`
- Catálogo nacional de códigos postales (datos abiertos): `https://datos.gob.mx/busca/dataset/catalogo-nacional-de-codigos-postales`

## Done when

- Se consultó el CP y se listaron las colonias, municipio y estado.
- Si el CP no existe, se reportó claramente y no se inventó información.
- Se indicó que la búsqueda inversa (dirección → CP) requiere el servicio oficial.

## Failure modes

- La fuente pública devuelve 404 para CPs fuera de su cobertura (aunque existan en SEPOMEX). No afirmar que el CP "no existe"; decir que no está en la cobertura de la fuente pública y remitir al catálogo SEPOMEX.
- El servicio oficial de Correos de México bloquea o falla la automatización (vacío/HTTP 500).
- CP con formato incorrecto (no son 5 dígitos).

## Notes

- Skill de solo consulta; no valida direcciones para envíos.
- No se almacenan búsquedas del usuario.
