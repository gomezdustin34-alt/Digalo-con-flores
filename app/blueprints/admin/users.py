from flask import render_template, redirect, url_for, flash
from flask_login import current_user, login_user

from app.blueprints.admin import bp
from app.blueprints.admin.forms import StaffUserForm
from app.extensions import db
from app.models.user import User
from app.utils.permissions import roles_required


@bp.route("/usuarios")
@roles_required("super_admin")
def staff_list():
    staff = User.query.filter(User.role != "customer").order_by(User.role).all()
    return render_template("admin/staff/list.html", staff=staff)


@bp.route("/usuarios/nuevo", methods=["GET", "POST"])
@roles_required("super_admin")
def staff_new():
    form = StaffUserForm(es_nuevo=True)
    if form.validate_on_submit():
        existing = User.query.filter_by(email=form.email.data.lower().strip()).first()
        if existing:
            flash("Ya existe un usuario con ese email.", "danger")
        else:
            user = User(
                first_name=form.first_name.data,
                last_name=form.last_name.data,
                email=form.email.data.lower().strip(),
                role=form.role.data,
            )
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()
            flash("Usuario del panel creado.", "success")
            return redirect(url_for("admin.staff_list"))
    return render_template("admin/staff/form.html", form=form, staff_user=None)


@bp.route("/usuarios/<int:user_id>/editar", methods=["GET", "POST"])
@roles_required("super_admin")
def staff_edit(user_id):
    staff_user = User.query.filter(User.id == user_id, User.role != "customer").first_or_404()
    form = StaffUserForm(obj=staff_user)
    if form.validate_on_submit():
        email = form.email.data.lower().strip()
        es_uno_mismo = staff_user.id == current_user.id
        if User.query.filter(User.email == email, User.id != staff_user.id).first():
            # El email es unico: sin esto, guardar uno repetido daba error 500.
            flash("Ya existe otro usuario con ese email.", "danger")
        elif es_uno_mismo and form.role.data != staff_user.role:
            # Quitarse a uno mismo el rol de super administrador deja la tienda
            # sin nadie que pueda gestionar usuarios.
            flash("No puedes cambiar tu propio rol.", "danger")
        else:
            staff_user.first_name = form.first_name.data
            staff_user.last_name = form.last_name.data
            staff_user.email = email
            staff_user.role = form.role.data
            if form.password.data:
                staff_user.set_password(form.password.data)
            db.session.commit()
            if es_uno_mismo and form.password.data:
                # La sesion depende de la contraseña: sin esto, cambiarse la
                # propia clave desde aqui cerraba la sesion de quien lo hacia.
                login_user(staff_user, fresh=True)
            flash("Usuario actualizado.", "success")
            return redirect(url_for("admin.staff_list"))
    return render_template("admin/staff/form.html", form=form, staff_user=staff_user)


@bp.route("/usuarios/<int:user_id>/eliminar", methods=["POST"])
@roles_required("super_admin")
def staff_delete(user_id):
    if user_id == current_user.id:
        flash("No puedes eliminar tu propio usuario.", "danger")
        return redirect(url_for("admin.staff_list"))
    staff_user = User.query.filter(User.id == user_id, User.role != "customer").first_or_404()
    db.session.delete(staff_user)
    db.session.commit()
    flash("Usuario eliminado.", "info")
    return redirect(url_for("admin.staff_list"))
