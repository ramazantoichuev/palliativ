from django.test import TestCase

from resources.models.resources import Resource


class ResourceGetAbsoluteUrlTests(TestCase):
    def test_get_absolute_url_returns_correct_path(self):
        resource = Resource.objects.create(
            title="Тестовый материал",
            audience="caregiver",
            subcategory="care_feeding",
        )

        url = resource.get_absolute_url()

        self.assertEqual(url, f"/resources/{resource.slug}/")
