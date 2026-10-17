import os

IMAGE_EXTENSIONS = {"jpg", "jpeg", "png", "webp"}


def file_kind(name):
    """Тип файла по расширению: 'pdf', 'image' или 'other'."""
    ext = os.path.splitext(name or "")[1].lower().lstrip(".")
    if ext == "pdf":
        return "pdf"
    if ext in IMAGE_EXTENSIONS:
        return "image"
    return "other"