from flask import render_template, request, redirect, url_for, flash, session
from flask_login import current_user

from app.blueprints.storefront import bp
from app.blueprints.storefront.forms import ContactForm, NewsletterForm, SeguimientoForm
from app.blueprints.storefront.product_query import filtered_products
from app.extensions import db, limiter
from app.models.category import Category
from app.models.product import Product
from app.models.contact import ContactMessage
from app.models.order import Order
from app.models.subscriber import Subscriber
from app.models.review import Testimonial
from app.models.favorite import Favorite
from app.utils.content import is_section_visible, notify
from app.services.email import get_email_provider
from app.services.email.templates import welcome_subscriber_email


@bp.route("/")
def home():
    return render_template("storefront/home.html")


@bp.route("/catalogo")
def catalog():
    page_obj = filtered_products(request.args)
    return render_template(
        "storefront/catalog.html",
        page_obj=page_obj,
        products=page_obj.items,
        category=None,
        categories=Category.query.filter_by(is_active=True).order_by(Category.sort_order).all(),
        page_title="Flores",
        breadcrumb="Flores",
    )


@bp.route("/categoria/<slug>")
def category(slug):
    category = Category.query.filter_by(slug=slug, is_active=True).first_or_404()
    page_obj = filtered_products(request.args, category=category)
    return render_template(
        "storefront/catalog.html",
        page_obj=page_obj,
        products=page_obj.items,
        category=category,
        categories=Category.query.filter_by(is_active=True).order_by(Category.sort_order).all(),
        page_title=category.name,
        breadcrumb=category.name,
    )


@bp.route("/producto/<slug>")
def product_detail(slug):
    product = Product.query.filter_by(slug=slug, is_active=True).first_or_404()
    related = (
        Product.query.filter(Product.category_id == product.category_id, Product.id != product.id, Product.is_active.is_(True))
        .limit(4)
        .all()
    )
    is_favorite = False
    if current_user.is_authenticated:
        is_favorite = Favorite.query.filter_by(user_id=current_user.id, product_id=product.id).first() is not None
    return render_template("storefront/product_detail.html", product=product, related=related, is_favorite=is_favorite)


@bp.route("/ocasiones")
def occasions():
    categories = Category.query.filter_by(is_active=True).order_by(Category.sort_order).all()
    return render_template("storefront/occasions.html", categories=categories)


@bp.route("/promociones")
def promotions():
    page_obj = filtered_products(request.args, base_query=Product.query.filter(
        Product.is_active.is_(True), Product.compare_at_price.isnot(None)
    ))
    return render_template(
        "storefront/promotions.html",
        page_obj=page_obj,
        products=page_obj.items,
        show_promo_band=is_section_visible("promociones"),
    )


@bp.route("/nosotros")
def about():
    testimonials = Testimonial.query.filter_by(status="aprobado").order_by(Testimonial.created_at.desc()).limit(6).all()
    return render_template(
        "storefront/about.html",
        testimonials=testimonials,
        show_testimonials=is_section_visible("testimonios"),
    )


@bp.route("/contacto", methods=["GET", "POST"])
@limiter.limit("6 per hour", methods=["POST"])
def contact():
    form = ContactForm()
    if form.validate_on_submit():
        msg = ContactMessage(
            name=form.name.data,
            email=form.email.data,
            phone=form.phone.data,
            subject=form.subject.data,
            message=form.message.data,
        )
        db.session.add(msg)
        notify("nuevo_mensaje", f"Nuevo mensaje de contacto de {msg.name}", link="/admin/mensajes")
        db.session.commit()
        flash("Tu mensaje fue enviado. Te responderemos pronto.", "success")
        return redirect(url_for("storefront.contact"))
    return render_template("storefront/contact.html", form=form)


# Fecha de la ultima revision de los textos legales. Actualizala cuando cambies
# el contenido de cualquiera de las paginas de abajo.
LEGAL_ACTUALIZADO = "11 de septiembre de 2026"

PAGINAS_LEGALES = {
    "privacidad": ("Politica de Privacidad y Tratamiento de Datos", "Politica de privacidad"),
    "cookies": ("Politica de Cookies", "Cookies"),
    "terminos": ("Terminos y Condiciones", "Terminos y condiciones"),
    "envios": ("Politica de Envios, Cambios y Devoluciones", "Envios y devoluciones"),
}


def _legal(pagina):
    titulo, breadcrumb = PAGINAS_LEGALES[pagina]
    return render_template(
        f"storefront/legal/{pagina}.html",
        legal_title=titulo,
        legal_breadcrumb=breadcrumb,
        legal_updated=LEGAL_ACTUALIZADO,
    )


@bp.route("/politica-de-privacidad")
def privacy():
    return _legal("privacidad")


@bp.route("/politica-de-cookies")
def cookies():
    return _legal("cookies")


@bp.route("/terminos-y-condiciones")
def terms():
    return _legal("terminos")


@bp.route("/envios-y-devoluciones")
def shipping_policy():
    return _legal("envios")


@bp.route("/mi-pedido", methods=["GET", "POST"])
@limiter.limit("20 per hour", methods=["POST"])
def track_order():
    """Consultar un pedido con el numero y el correo, sin tener cuenta.

    La mayoria de los pedidos los hacen invitados: sin esto, si cerraban la
    pestaña de la confirmacion no tenian forma de volver a ver su pedido.
    """
    form = SeguimientoForm()
    if form.validate_on_submit():
        numero = form.number.data.strip().upper()
        correo = form.email.data.strip().lower()
        order = Order.query.filter_by(number=numero).first()
        if order and (order.customer_email or "").lower() == correo:
            # Verificado numero + correo: se autoriza a este navegador a ver la
            # pagina de confirmacion de ese pedido.
            recientes = session.get("mis_pedidos", [])
            if order.number not in recientes:
                session["mis_pedidos"] = ([order.number] + recientes)[:20]
                session.modified = True
            return redirect(url_for("checkout.whatsapp_redirect", order_number=order.number))
        flash("No encontramos un pedido con ese número y ese correo. Revísalos e intenta de nuevo.", "danger")
    return render_template("storefront/track_order.html", form=form)


@bp.route("/buscar")
def search():
    page_obj = filtered_products(request.args)
    return render_template(
        "storefront/catalog.html",
        page_obj=page_obj,
        products=page_obj.items,
        category=None,
        categories=Category.query.filter_by(is_active=True).order_by(Category.sort_order).all(),
        page_title=f'Resultados para "{request.args.get("q", "")}"',
        breadcrumb="Buscar",
    )


@bp.route("/newsletter/suscribir", methods=["POST"])
@limiter.limit("10 per hour")
def newsletter_subscribe():
    form = NewsletterForm()
    if form.validate_on_submit():
        email = form.email.data.lower().strip()
        existing = Subscriber.query.filter_by(email=email).first()
        if existing:
            if not existing.is_active:
                existing.is_active = True
                existing.unsubscribed_at = None
                db.session.commit()
                flash("¡Tu suscripción fue reactivada!", "success")
            else:
                flash("Ese email ya está suscrito.", "info")
        else:
            db.session.add(Subscriber(email=email))
            notify("nueva_suscripcion", f"Nueva suscripción: {email}")
            db.session.commit()
            get_email_provider().send(email, "¡Bienvenido/a a Dígalo con Flores!", welcome_subscriber_email())
            flash("¡Gracias por suscribirte!", "success")
    else:
        flash("Ingresa un email válido.", "danger")
    return redirect(request.referrer or url_for("storefront.home"))


@bp.route("/newsletter/cancelar", methods=["POST"])
def newsletter_unsubscribe():
    email = request.form.get("email", "").lower().strip()
    sub = Subscriber.query.filter_by(email=email).first()
    if sub:
        sub.is_active = False
        from datetime import datetime, timezone
        sub.unsubscribed_at = datetime.now(timezone.utc)
        db.session.commit()
        flash("Tu suscripción fue cancelada.", "info")
    return redirect(url_for("storefront.home"))
