from flask import render_template, redirect, url_for, flash

from app.blueprints.admin import bp
from app.blueprints.admin.forms import CouponForm
from app.extensions import db
from app.models.coupon import Coupon


@bp.route("/cupones")
def coupons_list():
    coupons = Coupon.query.order_by(Coupon.created_at.desc()).all()
    return render_template("admin/coupons/list.html", coupons=coupons)


@bp.route("/cupones/nuevo", methods=["GET", "POST"])
def coupon_new():
    form = CouponForm()
    if form.validate_on_submit():
        coupon = Coupon(code=form.code.data.strip().upper())
        form.populate_obj(coupon)
        coupon.code = form.code.data.strip().upper()
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
        form.populate_obj(coupon)
        coupon.code = form.code.data.strip().upper()
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
