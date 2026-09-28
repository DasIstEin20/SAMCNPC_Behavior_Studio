"""Finite mission data, deliberately separate from Graph action wiring.

Runtime admission remains authoritative for operation semantics and world authority.
"""
from __future__ import annotations
import copy
import io
import json
import re
import zipfile
from pathlib import Path
from engine import Graph, StudioError, strict_json, dump, validate_pack, atomic_write
from catalog import item_query_valid

LOCAL_ID = re.compile(r'[a-z0-9_]{1,48}\Z')
ID = re.compile(r'[a-z0-9_.-]+:[a-z0-9_./-]+\Z')
PREDICATES = ('inventory_count', 'equipment_matches', 'at_position', 'destination_count', 'soil_prepared', 'task_success')

def require(ok, message):
    if not ok: raise StudioError(message)

def record(value, fields):
    require(isinstance(value, dict) and not set(value)-set(fields), 'Unknown field or expected object')

def integer(value, low, high):
    require(type(value) is int and low <= value <= high, f'Integer must be {low}..{high}')

def number(value, low, high):
    require(type(value) in (int, float) and low <= value <= high, f'Number must be {low}..{high}')

def point(value, block=False):
    record(value, ('x','y','z')); require(set(value)=={'x','y','z'}, 'Position needs x, y, z')
    for key in value:
        (integer if block else number)(value[key], -2048 if key=='y' else -29999984, 2048 if key=='y' else 29999984)

def _schema(value, schema, root):
    """Validate the constrained JSON Schema vocabulary emitted by Behavior's catalog."""
    if '$ref' in schema:
        ref=schema['$ref']; require(ref.startswith('#/$defs/'),'Unsupported schema reference')
        return _schema(value,root['$defs'][ref.split('/')[-1]],root)
    if 'oneOf' in schema or 'anyOf' in schema:
        matches=0
        for child in schema.get('oneOf',schema.get('anyOf')):
            try: _schema(value,child,root); matches+=1
            except StudioError: pass
        require(matches==1 if 'oneOf' in schema else matches>0,'Operation does not match a registered shape'); return
    if 'const' in schema: require(value==schema['const'],'Unsupported document discriminator/version')
    if 'enum' in schema: require(value in schema['enum'],'Unsupported registered value')
    kind=schema.get('type')
    if isinstance(kind,list):
        matches=0
        for k in kind:
            try: _schema(value,{**schema,'type':k},root); matches+=1
            except StudioError: pass
        require(matches>0,'Wrong value type'); return
    if kind=='null': require(value is None,'Expected null')
    elif kind=='object':
        require(isinstance(value,dict),'Expected object')
        require(set(schema.get('required',[]))<=set(value),'Missing operation field')
        props=schema.get('properties',{})
        if schema.get('additionalProperties') is False: require(not set(value)-set(props),'Unknown operation field')
        for key, item in value.items():
            if key in props: _schema(item,props[key],root)
    elif kind=='array':
        require(isinstance(value,list),'Expected list'); integer(len(value),schema.get('minItems',0),schema.get('maxItems',16384))
        if schema.get('uniqueItems'): require(len({json.dumps(x,sort_keys=True) for x in value})==len(value),'Duplicate list entry')
        for item in value: _schema(item,schema['items'],root)
    elif kind=='string':
        require(isinstance(value,str),'Expected text'); integer(len(value),schema.get('minLength',0),schema.get('maxLength',512))
        if 'pattern' in schema: require(re.search(schema['pattern'],value) is not None,'Invalid operation text')
    elif kind in ('integer','number'):
        (integer if kind=='integer' else number)(value,schema.get('minimum',-1e20),schema.get('maximum',1e20))
    elif kind=='boolean': require(type(value) is bool,'Expected boolean')

def validate_mission(doc, packs=None):
    # Apply the same lexical and whole-document limits as the runtime.
    strict_json(dump(doc))
    record(doc,('documentType','documentVersion','id','dimensionId','requirements','stages','guards'))
    require(doc.get('documentType')=='samcnpc:mission' and type(doc.get('documentVersion')) is int and doc['documentVersion']==1,'Unsupported mission version')
    for key in ('id','dimensionId'): require(isinstance(doc.get(key),str) and len(doc[key])<=128 and ID.fullmatch(doc[key]),'Invalid namespaced ID')
    requirements=doc.get('requirements'); stages=doc.get('stages')
    require(isinstance(requirements,list) and 1<=len(requirements)<=16 and isinstance(stages,list) and 1<=len(stages)<=16,'Mission needs 1..16 requirements and stages')
    requirements_by_id={}
    for row in requirements:
        record(row,('id','predicate')); name=row.get('id')
        require(isinstance(name,str) and LOCAL_ID.fullmatch(name) and name not in requirements_by_id,'Invalid/duplicate requirement ID')
        p=row.get('predicate'); require(isinstance(p,dict),'Missing predicate'); kind=p.get('type'); require(kind in PREDICATES,'Unsupported predicate')
        fields={'inventory_count':('query','count','minimumDurability'),'equipment_matches':('query','destination','minimumDurability'),
                'at_position':('position','radius'),'destination_count':('position','itemId','count'),'soil_prepared':('cells',),'task_success':('stageId',)}[kind]
        record(p,('type',)+fields); require(set(fields)<=set(p),'Missing predicate field')
        if 'query' in p: require(isinstance(p['query'],str) and item_query_valid(p['query']),'Invalid ItemQuery')
        if 'count' in p: integer(p['count'],1,4096)
        if 'minimumDurability' in p: number(p['minimumDurability'],0,1)
        if 'destination' in p: require(p['destination'] in ('MAIN_HAND','OFF_HAND','HEAD','CHEST','LEGS','FEET'),'Invalid equipment destination')
        if 'position' in p: point(p['position'],kind=='destination_count')
        if 'radius' in p: number(p['radius'],0.25,2)
        if 'itemId' in p: require(isinstance(p['itemId'],str) and len(p['itemId'])<=128 and ID.fullmatch(p['itemId']),'Invalid item ID')
        if kind=='soil_prepared':
            cells=p['cells']; require(isinstance(cells,list) and 1<=len(cells)<=64,'Soil needs 1..64 cells')
            for cell in cells: point(cell,True)
            require(len({tuple(c[k] for k in ('x','y','z')) for c in cells})==len(cells) and len({c['y'] for c in cells})==1,'Duplicate soil cell or multiple planes')
            require(all(max(c[k] for c in cells)-min(c[k] for c in cells)<=63 for k in ('x','z')),'Soil area too wide')
        requirements_by_id[name]=p
    by_id={}; op_schema=None
    for s in stages:
        record(s,('id','pack','operation','completion','timeoutTicks','success','retries')); name=s.get('id')
        require(isinstance(name,str) and LOCAL_ID.fullmatch(name) and name not in by_id,'Invalid/duplicate stage ID')
        require(isinstance(s.get('pack'),str) and len(s['pack'])<=128 and ID.fullmatch(s['pack']),'Invalid pack ID')
        if packs is not None: require(s['pack'] in packs,'Referenced custom pack is missing from project')
        integer(s.get('timeoutTicks'),20,72000); integer(s.get('retries'),0,0)
        refs=s.get('completion'); require(isinstance(refs,list) and 1<=len(refs)<=16 and all(isinstance(x,str) for x in refs),'Missing completion references')
        require(len(set(refs))==len(refs) and set(refs)<=set(requirements_by_id),'Duplicate/unknown completion reference')
        if 'operation' in s:
            if op_schema is None: op_schema=json.loads((Path(__file__).parent/'vendor/operation.schema.json').read_text(encoding='utf-8'))
            _schema(s['operation'],op_schema,op_schema)
            require(s['operation']['parameters']['dimensionId']==doc['dimensionId'],'Operation dimension differs')
        by_id[name]=s
    visited=set(); cursor=stages[0]['id']
    while cursor is not None:
        require(isinstance(cursor,str) and cursor in by_id and cursor not in visited,'Missing success destination or cycle')
        visited.add(cursor);cursor=by_id[cursor].get('success')
    require(len(visited)==len(stages),'Unreachable stages')
    for name,p in requirements_by_id.items():
        require(any(name in s['completion'] for s in stages),'Requirement has no completion checkpoint')
        if p['type']=='task_success': require(any(s['id']==p['stageId'] and 'operation' in s and name in s['completion'] for s in stages),'Historical success needs exact operation stage')
    guards=doc.get('guards',[]); require(isinstance(guards,list) and len(guards)<=3 and all(isinstance(x,str) and len(x)<=128 and ID.fullmatch(x) for x in guards),'Invalid guards')
    require(len(set(guards))==len(guards) and not set(guards)&{s['pack'] for s in stages},'Duplicate/main guard pack')
    if packs is not None: require(set(guards)<=set(packs),'Guard pack missing from project')
    return doc

class MissionProject:
    def __init__(self, mission, packs):
        self.mission=copy.deepcopy(mission); self.packs=copy.deepcopy(packs)
    @classmethod
    def read(cls, value):
        record(value,('format','version','mission','packs'))
        require(value.get('format')=='samcnpc-mission-studio' and value.get('version')==1,'Unsupported mission project')
        p=cls(value['mission'],value['packs']); p.validate(); return p
    def project(self): return {'format':'samcnpc-mission-studio','version':1,'mission':copy.deepcopy(self.mission),'packs':copy.deepcopy(self.packs)}
    def validate(self):
        require(isinstance(self.packs,list) and 1<=len(self.packs)<=64,'Bundle needs 1..64 packs')
        ids=[]
        for p in self.packs:
            report=validate_pack(p); require(report.ok,'; '.join(report.errors)); ids.append(p['id'])
        require(len(set(ids))==len(ids),'Duplicate pack ID')
        validate_mission(self.mission,set(ids)); return self
    def export(self, path):
        self.validate()
        entries={f'behaviors/pack_{i:02d}.json':dump(p) for i,p in enumerate(self.packs)}
        entries['missions/mission.json']=dump(self.mission)
        entries['mission-manifest.json']=dump({'documentType':'samcnpc:mission_bundle','documentVersion':1,
            'packs':[p for p in entries if p.startswith('behaviors/')],'missions':['missions/mission.json']})
        require(len(entries)<=128 and all(len(x.encode('utf-8'))<=128*1024 for x in entries.values()) and sum(len(x.encode('utf-8')) for x in entries.values())<=2*1024*1024,'Bundle exceeds runtime limits')
        # Stored entries avoid compression-ratio ambiguity while staying inside the compressed cap.
        out=io.BytesIO()
        with zipfile.ZipFile(out,'w',compression=zipfile.ZIP_STORED) as archive:
            for name,text in entries.items(): archive.writestr(name,text.encode('utf-8'))
        require(len(out.getvalue())<=4*1024*1024,'Bundle exceeds compressed size limit')
        destination=Path(path); temporary=destination.with_name(destination.name+'.pending')
        temporary.write_bytes(out.getvalue()); temporary.replace(destination)

def tutorial_project():
    # A registered controller rule is enough; admission is explicitly in the mission stage.
    base={'schemaVersion':1,'id':'acceptance:tutorial','description':'Advance the explicitly admitted tutorial operation.','priority':200,'channels':['movement','look','combat','main_hand','off_hand','inventory','interaction','block_action'],
          'rules':[{'id':'advance','priority':100,'when':{'test':{'condition':'samcnpc:task_ready'}},'actions':[{'action':'samcnpc:run_navigation_task'}]}]}
    prep=copy.deepcopy(base);prep['id']='acceptance:quartermaster';prep['rules'][0]['when']['test']['condition']='samcnpc:task_inventory_ready';prep['rules'][0]['actions'][0]['action']='samcnpc:run_inventory_task'
    home={'x':0.5,'y':65,'z':0.5}; away={'x':8.5,'y':65,'z':0.5}
    def order(kind,version,parameters):return {'documentVersion':1,'type':'samcnpc:'+kind,'definitionVersion':version,'parameters':{'dimensionId':'minecraft:overworld',**parameters}}
    requirements=[{'id':'axe','predicate':{'type':'equipment_matches','query':'@axe','destination':'MAIN_HAND','minimumDurability':0.2}},
        {'id':'outbound','predicate':{'type':'task_success','stageId':'travel'}},{'id':'home','predicate':{'type':'at_position','position':home,'radius':0.75}}]
    stages=[{'id':'prepare','pack':prep['id'],'operation':order('inventory_work',3,{'work':{'kind':'ENSURE','query':'@axe','count':1,'sources':{'positions':[{'x':3,'y':65,'z':0}]},'minimumDurability':0.2,'destination':'MAIN_HAND','sourceReserve':0},'anchor':home,'workTicks':800,'budget':{'ticks':1200}}),'completion':['axe'],'timeoutTicks':1400,'retries':0,'success':'travel'},
        {'id':'travel','pack':base['id'],'operation':order('navigate',1,{'destination':away,'budget':{'ticks':600}}),'completion':['outbound'],'timeoutTicks':700,'retries':0,'success':'return'},
        {'id':'return','pack':base['id'],'operation':order('navigate',1,{'destination':home,'budget':{'ticks':600}}),'completion':['home'],'timeoutTicks':700,'retries':0,'success':None}]
    return MissionProject({'documentType':'samcnpc:mission','documentVersion':1,'id':'acceptance:tutorial','dimensionId':'minecraft:overworld','requirements':requirements,'stages':stages,'guards':[]},[prep,base])
