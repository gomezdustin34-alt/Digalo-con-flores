from flask import render_template, request, redirect, url_for, flash

from app.blueprints.admin import bp
from app.extensions import db
from app.models.content import SiteSection
from app.utils.content import get_content, set_content, clear_content_cache
from app.utils.uploads import save_upload


HERO_FIELDS = ["hero_eyebrow", "hero_title", "hero_script", "hero_description", "hero_cta_primary", "hero_cta_secondary"]
ABOUT_FIELDS = ["about_title", "about_text"]
FOOTER_FIELDS = ["footer_text"]


@bp.route("/contenido/inicio/quitar-imagen", methods=["POST"])
def content_home_remove_image():
    set_content("hero_image", "", value_type="image", section="hero")
    db.session.commit()
    clear_content_cache()
    flash("Imagen del inicio restaurada a la de por defecto.", "info")
    return redirect(url_for("admin.content_home"))


@bp.route("/contenido/inicio", methods=["GET", "POST"])
def content_home():
    if request.method == "POST":
        for field in HERO_FIELDS:
            set_content(field, request.form.get(field, ""), section="hero")
        image_url = save_upload(request.files.get("hero_image"), "content")
        if image_url:
            set_content("hero_image", image_url, value_type="image", section="hero")
        db.session.commit()
        clear_content_cache()
        flash("Contenido del inicio actualizado.", "success")
        return redirect(url_for("admin.content_home"))

    values = {field: get_content(field) for field in HERO_FIELDS}
    values["hero_image"] = get_content("hero_image")
    return render_template("admin/content/home.html", values=values)


@bp.route("/contenido/nosotros", methods=["GET", "POST"])
def content_about():
    if request.method == "POST":
        for field in ABOUT_FIELDS:
            set_content(field, request.form.get(field, ""), section="about")
        image_url = save_upload(request.files.get("about_image"), "content")
        if image_url:
            set_content("about_image", image_url, value_type="image", section="about")
        db.session.commit()
        clear_content_cache()
        flash("Contenido de Nosotros actualizado.", "success")
        return redirect(url_for("admin.content_about"))

    values = {field: get_content(field) for field in ABOUT_FIELDS}
    values["about_image"] = get_content("about_image")
    return render_template("admin/content/about.html", values=values)


@bp.route("/contenido/footer", methods=["GET", "POST"])
def content_footer():
    if request.method == "POST":
        for field in FOOTER_FIELDS:
            set_content(field, request.form.get(field, ""), section="footer")
        db.session.commit()
        clear_content_cache()
        flash("Footer actualizado.", "success")
        return redirect(url_for("admin.content_footer"))

    values = {field: get_content(field) for field in FOOTER_FIELDS}
    return render_template("admin/content/footer.html", values=values)


@bp.route("/contenido/secciones", methods=["GET", "POST"])
def content_sections():
    if request.method == "POST":
        for section in SiteSection.query.all():
            section.is_visible = request.form.get(f"visible_{section.key}") == "on"
        db.session.commit()
        clear_content_cache()
        flash("Secciones actualizadas.", "success")
        return redirect(url_for("admin.content_sections"))

    sections = SiteSection.query.order_by(SiteSection.sort_order).all()
    return render_template("admin/content/sections.html", sections=sections)
