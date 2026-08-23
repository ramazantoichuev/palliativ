from django.db import models
from django.utils.translation import gettext_lazy as _
from accounts.models import PatientProfile, DoctorProfile

class Symptom(models.Model):
    name = models.CharField(_('Название симптома'), max_length=255, unique=True)

    class Meta:
        verbose_name = _('Симптом')
        verbose_name_plural = _('Симптомы')

    def __str__(self):
        return self.name

class PatientCard(models.Model):
    patient = models.ForeignKey(
        PatientProfile,
        on_delete=models.CASCADE,
        related_name='medical_cards',
        verbose_name=_('Пациент')
    )
    doctor = models.ForeignKey(
        DoctorProfile,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_cards',
        verbose_name=_('Лечащий врач')
    )
    diagnosis = models.TextField(_('Диагноз'))
    medications = models.TextField(_('Принимаемые препараты'), blank=True)
    contraindications = models.TextField(_('Противопоказания'), blank=True)
    previous_treatment = models.TextField(_('Ранее проведенное лечение'), blank=True)
    symptoms = models.ManyToManyField(Symptom, blank=True, verbose_name=_('Симптомы'))
    created_at = models.DateTimeField(_('Дата создания'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Дата изменения'), auto_now=True)

    class Meta:
        verbose_name = _('Карточка пациента')
        verbose_name_plural = _('Карточки пациентов')

    def __str__(self):
        return f"{self.patient} — {self.diagnosis[:30]}"

    def get_queryset(self):
        return PatientCard.objects.filter(doctor=self.request.user.doctor_profile)