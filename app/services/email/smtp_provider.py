from flask import current_app
from flask_mail import Message

from app.extensions import mail
from app.services.email.base import EmailProvider


class SMTPEmailProvider(EmailProvider):
    def send(self, to, subject, html_body, text_body=None):
        """Envia un correo. Devuelve False si no se pudo, sin lanzar excepciones.

        Un servidor SMTP caido o una clave vencida no pueden tumbar la accion
        que envia el correo: antes, un fallo aqui dejaba el checkout en error
        500 y el pedido del cliente no se guardaba.
        """
        if not current_app.config.get("MAIL_USERNAME"):
            current_app.logger.info("[email simulado] Para: %s | Asunto: %s", to, subject)
            return True
        try:
            msg = Message(subject=subject, recipients=[to], html=html_body, body=text_body or "")
            mail.send(msg)
            return True
        except Exception as e:  # noqa: BLE001 - ningun fallo de correo detiene la operacion
            current_app.logger.warning("No se pudo enviar el correo a %s (%s): %s", to, subject, e)
            return False
