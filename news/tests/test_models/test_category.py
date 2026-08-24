from django.test import TestCase

from news.models import Category


class TestCategory(TestCase):

    def test_category_creation(self):
        category = Category.objects.create(name='test_category')
        self.assertEqual(category.name, 'test_category')