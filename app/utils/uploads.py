import io
import uuid

from werkzeug.utils import secure_filename

from app.extensions import db
from app.models.media import MediaFile

# Las imágenes se redimensionan y recomprimen antes de guardarlas para que el
# sitio cargue rápido: una foto de 4 MB del celular queda en ~150 KB sin que se
# note diferencia en pantalla.
MAX_ANCHO = 1400
CALIDAD_JPEG = 82

EXTENSIONES_IMAGEN = {"jpg", "jpeg", "png", "webp", "gif", "avif"}
TIPOS = {
    "jpg": "image/jpeg", "jpeg": "image/jpeg", "png": "image/png",
    "webp": "image/webp", "gif": "image/gif", "avif": "image/avif",
    "ico": "image/x-icon", "svg": "image/svg+xml",
}


def _optimizar(contenido: bytes, extension: str):
    """Redimensiona y recomprime la imagen. Devuelve (bytes, extension)."""
    if extension not in EXTENSIONES_IMAGEN or extension == "gif":
        return contenido, extension
    try:
        from PIL import Image
    except ImportError:
        return contenido, extension

    try:
        img = Image.open(io.BytesIO(contenido))
        img.load()
    except Exception:
        return contenido, extension

    transparente = img.mode in ("RGBA", "LA", "P")

    if img.width > MAX_ANCHO:
        alto = round(img.height * (MAX_ANCHO / img.width))
        img = img.resize((MAX_ANCHO, alto), Image.LANCZOS)

    salida = io.BytesIO()
    if transparente:
        img = img.convert("RGBA")
        img.save(salida, format="PNG", optimize=True)
        nueva_ext = "png"
    else:
        img = img.convert("RGB")
        img.save(salida, format="JPEG", quality=CALIDAD_JPEG, optimize=True, progressive=True)
        nueva_ext = "jpg"

    optimizado = salida.getvalue()
    # Si la "optimización" empeoró el peso, conservamos el original
    if len(optimizado) >= len(contenido):
        return contenido, extension
    return optimizado, nueva_ext


def save_upload(file_storage, subfolder="products"):
    """Guarda el archivo en la base de datos y devuelve su URL pública.

    `subfolder` se mantiene por compatibilidad con las llamadas existentes.
    """
    if not file_storage or not getattr(file_storage, "filename", ""):
        return None

    nombre_seguro = secure_filename(file_storage.filename)
    extension = nombre_seguro.rsplit(".", 1)[-1].lower() if "." in nombre_seguro else "bin"

    contenido = file_storage.read()
    if not contenido:
        return None

    contenido, extension = _optimizar(contenido, extension)

    archivo = MediaFile(
        id=f"{uuid.uuid4().hex}.{extension}",
        content_type=TIPOS.get(extension, "application/octet-stream"),
        data=contenido,
        size=len(contenido),
        original_name=nombre_seguro[:255],
    )
    db.session.add(archivo)
    db.session.flush()
    return archivo.url
