import os
import tempfile

from flask import Flask, flash, jsonify, redirect, render_template, request, url_for
from dotenv import load_dotenv

load_dotenv()

from app.config import EN_SERVERLESS, Config
from app.extensions import db, migrate, login_manager, csrf, mail, limiter


def create_app(config_class=Config):
    # En serverless el disco de la aplicacion es de solo lectura: Flask-SQLAlchemy
    # intenta crear la carpeta "instance" al arrancar y eso tumbaria la funcion
    # entera. /tmp es lo unico escribible, asi que la instancia vive ahi.
    instance_path = os.path.join(tempfile.gettempdir(), "instance") if EN_SERVERLESS else None
    app = Flask(__name__, instance_relative_config=True, instance_path=instance_path)
    app.config.from_object(config_class)

    # Detrás del proxy de Vercel/Render: respeta el host y el esquema https
    # reales, necesarios para generar enlaces correctos (WhatsApp, emails).
    from werkzeug.middleware.proxy_fix import ProxyFix
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)
    mail.init_app(app)
    limiter.init_app(app)

    from app.models.user import User

    @login_manager.unauthorized_handler
    def no_autorizado():
        """Sin sesion iniciada.

        A una peticion AJAX hay que responderle 401: si le devolvemos el
        redirect a la pagina de login, `fetch` lo sigue en silencio, recibe
        HTML donde esperaba JSON y el boton parece no hacer nada.
        """
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify(ok=False, error="login_required", login_url=url_for("auth.login")), 401
        flash(login_manager.login_message, login_manager.login_message_category)
        return redirect(url_for("auth.login", next=request.path))

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    from app.blueprints.storefront import bp as storefront_bp
    from app.blueprints.auth import bp as auth_bp
    from app.blueprints.cart import bp as cart_bp
    from app.blueprints.checkout import bp as checkout_bp
    from app.blueprints.account import bp as account_bp
    from app.blueprints.admin import bp as admin_bp
    from app.blueprints.media import bp as media_bp

    app.register_blueprint(media_bp)
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
    from app.blueprints.cart.cart_service import cart_count

    def pagination_url(page):
        args = {**request.view_args, **request.args.to_dict(), "page": page}
        return url_for(request.endpoint, **args)

    def unread_notifications_count():
        from app.models.notification import Notification
        return Notification.query.filter_by(is_read=False).count()

    from app.utils.assets import asset_urls

    def assets(nombre):
        return asset_urls(nombre, app.static_folder)

    @app.context_processor
    def inject_globals():
        return dict(
            format_currency=format_currency,
            get_setting=get_setting,
            get_content=get_content,
            is_section_visible=is_section_visible,
            # Se lee de la sesión, sin tocar la base de datos
            cart_count=cart_count(),
            store_name=get_setting("store_name", "Dígalo con Flores"),
            now_year=datetime.now(timezone.utc).year,
            unread_notifications_count=unread_notifications_count,
            pagination_url=pagination_url,
            assets=assets,
        )


def register_error_handlers(app):
    @app.errorhandler(404)
    def not_found(e):
        return render_template("errors/404.html"), 404

    @app.errorhandler(403)
    def forbidden(e):
        return render_template("errors/403.html"), 403

    @app.errorhandler(429)
    def too_many_requests(e):
        # El limitador protege el login y la recuperacion de contrasena. Sin
        # este manejador, quien se pasaba del limite veia la pagina en blanco
        # de Flask, en ingles y sin forma de volver.
        return render_template("errors/429.html"), 429

    @app.errorhandler(500)
    def server_error(e):
        return render_template("errors/500.html"), 500


def register_cli(app):
    @app.cli.command("seed")
    def seed_command():
        from seed import run_seed

        run_seed()
        print("Base de datos poblada con datos de ejemplo.")
