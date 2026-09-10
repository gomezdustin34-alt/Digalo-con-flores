from itsdangerous import URLSafeTimedSerializer
from flask import current_app

RESET_SALT = "password-reset"


def generate_reset_token(user_email):
    serializer = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
    return serializer.dumps(user_email, salt=RESET_SALT)


def verify_reset_token(token, max_age=3600):
    serializer = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
    try:
        return serializer.loads(token, salt=RESET_SALT, max_age=max_age)
    except Exception:
        return None
