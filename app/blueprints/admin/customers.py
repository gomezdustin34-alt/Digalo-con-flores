from flask import render_template, redirect, url_for, flash, request

from app.blueprints.admin import bp
from app.extensions import db
from app.models.user import User
from app.models.order import Order


@bp.route("/clientes")
def customers_list():
    q = request.args.get("q", "").strip()
    query = User.query.filter_by(role="customer")
    if q:
        query = query.filter(User.email.ilike(f"%{q}%"))
    customers = query.order_by(User.created_at.desc()).all()
    return render_template("admin/customers/list.html", customers=customers, q=q)


@bp.route("/clientes/<int:user_id>")
def customer_detail(user_id):
    customer = User.query.filter_by(id=user_id, role="customer").first_or_404()
    orders = Order.query.filter_by(user_id=customer.id).order_by(Order.created_at.desc()).all()
    return render_template("admin/customers/detail.html", customer=customer, orders=orders)


@bp.route("/clientes/<int:user_id>/alternar-bloqueo", methods=["POST"])
def customer_toggle_block(user_id):
    customer = User.query.filter_by(id=user_id, role="customer").first_or_404()
    customer.is_blocked = not customer.is_blocked
    db.session.commit()
    flash("Cliente bloqueado." if customer.is_blocked else "Cliente desbloqueado.", "info")
    return redirect(url_for("admin.customer_detail", user_id=customer.id))
