from flask import render_template, redirect, url_for, flash, request
from flask_login import current_user

from app.blueprints.checkout import bp
from app.blueprints.checkout.forms import CheckoutForm
from app.blueprints.checkout import order_service
from app.blueprints.checkout.whatsapp import build_whatsapp_url, store_whatsapp_number
from app.blueprints.cart import cart_service
from app.models.order import Order
from app.services.email import get_email_provider
from app.services.email.templates import order_confirmation_email


@bp.route("/", methods=["GET", "POST"])
def checkout():
    cart = cart_service.get_cart()
    if not cart["lines"]:
        flash("Tu carrito está vacío.", "info")
        return redirect(url_for("cart.view_cart"))

    form = CheckoutForm()
    if current_user.is_authenticated and request.method == "GET":
        form.first_name.data = current_user.first_name
        form.last_name.data = current_user.last_name
        form.email.data = current_user.email
        form.phone.data = current_user.phone

    if form.validate_on_submit():
        faltantes = order_service.check_stock(cart)
        if faltantes:
            for producto, disponible, pedido in faltantes:
                if disponible == 0:
                    flash(f"“{producto.name}” se agotó. Quítalo del carrito para continuar.", "danger")
                else:
                    flash(
                        f"Solo quedan {disponible} unidades de “{producto.name}” "
                        f"(pediste {pedido}). Ajusta la cantidad para continuar.",
                        "danger",
                    )
            return redirect(url_for("cart.view_cart"))

        order = order_service.create_order_from_cart(form)
        if not order:
            flash("Tu carrito está vacío.", "info")
            return redirect(url_for("cart.view_cart"))

        get_email_provider().send(
            order.customer_email,
            f"Confirmación de tu pedido {order.number}",
            order_confirmation_email(order),
        )

        return redirect(url_for("checkout.whatsapp_redirect", order_number=order.number))

    return render_template("checkout/checkout.html", form=form, cart=cart)


@bp.route("/pedido/<order_number>")
def whatsapp_redirect(order_number):
    order = Order.query.filter_by(number=order_number).first_or_404()
    return render_template(
        "checkout/whatsapp.html",
        order=order,
        whatsapp_url=build_whatsapp_url(order),
        has_whatsapp=bool(store_whatsapp_number()),
    )
