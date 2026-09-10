from flask import render_template, redirect, url_for, flash

from app.blueprints.admin import bp
from app.blueprints.admin.forms import TestimonialForm
from app.extensions import db
from app.models.review import Testimonial
from app.utils.uploads import save_upload


@bp.route("/testimonios")
def testimonials_list():
    testimonials = Testimonial.query.order_by(Testimonial.created_at.desc()).all()
    return render_template("admin/testimonials/list.html", testimonials=testimonials)


@bp.route("/testimonios/nuevo", methods=["GET", "POST"])
def testimonial_new():
    form = TestimonialForm()
    if form.validate_on_submit():
        testimonial = Testimonial()
        form.populate_obj(testimonial)
        photo_url = save_upload(form.photo.data, "testimonials")
        if photo_url:
            testimonial.photo_url = photo_url
        db.session.add(testimonial)
        db.session.commit()
        flash("Testimonio creado.", "success")
        return redirect(url_for("admin.testimonials_list"))
    return render_template("admin/testimonials/form.html", form=form, testimonial=None)


@bp.route("/testimonios/<int:testimonial_id>/editar", methods=["GET", "POST"])
def testimonial_edit(testimonial_id):
    testimonial = Testimonial.query.get_or_404(testimonial_id)
    form = TestimonialForm(obj=testimonial)
    if form.validate_on_submit():
        form.populate_obj(testimonial)
        photo_url = save_upload(form.photo.data, "testimonials")
        if photo_url:
            testimonial.photo_url = photo_url
        db.session.commit()
        flash("Testimonio actualizado.", "success")
        return redirect(url_for("admin.testimonials_list"))
    return render_template("admin/testimonials/form.html", form=form, testimonial=testimonial)


@bp.route("/testimonios/<int:testimonial_id>/eliminar", methods=["POST"])
def testimonial_delete(testimonial_id):
    testimonial = Testimonial.query.get_or_404(testimonial_id)
    db.session.delete(testimonial)
    db.session.commit()
    flash("Testimonio eliminado.", "info")
    return redirect(url_for("admin.testimonials_list"))
