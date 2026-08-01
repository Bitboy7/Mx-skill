# Guía de clima en México (Open-Meteo)

## Qué puedes hacer

- Clima actual (temperatura, humedad, viento, descripción) de una ciudad de México.
- Pronóstico diario (máx/mín, probabilidad de lluvia) de 1 a 7 días.

## Entradas

- `--place`: ciudad (ej. "Guadalajara").
- `--days`: días de pronóstico (1–7).

## Ejemplos

```bash
npx -y @nomadamas/k-skill@0 exec mx-weather scripts/mx_weather.py -- --place "Guadalajara" --days 3
```

## Fuentes

- Open-Meteo (pública, sin clave): https://open-meteo.com/
- Referencia oficial de México: SMN/CONAGUA https://smn.conagua.gob.mx/

## Precauciones

- Para alertas meteorológicas oficiales usar el SMN.
- El geocodificador puede no reconocer puntos de referencia muy específicos.
