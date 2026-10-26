import os

from resources.constants import (
    RESOURCE_SUBCATEGORY_MORE_THRESHOLD,
    RESOURCE_SUBCATEGORY_VISIBLE,
)

IMAGE_EXTENSIONS = {"jpg", "jpeg", "png", "webp"}


def file_kind(name):
    """Тип файла по расширению: 'pdf', 'image' или 'other'."""
    ext = os.path.splitext(name or "")[1].lower().lstrip(".")
    if ext == "pdf":
        return "pdf"
    if ext in IMAGE_EXTENSIONS:
        return "image"
    return "other"

def split_visible_hidden(
    items,
    active_value=None,
    visible=RESOURCE_SUBCATEGORY_VISIBLE,
    threshold=RESOURCE_SUBCATEGORY_MORE_THRESHOLD,
):
    """Делит [(value, label), ...] на видимые и скрытые.

    Если элементов не больше threshold, видны все. Иначе видны первые
    `visible`, остальные уходят в «Ещё N». Активный скрытый элемент
    встаёт в видимый ряд вместо последнего, а вытесненный уходит в скрытые.
    """
    items = list(items)
    if len(items) <= threshold:
        return items, []
    shown, hidden = items[:visible], items[visible:]
    for index, (value, _label) in enumerate(hidden):
        if active_value and value == active_value:
            active = hidden.pop(index)
            hidden.insert(0, shown.pop())
            shown.append(active)
            break
    return shown, hidden