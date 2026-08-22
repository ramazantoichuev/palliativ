from django.shortcuts import render

class PatientCardDetailView(LoginRequiredMixin, ListView):
    model = PatientCard
    template_name = 'patients/patient_dashboard.html'
    context_object_name = 'patient_cards'

    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return super().get(request, *args, **kwargs)
        if request.user.role != BaseUser.Role.PATIENT:
            raise PermissionDenied
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        return PatientCard.objects.filter(
            patient=self.request.user.patient_profile
        ).order_by('-updated_at')

# Create your views here.
