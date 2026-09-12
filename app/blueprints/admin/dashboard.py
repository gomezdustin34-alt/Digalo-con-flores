from datetime import datetime, timedelta, timezone

from flask import render_template
from sqlalchemy import func

from app.blueprints.admin import bp
from app.extensions import db
from app.models.order import Order
from app.models.product import Product
from app.models.user import User
from app.models.subscriber import Subscriber
from app.utils.fechas import ahora as ahora_local, hoy as hoy_local, inicio_del_dia, inicio_del_mes


# Medidas del grafico de ventas, en unidades del viewBox del SVG.
ANCHO, ALTO, MARGEN_X, MARGEN_ARRIBA, MARGEN_ABAJO = 700, 200, 34, 16, 26


def _puntos_del_grafico(etiquetas, valores):
    """Convierte la serie de ventas en coordenadas listas para dibujar.

    Se calcula aqui y no en el navegador para que el panel no dependa de
    ninguna descarga externa: el grafico llega ya dibujado en el HTML.
    """
    maximo = max(valores) if valores else 0
    util_ancho = ANCHO - MARGEN_X * 2
    util_alto = ALTO - MARGEN_ARRIBA - MARGEN_ABAJO
    pasos = max(len(valores) - 1, 1)

    puntos = []
    for i, (etiqueta, valor) in enumerate(zip(etiquetas, valores)):
        x = MARGEN_X + (util_ancho * i / pasos)
        # Sin ventas todavia: la linea descansa en la base.
        y = ALTO - MARGEN_ABAJO - (util_alto * (valor / maximo) if maximo else 0)
        puntos.append({"etiqueta": etiqueta, "valor": valor, "x": round(x, 1), "y": round(y, 1)})

    return {
        "puntos": puntos,
        "maximo": maximo,
        "linea": " ".join(f"{p['x']},{p['y']}" for p in puntos),
        "area": (
            f"M {puntos[0]['x']},{ALTO - MARGEN_ABAJO} "
            + " ".join(f"L {p['x']},{p['y']}" for p in puntos)
            + f" L {puntos[-1]['x']},{ALTO - MARGEN_ABAJO} Z"
        ) if puntos else "",
        "base": ALTO - MARGEN_ABAJO,
        "ancho": ANCHO,
        "alto": ALTO,
    }


@bp.route("/")
def dashboard():
    # Los cortes de dia y de mes son los de la floristeria, no los del servidor
    now = ahora_local()
    today_start = inicio_del_dia()
    month_start = inicio_del_mes()

    total_sales = db.session.query(func.coalesce(func.sum(Order.total), 0)).filter(Order.status != "cancelado").scalar()
    sales_today = db.session.query(func.coalesce(func.sum(Order.total), 0)).filter(
        Order.status != "cancelado", Order.created_at >= today_start
    ).scalar()
    sales_month = db.session.query(func.coalesce(func.sum(Order.total), 0)).filter(
        Order.status != "cancelado", Order.created_at >= month_start
    ).scalar()

    total_orders = Order.query.count()
    total_customers = User.query.filter_by(role="customer").count()
    total_subscribers = Subscriber.query.filter_by(is_active=True).count()
    total_products = Product.query.count()
    out_of_stock = Product.query.filter(Product.stock <= 0).count()
    low_stock = Product.query.filter(Product.stock > 0, Product.stock <= Product.stock_minimo).count()

    from app.models.order import OrderItem
    best_sellers = (
        db.session.query(
            OrderItem.product_name,
            func.sum(OrderItem.quantity).label("total_qty"),
        )
        .group_by(OrderItem.product_name)
        .order_by(func.sum(OrderItem.quantity).desc())
        .limit(5)
        .all()
    )

    recent_orders = Order.query.order_by(Order.created_at.desc()).limit(6).all()
    recent_customers = User.query.filter_by(role="customer").order_by(User.created_at.desc()).limit(6).all()

    days = []
    sales_series = []
    for i in range(6, -1, -1):
        day = hoy_local() - timedelta(days=i)
        desde = inicio_del_dia(day)
        hasta = inicio_del_dia(day + timedelta(days=1))
        day_total = db.session.query(func.coalesce(func.sum(Order.total), 0)).filter(
            Order.status != "cancelado",
            Order.created_at >= desde,
            Order.created_at < hasta,
        ).scalar()
        days.append(day.strftime("%d/%m"))
        sales_series.append(float(day_total or 0))

    # El grafico se dibuja como SVG en la propia pagina: antes dependia de una
    # libreria externa cuyo archivo devolvia 404, asi que no se veia nada.
    grafico = _puntos_del_grafico(days, sales_series)

    return render_template(
        "admin/dashboard.html",
        grafico=grafico,
        total_sales=total_sales,
        sales_today=sales_today,
        sales_month=sales_month,
        total_orders=total_orders,
        total_customers=total_customers,
        total_subscribers=total_subscribers,
        total_products=total_products,
        out_of_stock=out_of_stock,
        low_stock=low_stock,
        best_sellers=best_sellers,
        recent_orders=recent_orders,
        recent_customers=recent_customers,
        chart_days=days,
        chart_sales=sales_series,
    )
