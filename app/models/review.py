from datetime import datetime, timezone

from app.extensions import db


class Testimonial(db.Model):
    __tablename__ = "testimonials"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    photo_url = db.Column(db.String(500))
    comment = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Integer, default=5)  # 1-5

    status = db.Column(db.String(20), default="pendiente")  # pendiente | aprobado | oculto

    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
