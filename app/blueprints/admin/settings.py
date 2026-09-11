from flask import render_template, request, redirect, url_for, flash

from app.blueprints.admin import bp
from app.extensions import db
from app.utils.helpers import get_setting, set_setting, clear_settings_cache
from app.utils.uploads import save_upload

SETTING_FIELDS = [
    "store_name", "contact_email", "contact_phone", "whatsapp",
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

        logo_url = save_upload(request.files.get("logo"), "branding")
        if logo_url:
            set_setting("logo_url", logo_url)

        favicon_url = save_upload(request.files.get("favicon"), "branding")
        if favicon_url:
            set_setting("favicon_url", favicon_url)

        db.session.commit()
        clear_settings_cache()
        flash("Configuración actualizada.", "success")
        return redirect(url_for("admin.settings"))

    values = {field: get_setting(field, "") for field in SETTING_FIELDS}
    values["logo_url"] = get_setting("logo_url", "")
    values["favicon_url"] = get_setting("favicon_url", "")
    return render_template("admin/settings.html", values=values)
