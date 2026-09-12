"""Avisos a la floristería cuando ocurre algo que requiere su atención.

Hoy solo hay uno: un pedido nuevo, que se avisa por correo y por WhatsApp con
un enlace directo al pedido en el panel.

Regla de oro de este módulo: **nunca puede tumbar la operación que lo llamó**.
Si el correo o el WhatsApp fallan, el pedido del cliente ya está guardado y
debe seguir su curso; el fallo se anota en el log y nada más.
"""
from flask import current_app

from app.services.email import get_email_provider
from app.services.email.templates import admin_new_order_email
from app.services.whatsapp import send_whatsapp
from app.utils.helpers import get_setting


def admin_order_url(order):
    """URL absoluta del pedido en el panel, para abrirla desde el correo o WhatsApp."""
    base = (current_app.config.get("SITE_URL") or "").rstrip("/")
    return f"{base}/admin/pedidos/{order.id}"


def _texto_whatsapp(order):
    lineas = [
        f"🌸 *Nuevo pedido {order.number}*",
        "",
        f"Cliente: {order.customer_name}",
        f"Teléfono: {order.customer_phone or '—'}",
        f"Total: ${order.total:,.0f}",
    ]
    if order.recipient_name:
        lineas.append(f"Para: {order.recipient_name}")
    if order.delivery_address:
        lineas.append(f"Entrega: {order.delivery_address}")
    if order.delivery_notes:
        lineas.append(f"Cómo llegar: {order.delivery_notes}")
    if order.delivery_date:
        fecha = order.delivery_date.strftime("%d/%m/%Y")
        lineas.append(f"Fecha: {fecha}{' · ' + order.delivery_time if order.delivery_time else ''}")
    lineas += ["", "Ábrelo para recibirlo:", admin_order_url(order)]
    return "\n".join(lineas)


def notify_new_order(order):
    """Avisa del pedido por los canales configurados. Devuelve qué se logró enviar."""
    resultado = {"email": False, "whatsapp": False}

    # El correo de avisos puede ser distinto del que se publica en la web:
    # el publico lo ve cualquiera, este es donde la floristeria quiere que le
    # suene el telefono cuando entra un pedido.
    destino = get_setting("order_notification_email") or get_setting("contact_email")
    if destino:
        try:
            get_email_provider().send(
                destino,
                f"🌸 Nuevo pedido {order.number} — ${order.total:,.0f}",
                admin_new_order_email(order, admin_order_url(order)),
            )
            resultado["email"] = True
        except Exception as e:  # noqa: BLE001 - ningun fallo de correo detiene un pedido
            current_app.logger.warning("No se pudo avisar del pedido %s por correo: %s", order.number, e)

    try:
        resultado["whatsapp"] = send_whatsapp(
            _texto_whatsapp(order),
            parametros_plantilla=[
                order.number,
                order.customer_name,
                f"${order.total:,.0f}",
                admin_order_url(order),
            ],
        )
    except Exception as e:  # noqa: BLE001 - el servicio ya atrapa lo suyo; esto es el cinturon
        current_app.logger.warning("No se pudo avisar del pedido %s por WhatsApp: %s", order.number, e)

    return resultado
