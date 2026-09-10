from slugify import slugify as _slugify

from app.extensions import db
from app.models.content import Setting


def slugify(text):
    return _slugify(text, allow_unicode=False)


def unique_slug(model, base_text, exclude_id=None):
    """Genera un slug único para el modelo dado, agregando -2, -3... si hace falta."""
    base = slugify(base_text) or "item"
    slug = base
    i = 2
    while True:
        query = model.query.filter_by(slug=slug)
        if exclude_id is not None:
            query = query.filter(model.id != exclude_id)
        if not query.first():
            return slug
        slug = f"{base}-{i}"
        i += 1


def format_currency(amount, currency="COP"):
    try:
        amount = float(amount)
    except (TypeError, ValueError):
        amount = 0
    symbol = "$" if currency == "COP" else currency + " "
    return f"{symbol}{amount:,.0f}".replace(",", ".")


_SETTINGS_CACHE = {}


def get_setting(key, default=None):
    if key in _SETTINGS_CACHE:
        return _SETTINGS_CACHE[key]
    row = Setting.query.filter_by(key=key).first()
    value = row.value if row else default
    _SETTINGS_CACHE[key] = value
    return value


def set_setting(key, value):
    row = Setting.query.filter_by(key=key).first()
    if row is None:
        row = Setting(key=key, value=value)
        db.session.add(row)
    else:
        row.value = value
    _SETTINGS_CACHE[key] = value


def clear_settings_cache():
    _SETTINGS_CACHE.clear()
