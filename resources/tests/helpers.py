import io
import os

from django.core.files.base import ContentFile
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image

from common.choices import ImageProcessingStatus
from resources.models.resources import ResourceFile


def make_pdf_file(resource, name="doc.pdf", content=b"%PDF-1.4 plain"):
    return ResourceFile.objects.create(
        resource=resource,
        file=SimpleUploadedFile(name, content, content_type="application/pdf"),
    )


def make_image_file(resource, name="scale.png"):
    buffer = io.BytesIO()
    Image.new("RGB", (2, 2), "white").save(buffer, "PNG")
    rf = ResourceFile.objects.create(
        resource=resource,
        file=SimpleUploadedFile(name, buffer.getvalue(), content_type="image/png"),
    )
    rf.refresh_from_db()
    return rf


def make_pending_word_file(resource, name="draft.docx"):
    rf = ResourceFile.objects.create(
        resource=resource,
        file=SimpleUploadedFile(name, b"word-bytes", content_type="application/octet-stream"),
    )
    ResourceFile.objects.filter(pk=rf.pk).update(
        processing_status=ImageProcessingStatus.PENDING
    )
    rf.refresh_from_db()
    return rf


def make_converted_word_file(resource, name="guide.docx", pdf_content=b"%PDF-1.4 converted"):
    """Word-файл с готовой PDF-версией"""
    rf = make_pending_word_file(resource, name=name)
    base_name = os.path.splitext(os.path.basename(name))[0]
    rf.converted_pdf.save(f"{base_name}.pdf", ContentFile(pdf_content), save=False)
    ResourceFile.objects.filter(pk=rf.pk).update(
        converted_pdf=rf.converted_pdf.name,
        processing_status=ImageProcessingStatus.DONE,
    )
    rf.refresh_from_db()
    return rf