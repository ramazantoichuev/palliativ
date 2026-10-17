"""Тесты страницы «Контакты» (Ticket 116): проверяем то, что видит пользователь."""
from html.parser import HTMLParser

from django.apps import apps
from django.test import TestCase
from django.urls import reverse

# main.models — пакет, SiteContacts из него не экспортируется, берём через реестр
SiteContacts = apps.get_model("main", "SiteContacts")


FULL_CONTACTS = dict(
    address="г. Бишкек, ул. Юдахина, 61",
    phone="+996312214015",
    phone_display="0312 214015",
    email="info@palliativ.kg",
    whatsapp_url="https://wa.me/996555922604",
    whatsapp_display="+996 555 922 604",
    instagram_url="https://www.instagram.com/palliativecare_kg/",
    facebook_url="https://www.facebook.com/palliativecare.kg",
    twogis_url="https://2gis.kg/bishkek/geo/70000001",
)

REQUIRED_ONLY = dict(
    address=FULL_CONTACTS["address"],
    phone=FULL_CONTACTS["phone"],
    phone_display=FULL_CONTACTS["phone_display"],
    email=FULL_CONTACTS["email"],
    whatsapp_url="",
    whatsapp_display="",
    instagram_url="",
    facebook_url="",
    twogis_url="",
)


class _AnchorCollector(HTMLParser):
    """Собирает атрибуты всех <a> на странице."""

    def __init__(self):
        super().__init__()
        self.anchors = []

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            self.anchors.append(dict(attrs))


def _main_html(response):
    """Содержимое <main>: подвал и шапка дублируют контакты и не должны влиять на тесты."""
    html = response.content.decode()
    start = html.index("<main")
    end = html.index("</main>", start)
    return html[start:end]


def _anchors(response):
    parser = _AnchorCollector()
    parser.feed(_main_html(response))
    return parser.anchors


def _hrefs(response):
    return [a.get("href", "") for a in _anchors(response)]


class ContactsPageTests(TestCase):
    url = None

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.url = reverse("main:contacts")

    def _get(self, **contacts):
        # save() форсирует pk=1, поэтому повторный вызов обновляет единственную запись
        SiteContacts(**contacts).save()
        return self.client.get(self.url)

    # --- полностью заполненные контакты ---

    def test_full_contacts_show_all_links(self):
        response = self._get(**FULL_CONTACTS)

        self.assertEqual(response.status_code, 200)
        hrefs = _hrefs(response)
        self.assertIn("tel:+996312214015", hrefs)
        self.assertIn("mailto:info@palliativ.kg", hrefs)
        self.assertIn(FULL_CONTACTS["whatsapp_url"], hrefs)
        self.assertIn(FULL_CONTACTS["instagram_url"], hrefs)
        self.assertIn(FULL_CONTACTS["facebook_url"], hrefs)
        self.assertIn(FULL_CONTACTS["twogis_url"], hrefs)

    def test_full_contacts_show_visible_values(self):
        response = self._get(**FULL_CONTACTS)

        self.assertContains(response, FULL_CONTACTS["address"])
        self.assertContains(response, "0312 214015")
        self.assertContains(response, "info@palliativ.kg")
        self.assertContains(response, "+996 555 922 604")
        # у Instagram перед именем профиля стоит @
        self.assertContains(response, "@palliativecare_kg")
        self.assertContains(response, "palliativecare.kg")

    def test_whatsapp_falls_back_to_url_when_display_is_empty(self):
        data = {**FULL_CONTACTS, "whatsapp_display": ""}
        response = self._get(**data)

        self.assertContains(response, ">https://wa.me/996555922604<")

    # --- обязательные поля без необязательных ---

    def test_optional_cards_are_hidden_when_fields_are_empty(self):
        response = self._get(**REQUIRED_ONLY)

        hrefs = _hrefs(response)
        self.assertEqual(response.status_code, 200)
        self.assertIn("tel:+996312214015", hrefs)
        self.assertIn("mailto:info@palliativ.kg", hrefs)
        self.assertContains(response, FULL_CONTACTS["address"])
        for needle in ("wa.me", "instagram.com", "facebook.com", "2gis"):
            with self.subTest(needle=needle):
                self.assertFalse(
                    any(needle in href for href in hrefs),
                    f"На странице не должно быть ссылки с «{needle}»",
                )

    def test_twogis_button_is_hidden_when_url_is_empty(self):
        data = {**FULL_CONTACTS, "twogis_url": ""}
        response = self._get(**data)

        self.assertNotIn(FULL_CONTACTS["twogis_url"], _hrefs(response))
        # остальные необязательные карточки при этом на месте
        self.assertIn(FULL_CONTACTS["whatsapp_url"], _hrefs(response))

    # --- кнопка «Оставить заявку» ---

    def test_consultation_cta_links_to_form_with_full_contacts(self):
        response = self._get(**FULL_CONTACTS)

        self._assert_cta_links_to_consultation(response)

    def test_consultation_cta_links_to_form_without_optional_fields(self):
        response = self._get(**REQUIRED_ONLY)

        self._assert_cta_links_to_consultation(response)

    def _assert_cta_links_to_consultation(self, response):
        html = _main_html(response)
        self.assertIn("contact-cta", html)
        cta_html = html.split("contact-cta", 1)[1]
        parser = _AnchorCollector()
        parser.feed(cta_html)
        self.assertTrue(parser.anchors, "В синем блоке нет ссылки")
        self.assertEqual(
            parser.anchors[0].get("href"), reverse("main:new-consultation")
        )

    # --- безопасность внешних ссылок ---

    def test_external_links_have_noopener_noreferrer(self):
        response = self._get(**FULL_CONTACTS)

        external = [
            a for a in _anchors(response)
            if a.get("href", "").startswith("http")
            and a["href"] in {
                FULL_CONTACTS["whatsapp_url"],
                FULL_CONTACTS["instagram_url"],
                FULL_CONTACTS["facebook_url"],
                FULL_CONTACTS["twogis_url"],
            }
        ]
        self.assertEqual(len(external), 4)
        for anchor in external:
            with self.subTest(href=anchor["href"]):
                self.assertEqual(anchor.get("target"), "_blank")
                rel = (anchor.get("rel") or "").split()
                self.assertIn("noopener", rel)
                self.assertIn("noreferrer", rel)