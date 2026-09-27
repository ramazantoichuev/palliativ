import factory
from django.core.files.uploadedfile import SimpleUploadedFile

from news.models.posts import Category, Post

ONE_PIXEL_GIF = (
    b"GIF87a\x01\x00\x01\x00\x80\x01\x00\x00\x00\x00ccc,"
    b"\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;"
)


def make_image(name="post.gif"):
    return SimpleUploadedFile(name, ONE_PIXEL_GIF, content_type="image/gif")


class CategoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Category

    name = factory.Sequence(lambda n: f"Категория {n}")


class PostFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Post

    title = factory.Sequence(lambda n: f"Новость {n}")
    content = "Полный текст новости."
    description = "Краткое описание новости."
    category = factory.SubFactory(CategoryFactory)
