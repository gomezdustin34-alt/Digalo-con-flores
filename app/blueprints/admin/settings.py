from flask import current_app, render_template, request, redirect, url_for, flash
from flask_mail import Message

from app.blueprints.admin import bp
from app.extensions import db, mail
from app.utils.helpers import get_setting, set_setting, clear_settings_cache, parse_amount
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

CAMPOS_IMPORTE = ("shipping_flat_rate", "free_shipping_threshold")


@bp.route("/configuracion", methods=["GET", "POST"])
def settings():
    if request.method == "POST":
        for field in SETTING_FIELDS:
            valor = request.form.get(field, "")
            if field in CAMPOS_IMPORTE and valor.strip():
                numero = parse_amount(valor)
                if numero is None:
                    flash(f"El valor «{valor}» no es un importe válido; no se cambió.", "danger")
                    continue
                # Se guarda limpio ("12000"), sin simbolos ni puntos de miles.
                valor = str(int(numero)) if numero.is_integer() else str(numero)
            set_setting(field, valor)

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


@bp.route("/configuracion/probar-correo", methods=["POST"])
def settings_probar_correo():
    """Manda un correo de prueba y dice exactamente que contesto el servidor.

    Un fallo de correo es invisible desde fuera: la tienda sigue vendiendo y
    los avisos simplemente dejan de llegar. Con esto se comprueba en dos
    segundos si el usuario y la contrasena siguen sirviendo.
    """
    destino = get_setting("order_notification_email") or get_setting("contact_email")
    if not destino:
        flash("Primero escribe el email de avisos (o el de contacto) y guarda.", "danger")
        return redirect(url_for("admin.settings"))

    if not current_app.config.get("MAIL_USERNAME"):
        flash(
            "No hay credenciales de correo configuradas (MAIL_USERNAME y MAIL_PASSWORD), "
            "asi que la tienda no envia ningun correo.",
            "danger",
        )
        return redirect(url_for("admin.settings"))

    cuerpo = (
        "<p>Esto es una prueba enviada desde el panel de Dígalo con Flores.</p>"
        "<p>Si lo estás leyendo, los avisos de pedido y los correos a los "
        "clientes están saliendo bien.</p>"
    )
    try:
        mail.send(Message(
            subject="Prueba de correo — Dígalo con Flores",
            recipients=[destino],
            html=cuerpo,
            body="Prueba enviada desde el panel de Dígalo con Flores.",
        ))
        flash(
            f"Correo de prueba enviado a {destino}. Si no llega en un par de minutos, "
            "mira la carpeta de spam.",
            "success",
        )
    except Exception as e:  # noqa: BLE001 - se muestra el motivo tal cual
        flash(f"El servidor de correo rechazó el envío: {str(e)[:300]}", "danger")
    return redirect(url_for("admin.settings"))
