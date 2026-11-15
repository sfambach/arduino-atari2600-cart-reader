"""Game titles by MD5 and box art, both downloaded on demand from the open libretro collections.

Nothing is shipped with the program: the game list and every cover are fetched the first time they are
needed and kept in the cache folder.
"""
from __future__ import annotations

import pathlib
import re
import urllib.parse
import urllib.request
from typing import Optional

from .paths import cache_dir

DAT_URL = ("https://raw.githubusercontent.com/libretro/libretro-database/master/"
           "metadat/no-intro/Atari%20-%202600.dat")
COVER_URL = "https://raw.githubusercontent.com/libretro-thumbnails/Atari_-_2600/master/Named_Boxarts/{}.png"
TIMEOUT = 15

_ENTRY = re.compile(r'game \(\s*name "(?P<name>[^"]*)".*?md5 (?P<md5>[0-9A-Fa-f]{32})', re.S)


def parse_dat(text: str) -> dict[str, str]:
    return {m["md5"].upper(): m["name"] for m in _ENTRY.finditer(text)}


def _download(url: str, target: pathlib.Path) -> pathlib.Path:
    with urllib.request.urlopen(url, timeout=TIMEOUT) as answer:
        data = answer.read()
    target.write_bytes(data)
    return target


class GameDatabase:
    def __init__(self, folder: Optional[pathlib.Path] = None):
        self.folder = folder or cache_dir()
        self._titles: Optional[dict[str, str]] = None

    def titles(self, download: bool = True) -> dict[str, str]:
        if self._titles is None:
            dat = self.folder / "atari2600.dat"
            if not dat.exists():
                if not download:
                    return {}
                _download(DAT_URL, dat)
            self._titles = parse_dat(dat.read_text(encoding="utf-8", errors="replace"))
        return self._titles

    def title(self, md5: str, download: bool = True) -> Optional[str]:
        try:
            return self.titles(download).get(md5.upper())
        except OSError:
            return None

    def cover(self, title: str, download: bool = True) -> Optional[pathlib.Path]:
        # libretro replaces these characters in thumbnail file names
        name = re.sub(r'[&*/:`<>?\\|"]', "_", title)
        covers = self.folder / "covers"
        covers.mkdir(exist_ok=True)
        path = covers / f"{name}.png"
        if path.exists():
            return path
        if not download:
            return None
        try:
            return _download(COVER_URL.format(urllib.parse.quote(name)), path)
        except OSError:
            return None
