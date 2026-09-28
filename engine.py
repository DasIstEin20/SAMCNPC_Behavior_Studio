"""Pure data layer: graph, source-derived validation and safe file exports.

The graph is a rule/condition graph, NOT an execution sequence. No code execution,
Minecraft commands or arbitrary Python expressions are accepted as node data.
"""
from __future__ import annotations
import copy
import json
import math
import os
import re
import tempfile
import uuid
import zipfile
from dataclasses import dataclass, field
from decimal import Decimal
from pathlib import Path
from typing import Any

BASE = Path(__file__).resolve().parent
from catalog import load_schema, item_query_valid, CatalogError

def _catalog(path):
    value=load_schema(path)
    labels=json.loads((BASE/'vendor/labels-pl.json').read_text(encoding='utf-8'))
    for row in value['conditions']+value['actions']:
        label=labels.get(row['id'],{})
        for name in ('label','description'):
            if name in label: row[name]=label[name]
        for name,spec in row['args'].items():
            spec['label']=label.get('args',{}).get(name,spec['label'])
    return value

CATALOG = _catalog(BASE/'vendor/behavior-pack-registered.schema.json')
CONDITIONS = {x['id']: x for x in CATALOG['conditions']}
ACTIONS = {x['id']: x for x in CATALOG['actions']}
CHANNELS = CATALOG['channels']
BUILTINS = set(CATALOG['builtins'])
MAX_BYTES = 128*1024
MAX_PROJECT_BYTES = 4*1024*1024
ID_PATTERN = re.compile(r'^[a-z0-9_.-]+:[a-z0-9_./-]+$')
RULE_PATTERN = re.compile(r'^[a-z0-9_.-]+$')
KINDS = {'rule','condition','all','any','not','action'}

class StudioError(ValueError):
    pass

def refresh_catalog(path):
    try: candidate=_catalog(path)
    except (OSError,ValueError,TypeError,KeyError,AttributeError) as error: raise StudioError(str(error)) from error
    # Keep imported dictionaries/lists alive; an open graph and its widgets retain their identities.
    CATALOG.clear();CATALOG.update(candidate)
    CONDITIONS.clear();CONDITIONS.update({x['id']:x for x in candidate['conditions']})
    ACTIONS.clear();ACTIONS.update({x['id']:x for x in candidate['actions']})
    CHANNELS[:]=candidate['channels'];BUILTINS.clear();BUILTINS.update(candidate['builtins'])
    return CATALOG


@dataclass
class Report:
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    @property
    def ok(self): return not self.errors


def strict_json(text: str, *, project: bool = False) -> Any:
    """Reject duplicates, NaN, surrogate strings and oversized trees before import."""
    limit = MAX_PROJECT_BYTES if project else MAX_BYTES
    try:
        if len(text.encode('utf-8')) > limit: raise StudioError(f'Plik przekracza limit {limit} bajtów.')
    except UnicodeError as e: raise StudioError('Niepoprawny Unicode.') from e
    def pairs(items):
        result = {}
        for k,v in items:
            if k in result: raise StudioError(f'Powtórzone pole JSON: {k}')
            result[k]=v
        return result
    def number(s):
        if len(s)>64: raise StudioError('Liczba ma ponad 64 znaki.')
        x=Decimal(s)
        if not x.is_finite(): raise StudioError('Wymagana skończona liczba.')
        # Keep small exact schema integers exact; reject extreme numeric magnitudes.
        if x==x.to_integral_value() and abs(x)<Decimal('1e18'): return int(x)
        f=float(x)
        if not math.isfinite(f): raise StudioError('Liczba poza obsługiwanym zakresem.')
        if x != x.to_integral_value() and f.is_integer():
            raise StudioError('Liczba ułamkowa traci precyzję; nie zaokrąglam jej do liczby całkowitej.')
        return f
    def bad(s): raise StudioError(f'Niedozwolona wartość JSON: {s}')
    try:
        value=json.loads(text.removeprefix('\ufeff'),object_pairs_hook=pairs,
                         parse_int=number,parse_float=number,parse_constant=bad)
    except (json.JSONDecodeError, RecursionError, ArithmeticError, ValueError) as e:
        raise StudioError(f'Niepoprawny JSON: {e}') from e
    count=0
    def walk(v,depth):
        nonlocal count
        count+=1
        if depth>32 or count>(65000 if project else 16384): raise StudioError('Przekroczony limit głębokości/liczby wartości JSON.')
        if isinstance(v,str):
            if len(v)>(16384 if project else 512): raise StudioError('Zbyt długi tekst w JSON.')
            try: v.encode('utf-8')
            except UnicodeError as e: raise StudioError('Niesparowany znak Unicode.') from e
        if isinstance(v,dict):
            for k,item in v.items():
                if len(k)>512: raise StudioError('Zbyt długa nazwa pola.')
                try: k.encode('utf-8')
                except UnicodeError as e: raise StudioError('Niepoprawna nazwa pola Unicode.') from e
                walk(item,depth+1)
        elif isinstance(v,list):
            for item in v: walk(item,depth+1)
    walk(value,0)
    return value


def dump(data: Any) -> str:
    return json.dumps(data,ensure_ascii=False,indent=2,allow_nan=False)+'\n'


def validate_pack(pack: Any, *, external=True) -> Report:
    """Local mirror of inspected compiler rules; final acceptance is always in Forge."""
    r=Report()
    def error(path,msg): r.errors.append(f'{path}: {msg}')
    def record(v,path,allowed,required):
        if not isinstance(v,dict): error(path,'wymagany obiekt'); return False
        for k in set(v)-set(allowed): error(path,f'nieznane pole {k}')
        for k in set(required)-set(v): error(path,f'brak pola {k}')
        return True
    def integer(v,path,lo,hi):
        if isinstance(v,bool) or not isinstance(v,(int,float)) or not math.isfinite(v) or int(v)!=v or not lo<=v<=hi:
            error(path,f'wymagana liczba całkowita {lo}..{hi}')
    def text(v,path,n,pattern=None):
        if not isinstance(v,str) or len(v)>n or (pattern and not pattern.fullmatch(v)):
            error(path,'niepoprawny identyfikator/tekst'); return
        try: v.encode('utf-8')
        except UnicodeError: error(path,'niepoprawny Unicode')
    def sequence(v,path,lo,hi):
        if not isinstance(v,list) or not lo<=len(v)<=hi: error(path,f'wymagana lista {lo}..{hi} elementów'); return False
        return True
    def args(v,meta,path):
        if not isinstance(v,dict): error(path,'args muszą być obiektem'); return
        fields=meta['args']
        for k in set(v)-set(fields): error(path,f'nieznany argument {k}')
        for k,spec in fields.items():
            if k not in v:
                if spec['required']: error(path,f'brak argumentu {k}')
                continue
            val=v[k]; p=path+'.'+k
            if spec['type']=='boolean':
                if not isinstance(val,bool): error(p,'wymagane true/false')
            elif spec['type']=='string':
                if not isinstance(val,str) or ('enum' in spec and val not in spec['enum']) or ('enum' not in spec and (not spec['minLength']<=len(val)<=spec['maxLength'] or not item_query_valid(val))): error(p,'niedozwolona wartość')
            elif spec['type']=='integer': integer(val,p,spec['minimum'],spec['maximum'])
            elif isinstance(val,bool) or not isinstance(val,(float,int)) or not math.isfinite(val) or not spec['minimum']<=val<=spec['maximum']:
                error(p,f"wymagana skończona liczba {spec['minimum']}..{spec['maximum']}")
        for name,spec in fields.items():
            related=spec.get('x-samcnpc-greater-than')
            if not related: continue
            reference=v.get(related,fields[related].get('default'))
            value=v.get(name)
            default=spec.get('x-samcnpc-default-from')
            if value is None and name not in v and default and isinstance(reference,(int,float)) and not isinstance(reference,bool): value=reference+default['offset']
            if isinstance(value,(int,float)) and not isinstance(value,bool) and isinstance(reference,(int,float)) and not isinstance(reference,bool):
                if not (value>reference and spec['minimum']<=value<=spec['maximum']): error(path,name+' must be greater than '+related+' and within its declared bounds')
    def expr(v,path,depth=0):
        if depth>=8: error(path,'warunek przekracza 8 poziomów (root = poziom 1)'); return
        if not isinstance(v,dict) or len(v)!=1 or next(iter(v),None) not in {'test','all','any','not'}:
            error(path,'dokładnie jedno pole: test / all / any / not'); return
        k=next(iter(v)); sub=v[k]
        if k=='test':
            if not record(sub,path+'.test',{'condition','args'},{'condition'}): return
            cid=sub.get('condition'); meta=CONDITIONS.get(cid) if isinstance(cid,str) else None
            if meta is None: error(path,f'nieznany warunek {cid!r}'); return
            args(sub.get('args',{}),meta,path+'.test.args')
        elif k=='not': expr(sub,path+'.not',depth+1)
        elif sequence(sub,path+'.'+k,1,16):
            for i,item in enumerate(sub): expr(item,f'{path}.{k}[{i}]',depth+1)
    if not record(pack,'pack',{'schemaVersion','id','description','priority','channels','rules'},
                  {'schemaVersion','id','description','priority','channels','rules'}): return r
    integer(pack.get('schemaVersion'),'schemaVersion',1,1)
    text(pack.get('id'),'id',128,ID_PATTERN)
    text(pack.get('description'),'description',512)
    integer(pack.get('priority'),'priority',-100000,100000)
    pid=pack.get('id')
    if isinstance(pid,str) and pid in BUILTINS:
        if external: error('id','kolizja z paczką wbudowaną. Zmień ID przed eksportem do config.')
        else: r.warnings.append('Referencja wbudowana: nie kopiuj jej ID do config; loader odrzuci duplikat.')
    ch=pack.get('channels',[])
    if sequence(ch,'channels',1,16):
        if any(not isinstance(x,str) or x not in CHANNELS for x in ch): error('channels','nieznany kanał')
        elif len(set(ch))!=len(ch): error('channels','kanały muszą być unikalne')
    allowed=set(x for x in ch if isinstance(x,str)) if isinstance(ch,list) else set()
    rules=pack.get('rules')
    advanced=set(); ids=[]
    if sequence(rules,'rules',1,256):
        for i,rule in enumerate(rules):
            path=f'rules[{i}]'
            if not record(rule,path,{'id','priority','cooldownTicks','when','actions'},{'id','priority','when','actions'}): continue
            text(rule.get('id'),path+'.id',96,RULE_PATTERN); ids.append(rule.get('id'))
            integer(rule.get('priority'),path+'.priority',-100000,100000)
            if 'cooldownTicks' in rule: integer(rule['cooldownTicks'],path+'.cooldownTicks',0,120000)
            expr(rule.get('when'),path+'.when')
            actions=rule.get('actions'); seen_channels={}
            if sequence(actions,path+'.actions',1,16):
                for j,a in enumerate(actions):
                    p=f'{path}.actions[{j}]'
                    if not record(a,p,{'action','args'},{'action'}): continue
                    aid=a.get('action'); meta=ACTIONS.get(aid) if isinstance(aid,str) else None
                    if meta is None: error(p,f'nieznana akcja {aid!r}'); continue
                    args(a.get('args',{}),meta,p+'.args')
                    required=set(meta['channels'])
                    if not required<=allowed: error(p,'brak kanałów: '+', '.join(sorted(required-allowed)))
                    for c in required:
                        if c in seen_channels:
                            r.warnings.append(f'{path}: akcje {seen_channels[c]+1} i {j+1} konkurują o {c}. Lista nie jest sekwencją; późniejsza może nie zostać wybrana.')
                            break
                    for c in required: seen_channels.setdefault(c,j)
                    if meta['advanced']: advanced.add(aid)
                    if rule.get('cooldownTicks',0) and (aid.startswith('samcnpc:run_') or aid in {'samcnpc:move_to_summoner','samcnpc:move_to_target'}):
                        r.warnings.append(f'{p}: cooldown może zwolnić długą akcję; zazwyczaj użyj 0.')
            if isinstance(rule.get('when'),dict) and rule['when']=={'test':{'condition':'samcnpc:always'}} and any(a.get('action')=='samcnpc:stop_movement' for a in (actions or []) if isinstance(a,dict)):
                r.warnings.append(f'{path}: bezwarunkowe stop_movement może blokować inne reguły zależnie od priorytetów.')
        valid_ids=[x for x in ids if isinstance(x,str)]
        if len(set(valid_ids))!=len(valid_ids): error('rules','powtórzone ID reguły')
    if advanced:
        r.warnings.append('Zaawansowane run_*/begin_* tylko kontynuują istniejący task/job. Sam import lub przypisanie tej paczki nie tworzy zadania.')
        r.warnings.append('TaskService wymaga oryginalnego ID task packa. Usunięcie go z przypisań anuluje task; custom paczka nie jest automatycznym zamiennikiem.')
    try:
        raw=dump(pack)
        strict_json(raw)
    except (ValueError,TypeError,OverflowError,RecursionError) as e: error('JSON',str(e))
    r.warnings=list(dict.fromkeys(r.warnings))
    return r

@dataclass
class Node:
    id: str
    kind: str
    ref: str = ''
    args: dict = field(default_factory=dict)
    rule_id: str = ''
    priority: int = 100
    cooldown: int = 0
    has_cooldown: bool = False
    has_args: bool = False
    x: float = 0
    y: float = 0

@dataclass
class Graph:
    pack_id: str = 'custom:my_behavior'
    description: str = 'Moja paczka zachowań SAMCNPC.'
    priority: int = 100
    channels: list[str] = field(default_factory=lambda:['look'])
    nodes: dict[str,Node] = field(default_factory=dict)
    edges: list[tuple[str,str]] = field(default_factory=list)
    def add(self,kind,ref='',**kwargs):
        if kind not in KINDS or len(self.nodes)>=4096: raise StudioError('Nieznany typ lub za dużo węzłów.')
        nid=uuid.uuid4().hex[:12]; n=Node(nid,kind,ref,**kwargs); self.nodes[nid]=n; return n
    def incoming(self,nid): return [a for a,b in self.edges if b==nid]
    def outgoing(self,nid): return [b for a,b in self.edges if a==nid]
    def connect(self,src,dst):
        if src==dst or src not in self.nodes or dst not in self.nodes: raise StudioError('Niepoprawne końce połączenia.')
        if (src,dst) in self.edges: raise StudioError('To połączenie już istnieje.')
        a,b=self.nodes[src],self.nodes[dst]
        if a.kind=='rule':
            if b.kind!='action': raise StudioError('Wyjście reguły łączy się tylko z akcją, nie z kolejną regułą.')
            if self.incoming(dst): raise StudioError('Akcja może należeć tylko do jednej reguły.')
            if len(self.outgoing(src))>=16: raise StudioError('Maksymalnie 16 akcji na regułę.')
        elif a.kind in {'condition','all','any','not'}:
            if b.kind not in {'all','any','not','rule'}: raise StudioError('Warunek łączy się z AND / OR / NOT lub wejściem reguły.')
            if b.kind in {'rule','not'} and self.incoming(dst): raise StudioError('To wejście przyjmuje jeden warunek. Użyj AND lub OR.')
            if len(self.incoming(dst))>=16: raise StudioError('Maksymalnie 16 dzieci wyrażenia.')
        else: raise StudioError('Akcje nie mają wyjść. To nie jest sekwencja kroków.')
        visited=set()
        def reaches(n):
            if n==src: return True
            if n in visited: return False
            visited.add(n)
            return any(reaches(c) for c in self.outgoing(n))
        if reaches(dst): raise StudioError('Cykl w grafie jest niedozwolony.')
        self.edges.append((src,dst))
    def remove(self,nid):
        self.nodes.pop(nid,None); self.edges=[(a,b) for a,b in self.edges if nid not in (a,b)]
    def needed_channels(self):
        ch=set()
        for n in self.nodes.values():
            if n.kind=='action' and n.ref in ACTIONS: ch.update(ACTIONS[n.ref]['channels'])
        return [x for x in CHANNELS if x in ch] or ['look']
    def to_pack(self):
        used=set(); stack=set(); expanded=0
        def expression(nid,depth=0):
            nonlocal expanded
            expanded+=1
            if expanded>16384: raise StudioError('Po rozwinięciu graf jest za duży.')
            if depth>=8: raise StudioError('Warunek ma więcej niż 8 poziomów.')
            if nid in stack: raise StudioError('Cykl w grafie.')
            stack.add(nid); used.add(nid); n=self.nodes[nid]
            if n.kind=='condition':
                t={'condition':n.ref}
                if n.has_args or n.args: t['args']=copy.deepcopy(n.args)
                value={'test':t}
            elif n.kind in {'all','any','not'}:
                children=self.incoming(nid)
                if not children or len(children)>16 or n.kind=='not' and len(children)!=1:
                    raise StudioError(f'{n.kind.upper()}: niepoprawna liczba wejść.')
                v=[expression(c,depth+1) for c in children]
                value={n.kind:v[0] if n.kind=='not' else v}
            else: raise StudioError('Nieprawidłowy węzeł w drzewie warunków.')
            stack.remove(nid); return value
        rules=[]
        for n in self.nodes.values():
            if n.kind!='rule': continue
            used.add(n.id); ins=self.incoming(n.id); outs=self.outgoing(n.id)
            if len(ins)!=1: raise StudioError(f'Reguła {n.rule_id}: podłącz dokładnie jeden warunek.')
            if not 1<=len(outs)<=16: raise StudioError(f'Reguła {n.rule_id}: podłącz od 1 do 16 akcji.')
            r={'id':n.rule_id,'priority':n.priority}
            if n.has_cooldown or n.cooldown: r['cooldownTicks']=n.cooldown
            r['when']=expression(ins[0]); r['actions']=[]
            for aid in outs:
                a=self.nodes[aid]
                if a.kind!='action' or len(self.incoming(aid))!=1: raise StudioError('Niepoprawne połączenie akcji.')
                used.add(aid); row={'action':a.ref}
                if a.has_args or a.args: row['args']=copy.deepcopy(a.args)
                r['actions'].append(row)
            rules.append(r)
        orphan=set(self.nodes)-used
        if orphan: raise StudioError(f'Niepodłączone węzły: {len(orphan)}. Połącz je albo usuń; eksport nie może ich po cichu pomijać.')
        return dict(schemaVersion=1,id=self.pack_id,description=self.description,priority=self.priority,channels=self.channels[:],rules=rules)
    @classmethod
    def from_pack(cls,pack):
        report=validate_pack(pack,external=False)
        if not report.ok: raise StudioError('\n'.join(report.errors[:20]))
        g=cls(pack['id'],pack['description'],int(pack['priority']),pack['channels'][:])
        def add_expr(e):
            k=next(iter(e))
            if k=='test':
                t=e[k]; return g.add('condition',t['condition'],args=copy.deepcopy(t.get('args',{})),has_args='args' in t)
            n=g.add(k)
            for child in ([e[k]] if k=='not' else e[k]): g.connect(add_expr(child).id,n.id)
            return n
        for rule in pack['rules']:
            r=g.add('rule',rule_id=rule['id'],priority=int(rule['priority']),cooldown=int(rule.get('cooldownTicks',0)),has_cooldown='cooldownTicks' in rule)
            g.connect(add_expr(rule['when']).id,r.id)
            for a in rule['actions']:
                node=g.add('action',a['action'],args=copy.deepcopy(a.get('args',{})),has_args='args' in a)
                g.connect(r.id,node.id)
        g.layout(); return g
    def layout(self):
        laid=set(); top=55.0
        for r in [n for n in self.nodes.values() if n.kind=='rule']:
            local=set()
            def depth(nid,vis=None):
                vis=set() if vis is None else vis
                if nid in vis: return 0
                vis.add(nid)
                return 1+max((depth(x,vis.copy()) for x in self.incoming(nid)),default=-1)
            roots=self.incoming(r.id); maxdepth=max((depth(x) for x in roots),default=0)
            y=[top]
            def place(nid,d):
                if nid in local: return self.nodes[nid].y
                local.add(nid); n=self.nodes[nid]; kids=self.incoming(nid)
                ys=[place(x,d+1) for x in kids]
                yy=sum(ys)/len(ys) if ys else y[0]
                if not ys:y[0]+=135
                if nid not in laid: n.x=45+(maxdepth-d)*285; n.y=yy
                laid.add(nid); return n.y
            for root in roots: place(root,0)
            center=(top+max(top,y[0]-135))/2
            r.x=45+(maxdepth+1)*285;r.y=center;laid.add(r.id)
            outs=self.outgoing(r.id)
            for i,aid in enumerate(outs):
                self.nodes[aid].x=r.x+310; self.nodes[aid].y=top+i*135;laid.add(aid)
            top=max(y[0],top+135*max(1,len(outs)))+55
        for nid in set(self.nodes)-laid:
            self.nodes[nid].x=45;self.nodes[nid].y=top;top+=135
    def to_project(self):
        return {'format':'samcnpc-studio','version':1,'targetCommit':CATALOG['commit'],
                'pack':{'id':self.pack_id,'description':self.description,'priority':self.priority,'channels':self.channels},
                'nodes':[copy.deepcopy(n.__dict__) for n in self.nodes.values()], 'edges':[list(e) for e in self.edges]}
    @classmethod
    def from_project(cls,v):
        if not isinstance(v,dict) or v.get('format')!='samcnpc-studio' or v.get('version')!=1: raise StudioError('Nieobsługiwany projekt Studio.')
        meta=v.get('pack'); nodes=v.get('nodes'); edges=v.get('edges')
        if not isinstance(meta,dict) or not isinstance(nodes,list) or not isinstance(edges,list) or len(nodes)>4096 or len(edges)>8192: raise StudioError('Niepoprawny lub zbyt duży projekt.')
        if not isinstance(meta.get('id'),str) or not isinstance(meta.get('description'),str) or type(meta.get('priority')) is not int or not isinstance(meta.get('channels'),list): raise StudioError('Niepoprawne metadane projektu.')
        if any(not isinstance(c,str) or c not in CHANNELS for c in meta['channels']): raise StudioError('Nieznane kanały projektu.')
        g=cls(meta['id'],meta['description'],meta['priority'],meta['channels'])
        fields=set(Node.__dataclass_fields__)
        for row in nodes:
            if not isinstance(row,dict) or set(row)!=fields: raise StudioError('Niepoprawny rekord węzła.')
            if not isinstance(row['id'],str) or not re.fullmatch('[a-zA-Z0-9_-]{1,64}',row['id']) or row['id'] in g.nodes: raise StudioError('Niepoprawne/powtórzone ID węzła.')
            if not isinstance(row['kind'],str) or row['kind'] not in KINDS: raise StudioError('Nieznany typ węzła.')
            if any(not isinstance(row[k],str) for k in ['ref','rule_id']) or not isinstance(row['args'],dict): raise StudioError('Niepoprawne dane węzła.')
            if any(type(row[k]) is not int for k in ['priority','cooldown']) or any(type(row[k]) is not bool for k in ['has_args','has_cooldown']): raise StudioError('Niepoprawne parametry reguły.')
            if any(isinstance(row[k],bool) or not isinstance(row[k],(int,float)) or not math.isfinite(row[k]) or abs(row[k])>1e6 for k in ['x','y']): raise StudioError('Niepoprawna pozycja węzła.')
            if row['kind']=='condition' and row['ref'] not in CONDITIONS or row['kind']=='action' and row['ref'] not in ACTIONS: raise StudioError('Węzeł spoza katalogu tej wersji.')
            g.nodes[row['id']]=Node(**row)
        for e in edges:
            if not isinstance(e,list) or len(e)!=2 or not all(isinstance(s,str) for s in e): raise StudioError('Niepoprawne połączenie.')
            g.connect(*e)
        return g


def atomic_write(path: Path,text: str):
    path=Path(path)
    if path.is_symlink(): raise StudioError('Nie zapisuję przez dowiązanie symboliczne.')
    data=text.encode('utf-8')
    path.parent.mkdir(parents=True,exist_ok=True)
    fd,name=tempfile.mkstemp(prefix='.'+path.stem+'_',suffix='.tmp',dir=path.parent)
    try:
        with os.fdopen(fd,'wb') as f: f.write(data);f.flush();os.fsync(f.fileno())
        os.replace(name,path)
    finally:
        if os.path.exists(name): os.unlink(name)


def require_export(g: Graph) -> tuple[dict,Report]:
    pack=g.to_pack();report=validate_pack(pack)
    if report.errors: raise StudioError('\n'.join(report.errors[:25]))
    return pack,report


def safe_filename(pack_id):
    # IDs may contain '/' but must never become filesystem paths.
    return re.sub('[^a-zA-Z0-9_.-]','_',pack_id)+'.json'


def installation_text(pack,lang='en'):
    filename=safe_filename(pack['id']);zipname=Path(filename).with_suffix('.zip').name
    intro={
      'en': 'Choose one format for each pack ID. JSON is installed in config; ZIP goes directly into resources without unpacking. Both locations belong to the Minecraft instance. This is an SAMCNPC external resource, not a vanilla resource pack or datapack.',
      'pl': 'Wybierz jeden format dla danego ID paczki. JSON trafia do config, ZIP bez wypakowywania do resources. Oba katalogi należą do instancji Minecraft. To zewnętrzny zasób SAMCNPC, nie vanilla resource pack ani datapack.',
      'de': 'Pro Pack-ID ein Format wählen. JSON wird in config installiert; ZIP kommt ohne Entpacken direkt nach resources. Beide Verzeichnisse gehören zur Minecraft-Instanz. Dies ist eine externe SAMCNPC-Ressource, kein Vanilla-Resourcepack oder Datapack.'}
    note={
      'en':'assign replaces the assigned pack list. Use an idle NPC. run_*/begin_* continue existing durable tasks; they do not create a task. Invalid candidates retain the last working registry.',
      'pl':'assign zastępuje listę przypisanych paczek. Użyj bezczynnego NPC. run_*/begin_* kontynuują istniejące trwałe zadania; nie tworzą zadania. Błędny reload zachowuje ostatni poprawny rejestr.',
      'de':'assign ersetzt die zugewiesene Pack-Liste. Einen untätigen NPC verwenden. run_*/begin_* setzen bestehende dauerhafte Tasks fort; sie erzeugen keine Tasks. Ein ungültiger Reload behält das letzte gültige Register.'}
    return f"SAMCNPC Behavior Studio 1.2.0 — {pack['id']}\n\n{intro.get(lang,intro['en'])}\n\nJSON: config/samcnpc/behaviors/{filename}\nZIP:  resources/samcnpc/behaviors/{zipname}\nArchive: behaviors/{filename}\n\n/samcnpc behavior reload\n/samcnpc behavior packs\n/samcnpc behavior assign Sam {pack['id']}\n/samcnpc behavior diagnostics Sam\n\n{note.get(lang,note['en'])}\n"


def export_zip(path: Path,g: Graph, *, overwrite=False):
    pack,report=require_export(g)
    if path.is_symlink(): raise StudioError('Nie zapisuję przez dowiązanie.')
    if path.exists() and not overwrite: raise StudioError('ZIP already exists; explicit overwrite is required.')
    path.parent.mkdir(parents=True,exist_ok=True)
    fd,tmp=tempfile.mkstemp(prefix='.'+path.stem,suffix='.tmp',dir=path.parent);os.close(fd)
    try:
        with zipfile.ZipFile(tmp,'w',zipfile.ZIP_STORED) as z:
            z.writestr('behaviors/'+safe_filename(pack['id']),dump(pack))
            z.writestr('INSTALL_PL.txt',installation_text(pack,'pl'))
            z.writestr('INSTALL_EN.txt',installation_text(pack,'en'))
            z.writestr('INSTALL_DE.txt',installation_text(pack,'de'))
        os.replace(tmp,path)
    finally:
        if os.path.exists(tmp):os.unlink(tmp)


def check_install(g: Graph,instance: Path,format='json'):
    from pack_install import check_candidate
    return check_candidate(g,instance,format)


def install(g: Graph,instance: Path, *, overwrite=False,format='json'):
    path,pack,report=check_install(g,instance,format)
    if path.exists() and not overwrite: raise StudioError('File exists; explicit overwrite confirmation is required.')
    if path.exists():
        backup=path.with_suffix(path.suffix+'.bak')
        if backup.is_symlink(): raise StudioError('Backup cannot be a link.')
        atomic_write_bytes(backup,path.read_bytes())
    if format=='zip': export_zip(path,g,overwrite=overwrite)
    else: atomic_write(path,dump(pack))
    return path


def atomic_write_bytes(path,data):
    if path.is_symlink(): raise StudioError('Cannot write through a link.')
    path.parent.mkdir(parents=True,exist_ok=True)
    fd,tmp=tempfile.mkstemp(prefix='.'+path.stem,suffix='.tmp',dir=path.parent)
    try:
        with os.fdopen(fd,'wb') as stream: stream.write(data);stream.flush();os.fsync(stream.fileno())
        os.replace(tmp,path)
    finally:
        if os.path.exists(tmp): os.unlink(tmp)
