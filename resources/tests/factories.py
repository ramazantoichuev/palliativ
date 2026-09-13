import factory
from resources.models.resources import Resource, ResourceFile, ResourceVideoLink
from patients.models.patients import Symptom


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
