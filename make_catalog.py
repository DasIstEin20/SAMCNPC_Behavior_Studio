"""Bundle a registered Behavior schema from a repository path or schema file."""
import json
import sys
from pathlib import Path
from catalog import load_schema
ROOT=Path(__file__).resolve().parent

def main():
    source=Path(sys.argv[1]) if len(sys.argv)>1 else ROOT/'vendor/behavior-pack-registered.schema.json'
    if source.is_dir(): source=source/'contracts/behavior-pack-registered.schema.json'
    catalog=load_schema(source)
    raw=source.read_bytes()
    (ROOT/'vendor/behavior-pack-registered.schema.json').write_bytes(raw)
    (ROOT/'vendor/studio-registered.schema.json').write_bytes(raw)
    (ROOT/'vendor/catalog.json').write_text(json.dumps(catalog,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(f"Catalog {catalog['catalogVersion']}: {len(catalog['conditions'])} conditions, {len(catalog['actions'])} actions; {catalog['commit']}")
if __name__=='__main__': main()
