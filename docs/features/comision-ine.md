# Guía de candidatas y candidatos del INE

## Qué puedes hacer

- Buscar candidatas/candidatos del INE por nombre y tipo de candidatura.
- Ver partido, sexo, edad y propuestas.

## Entradas

- `--name`: fragmento del nombre.
- `--tipo`: `presidente`, `senadores`, `senadores_mr`, `diputados`, `diputados_mr`.
- `--all`: listar todo el tipo.

## Ejemplos

```bash
npx -y @nomadamas/k-skill@0 exec comision-ine scripts/comision_ine.py -- --all --tipo presidente
npx -y @nomadamas/k-skill@0 exec comision-ine scripts/comision_ine.py -- --name "Claudia"
```

## Fuente

- Datos públicos INE: https://candidaturas.ine.mx/cycc/documentos/json/

## Precauciones

- Los archivos se publican por proceso electoral; algunos tipos pueden no existir fuera del año electoral.
- Para resultados de elecciones usar el PREP/resultados oficiales del INE.
