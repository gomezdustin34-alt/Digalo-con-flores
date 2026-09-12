"""Cabeceras de seguridad que acompañan a toda respuesta HTML.

Son la segunda linea de defensa: aunque se colara contenido malicioso, el
navegador se niega a ejecutarlo, a enmarcar el sitio en otra pagina o a
adivinar el tipo de un archivo.
"""
import secrets

from flask import g, request

# Dominios externos de los que el sitio carga algo. Hoy solo las tipografias
# de Google; cualquier otro origen queda bloqueado por el navegador.
FUENTES_CSS = "https://fonts.googleapis.com"
FUENTES_ARCHIVOS = "https://fonts.gstatic.com"


def _politica(nonce):
    """Content-Security-Policy.

    - `script-src` sin 'unsafe-inline': los scripts propios van en archivos y
      los dos que quedan en linea llevan este nonce, que cambia en cada
      peticion. Un script inyectado no puede adivinarlo.
    - `style-src` si permite 'unsafe-inline' porque las plantillas usan
      atributos style="..." en muchos sitios; quitarlo exigiria reescribirlas
      y el riesgo que cubre es mucho menor.
    - `frame-ancestors 'none'` impide que el sitio se cargue dentro de un
      iframe ajeno (clickjacking).
    - `form-action 'self'` evita que un formulario inyectado envie los datos
      del cliente a otro servidor.
    """
    return "; ".join([
        "default-src 'self'",
        "base-uri 'self'",
        "object-src 'none'",
        "frame-ancestors 'none'",
        "form-action 'self'",
        f"script-src 'self' 'nonce-{nonce}'",
        f"style-src 'self' 'unsafe-inline' {FUENTES_CSS}",
        f"font-src 'self' {FUENTES_ARCHIVOS} data:",
        "img-src 'self' data: blob:",
        "connect-src 'self'",
        "manifest-src 'self'",
        "upgrade-insecure-requests",
    ])


def registrar(app):
    @app.before_request
    def _generar_nonce():
        # Un valor distinto por peticion: es lo que autoriza a los dos scripts
        # en linea de la plantilla base.
        g.csp_nonce = secrets.token_urlsafe(16)

    @app.context_processor
    def _exponer_nonce():
        return {"csp_nonce": g.get("csp_nonce", "")}

    @app.after_request
    def _cabeceras(respuesta):
        respuesta.headers.setdefault("X-Content-Type-Options", "nosniff")
        respuesta.headers.setdefault("X-Frame-Options", "DENY")
        respuesta.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
        respuesta.headers.setdefault(
            "Permissions-Policy",
            "geolocation=(), microphone=(), camera=(), payment=(), usb=(), interest-cohort=()",
        )
        # HSTS solo tiene sentido sobre HTTPS; en local estorbaria.
        if request.is_secure:
            respuesta.headers.setdefault(
                "Strict-Transport-Security", "max-age=31536000; includeSubDomains"
            )

        # La CSP se aplica al HTML. Los archivos de /media llevan la suya, mas
        # restrictiva todavia (ver app/blueprints/media/routes.py).
        if respuesta.mimetype == "text/html":
            respuesta.headers.setdefault(
                "Content-Security-Policy", _politica(g.get("csp_nonce", ""))
            )
            # Las paginas privadas no deben quedar en la cache del navegador ni
            # en la de un proxy compartido.
            if request.path.startswith(("/admin", "/mi-cuenta", "/checkout")):
                respuesta.headers["Cache-Control"] = "no-store, private"
                respuesta.headers.setdefault("X-Robots-Tag", "noindex, nofollow")

        return respuesta
