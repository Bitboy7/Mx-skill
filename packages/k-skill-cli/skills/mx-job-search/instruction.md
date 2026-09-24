# MX Job Search

## What this skill does

Busca **vacantes de empleo en México y LATAM** con la API pública de **Vacantes Digitales** (`vacantesdigitales.com/api`), sin autenticación ni API key. Está enfocada en puestos de **tecnología e IA** (desarrollo, data, DevOps, diseño, marketing, etc.) y cubre México dentro de LATAM.

## When to use

- "Busca vacantes de desarrollador en México"
- "¿Hay empleos de Python remotos?"
- "Vacantes de data science senior"

## When not to use

- Para puestos fuera de tecnología (usa el Portal del Empleo, OCC o Computrabajo; la skill enlaza a ellos).
- Para postularse: la postulación la hace el usuario en el enlace original.

## Prerequisites

- Internet y `python3` (solo biblioteca estándar).
- Sin API key.

## Inputs

- `query` (posicional) o `--query`: puesto, skill o empresa.
- `--limit`: resultados (1–50, por defecto 5).
- `--page`: página de resultados.
- `--category`: categoría (ej. `desarrollo`, `data`, `devops`).
- `--experience`: nivel (`junior`, `mid`, `senior`, `lead`).
- `--location-type`: modalidad (`remoto`, `hibrido`, `presencial`).
- `--json`: salida JSON.

## Workflow

```bash
npx -y @nomadamas/k-skill@0 exec mx-job-search scripts/mx_job_search.py -- "python"
npx -y @nomadamas/k-skill@0 exec mx-job-search scripts/mx_job_search.py -- "desarrollador" --limit 5 --json
npx -y @nomadamas/k-skill@0 exec mx-job-search scripts/mx_job_search.py -- "data" --category data --experience senior
```

La API consultada es `GET https://vacantesdigitales.com/api/vacancies?q=<query>&limit=<n>` (filtros opcionales `category`, `experience`, `location_type`, `page`).

## Output

- `source`: atribución (Vacantes Digitales, API pública).
- `results[]`: `puesto`, `empresa`, `categoria`, `experiencia`, `modalidad`, `tipo_empleo`, `ubicacion`, `salario`, `publicado`, `habilidades`, `url`.
- `official_links`: Vacantes Digitales, Portal del Empleo, OCC y Computrabajo.
- `notice`: aparece si la API pública falló (se muestran solo los enlaces).

## Done when

- Se listaron vacantes relevantes con empresa, modalidad y enlace.
- Se indicó la fuente y los portales oficiales alternativos.

## Failure modes

- API pública caída o con timeout: el helper degrada a los enlaces oficiales (`notice`).
- Sin resultados para la palabra clave (probar sinónimos o en inglés).
- La cobertura es tecnológica/LATAM; para otros sectores usar los portales oficiales.

## Notes

- Skill de solo consulta. No aplica a las vacantes ni contacta a las empresas.
- Atribución: datos de Vacantes Digitales (API pública gratuita, sin API key).
