"""Resuelve las URLs de los recursos compilados (CSS/JS con hash)."""
import json
import os

from flask import url_for

_MANIFIESTO = None
_RUTA_MANIFIESTO = None
_MTIME = None

# Si no hay compilación (desarrollo), se sirven los archivos sueltos.
FALLBACK = {
    "tienda.css": ["css/tokens.css", "css/base.css", "css/components.css", "css/storefront.css"],
    "tienda.js": ["js/main.js", "js/cart.js"],
    "panel.css": ["css/tokens.css", "css/base.css", "css/components.css", "css/admin.css"],
    "panel.js": ["js/admin.js"],
}


def _cargar(static_folder):
    """Lee el manifiesto, releyéndolo si el archivo cambió (tras recompilar)."""
    global _MANIFIESTO, _RUTA_MANIFIESTO, _MTIME
    ruta = os.path.join(static_folder, "dist", "manifest.json")
    mtime = os.path.getmtime(ruta) if os.path.exists(ruta) else None

    if _MANIFIESTO is not None and _RUTA_MANIFIESTO == ruta and _MTIME == mtime:
        return _MANIFIESTO

    if mtime is not None:
        with open(ruta, encoding="utf-8") as f:
            _MANIFIESTO = json.load(f)
    else:
        _MANIFIESTO = {}
    _RUTA_MANIFIESTO = ruta
    _MTIME = mtime
    return _MANIFIESTO


def asset_urls(nombre, static_folder):
    """Devuelve la lista de URLs a incluir para un paquete dado."""
    manifiesto = _cargar(static_folder)
    if nombre in manifiesto:
        return [url_for("static", filename=manifiesto[nombre])]
    return [url_for("static", filename=parte) for parte in FALLBACK.get(nombre, [])]
