# Guía de búsqueda de empleo en México (Vacantes Digitales)

## Qué puedes hacer

- Buscar vacantes de empleo en México/LATAM por puesto, skill o empresa.
- Filtrar por categoría, nivel de experiencia y modalidad.
- Obtener empresa, ubicación y enlace de cada vacante.

## Fuente de datos

- API pública de **Vacantes Digitales** (sin autenticación ni API key): https://vacantesdigitales.com/api
- Enfocada en empleos de **tecnología e IA** en LATAM (incluye México).

## Entradas

- `query` (posicional) o `--query`: puesto, skill o empresa.
- `--limit`: resultados (1–50, por defecto 5).
- `--page`: página de resultados.
- `--category`: `desarrollo`, `data`, `devops`, `diseno`, etc.
- `--experience`: `junior`, `mid`, `senior`, `lead`.
- `--location-type`: `remoto`, `hibrido`, `presencial`.
- `--json`: salida JSON.

## Ejemplos

```bash
npx -y @nomadamas/k-skill@0 exec mx-job-search scripts/mx_job_search.py -- "python"
npx -y @nomadamas/k-skill@0 exec mx-job-search scripts/mx_job_search.py -- "desarrollador" --limit 5 --json
npx -y @nomadamas/k-skill@0 exec mx-job-search scripts/mx_job_search.py -- "data" --category data --experience senior
```

## Portales oficiales alternativos

- Portal del Empleo (SNE): https://www.empleo.gob.mx/
- OCC Mundial: https://www.occ.com.mx/empleos/
- Computrabajo: https://www.computrabajo.com.mx/

## Precauciones

- La cobertura es de tecnología/LATAM; para otros sectores usa los portales oficiales.
- La postulación la realiza el usuario en el enlace original.
- Atribución: datos de Vacantes Digitales (API pública gratuita).
