from flask import render_template, request, redirect, url_for, flash

from app.blueprints.admin import bp
from app.extensions import db
from app.models.order import Order, ORDER_STATUSES
from app.services.email import get_email_provider
from app.services.email.templates import order_status_update_email


@bp.route("/pedidos")
def orders_list():
    status = request.args.get("status", "")
    query = Order.query
    if status:
        query = query.filter_by(status=status)
    orders = query.order_by(Order.created_at.desc()).all()
    return render_template("admin/orders/list.html", orders=orders, status=status, statuses=ORDER_STATUSES)


@bp.route("/pedidos/<int:order_id>")
def order_detail(order_id):
    order = Order.query.get_or_404(order_id)
    return render_template("admin/orders/detail.html", order=order, statuses=ORDER_STATUSES)


@bp.route("/pedidos/<int:order_id>/estado", methods=["POST"])
def order_update_status(order_id):
    order = Order.query.get_or_404(order_id)
    new_status = request.form.get("status")
    if new_status in ORDER_STATUSES:
        order.status = new_status
        db.session.commit()
        get_email_provider().send(
            order.customer_email, f"Actualización de tu pedido {order.number}", order_status_update_email(order)
        )
        flash("Estado del pedido actualizado.", "success")
    return redirect(url_for("admin.order_detail", order_id=order.id))
