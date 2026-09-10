from flask import Response, render_template, current_app

from app.blueprints.storefront import bp
from app.models.product import Product
from app.models.category import Category


@bp.route("/sitemap.xml")
def sitemap():
    site_url = current_app.config.get("SITE_URL", "").rstrip("/")
    static_paths = ["/", "/catalogo", "/ocasiones", "/promociones", "/nosotros", "/contacto"]
    products = Product.query.filter_by(is_active=True).all()
    categories = Category.query.filter_by(is_active=True).all()

    urls = [f"{site_url}{p}" for p in static_paths]
    urls += [f"{site_url}/producto/{p.slug}" for p in products]
    urls += [f"{site_url}/categoria/{c.slug}" for c in categories]

    xml = render_template("storefront/sitemap.xml", urls=urls)
    return Response(xml, mimetype="application/xml")


@bp.route("/robots.txt")
def robots():
    site_url = current_app.config.get("SITE_URL", "").rstrip("/")
    content = f"User-agent: *\nAllow: /\nDisallow: /admin/\nDisallow: /mi-cuenta/\nDisallow: /checkout/\nSitemap: {site_url}/sitemap.xml\n"
    return Response(content, mimetype="text/plain")
