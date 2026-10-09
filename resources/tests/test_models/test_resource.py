from django.test import TestCase

from resources.models.resources import Resource, ResourceVideoLink
from resources.tests.factories import ResourceFactory, SymptomFactory


class ResourceModelTest(TestCase):
    def test_str_returns_title(self):
        resource = ResourceFactory(title='Уход при боли')
        self.assertEqual(str(resource), 'Уход при боли')

    def test_audience_choices(self):
        resource = ResourceFactory(audience=Resource.AUDIENCE_CAREGIVER)
        self.assertEqual(resource.audience, 'caregiver')

    def test_subcategory_choices(self):
        resource = ResourceFactory(subcategory='npa')
        self.assertEqual(resource.subcategory, 'npa')

    def test_pain_management_subcategory_can_be_saved(self):
        resource = ResourceFactory(
            audience=Resource.AUDIENCE_CAREGIVER, subcategory='pain_management'
        )

        resource.refresh_from_db()

        self.assertEqual(resource.subcategory, 'pain_management')

    def test_symptoms_relation(self):
        symptom = SymptomFactory(name='Боль')
        resource = ResourceFactory(symptoms=[symptom])
        self.assertIn(symptom, resource.symptoms.all())


class ResourceGetAbsoluteUrlTests(TestCase):
    def test_get_absolute_url_returns_correct_path(self):
        resource = Resource.objects.create(
            title="Тестовый материал",
            audience="caregiver",
            subcategory="care_feeding",
        )

        url = resource.get_absolute_url()

        self.assertEqual(url, f"/resources/{resource.slug}/")


class ResourceVideoLinkTests(TestCase):
    def setUp(self):
        self.resource = ResourceFactory()

    def test_str_returns_url(self):
        video = ResourceVideoLink.objects.create(
            resource=self.resource,
            url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        )

        self.assertEqual(
            str(video),
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        )

    def test_get_embed_url_from_youtube_watch_url(self):
        video = ResourceVideoLink.objects.create(
            resource=self.resource,
            url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        )

        self.assertEqual(
            video.get_embed_url(),
            "https://www.youtube.com/embed/dQw4w9WgXcQ",
        )

    def test_get_embed_url_from_youtu_be_url(self):
        video = ResourceVideoLink.objects.create(
            resource=self.resource,
            url="https://youtu.be/dQw4w9WgXcQ",
        )

        self.assertEqual(
            video.get_embed_url(),
            "https://www.youtube.com/embed/dQw4w9WgXcQ",
        )

    def test_get_embed_url_from_embed_url(self):
        video = ResourceVideoLink.objects.create(
            resource=self.resource,
            url="https://www.youtube.com/embed/dQw4w9WgXcQ",
        )

        self.assertEqual(
            video.get_embed_url(),
            "https://www.youtube.com/embed/dQw4w9WgXcQ",
        )

    def test_get_embed_url_from_live_url(self):
        video = ResourceVideoLink.objects.create(
            resource=self.resource,
            url="https://www.youtube.com/live/dQw4w9WgXcQ",
        )

        self.assertEqual(
            video.get_embed_url(),
            "https://www.youtube.com/embed/dQw4w9WgXcQ",
        )

    def test_get_embed_url_from_shorts_url(self):
        video = ResourceVideoLink.objects.create(
            resource=self.resource,
            url="https://www.youtube.com/shorts/dQw4w9WgXcQ",
        )

        self.assertEqual(
            video.get_embed_url(),
            "https://www.youtube.com/embed/dQw4w9WgXcQ",
        )

    def test_get_embed_url_returns_none_for_invalid_url(self):
        video = ResourceVideoLink.objects.create(
            resource=self.resource,
            url="https://example.com/video",
        )

        self.assertIsNone(video.get_embed_url())