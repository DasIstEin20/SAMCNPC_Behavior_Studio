"""Bounded, read-only candidate checks for the two instance-owned Behavior locations."""
import io
import os
import stat
import zipfile
from itertools import islice
from pathlib import Path

MAX_ARCHIVE=4*1024*1024
MAX_EXPANDED=2*1024*1024

def is_link(path):
    if path.is_symlink(): return True
    # Path.is_junction is not available on every supported Python version.
    attributes=getattr(path.lstat(),'st_file_attributes',0) if path.exists() else 0
    return bool(attributes & getattr(stat,'FILE_ATTRIBUTE_REPARSE_POINT',0))

def documents(path):
    from engine import StudioError, MAX_BYTES, strict_json
    before=path.stat()
    if is_link(path) or not path.is_file() or before.st_size>MAX_ARCHIVE: raise StudioError('Unsafe/oversized ZIP: '+path.name)
    with path.open('rb') as stream: raw=stream.read(MAX_ARCHIVE+1)
    after=path.stat()
    if (before.st_size,before.st_mtime_ns,before.st_ino)!=(after.st_size,after.st_mtime_ns,after.st_ino) or len(raw)>MAX_ARCHIVE: raise StudioError('ZIP changed during inspection: '+path.name)
    if not raw.startswith(b'PK\x03\x04'): raise StudioError('ZIP preambles/empty archives are unsupported: '+path.name)
    total=0;seen=set();packs=[]
    try:
        with zipfile.ZipFile(io.BytesIO(raw)) as archive:
            entries=archive.infolist()
            if len(entries)>128: raise StudioError('ZIP exceeds 128 entries.')
            for info in entries:
                name=info.filename;parts=name.removesuffix('/').split('/')
                if not name or len(name)>240 or '\\' in name or ':' in name or any(ord(c)<32 or ord(c)==127 for c in name) or len(parts)>8 or any(not p or p in ('.','..') or p.endswith(('.', ' ')) for p in parts): raise StudioError('Unsafe ZIP member: '+name)
                if name.casefold() in seen: raise StudioError('Ambiguous ZIP members: '+name)
                seen.add(name.casefold())
                kind=stat.S_IFMT(info.external_attr>>16)
                if kind not in (0,stat.S_IFREG,stat.S_IFDIR) or info.flag_bits&1 or info.compress_type not in (zipfile.ZIP_STORED,zipfile.ZIP_DEFLATED) or info.extract_version>20: raise StudioError('Unsupported ZIP member: '+name)
                if info.file_size>MAX_BYTES or info.file_size>max(1,info.compress_size)*200: raise StudioError('ZIP entry exceeds decompression bounds: '+name)
                if kind==stat.S_IFDIR and not info.is_dir() or info.is_dir() and info.file_size!=0: raise StudioError('Inconsistent ZIP directory: '+name)
                if info.is_dir(): continue
                with archive.open(info) as stream: data=stream.read(MAX_BYTES+1)
                total+=len(data)
                if len(data)>MAX_BYTES or total>MAX_EXPANDED: raise StudioError('ZIP expanded bytes exceed limits.')
                if len(parts)>=2 and parts[0]=='behaviors' and parts[-1].lower().endswith('.json'):
                    packs.append((name,strict_json(data.decode('utf-8-sig'))))
        if not packs: raise StudioError('ZIP contains no behaviors/**/*.json documents: '+path.name)
        return packs,total
    except (zipfile.BadZipFile,NotImplementedError,UnicodeError,RuntimeError) as error:
        raise StudioError('Invalid ZIP '+path.name+': '+str(error)) from error

def check_candidate(graph,instance,format='json'):
    from engine import StudioError,require_export,safe_filename,validate_pack,strict_json,MAX_BYTES,dump,installation_text
    if format not in ('json','zip'): raise StudioError('Unknown install format.')
    pack,report=require_export(graph);instance=Path(instance).expanduser().absolute()
    filename=safe_filename(pack['id'])
    destination=instance/('config' if format=='json' else 'resources')/'samcnpc'/'behaviors'/Path(filename).with_suffix('.'+format)
    ids=set();count=0
    expanded=(len(dump(pack).encode('utf-8'))+sum(len(installation_text(pack,lang).encode('utf-8')) for lang in ('en','pl','de'))) if format=='zip' else 0
    for root,suffix,limit in (('config','.json',64),('resources','.zip',16)):
        directory=instance/root/'samcnpc'/'behaviors'
        for entry in (instance,instance/root,instance/root/'samcnpc',directory):
            if is_link(entry): raise StudioError('Install path cannot contain a link/junction.')
            if entry.exists() and not entry.is_dir(): raise StudioError('Expected directory: '+str(entry))
        entries=[]
        if directory.exists():
            with os.scandir(directory) as scanned: entries=[Path(entry.path) for entry in islice(scanned,1025)]
        if len(entries)+int(destination.parent==directory and not destination.exists())>1024: raise StudioError('Behavior directory exceeds 1024 entries.')
        files=[p for p in entries if p.suffix.lower()==suffix]
        if len(files)+int(destination.parent==directory and not destination.exists())>limit: raise StudioError('Too many Behavior '+suffix+' files.')
        for path in sorted(files,key=lambda p:p.name):
            if is_link(path) or not path.is_file(): raise StudioError('Unsafe Behavior file: '+path.name)
            if path==destination: continue
            if suffix=='.json':
                with path.open('rb') as stream: raw=stream.read(MAX_BYTES+1)
                if len(raw)>MAX_BYTES: raise StudioError('Oversized behavior JSON: '+path.name)
                rows=[(path.name,strict_json(raw.decode('utf-8-sig')))]
            else:
                rows,size=documents(path);expanded+=size
                if expanded>8*1024*1024: raise StudioError('ZIP collection exceeds total expanded byte limit.')
            for name,other in rows:
                count+=1;result=validate_pack(other)
                if not result.ok: raise StudioError('Invalid existing behavior '+path.name+'!/'+name+': '+str(result.errors[:4]))
                if other['id'] in ids: raise StudioError('Duplicate behavior ID: '+other['id'])
                ids.add(other['id'])
    if count+1>64: raise StudioError('Combined JSON/ZIP documents exceed 64.')
    if pack['id'] in ids: raise StudioError('Another JSON/ZIP already contains ID '+pack['id'])
    return destination,pack,report
