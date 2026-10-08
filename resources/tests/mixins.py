import shutil
import tempfile
from unittest import mock

from django.test import override_settings

from resources.tasks import delete_file_task


class MediaCleanupTestMixin:
    """Свой временный MEDIA_ROOT на каждый тест и синхронное выполнение Huey-задачи удаления."""

    def setUp(self):
        super().setUp()
        tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)

        override = override_settings(MEDIA_ROOT=tmp)
        override.enable()
        self.addCleanup(override.disable)

        patcher = mock.patch(
            "resources.tasks.delete_file_task", new=delete_file_task.call_local
        )
        patcher.start()
        self.addCleanup(patcher.stop)