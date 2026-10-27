from django.contrib.auth import get_user_model
from django.test import TestCase

from accounts.models import DoctorProfile, PatientProfile
from accounts.tests.factories import UserFactory
from patients.admin import PatientCardAdminForm
from patients.models import PatientCard

User = get_user_model()


class PatientCardAdminFormIsChildTests(TestCase):
    """Менеджер меняет признак «ребёнок» и из карточки пациента (Ticket 126)."""

    def setUp(self):
        super().setUp()
        patient_user = UserFactory(role=User.Role.PATIENT)
        self.profile, _created = PatientProfile.objects.get_or_create(
            user=patient_user
        )
        doctor_user = UserFactory(role=User.Role.DOCTOR)
        self.doctor, _created = DoctorProfile.objects.get_or_create(user=doctor_user)
        self.card = PatientCard.objects.create(
            patient=self.profile, doctor=self.doctor, diagnosis="диагноз"
        )

    def form_data(self, **overrides):
        data = {
            "patient": self.profile.pk,
            "doctor": self.doctor.pk,
            "diagnosis": "диагноз",
            "medications": "",
            "contraindications": "",
            "previous_treatment": "",
            "symptoms": [],
        }
        data.update(overrides)
        return data

    def test_form_shows_current_flag_of_existing_card(self):
        self.profile.is_child = True
        self.profile.save()

        form = PatientCardAdminForm(instance=self.card)

        self.assertTrue(form.fields["is_child"].initial)

    def test_checked_flag_is_saved_to_patient_profile(self):
        form = PatientCardAdminForm(
            self.form_data(is_child="on"), instance=self.card
        )

        self.assertTrue(form.is_valid(), form.errors)
        # как в админке: save(commit=False), объект сохраняется отдельно
        form.save(commit=False)

        self.profile.refresh_from_db()
        self.assertTrue(self.profile.is_child)

    def test_unchecked_flag_resets_patient_profile(self):
        self.profile.is_child = True
        self.profile.save()

        form = PatientCardAdminForm(self.form_data(), instance=self.card)

        self.assertTrue(form.is_valid(), form.errors)
        form.save(commit=False)

        self.profile.refresh_from_db()
        self.assertFalse(self.profile.is_child)
