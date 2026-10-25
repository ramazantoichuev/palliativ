import os
import shutil
import stat
import tempfile
from unittest import mock

from django.core.files.storage import FileSystemStorage
from django.test import SimpleTestCase, override_settings

from resources.tasks import _atomic_replace, _compress_pdf


class CompressedFilePermissionsTestCase(SimpleTestCase):
    """Сжатый файл должен оставаться читаемым для nginx (Ticket 123).

    mkstemp создаёт временный файл с правами 0600, и os.replace переносил их
    на место оригинала — ссылка /media/... отдавала 403. Ghostscript не
    вызываем: подменяем subprocess.run и проверяем наблюдаемый результат.
    """

    original_bytes = b'%PDF-original' + b'0' * 5000

    def setUp(self):
        super().setUp()
        tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
        self.storage = FileSystemStorage(location=tmp)
        self.file_name = 'doc.pdf'
        self.storage_path = self.storage.path(self.file_name)
        with open(self.storage_path, 'wb') as f:
            f.write(self.original_bytes)
        os.chmod(self.storage_path, 0o644)

    def file_mode(self):
        return stat.S_IMODE(os.stat(self.storage_path).st_mode)


class AtomicReplacePermissionsTests(CompressedFilePermissionsTestCase):
    def test_replace_keeps_file_readable_by_others(self):
        _atomic_replace(self.storage, self.file_name, b'new-bytes')

        self.assertTrue(self.file_mode() & stat.S_IROTH)
        self.assertEqual(self.file_mode(), 0o644)

    def test_replace_writes_new_content(self):
        _atomic_replace(self.storage, self.file_name, b'new-bytes')

        with open(self.storage_path, 'rb') as f:
            self.assertEqual(f.read(), b'new-bytes')

    def test_failed_write_keeps_original_and_leaves_no_tmp_files(self):
        def failing_fdopen(fd, mode):
            os.close(fd)
            tmp_file = mock.MagicMock()
            tmp_file.__enter__.return_value.write.side_effect = OSError('disk full')
            tmp_file.__exit__.return_value = False
            return tmp_file

        with mock.patch('resources.tasks.os.fdopen', side_effect=failing_fdopen):
            with self.assertRaises(OSError):
                _atomic_replace(self.storage, self.file_name, b'new-bytes')

        with open(self.storage_path, 'rb') as f:
            self.assertEqual(f.read(), self.original_bytes)
        self.assertEqual(self.file_mode(), 0o644)
        self.assertEqual(os.listdir(self.storage.location), [self.file_name])


@override_settings(MIN_RESOURCE_FILE_SIZE_FOR_COMPRESSION_MB=0.001)
class CompressPdfPermissionsTests(CompressedFilePermissionsTestCase):
    @staticmethod
    def fake_ghostscript(output_content):
        def side_effect(cmd, timeout, capture_output):
            output_path = next(
                arg.split('=', 1)[1] for arg in cmd if arg.startswith('-sOutputFile=')
            )
            with open(output_path, 'wb') as f:
                f.write(output_content)
            return mock.Mock(returncode=0, stderr=b'')
        return side_effect

    def test_compressed_pdf_is_not_0600_and_matches_original_mode(self):
        resource_file = mock.Mock()
        resource_file.file.storage = self.storage
        resource_file.file.name = self.file_name

        with mock.patch(
            'resources.tasks.subprocess.run',
            side_effect=self.fake_ghostscript(b'%PDF-small'),
        ):
            changed = _compress_pdf(resource_file, len(self.original_bytes))

        self.assertTrue(changed)
        self.assertNotEqual(self.file_mode(), 0o600)
        self.assertEqual(self.file_mode(), 0o644)
        with open(self.storage_path, 'rb') as f:
            self.assertEqual(f.read(), b'%PDF-small')
