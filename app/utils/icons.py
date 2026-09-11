"""Catálogo de iconos vectoriales disponibles para las categorías."""

# (clave, etiqueta para el panel)
ICONOS = [
    ("flor", "Flor"),
    ("rosa", "Rosa"),
    ("tulipan", "Tulipán"),
    ("ramo", "Ramo"),
    ("arreglo", "Arreglo floral"),
    ("canasta", "Canasta"),
    ("planta", "Planta"),
    ("regalo", "Regalo"),
    ("amor", "Amor"),
    ("aniversario", "Aniversario"),
    ("cumpleanos", "Cumpleaños"),
    ("especial", "Ocasión especial"),
]

CLAVES = {clave for clave, _ in ICONOS}

# Los emojis que se usaban antes se convierten a su icono equivalente
EMOJI_A_ICONO = {
    "🌹": "rosa", "🌷": "tulipan", "💐": "ramo", "🌸": "arreglo",
    "🌿": "planta", "🎁": "regalo", "❤️": "amor", "❤": "amor",
    "💍": "aniversario", "🎂": "cumpleanos", "✨": "especial",
    "🌺": "flor", "🌻": "flor", "🌼": "flor",
}

# Icono sugerido según el nombre/slug de la categoría
POR_SLUG = {
    "rosas": "rosa", "ramos": "ramo", "arreglos-florales": "arreglo",
    "plantas": "planta", "cumpleanos": "cumpleanos", "aniversarios": "aniversario",
    "amor": "amor", "ocasiones-especiales": "especial",
}


def normalizar(valor, slug=None):
    """Devuelve una clave de icono válida a partir de un emoji, clave o slug."""
    if valor:
        valor = valor.strip()
        if valor in CLAVES:
            return valor
        if valor in EMOJI_A_ICONO:
            return EMOJI_A_ICONO[valor]
    if slug and slug in POR_SLUG:
        return POR_SLUG[slug]
    return "flor"
