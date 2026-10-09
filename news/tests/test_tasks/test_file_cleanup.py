from django.core.files.storage import default_storage
from django.test import TestCase

from events.tests.factories import EventFactory
from news.tests.factories import PostFactory, make_image
from resources.tests.mixins import MediaCleanupTestMixin


class PostImageCleanupTests(MediaCleanupTestMixin, TestCase):

    def test_delete_removes_image(self):
        post = PostFactory()
        path = post.image.name
        self.assertTrue(default_storage.exists(path))
        with self.captureOnCommitCallbacks(execute=True):
            post.delete()
        self.assertFalse(default_storage.exists(path))

    def test_replace_removes_old_keeps_new(self):
        post = PostFactory()
        old = post.image.name
        post.image = make_image("new.gif")
        with self.captureOnCommitCallbacks(execute=True):
            post.save()
        self.assertFalse(default_storage.exists(old))
        self.assertTrue(default_storage.exists(post.image.name))

    def test_clearing_image_removes_old_file(self):
        post = PostFactory()
        old = post.image.name
        post.image = None
        with self.captureOnCommitCallbacks(execute=True):
            post.save()
        self.assertFalse(default_storage.exists(old))

    def test_delete_post_without_image_does_not_fail(self):
        post = PostFactory(image=None)
        with self.captureOnCommitCallbacks(execute=True):
            post.delete()


class EventImageCleanupTests(MediaCleanupTestMixin, TestCase):

    def test_delete_removes_image(self):
        event = EventFactory()
        path = event.image.name
        self.assertTrue(default_storage.exists(path))
        with self.captureOnCommitCallbacks(execute=True):
            event.delete()
        self.assertFalse(default_storage.exists(path))

    def test_replace_removes_old_keeps_new(self):
        event = EventFactory()
        old = event.image.name
        event.image = make_image("new.gif")
        with self.captureOnCommitCallbacks(execute=True):
            event.save()
        self.assertFalse(default_storage.exists(old))
        self.assertTrue(default_storage.exists(event.image.name))

    def test_clearing_image_removes_old_file(self):
        event = EventFactory()
        old = event.image.name
        event.image = None
        with self.captureOnCommitCallbacks(execute=True):
            event.save()
        self.assertFalse(default_storage.exists(old))

    def test_delete_event_without_image_does_not_fail(self):
        event = EventFactory(image=None)
        with self.captureOnCommitCallbacks(execute=True):
            event.delete()