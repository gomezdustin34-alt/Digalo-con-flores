import hashlib

from flask import Response, abort, request

from app.blueprints.media import bp
from app.models.media import MediaFile

# Un año. Los nombres de archivo llevan un uuid único, así que el contenido de
# una URL nunca cambia: es seguro cachearlo de forma indefinida en el CDN.
CACHE = "public, max-age=31536000, immutable"


@bp.route("/media/<file_id>")
def serve(file_id):
    archivo = MediaFile.query.get(file_id)
    if archivo is None:
        abort(404)

    etag = hashlib.md5(f"{archivo.id}-{archivo.size}".encode()).hexdigest()
    if request.headers.get("If-None-Match") == etag:
        return Response(status=304, headers={"ETag": etag, "Cache-Control": CACHE})

    return Response(
        archivo.data,
        mimetype=archivo.content_type,
        headers={
            "Cache-Control": CACHE,
            "ETag": etag,
            "Content-Length": str(archivo.size),
        },
    )
