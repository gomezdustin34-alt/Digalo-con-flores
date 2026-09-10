import urllib.parse

from app.utils.helpers import get_setting, format_currency


def store_whatsapp_number():
    """Solo dígitos, con código de país, listo para wa.me (sin '+' ni espacios)."""
    raw = get_setting("whatsapp", "")
    return "".join(ch for ch in raw if ch.isdigit())


def build_order_message(order):
    currency = get_setting("currency", "COP")
    lines = [f"🌸 *Nuevo pedido {order.number}*", ""]
    lines.append(f"*Cliente:* {order.customer_name}")
    if order.customer_phone:
        lines.append(f"*Teléfono:* {order.customer_phone}")
    lines.append(f"*Email:* {order.customer_email}")
    lines.append("")
    lines.append("*Productos:*")
    for item in order.items:
        detail = item.product_name
        if item.variation_label:
            detail += f" ({item.variation_label})"
        lines.append(f"- {detail} x{item.quantity} — {format_currency(item.line_total, currency)}")
        if item.recipient_name:
            lines.append(f"  Para: {item.recipient_name}")
        if item.dedication_message:
            lines.append(f"  Dedicatoria: \"{item.dedication_message}\"")
    lines.append("")
    if order.discount_total:
        lines.append(f"*Descuento:* -{format_currency(order.discount_total, currency)}")
    lines.append(f"*Envío:* {format_currency(order.shipping_total, currency)}")
    lines.append(f"*Total:* {format_currency(order.total, currency)}")
    lines.append("")
    lines.append(f"*Entrega:* {order.delivery_address or '—'}")
    if order.delivery_date:
        when = order.delivery_date.strftime("%d/%m/%Y")
        if order.delivery_time:
            when += f" — {order.delivery_time}"
        lines.append(f"*Fecha de entrega:* {when}")
    if order.dedication_message:
        lines.append(f"*Dedicatoria general:* \"{order.dedication_message}\"")
    lines.append("")
    lines.append("Quedo atento/a para coordinar el pago y la entrega. 🌷")
    return "\n".join(lines)


def build_whatsapp_url(order):
    number = store_whatsapp_number()
    message = build_order_message(order)
    return f"https://wa.me/{number}?text={urllib.parse.quote(message)}"
