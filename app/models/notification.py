from datetime import datetime, timezone

from app.extensions import db


class Notification(db.Model):
    __tablename__ = "notifications"

    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(40), nullable=False)  # nuevo_pedido | nuevo_cliente | nuevo_pago | stock_bajo | nueva_suscripcion | nuevo_mensaje
    message = db.Column(db.String(300), nullable=False)
    link = db.Column(db.String(300))
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
