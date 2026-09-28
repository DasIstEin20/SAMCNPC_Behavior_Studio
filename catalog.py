"""Bounded adapter for BehaviorSchemaApi's registered schema; no executable plugins."""
from __future__ import annotations
import copy
import hashlib
import json
import math
import re
from pathlib import Path

MAX_SCHEMA_BYTES = 1024 * 1024
ITEM_ID = re.compile(r'[a-z0-9_.-]+:[a-z0-9_./-]+')
ROLES = frozenset(('axe','pickaxe','shovel','hoe','food','placeable_block','tool','shield','armor','melee_weapon','ranged_weapon','ammunition'))

class CatalogError(ValueError):
    pass

def item_query_valid(text):
    if not isinstance(text,str) or not 1 <= len(text) <= 512: return False
    parts=text.split('|')
    return 1 <= len(parts) <= 8 and len(set(parts)) == len(parts) and all(
        part[1:] in ROLES if part.startswith('@') else 3 <= len(part) <= 128 and ITEM_ID.fullmatch(part) for part in parts)

def load_schema(path: Path):
    path=Path(path)
    if path.is_dir(): path=path/'contracts'/'behavior-pack-registered.schema.json'
    with path.open('rb') as stream: raw=stream.read(MAX_SCHEMA_BYTES+1)
    if len(raw)>MAX_SCHEMA_BYTES: raise CatalogError('Catalog exceeds 1 MiB.')
    def pairs(entries):
        result={}
        for k,v in entries:
            if k in result: raise CatalogError('Duplicate catalog key: '+k)
            result[k]=v
        return result
    try:
        value=json.loads(raw.decode('utf-8-sig'),object_pairs_hook=pairs,parse_constant=lambda x: (_ for _ in ()).throw(CatalogError('Non-finite catalog number.')))
        return from_schema(value,hashlib.sha256(raw).hexdigest())
    except (UnicodeError,RecursionError,TypeError,KeyError,AttributeError,ValueError) as error:
        raise CatalogError('Invalid registered Behavior catalog: '+str(error)) from error

def from_schema(schema, fingerprint='in-memory'):
    def require(ok,message):
        if not ok: raise CatalogError(message)
    require(isinstance(schema,dict),'Schema must be an object.')
    require(schema.get('x-samcnpc-definition-semantics-version')==1,'Unsupported definition semantics.')
    version=schema.get('x-samcnpc-catalog-version')
    require(type(version) is int and 1<=version<=10000,'Invalid catalog version.')
    require(schema['properties']['schemaVersion'].get('const')==1,'Unsupported behavior document version.')
    channels=schema['properties']['channels']['items']['enum']
    builtins=schema['x-samcnpc-builtins']
    require(isinstance(channels,list) and 1<=len(channels)<=16 and all(isinstance(x,str) and 1<=len(x)<=40 for x in channels) and len(set(channels))==len(channels),'Invalid channels.')
    require(isinstance(builtins,list) and len(builtins)<=128 and all(isinstance(x,str) and len(x)<=128 and ITEM_ID.fullmatch(x) for x in builtins) and len(set(builtins))==len(builtins),'Invalid built-in IDs.')
    def component_rows(key,field):
        variants=schema['$defs'][key]['oneOf']
        require(isinstance(variants,list) and 1<=len(variants)<=256,'Invalid component count.')
        rows=[];seen=set()
        for variant in variants:
            require(variant.get('type')=='object' and variant.get('additionalProperties') is False,'Component must be closed.')
            props=variant['properties'];identifier=props[field]['const']
            require(isinstance(identifier,str) and len(identifier)<=128 and ITEM_ID.fullmatch(identifier) and identifier not in seen,'Invalid/duplicate component ID.')
            seen.add(identifier)
            required_channels=variant.get('x-samcnpc-required-channels')
            require(isinstance(required_channels,list) and all(x in channels for x in required_channels) and len(set(required_channels))==len(required_channels),'Unknown required channel.')
            shape=props['args']; required=shape.get('required',[]); fields=shape['properties']
            require(shape.get('additionalProperties') is False and isinstance(fields,dict) and len(fields)<=32,'Invalid argument object.')
            require(isinstance(required,list) and all(x in fields for x in required),'Invalid required fields.')
            arguments={}
            for name,value in fields.items():
                require(isinstance(name,str) and re.fullmatch('[A-Za-z][A-Za-z0-9_]{0,63}',name),'Invalid field name.')
                spec=copy.deepcopy(value);kind=spec.get('type')
                require(kind in ('number','integer','boolean','string'),'Unsupported field type.')
                spec['required']=name in required;spec['label']=name;spec['description']=value.get('description','')
                require(isinstance(spec['description'],str) and len(spec['description'])<=2048,'Invalid description.')
                if kind in ('number','integer'):
                    lo=spec.get('minimum');hi=spec.get('maximum')
                    require(all(type(n) in (int,float) and math.isfinite(n) for n in (lo,hi)) and lo<=hi,'Invalid numeric bounds.')
                    spec['suggested']=spec.get('default',lo)
                elif kind=='boolean':spec['suggested']=spec.get('default',False)
                elif 'enum' in spec:
                    enum=spec['enum']; require(isinstance(enum,list) and 1<=len(enum)<=128 and all(isinstance(x,str) and len(x)<=128 for x in enum) and len(set(enum))==len(enum),'Invalid enum.')
                    spec['suggested']=enum[0]
                else:
                    require(spec.get('x-samcnpc-text-format')=='item-query','Unsupported text format; update Studio before using this catalog.')
                    require(type(spec.get('minLength')) is int and type(spec.get('maxLength')) is int and 1<=spec['minLength']<=spec['maxLength']<=512,'Invalid text bounds.')
                    spec['suggested']=spec.get('x-samcnpc-example','minecraft:coal')
                    require(item_query_valid(spec['suggested']),'Invalid item-query example.')
                if 'x-samcnpc-default-from' in spec:
                    relation=spec['x-samcnpc-default-from']
                    require(isinstance(relation,dict) and relation.get('parameter') in fields and type(relation.get('offset')) in (int,float) and math.isfinite(relation['offset']),'Invalid related default.')
                if 'x-samcnpc-greater-than' in spec: require(spec['x-samcnpc-greater-than'] in fields,'Invalid related bound.')
                arguments[name]=spec
            label=variant.get('title',identifier.split(':',1)[1].replace('_',' '))
            require(isinstance(label,str) and len(label)<=256,'Invalid component title.')
            advanced=identifier.split(':',1)[1].startswith(('run_','begin_'))
            rows.append(dict(id=identifier,label=label,description=variant.get('description',label),args=arguments,channels=list(required_channels),advanced=advanced,requires=None,version=variant.get('x-samcnpc-component-version',1)))
        return rows
    return dict(catalogFormat=2,repository='SAMCNPC Behavior registered API',commit='schema:'+fingerprint,schemaVersion=1,
                catalogVersion=version,conditions=component_rows('test','condition'),actions=component_rows('action','action'),
                channels=list(channels),builtins=list(builtins),note='Generated from BehaviorSchemaApi; final activation uses the actual Forge compiler.')
