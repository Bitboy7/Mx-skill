# Guía de universidades y carreras de México

## Qué puedes hacer

- Buscar universidades de México por nombre, carrera o estado.
- Ver tipo (pública/privada), ubicación, carreras representativas y sitio oficial.
- Filtrar por tipo de institución o por estado.

## Fuente de datos

- **Catálogo curado** de las principales instituciones de educación superior de México, con enlaces oficiales.
- Referencias oficiales: SEP / DGESUI (educación superior) y los sitios de cada institución.

## Entradas

- `query` (posicional) o `--query`: universidad o carrera (ej. `UNAM`, `medicina`).
- `--tipo`: `pública` o `privada`.
- `--estado`: estado (ej. `Jalisco`).
- `--list`: listar todas las universidades del catálogo.
- `--json`: salida JSON.

## Ejemplos

```bash
npx -y @nomadamas/k-skill@0 exec mx-university-search scripts/mx_university_search.py -- "medicina"
npx -y @nomadamas/k-skill@0 exec mx-university-search scripts/mx_university_search.py -- "ingeniería" --tipo pública --estado Jalisco
npx -y @nomadamas/k-skill@0 exec mx-university-search scripts/mx_university_search.py -- --list --json
```

## Salida

- `results[]`: `nombre`, `tipo`, `estado`, `ciudad`, `sitio`, `carreras`.

## Precauciones

- El catálogo es de referencia y **no es exhaustivo**; cada institución puede ofrecer más carreras.
- Consulta siempre el enlace oficial para la oferta educativa vigente y fechas de admisión.
- No existe una API pública estable de toda la oferta educativa; el enlace oficial es la fuente de verdad.
