from datetime import timedelta

import factory
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone

from events.models import Event

# Минимальный валидный GIF 1x1 — чтобы ImageField принял файл без внешних фикстур.
ONE_PIXEL_GIF = (
    b'GIF87a\x01\x00\x01\x00\x80\x01\x00\x00\x00\x00ccc,'
    b'\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;'
)


def make_image(name='event.gif'):
    return SimpleUploadedFile(name, ONE_PIXEL_GIF, content_type='image/gif')


class EventFactory(factory.django.DjangoModelFactory):
    """Предстоящее мероприятие — попадает в upcoming_events."""

    class Meta:
        model = Event

    title = factory.Sequence(lambda n: f"Мероприятие {n}")
    slug = factory.Sequence(lambda n: f"event-{n}")
    description = 'Краткое описание мероприятия.'
    content = 'Подробная программа мероприятия.'
    location = 'г. Бишкек, ул. Юдахина 61'
    event_date = factory.LazyFunction(lambda: timezone.now() + timedelta(days=7))


class PastEventFactory(EventFactory):
    """Мероприятие с датой в прошлом — попадает в past_events."""

    event_date = factory.LazyFunction(lambda: timezone.now() - timedelta(days=30))
