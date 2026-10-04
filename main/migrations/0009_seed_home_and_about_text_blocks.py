from django.db import migrations

TEXT_BLOCKS = {
    "home_hero_title": "Жизнь без боли — это право каждого.",
    "home_hero_subtitle": (
        "Ассоциация паллиативной и хосписной помощи Кыргызской Республики. "
        "Мы объединяем врачей, клиники и семьи, чтобы обеспечить достойное "
        "качество жизни на любом её этапе."
    ),
    "home_card_patients_title": "Для пациентов",
    "home_card_care_tips_title": "Советы по уходу",
    "home_card_care_tips_desc": (
        "Как ухаживать за больным дома: кормление, гигиена, "
        "психологическая поддержка."
    ),
    "home_card_pain_management_title": "Управление болью",
    "home_card_pain_management_desc": (
        "Что такое боль, когда нужно обращаться к врачу, и ваше право "
        "на обезболивание."
    ),
    "home_card_meds_access_title": "Доступ к услугам и лекарственным средствам",
    "home_card_meds_access_desc": (
        "Как получить помощь паллиативного врача, право на стационарную "
        "помощь и рецепт."
    ),
    "home_card_doctors_title": "Для врачей",
    "home_card_doctors_desc": (
        "Протоколы, лекции и справочные материалы по уходу за пациентами."
    ),
    # О нас
    "about_page_title": "Об Ассоциации",
    "about_work_directions_heading": "Основные направления нашей работы",
    "about_belief_heading": "Мы верим",
    "about_contribution_heading": (
        "Наш вклад в развитие паллиативной помощи в Кыргызстане"
    ),
    "about_intro": (
        "Ассоциация паллиативной и хосписной помощи — профессиональное "
        "объединение, содействующее развитию доступной и качественной "
        "паллиативной помощи в Кыргызской Республике."
    ),
    "about_work_directions": (
        "Мы работаем над развитием нормативной базы, обучением "
        "специалистов и повышением доступности паллиативной помощи "
        "для пациентов и их семей по всей стране."
    ),
    "about_belief": (
        "Мы верим, что каждый человек имеет право на достойную жизнь "
        "и избавление от боли, независимо от диагноза и прогноза."
    ),
    "about_contribution_intro": (
        "За годы работы Ассоциация внесла вклад в развитие паллиативной "
        "помощи в Кыргызстане по нескольким направлениям."
    ),
    "about_contribution_01": (
        "Участие в разработке нормативно-правовых актов, регулирующих "
        "паллиативную помощь в стране."
    ),
    "about_contribution_02": (
        "Разработка клинических руководств и стандартов оказания "
        "паллиативной помощи."
    ),
    "about_contribution_03": (
        "Организация практических услуг для пациентов и их семей."
    ),
    "about_contribution_04": (
        "Подготовка и повышение квалификации медицинских специалистов "
        "в области паллиативной помощи."
    ),
    "about_contribution_05": (
        "Диалог с государственными органами и защита прав пациентов."
    ),
    "about_contribution_06": (
        "Международное сотрудничество и обмен опытом с партнёрскими "
        "организациями."
    ),
}


def seed_text_blocks(apps, schema_editor):
    EditableTextBlock = apps.get_model("main", "EditableTextBlock")
    for slug, content in TEXT_BLOCKS.items():
        EditableTextBlock.objects.get_or_create(
            slug=slug,
            defaults={"content": content, "content_ru": content},
        )


def remove_text_blocks(apps, schema_editor):
    EditableTextBlock = apps.get_model("main", "EditableTextBlock")
    EditableTextBlock.objects.filter(slug__in=TEXT_BLOCKS.keys()).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("main", "0008_merge_0006_systemsettings_0007_seed_site_contacts"),
    ]

    operations = [
        migrations.RunPython(seed_text_blocks, remove_text_blocks),
    ]