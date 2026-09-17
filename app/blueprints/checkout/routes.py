from flask import render_template, redirect, url_for, flash, request, session
from flask_login import current_user

from app.extensions import limiter
from app.blueprints.checkout import bp
from app.blueprints.checkout.forms import CheckoutForm
from app.blueprints.checkout import order_service
from app.blueprints.checkout.whatsapp import build_whatsapp_url, store_whatsapp_number
from app.blueprints.cart import cart_service
from app.models.order import Order
from app.services.email import get_email_provider
from app.services.email.templates import order_confirmation_email


@bp.route("/", methods=["GET", "POST"])
@limiter.limit("12 per hour", methods=["POST"])
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

        if current_user.is_authenticated:
            order_service.completar_perfil(current_user, form)

        get_email_provider().send(
            order.customer_email,
            f"Confirmación de tu pedido {order.number}",
            order_confirmation_email(order),
        )

        # Se recuerda en la sesion que este navegador acaba de hacer el pedido.
        # Es lo que autoriza a ver la pagina de confirmacion sin tener cuenta,
        # sin abrirla a cualquiera que conozca el numero.
        recientes = session.get("mis_pedidos", [])
        recientes = ([order.number] + recientes)[:20]
        session["mis_pedidos"] = recientes
        session.modified = True

        return redirect(url_for("checkout.whatsapp_redirect", order_number=order.number))

    return render_template(
        "checkout/checkout.html", form=form, cart=cart,
        regalo=cart_service.gift_details(),
    )


def _puede_ver(order):
    """Quien puede ver la pagina de confirmacion de un pedido.

    - Quien lo acaba de hacer (guardado en la sesion de este navegador).
    - El cliente con cuenta que es su dueño.
    Un desconocido que solo tenga el numero NO: para eso esta "Seguir mi
    pedido", que exige numero + correo.
    """
    if order.number in session.get("mis_pedidos", []):
        return True
    if current_user.is_authenticated and order.user_id == current_user.id:
        return True
    return False


@bp.route("/pedido/<order_number>")
def whatsapp_redirect(order_number):
    order = Order.query.filter_by(number=order_number).first_or_404()
    if not _puede_ver(order):
        # No es de este navegador ni de esta cuenta: se manda a la consulta con
        # correo, sin confirmar siquiera si el numero existe.
        flash("Para ver un pedido, confírmalo con tu número y tu correo.", "info")
        return redirect(url_for("storefront.track_order"))
    return render_template(
        "checkout/whatsapp.html",
        order=order,
        whatsapp_url=build_whatsapp_url(order),
        has_whatsapp=bool(store_whatsapp_number()),
    )
