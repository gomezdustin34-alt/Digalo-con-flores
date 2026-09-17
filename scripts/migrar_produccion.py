"""Aplica a la base de datos de producción las migraciones pendientes.

Vercel NO corre migraciones al desplegar: si el código sube con un modelo nuevo
y nadie migra, la web queda con el esquema viejo y cosas como guardar un pedido
fallan para todos los clientes. Este script hace ese paso, comprueba que quedó
bien y lo dice en castellano.

Uso (PowerShell, desde la carpeta del proyecto):

    python scripts/migrar_produccion.py

Toma la URL de `.env.local` (la que deja `vercel env pull`), prefiriendo
DATABASE_URL_UNPOOLED: el DDL no debe pasar por el pooler de conexiones.
También acepta la URL como argumento:

    python scripts/migrar_produccion.py "postgresql://..."

No borra ni modifica datos: solo agrega las columnas y tablas que falten.
"""
import os
import re
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)

# La consola de Windows no siempre habla UTF-8: sin esto, un acento o una
# flecha en un mensaje tumbaban el script al imprimirlo.
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:  # noqa: BLE001 - consolas antiguas
    pass


def leer_env_local():
    """Variables de `.env.local` (el archivo que genera `vercel env pull`)."""
    ruta = os.path.join(RAIZ, ".env.local")
    if not os.path.exists(ruta):
        return {}
    valores = {}
    with open(ruta, encoding="utf-8") as f:
        for linea in f:
            linea = linea.strip()
            if not linea or linea.startswith("#") or "=" not in linea:
                continue
            clave, valor = linea.split("=", 1)
            valores[clave.strip()] = valor.strip().strip('"').strip("'")
    return valores


def resolver_url():
    if len(sys.argv) > 1 and sys.argv[1].startswith(("postgres://", "postgresql://", "sqlite:///")):
        return sys.argv[1], "el argumento de la línea de comandos"
    env = leer_env_local()
    for clave in ("DATABASE_URL_UNPOOLED", "POSTGRES_URL_NON_POOLING", "DATABASE_URL", "POSTGRES_URL"):
        if env.get(clave):
            return env[clave], f".env.local ({clave})"
    return None, None


def oculta(url):
    """La URL sin la contraseña, para poder mostrarla sin filtrarla."""
    return re.sub(r"://([^:/@]+):[^@]*@", r"://\1:***@", url)


def main():
    url, origen = resolver_url()
    if not url:
        print("No encontré la URL de la base de datos.")
        print("Ejecuta `vercel env pull` para crear .env.local, o pásala como argumento.")
        return 1

    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)

    print(f"Base de datos: {oculta(url)}")
    print(f"   (tomada de {origen})")
    if "sslmode" not in url and "neon.tech" in url:
        url += ("&" if "?" in url else "?") + "sslmode=require"

    os.environ["DATABASE_URL"] = url
    os.environ.setdefault("SECRET_KEY", "solo-para-migrar")

    from sqlalchemy import inspect

    from app import create_app
    from app.extensions import db

    app = create_app()

    with app.app_context():
        inspector = inspect(db.engine)
        tablas = set(inspector.get_table_names())
        pendientes = []
        for nombre, tabla in db.metadata.tables.items():
            if nombre not in tablas:
                pendientes.append(f"falta la tabla «{nombre}»")
                continue
            columnas = {c["name"] for c in inspector.get_columns(nombre)}
            faltan = [c.name for c in tabla.columns if c.name not in columnas]
            if faltan:
                pendientes.append(f"a la tabla «{nombre}» le faltan: {', '.join(faltan)}")

        if not pendientes:
            print("\nLa base de producción ya está al día. No hay nada que migrar.")
        else:
            print("\nLe falta esto para estar al día:")
            for p in pendientes:
                print("  -", p)
            respuesta = input("\n¿Aplico las migraciones? (escribe SI): ").strip().upper()
            if respuesta != "SI":
                print("Cancelado. No se tocó nada.")
                return 1

            from flask_migrate import upgrade
            print()
            upgrade()

        # Comprobación final: el esquema tiene que coincidir con los modelos.
        inspector = inspect(db.engine)
        tablas = set(inspector.get_table_names())
        problemas = []
        for nombre, tabla in db.metadata.tables.items():
            if nombre not in tablas:
                problemas.append(f"sigue faltando la tabla «{nombre}»")
                continue
            columnas = {c["name"] for c in inspector.get_columns(nombre)}
            faltan = [c.name for c in tabla.columns if c.name not in columnas]
            if faltan:
                problemas.append(f"a «{nombre}» le siguen faltando: {', '.join(faltan)}")

        if problemas:
            print("\nQUEDÓ ALGO SIN APLICAR:")
            for p in problemas:
                print("  -", p)
            return 1

        print("\nListo: el esquema de producción coincide con el código.")

        # El número de WhatsApp vive en la configuración de la tienda, no en el
        # código: se cambia desde el panel, y aquí solo se muestra el actual.
        from app.utils.helpers import get_setting
        numero = get_setting("whatsapp", "") or "(vacío)"
        print(f"\nWhatsApp de la tienda en producción: {numero}")
        if numero.replace(" ", "") in ("(vacío)", "+573001234567"):
            print("  ATENCIÓN: ese es el número de ejemplo, no recibe mensajes.")
            print("  Cámbialo en el panel: Configuracion > WhatsApp.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
