import factory
from main.models.consultation import ConsultationRequest


class ConsultationRequestFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ConsultationRequest

    first_name = factory.Sequence(lambda n: f'Пациент {n}')
    phone = '+996555123456'
    email = factory.Sequence(lambda n: f'test{n}@example.com')
    topic = 'medical_help'
