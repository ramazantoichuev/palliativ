import io

import factory
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image

from news.models.posts import Category, Post


def make_test_image_bytes(size=(50, 50), color='blue', fmt='JPEG', quality=90):
    img = Image.new('RGB', size, color=color)
    buf = io.BytesIO()
    img.save(buf, format=fmt, quality=quality)
    return buf.getvalue()


class CategoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Category

    name = factory.Sequence(lambda n: f'Категория {n}')


class PostFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Post

    title = factory.Sequence(lambda n: f'Новость {n}')
    slug = factory.Sequence(lambda n: f'novost-{n}')
    content = 'Тестовый текст новости'
    description = 'Тестовое описание'
    category = factory.SubFactory(CategoryFactory)
    image = factory.LazyFunction(
        lambda: SimpleUploadedFile(
            'test.jpg', make_test_image_bytes(), content_type='image/jpeg'
        )
    )