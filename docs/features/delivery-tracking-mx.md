# Guía de seguimiento de paquetes en México

## Qué puedes hacer

- Rastrear guías de **Estafeta** (22 dígitos) vía endpoint público.
- Documenta los límites de Correos de México y 99 Minutos (anti-bot/OAuth).

## Entradas

- `--carrier estafeta` y `--guia`.

## Ejemplos

```bash
npx -y @nomadamas/k-skill@0 exec delivery-tracking-mx scripts/delivery_tracking_mx.py -- --carrier estafeta --guia 0000000000000000000000
```

## Superficies

- Estafeta: https://cs.estafeta.com/es/Tracking/searchByGet?wayBill=<guia>&wayBillType=0
- Correos de México: https://www.gob.mx/correosdemexico
- 99 Minutos: https://tracking.99minutos.com/

## Precauciones

- Correos de México y 99 Minutos no son accesibles por HTTP directo; usar sus portales.
- Solo consulta.
