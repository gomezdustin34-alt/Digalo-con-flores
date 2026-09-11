"""Traslada las imágenes subidas desde disco a la base de datos.

Necesario al pasar a un hosting serverless (Vercel), donde el disco es efímero.
Se ejecuta una sola vez:  python scripts/migrar_imagenes_a_bd.py
"""
import os
import sys
import uuid

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.extensions import db
from app.models.media import MediaFile
from app.models.product import ProductImage
from app.models.category import Category
from app.models.review import Testimonial
from app.models.content import Setting, WebsiteContent
from app.utils.uploads import TIPOS

app = create_app()


def migrar():
    base = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "app")
    equivalencias = {}
    migrados = 0

    def subir(url_antigua):
        """Copia un archivo de /static/uploads/... a la base de datos."""
        if not url_antigua or not url_antigua.startswith("/static/uploads/"):
            return None
        if url_antigua in equivalencias:
            return equivalencias[url_antigua]

        ruta = os.path.join(base, url_antigua.lstrip("/").replace("/", os.sep))
        if not os.path.exists(ruta):
            print(f"  ! no se encontró el archivo: {url_antigua}")
            return None

        with open(ruta, "rb") as f:
            contenido = f.read()
        extension = url_antigua.rsplit(".", 1)[-1].lower()
        archivo = MediaFile(
            id=f"{uuid.uuid4().hex}.{extension}",
            content_type=TIPOS.get(extension, "application/octet-stream"),
            data=contenido,
            size=len(contenido),
            original_name=os.path.basename(ruta),
        )
        db.session.add(archivo)
        equivalencias[url_antigua] = archivo.url
        return archivo.url

    with app.app_context():
        for img in ProductImage.query.all():
            nueva = subir(img.url)
            if nueva:
                img.url = nueva
                migrados += 1

        for cat in Category.query.all():
            nueva = subir(cat.image_url)
            if nueva:
                cat.image_url = nueva
                migrados += 1

        for t in Testimonial.query.all():
            nueva = subir(t.photo_url)
            if nueva:
                t.photo_url = nueva
                migrados += 1

        for clave in ("logo_url", "favicon_url"):
            s = Setting.query.filter_by(key=clave).first()
            if s:
                nueva = subir(s.value)
                if nueva:
                    s.value = nueva
                    migrados += 1

        for c in WebsiteContent.query.filter_by(value_type="image").all():
            nueva = subir(c.value)
            if nueva:
                c.value = nueva
                migrados += 1

        db.session.commit()

    print(f"Listo: {migrados} referencias migradas ({len(equivalencias)} archivos únicos).")


if __name__ == "__main__":
    migrar()
