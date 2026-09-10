from app.extensions import db


class WebsiteContent(db.Model):
    """Pares clave/valor editables desde el panel (ej. hero.title, about.text)."""

    __tablename__ = "website_content"

    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(120), unique=True, nullable=False, index=True)
    value = db.Column(db.Text)
    value_type = db.Column(db.String(20), default="text")  # text | image | html
    section = db.Column(db.String(60))  # hero | about | contact | footer ...


class SiteSection(db.Model):
    """Controla qué secciones del sitio están visibles y en qué orden."""

    __tablename__ = "site_sections"

    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(60), unique=True, nullable=False)  # hero, categorias, destacados...
    label = db.Column(db.String(120), nullable=False)
    is_visible = db.Column(db.Boolean, default=True)
    sort_order = db.Column(db.Integer, default=0)


class Setting(db.Model):
    """Configuración general de la tienda (clave/valor)."""

    __tablename__ = "settings"

    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(120), unique=True, nullable=False, index=True)
    value = db.Column(db.Text)
