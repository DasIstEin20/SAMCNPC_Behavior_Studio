"""Offline validation/conversion without importing Tkinter."""
import argparse
import sys
from pathlib import Path
from engine import *

def main():
    p=argparse.ArgumentParser(description='SAMCNPC Behavior Studio — lokalna walidacja / eksport')
    p.add_argument('input',type=Path,help='Plik .json albo .samgraph')
    p.add_argument('--json-out',type=Path);p.add_argument('--zip-out',type=Path);p.add_argument('--reference',action='store_true',help='Zezwól na oryginalne ID builtin tylko do analizy (nie do eksportu).')
    a=p.parse_args()
    try:
        if a.input.stat().st_size>MAX_PROJECT_BYTES:raise StudioError('Za duży plik.')
        value=strict_json(a.input.read_text(encoding='utf-8'),project=a.input.suffix=='.samgraph')
        g=Graph.from_project(value) if value.get('format')=='samcnpc-studio' else Graph.from_pack(value)
        pack=g.to_pack();r=validate_pack(pack,external=not a.reference)
        for msg in r.errors:print('ERROR:',msg)
        for msg in r.warnings:print('WARN:',msg)
        if not r.ok:return 1
        if a.json_out:require_export(g);atomic_write(a.json_out,dump(pack))
        if a.zip_out:export_zip(a.zip_out,g)
        print('LOCAL PASS — ostateczna walidacja nadal wymaga /samcnpc behavior reload w grze.')
        return 0
    except (OSError,ValueError,TypeError,AttributeError) as e:print('ERROR:',e);return 1
if __name__=='__main__':sys.exit(main())
