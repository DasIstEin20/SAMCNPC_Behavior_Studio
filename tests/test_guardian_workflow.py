"""User workflows against the real 506-node example and Studio GUI handlers."""
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
import zipfile

from engine import BASE, Graph, strict_json
from i18n import LANGUAGES

PROJECT = BASE / 'examples/advanced/guardian_forester/guardian_forester.samgraph'

@unittest.skipIf(sys.platform.startswith('linux') and not os.environ.get('DISPLAY'), 'GUI needs a display')
class GuardianWorkflowTests(unittest.TestCase):
    def setUp(self):
        from studio import Studio
        self.app = Studio()
        self.errors = []
        self.app.report_callback_exception = lambda *args: self.errors.append(args)
        self.app.tk.createcommand('bgerror', lambda text: self.errors.append(text))
        self.app.update()
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        with patch('studio.filedialog.askopenfilename', return_value=str(PROJECT)):
            self.app.open_file()
        self.app.update()

    def tearDown(self):
        self.app.update()
        self.app.destroy()
        self.assertEqual([], self.errors)

    def test_open_validate_switch_export_roundtrip_install_and_backup(self):
        a = self.app
        original = a.graph.to_pack()
        self.assertEqual(original, strict_json(PROJECT.with_suffix('.json').read_text(encoding='utf-8')))
        with zipfile.ZipFile(PROJECT.with_suffix('.zip')) as archive:
            self.assertEqual(original, json.loads(archive.read('behaviors/showcase_guardian_forester.json')))
        native_fixture = BASE / 'tests/fixtures/guardian_forester_forge.zip'
        with zipfile.ZipFile(native_fixture) as archive:
            self.assertEqual(original, json.loads(archive.read('behaviors/showcase_guardian_forester.json')))
        self.assertEqual(506, len(a.graph.nodes))
        self.assertEqual(473, len(a.graph.edges))
        self.assertEqual(33, len(original['rules']))
        for lang in ('pl', 'de', 'en') * 2:
            a.language_name.set(LANGUAGES[lang]); a.set_language(); a.update()
            a.validate(); a.update()
            self.assertEqual(str(a.json_tab), a.tabs.select())
            self.assertIn(a.tr('validation_ok'), a.report_text.get('1.0', 'end'))
            self.assertEqual(original, a.graph.to_pack())
        destination = Path(self.temp.name)
        exported_json = destination / 'export.json'
        exported_zip = destination / 'export.zip'
        with patch('studio.messagebox.askokcancel', return_value=True) as warnings, \
             patch('studio.messagebox.showerror') as error, \
             patch('studio.filedialog.asksaveasfilename', return_value=str(exported_json)):
            a.export_json()
            error.assert_not_called()
            warnings.assert_called_once()
        self.assertEqual(original, strict_json(exported_json.read_text(encoding='utf-8')))
        with patch('studio.messagebox.askokcancel', return_value=True), \
             patch('studio.messagebox.showerror') as error, \
             patch('studio.filedialog.asksaveasfilename', return_value=str(exported_zip)):
            a.export_bundle()
            error.assert_not_called()
        with zipfile.ZipFile(exported_zip) as archive:
            documents = [n for n in archive.namelist() if n.startswith('behaviors/')]
            self.assertEqual(['behaviors/showcase_guardian_forester.json'], documents)
            self.assertEqual(original, json.loads(archive.read(documents[0])))
            self.assertFalse(any(n.endswith(('.py', '.samgraph', '.class')) for n in archive.namelist()))
        instance = destination / 'fake_minecraft'
        instance.mkdir()
        with patch('studio.filedialog.askdirectory', return_value=str(instance)):
            a.choose_instance()
        with patch('studio.messagebox.askokcancel', return_value=True), \
             patch('studio.messagebox.askyesno', return_value=True), \
             patch('studio.messagebox.showinfo'), patch('studio.messagebox.showerror') as error:
            a.install_pack('zip')
            error.assert_not_called()
            installed = instance / 'resources/samcnpc/behaviors/showcase_guardian_forester.zip'
            previous = installed.read_bytes()
            a.install_pack('zip')
            error.assert_not_called()
            self.assertEqual(previous, installed.with_suffix('.zip.bak').read_bytes())
            # A user accidentally tries both formats: keep the installed ZIP and report the duplicate ID.
            a.install_pack('json')
            error.assert_called_once()
            self.assertFalse((instance / 'config/samcnpc/behaviors/showcase_guardian_forester.json').exists())
        a.dirty = False
        with patch('studio.filedialog.askopenfilename', return_value=str(exported_json)):
            a.open_file()
        self.assertEqual(original, a.graph.to_pack())
        a.validate()
        self.assertIn(a.tr('validation_ok'), a.report_text.get('1.0', 'end'))

    def test_invalid_query_is_visible_and_export_is_blocked_without_a_file_dialog(self):
        a = self.app
        node = next(n for n in a.graph.nodes.values() if n.ref == 'samcnpc:ensure_equipment')
        node.args['query'] = '@invented_role'
        a.changed()
        a.validate()
        self.assertIn('EXPORT BLOCKED', a.report_text.get('1.0', 'end'))
        with patch('studio.messagebox.showerror') as error, \
             patch('studio.filedialog.asksaveasfilename') as filename:
            a.export_bundle()
            error.assert_called_once()
            filename.assert_not_called()
