from app.extensions import db
from app.models.content import WebsiteContent, SiteSection
from app.models.notification import Notification

_CONTENT_CACHE = {}
_SECTIONS_CACHE = None


def get_content(key, default=""):
    if key in _CONTENT_CACHE:
        return _CONTENT_CACHE[key]
    row = WebsiteContent.query.filter_by(key=key).first()
    value = row.value if row and row.value is not None else default
    _CONTENT_CACHE[key] = value
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
    _CONTENT_CACHE[key] = value


def clear_content_cache():
    _CONTENT_CACHE.clear()
    global _SECTIONS_CACHE
    _SECTIONS_CACHE = None


def visible_sections():
    global _SECTIONS_CACHE
    if _SECTIONS_CACHE is None:
        rows = SiteSection.query.order_by(SiteSection.sort_order).all()
        _SECTIONS_CACHE = {row.key: row.is_visible for row in rows}
    return _SECTIONS_CACHE


def is_section_visible(key, default=True):
    return visible_sections().get(key, default)


def notify(type_, message, link=None):
    db.session.add(Notification(type=type_, message=message, link=link))
