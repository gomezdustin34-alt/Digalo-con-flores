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


def add_to_cart(product_id, quantity=1, variation_label=None, price_delta=0,
                 recipient_name=None, dedication_message=None, delivery_date=None, delivery_time=None):
    product = Product.query.get_or_404(product_id)
    key = _line_key(product_id, variation_label, recipient_name, dedication_message, delivery_date, delivery_time)

    cart = _raw_cart()
    for line in cart:
        if line["key"] == key:
            line["quantity"] += quantity
            session.modified = True
            return

    cart.append({
        "key": key,
        "product_id": product.id,
        "quantity": quantity,
        "unit_price": float(product.price) + float(price_delta or 0),
        "variation_label": variation_label,
        "recipient_name": recipient_name,
        "dedication_message": dedication_message,
        "delivery_date": delivery_date,
        "delivery_time": delivery_time,
    })
    session.modified = True


def update_quantity(key, quantity):
    cart = _raw_cart()
    for line in cart:
        if line["key"] == key:
            line["quantity"] = max(1, quantity)
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
        line_total = line["unit_price"] * line["quantity"]
        subtotal += line_total
        count += line["quantity"]
        lines.append({
            **line,
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
