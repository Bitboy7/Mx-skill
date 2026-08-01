# CompraNet Search

## What this skill does

Ayuda a buscar **licitaciones y contrataciones públicas de México** en las plataformas oficiales: **CompraNet** y **Contrataciones Abiertas** de la Secretaría de la Función Pública (UPCP). Es una skill de navegación de superficies oficiales: no existe una API pública estable y abierta para todo el catálogo, y los portales aplican controles anti-bot.

## When to use

- "¿Qué licitaciones abiertas hay para software en CDMX?"
- "Busca concursos de obra pública del gobierno federal"
- "¿Cómo busco una contratación específica en CompraNet?"

## When not to use

- Para participar en una licitación (requiere alta en CompraNet y, en su caso, e.firma): el usuario completa ese trámite manualmente.
- Para datos históricos masivos: usar los datasets abiertos de Contrataciones Abiertas (`contratacionesabiertas.hacienda.gob.mx`).

## Prerequisites

- Internet y un navegador para los pasos que exigen interacción manual.
- No requiere API key.

## Workflow

1. Consultar el buscador público de **CompraNet**:
   - `https://compranet.hacienda.gob.mx/` → módulo de búsqueda de procedimientos.
2. Consultar **Contrataciones Abiertas** (datos abiertos y buscador):
   - `https://contratacionesabiertas.hacienda.gob.mx/`
3. Aplicar filtros: palabra clave, entidad federativa, tipo de procedimiento (licitación pública, invitación restringida, adjudicación directa), fecha.
4. Resumir las contrataciones encontradas: número de expediente, objeto, dependencia, monto, estado.

## Done when

- Se identificaron las contrataciones relevantes con su expediente y enlace oficial.
- Se explicó que la participación requiere el trámite oficial en CompraNet.

## Failure modes

- Los portales pueden estar fuera de servicio o bloquear peticiones automatizadas (challenges anti-bot): en ese caso se da el enlace oficial y el usuario completa la búsqueda manualmente.
- Sin resultados para los filtros elegidos.
- Los datos de Contrataciones Abiertas pueden tener desfase respecto a CompraNet.

## Notes

- Skill de solo consulta/guía. No inscribe ni presenta ofertas.
- No se recopilan datos de empresas ni se guardan búsquedas.
