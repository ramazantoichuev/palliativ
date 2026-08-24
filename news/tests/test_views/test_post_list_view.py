from django.template.defaultfilters import title
from django.test import TestCase
from django.urls import reverse

from news.models import Category, Post


class PostListViewTest(TestCase):

    def setUp(self):
        self.url = reverse('news:post_list')
        self.category = Category.objects.create(name='sport')
        self.post = Post.objects.create(
            title='тест',
            slug='post',
            content='test_content',
            description='test_description',
            category=self.category,
            created_at ='2026-08-22 14:30:00'
            )
        self.post.created_at ='2026-08-22 14:30:00'
        self.post.save()
        self.post2 = Post.objects.create(
            title='test2',
            slug='post2',
            content='test_content2',
            description='test_description2',
            category=self.category,
        )

    def test_post_filter_category(self):
        response = self.client.get(self.url, {'category_id': self.category.id})
        self.assertEqual(response.status_code, 200)

    def test_post_filter_date(self):
        response = self.client.get(self.url, {
            'date_from': '2026-08-21',
            'date_to': '2026-08-23',
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.post.title)

    def test_post_empty(self):
        self.post.delete()
        self.post2.delete()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(response.context['posts']), [])


    def test_title_en_empty_falls_back_to_ru(self):
        self.client.cookies['django_language'] = 'en'
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'test')

