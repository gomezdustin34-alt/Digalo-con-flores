from flask import Blueprint

bp = Blueprint("storefront", __name__, template_folder="../../templates/storefront")

from app.blueprints.storefront import routes  # noqa: E402,F401
from app.blueprints.storefront import seo  # noqa: E402,F401
