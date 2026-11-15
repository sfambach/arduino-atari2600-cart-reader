#!/usr/bin/env python3
"""Copy the master config.h (firmware/AtariCartReader) into every test sketch.

usage: sync_config.py          copy
       sync_config.py --check  exit 1 if a copy differs
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
MASTER = ROOT / 'firmware' / 'AtariCartReader' / 'config.h'


def main():
    master = MASTER.read_bytes()
    copies = [p.parent / 'config.h' for p in sorted((ROOT / 'test').glob('*/*.ino'))]
    differ = [c for c in copies if not c.exists() or c.read_bytes() != master]
    if '--check' in sys.argv:
        for c in differ:
            print('differs:', c.relative_to(ROOT))
        sys.exit(1 if differ else 0)
    for c in differ:
        c.write_bytes(master)
        print('updated:', c.relative_to(ROOT))
    print(f'{len(copies)} copies, {len(differ)} updated')


if __name__ == '__main__':
    main()
