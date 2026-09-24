# Flujo del fork MX (Bitboy7/Mx-skill)

Este repositorio es un **fork de producto**: adaptamos las skills coreanas de
[`NomaDamas/k-skill`](https://github.com/NomaDamas/k-skill) al público mexicano.
La rama `main` de este fork es **nuestro producto (MX)** y puede divergir de
upstream libremente.

## Modelo de ramas y remotos

| Rol | Remoto / rama | Uso |
| --- | --- | --- |
| Producto | `origin` = `Bitboy7/Mx-skill`, rama `main` | Aquí vive el contenido MX |
| Inspiración | `upstream` = `NomaDamas/k-skill`, rama `main` | Solo `fetch` + copiar/cherry-pick |
| Referencia | `upstream-main` (local) | Espejo de `upstream/main` |

- `upstream` está configurado **fetch-only** (`push` = `DISABLED`).
- La `main` del fork se fijó a la antigua rama `MX` (`a019aac`) mediante
  `git push --force-with-lease origin main`.
- Respaldos: rama `backup/MX` y tag `backup-mx-20260923`.

## Traer mejoras desde upstream (copia selectiva)

No hagas `git merge upstream/main` completo (trae cientos de commits y
conflictos). Copia solo lo que necesites:

```bash
git fetch upstream
git log --oneline upstream/main            # ver novedades
git checkout upstream/main -- <skill-dir>  # traer una skill concreta al árbol
# o, para un cambio puntual:
git cherry-pick <sha>
```

### Checklist al adaptar una skill coreana a MX

1. Renombrar el directorio a `mx-<nombre>` (o un nombre MX claro).
2. Cambiar las fuentes de datos a servicios públicos de México (sin API key si
   es posible) y documentar la referencia oficial.
3. Añadir `scripts/<helper>.py` (solo stdlib) y `tests/test_*.py`.
4. `skill.json` con `metadata.locale: es-MX`; `instruction.md` en español.
5. Regenerar y sincronizar:
   ```bash
   npm run generate:skill-stubs
   npm run migrate:cli-assets
   npm run sync:cli-skills
   ```
6. Registrar la skill en el bot (`tools/mx-telegram-bot/bot/runner.py` y un
   handler en `bot/skills/`).
7. Verificar: tests del helper + `python tools/mx-telegram-bot/run.py --smoke`.

## Convenciones del repo

- Trabaja con ramas `feat/mx-...` → PR a `main`.
- Nunca hagas `push` a `upstream`.
- No commitees secretos: `.env` está en `.gitignore`.
- Si algún día quieres contribuir a NomaDanas, hazlo desde una rama basada en
  `upstream/main`, no desde tu `main` divergente.
- Las skills coreanas se conservan por ahora como referencia; se pueden podar
  más adelante (mover a `korean-reference/` o eliminar y ajustar tests).

## Workflows de GitHub

Están **desactivados manualmente** en el fork para evitar releases/publishes
accidentales y CI en rojo mientras se estabiliza:

- `CI`
- `Publish Manus bundle`
- `Release npm packages`
- `Release Python packages`

Reactivar cuando corresponda:

```bash
gh workflow enable "CI" --repo Bitboy7/Mx-skill
# etc.
```

## Respaldos y recuperación

```bash
git checkout backup/MX          # rama de respaldo
git tag -l 'backup-*'           # tags de respaldo
```

Para deshacer la conversión (volver `main` al espejo de upstream):

```bash
git checkout main
git reset --hard upstream-main
git push --force-with-lease origin main
```
