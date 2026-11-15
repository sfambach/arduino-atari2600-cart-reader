"""Game collection: every saved ROM with title, scheme and cover, to play it again later."""
from __future__ import annotations

import datetime
import json
import pathlib
import re
from dataclasses import asdict, dataclass
from typing import Optional

from .paths import data_dir
from .rom import md5


@dataclass
class Game:
    md5: str
    title: str
    scheme: str
    file: str
    saved: str
    cover: Optional[str] = None


class Library:
    def __init__(self, folder: Optional[pathlib.Path] = None):
        self.folder = folder or data_dir() / "library"
        self.folder.mkdir(parents=True, exist_ok=True)
        self.index = self.folder / "library.json"

    def games(self) -> list[Game]:
        if not self.index.exists():
            return []
        entries = json.loads(self.index.read_text(encoding="utf-8"))
        return [Game(**e) for e in entries]

    def _write(self, games: list[Game]) -> None:
        self.index.write_text(json.dumps([asdict(g) for g in games], indent=1), encoding="utf-8")

    def add(self, rom: bytes, title: str, scheme: str, cover: Optional[pathlib.Path] = None) -> Game:
        checksum = md5(rom)
        name = re.sub(r"[^\w\- ()!.,']", "_", title).strip() or checksum
        path = self.folder / f"{name}.a26"
        path.write_bytes(rom)
        game = Game(checksum, title, scheme, path.name, datetime.datetime.now().isoformat(timespec="seconds"),
                    str(cover) if cover else None)
        games = [g for g in self.games() if g.md5 != checksum]
        games.insert(0, game)
        self._write(games)
        return game

    def remove(self, game: Game) -> None:
        self._write([g for g in self.games() if g.md5 != game.md5])

    def rom(self, game: Game) -> bytes:
        return (self.folder / game.file).read_bytes()
