"""Envío de mensajes por WhatsApp a través de la API oficial de Meta (Cloud API).

Se usa para avisarle a la floristería cuando entra un pedido nuevo. Si las
credenciales no están configuradas, `send_whatsapp` no hace nada y lo deja
anotado en el log: la tienda sigue funcionando igual, solo que sin ese aviso.

Variables de entorno necesarias:

    WHATSAPP_TOKEN      Token de acceso permanente de la app de Meta
    WHATSAPP_PHONE_ID   ID del número remitente (lo da Meta, no es el número)
    WHATSAPP_TO         Número que recibe el aviso, con indicativo: 573001234567

Opcional:

    WHATSAPP_TEMPLATE   Nombre de una plantilla aprobada. Meta solo permite
                        mensajes de texto libre dentro de las 24 horas
                        siguientes a un mensaje del destinatario; fuera de esa
                        ventana hay que usar una plantilla. Si se define, se
                        envía la plantilla con los parámetros de cuerpo que
                        reciba `send_whatsapp`.
    WHATSAPP_LANG       Idioma de la plantilla (por defecto "es").
"""
import requests
from flask import current_app

API_VERSION = "v21.0"
TIMEOUT = 8


def _config():
    cfg = current_app.config
    return (
        cfg.get("WHATSAPP_TOKEN"),
        cfg.get("WHATSAPP_PHONE_ID"),
        cfg.get("WHATSAPP_TO"),
    )


def is_configured():
    return all(_config())


def send_whatsapp(texto, parametros_plantilla=None):
    """Envía un mensaje al número de la floristería.

    Devuelve True si Meta lo aceptó. Nunca lanza excepciones: un fallo de red o
    un token vencido no pueden tumbar el pedido de un cliente.
    """
    token, phone_id, destino = _config()
    if not all((token, phone_id, destino)):
        current_app.logger.info("[whatsapp sin configurar] %s", texto)
        return False

    plantilla = current_app.config.get("WHATSAPP_TEMPLATE")
    if plantilla:
        idioma = current_app.config.get("WHATSAPP_LANG", "es")
        cuerpo = {
            "messaging_product": "whatsapp",
            "to": destino,
            "type": "template",
            "template": {
                "name": plantilla,
                "language": {"code": idioma},
                "components": [{
                    "type": "body",
                    "parameters": [{"type": "text", "text": str(p)} for p in (parametros_plantilla or [])],
                }],
            },
        }
    else:
        cuerpo = {
            "messaging_product": "whatsapp",
            "to": destino,
            "type": "text",
            "text": {"preview_url": True, "body": texto},
        }

    try:
        respuesta = requests.post(
            f"https://graph.facebook.com/{API_VERSION}/{phone_id}/messages",
            json=cuerpo,
            headers={"Authorization": f"Bearer {token}"},
            timeout=TIMEOUT,
        )
        if respuesta.status_code >= 400:
            current_app.logger.warning(
                "WhatsApp rechazo el mensaje (%s): %s", respuesta.status_code, respuesta.text[:300]
            )
            return False
        return True
    except requests.RequestException as e:
        current_app.logger.warning("No se pudo enviar el WhatsApp: %s", e)
        return False
