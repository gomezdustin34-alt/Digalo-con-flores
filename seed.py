"""Datos de ejemplo para desarrollo: categorías, productos, usuario admin, configuración."""
from datetime import date, timedelta

from app import create_app
from app.extensions import db
from app.models.user import User
from app.models.category import Category
from app.models.product import Product, ProductImage
from app.models.coupon import Coupon
from app.models.review import Testimonial
from app.models.content import SiteSection, Setting

IMG = lambda name: f"/static/img/seed/{name}"

CATEGORIES = [
    dict(name="Rosas", slug="rosas", icon="🌹", image_url=IMG("cat-rosas.jpg")),
    dict(name="Ramos", slug="ramos", icon="💐", image_url=IMG("cat-ramos.jpg")),
    dict(name="Arreglos Florales", slug="arreglos-florales", icon="🌸", image_url=IMG("cat-arreglos.jpg")),
    dict(name="Plantas", slug="plantas", icon="🌿", image_url=IMG("cat-plantas.jpg")),
    dict(name="Cumpleaños", slug="cumpleanos", icon="🎂", image_url=IMG("prod1.jpg")),
    dict(name="Aniversarios", slug="aniversarios", icon="💍", image_url=IMG("prod3.jpg")),
    dict(name="Amor", slug="amor", icon="❤️", image_url=IMG("prod2.jpg")),
    dict(name="Ocasiones Especiales", slug="ocasiones-especiales", icon="✨", image_url=IMG("prod4.jpg")),
]

PRODUCTS = [
    dict(name="Ramo Amor Eterno", slug="ramo-amor-eterno", category="rosas", price=120000, compare_at_price=150000,
         image="prod1.jpg", is_featured=True, is_new=True, short_description="Rosas rojas y peonías en un ramo romántico.",
         description="Un ramo de rosas rojas premium combinadas con peonías rosa pálido, envuelto a mano en papel kraft y listón de seda.",
         tags="rosas,romantico,aniversario"),
    dict(name="Bouquet Primavera Rosa", slug="bouquet-primavera-rosa", category="ramos", price=76000, compare_at_price=95000,
         image="prod2.jpg", is_new=True, short_description="Tulipanes y astromelias en tonos rosa y blanco.",
         description="Una explosión de color primaveral con tulipanes, astromelias y flor de llenado, perfecta para alegrar cualquier día.",
         tags="ramos,primavera,cumpleanos"),
    dict(name="Caja Elegancia Blanca", slug="caja-elegancia-blanca", category="arreglos-florales", price=145000,
         image="prod3.jpg", is_featured=True, short_description="Rosas blancas y eucalipto en caja de lujo.",
         description="Rosas blancas frescas junto a follaje de eucalipto, presentadas en una elegante caja de sombrero.",
         tags="arreglos,elegante,boda"),
    dict(name="Arreglo Jardín Secreto", slug="arreglo-jardin-secreto", category="arreglos-florales", price=168000,
         image="prod4.jpg", short_description="Mix de flores de temporada en base de cerámica.",
         description="Una mezcla exuberante de flores de temporada en una base de cerámica artesanal, ideal para decorar cualquier espacio.",
         tags="arreglos,premium,decoracion"),
    dict(name="Docena de Rosas Rojas", slug="docena-rosas-rojas", category="rosas", price=98000,
         image="cat-rosas.jpg", is_featured=True, short_description="12 rosas rojas de tallo largo.",
         description="El clásico ramo de 12 rosas rojas de tallo largo, perfecto para decir 'te amo'.",
         tags="rosas,amor,clasico"),
    dict(name="Ramo Campestre", slug="ramo-campestre", category="ramos", price=88000,
         image="cat-ramos.jpg", short_description="Flores silvestres en estilo campestre.",
         description="Un ramo relajado con flores silvestres de temporada, ideal para regalar sin ocasión especial.",
         tags="ramos,silvestre,natural"),
    dict(name="Arreglo Atardecer", slug="arreglo-atardecer", category="arreglos-florales", price=132000,
         image="cat-arreglos.jpg", is_new=True, short_description="Tonos cálidos coral y durazno.",
         description="Un arreglo en tonos cálidos —coral, durazno y amarillo— que evoca los colores de un atardecer.",
         tags="arreglos,calido,cumpleanos"),
    dict(name="Suculenta en Maceta", slug="suculenta-en-maceta", category="plantas", price=54000,
         image="cat-plantas.jpg", short_description="Suculenta en maceta de cerámica.",
         description="Una suculenta de bajo mantenimiento en maceta de cerámica blanca, perfecta como detalle duradero.",
         tags="plantas,decoracion,oficina", allow_dedication=False, allow_recipient_name=False),
    dict(name="Ramo Aniversario Dorado", slug="ramo-aniversario-dorado", category="aniversarios", price=175000, compare_at_price=210000,
         image="prod1.jpg", is_featured=True, short_description="Rosas y flores doradas para celebrar el amor.",
         description="Rosas premium combinadas con follaje dorado, especialmente diseñado para aniversarios memorables.",
         tags="aniversario,amor,premium"),
    dict(name="Detalle Cumpleaños Feliz", slug="detalle-cumpleanos-feliz", category="cumpleanos", price=69000,
         image="prod2.jpg", is_new=True, short_description="Ramo alegre y colorido para cumpleaños.",
         description="Flores de colores vibrantes que transmiten alegría, ideales para celebrar un cumpleaños especial.",
         tags="cumpleanos,colorido,alegre"),
]

TESTIMONIALS = [
    dict(name="Camila Rodríguez", photo="testi1.jpg", rating=5,
         comment="El ramo llegó impecable y justo a la hora prometida. La calidad de las flores superó lo que vi en la foto."),
    dict(name="Juan Pablo Díaz", photo="testi2.jpg", rating=5,
         comment="Pedí la personalización con dedicatoria y quedó perfecta. Se nota el cuidado en cada detalle."),
    dict(name="Valentina Gómez", photo="testi3.jpg", rating=5,
         comment="Mi florería de confianza desde hace un año. El sitio es facilísimo de usar y siempre llega a tiempo."),
]

SITE_SECTIONS = [
    dict(key="newsletter", label="Newsletter en el footer", sort_order=1),
    dict(key="testimonios", label="Testimonios en 'Nosotros'", sort_order=2),
    dict(key="promociones", label="Banda de promoción destacada", sort_order=3),
]

SETTINGS = {
    "store_name": "Dígalo con Flores",
    "contact_email": "hola@digaloconflores.com",
    "contact_phone": "+57 300 123 4567",
    "whatsapp": "+57 300 123 4567",
    "address": "Calle 10 # 25-30, Bogotá",
    "hours": "Lun-Sáb · 8:00-19:00",
    "currency": "COP",
    "shipping_flat_rate": "12000",
    "free_shipping_threshold": "150000",
}


def run_seed():
    app = create_app()
    with app.app_context():
        db.create_all()

        if not User.query.filter_by(email="admin@digaloconflores.com").first():
            admin = User(
                first_name="Admin",
                last_name="Dígalo con Flores",
                email="admin@digaloconflores.com",
                role="super_admin",
            )
            admin.set_password("Flores2026!")
            db.session.add(admin)

        categories_by_slug = {}
        for i, cat_data in enumerate(CATEGORIES):
            cat = Category.query.filter_by(slug=cat_data["slug"]).first()
            if not cat:
                cat = Category(sort_order=i, **cat_data)
                db.session.add(cat)
            categories_by_slug[cat_data["slug"]] = cat
        db.session.flush()

        for p_data in PRODUCTS:
            if Product.query.filter_by(slug=p_data["slug"]).first():
                continue
            category = categories_by_slug[p_data.pop("category")]
            image = p_data.pop("image")
            product = Product(category_id=category.id, stock=25, sku=p_data["slug"].upper()[:20], **p_data)
            db.session.add(product)
            db.session.flush()
            db.session.add(ProductImage(product_id=product.id, url=IMG(image), sort_order=0))

        if not Coupon.query.filter_by(code="FLORES20").first():
            db.session.add(Coupon(
                code="FLORES20",
                discount_type="percent",
                discount_value=20,
                expires_at=date.today() + timedelta(days=90),
                min_purchase=50000,
                is_active=True,
            ))

        for t_data in TESTIMONIALS:
            if not Testimonial.query.filter_by(name=t_data["name"]).first():
                db.session.add(Testimonial(
                    name=t_data["name"],
                    photo_url=IMG(t_data["photo"]),
                    rating=t_data["rating"],
                    comment=t_data["comment"],
                    status="aprobado",
                ))

        for s_data in SITE_SECTIONS:
            if not SiteSection.query.filter_by(key=s_data["key"]).first():
                db.session.add(SiteSection(is_visible=True, **s_data))

        for key, value in SETTINGS.items():
            if not Setting.query.filter_by(key=key).first():
                db.session.add(Setting(key=key, value=value))

        db.session.commit()


if __name__ == "__main__":
    run_seed()
    print("Base de datos poblada con datos de ejemplo.")
    print("Usuario admin: admin@digaloconflores.com / Flores2026!")
