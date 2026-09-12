from flask import Blueprint, abort, request
from flask_login import login_required, current_user

from app.utils.permissions import STAFF_ROLES, MANAGEMENT_ROLES, CONTENT_ROLES, ORDER_ROLES, roles_required

bp = Blueprint("admin", __name__, template_folder="../../templates/admin")

# Prefijo del endpoint (después de "admin.") -> roles permitidos.
# Se evalúa en orden; el primer prefijo que coincida gana. "staff" (Usuarios y
# roles) ya está protegido aparte con roles_required("super_admin") en users.py.
SECTION_ROLES = [
    ("dashboard", STAFF_ROLES),
    ("notification", STAFF_ROLES),
    ("product", ORDER_ROLES),
    ("categor", ORDER_ROLES),
    ("order", ORDER_ROLES),
    ("content", CONTENT_ROLES),
    ("testimonial", CONTENT_ROLES),
    ("cambiar_clave", STAFF_ROLES),
    ("staff", ("super_admin",)),
    ("audit", ("super_admin",)),
]


def _allowed_roles_for(endpoint):
    name = endpoint.split(".", 1)[-1] if endpoint else ""
    for prefix, roles in SECTION_ROLES:
        if name.startswith(prefix):
            return roles
    return MANAGEMENT_ROLES


@bp.before_request
@login_required
@roles_required(*STAFF_ROLES)
def require_staff():
    if current_user.role not in _allowed_roles_for(request.endpoint):
        from app.utils.auditoria import registrar
        registrar(f"acceso denegado a {request.endpoint}", resultado="denegado")
        abort(403)


@bp.after_request
def registrar_accion(respuesta):
    """Deja constancia de todo lo que modifica algo en el panel.

    Se engancha aqui, al blueprint entero, y no en cada vista: asi ninguna ruta
    nueva puede olvidarse de auditar. Solo se anota la accion y la ruta, jamas
    el contenido del formulario.
    """
    if request.method in ("GET", "HEAD", "OPTIONS"):
        return respuesta
    from app.utils.auditoria import registrar
    registrar(
        request.endpoint or request.path,
        resultado="ok" if respuesta.status_code < 400 else "error",
        detalle=f"HTTP {respuesta.status_code}",
    )
    return respuesta


from app.blueprints.admin import (  # noqa: E402,F401
    audit,
    perfil,
    dashboard,
    products,
    categories,
    orders,
    customers,
    coupons,
    content,
    settings,
    testimonials,
    messages,
    subscribers,
    campaigns,
    notifications,
    users,
)
