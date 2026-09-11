"""Compila los recursos estáticos para producción.

- Une y minifica el CSS en un solo archivo por área (tienda / panel), lo que
  reduce peticiones y peso.
- Une el JavaScript por área (code splitting: la tienda no descarga el JS del
  panel y viceversa).
- Pone un hash del contenido en el nombre del archivo, de modo que se puede
  cachear para siempre y aun así actualizarse solo cuando el contenido cambia.

Se ejecuta en el despliegue:  python scripts/build_assets.py
"""
import hashlib
import json
import os
import re
import shutil

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ESTATICOS = os.path.join(RAIZ, "app", "static")
DIST = os.path.join(ESTATICOS, "dist")

# Un paquete por área: la tienda nunca descarga el CSS/JS del panel.
PAQUETES = {
    "tienda.css": ["css/tokens.css", "css/base.css", "css/components.css", "css/storefront.css"],
    "tienda.js": ["js/main.js", "js/cart.js"],
    "panel.css": ["css/tokens.css", "css/base.css", "css/components.css", "css/admin.css"],
    "panel.js": ["js/admin.js"],
}


def minificar_css(css: str) -> str:
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.DOTALL)      # comentarios
    css = re.sub(r"\s+", " ", css)                             # espacios repetidos
    css = re.sub(r"\s*([{};:,>])\s*", r"\1", css)              # espacios alrededor de símbolos
    css = css.replace(";}", "}")                               # punto y coma final sobrante
    return css.strip()


def construir():
    if os.path.exists(DIST):
        shutil.rmtree(DIST)
    os.makedirs(DIST, exist_ok=True)

    manifiesto = {}
    for nombre, partes in PAQUETES.items():
        contenido = []
        for parte in partes:
            ruta = os.path.join(ESTATICOS, parte.replace("/", os.sep))
            with open(ruta, encoding="utf-8") as f:
                contenido.append(f.read())
        unido = "\n".join(contenido)

        if nombre.endswith(".css"):
            unido = minificar_css(unido)

        hash_corto = hashlib.sha1(unido.encode("utf-8")).hexdigest()[:10]
        base, ext = nombre.rsplit(".", 1)
        archivo = f"{base}.{hash_corto}.{ext}"
        with open(os.path.join(DIST, archivo), "w", encoding="utf-8") as f:
            f.write(unido)

        manifiesto[nombre] = f"dist/{archivo}"
        print(f"  {nombre:12s} -> {archivo}  ({len(unido)/1024:.1f} KB)")

    with open(os.path.join(DIST, "manifest.json"), "w", encoding="utf-8") as f:
        json.dump(manifiesto, f, indent=2)

    print(f"Recursos compilados en {DIST}")


if __name__ == "__main__":
    construir()
