from django.db import IntegrityError, transaction
from django.test import TestCase

from patients.models import Symptom


class SymptomModelTests(TestCase):

    def test_name_is_unique(self):
        Symptom.objects.create(name="Слабость")
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Symptom.objects.create(name="Слабость")