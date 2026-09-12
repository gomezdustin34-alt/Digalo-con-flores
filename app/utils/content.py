from flask import g, has_request_context

from app.extensions import db
from app.models.content import WebsiteContent, SiteSection
from app.models.notification import Notification

# La caché vive UNA petición, no la vida del proceso. En serverless hay varias
# instancias: una caché por-proceso hacía que, tras editar el contenido en una
# instancia, otra siguiera sirviendo el valor viejo de su memoria sin volver a
# mirar la base de datos. Con flask.g cada petición lee fresco y solo memoiza
# dentro de sí misma para no repetir consultas al pintar una página.
def _cache():
    if has_request_context():
        if not hasattr(g, "_content_cache"):
            g._content_cache = {}
        return g._content_cache
    return {}  # fuera de una petición (CLI, seed): sin caché


def get_content(key, default=""):
    cache = _cache()
    if key in cache:
        return cache[key]
    row = WebsiteContent.query.filter_by(key=key).first()
    value = row.value if row and row.value is not None else default
    cache[key] = value
    return value


def set_content(key, value, value_type="text", section=None):
    row = WebsiteContent.query.filter_by(key=key).first()
    if row is None:
        row = WebsiteContent(key=key, value=value, value_type=value_type, section=section)
        db.session.add(row)
    else:
        row.value = value
        if section:
            row.section = section
    _cache()[key] = value


def clear_content_cache():
    if has_request_context():
        g.pop("_content_cache", None)
        g.pop("_sections_cache", None)


def visible_sections():
    if has_request_context() and hasattr(g, "_sections_cache"):
        return g._sections_cache
    rows = SiteSection.query.order_by(SiteSection.sort_order).all()
    mapa = {row.key: row.is_visible for row in rows}
    if has_request_context():
        g._sections_cache = mapa
    return mapa


def is_section_visible(key, default=True):
    return visible_sections().get(key, default)


def notify(type_, message, link=None):
    db.session.add(Notification(type=type_, message=message, link=link))
