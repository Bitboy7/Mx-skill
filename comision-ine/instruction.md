# Comisión INE (Candidatas y Candidatos)

## What this skill does

Busca **candidatas y candidatos del INE** (México) por nombre y tipo de candidatura, usando los **datos públicos** de la plataforma "Candidatas y Candidatos, Conóceles" (`candidaturas.ine.mx`). Devuelve nombre, partido, sexo, edad y propuestas.

## When to use

- "¿Quiénes son las candidatas a la presidencia?"
- "Busca a la candidata Xochitl por nombre"
- "Candidatos a diputados en mi distrito"

## When not to use

- Para resultados de elecciones (cómputos): usar el PREP / resultados oficiales del INE.
- Para candidaturas de elecciones locales recientes si no hay archivo publicado (el INE publica archivos por proceso electoral).

## Prerequisites

- Internet y `python3` (solo biblioteca estándar).
- Sin API key.

## Inputs

- `--name`: fragmento del nombre.
- `--tipo`: `presidente`, `senadores`, `senadores_mr`, `diputados`, `diputados_mr` (opcional; por defecto todos).
- `--all`: listar todo el tipo (sin filtro de nombre).

## Workflow

```bash
npx -y @nomadamas/k-skill@0 exec comision-ine scripts/comision_ine.py -- --all --tipo presidente
npx -y @nomadamas/k-skill@0 exec comision-ine scripts/comision_ine.py -- --name "Claudia"
```

## Official surface

- Datos públicos: `https://candidaturas.ine.mx/cycc/documentos/json/*.json`
- Plataforma: `https://candidaturas.ine.mx/`

## Done when

- Se listaron las candidatas/candidatos que coinciden con el filtro.
- Se resumieron partido, tipo y propuestas principales.

## Failure modes

- Un archivo JSON de elección local puede no existir fuera del año electoral (404): se explica y se sugiere otro tipo de candidatura.
- El INE actualiza los datos por proceso electoral; los nombres/partidos reflejan la publicación vigente.

## Notes

- Skill de solo consulta. Los datos son públicos del INE.
- No se guardan búsquedas.
