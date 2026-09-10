from flask import render_template, redirect, url_for

from app.blueprints.admin import bp
from app.extensions import db
from app.models.notification import Notification


@bp.route("/notificaciones")
def notifications_list():
    notifications = Notification.query.order_by(Notification.created_at.desc()).limit(100).all()
    return render_template("admin/notifications/list.html", notifications=notifications)


@bp.route("/notificaciones/<int:notification_id>/leer", methods=["POST"])
def notification_mark_read(notification_id):
    notification = Notification.query.get_or_404(notification_id)
    notification.is_read = True
    db.session.commit()
    return redirect(url_for("admin.notifications_list"))


@bp.route("/notificaciones/marcar-todas", methods=["POST"])
def notifications_mark_all_read():
    Notification.query.filter_by(is_read=False).update({"is_read": True})
    db.session.commit()
    return redirect(url_for("admin.notifications_list"))
