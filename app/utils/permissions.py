from functools import wraps

from flask import abort
from flask_login import current_user

ROLE_HIERARCHY = {
    "super_admin": 4,
    "admin": 3,
    "editor": 2,
    "order_manager": 2,
    "customer": 0,
}

# Roles con acceso al panel administrativo (no incluye "customer")
STAFF_ROLES = ("super_admin", "admin", "editor", "order_manager")

# Gestión general de la tienda (catálogo, ventas, marketing, configuración)
MANAGEMENT_ROLES = ("super_admin", "admin")

# Puede modificar contenido del sitio (inicio, nosotros, footer, secciones, testimonios)
CONTENT_ROLES = ("super_admin", "admin", "editor")

# Puede gestionar pedidos e inventario (productos, categorías, stock)
ORDER_ROLES = ("super_admin", "admin", "order_manager")


def roles_required(*roles):
    """Restringe una vista a usuarios autenticados con alguno de los roles indicados."""

    def decorator(view_func):
        @wraps(view_func)
        def wrapped(*args, **kwargs):
            if not current_user.is_authenticated:
                abort(401)
            if current_user.role not in roles:
                abort(403)
            return view_func(*args, **kwargs)

        return wrapped

    return decorator


def staff_required(view_func):
    return roles_required(*STAFF_ROLES)(view_func)
