from datetime import datetime, timezone

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from app.extensions import db

ROLES = ("super_admin", "admin", "editor", "order_manager", "customer")


class User(db.Model, UserMixin):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)

    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(30))

    role = db.Column(db.String(20), nullable=False, default="customer")
    is_active_account = db.Column(db.Boolean, default=True, nullable=False)
    is_blocked = db.Column(db.Boolean, default=False, nullable=False)

    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    addresses = db.relationship("Address", backref="user", cascade="all, delete-orphan")
    orders = db.relationship("Order", backref="user")
    favorites = db.relationship("Favorite", backref="user", cascade="all, delete-orphan")

    def set_password(self, raw_password):
        self.password_hash = generate_password_hash(raw_password)

    def check_password(self, raw_password):
        return check_password_hash(self.password_hash, raw_password)

    @property
    def huella_sesion(self):
        """Trozo del hash que identifica la contraseña vigente.

        No permite deducir la contraseña: es un fragmento de un hash que ya es
        irreversible. Sirve para saber si una sesion se abrio antes o despues
        del ultimo cambio de contraseña.
        """
        return (self.password_hash or "")[-16:]

    def get_id(self):
        """Identidad que se guarda en la cookie de sesion.

        Al llevar la huella de la contraseña, cambiarla deja sin valor todas
        las sesiones abiertas antes: quien hubiera entrado con la contraseña
        anterior (en otro equipo, o alguien que la hubiera robado) pierde el
        acceso en ese mismo momento.
        """
        return f"{self.id}|{self.huella_sesion}"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    @property
    def is_active(self):
        return self.is_active_account and not self.is_blocked

    def has_role(self, *roles):
        return self.role in roles

    @property
    def total_orders(self):
        return len(self.orders)

    @property
    def total_spent(self):
        return sum(o.total for o in self.orders if o.status not in ("cancelado",))

    def __repr__(self):
        return f"<User {self.email} ({self.role})>"


class Address(db.Model):
    __tablename__ = "addresses"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    label = db.Column(db.String(50), default="Casa")
    recipient_name = db.Column(db.String(150))
    line1 = db.Column(db.String(255), nullable=False)
    line2 = db.Column(db.String(255))
    city = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(30))
    notes = db.Column(db.String(255))
    is_default = db.Column(db.Boolean, default=False)
