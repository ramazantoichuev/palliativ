from django.test import TestCase

from news.models import Category, Post


class TestPost(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name='sport')
        self.post = Post.objects.create(
            title='test',
            slug='post',
            content='test_content',
            description='test_description',
            category=self.category)


    def test_post_creation(self):
        self.assertTrue(isinstance(self.post, Post))
        self.assertEqual(self.post.category.name, 'sport')
        self.assertEqual(self.category.posts.all().first().title, 'test')




