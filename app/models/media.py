from datetime import datetime, timezone

from app.extensions import db


class MediaFile(db.Model):
    """Archivo subido desde el panel (logo, fotos de productos, etc.).

    Se guarda en la base de datos —no en disco— para que funcione en hosting
    serverless (Vercel), donde el sistema de archivos es efímero y cualquier
    archivo escrito se pierde en el siguiente despliegue.
    """

    __tablename__ = "media_files"

    id = db.Column(db.String(40), primary_key=True)      # uuid hex + extensión
    content_type = db.Column(db.String(100), nullable=False, default="application/octet-stream")
    data = db.Column(db.LargeBinary, nullable=False)
    size = db.Column(db.Integer, nullable=False, default=0)
    original_name = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    @property
    def url(self):
        return f"/media/{self.id}"
