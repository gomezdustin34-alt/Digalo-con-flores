"""URLs absolutas ancladas a SITE_URL, no a la cabecera Host de la petición.

Un enlace que va dentro de un correo (recuperar contraseña, avisos) no debe
construirse con `url_for(_external=True)`, porque ese toma el host de la
petición y el host puede venir manipulado por un atacante (cabecera Host o
X-Forwarded-Host). En Vercel hoy el borde normaliza el host, pero no queremos
depender de la infraestructura: el dominio del enlace sale de la configuración.
"""
from urllib.parse import urljoin

from flask import current_app, url_for


def url_absoluta(endpoint, **valores):
    """Como url_for(_external=True), pero anclada a SITE_URL."""
    base = (current_app.config.get("SITE_URL") or "").rstrip("/")
    ruta = url_for(endpoint, **valores)  # ruta relativa, sin host
    if not base:
        # Sin SITE_URL configurado se cae a _external como último recurso.
        return url_for(endpoint, _external=True, **valores)
    return urljoin(base + "/", ruta.lstrip("/"))
