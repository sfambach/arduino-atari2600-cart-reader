"""Command line: python -m acr.cli <port> status | list | read <file> [scheme] [kb]"""
from __future__ import annotations

import argparse
import sys

from . import rom
from .reader import Reader, ReaderError


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="acr", description="Atari 2600 Cart Reader")
    parser.add_argument("port")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("status")
    sub.add_parser("list")
    read = sub.add_parser("read")
    read.add_argument("file")
    read.add_argument("scheme", nargs="?", default="auto")
    read.add_argument("kb", nargs="?", type=int)
    args = parser.parse_args(argv)

    try:
        reader = Reader.open(args.port)
        print(f"firmware {reader.hello.version}, board {reader.hello.board}")
        if args.command == "status":
            s = reader.status()
            print(f"orientation {'ok' if s.orientation_ok else 'reversed'}, supply {s.supply}")
        elif args.command == "list":
            for s in reader.schemes():
                print(f"{s.name} {s.kb}K")
        else:
            progress = lambda done, total: print(f"\r{done}/{total}", end="", file=sys.stderr)
            if args.scheme.lower() == "auto":
                found = rom.detect(reader.dump(rom.PROBE_SCHEME, progress=progress))
                scheme, data = found.scheme, found.rom
            else:
                scheme, data = args.scheme.upper(), reader.dump(args.scheme, args.kb, progress)
            print(file=sys.stderr)
            with open(args.file, "wb") as f:
                f.write(data)
            print(f"{args.file}: {len(data)} bytes, scheme {scheme}, md5 {rom.md5(data)}")
        reader.close()
    except ReaderError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
