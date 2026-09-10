from flask import render_template, redirect, url_for, flash

from app.blueprints.admin import bp
from app.extensions import db
from app.models.contact import ContactMessage


@bp.route("/mensajes")
def messages_list():
    messages = ContactMessage.query.order_by(ContactMessage.created_at.desc()).all()
    return render_template("admin/messages/list.html", messages=messages)


@bp.route("/mensajes/<int:message_id>")
def message_detail(message_id):
    message = ContactMessage.query.get_or_404(message_id)
    if not message.is_read:
        message.is_read = True
        db.session.commit()
    return render_template("admin/messages/detail.html", message=message)


@bp.route("/mensajes/<int:message_id>/eliminar", methods=["POST"])
def message_delete(message_id):
    message = ContactMessage.query.get_or_404(message_id)
    db.session.delete(message)
    db.session.commit()
    flash("Mensaje eliminado.", "info")
    return redirect(url_for("admin.messages_list"))
