import logging
import os
import zipfile
from io import BytesIO
from urllib.parse import urlencode

from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404
from django.views import View
from django.views.generic import DetailView, ListView

from .constants import RESOURCE_AUDIENCE_CHIPS_MAX, RESOURCES_PER_PAGE
from .models.resources import Resource
from .utils import split_visible_hidden

logger = logging.getLogger(__name__)


class ResourceListView(ListView):
    model = Resource
    template_name = "resources/resource_list.html"
    context_object_name = "resources"
    paginate_by = RESOURCES_PER_PAGE

    def get_queryset(self):
        queryset = (
            Resource.objects.all()
            .prefetch_related("files", "videos")
            .order_by("-created_at")
        )

        audience = self.request.GET.get("audience")
        subcategory = self.request.GET.get("subcategory")
        symptom = self.request.GET.get("symptom")

        if audience:
            queryset = queryset.filter(audience=audience)
        if subcategory:
            queryset = queryset.filter(subcategory=subcategory)
        if symptom:
            queryset = queryset.filter(symptoms__id=symptom)

        return queryset.distinct()

    def get_context_data(self, **kwargs):
        from patients.models.patients import Symptom

        context = super().get_context_data(**kwargs)
        context["audience_choices"] = Resource.AUDIENCE_CHOICES
        context["subcategory_choices"] = Resource.SUBCATEGORY_CHOICES
        context["symptoms"] = Symptom.objects.all()
        context["selected_audience"] = self.request.GET.get("audience", "")
        context["selected_subcategory"] = self.request.GET.get("subcategory", "")
        context["selected_symptom"] = self.request.GET.get("symptom", "")
        visible, hidden = split_visible_hidden(Resource.SUBCATEGORY_CHOICES, context["selected_subcategory"])
        context["audience_chips"] = list(Resource.AUDIENCE_CHOICES)[:RESOURCE_AUDIENCE_CHIPS_MAX]
        context["subcategory_visible"] = visible
        context["subcategory_hidden"] = hidden
        params = {
            key: value
            for key, value in self.request.GET.items()
            if key != "page" and value
        }
        context["query"] = urlencode(params)
        return context


class ResourceDetailView(DetailView):
    model = Resource
    template_name = "resources/resource_detail.html"
    context_object_name = "resource"

    def get_queryset(self):
        return super().get_queryset().prefetch_related("symptoms", "files", "videos")


class ResourceFilesZipView(View):
    """Отдаёт все доступные посетителю файлы ресурса одним ZIP-архивом.

    Архив собирается на лету в памяти и содержит ровно те же файлы,
    что отдаются по одиночным ссылкам на странице ресурса
    (Word — готовой PDF-версией, необработанный Word пропускается).
    """

    def get(self, request, slug):
        resource = get_object_or_404(Resource, slug=slug)
        public_files = resource.public_files
        if not public_files:
            raise Http404

        buffer = BytesIO()
        used_names = set()
        with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as archive:
            for field_file in public_files:
                arcname = self._unique_arcname(
                    os.path.basename(field_file.name), used_names
                )
                try:
                    with field_file.open("rb") as f:
                        archive.writestr(arcname, f.read())
                except OSError:
                    logger.warning(
                        "Не удалось добавить файл %s в архив ресурса %s",
                        field_file.name,
                        slug,
                    )

        response = HttpResponse(buffer.getvalue(), content_type="application/zip")
        response["Content-Disposition"] = f'attachment; filename="{slug}.zip"'
        return response

    @staticmethod
    def _unique_arcname(name, used_names):
        base_name, extension = os.path.splitext(name)
        candidate = name
        counter = 1
        while candidate in used_names:
            candidate = f"{base_name}-{counter}{extension}"
            counter += 1
        used_names.add(candidate)
        return candidate


# Create your views here.
