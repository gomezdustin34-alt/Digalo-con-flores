from datetime import datetime, timezone

from app.extensions import db

PAYMENT_STATUSES = ("pendiente", "aprobado", "rechazado", "cancelado", "reembolsado")


class Payment(db.Model):
    __tablename__ = "payments"

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("orders.id"), nullable=False)

    provider = db.Column(db.String(30), nullable=False, default="mercadopago")
    external_payment_id = db.Column(db.String(120))  # id devuelto por la pasarela
    method = db.Column(db.String(60))  # ej. "tarjeta_credito", "pse"

    amount = db.Column(db.Numeric(10, 2), nullable=False)
    status = db.Column(db.String(20), nullable=False, default="pendiente")

    raw_response = db.Column(db.Text)  # payload JSON de la pasarela (sin datos sensibles)

    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
