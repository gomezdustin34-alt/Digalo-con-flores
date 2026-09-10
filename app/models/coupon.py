from datetime import datetime, timezone

from app.extensions import db

coupon_categories = db.Table(
    "coupon_categories",
    db.Column("coupon_id", db.Integer, db.ForeignKey("coupons.id"), primary_key=True),
    db.Column("category_id", db.Integer, db.ForeignKey("categories.id"), primary_key=True),
)


class Coupon(db.Model):
    __tablename__ = "coupons"

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(40), unique=True, nullable=False, index=True)

    discount_type = db.Column(db.String(20), nullable=False, default="percent")  # percent | fixed
    discount_value = db.Column(db.Numeric(10, 2), nullable=False)

    starts_at = db.Column(db.DateTime, nullable=True)
    expires_at = db.Column(db.DateTime, nullable=True)

    max_uses = db.Column(db.Integer, nullable=True)  # None = ilimitado
    used_count = db.Column(db.Integer, default=0)

    min_purchase = db.Column(db.Numeric(10, 2), default=0)
    is_active = db.Column(db.Boolean, default=True)

    categories = db.relationship("Category", secondary=coupon_categories, backref="coupons")

    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def is_valid_now(self):
        now = datetime.now(timezone.utc)
        if not self.is_active:
            return False, "Este cupón ya no está activo."
        if self.starts_at and now < self.starts_at.replace(tzinfo=timezone.utc):
            return False, "Este cupón todavía no está disponible."
        if self.expires_at and now > self.expires_at.replace(tzinfo=timezone.utc):
            return False, "Este cupón ha expirado."
        if self.max_uses is not None and self.used_count >= self.max_uses:
            return False, "Este cupón alcanzó su límite de usos."
        return True, None

    def compute_discount(self, subtotal):
        subtotal = float(subtotal)
        if float(self.min_purchase or 0) > subtotal:
            return 0
        if self.discount_type == "percent":
            return round(subtotal * float(self.discount_value) / 100, 2)
        return min(float(self.discount_value), subtotal)
