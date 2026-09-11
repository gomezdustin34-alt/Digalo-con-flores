# Despliegue en Vercel — Dígalo con Flores

El proyecto ya está preparado para Vercel. Esta guía tiene los pasos exactos.

---

## Antes de empezar: qué cambió y por qué

Vercel ejecuta la aplicación en **funciones serverless**, lo que impone dos reglas:

1. **No hay disco persistente.** Cualquier archivo que la aplicación escriba
   desaparece. Por eso las imágenes que subes desde el panel (logo, fotos de
   productos, testimonios) ahora se guardan **en la base de datos** y se sirven
   por `/media/<archivo>` con caché de un año en el CDN.
2. **No hay base de datos local.** SQLite no sirve en producción: hay que usar
   una base de datos PostgreSQL externa.

---

## Paso 1 — Base de datos PostgreSQL

Necesitas una base PostgreSQL accesible por internet. Opciones gratuitas:

- **Neon** (neon.tech) — recomendado, plan gratuito sin vencimiento.
- **Supabase** (supabase.com).
- La base de Render que ya existe (vence a los 90 días del plan gratuito).

Copia la **cadena de conexión** (empieza por `postgres://` o `postgresql://`).

## Paso 2 — Preparar la base de datos

Desde tu computador, apuntando a la base nueva, crea las tablas y los datos
iniciales:

```bash
# Windows (PowerShell)
$env:DATABASE_URL="postgresql://usuario:clave@host/basededatos"
$env:FLASK_APP="wsgi.py"
python -m flask db upgrade
python seed.py
```

Si vienes de una instalación anterior que tenía imágenes en disco, ejecuta
además (una sola vez) para trasladarlas a la base de datos:

```bash
python scripts/migrar_imagenes_a_bd.py
```

## Paso 3 — Compilar los recursos estáticos

```bash
python scripts/build_assets.py
```

Esto genera `app/static/dist/` (CSS y JS unidos, minificados y con hash).
**Esos archivos se suben al repositorio**, por eso hay que ejecutarlo cada vez
que cambies un CSS o un JS antes de desplegar.

## Paso 4 — Subir los cambios a GitHub

```bash
git add -A
git commit -m "Preparado para Vercel"
git push
```

## Paso 5 — Crear el proyecto en Vercel

1. Entra a **vercel.com** e inicia sesión con GitHub.
2. **Add New… → Project** y elige el repositorio `Digalo-con-flores`.
3. En *Framework Preset* deja **Other** (la configuración ya está en `vercel.json`).
4. Antes de desplegar, abre **Environment Variables** y agrega:

| Variable | Valor |
|---|---|
| `DATABASE_URL` | la cadena de conexión de PostgreSQL del paso 1 |
| `SECRET_KEY` | una cadena larga y aleatoria (no la de desarrollo) |
| `SITE_URL` | `https://tu-proyecto.vercel.app` |
| `MAIL_SERVER` | `smtp.gmail.com` |
| `MAIL_PORT` | `587` |
| `MAIL_USE_TLS` | `1` |
| `MAIL_USERNAME` | tu correo de Gmail |
| `MAIL_PASSWORD` | la contraseña de aplicación de 16 letras |
| `MAIL_DEFAULT_SENDER` | `Dígalo con Flores <tucorreo@gmail.com>` |
| `CURRENCY` | `COP` |

5. **Deploy**.

Para generar una `SECRET_KEY` segura:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

## Paso 6 — Después del primer despliegue

1. Entra a `https://tu-proyecto.vercel.app/cuenta/iniciar-sesion` con el usuario
   de ejemplo (`admin@digaloconflores.com` / `Flores2026!`) y **cambia la contraseña**.
2. Sube el logo real en **Panel → Configuración → Logo**.
3. Pon el número real en **Panel → Configuración → WhatsApp** (con indicativo,
   ej. `+57 300 123 4567`).
4. Ajusta `SITE_URL` en Vercel si la URL final es distinta.

---

## Actualizaciones futuras

```bash
python scripts/build_assets.py   # solo si cambiaste CSS o JS
git add -A && git commit -m "..." && git push
```

Vercel despliega automáticamente con cada `push`.

Si cambias algo de la base de datos (modelos), genera y aplica la migración:

```bash
python -m flask db migrate -m "descripción del cambio"
$env:DATABASE_URL="...la de produccion..."; python -m flask db upgrade
```

---

## Rendimiento incluido

- **CSS y JS unidos y minificados**, separados por área (la tienda no descarga
  nada del panel) y con hash en el nombre → caché permanente en el CDN.
- **Imágenes optimizadas al subirlas**: se redimensionan a 1400px de ancho y se
  recomprimen (una foto de 4 MB queda en ~150 KB).
- **Carga diferida** (`loading="lazy"`) en todas las imágenes fuera de la
  pantalla inicial, con dimensiones declaradas para que el diseño no salte.
- **Precarga con prioridad alta** de la imagen principal del inicio (mejora el LCP).
- **Fuentes sin bloquear el render** y `preconnect` a Google Fonts.
- **Scripts diferidos** (`defer`), no bloquean el análisis del HTML.
- **Cabeceras de caché** afinadas por tipo de recurso en `vercel.json`.
