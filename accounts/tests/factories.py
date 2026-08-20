import factory
from django.contrib.auth import get_user_model

User = get_user_model()


class UserFactory(factory.django.DjangoModelFactory):
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    email = factory.Faker('email')
    password = factory.PostGenerationMethodCall('set_password', '')
    phone = factory.Faker('bothify', text='+996#########')

    class Meta:
        model = User
        django_get_or_create = ('email',)
