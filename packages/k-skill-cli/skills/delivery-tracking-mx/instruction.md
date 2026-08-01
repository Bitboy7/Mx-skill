# Delivery Tracking MX

## What this skill does

Consulta el **seguimiento de paquetes en México**:
- **Estafeta**: endpoint público verificado (`cs.estafeta.com`, guías de 22 dígitos) — ruta primaria.
- **Correos de México** y **99 Minutos**: detrás de challenges anti-bot JS / API con OAuth; se documentan como límites y se remite a sus portales.

## When to use

- "¿Dónde está mi paquete de Estafeta?"
- "Rastrea la guía 0000000000000000000000"
- "¿Ya llegó mi envío?"

## When not to use

- Solo con número de pedido (sin guía): no se puede rastrear.
- Para Correos de México / 99 Minutos por HTTP directo: usar sus portales oficiales.

## Prerequisites

- Internet y `python3` (solo biblioteca estándar).
- Sin API key.

## Inputs

- `--carrier estafeta` (por ahora solo Estafeta).
- `--guia`: 22 dígitos.

## Workflow

```bash
npx -y @nomadamas/k-skill@0 exec delivery-tracking-mx scripts/delivery_tracking_mx.py -- --carrier estafeta --guia 0000000000000000000000
```

## Official surfaces

- Estafeta tracking: `https://cs.estafeta.com/es/Tracking/searchByGet?wayBill=<guia>&wayBillType=0`
- Correos de México: `https://www.gob.mx/correosdemexico` (seguimiento de envíos)
- 99 Minutos: `https://tracking.99minutos.com/`

## Done when

- Se reportó el estado y los eventos recientes del envío (Estafeta).
- Si no hay información para la guía, se indica claramente.

## Failure modes

- Guía inválida (no 22 dígitos) o sin información en Estafeta.
- El marcado HTML de Estafeta cambia: se actualiza el parser en `delivery_tracking_mx.py`.
- Correos de México / 99 Minutos no son accesibles por HTTP directo (anti-bot/JS); se remite a sus portales.

## Notes

- Skill de solo consulta.
- Diseño tipo "carrier adapter" para añadir más mensajerías mexicanas en el futuro.
