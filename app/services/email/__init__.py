from app.services.email.base import EmailProvider
from app.services.email.smtp_provider import SMTPEmailProvider

_provider = None


def get_email_provider() -> EmailProvider:
    global _provider
    if _provider is None:
        _provider = SMTPEmailProvider()
    return _provider
