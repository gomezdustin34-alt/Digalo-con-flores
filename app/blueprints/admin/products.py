from flask import render_template, request, redirect, url_for, flash

from app.blueprints.admin import bp
from app.blueprints.admin.forms import ProductForm
from app.extensions import db
from app.models.product import Product, ProductImage
from app.models.category import Category
from app.models.favorite import Favorite
from app.models.order import OrderItem
from app.utils.helpers import unique_slug
from app.utils.uploads import save_upload


def _populate_choices(form):
    form.category_id.choices = [(c.id, c.name) for c in Category.query.order_by(Category.name).all()]


def _sku_valido(form, excluir_id=None):
    """Normaliza el SKU y comprueba que no este repetido.

    El SKU es unico en la base de datos. El formulario enviaba "" cuando se
    dejaba vacio, asi que el segundo producto sin SKU chocaba con el primero y
    el panel mostraba un error 500. Vacio se guarda como NULL, que no choca.
    """
    sku = (form.sku.data or "").strip() or None
    form.sku.data = sku
    if sku is None:
        return True
    query = Product.query.filter_by(sku=sku)
    if excluir_id is not None:
        query = query.filter(Product.id != excluir_id)
    if query.first() is not None:
        flash(f"Ya existe otro producto con el SKU {sku}.", "danger")
        return False
    return True


@bp.route("/productos")
def products_list():
    q = request.args.get("q", "").strip()
    query = Product.query
    if q:
        query = query.filter(Product.name.ilike(f"%{q}%"))
    products = query.order_by(Product.created_at.desc()).all()
    return render_template("admin/products/list.html", products=products, q=q)


@bp.route("/productos/nuevo", methods=["GET", "POST"])
def product_new():
    form = ProductForm()
    _populate_choices(form)

    if form.validate_on_submit() and _sku_valido(form):
        product = Product(slug=unique_slug(Product, form.name.data))
        form.populate_obj(product)
        product.slug = unique_slug(Product, form.name.data)
        db.session.add(product)
        db.session.flush()

        image_url = save_upload(form.image.data, "products")
        if image_url:
            db.session.add(ProductImage(product_id=product.id, url=image_url, sort_order=0))

        db.session.commit()
        flash("Producto creado.", "success")
        return redirect(url_for("admin.products_list"))

    return render_template("admin/products/form.html", form=form, product=None)


@bp.route("/productos/<int:product_id>/editar", methods=["GET", "POST"])
def product_edit(product_id):
    product = Product.query.get_or_404(product_id)
    form = ProductForm(obj=product)
    _populate_choices(form)

    if form.validate_on_submit() and _sku_valido(form, excluir_id=product.id):
        form.populate_obj(product)
        image_url = save_upload(form.image.data, "products")
        if image_url:
            db.session.add(ProductImage(product_id=product.id, url=image_url, sort_order=len(product.images)))
        db.session.commit()
        flash("Producto actualizado.", "success")
        return redirect(url_for("admin.products_list"))

    return render_template("admin/products/form.html", form=form, product=product)


@bp.route("/productos/<int:product_id>/eliminar", methods=["POST"])
def product_delete(product_id):
    product = Product.query.get_or_404(product_id)
    # Los pedidos guardan el nombre y el precio del producto, asi que siguen
    # completos sin el: solo se suelta el enlace. Los favoritos si se borran.
    # Sin esto la base de datos rechazaba borrar un producto ya vendido o
    # marcado como favorito, y el panel mostraba un error 500.
    OrderItem.query.filter_by(product_id=product.id).update({"product_id": None})
    Favorite.query.filter_by(product_id=product.id).delete()
    db.session.delete(product)
    db.session.commit()
    flash("Producto eliminado.", "info")
    return redirect(url_for("admin.products_list"))


@bp.route("/productos/<int:product_id>/imagen/<int:image_id>/eliminar", methods=["POST"])
def product_image_delete(product_id, image_id):
    imagen = ProductImage.query.filter_by(id=image_id, product_id=product_id).first_or_404()
    db.session.delete(imagen)
    db.session.commit()
    flash("Imagen eliminada.", "info")
    return redirect(url_for("admin.product_edit", product_id=product_id))


@bp.route("/productos/<int:product_id>/alternar-publicado", methods=["POST"])
def product_toggle_active(product_id):
    product = Product.query.get_or_404(product_id)
    product.is_active = not product.is_active
    db.session.commit()
    return redirect(request.referrer or url_for("admin.products_list"))
