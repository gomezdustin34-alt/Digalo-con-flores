from datetime import datetime, timezone

from app.extensions import db


class Product(db.Model):
    __tablename__ = "products"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(220), unique=True, nullable=False, index=True)
    description = db.Column(db.Text)
    short_description = db.Column(db.String(300))

    price = db.Column(db.Numeric(10, 2), nullable=False)
    compare_at_price = db.Column(db.Numeric(10, 2))  # precio anterior

    sku = db.Column(db.String(60), unique=True)
    stock = db.Column(db.Integer, default=0, nullable=False)
    stock_minimo = db.Column(db.Integer, default=5, nullable=False)

    category_id = db.Column(db.Integer, db.ForeignKey("categories.id"))

    is_active = db.Column(db.Boolean, default=True, nullable=False)
    is_featured = db.Column(db.Boolean, default=False)
    is_new = db.Column(db.Boolean, default=False)
    tags = db.Column(db.String(300))  # separadas por coma

    # Personalización habilitada por producto
    allow_dedication = db.Column(db.Boolean, default=True)
    allow_recipient_name = db.Column(db.Boolean, default=True)
    allow_delivery_datetime = db.Column(db.Boolean, default=True)
    allow_color_choice = db.Column(db.Boolean, default=False)
    allow_size_choice = db.Column(db.Boolean, default=False)

    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    images = db.relationship("ProductImage", backref="product", cascade="all, delete-orphan", order_by="ProductImage.sort_order")
    variations = db.relationship("ProductVariation", backref="product", cascade="all, delete-orphan")

    @property
    def is_on_sale(self):
        return bool(self.compare_at_price and self.compare_at_price > self.price)

    @property
    def discount_percent(self):
        if not self.is_on_sale:
            return 0
        return round((1 - float(self.price) / float(self.compare_at_price)) * 100)

    @property
    def is_out_of_stock(self):
        return self.stock <= 0

    @property
    def is_low_stock(self):
        return 0 < self.stock <= self.stock_minimo

    @property
    def primary_image(self):
        return self.images[0].url if self.images else None

    @property
    def tag_list(self):
        return [t.strip() for t in (self.tags or "").split(",") if t.strip()]

    def __repr__(self):
        return f"<Product {self.slug}>"


class ProductImage(db.Model):
    __tablename__ = "product_images"

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    url = db.Column(db.String(500), nullable=False)
    alt_text = db.Column(db.String(200))
    sort_order = db.Column(db.Integer, default=0)


class ProductVariation(db.Model):
    __tablename__ = "product_variations"

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    kind = db.Column(db.String(50), nullable=False)  # ej. "Tamaño", "Color"
    value = db.Column(db.String(80), nullable=False)  # ej. "Grande", "Rojo"
    price_delta = db.Column(db.Numeric(10, 2), default=0)
    stock = db.Column(db.Integer, default=0)
