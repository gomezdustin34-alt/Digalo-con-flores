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

EXTENSIONES_IMAGEN = {"jpg", "jpeg", "png", "webp", "gif"}

# Formatos que aceptamos, identificados por lo que Pillow encuentra DENTRO del
# archivo, no por como se llame. Se excluye SVG a proposito: es XML y puede
# llevar scripts, asi que un SVG servido desde nuestro dominio seria una via de
# XSS almacenado.
FORMATOS_PERMITIDOS = {
    "JPEG": ("jpg", "image/jpeg"),
    "PNG": ("png", "image/png"),
    "WEBP": ("webp", "image/webp"),
    "GIF": ("gif", "image/gif"),
}

TIPOS = {
    "jpg": "image/jpeg", "jpeg": "image/jpeg", "png": "image/png",
    "webp": "image/webp", "gif": "image/gif",
}

# Tope por archivo, ademas del limite global de la peticion.
MAX_BYTES = 6 * 1024 * 1024


def _identificar(contenido):
    """Averigua que hay realmente dentro del archivo.

    Devuelve (extension, tipo_mime) o None si no es una imagen de las que
    aceptamos. No se mira la extension del nombre: un .jpg puede contener
    cualquier cosa.
    """
    try:
        from PIL import Image
    except ImportError:  # pragma: no cover - Pillow esta en requirements
        return None
    try:
        img = Image.open(io.BytesIO(contenido))
        img.verify()  # comprueba que el contenido es una imagen integra
        formato = (img.format or "").upper()
    except Exception:
        return None
    return FORMATOS_PERMITIDOS.get(formato)


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

    contenido = file_storage.read()
    if not contenido or len(contenido) > MAX_BYTES:
        return None

    # El tipo sale del contenido, nunca del nombre que envio el navegador.
    identificado = _identificar(contenido)
    if identificado is None:
        return None
    extension, _mime = identificado

    contenido, extension = _optimizar(contenido, extension)

    # El identificador se genera aqui: el nombre original solo se guarda como
    # dato informativo y nunca se usa como ruta ni como URL.
    archivo = MediaFile(
        id=f"{uuid.uuid4().hex}.{extension}",
        content_type=TIPOS[extension],
        data=contenido,
        size=len(contenido),
        original_name=nombre_seguro[:255],
    )
    db.session.add(archivo)
    db.session.flush()
    return archivo.url
