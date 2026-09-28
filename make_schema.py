"""The editor schema is the actual registered Behavior contract."""
from pathlib import Path
from catalog import load_schema
ROOT=Path(__file__).resolve().parent
if __name__=='__main__':
    source=ROOT/'vendor/behavior-pack-registered.schema.json'
    load_schema(source)
    (ROOT/'vendor/studio-registered.schema.json').write_bytes(source.read_bytes())
