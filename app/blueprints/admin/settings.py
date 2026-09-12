from flask import render_template, request, redirect, url_for, flash

from app.blueprints.admin import bp
from app.extensions import db
from app.utils.helpers import get_setting, set_setting, clear_settings_cache
from app.utils.uploads import save_upload

SETTING_FIELDS = [
    "store_name", "contact_email", "contact_phone", "whatsapp",
    # A donde llegan los avisos de pedido nuevo (privado, no se publica)
    "order_notification_email",
    "address", "hours", "currency",
    # Identificacion legal: aparece en las paginas de privacidad y terminos
    "legal_name", "legal_id",
    "instagram_url", "facebook_url", "tiktok_url",
    "shipping_flat_rate", "free_shipping_threshold",
]


@bp.route("/configuracion", methods=["GET", "POST"])
def settings():
    if request.method == "POST":
        for field in SETTING_FIELDS:
            set_setting(field, request.form.get(field, ""))

        for campo, ajuste in (("logo", "logo_url"), ("favicon", "favicon_url")):
            archivo = request.files.get(campo)
            url = save_upload(archivo, "branding")
            if url:
                set_setting(ajuste, url)
            elif archivo and archivo.filename:
                # Se rechazo por no ser una imagen valida o por pesar demasiado.
                flash(
                    f"El archivo de {campo} no se guardó: debe ser una imagen "
                    "JPG, PNG, WEBP o GIF de menos de 6 MB.",
                    "danger",
                )

        db.session.commit()
        clear_settings_cache()
        flash("Configuración actualizada.", "success")
        return redirect(url_for("admin.settings"))

    values = {field: get_setting(field, "") for field in SETTING_FIELDS}
    values["logo_url"] = get_setting("logo_url", "")
    values["favicon_url"] = get_setting("favicon_url", "")
    return render_template("admin/settings.html", values=values)
