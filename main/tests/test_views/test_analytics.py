from django.test import TestCase, override_settings
from django.urls import reverse


class AnalyticsSnippetTests(TestCase):
    """Скрипты аналитики рендерятся только при заполненных ID (Ticket 54)."""

    @override_settings(GOOGLE_ANALYTICS_ID='', GOOGLE_TAG_MANAGER_ID='', YANDEX_METRIKA_ID='')
    def test_empty_ids_render_nothing(self):
        response = self.client.get(reverse('main:home'))
        self.assertNotContains(response, 'googletagmanager.com')
        self.assertNotContains(response, 'mc.yandex.ru')

    @override_settings(GOOGLE_ANALYTICS_ID='G-TEST12345', YANDEX_METRIKA_ID='12345678')
    def test_filled_ids_render_both_snippets(self):
        response = self.client.get(reverse('main:home'))
        self.assertContains(response, 'googletagmanager.com/gtag/js?id=G-TEST12345')
        self.assertContains(response, "gtag('config', 'G-TEST12345')")
        self.assertContains(response, 'mc.yandex.ru/metrika/tag.js')
        self.assertContains(response, 'ym(12345678, "init"')
        self.assertContains(response, 'mc.yandex.ru/watch/12345678')

    @override_settings(GOOGLE_ANALYTICS_ID='G-TEST12345', YANDEX_METRIKA_ID='')
    def test_counters_are_independent(self):
        response = self.client.get(reverse('main:home'))
        self.assertContains(response, 'googletagmanager.com')
        self.assertNotContains(response, 'mc.yandex.ru')

    @override_settings(GOOGLE_TAG_MANAGER_ID='')
    def test_empty_gtm_renders_nothing(self):
        response = self.client.get(reverse('main:home'))
        self.assertNotContains(response, 'gtm.js')
        self.assertNotContains(response, 'ns.html')

    @override_settings(GOOGLE_TAG_MANAGER_ID='GTM-TEST123')
    def test_filled_gtm_renders_both_parts(self):
        response = self.client.get(reverse('main:home'))
        self.assertContains(response, "'https://www.googletagmanager.com/gtm.js?id='+i+dl")
        self.assertContains(response, "'GTM-TEST123'")
        self.assertContains(response, 'googletagmanager.com/ns.html?id=GTM-TEST123')
