from flask import Blueprint

bp = Blueprint("cart", __name__, template_folder="../../templates/cart")

from app.blueprints.cart import routes  # noqa: E402,F401
