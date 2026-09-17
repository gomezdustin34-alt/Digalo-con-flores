import secrets
from datetime import datetime, timezone

from app.extensions import db

ORDER_STATUSES = ("pendiente", "confirmado", "preparando", "en_camino", "entregado", "cancelado")


def generate_order_number():
    return "DCF-" + secrets.token_hex(4).upper()


class Order(db.Model):
    __tablename__ = "orders"

    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.String(20), unique=True, nullable=False, default=generate_order_number)

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)  # nullable: compra como invitado

    guest_email = db.Column(db.String(255))
    guest_name = db.Column(db.String(150))
    guest_phone = db.Column(db.String(30))

    status = db.Column(db.String(20), nullable=False, default="pendiente")

    subtotal = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    discount_total = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    shipping_total = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    total = db.Column(db.Numeric(10, 2), nullable=False, default=0)

    coupon_id = db.Column(db.Integer, db.ForeignKey("coupons.id"), nullable=True)

    delivery_address = db.Column(db.String(400))
    delivery_city = db.Column(db.String(100))
    # Referencias para llegar: apartamento, porteria, un punto conocido...
    delivery_notes = db.Column(db.String(300))
    delivery_date = db.Column(db.Date)
    delivery_time = db.Column(db.String(50))
    dedication_message = db.Column(db.Text)
    recipient_name = db.Column(db.String(150))

    # Marca si las unidades de este pedido ya fueron devueltas al inventario
    # (al cancelarlo), para no devolverlas dos veces.
    stock_restored = db.Column(db.Boolean, default=False, nullable=False)

    # Los pedidos terminados se archivan en vez de borrarse: salen de la lista
    # de trabajo del panel pero siguen existiendo, porque son el soporte de una
    # venta y la ley obliga a conservarlos.
    archived_at = db.Column(db.DateTime, nullable=True)

    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    items = db.relationship("OrderItem", backref="order", cascade="all, delete-orphan")
    payments = db.relationship("Payment", backref="order", cascade="all, delete-orphan")
    coupon = db.relationship("Coupon", backref="orders")

    # Los datos de contacto del pedido son los que el cliente escribió al
    # comprar, aunque tenga cuenta: el formulario llega autocompletado con los
    # de su perfil, y si cambió algo (otro teléfono para esta entrega, por
    # ejemplo) es eso lo que vale. Antes se tomaban siempre los de la cuenta y
    # el cambio se perdía. La cuenta queda solo como respaldo si faltara algo.
    @property
    def customer_name(self):
        return self.guest_name or (self.user.full_name if self.user else None)

    @property
    def customer_email(self):
        return self.guest_email or (self.user.email if self.user else None)

    @property
    def customer_phone(self):
        return self.guest_phone or (self.user.phone if self.user else None)

    @property
    def latest_payment(self):
        return self.payments[-1] if self.payments else None

    STATUS_LABELS = {
        "pendiente": "Pendiente",
        "confirmado": "Confirmado",
        "preparando": "Preparando",
        "en_camino": "En camino",
        "entregado": "Entregado",
        "cancelado": "Cancelado",
    }

    @property
    def is_archived(self):
        return self.archived_at is not None

    @property
    def status_label(self):
        return self.STATUS_LABELS.get(self.status, self.status)


class OrderItem(db.Model):
    __tablename__ = "order_items"

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("orders.id"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=True)

    product_name = db.Column(db.String(200), nullable=False)  # snapshot al momento de la compra
    quantity = db.Column(db.Integer, nullable=False, default=1)
    unit_price = db.Column(db.Numeric(10, 2), nullable=False)

    variation_label = db.Column(db.String(150))
    dedication_message = db.Column(db.Text)
    recipient_name = db.Column(db.String(150))

    product = db.relationship("Product")

    @property
    def line_total(self):
        return self.unit_price * self.quantity
