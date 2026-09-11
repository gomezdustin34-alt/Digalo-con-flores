# Despliegue en Vercel — Dígalo con Flores

El sitio ya está en producción: **https://digalo-con-flores.vercel.app**

Esta guía describe cómo quedó montado y qué hacer para actualizarlo.

---

## Cómo funciona

Vercel ejecuta la aplicación en **funciones serverless**, lo que impone dos reglas
que moldearon el proyecto:

1. **No hay disco persistente ni escritura.** Todo `/var/task` es de solo lectura.
   Por eso las imágenes que subes desde el panel (logo, fotos de productos,
   testimonios) se guardan **en la base de datos** y se sirven por
   `/media/<archivo>` con caché de un año en el CDN. Por eso también la carpeta
   `instance` de Flask vive en el directorio temporal (ver `app/__init__.py`).
2. **No hay base de datos local.** SQLite no sirve en producción; se usa
   PostgreSQL de Neon.

## Lo que ya está configurado

| Pieza | Valor |
|---|---|
| Proyecto | `b1-nar-10/digalo-con-flores` |
| Dominio | `https://digalo-con-flores.vercel.app` |
| Base de datos | Neon PostgreSQL, plan Free, región `iad1` |
| Repositorio | `gomezdustin34-alt/Digalo-con-flores`, conectado |
| Punto de entrada | `api/index.py` |
| Rutas y caché | `vercel.json` |

Variables de entorno en producción: `DATABASE_URL` (la conecta la integración de
Neon), `SECRET_KEY`, `SITE_URL`, `CURRENCY`.

**Pendiente:** las `MAIL_*` no están definidas, así que los correos
transaccionales no salen. Para activarlos hay que agregar `MAIL_SERVER`,
`MAIL_PORT`, `MAIL_USE_TLS`, `MAIL_USERNAME`, `MAIL_PASSWORD` y
`MAIL_DEFAULT_SENDER` con `vercel env add` o desde el panel.

---

## Actualizaciones del día a día

Cada `push` a `main` despliega a producción automáticamente.

```bash
python scripts/build_assets.py   # SOLO si cambiaste algún CSS o JS
git add -A && git commit -m "..." && git push
```

`build_assets.py` genera `app/static/dist/` (CSS y JS unidos, minificados y con
hash). **Esos archivos se versionan**, por eso hay que recompilar antes de subir
cuando toques un estilo o un script; si no, el sitio seguirá sirviendo el bundle
viejo.

## Si cambias un modelo

Vercel **no** corre migraciones al desplegar. Hay que aplicarlas a mano *antes*
de hacer push, o el código nuevo saldrá contra el esquema viejo:

```bash
# PowerShell
python -m flask db migrate -m "descripción del cambio"
$env:FLASK_APP="wsgi.py"
$env:DATABASE_URL="<DATABASE_URL_UNPOOLED de .env.local>"
python -m flask db upgrade
```

Se usa la URL *unpooled* para las migraciones: el DDL no debe pasar por el
pooler de conexiones.

Para traer las variables de producción a `.env.local`:

```bash
vercel env pull
```

## Despliegue manual

Si necesitas desplegar sin pasar por GitHub:

```bash
vercel deploy --prod
```

Si falla con `fetch failed`, es la red cortando la subida — reintenta.

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
- **Conexiones a la base de datos** con `pool_pre_ping` y reciclado corto, para
  no agotar el límite de Neon entre invocaciones.
