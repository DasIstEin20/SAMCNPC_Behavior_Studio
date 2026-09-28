import copy
import json
import tempfile
import unittest
import zipfile
from pathlib import Path
from engine import *
from examples import *

class PackValidationTests(unittest.TestCase):
    def setUp(self):self.p=follow()
    def bad(self,mutator):
        mutator(self.p);self.assertFalse(validate_pack(self.p).ok)
    def test_source_counts(self):self.assertEqual((len(CONDITIONS),len(ACTIONS),len(BUILTINS)),(25,25,17))
    def test_follow(self):self.assertTrue(validate_pack(self.p).ok)
    def test_cautious(self):self.assertTrue(validate_pack(cautious()).ok)
    def test_retaliation(self):self.assertTrue(validate_pack(retaliate()).ok)
    def test_builtin_reserved(self):self.assertFalse(validate_pack(demo_reference()).ok)
    def test_reference_read(self):self.assertTrue(validate_pack(task_reference(),external=False).ok)
    def test_unknown_id(self):self.bad(lambda p:p['rules'][0]['actions'][0].update(action='samcnpc:chop_tree'))
    def test_no_has_axe(self):self.bad(lambda p:p['rules'][0].update(when=test('has_axe')))
    def test_unknown_property(self):self.bad(lambda p:p.update(script='print(42)'))
    def test_missing_channels(self):self.bad(lambda p:p.update(channels=['movement']))
    def test_duplicate_channels(self):self.bad(lambda p:p.update(channels=['movement','look','look']))
    def test_rule_duplicates(self):self.bad(lambda p:p['rules'].append(copy.deepcopy(p['rules'][0])))
    def test_invalid_pack_id(self):self.bad(lambda p:p.update(id='Invalid Name'))
    def test_schema_boolean(self):self.bad(lambda p:p.update(schemaVersion=True))
    def test_description_too_long(self):self.bad(lambda p:p.update(description='a'*513))
    def test_priority_bounds(self):self.bad(lambda p:p.update(priority=100001))
    def test_priority_fraction(self):self.bad(lambda p:p.update(priority=1.5))
    def test_unknown_args(self):self.bad(lambda p:p['rules'][0]['actions'][0]['args'].update(execute='no'))
    def test_missing_arg(self):self.bad(lambda p:p['rules'][0]['actions'][0]['args'].pop('speed'))
    def test_speed_bounds(self):self.bad(lambda p:p['rules'][0]['actions'][0]['args'].update(speed=0.09))
    def test_default_start(self):self.p['rules'][0]['actions'][0]['args']['stopDistance']=16;self.assertTrue(validate_pack(self.p).ok)
    def test_start_relation(self):self.bad(lambda p:p['rules'][0]['actions'][0]['args'].update(startDistance=2))
    def test_float_nan(self):self.bad(lambda p:p['rules'][0]['actions'][0]['args'].update(speed=float('nan')))
    def test_numeric_bool(self):self.bad(lambda p:p['rules'][0]['actions'][0]['args'].update(speed=True))
    def test_empty_all(self):self.bad(lambda p:p['rules'][0].update(when={'all':[]}))
    def test_not_null(self):self.bad(lambda p:p['rules'][0].update(when={'not':None}))
    def test_depth_eight_passes(self):
        e=test('always')
        for _ in range(7):e={'not':e}
        self.p['rules'][0]['when']=e;self.assertTrue(validate_pack(self.p).ok)
    def test_depth_nine_fails(self):
        e=test('always')
        for _ in range(8):e={'not':e}
        self.p['rules'][0]['when']=e;self.assertFalse(validate_pack(self.p).ok)
    def test_conflict_warning(self):
        self.p['rules'][0]['actions'].append(action('look_at_summoner'))
        r=validate_pack(self.p);self.assertTrue(r.ok);self.assertTrue(any('konkurują' in w for w in r.warnings))
    def test_registered_components(self):
        for cid,meta in CONDITIONS.items():
            with self.subTest(cid=cid):
                p=follow();p['rules'][0]['when']={'test':{'condition':cid,'args':{k:s['suggested'] for k,s in meta['args'].items() if s['required']}}}
                self.assertTrue(validate_pack(p).ok)
        for aid,meta in ACTIONS.items():
            with self.subTest(aid=aid):
                p=follow();p['channels']=CHANNELS[:];p['rules'][0]['actions']=[{'action':aid,'args':{k:s['suggested'] for k,s in meta['args'].items() if s['required']}}]
                self.assertTrue(validate_pack(p).ok)

class StrictJsonTests(unittest.TestCase):
    def test_duplicates(self):
        with self.assertRaises(StudioError):strict_json('{"a":1,"a":2}')
    def test_trailing_comma(self):
        with self.assertRaises(StudioError):strict_json('{"a":1,}')
    def test_nan(self):
        with self.assertRaises(StudioError):strict_json('{"a":NaN}')
    def test_no_execution(self):
        with self.assertRaises(StudioError):strict_json('__import__("os").system("echo NO")')
    def test_unicode(self):self.assertEqual(strict_json('"zażółć"'),'zażółć')
    def test_surrogate(self):
        with self.assertRaises(StudioError):strict_json('"\\ud800"')
    def test_integer_decimal(self):self.assertEqual(strict_json('1.0'),1)
    def test_no_fraction_rounding(self):
        with self.assertRaises(StudioError):strict_json('1.0000000000000000000000001')
    def test_number_length(self):
        with self.assertRaises(StudioError):strict_json('1'*65)
    def test_utf8_byte_limit(self):
        with self.assertRaises(StudioError):strict_json('"'+'ą'*70000+'"')
    def test_tree_depth(self):
        with self.assertRaises(StudioError):strict_json('['*34+'0'+']'*34)
    def test_node_count(self):
        with self.assertRaises(StudioError):strict_json('['+','.join('0' for _ in range(16400))+']')

class GraphTests(unittest.TestCase):
    def test_roundtrip_examples(self):
        for name,factory in EXAMPLES.items():
            with self.subTest(name=name):self.assertEqual(Graph.from_pack(factory()).to_pack(),factory())
    def test_project_roundtrip(self):
        g=Graph.from_pack(follow());h=Graph.from_project(strict_json(dump(g.to_project()),project=True));self.assertEqual(g.to_project(),h.to_project())
    def test_dangling(self):
        g=Graph.from_pack(follow());g.add('condition','samcnpc:always')
        with self.assertRaises(StudioError):g.to_pack()
    def test_cycles(self):
        g=Graph();a=g.add('all');b=g.add('any');g.connect(a.id,b.id)
        with self.assertRaises(StudioError):g.connect(b.id,a.id)
    def test_action_to_action(self):
        g=Graph();a=g.add('action','samcnpc:look_at_summoner');b=g.add('action','samcnpc:stop_movement')
        with self.assertRaises(StudioError):g.connect(a.id,b.id)
    def test_single_rule_input(self):
        g=Graph();r=g.add('rule');a=g.add('condition','samcnpc:always');b=g.add('condition','samcnpc:always');g.connect(a.id,r.id)
        with self.assertRaises(StudioError):g.connect(b.id,r.id)
    def test_one_rule_per_action(self):
        g=Graph();r=g.add('rule');s=g.add('rule');a=g.add('action','samcnpc:stop_movement');g.connect(r.id,a.id)
        with self.assertRaises(StudioError):g.connect(s.id,a.id)
    def test_edge_order(self):
        g=Graph.from_pack(retaliate());p=g.to_pack();h=Graph.from_pack(p);self.assertEqual(p,h.to_pack())
    def test_project_missing_node(self):
        v=Graph.from_pack(follow()).to_project();v['edges'].append(['missing','missing'])
        with self.assertRaises(StudioError):Graph.from_project(v)
    def test_project_invalid_position(self):
        v=Graph.from_pack(follow()).to_project();v['nodes'][0]['x']=float('nan')
        with self.assertRaises(StudioError):Graph.from_project(v)
    def test_need_channels(self):self.assertEqual(set(Graph.from_pack(retaliate()).needed_channels()),{'movement','look','combat','main_hand'})

class ExportTests(unittest.TestCase):
    def setUp(self):self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name);self.g=Graph.from_pack(follow())
    def tearDown(self):self.temp.cleanup()
    def test_atomic_save(self):
        p=self.root/'a.samgraph';atomic_write(p,dump(self.g.to_project()));self.assertEqual(Graph.from_project(strict_json(p.read_text(),project=True)).to_pack(),self.g.to_pack());self.assertFalse(list(self.root.glob('*.tmp')))
    def test_zip(self):
        p=self.root/'out.zip';export_zip(p,self.g)
        with zipfile.ZipFile(p) as z:
            self.assertEqual(set(z.namelist()),{'behaviors/example_follow.json','INSTALL_PL.txt','INSTALL_EN.txt','INSTALL_DE.txt'})
            self.assertEqual(strict_json(z.read('behaviors/example_follow.json').decode()),self.g.to_pack())
    def test_path_id(self):
        name=safe_filename('foo:../../bar');self.assertNotIn('/',name);self.assertNotIn('\\',name)
    def test_install(self):
        p=install(self.g,self.root);self.assertEqual(p,self.root/'config/samcnpc/behaviors/example_follow.json');self.assertEqual(strict_json(p.read_text()),self.g.to_pack())
    def test_no_silent_overwrite(self):
        install(self.g,self.root)
        with self.assertRaises(StudioError):install(self.g,self.root)
    def test_backup(self):
        p=install(self.g,self.root);old=p.read_text();self.g.priority=42;install(self.g,self.root,overwrite=True);self.assertEqual(p.with_suffix('.json.bak').read_text(),old)
    def test_duplicate_installed_id(self):
        p=install(self.g,self.root);p.rename(p.with_name('other.json'))
        with self.assertRaises(StudioError):install(self.g,self.root)
    def test_broken_existing(self):
        folder=self.root/'config/samcnpc/behaviors';folder.mkdir(parents=True);(folder/'bad.json').write_text('{')
        with self.assertRaises(StudioError):install(self.g,self.root)
    def test_symlink(self):
        other=self.root/'elsewhere';other.mkdir()
        try:(self.root/'config').symlink_to(other,target_is_directory=True)
        except OSError as e:self.skipTest('Brak uprawnień do dowiązań: '+str(e))
        with self.assertRaises(StudioError):install(self.g,self.root)
    def test_reserved_id_export(self):
        with self.assertRaises(StudioError):export_zip(self.root/'out.zip',Graph.from_pack(demo_reference()))

if __name__=='__main__':unittest.main()
