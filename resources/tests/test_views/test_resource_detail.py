import tempfile

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse

from resources.models.resources import ResourceFile
from resources.tests.factories import ResourceFactory, ResourceVideoLinkFactory


@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
class ResourceDetailViewTest(TestCase):
    def test_detail_returns_200(self):
        resource = ResourceFactory()
        url = reverse('resources:resource_detail', kwargs={'slug': resource.slug})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_files_and_videos_in_context(self):
        resource = ResourceFactory()
        ResourceFile.objects.create(
            resource=resource,
            file=SimpleUploadedFile('test.pdf', b'file_content', content_type='application/pdf')
        )
        ResourceVideoLinkFactory(resource=resource)
        url = reverse('resources:resource_detail', kwargs={'slug': resource.slug})
        response = self.client.get(url)

        self.assertEqual(len(response.context['resource'].files.all()), 1)
        self.assertEqual(len(response.context['resource'].videos.all()), 1)

    def test_resource_without_attachments_does_not_fail(self):
        resource = ResourceFactory()
        url = reverse('resources:resource_detail', kwargs={'slug': resource.slug})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_nonexistent_pk_returns_404(self):
        url = reverse('resources:resource_detail', kwargs={'slug': 'non-existent-slug'})

        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
