from flask import render_template

from app.blueprints.admin import bp
from app.models.subscriber import Subscriber


@bp.route("/suscriptores")
def subscribers_list():
    subscribers = Subscriber.query.order_by(Subscriber.created_at.desc()).all()
    return render_template("admin/subscribers/list.html", subscribers=subscribers)
