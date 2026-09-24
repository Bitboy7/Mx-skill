# Guía de CompraNet / Compras MX (licitaciones públicas de México)

## Qué puedes hacer

- Buscar licitaciones y contrataciones públicas del gobierno mexicano por palabra clave.
- Filtrar por año, tipo de procedimiento y estatus.
- Obtener el enlace oficial (Compras MX) de cada procedimiento.

## Fuente de datos

- API pública de sólo lectura **LicitIA Abierto** (sin autenticación, CC BY 4.0): https://api.licitia.com.mx/api/open/v1
- Normaliza los datos que el gobierno publica en **Compras MX** (antes CompraNet).

## Entradas

- `query` (posicional) o `--query`: palabra clave.
- `--limit`: resultados (1–50, por defecto 5).
- `--year`, `--tipo`, `--estatus`: filtros opcionales.
- `--json`: salida JSON.

## Ejemplos

```bash
npx -y @nomadamas/k-skill@0 exec compranet-search scripts/compranet_search.py -- "software" --limit 5
npx -y @nomadamas/k-skill@0 exec compranet-search scripts/compranet_search.py -- "obra publica" --year 2026 --json
```

## Superficies oficiales

- Compras MX (difusión de procedimientos): https://comprasmx.buengobierno.gob.mx/sitiopublico/#/
- Datos Abiertos de Compras MX: https://comprasmx.buengobierno.gob.mx/datos-abiertos
- Archivo histórico CompraNet 5.0: https://historico-compranet.buengobierno.gob.mx/

## Precauciones

- No hay una API pública oficial estable para todo el catálogo; si la API de LicitIA no responde, el helper muestra los enlaces oficiales.
- Los datos normalizados pueden tener desfase respecto a Compras MX; el enlace oficial es la fuente primaria.
- La participación en licitaciones es un trámite oficial que el usuario completa manualmente.
- Atribución obligatoria: LicitIA Abierto (CC BY 4.0) sobre datos de Compras MX.
