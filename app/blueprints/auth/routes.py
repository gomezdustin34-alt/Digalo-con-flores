from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user

from app.blueprints.auth import bp
from app.blueprints.auth.forms import LoginForm, RegisterForm, ForgotPasswordForm, ResetPasswordForm
from app.blueprints.auth.tokens import generate_reset_token, verify_reset_token
from app.extensions import db, limiter
from app.models.user import User
from app.services.email import get_email_provider
from app.utils.content import notify


def _post_login_redirect(user):
    if user.role != "customer":
        return url_for("admin.dashboard")
    return url_for("storefront.home")


def _destino_seguro(user=None):
    """Devuelve el `next` solo si es una ruta interna.

    Sin esta comprobacion, un enlace con ?next=https://sitio-falso.com llevaria
    al usuario fuera del sitio justo despues de iniciar sesion.

    Ademas, a quien trabaja en el panel no se le manda a la tienda: si entra
    con sus credenciales, quiere administrar, no comprar. Para ver la tienda
    esta el boton "Ver tienda", que la abre aparte.
    """
    destino = request.args.get("next")
    if not destino or not destino.startswith("/") or destino.startswith("//"):
        return None
    if user is not None and user.role != "customer" and not destino.startswith("/admin"):
        return None
    return destino


@bp.route("/iniciar-sesion", methods=["GET", "POST"])
@limiter.limit("10 per minute")
def login():
    if current_user.is_authenticated:
        return redirect(_post_login_redirect(current_user))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower().strip()).first()
        if user and user.check_password(form.password.data):
            if user.is_blocked:
                flash("Tu cuenta ha sido bloqueada. Contáctanos para más información.", "danger")
                return render_template("auth/login.html", form=form)
            login_user(user, remember=form.remember.data)
            return redirect(_destino_seguro(user) or _post_login_redirect(user))
        flash("Email o contraseña incorrectos.", "danger")

    return render_template("auth/login.html", form=form)


@bp.route("/registro", methods=["GET", "POST"])
@limiter.limit("10 per minute")
def register():
    if current_user.is_authenticated:
        return redirect(url_for("storefront.home"))

    form = RegisterForm()
    if form.validate_on_submit():
        existing = User.query.filter_by(email=form.email.data.lower().strip()).first()
        if existing:
            flash("Ya existe una cuenta con ese email.", "danger")
        else:
            user = User(
                first_name=form.first_name.data.strip(),
                last_name=form.last_name.data.strip(),
                email=form.email.data.lower().strip(),
                phone=form.phone.data,
                role="customer",
            )
            user.set_password(form.password.data)
            db.session.add(user)
            notify("nuevo_cliente", f"Nuevo cliente registrado: {user.full_name}")
            db.session.commit()
            login_user(user)
            flash("¡Cuenta creada! Bienvenido/a a Dígalo con Flores.", "success")
            return redirect(url_for("storefront.home"))

    return render_template("auth/register.html", form=form)


@bp.route("/salir")
@login_required
def logout():
    logout_user()
    flash("Sesión cerrada.", "info")
    return redirect(url_for("storefront.home"))


@bp.route("/recuperar", methods=["GET", "POST"])
@limiter.limit("5 per minute")
def forgot_password():
    form = ForgotPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower().strip()).first()
        if user:
            token = generate_reset_token(user.email)
            reset_url = url_for("auth.reset_password", token=token, _external=True)
            html = f"""
            <div style='font-family:Arial,sans-serif;'>
              <h2>Recupera tu contraseña</h2>
              <p>Haz clic en el siguiente enlace para restablecer tu contraseña (válido por 1 hora):</p>
              <p><a href="{reset_url}">{reset_url}</a></p>
            </div>
            """
            get_email_provider().send(user.email, "Recupera tu contraseña — Dígalo con Flores", html)
        flash("Si el email existe, te enviamos instrucciones para recuperar tu contraseña.", "info")
        return redirect(url_for("auth.login"))

    return render_template("auth/forgot_password.html", form=form)


@bp.route("/restablecer/<token>", methods=["GET", "POST"])
def reset_password(token):
    email = verify_reset_token(token)
    if not email:
        flash("El enlace de recuperación no es válido o expiró.", "danger")
        return redirect(url_for("auth.forgot_password"))

    form = ResetPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=email).first()
        if user:
            user.set_password(form.password.data)
            db.session.commit()
            flash("Contraseña actualizada. Ya puedes iniciar sesión.", "success")
            return redirect(url_for("auth.login"))

    return render_template("auth/reset_password.html", form=form)
