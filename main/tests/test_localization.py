from django.test import SimpleTestCase
from django.utils import translation
from django.utils.translation import gettext as _


class InterfaceLocalizationTestCase(SimpleTestCase):
    CRITICAL_STRINGS = [
        "Поиск",
        "Контакты",
        "Советы по уходу",
        "Управление болью",
        "Ошибка обработки",
    ]
    ALLOWED_MATCHES_KY = {
        "Администратор",
        "Менеджер",
        "Категория",
        "Файл",
        "Видео",
        "WhatsApp",
        "Facebook",
        "Instagram",
        "Паллиатив.kg",
        "ФИО",
    }

    ALLOWED_MATCHES_EN = {
        "WhatsApp",
        "Facebook",
        "Instagram",
        "Паллиатив.kg",
    }

    def test_kyrgyz_localization_is_complete(self):
        with translation.override("ky"):
            for msgid in self.CRITICAL_STRINGS:
                translated = _(msgid)
                self.assertTrue(translated.strip(), f"Строка '{msgid}' имеет пустой перевод на KY!")
                if msgid not in self.ALLOWED_MATCHES_KY:
                    self.assertNotEqual(
                        translated, msgid,
                        f"Строка '{msgid}' на KY возвращает русский текст! Проверьте, скомпилирован ли .mo файл."
                    )

    def test_english_localization_is_complete(self):
        with translation.override("en"):
            for msgid in self.CRITICAL_STRINGS:
                translated = _(msgid)
                self.assertTrue(translated.strip(), f"Строка '{msgid}' имеет пустой перевод на EN!")
                if msgid not in self.ALLOWED_MATCHES_EN:
                    self.assertNotEqual(
                        translated, msgid,
                        f"Строка '{msgid}' на EN возвращает русский текст! Проверьте файл локализации."
                    )
