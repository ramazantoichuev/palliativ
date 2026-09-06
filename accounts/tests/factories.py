import factory
from django.contrib.auth import get_user_model

User = get_user_model()

class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User
        django_get_or_create = ('email',)

    username = factory.Sequence(lambda n: f"user{n}")
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    email = factory.Sequence(lambda n: 'person{}@example.com'.format(n))
    password = factory.PostGenerationMethodCall('set_password', '')
    phone = factory.Sequence(
        lambda n: f"+996555123{n:03d}"
    )

