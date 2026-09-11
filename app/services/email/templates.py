def _wrapper(inner_html):
    return f"""
    <div style="font-family:Arial,sans-serif; background:#FFFDF8; padding:32px;">
      <div style="max-width:520px; margin:0 auto; background:#ffffff; border-radius:16px; overflow:hidden; border:1px solid #F0DCE3;">
        <div style="background:#8A6A3A; padding:20px 28px;">
          <span style="color:#FFFDF8; font-size:18px; font-weight:bold;">Dígalo con Flores</span>
        </div>
        <div style="padding:28px;">
          {inner_html}
        </div>
        <div style="padding:16px 28px; background:#FEF8F5; color:#9A8D80; font-size:12px;">
          © Dígalo con Flores — este es un correo automático.
        </div>
      </div>
    </div>
    """


def order_confirmation_email(order):
    items_html = "".join(
        f"<tr><td style='padding:6px 0;'>{i.product_name} x{i.quantity}</td>"
        f"<td style='padding:6px 0; text-align:right;'>${i.line_total:,.0f}</td></tr>"
        for i in order.items
    )
    inner = f"""
      <h2 style="color:#3A332C; margin-top:0;">¡Gracias por tu pedido!</h2>
      <p style="color:#6B6058;">Tu pedido <strong>{order.number}</strong> fue recibido y está <strong>{order.status_label.lower()}</strong>.</p>
      <table style="width:100%; border-collapse:collapse; margin:16px 0;">{items_html}</table>
      <p style="color:#3A332C; font-size:16px;"><strong>Total: ${order.total:,.0f}</strong></p>
      <p style="color:#6B6058; font-size:13px;">Te avisaremos por email cuando el estado de tu pedido cambie.</p>
    """
    return _wrapper(inner)


def admin_new_order_email(order, panel_url=None):
    """Aviso para la floristeria. `panel_url` es el enlace directo al pedido."""
    items_html = "".join(
        f"<tr><td style='padding:6px 0;'>{i.product_name} x{i.quantity}</td>"
        f"<td style='padding:6px 0; text-align:right;'>${i.line_total:,.0f}</td></tr>"
        for i in order.items
    )

    def fila(etiqueta, valor):
        if not valor:
            return ""
        return (
            f"<tr><td style='padding:4px 0; color:#9A8D80; font-size:13px; width:38%;'>{etiqueta}</td>"
            f"<td style='padding:4px 0; color:#3A332C; font-size:13px;'>{valor}</td></tr>"
        )

    fecha = order.delivery_date.strftime("%d/%m/%Y") if order.delivery_date else ""
    if fecha and order.delivery_time:
        fecha = f"{fecha} · {order.delivery_time}"

    detalles = (
        fila("Cliente", order.customer_name)
        + fila("Teléfono", order.customer_phone)
        + fila("Email", order.customer_email)
        + fila("Destinatario", order.recipient_name)
        + fila("Entrega", order.delivery_address)
        + fila("Fecha", fecha)
        + fila("Dedicatoria", order.dedication_message)
    )

    boton = ""
    if panel_url:
        boton = f"""
      <table role="presentation" style="margin:24px 0;"><tr><td style="background:#8A6A3A; border-radius:999px;">
        <a href="{panel_url}" style="display:inline-block; padding:14px 30px; color:#FFFDF8; font-size:15px; font-weight:bold; text-decoration:none;">
          Ver y recibir el pedido
        </a>
      </td></tr></table>
      <p style="color:#9A8D80; font-size:12px;">Si el botón no funciona, copia este enlace: {panel_url}</p>
    """

    inner = f"""
      <h2 style="color:#3A332C; margin-top:0;">🌸 ¡Nuevo pedido recibido!</h2>
      <p style="color:#6B6058;">Pedido <strong>{order.number}</strong> por <strong>${order.total:,.0f}</strong>.</p>
      <table style="width:100%; border-collapse:collapse; margin:16px 0;">{detalles}</table>
      <table style="width:100%; border-collapse:collapse; margin:16px 0; border-top:1px solid #F0DCE3;">{items_html}</table>
      <p style="color:#3A332C; font-size:16px;"><strong>Total: ${order.total:,.0f}</strong></p>
      {boton}
    """
    return _wrapper(inner)


def order_status_update_email(order):
    inner = f"""
      <h2 style="color:#3A332C; margin-top:0;">Actualización de tu pedido {order.number}</h2>
      <p style="color:#6B6058;">Tu pedido ahora está: <strong style="color:#8A6A3A;">{order.status_label}</strong></p>
    """
    return _wrapper(inner)


def welcome_subscriber_email():
    inner = """
      <h2 style="color:#3A332C; margin-top:0;">¡Bienvenido/a a nuestra comunidad!</h2>
      <p style="color:#6B6058;">Ya estás suscrito/a para recibir flores, promociones y sorpresas de Dígalo con Flores.</p>
    """
    return _wrapper(inner)
