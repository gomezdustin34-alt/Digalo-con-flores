import os
import uuid

from flask import current_app, url_for
from werkzeug.utils import secure_filename


def save_upload(file_storage, subfolder="products"):
    if not file_storage or not file_storage.filename:
        return None

    ext = secure_filename(file_storage.filename).rsplit(".", 1)[-1].lower()
    filename = f"{uuid.uuid4().hex}.{ext}"

    folder = os.path.join(current_app.config["UPLOAD_FOLDER"], subfolder)
    os.makedirs(folder, exist_ok=True)
    file_storage.save(os.path.join(folder, filename))

    return url_for("static", filename=f"uploads/{subfolder}/{filename}")
