import contextlib
import io
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch
from diagnostics import log_exception

class DiagnosticsTests(unittest.TestCase):
    def test_log_contains_runtime_and_trace(self):
        with TemporaryDirectory() as folder, patch('diagnostics.Path.home', return_value=Path(folder)):
            with contextlib.redirect_stderr(io.StringIO()):
                path = log_exception('RuntimeError: test callback')
            self.assertEqual(path, Path(folder)/'samcnpc-studio-error.log')
            text = path.read_text(encoding='utf-8')
            self.assertIn('RuntimeError: test callback', text)
            self.assertIn('Python ', text)
            self.assertIn('Behavior Studio 1.3.0', text)

    def test_no_writable_home_does_not_raise(self):
        with patch('diagnostics.Path.home', side_effect=RuntimeError('home unavailable')):
            with contextlib.redirect_stderr(io.StringIO()):
                self.assertIsNone(log_exception('test'))

    def test_log_rotates_at_bound(self):
        with TemporaryDirectory() as folder, patch('diagnostics.Path.home', return_value=Path(folder)):
            path = Path(folder)/'samcnpc-studio-error.log'
            path.write_text('x'*1_000_001)
            with contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(log_exception('test'), path)
            self.assertLess(path.stat().st_size, 1000)
            self.assertEqual(path.with_suffix('.log.previous').stat().st_size, 1_000_001)
