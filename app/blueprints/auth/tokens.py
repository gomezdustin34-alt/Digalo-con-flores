from itsdangerous import URLSafeTimedSerializer
from flask import current_app

RESET_SALT = "password-reset"


def generate_reset_token(user):
    """Token de recuperacion atado a la contraseña vigente.

    Lleva la huella de la contraseña actual: en cuanto se usa y la contraseña
    cambia, el mismo enlace deja de servir. Antes podia reutilizarse durante
    toda la hora, por ejemplo desde un correo reenviado.
    """
    serializer = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
    return serializer.dumps([user.email, user.huella_sesion], salt=RESET_SALT)


def verify_reset_token(token, max_age=3600):
    """Devuelve (email, huella) si el token es valido, o None."""
    serializer = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
    try:
        datos = serializer.loads(token, salt=RESET_SALT, max_age=max_age)
    except Exception:
        return None
    if not isinstance(datos, list) or len(datos) != 2:
        return None
    return datos[0], datos[1]
