from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user

from app.blueprints.account import bp
from app.blueprints.account.forms import ProfileForm, ChangePasswordForm, AddressForm
from app.extensions import db
from app.models.order import Order
from app.models.user import Address
from app.models.favorite import Favorite
from app.models.product import Product


@bp.before_request
@login_required
def require_login():
    if current_user.role != "customer":
        return redirect(url_for("admin.dashboard"))


@bp.route("/")
def dashboard():
    orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.created_at.desc()).limit(5).all()
    return render_template("account/dashboard.html", orders=orders)


@bp.route("/pedidos")
def orders():
    all_orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.created_at.desc()).all()
    return render_template("account/orders.html", orders=all_orders)


@bp.route("/pedidos/<number>")
def order_detail(number):
    order = Order.query.filter_by(number=number, user_id=current_user.id).first_or_404()
    return render_template("account/order_detail.html", order=order)


@bp.route("/perfil", methods=["GET", "POST"])
def profile():
    form = ProfileForm(obj=current_user)
    password_form = ChangePasswordForm()

    if request.method == "POST" and "first_name" in request.form:
        if form.validate_on_submit():
            current_user.first_name = form.first_name.data
            current_user.last_name = form.last_name.data
            current_user.phone = form.phone.data
            db.session.commit()
            flash("Perfil actualizado.", "success")
            return redirect(url_for("account.profile"))

    if request.method == "POST" and "current_password" in request.form:
        if password_form.validate_on_submit():
            if current_user.check_password(password_form.current_password.data):
                current_user.set_password(password_form.new_password.data)
                db.session.commit()
                flash("Contraseña actualizada.", "success")
            else:
                flash("La contraseña actual no es correcta.", "danger")
            return redirect(url_for("account.profile"))

    return render_template("account/profile.html", form=form, password_form=password_form)


@bp.route("/direcciones")
def addresses():
    return render_template("account/addresses.html", addresses=current_user.addresses)


@bp.route("/direcciones/nueva", methods=["GET", "POST"])
def new_address():
    form = AddressForm()
    if form.validate_on_submit():
        if form.is_default.data:
            for a in current_user.addresses:
                a.is_default = False
        address = Address(user_id=current_user.id)
        form.populate_obj(address)
        db.session.add(address)
        db.session.commit()
        flash("Dirección guardada.", "success")
        return redirect(url_for("account.addresses"))
    return render_template("account/address_form.html", form=form)


@bp.route("/direcciones/<int:address_id>/eliminar", methods=["POST"])
def delete_address(address_id):
    address = Address.query.filter_by(id=address_id, user_id=current_user.id).first_or_404()
    db.session.delete(address)
    db.session.commit()
    flash("Dirección eliminada.", "info")
    return redirect(url_for("account.addresses"))


@bp.route("/favoritos")
def favorites():
    favs = Favorite.query.filter_by(user_id=current_user.id).order_by(Favorite.created_at.desc()).all()
    return render_template("account/favorites.html", favorites=favs)


@bp.route("/favoritos/<int:product_id>/alternar", methods=["POST"])
def toggle_favorite(product_id):
    product = Product.query.get_or_404(product_id)
    fav = Favorite.query.filter_by(user_id=current_user.id, product_id=product.id).first()
    if fav:
        db.session.delete(fav)
        is_favorite = False
    else:
        db.session.add(Favorite(user_id=current_user.id, product_id=product.id))
        is_favorite = True
    db.session.commit()

    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        from flask import jsonify
        return jsonify(ok=True, is_favorite=is_favorite)

    return redirect(request.referrer or url_for("account.favorites"))
