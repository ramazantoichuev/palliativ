# resources/tests/test_views/test_resource_detail.py
# Страница материала: файлы, картинки, теги.
# Кнопка «Скачать все файлы (ZIP)» и содержимое архива проверяются в тестах ZIP
# (DownloadAllButtonTest, ResourceFilesZipViewTest) — здесь не дублируются.
import re

from django.conf import settings
from django.test import TestCase
from django.test.utils import CaptureQueriesContext
from django.utils import translation
from django.db import connection
from django.utils.translation import gettext

from resources.models.resources import Resource
from resources.tests.factories import ResourceFactory, SymptomFactory
from resources.tests.helpers import (
    make_converted_word_file,
    make_image_file,
    make_pdf_file,
    make_pending_word_file,
)
from resources.tests.mixins import MediaCleanupTestMixin


class ResourceDetailTests(MediaCleanupTestMixin, TestCase):

    def setUp(self):
        super().setUp()
        self.resource = ResourceFactory(
            audience=Resource.AUDIENCE_CAREGIVER, subcategory="pain_management"
        )
    def _get(self, lang="ru"):
        self.addCleanup(translation.activate, "ru")
        self.client.cookies[settings.LANGUAGE_COOKIE_NAME] = lang
        return self.client.get(self.resource.get_absolute_url(), HTTP_ACCEPT_LANGUAGE=lang)

    @staticmethod
    def _rows(response):
        return re.findall(
            r'<div class="file-row">.*?</div>',
            response.content.decode("utf-8"), re.S,
        )

    @staticmethod
    def _images(response):
        return re.findall(
            r'<img[^>]*class="resource-image"[^>]*>',
            response.content.decode("utf-8"),
        )

    def test_pdf_row_has_name_icon_link_and_download_button(self):
        rf = make_pdf_file(self.resource, name="guide.pdf")
        response = self._get()
        self.assertContains(response, 'class="file-row"', count=1)
        self.assertContains(response, 'target="_blank" rel="noopener"')
        self.assertContains(response, rf.public_file.url)
        row = self._rows(response)[0]
        self.assertIn('class="file-row__name">guide', row)
        self.assertIn("fa-file-pdf", row)
        self.assertIn(" download", row)

    def test_image_is_shown_on_page_and_listed_in_files(self):
        rf = make_image_file(self.resource, name="scale.png")
        response = self._get()

        images = self._images(response)
        self.assertEqual(len(images), 1)
        self.assertIn(f'src="{rf.public_file.url}"', images[0])
        self.assertIn('loading="lazy"', images[0])
        self.assertRegex(images[0], r'alt="scale[^".]*"')  # без расширения

        rows = self._rows(response)
        self.assertEqual(len(rows), 1)
        self.assertIn('class="file-row__name">scale', rows[0])
        self.assertIn("fa-image", rows[0])
        self.assertIn(" download", rows[0])
        self.assertIn("Скачать", rows[0])

    def test_pdf_only_resource_has_no_image(self):
        make_pdf_file(self.resource, name="guide.pdf")
        self.assertEqual(self._images(self._get()), [])

    def test_unconverted_word_is_hidden(self):
        make_pending_word_file(self.resource, name="draft.docx")
        response = self._get()
        self.assertNotContains(response, 'class="file-row"')
        self.assertNotContains(response, ".docx")

    def test_converted_word_shows_pdf_version_name(self):
        make_converted_word_file(self.resource, name="guide.docx")
        response = self._get()
        rows = self._rows(response)
        self.assertEqual(len(rows), 1)
        self.assertIn('class="file-row__name">guide', rows[0])
        self.assertIn(".pdf", rows[0])
        self.assertIn("fa-file-pdf", rows[0])
        self.assertNotContains(response, ".docx")

    def test_several_files_have_own_name_and_type(self):
        make_pdf_file(self.resource, name="guide.pdf")
        make_image_file(self.resource, name="scale.png")
        rows = self._rows(self._get())
        self.assertEqual(len(rows), 2)
        pdf_row = next(r for r in rows if 'file-row__name">guide' in r)
        image_row = next(r for r in rows if 'file-row__name">scale' in r)
        self.assertIn("fa-file-pdf", pdf_row)
        self.assertNotIn("fa-image", pdf_row)
        self.assertIn("fa-image", image_row)
        self.assertNotIn("fa-file-pdf", image_row)

    def test_audience_subcategory_and_symptoms_are_visible(self):
        symptom = SymptomFactory(name="Боль")
        resource = ResourceFactory(
            audience=Resource.AUDIENCE_CAREGIVER,
            subcategory="pain_management",
            symptoms=[symptom],
        )
        self.resource = resource
        with translation.override("ru"):
            audience = str(resource.get_audience_display())
            subcategory = str(resource.get_subcategory_display())
        response = self._get()
        self.assertContains(response, '<span class="resource-tags__label">Для кого</span>')
        self.assertContains(response, f'<li class="tag-pill">{audience}</li>')
        self.assertContains(response, f'<li class="tag-pill">{subcategory}</li>')
        self.assertContains(response, '<span class="resource-tags__label">Симптомы</span>')
        self.assertContains(response, '<li class="tag-pill tag-pill--symptom">Боль</li>')

    def test_symptoms_row_is_hidden_without_symptoms(self):
        response = self._get()
        self.assertNotContains(response, "resource-tags__row--symptoms")
        self.assertNotContains(response, '<span class="resource-tags__label">Симптомы</span>')

    def test_labels_and_symptoms_are_translated(self):
        symptom = SymptomFactory(name="Боль", name_ky="Оору", name_en="Pain")
        self.resource = ResourceFactory(symptoms=[symptom])
        for lang, symptom_name in (("ky", "Оору"), ("en", "Pain")):
            with self.subTest(lang=lang):
                with translation.override(lang):
                    who = gettext("Для кого")
                    symptoms = gettext("Симптомы")
                self.assertNotEqual(who, "Для кого")
                self.assertNotEqual(symptoms, "Симптомы")
                response = self._get(lang)
                self.assertContains(response, f'<span class="resource-tags__label">{who}</span>')
                self.assertContains(response, f'<span class="resource-tags__label">{symptoms}</span>')
                self.assertContains(response, f'tag-pill--symptom">{symptom_name}</li>')
                self.assertNotContains(response, 'tag-pill--symptom">Боль</li>')
                self.assertNotContains(response, '<span class="resource-tags__label">Для кого</span>')

    def test_several_images_are_shown_and_open_in_new_tab(self):
        make_image_file(self.resource, name="first.png")
        make_image_file(self.resource, name="second.png")
        response = self._get()
        self.assertEqual(len(self._images(response)), 2)
        self.assertContains(
            response, 'target="_blank" rel="noopener" class="d-block mb-3"', count=2
        )

    def test_query_count_does_not_grow_with_files_and_symptoms(self):
        url = self.resource.get_absolute_url()
        make_pdf_file(self.resource, name="a.pdf")
        self.resource.symptoms.add(SymptomFactory())
        self.client.get(url)  # прогрев: контекст-процессоры могут создавать записи
        with CaptureQueriesContext(connection) as before:
            self.client.get(url)
        make_pdf_file(self.resource, name="b.pdf")
        make_image_file(self.resource, name="c.png")
        self.resource.symptoms.add(*SymptomFactory.create_batch(3))
        with CaptureQueriesContext(connection) as after:
            self.client.get(url)
        self.assertEqual(len(before), len(after))