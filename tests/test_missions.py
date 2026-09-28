import copy
import json
import tempfile
import unittest
import zipfile
from pathlib import Path
from engine import StudioError
from missions import MissionProject, tutorial_project, validate_mission

class MissionTests(unittest.TestCase):
    def test_tutorial_has_three_explicit_operations_and_distinct_requirements(self):
        p=tutorial_project().validate()
        self.assertEqual(3,len(p.mission['stages']))
        self.assertEqual(['equipment_matches','task_success','at_position'],[r['predicate']['type'] for r in p.mission['requirements']])
        self.assertEqual(p.project(),MissionProject.read(p.project()).project())
    def test_export_manifest_and_content_are_exact(self):
        p=tutorial_project()
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'mission.zip';p.export(path)
            with zipfile.ZipFile(path) as z:
                manifest=json.loads(z.read('mission-manifest.json'))
                self.assertEqual(set(z.namelist()),set(manifest['packs']+manifest['missions']+['mission-manifest.json']))
                self.assertEqual(p.mission,json.loads(z.read('missions/mission.json')))
                self.assertTrue(all(info.file_size<=131072 for info in z.infolist()))
    def test_cycles_unreachable_missing_refs_and_duplicate_ids_fail(self):
        for change in [lambda d:d['stages'][2].update(success='prepare'),lambda d:d['stages'][0].update(success=None),lambda d:d['stages'][0].update(success='absent'),lambda d:d['stages'][1].update(id='prepare'),lambda d:d['stages'][0].update(completion=['absent'])]:
            p=tutorial_project();change(p.mission)
            with self.assertRaises(StudioError):p.validate()
    def test_missing_pack_and_duplicate_bundle_pack_fail(self):
        p=tutorial_project();p.packs.pop()
        with self.assertRaises(StudioError):p.validate()
        p=tutorial_project();p.packs.append(copy.deepcopy(p.packs[0]))
        with self.assertRaises(StudioError):p.validate()
    def test_no_arbitrary_predicate_operation_or_historical_stock(self):
        for change in [lambda d:d['requirements'][0]['predicate'].update(type='eval'),lambda d:d['requirements'][0].update(latched=True),lambda d:d['stages'][0]['operation'].update(type='samcnpc:command'),lambda d:d['stages'][0].update(retries=99)]:
            p=tutorial_project();change(p.mission)
            with self.assertRaises(StudioError):p.validate()
    def test_ordinary_project_not_reinterpreted_as_mission(self):
        with self.assertRaises(StudioError):MissionProject.read({'format':'samcnpc-studio','version':1})
    def test_ui_languages_and_history_preserve_project(self):
        from studio import Studio
        app=Studio();app.withdraw()
        try:
            app.open_mission();window=app.mission_window;window.withdraw()
            original=window.project.project();window.add();self.assertEqual(4,len(window.project.mission['stages']))
            window.undo();self.assertEqual(original,window.project.project());window.redo();self.assertEqual(4,len(window.project.mission['stages']))
            window.undo();window.vars['id'].set('uncommitted_draft')
            from i18n import LANGUAGES
            for lang in ('pl','de','en','pl','en'):
                app.language_name.set(LANGUAGES[lang]);app.set_language();app.update()
                self.assertEqual(original,window.project.project());self.assertEqual('uncommitted_draft',window.vars['id'].get())
            self.assertEqual(3,len(window.node_ranges))
        finally:app.destroy()

if __name__=='__main__':unittest.main()
