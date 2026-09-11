from flask_login import current_user

from app.extensions import db
from app.blueprints.cart import cart_service
from app.models.order import Order, OrderItem
from app.models.subscriber import Subscriber
from app.utils.content import notify
from app.utils.helpers import get_setting
from app.services.email import get_email_provider
from app.services.email.templates import admin_new_order_email, welcome_subscriber_email


def _subscribe_email(email):
    email = email.lower().strip()
    subscriber = Subscriber.query.filter_by(email=email).first()
    if subscriber is None:
        db.session.add(Subscriber(email=email))
        get_email_provider().send(email, "¡Bienvenido/a a Dígalo con Flores!", welcome_subscriber_email())
    elif not subscriber.is_active:
        subscriber.is_active = True
        subscriber.unsubscribed_at = None


def check_stock(cart):
    """Devuelve la lista de productos del carrito sin unidades suficientes."""
    faltantes = []
    for line in cart["lines"]:
        producto = line["product"]
        if (producto.stock or 0) < line["quantity"]:
            faltantes.append((producto, producto.stock or 0, line["quantity"]))
    return faltantes


def create_order_from_cart(form):
    cart = cart_service.get_cart()
    if not cart["lines"]:
        return None

    order = Order(
        user_id=current_user.id if current_user.is_authenticated else None,
        guest_name=f"{form.first_name.data} {form.last_name.data}".strip(),
        guest_email=form.email.data.lower().strip(),
        guest_phone=form.phone.data,
        subtotal=cart["subtotal"],
        discount_total=cart["discount"],
        shipping_total=cart["shipping"],
        total=cart["total"],
        coupon_id=cart["coupon"].id if cart["coupon"] else None,
        delivery_address=f"{form.address.data}, {form.city.data}",
        delivery_city=form.city.data,
        delivery_date=form.delivery_date.data,
        delivery_time=dict(form.delivery_time.choices).get(form.delivery_time.data) if form.delivery_time.data else None,
        dedication_message=form.dedication_message.data,
        recipient_name=form.recipient_name.data,
    )

    for line in cart["lines"]:
        order.items.append(OrderItem(
            product_id=line["product"].id,
            product_name=line["product"].name,
            quantity=line["quantity"],
            unit_price=line["unit_price"],
            variation_label=line["variation_label"],
            dedication_message=line["dedication_message"],
            recipient_name=line["recipient_name"],
        ))
        # Descuenta inventario sin dejarlo nunca en negativo
        line["product"].stock = max(0, (line["product"].stock or 0) - line["quantity"])

    if cart["coupon"]:
        cart["coupon"].used_count = (cart["coupon"].used_count or 0) + 1

    db.session.add(order)
    db.session.flush()
    notify("nuevo_pedido", f"Nuevo pedido {order.number} por ${order.total:,.0f}", link=f"/admin/pedidos/{order.id}")
    _subscribe_email(order.customer_email)
    db.session.commit()

    admin_email = get_setting("contact_email")
    if admin_email:
        get_email_provider().send(
            admin_email,
            f"🌸 Nuevo pedido {order.number} — ${order.total:,.0f}",
            admin_new_order_email(order),
        )

    cart_service.clear_cart()
    return order
