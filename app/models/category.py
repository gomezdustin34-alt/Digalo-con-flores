from app.extensions import db


class Category(db.Model):
    __tablename__ = "categories"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    slug = db.Column(db.String(120), unique=True, nullable=False, index=True)
    description = db.Column(db.Text)
    image_url = db.Column(db.String(500))
    icon = db.Column(db.String(30))  # clave del icono vectorial, ej. "rosa"
    sort_order = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)

    products = db.relationship("Product", backref="category", lazy="dynamic")

    @property
    def icon_key(self):
        """Clave del icono vectorial, tolerando datos antiguos (emojis)."""
        from app.utils.icons import normalizar
        return normalizar(self.icon, self.slug)

    def __repr__(self):
        return f"<Category {self.slug}>"
