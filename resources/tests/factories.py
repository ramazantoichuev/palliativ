import io

import factory
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image

from patients.models.patients import Symptom
from resources.models.resources import Resource, ResourceFile, ResourceVideoLink


class SymptomFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Symptom

    name = factory.Sequence(lambda n: f'Симптом {n}')


class ResourceFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Resource

    title = factory.Sequence(lambda n: f'Ресурс {n}')
    description = 'Тестовое описание материала'
    audience = Resource.AUDIENCE_SPECIALIST
    subcategory = 'symptom_control'

    @factory.post_generation
    def symptoms(self, create, extracted, **kwargs):
        if not create or not extracted:
            return
        self.symptoms.add(*extracted)


class ResourceVideoLinkFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ResourceVideoLink

    resource = factory.SubFactory(ResourceFactory)
    url = 'https://youtube.com/watch?v=test123'



def make_test_image_bytes(size=(50, 50), color='blue', fmt='JPEG', quality=90):
    img = Image.new('RGB', size, color=color)
    buf = io.BytesIO()
    img.save(buf, format=fmt, quality=quality)
    return buf.getvalue()


def make_test_pdf_bytes():
    img = Image.new('RGB', (100, 100), color='white')
    buf = io.BytesIO()
    img.save(buf, format='PDF')
    return buf.getvalue()


class ResourceFileFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ResourceFile

    resource = factory.SubFactory(ResourceFactory)
    file = factory.LazyFunction(
        lambda: SimpleUploadedFile(
            'test.jpg', make_test_image_bytes(), content_type='image/jpeg'
        )
    )