from datetime import datetime, timezone

from app.extensions import db

CAMPAIGN_STATUSES = ("borrador", "programada", "enviando", "enviada")


class EmailCampaign(db.Model):
    __tablename__ = "email_campaigns"

    id = db.Column(db.Integer, primary_key=True)
    subject = db.Column(db.String(200), nullable=False)
    content_html = db.Column(db.Text, nullable=False)

    status = db.Column(db.String(20), nullable=False, default="borrador")
    scheduled_at = db.Column(db.DateTime, nullable=True)
    sent_at = db.Column(db.DateTime, nullable=True)
    recipients_count = db.Column(db.Integer, default=0)

    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
