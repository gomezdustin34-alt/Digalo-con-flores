"""Registro de acciones administrativas y eventos de seguridad.

Dos reglas que no se rompen:

1. **Nunca se guarda el contenido de un formulario.** Se registra que alguien
   hizo algo y sobre que ruta, no lo que escribio: asi es imposible que una
   contraseña, un token o el dato personal de un cliente acaben en el log.
2. **Un fallo registrando no puede tumbar la operacion.** Si la escritura del
   log falla, se anota en el log tecnico y la accion del usuario sigue.
"""
from flask import current_app, request
from flask_login import current_user

from app.extensions import db
from app.models.audit import AuditLog


def _ip():
    """IP real del visitante, respetando el proxy de Vercel."""
    reenviada = request.headers.get("X-Forwarded-For", "")
    if reenviada:
        return reenviada.split(",")[0].strip()[:45]
    return (request.remote_addr or "")[:45]


def registrar(accion, categoria="admin", resultado="ok", detalle=None, email=None):
    """Anota un evento. Devuelve el registro creado, o None si no se pudo."""
    try:
        autenticado = getattr(current_user, "is_authenticated", False)
        evento = AuditLog(
            categoria=categoria,
            accion=accion[:120],
            usuario_id=current_user.id if autenticado else None,
            usuario_email=(email or (current_user.email if autenticado else None) or "")[:255] or None,
            rol=(current_user.role if autenticado else None),
            ip=_ip(),
            metodo=request.method[:10],
            ruta=request.path[:300],
            resultado=resultado[:20],
            detalle=(detalle or "")[:300] or None,
        )
        db.session.add(evento)
        db.session.commit()
        return evento
    except Exception as e:  # noqa: BLE001 - auditar nunca puede romper la app
        db.session.rollback()
        current_app.logger.warning("No se pudo registrar la auditoría de %s: %s", accion, e)
        return None


def seguridad(accion, resultado="ok", detalle=None, email=None):
    """Atajo para eventos de cuenta: inicios de sesion, contraseñas, bloqueos."""
    return registrar(accion, categoria="seguridad", resultado=resultado, detalle=detalle, email=email)
