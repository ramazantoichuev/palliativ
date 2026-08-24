from django.test import TestCase
from django.urls import reverse

from news.models import Category, Post


class PostDetail(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name='sport')
        self.post = Post.objects.create(
            title='test',
            slug='post',
            content='test_content',
            description='test_description',
            category=self.category,
            created_at='2026-08-22 14:30:00'
        )

        self.post2 = Post.objects.create(
            title='test2',
            slug='post2',
            content='test_content2',
            description='test_description2',
            category=self.category,
        )
        self.url = reverse('news:post_detail', kwargs={'slug': self.post.slug})


    def test_post_detail(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

