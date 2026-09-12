from datetime import datetime, timezone

from app.extensions import db


class AuditLog(db.Model):
    """Rastro de quien hizo que y cuando.

    Guarda el hecho, nunca el contenido: aqui no entran contraseñas, tokens ni
    los datos del formulario, solo la accion y sobre que recurso se hizo.
    """

    __tablename__ = "audit_log"

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), index=True)

    # "admin" para acciones del panel, "seguridad" para inicios de sesion,
    # cambios de contraseña y demas eventos de cuenta.
    categoria = db.Column(db.String(20), nullable=False, default="admin", index=True)
    accion = db.Column(db.String(120), nullable=False)

    usuario_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    usuario_email = db.Column(db.String(255))  # se copia para que sobreviva al borrado del usuario
    rol = db.Column(db.String(30))

    ip = db.Column(db.String(45))  # cabe una IPv6
    metodo = db.Column(db.String(10))
    ruta = db.Column(db.String(300))
    resultado = db.Column(db.String(20))  # ok | denegado | error

    detalle = db.Column(db.String(300))

    def __repr__(self):
        return f"<AuditLog {self.categoria}:{self.accion} {self.usuario_email}>"
