# Guía de Programas para el Bienestar

## Qué puedes hacer

- Consultar información de los programas sociales federales: pensiones, becas, Jóvenes Construyendo el Futuro, Sembrando Vida, etc.
- Ver perfil, requisitos, tipo de apoyo y enlace oficial de cada programa.
- Filtrar por palabra clave o por categoría.

## Portal oficial

- https://www.programasparaelbienestar.gob.mx/

## Entradas

- `query` (posicional): palabra clave (pensión, beca, jóvenes, campo...).
- `--categoria`: `adultos mayores`, `mujeres`, `infancias`, `jóvenes`, `personas con discapacidad`, `campo y pesca`, `vivienda`.
- `--list`: listar todos los programas.
- `--json`: salida JSON.

## Ejemplos

```bash
npx -y @nomadamas/k-skill@0 exec beneficios-programas scripts/beneficios_programas.py -- "pensión"
npx -y @nomadamas/k-skill@0 exec beneficios-programas scripts/beneficios_programas.py -- "beca" --categoria jóvenes --json
npx -y @nomadamas/k-skill@0 exec beneficios-programas scripts/beneficios_programas.py -- --list
```

## Precauciones

- La inscripción/baja es un trámite oficial que el usuario completa manualmente.
- Montos y requisitos cambian con las reglas de operación vigentes: el enlace oficial es la fuente de verdad.
- El catálogo es federal; puede no incluir programas estatales o municipales.
- No se tramitan apoyos ni se piden datos personales.
