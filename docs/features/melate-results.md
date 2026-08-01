# Guía de Melate (Lotería Nacional de México)

## Qué puedes hacer

- Consultar los resultados oficiales más recientes de Melate, Revancha, Revanchita y otras bolsas (Chispazo, Tris, Progol, Mayor, etc.).
- Ver el número de sorteo, la fecha y la bolsa acumulada.
- Comparar los números del usuario contra el último sorteo de Melate.

## Primero necesitas

- Python 3 (solo biblioteca estándar, sin dependencias externas).
- Internet. No se requiere API key ni iniciar sesión.

## Entradas

- Juego opcional (`--game`) para filtrar resultados.
- Para verificar: seis números.

## Flujo básico

1. Se obtiene la página oficial de resultados.
2. Se parsean los paneles de cada juego (HTML server-rendered).
3. Se resumen el sorteo, la fecha, los números y la bolsa.
4. Si hay números del usuario, se comparan contra el último Melate.

## Ejemplos

```bash
npx -y @nomadamas/k-skill@0 exec melate-results scripts/melate_results.py -- latest
npx -y @nomadamas/k-skill@0 exec melate-results scripts/melate_results.py -- check --numbers "6 14 21 32 40 49"
```

## Fuente oficial

- Resultados: https://www.loterianacional.gob.mx/Home/Resultados
- Verificador oficial de boletos: https://www.loterianacional.gob.mx/Home/BuscadorBoleto

## Precauciones

- El premio exacto por categoría solo lo determina Lotería Nacional; el skill conecta con el verificador oficial.
- La página oficial solo publica resultados recientes, no históricos.
- El HTML puede cambiar; el parser se actualiza en `melate-results/scripts/melate_results.py`.
