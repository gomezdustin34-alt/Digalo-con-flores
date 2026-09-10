from flask import Blueprint

bp = Blueprint("checkout", __name__, template_folder="../../templates/checkout")

from app.blueprints.checkout import routes  # noqa: E402,F401
