from flask import render_template, request

from app.blueprints.admin import bp
from app.models.audit import AuditLog

POR_PAGINA = 50


@bp.route("/auditoria")
def audit_log():
    """Historial de acciones del panel y eventos de cuenta.

    Solo lo ve el super administrador: dice quien hizo que y desde que IP.
    """
    categoria = request.args.get("categoria", "")
    page = request.args.get("page", 1, type=int)

    query = AuditLog.query
    if categoria:
        query = query.filter_by(categoria=categoria)

    page_obj = query.order_by(AuditLog.created_at.desc()).paginate(
        page=page, per_page=POR_PAGINA, error_out=False
    )
    return render_template(
        "admin/audit/list.html",
        eventos=page_obj.items,
        page_obj=page_obj,
        categoria=categoria,
    )
