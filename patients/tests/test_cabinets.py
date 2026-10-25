from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from accounts.models import DoctorProfile, PatientProfile
from accounts.tests.factories import UserFactory
from patients.models import PatientCard, Symptom
from resources.models.resources import Resource
from resources.tests.factories import ResourceFactory

User = get_user_model()
NO_MATERIALS = "По этому симптому материалов пока нет"
NO_CHILD_MATERIALS = "материалов для детей пока нет"


class CabinetTests(TestCase):
    def setUp(self):
        self.symptom = Symptom.objects.create(name="Боль")

    def _patient(self, name, is_child):
        user = UserFactory(role=User.Role.PATIENT)
        profile, _created = PatientProfile.objects.get_or_create(user=user)
        profile.is_child = is_child
        profile.save()
        return user, profile

    def _card(self, profile, doctor=None):
        card = PatientCard.objects.create(patient=profile, doctor=doctor, diagnosis="d")
        card.symptoms.add(self.symptom)
        return card

    def _resource(self, audience, title):
        resource = ResourceFactory(audience=audience, title=title)
        resource.symptoms.add(self.symptom)
        return resource

    def test_adult_patient_sees_only_caregiver_and_link_leads_to_resource(self):
        user, profile = self._patient("adult", False)
        self._card(profile)
        care = self._resource(Resource.AUDIENCE_CAREGIVER, "Для ухода")
        self._resource(Resource.AUDIENCE_SPECIALIST, "Для врачей")
        self._resource(Resource.AUDIENCE_PEDIATRIC, "Для детей")

        self.client.force_login(user)
        response = self.client.get(reverse("patients:patient_dashboard"))

        self.assertContains(response, "Для ухода")
        self.assertContains(response, f'href="{care.get_absolute_url()}"')
        self.assertNotContains(response, "Для врачей")
        self.assertNotContains(response, "Для детей")

    def test_child_patient_sees_only_pediatric(self):
        user, profile = self._patient("kid", True)
        self._card(profile)
        self._resource(Resource.AUDIENCE_PEDIATRIC, "Для детей")
        self._resource(Resource.AUDIENCE_CAREGIVER, "Для ухода")

        self.client.force_login(user)
        response = self.client.get(reverse("patients:patient_dashboard"))

        self.assertContains(response, "Для детей")
        self.assertNotContains(response, "Для ухода")

    def test_child_patient_without_materials_sees_child_message(self):
        user, profile = self._patient("kid", True)
        self._card(profile)
        self.client.force_login(user)
        response = self.client.get(reverse("patients:patient_dashboard"))
        self.assertContains(response, NO_CHILD_MATERIALS)

    def test_adult_patient_without_materials_sees_generic_message(self):
        user, profile = self._patient("adult", False)
        self._card(profile)
        self.client.force_login(user)
        response = self.client.get(reverse("patients:patient_dashboard"))
        self.assertContains(response, NO_MATERIALS)
        self.assertNotContains(response, NO_CHILD_MATERIALS)

    def test_doctor_of_child_sees_specialist_and_pediatric(self):
        doctor_user = User.objects.create_user(
            username="doc", email="doc@example.com", password="x12345678",
            role=User.Role.DOCTOR,
        )
        doctor, _created = DoctorProfile.objects.get_or_create(user=doctor_user)
        _user, profile = self._patient("kid", True)
        self._card(profile, doctor=doctor)
        self._resource(Resource.AUDIENCE_SPECIALIST, "Для врачей")
        self._resource(Resource.AUDIENCE_PEDIATRIC, "Для детей")
        self._resource(Resource.AUDIENCE_CAREGIVER, "Для ухода")

        self.client.force_login(doctor_user)
        response = self.client.get(reverse("patients:doctor_dashboard"))

        self.assertContains(response, "Для врачей")
        self.assertContains(response, "Для детей")
        self.assertNotContains(response, "Для ухода")

    def test_survey_page_has_new_title_and_labelled_checkboxes(self):
        user, profile = self._patient("adult", False)
        self._card(profile)
        self.client.force_login(user)
        response = self.client.get(reverse("patients:symptom_survey"))

        self.assertContains(response, "Что сейчас беспокоит?")
        self.assertContains(response, 'type="checkbox"')
        self.assertContains(response, '<label class="symptom-tile" for="id_symptoms_0">')