from datetime import datetime, timezone

from flask import render_template, request, redirect, url_for, flash

from app.blueprints.admin import bp
from app.extensions import db
from app.models.order import Order, ORDER_STATUSES
from app.services.email import get_email_provider
from app.services.email.templates import order_status_update_email

# Cuantos pedidos se muestran por pagina en el panel.
POR_PAGINA = 25

# Al marcar un pedido asi, deja de ser trabajo pendiente y se archiva solo.
ESTADOS_TERMINADOS = ("entregado", "cancelado")


def _query_de_la_vista(vista, status):
    """La consulta que corresponde a la pestaña y al estado elegidos."""
    query = Order.query
    if vista == "activos":
        query = query.filter(Order.archived_at.is_(None))
    elif vista == "archivados":
        query = query.filter(Order.archived_at.isnot(None))
    if status:
        query = query.filter_by(status=status)
    return query


@bp.route("/pedidos")
def orders_list():
    status = request.args.get("status", "")
    vista = request.args.get("vista", "activos")  # activos | archivados | todos
    page = request.args.get("page", 1, type=int)

    page_obj = _query_de_la_vista(vista, status).order_by(Order.created_at.desc()).paginate(
        page=page, per_page=POR_PAGINA, error_out=False
    )

    return render_template(
        "admin/orders/list.html",
        orders=page_obj.items,
        page_obj=page_obj,
        status=status,
        vista=vista,
        statuses=ORDER_STATUSES,
        activos=Order.query.filter(Order.archived_at.is_(None)).count(),
        archivados=Order.query.filter(Order.archived_at.isnot(None)).count(),
        terminados_sin_archivar=Order.query.filter(
            Order.archived_at.is_(None), Order.status.in_(ESTADOS_TERMINADOS)
        ).count(),
    )


@bp.route("/pedidos/<int:order_id>")
def order_detail(order_id):
    order = Order.query.get_or_404(order_id)
    return render_template("admin/orders/detail.html", order=order, statuses=ORDER_STATUSES)


@bp.route("/pedidos/<int:order_id>/estado", methods=["POST"])
def order_update_status(order_id):
    order = Order.query.get_or_404(order_id)
    new_status = request.form.get("status")
    if new_status in ORDER_STATUSES:
        order.status = new_status

        # Al cancelar, las unidades vuelven al inventario (una sola vez).
        if new_status == "cancelado" and not order.stock_restored:
            for item in order.items:
                if item.product:
                    item.product.stock = (item.product.stock or 0) + item.quantity
            order.stock_restored = True
            flash("Pedido cancelado: las unidades volvieron al inventario.", "info")

        # Entregado o cancelado ya no es trabajo pendiente: sale de la lista.
        if new_status in ESTADOS_TERMINADOS and order.archived_at is None:
            order.archived_at = datetime.now(timezone.utc)
            flash(
                f"Pedido {order.number} archivado: ya no aparece en la lista de pendientes, "
                "pero puedes verlo en «Archivados».",
                "info",
            )
        elif new_status not in ESTADOS_TERMINADOS and order.archived_at is not None:
            # Si vuelve a un estado en curso, vuelve a la lista de trabajo.
            order.archived_at = None

        db.session.commit()
        get_email_provider().send(
            order.customer_email, f"Actualización de tu pedido {order.number}", order_status_update_email(order)
        )
        flash("Estado del pedido actualizado.", "success")
    return redirect(url_for("admin.order_detail", order_id=order.id))


@bp.route("/pedidos/<int:order_id>/archivar", methods=["POST"])
def order_archive(order_id):
    order = Order.query.get_or_404(order_id)
    order.archived_at = datetime.now(timezone.utc)
    db.session.commit()
    flash(f"Pedido {order.number} archivado.", "success")
    return redirect(request.referrer or url_for("admin.orders_list"))


@bp.route("/pedidos/<int:order_id>/restaurar", methods=["POST"])
def order_unarchive(order_id):
    order = Order.query.get_or_404(order_id)
    order.archived_at = None
    db.session.commit()
    flash(f"Pedido {order.number} devuelto a la lista.", "success")
    return redirect(request.referrer or url_for("admin.orders_list", vista="archivados"))


@bp.route("/pedidos/archivar-terminados", methods=["POST"])
def orders_archive_finished():
    """Archiva de una vez todo lo entregado o cancelado que siga en la lista."""
    pendientes = Order.query.filter(
        Order.archived_at.is_(None), Order.status.in_(ESTADOS_TERMINADOS)
    ).all()
    ahora = datetime.now(timezone.utc)
    for pedido in pendientes:
        pedido.archived_at = ahora
    db.session.commit()
    if pendientes:
        flash(f"{len(pendientes)} pedidos archivados.", "success")
    else:
        flash("No había pedidos terminados por archivar.", "info")
    return redirect(url_for("admin.orders_list"))


@bp.route("/pedidos/lote", methods=["POST"])
def orders_bulk():
    """Archiva, restaura o elimina varios pedidos marcados con las casillas."""
    accion = request.form.get("accion")
    ids = request.form.getlist("ids", type=int)

    # El destino viene del formulario: solo se acepta si es una ruta del panel,
    # para que nadie pueda convertir este boton en un salto a otro sitio.
    volver = request.form.get("volver") or ""
    if not volver.startswith("/admin/") or volver.startswith("//"):
        volver = url_for("admin.orders_list")

    # "Incluir los N de todas las páginas": la accion se aplica a todo lo que
    # cumple el filtro actual, no solo a lo que se ve en pantalla.
    if request.form.get("todos") == "1":
        pedidos = _query_de_la_vista(
            request.form.get("vista", "activos"), request.form.get("estado", "")
        ).all()
    elif ids:
        pedidos = Order.query.filter(Order.id.in_(ids)).all()
    else:
        flash("No marcaste ningún pedido.", "info")
        return redirect(volver)

    if not pedidos:
        flash("No había pedidos que coincidieran.", "info")
        return redirect(volver)

    if accion == "archivar":
        ahora = datetime.now(timezone.utc)
        cuantos = 0
        for pedido in pedidos:
            if pedido.archived_at is None:
                pedido.archived_at = ahora
                cuantos += 1
        db.session.commit()
        flash(f"{cuantos} pedidos archivados.", "success")

    elif accion == "restaurar":
        cuantos = 0
        for pedido in pedidos:
            if pedido.archived_at is not None:
                pedido.archived_at = None
                cuantos += 1
        db.session.commit()
        flash(f"{cuantos} pedidos devueltos a la lista.", "success")

    elif accion == "eliminar":
        # Solo se borra lo archivado: asi no se puede perder de un clic un
        # pedido que todavia esta en curso.
        borrados, saltados = 0, 0
        for pedido in pedidos:
            if pedido.archived_at is None:
                saltados += 1
                continue
            db.session.delete(pedido)
            borrados += 1
        db.session.commit()
        if borrados:
            flash(f"{borrados} pedidos eliminados definitivamente.", "info")
        if saltados:
            flash(f"{saltados} no se eliminaron porque siguen en curso: archívalos primero.", "danger")

    else:
        flash("Acción no reconocida.", "danger")

    return redirect(volver)


@bp.route("/pedidos/<int:order_id>/eliminar", methods=["POST"])
def order_delete(order_id):
    """Borra un pedido para siempre.

    Solo se permite sobre pedidos archivados, para que no se pueda borrar por
    error uno en curso. Un pedido es el soporte de una venta, asi que lo normal
    es archivarlo; esto queda para limpiar pruebas o pedidos falsos.
    """
    order = Order.query.get_or_404(order_id)
    if order.archived_at is None:
        flash("Solo se pueden eliminar pedidos archivados. Archívalo primero.", "danger")
        return redirect(url_for("admin.order_detail", order_id=order.id))

    numero = order.number
    db.session.delete(order)
    db.session.commit()
    flash(f"Pedido {numero} eliminado definitivamente.", "info")
    return redirect(url_for("admin.orders_list", vista="archivados"))
