from datetime import datetime, timedelta, timezone

from flask import render_template
from sqlalchemy import func

from app.blueprints.admin import bp
from app.extensions import db
from app.models.order import Order
from app.models.product import Product
from app.models.user import User
from app.models.subscriber import Subscriber


@bp.route("/")
def dashboard():
    now = datetime.now(timezone.utc)
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

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
        day = (now - timedelta(days=i)).date()
        day_total = db.session.query(func.coalesce(func.sum(Order.total), 0)).filter(
            Order.status != "cancelado",
            func.date(Order.created_at) == day.isoformat(),
        ).scalar()
        days.append(day.strftime("%d/%m"))
        sales_series.append(float(day_total or 0))

    return render_template(
        "admin/dashboard.html",
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
