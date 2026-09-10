from abc import ABC, abstractmethod


class EmailProvider(ABC):
    """Interfaz para el envío de emails transaccionales y de campañas.

    Cambiar de proveedor (SMTP genérico, SendGrid, etc.) solo requiere una
    nueva implementación de esta interfaz — el resto de la app llama
    siempre a get_email_provider().
    """

    @abstractmethod
    def send(self, to, subject, html_body, text_body=None):
        raise NotImplementedError

    def send_bulk(self, recipients, subject, html_body, text_body=None):
        sent = 0
        for to in recipients:
            try:
                self.send(to, subject, html_body, text_body)
                sent += 1
            except Exception:
                continue
        return sent
