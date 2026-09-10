from flask import current_app
from flask_mail import Message

from app.extensions import mail
from app.services.email.base import EmailProvider


class SMTPEmailProvider(EmailProvider):
    def send(self, to, subject, html_body, text_body=None):
        if not current_app.config.get("MAIL_USERNAME"):
            current_app.logger.info("[email simulado] Para: %s | Asunto: %s", to, subject)
            return
        msg = Message(subject=subject, recipients=[to], html=html_body, body=text_body or "")
        mail.send(msg)
