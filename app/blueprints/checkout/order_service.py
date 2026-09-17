from datetime import datetime

from flask_login import current_user

from app.extensions import db
from app.blueprints.cart import cart_service
from app.models.order import Order, OrderItem
from app.models.subscriber import Subscriber
from app.utils.content import notify
from app.services.email import get_email_provider
from app.services.email.templates import welcome_subscriber_email
from app.services.notifications import notify_new_order


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


def _fecha(valor):
    """Convierte la fecha guardada en el carrito ("2026-09-20") en un date."""
    if not valor:
        return None
    try:
        return datetime.strptime(valor, "%Y-%m-%d").date()
    except (TypeError, ValueError):
        return None


def vincular_pedidos_invitado(user):
    """Asocia a la cuenta los pedidos que se hicieron como invitado con su correo.

    Mucha gente compra sin cuenta y la crea despues. Sin esto, esos pedidos
    quedaban con user_id vacio y "Mis pedidos" salia vacio aunque el correo
    coincidiera. Se llama al iniciar sesion y al registrarse.
    """
    correo = (user.email or "").lower().strip()
    if not correo:
        return 0
    pedidos = Order.query.filter(
        Order.user_id.is_(None),
        db.func.lower(Order.guest_email) == correo,
    ).all()
    for pedido in pedidos:
        pedido.user_id = user.id
    if pedidos:
        db.session.commit()
    return len(pedidos)


def completar_perfil(user, form):
    """Guarda en la cuenta los datos que le faltaban, para no volver a pedirlos.

    Solo rellena lo que está vacío en el perfil. Si el cliente cambió algo
    únicamente para este pedido (otro teléfono, por ejemplo), su perfil no se
    toca: eso se edita en "Mi perfil".
    """
    telefono = (form.phone.data or "").strip()
    if telefono and not (user.phone or "").strip():
        user.phone = telefono[:30]
        db.session.commit()


def create_order_from_cart(form):
    cart = cart_service.get_cart()
    if not cart["lines"]:
        return None

    # Lo que el cliente ya escribio en la pagina del producto manda; el
    # formulario del checkout solo mostro los campos que faltaban.
    regalo = cart_service.gift_details()
    delivery_time = dict(form.delivery_time.choices).get(form.delivery_time.data) if form.delivery_time.data else None

    order = Order(
        user_id=current_user.id if current_user.is_authenticated else None,
        # Recortes al tamaño de las columnas: nombre y apellido (100 + 100) o
        # direccion y ciudad (400 + 100) juntos podian pasarse y PostgreSQL
        # rechazaba el pedido entero.
        guest_name=f"{form.first_name.data} {form.last_name.data}".strip()[:150],
        guest_email=form.email.data.lower().strip(),
        guest_phone=form.phone.data,
        subtotal=cart["subtotal"],
        discount_total=cart["discount"],
        shipping_total=cart["shipping"],
        total=cart["total"],
        coupon_id=cart["coupon"].id if cart["coupon"] else None,
        delivery_address=f"{form.address.data}, {form.city.data}"[:400],
        delivery_city=form.city.data,
        delivery_notes=form.additional_info.data or None,
        delivery_date=form.delivery_date.data or _fecha(regalo["delivery_date"]),
        delivery_time=delivery_time or regalo["delivery_time"],
        dedication_message=form.dedication_message.data or regalo["dedication_message"],
        recipient_name=form.recipient_name.data or regalo["recipient_name"],
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

    notify_new_order(order)

    cart_service.clear_cart()
    return order
