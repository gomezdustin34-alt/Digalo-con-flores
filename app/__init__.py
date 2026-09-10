from flask import Flask, render_template
from dotenv import load_dotenv

load_dotenv()

from app.config import Config
from app.extensions import db, migrate, login_manager, csrf, mail, limiter


def create_app(config_class=Config):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)
    mail.init_app(app)
    limiter.init_app(app)

    from app.models.user import User

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    from app.blueprints.storefront import bp as storefront_bp
    from app.blueprints.auth import bp as auth_bp
    from app.blueprints.cart import bp as cart_bp
    from app.blueprints.checkout import bp as checkout_bp
    from app.blueprints.account import bp as account_bp
    from app.blueprints.admin import bp as admin_bp

    app.register_blueprint(storefront_bp)
    app.register_blueprint(auth_bp, url_prefix="/cuenta")
    app.register_blueprint(cart_bp, url_prefix="/carrito")
    app.register_blueprint(checkout_bp, url_prefix="/checkout")
    app.register_blueprint(account_bp, url_prefix="/mi-cuenta")
    app.register_blueprint(admin_bp, url_prefix="/admin")

    register_context_processors(app)
    register_error_handlers(app)
    register_cli(app)

    return app


def register_context_processors(app):
    from datetime import datetime, timezone
    from flask import request, url_for
    from app.utils.helpers import format_currency, get_setting
    from app.utils.content import get_content, is_section_visible
    from app.models.category import Category
    from app.blueprints.cart.cart_service import get_cart

    def pagination_url(page):
        args = {**request.view_args, **request.args.to_dict(), "page": page}
        return url_for(request.endpoint, **args)

    def unread_notifications_count():
        from app.models.notification import Notification
        return Notification.query.filter_by(is_read=False).count()

    @app.context_processor
    def inject_globals():
        nav_categories = Category.query.filter_by(is_active=True).order_by(Category.sort_order).limit(6).all()
        cart = get_cart()
        return dict(
            format_currency=format_currency,
            get_setting=get_setting,
            get_content=get_content,
            is_section_visible=is_section_visible,
            nav_categories=nav_categories,
            cart_count=cart["count"],
            store_name=get_setting("store_name", "Dígalo con Flores"),
            now_year=datetime.now(timezone.utc).year,
            unread_notifications_count=unread_notifications_count,
            pagination_url=pagination_url,
        )


def register_error_handlers(app):
    @app.errorhandler(404)
    def not_found(e):
        return render_template("errors/404.html"), 404

    @app.errorhandler(403)
    def forbidden(e):
        return render_template("errors/403.html"), 403

    @app.errorhandler(500)
    def server_error(e):
        return render_template("errors/500.html"), 500


def register_cli(app):
    @app.cli.command("seed")
    def seed_command():
        from seed import run_seed

        run_seed()
        print("Base de datos poblada con datos de ejemplo.")
