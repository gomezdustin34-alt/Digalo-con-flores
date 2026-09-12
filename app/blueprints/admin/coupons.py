from flask import render_template, redirect, url_for, flash

from app.blueprints.admin import bp
from app.blueprints.admin.forms import CouponForm
from app.extensions import db
from app.models.coupon import Coupon


@bp.route("/cupones")
def coupons_list():
    coupons = Coupon.query.order_by(Coupon.created_at.desc()).all()
    return render_template("admin/coupons/list.html", coupons=coupons)


def _codigo_repetido(codigo, excluir_id=None):
    """El codigo es unico en la base de datos: sin esta comprobacion, guardar uno
    repetido reventaba con un IntegrityError y el panel mostraba un error 500."""
    query = Coupon.query.filter_by(code=codigo)
    if excluir_id is not None:
        query = query.filter(Coupon.id != excluir_id)
    return query.first() is not None


@bp.route("/cupones/nuevo", methods=["GET", "POST"])
def coupon_new():
    form = CouponForm()
    if form.validate_on_submit():
        codigo = form.code.data.strip().upper()
        if _codigo_repetido(codigo):
            flash(f"Ya existe un cupón con el código {codigo}.", "danger")
            return render_template("admin/coupons/form.html", form=form, coupon=None)
        coupon = Coupon(code=codigo)
        form.populate_obj(coupon)
        coupon.code = codigo
        db.session.add(coupon)
        db.session.commit()
        flash("Cupón creado.", "success")
        return redirect(url_for("admin.coupons_list"))
    return render_template("admin/coupons/form.html", form=form, coupon=None)


@bp.route("/cupones/<int:coupon_id>/editar", methods=["GET", "POST"])
def coupon_edit(coupon_id):
    coupon = Coupon.query.get_or_404(coupon_id)
    form = CouponForm(obj=coupon)
    if form.validate_on_submit():
        codigo = form.code.data.strip().upper()
        if _codigo_repetido(codigo, excluir_id=coupon.id):
            flash(f"Ya existe otro cupón con el código {codigo}.", "danger")
            return render_template("admin/coupons/form.html", form=form, coupon=coupon)
        form.populate_obj(coupon)
        coupon.code = codigo
        db.session.commit()
        flash("Cupón actualizado.", "success")
        return redirect(url_for("admin.coupons_list"))
    return render_template("admin/coupons/form.html", form=form, coupon=coupon)


@bp.route("/cupones/<int:coupon_id>/eliminar", methods=["POST"])
def coupon_delete(coupon_id):
    coupon = Coupon.query.get_or_404(coupon_id)
    db.session.delete(coupon)
    db.session.commit()
    flash("Cupón eliminado.", "info")
    return redirect(url_for("admin.coupons_list"))
