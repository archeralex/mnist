import sys
import os
import struct
import tempfile
import gzip
import array
import errno
import unittest
try:
    from unittest import mock
except ImportError:
    import mock  # py2
sys.path.append('..')
import mnist


SAMPLE_LABELS = (5, 0, 9, 1)
SAMPLE_DATA = struct.pack('>IIBBBB', (0x08 << 8) + 0x01, 4, *SAMPLE_LABELS)


class TestMnistLabels(unittest.TestCase):
    """Test that mnist_labels function returns the right data and
    types, and make the right calls."""

    def setUp(self):
        self.sample_fname = tempfile.mktemp(prefix='test_mnist_')
        with gzip.open(self.sample_fname, 'wb') as f:
            f.write(SAMPLE_DATA)

    def tearDown(self):
        try:
            os.remove(self.sample_fname)
        except OSError as e:  # not saved when download_mnist_file is mocked
            if e.errno == errno.ENOENT:  # py2 to capture only FileNotFoundError
                pass
            else:
                raise

    def test_passing_file_returns_correct_labels(self):
        actual_labels = tuple(mnist.mnist_labels(self.sample_fname))
        self.assertEqual(actual_labels, SAMPLE_LABELS)

    def test_returns_numpy_array_by_default(self):
        import numpy as np
        actual_labels = mnist.mnist_labels(self.sample_fname)
        self.assertIsInstance(actual_labels, np.ndarray)

    def test_returns_python_array(self):
        actual_labels = mnist.mnist_labels(self.sample_fname,
                                             use_numpy=False)
        self.assertIsInstance(actual_labels, array.array)

    def test_no_fname_calls_download(self):
        with mock.patch('mnist.main.download_mnist_file',
                        return_value=self.sample_fname) as download_mnist_file:
            mnist.main.mnist_labels()
            download_mnist_file.assert_called_once_with(labels=True, test=False)

    def test_no_fname_calls_download_for_test(self):
        with mock.patch('mnist.main.download_mnist_file', return_value=self.sample_fname) as download_mnist_file:
            mnist.mnist_labels(test=True)
            download_mnist_file.assert_called_once_with(labels=True, test=True)

    def test_passing_file_does_not_remove_file(self):
        with mock.patch('os.remove') as os_remove:
            mnist.mnist_labels(self.sample_fname)
        self.assertFalse(os_remove.called)

    def test_no_fname_removes_downloaded_file_by_default(self):
        with mock.patch('mnist.main.download_mnist_file', return_value=self.sample_fname):
            with mock.patch('os.remove') as os_remove:
                mnist.main.mnist_labels()
        os_remove.assert_called_once_with(self.sample_fname)

    def xtest_no_fname_does_not_remove_file(self):
        with mock.patch('mnist.main.download_mnist_file', self.sample_fname):
            with mock.patch('os.remove') as os_remove:
                mnist.mnist_labels(delete_tempfile=False)
        self.assertFalse(os_remove.called)
