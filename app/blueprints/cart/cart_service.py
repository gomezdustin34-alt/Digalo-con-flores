import hashlib
import json

from flask import session

from app.models.product import Product
from app.models.coupon import Coupon
from app.utils.helpers import get_setting

DEFAULT_SHIPPING_FLAT_RATE = 12000
DEFAULT_FREE_SHIPPING_THRESHOLD = 150000


def _shipping_flat_rate():
    return float(get_setting("shipping_flat_rate") or DEFAULT_SHIPPING_FLAT_RATE)


def _free_shipping_threshold():
    return float(get_setting("free_shipping_threshold") or DEFAULT_FREE_SHIPPING_THRESHOLD)


def _line_key(product_id, variation_label, recipient_name, dedication_message, delivery_date, delivery_time):
    raw = json.dumps(
        [product_id, variation_label, recipient_name, dedication_message, delivery_date, delivery_time],
        sort_keys=True,
    )
    return hashlib.md5(raw.encode()).hexdigest()[:12]


def _raw_cart():
    return session.setdefault("cart", [])


def cart_count():
    """Número de unidades en el carrito, leído solo de la sesión.

    No consulta la base de datos: se usa en el ícono del carrito que aparece en
    todas las páginas, así que debe ser lo más barato posible.
    """
    try:
        return sum(int(linea.get("quantity", 0)) for linea in session.get("cart", []))
    except (TypeError, ValueError):
        return 0


MAX_QUANTITY = 99


def add_to_cart(product_id, quantity=1, variation_id=None,
                 recipient_name=None, dedication_message=None, delivery_date=None, delivery_time=None):
    """Agrega una línea al carrito.

    El precio se calcula SIEMPRE en el servidor a partir del producto y —si
    aplica— de la variación guardada en la base de datos. Nunca se acepta un
    precio ni un ajuste de precio enviado por el navegador.
    """
    product = Product.query.get_or_404(product_id)

    variation_label = None
    price_delta = 0
    if variation_id is not None:
        variation = next((v for v in product.variations if v.id == variation_id), None)
        if variation is not None:
            variation_label = f"{variation.kind}: {variation.value}"
            price_delta = float(variation.price_delta or 0)

    quantity = max(1, min(MAX_QUANTITY, int(quantity)))
    key = _line_key(product_id, variation_label, recipient_name, dedication_message, delivery_date, delivery_time)

    cart = _raw_cart()
    for line in cart:
        if line["key"] == key:
            line["quantity"] = min(MAX_QUANTITY, line["quantity"] + quantity)
            session.modified = True
            return

    cart.append({
        "key": key,
        "product_id": product.id,
        "quantity": quantity,
        "unit_price": float(product.price) + price_delta,
        "variation_id": variation_id,
        "variation_label": variation_label,
        "recipient_name": recipient_name,
        "dedication_message": dedication_message,
        "delivery_date": delivery_date,
        "delivery_time": delivery_time,
    })
    session.modified = True


CAMPOS_REGALO = ("recipient_name", "dedication_message", "delivery_date", "delivery_time")


def gift_details():
    """Datos del regalo que el cliente ya escribio en la pagina del producto.

    Devuelve el primer valor no vacio de cada campo entre todas las lineas, para
    que el checkout no vuelva a preguntar lo que ya sabe.
    """
    datos = {campo: None for campo in CAMPOS_REGALO}
    for line in _raw_cart():
        for campo in CAMPOS_REGALO:
            if not datos[campo] and line.get(campo):
                datos[campo] = line[campo]
    return datos


def update_quantity(key, quantity):
    cart = _raw_cart()
    for line in cart:
        if line["key"] == key:
            line["quantity"] = max(1, min(MAX_QUANTITY, int(quantity)))
            break
    session.modified = True


def remove_from_cart(key):
    cart = _raw_cart()
    session["cart"] = [line for line in cart if line["key"] != key]
    session.modified = True


def clear_cart():
    session["cart"] = []
    session.pop("coupon_code", None)
    session.modified = True


def apply_coupon(code):
    coupon = Coupon.query.filter_by(code=code.strip().upper()).first()
    if not coupon:
        return False, "Cupón no válido."
    valid, error = coupon.is_valid_now()
    if not valid:
        return False, error
    session["coupon_code"] = coupon.code
    session.modified = True
    return True, None


def remove_coupon():
    session.pop("coupon_code", None)
    session.modified = True


def get_cart():
    cart = _raw_cart()
    lines = []
    subtotal = 0
    count = 0

    for line in cart:
        product = Product.query.get(line["product_id"])
        if not product:
            continue

        # El precio se recalcula desde la base de datos en cada lectura, para que
        # siempre refleje el precio vigente del producto y de su variación.
        unit_price = float(product.price)
        variation_id = line.get("variation_id")
        if variation_id is not None:
            variation = next((v for v in product.variations if v.id == variation_id), None)
            if variation is not None:
                unit_price += float(variation.price_delta or 0)

        quantity = max(1, min(MAX_QUANTITY, int(line["quantity"])))
        line_total = unit_price * quantity
        subtotal += line_total
        count += quantity
        lines.append({
            **line,
            "quantity": quantity,
            "unit_price": unit_price,
            "product": product,
            "line_total": line_total,
        })

    discount = 0
    coupon = None
    coupon_code = session.get("coupon_code")
    if coupon_code:
        coupon = Coupon.query.filter_by(code=coupon_code).first()
        if coupon:
            valid, _ = coupon.is_valid_now()
            if valid:
                discount = coupon.compute_discount(subtotal)
            else:
                coupon = None
                session.pop("coupon_code", None)

    shipping = 0
    if lines:
        shipping = 0 if subtotal >= _free_shipping_threshold() else _shipping_flat_rate()

    total = max(0, subtotal - discount) + shipping

    return {
        "lines": lines,
        "count": count,
        "subtotal": subtotal,
        "discount": discount,
        "coupon": coupon,
        "shipping": shipping,
        "total": total,
    }
