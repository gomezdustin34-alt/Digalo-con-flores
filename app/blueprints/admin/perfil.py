from flask import render_template, redirect, url_for, flash
from flask_login import current_user, login_user
from flask_wtf import FlaskForm
from wtforms import PasswordField
from wtforms.validators import DataRequired, EqualTo, Length

from app.blueprints.admin import bp
from app.extensions import db
from app.utils.auditoria import seguridad


class CambiarClaveForm(FlaskForm):
    actual = PasswordField("Contraseña actual", validators=[DataRequired()])
    nueva = PasswordField(
        "Nueva contraseña",
        validators=[DataRequired(), Length(min=10, message="Mínimo 10 caracteres.")],
    )
    confirmar = PasswordField(
        "Repite la nueva contraseña",
        validators=[DataRequired(), EqualTo("nueva", message="Las contraseñas no coinciden.")],
    )


@bp.route("/mi-clave", methods=["GET", "POST"])
def cambiar_clave():
    """Cambio de contraseña para cualquiera que trabaje en el panel.

    Hasta ahora no existia: el perfil de cliente rechaza al personal y la
    edicion de usuarios es solo del super administrador, asi que un editor no
    tenia ninguna forma de cambiar su clave.
    """
    form = CambiarClaveForm()
    if form.validate_on_submit():
        if not current_user.check_password(form.actual.data):
            seguridad("cambio de contraseña rechazado", resultado="denegado",
                      detalle="la contraseña actual no coincide")
            flash("La contraseña actual no es correcta.", "danger")
            return render_template("admin/perfil/clave.html", form=form)

        if form.nueva.data == form.actual.data:
            flash("La nueva contraseña debe ser distinta de la actual.", "danger")
            return render_template("admin/perfil/clave.html", form=form)

        current_user.set_password(form.nueva.data)
        db.session.commit()
        seguridad("contraseña cambiada")
        # La identidad de sesion depende del hash: sin esto, el propio cambio
        # dejaria fuera a quien lo esta haciendo.
        login_user(current_user, fresh=True)
        flash(
            "Contraseña actualizada. Las sesiones abiertas en otros dispositivos se cerraron.",
            "success",
        )
        return redirect(url_for("admin.dashboard"))

    return render_template("admin/perfil/clave.html", form=form)
