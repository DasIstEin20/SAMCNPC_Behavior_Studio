import copy
import json
import tempfile
import unittest
import zipfile
from pathlib import Path
from catalog import CatalogError,load_schema,item_query_valid
from engine import Graph,CATALOG,CONDITIONS,ACTIONS,BASE,StudioError,refresh_catalog,validate_pack,install,export_zip,strict_json
from examples import follow
from pack_install import documents

class CatalogZipTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name)
        self.schema=json.loads((BASE/'vendor/behavior-pack-registered.schema.json').read_text(encoding='utf-8'))
    def tearDown(self):
        refresh_catalog(BASE/'vendor/behavior-pack-registered.schema.json');self.temp.cleanup()
    def schema_file(self,value):
        path=self.root/'schema.json';path.write_text(json.dumps(value),encoding='utf-8');return path
    def test_catalog_descriptors_are_generated_and_refresh_preserves_graph_and_imported_maps(self):
        graph=Graph.from_pack(follow());before=graph.to_project();identity=id(CONDITIONS)
        new=copy.deepcopy(self.schema['$defs']['test']['oneOf'][0]);new['properties']['condition']['const']='custom:future_condition'
        self.schema['$defs']['test']['oneOf'].append(new)
        refresh_catalog(self.schema_file(self.schema))
        self.assertIn('custom:future_condition',CONDITIONS);self.assertEqual(id(CONDITIONS),identity)
        after=graph.to_project();after['targetCommit']=before['targetCommit'];self.assertEqual(after,before)
        self.assertEqual(ACTIONS['samcnpc:ensure_equipment']['args']['query']['type'],'string')
        self.assertEqual(ACTIONS['samcnpc:ensure_equipment']['args']['minimumDurability']['maximum'],1)
    def test_malformed_catalog_never_replaces_current_registry(self):
        before=copy.deepcopy(CATALOG)
        mutations=[lambda s:s.update({'x-samcnpc-definition-semantics-version':99}),
                   lambda s:s['$defs']['test']['oneOf'].append(copy.deepcopy(s['$defs']['test']['oneOf'][0])),
                   lambda s:s['$defs']['action']['oneOf'][0].update({'x-samcnpc-required-channels':['shell']})]
        for mutate in mutations:
            candidate=copy.deepcopy(self.schema);mutate(candidate)
            with self.assertRaises(StudioError):refresh_catalog(self.schema_file(candidate))
            self.assertEqual(CATALOG,before)
        path=self.root/'schema.json';path.write_text('{"a":1,"a":2}')
        with self.assertRaises(CatalogError):load_schema(path)
        path.write_text('['*10000)
        with self.assertRaises(CatalogError):load_schema(path)
    def test_generic_item_queries_and_new_component_roundtrip(self):
        self.assertTrue(item_query_valid('minecraft:coal|minecraft:charcoal'))
        for value in ('@invented','minecraft:coal|','@axe||@food','a:'+('b'*127),'minecraft:coal|minecraft:coal'):
            self.assertFalse(item_query_valid(value))
        pack=follow();pack['channels']=['inventory','main_hand','off_hand']
        pack['rules'][0]['when']={'test':{'condition':'samcnpc:inventory_count','args':{'query':'minecraft:coal','operator':'gte','count':2}}}
        pack['rules'][0]['actions']=[{'action':'samcnpc:ensure_equipment','args':{'query':'@axe','destination':'MAIN_HAND','minimumDurability':0.2}}]
        self.assertTrue(validate_pack(pack).ok)
        graph=Graph.from_pack(pack);self.assertEqual(Graph.from_project(graph.to_project()).to_pack(),pack)
        self.assertEqual(Graph.from_pack(strict_json(json.dumps(pack))).to_pack(),pack)
        pack['rules'][0]['actions'][0]['args']['query']='@invented';self.assertFalse(validate_pack(pack).ok)
    def test_zip_is_native_format_and_install_constructs_resources_path(self):
        graph=Graph.from_pack(follow());path=install(graph,self.root,format='zip')
        self.assertEqual(path,self.root/'resources/samcnpc/behaviors/example_follow.zip')
        rows,size=documents(path);self.assertEqual(rows,[('behaviors/example_follow.json',graph.to_pack())]);self.assertGreater(size,0)
        with self.assertRaises(StudioError):install(graph,self.root,format='zip')
        original=path.read_bytes();graph.priority=77;install(graph,self.root,format='zip',overwrite=True)
        self.assertEqual(path.with_suffix('.zip.bak').read_bytes(),original)
        with self.assertRaises(StudioError):export_zip(path,graph)
    def test_duplicate_ids_across_json_and_zip_are_rejected_but_distinct_packs_coexist(self):
        graph=Graph.from_pack(follow());install(graph,self.root)
        with self.assertRaises(StudioError):install(graph,self.root,format='zip')
        graph.pack_id='custom:different';self.assertTrue(install(graph,self.root,format='zip').is_file())
        other=Graph.from_pack(follow());other.pack_id='custom:third';self.assertTrue(install(other,self.root).is_file())
    def test_archive_traversal_and_bombs_are_rejected_before_install(self):
        graph=Graph.from_pack(follow());path=self.root/'resources/samcnpc/behaviors/bad.zip';path.parent.mkdir(parents=True)
        for name,data in (('../behaviors/a.json','{}'),('behaviors/a.json','x'*131073),('behaviors//a.json','{}')):
            with zipfile.ZipFile(path,'w') as archive:archive.writestr(name,data)
            with self.assertRaises(StudioError):install(graph,self.root)
    def test_existing_guardian_project_keeps_layout_and_export(self):
        path=BASE/'tutorials/examples/complex_guardian_escort.samgraph'
        value=strict_json(path.read_text(encoding='utf-8'),project=True)
        graph=Graph.from_project(value);restored=Graph.from_project(graph.to_project())
        self.assertGreater(len(graph.nodes),30);self.assertEqual(graph.to_pack(),restored.to_pack())
        self.assertEqual([(n.x,n.y) for n in graph.nodes.values()],[(n.x,n.y) for n in restored.nodes.values()])
        self.assertTrue(validate_pack(graph.to_pack()).ok)

    def test_native_uppercase_json_and_unsupported_archive_forms_match_install_preflight(self):
        graph=Graph.from_pack(follow());path=self.root/'resources/samcnpc/behaviors/other.zip';path.parent.mkdir(parents=True)
        with zipfile.ZipFile(path,'w') as archive:archive.writestr('behaviors/FOLLOW.JSON',json.dumps(graph.to_pack()))
        self.assertEqual(documents(path)[0][0][1]['id'],graph.pack_id)
        with self.assertRaisesRegex(StudioError,'Another JSON/ZIP'):install(graph,self.root)
        for name,payload in [('behaviors/','not a directory'),('behaviors/a\x7f.json','{}')]:
            with zipfile.ZipFile(path,'w') as archive:archive.writestr(name,payload)
            with self.assertRaises(StudioError):documents(path)
        with zipfile.ZipFile(path,'w',zipfile.ZIP_BZIP2) as archive:archive.writestr('behaviors/a.json',json.dumps(graph.to_pack()))
        with self.assertRaisesRegex(StudioError,'Unsupported ZIP'):documents(path)
