# Dígalo con Flores — Tienda Online

Tienda de florería completa: catálogo, carrito, pedidos por WhatsApp, cuentas de cliente, favoritos, cupones, newsletter, y panel administrativo.

## Requisitos

- Python 3.11+

## Instalación

```bash
pip install -r requirements.txt
```

Copia `.env.example` a `.env` y ajusta los valores (ya viene un `.env` de desarrollo funcional con SQLite y una clave secreta generada).

## Poner en marcha con datos de ejemplo

```bash
python seed.py
python wsgi.py
```

Abre http://127.0.0.1:5000

**Usuario administrador de ejemplo:**
- Email: `admin@digaloconflores.com`
- Contraseña: `Flores2026!`

Cámbiala o crea nuevos usuarios desde **Panel → Usuarios y roles** (solo visible para super administradores).

## Estructura

- `app/models/` — modelos SQLAlchemy (usuarios, productos, pedidos, cupones, contenido, archivos, etc.)
- `app/blueprints/` — storefront (tienda pública), auth, cart, checkout, account (mi cuenta), admin (panel), media (archivos)
- `app/blueprints/checkout/whatsapp.py` — arma el mensaje del pedido y el link `wa.me` que recibe el cliente al terminar el checkout
- `app/services/email/` — envío de emails vía SMTP genérico (Flask-Mail). Sin `MAIL_USERNAME` configurado, los emails se simulan (quedan en el log) en vez de enviarse.
- `app/templates/` — Jinja2, organizadas por blueprint
- `app/static/` — CSS, JS e imágenes de ejemplo. `dist/` contiene los paquetes compilados.
- `scripts/build_assets.py` — une y minifica CSS/JS por área, con hash para caché permanente
- `api/index.py` — punto de entrada serverless para Vercel
- `vercel.json` — rutas y cabeceras de caché del CDN

## Archivos subidos

Las imágenes que se suben desde el panel **se guardan en la base de datos**, no
en disco, para que el sitio funcione en hosting serverless (Vercel), donde el
sistema de archivos es efímero. Se optimizan al subirlas (máximo 1400px de
ancho, recompresión) y se sirven por `/media/<archivo>` con caché de un año.

## Cómo funciona el pedido (sin pasarela de pago)

El cliente arma su carrito, llena sus datos de entrega en el checkout, y al confirmar se le arma automáticamente un mensaje de WhatsApp con el resumen del pedido (productos, total, dirección, dedicatoria) para que lo envíe directo al número de la tienda. El pago y la entrega se coordinan manualmente por WhatsApp. Configura el número real en **Panel → Configuración → WhatsApp**.

## Emails reales

Define `MAIL_SERVER`, `MAIL_USERNAME`, `MAIL_PASSWORD` y `MAIL_DEFAULT_SENDER` en `.env` con tu proveedor SMTP (Gmail, Zoho, tu hosting, etc.). Con esto configurado, se envían automáticamente: bienvenida al suscribirse, confirmación de pedido, aviso al dueño de la tienda (`contact_email` en Configuración) por cada pedido nuevo, cambios de estado de pedido, recuperación de contraseña y campañas de marketing.

## Despliegue en producción (Vercel) — recomendado

Ver la guía paso a paso en **[DESPLIEGUE-VERCEL.md](DESPLIEGUE-VERCEL.md)**.
Resumen: base PostgreSQL externa (Neon/Supabase), `python scripts/build_assets.py`,
`git push`, y crear el proyecto en Vercel con las variables de entorno.

## Despliegue alternativo (Render)

El proyecto ya incluye `render.yaml`, `Procfile` y soporte para PostgreSQL — listo para desplegar en [Render](https://render.com) con su plan gratuito:

1. Sube este proyecto a un repositorio de GitHub.
2. Crea una cuenta en Render y entra a **New + → Blueprint**.
3. Conecta el repositorio — Render detecta `render.yaml` y crea automáticamente el servicio web **y** una base de datos PostgreSQL gratuita, ya conectada por `DATABASE_URL`.
4. Antes de aplicar, completa las variables marcadas como manuales: `SITE_URL` (la URL que Render te asigna, ej. `https://digalo-con-flores.onrender.com`), `MAIL_USERNAME`, `MAIL_PASSWORD`, `MAIL_DEFAULT_SENDER`.
5. Aplica el blueprint. Render instala dependencias, corre las migraciones (`flask db upgrade`) y siembra datos de ejemplo (`seed.py`) automáticamente en cada build.
6. Una vez arriba, entra con el usuario admin de ejemplo, cambia la contraseña, sube el logo real y configura el número de WhatsApp — igual que en local.

El plan gratuito de Render "duerme" el servicio tras un rato sin uso (tarda unos segundos en despertar con la primera visita) y la base de datos gratuita expira a los 90 días — para una tienda real en producción, conviene pasar a un plan pago cuando el negocio lo justifique.

## Migrar de SQLite a otra base de datos

Cambia `DATABASE_URL` por tu cadena de conexión (Postgres, MySQL, etc.) e instala el driver correspondiente (`psycopg2-binary` ya incluido para Postgres; para MySQL instala `PyMySQL`). El código no usa nada específico de SQLite — solo tipos y consultas estándar de SQLAlchemy.

## Notas pendientes conocidas

- El logo real de la marca aún no está integrado como archivo — se usa una recreación en CSS/SVG del sello circular. Súbelo desde **Panel → Configuración → Logo** para reemplazarlo.
- Las fotos de productos son de stock (Unsplash), solo para referencia visual — reemplázalas con fotografía real del catálogo desde el panel.
- El número de WhatsApp de la tienda todavía tiene un valor de ejemplo — cámbialo en **Panel → Configuración → WhatsApp**.
- El envío de campañas de email es inmediato (botón "Enviar ahora"); la programación (`scheduled_at`) guarda la fecha pero requiere un proceso programado externo (cron / Celery) para dispararse automáticamente en producción.
