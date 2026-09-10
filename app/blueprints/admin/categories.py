from flask import render_template, request, redirect, url_for, flash

from app.blueprints.admin import bp
from app.blueprints.admin.forms import CategoryForm
from app.extensions import db
from app.models.category import Category
from app.utils.helpers import unique_slug
from app.utils.uploads import save_upload


@bp.route("/categorias")
def categories_list():
    categories = Category.query.order_by(Category.sort_order).all()
    return render_template("admin/categories/list.html", categories=categories)


@bp.route("/categorias/nueva", methods=["GET", "POST"])
def category_new():
    form = CategoryForm()
    if form.validate_on_submit():
        category = Category(slug=unique_slug(Category, form.name.data))
        form.populate_obj(category)
        category.slug = unique_slug(Category, form.name.data)
        image_url = save_upload(form.image.data, "categories")
        if image_url:
            category.image_url = image_url
        db.session.add(category)
        db.session.commit()
        flash("Categoría creada.", "success")
        return redirect(url_for("admin.categories_list"))
    return render_template("admin/categories/form.html", form=form, category=None)


@bp.route("/categorias/<int:category_id>/editar", methods=["GET", "POST"])
def category_edit(category_id):
    category = Category.query.get_or_404(category_id)
    form = CategoryForm(obj=category)
    if form.validate_on_submit():
        form.populate_obj(category)
        image_url = save_upload(form.image.data, "categories")
        if image_url:
            category.image_url = image_url
        db.session.commit()
        flash("Categoría actualizada.", "success")
        return redirect(url_for("admin.categories_list"))
    return render_template("admin/categories/form.html", form=form, category=category)


@bp.route("/categorias/<int:category_id>/eliminar", methods=["POST"])
def category_delete(category_id):
    category = Category.query.get_or_404(category_id)
    if category.products.count() > 0:
        flash("No puedes eliminar una categoría con productos asociados. Desactívala en su lugar.", "danger")
    else:
        db.session.delete(category)
        db.session.commit()
        flash("Categoría eliminada.", "info")
    return redirect(url_for("admin.categories_list"))


@bp.route("/categorias/<int:category_id>/mover/<direction>", methods=["POST"])
def category_move(category_id, direction):
    categories = Category.query.order_by(Category.sort_order).all()
    ids = [c.id for c in categories]
    if category_id not in ids:
        return redirect(url_for("admin.categories_list"))

    index = ids.index(category_id)
    swap_with = index - 1 if direction == "up" else index + 1
    if 0 <= swap_with < len(categories):
        categories[index].sort_order, categories[swap_with].sort_order = (
            categories[swap_with].sort_order,
            categories[index].sort_order,
        )
        db.session.commit()
    return redirect(url_for("admin.categories_list"))
