from django.test import TestCase
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from resources.tests.factories import ResourceFactory, ResourceVideoLinkFactory
from resources.models.resources import ResourceFile


class ResourceDetailViewTest(TestCase):
    def test_detail_returns_200(self):
        resource = ResourceFactory()
        url = reverse('resources:resource_detail', kwargs={'pk': resource.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_files_and_videos_in_context(self):
        resource = ResourceFactory()
        ResourceFile.objects.create(
            resource=resource,
            file=SimpleUploadedFile('test.pdf', b'file_content', content_type='application/pdf')
        )
        ResourceVideoLinkFactory(resource=resource)

        url = reverse('resources:resource_detail', kwargs={'pk': resource.pk})
        response = self.client.get(url)

        self.assertEqual(len(response.context['resource'].files.all()), 1)
        self.assertEqual(len(response.context['resource'].videos.all()), 1)

    def test_resource_without_attachments_does_not_fail(self):
        resource = ResourceFactory()
        url = reverse('resources:resource_detail', kwargs={'pk': resource.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_nonexistent_pk_returns_404(self):
        url = reverse('resources:resource_detail', kwargs={'pk': 99999})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
