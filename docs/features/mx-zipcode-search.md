# Guía de código postal de México (SEPOMEX)

## Qué puedes hacer

- Consultar el código postal de México y las colonias, municipio y estado asociados.
- Validar si un CP existe en la fuente pública.

## Primero necesitas

- Python 3 (solo biblioteca estándar).
- Internet. Sin API key.

## Entradas

- Código postal de 5 dígitos (ej. `06600`).

## Flujo básico

1. Se consulta la fuente pública `api.zippopotam.us/mx/<cp>`.
2. Se listan las colonias, municipio y estado.
3. Si el CP no está en cobertura (404), se reporta y se remite al catálogo SEPOMEX oficial.

## Ejemplos

```bash
npx -y @nomadamas/k-skill@0 exec mx-zipcode-search scripts/mx_zipcode_search.py -- 06600
```

## Fuentes

- Fuente pública: https://api.zippopotam.us/mx/<cp>
- Referencia oficial SEPOMEX (Correos de México): https://www.correosdemexico.gob.mx/SSLServicios/ConsultaCP/ConsultaCP.aspx
- Catálogo nacional de códigos postales: https://datos.gob.mx/busca/dataset/catalogo-nacional-de-codigos-postales

## Precauciones

- La búsqueda inversa (dirección → CP) no está disponible en la fuente pública; requiere el catálogo SEPOMEX completo o el servicio oficial.
- Un CP fuera de la cobertura de la fuente pública no significa que "no exista": remitir al catálogo SEPOMEX.
- El servicio oficial de Correos de México puede bloquear la automatización (respuestas vacías o HTTP 500).
