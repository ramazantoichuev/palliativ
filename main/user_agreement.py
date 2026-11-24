from .models.editable_text_block import EditableTextBlock

USER_AGREEMENT_SLUGS = (
    "user-agreement-intro",
    "user-agreement-general",
    "user-agreement-nature",
    "user-agreement-duties",
    "user-agreement-ip",
    "user-agreement-liability",
    "user-agreement-changes",
    "user-agreement-law",
)


def is_user_agreement_published():
    """Соглашение видно сайту, только когда все блоки есть и заполнены по-русски.

    Пока менеджер не внёс весь текст, страница отвечает 404, а ссылка
    в футере не показывается (Ticket 76: не публиковать до согласования).
    Удалённые (soft delete) блоки в выборку не попадают.
    """
    texts = dict(
        EditableTextBlock.objects.filter(
            slug__in=USER_AGREEMENT_SLUGS
        ).values_list("slug", "content_ru")
    )
    return all(
        (texts.get(slug) or "").strip() for slug in USER_AGREEMENT_SLUGS
    )
