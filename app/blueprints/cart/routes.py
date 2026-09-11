from flask import render_template, request, redirect, url_for, flash, jsonify

from app.blueprints.cart import bp
from app.blueprints.cart import cart_service

MAX_QUANTITY = 99


def _safe_quantity(raw, default=1):
    """Convierte la cantidad recibida del formulario a un entero seguro (1..99)."""
    try:
        value = int(str(raw).strip())
    except (TypeError, ValueError):
        value = default
    return max(1, min(MAX_QUANTITY, value))


def _safe_int(raw):
    try:
        return int(str(raw).strip())
    except (TypeError, ValueError):
        return None


@bp.route("/")
def view_cart():
    cart = cart_service.get_cart()
    return render_template("cart/cart.html", cart=cart)


@bp.route("/agregar/<int:product_id>", methods=["POST"])
def add(product_id):
    quantity = _safe_quantity(request.form.get("quantity", 1))
    # El precio NUNCA viene del formulario: se resuelve en el servidor a partir
    # del id de la variación guardada en la base de datos.
    variation_id = _safe_int(request.form.get("variation_id"))
    recipient_name = request.form.get("recipient_name") or None
    dedication_message = request.form.get("dedication_message") or None
    delivery_date = request.form.get("delivery_date") or None
    delivery_time = request.form.get("delivery_time") or None

    cart_service.add_to_cart(
        product_id, quantity, variation_id,
        recipient_name, dedication_message, delivery_date, delivery_time,
    )

    # "Comprar ahora": se agrega al carrito y se va derecho a pagar
    if request.form.get("accion") == "comprar":
        return redirect(url_for("checkout.checkout"))

    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        cart = cart_service.get_cart()
        return jsonify(ok=True, count=cart["count"])

    flash("Producto agregado al carrito.", "success")
    return redirect(request.referrer or url_for("cart.view_cart"))


@bp.route("/actualizar/<key>", methods=["POST"])
def update(key):
    quantity = _safe_quantity(request.form.get("quantity", 1))
    cart_service.update_quantity(key, quantity)
    return redirect(url_for("cart.view_cart"))


@bp.route("/eliminar/<key>", methods=["POST"])
def remove(key):
    cart_service.remove_from_cart(key)
    flash("Producto eliminado del carrito.", "info")
    return redirect(url_for("cart.view_cart"))


@bp.route("/cupon", methods=["POST"])
def apply_coupon():
    code = request.form.get("code", "")
    ok, error = cart_service.apply_coupon(code)
    if ok:
        flash("Cupón aplicado.", "success")
    else:
        flash(error, "danger")
    return redirect(url_for("cart.view_cart"))


@bp.route("/cupon/quitar", methods=["POST"])
def remove_coupon():
    cart_service.remove_coupon()
    return redirect(url_for("cart.view_cart"))
