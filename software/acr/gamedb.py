"""Game titles by MD5 and box art, downloaded on demand from the open libretro collections and Stella.

Nothing is shipped with the program: the game lists and every cover are fetched the first time they are
needed and kept in the cache folder. The No-Intro list names the original releases; Stella's list also knows
modified versions such as the single games of a multicart, so it fills the gaps.
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
STELLA_URL = "https://raw.githubusercontent.com/stella-emu/stella/master/src/emucore/stella.pro"
COVER_URL = "https://raw.githubusercontent.com/libretro-thumbnails/Atari_-_2600/master/Named_Boxarts/{}.png"
TIMEOUT = 15

_ENTRY = re.compile(r'game \(\s*name "(?P<name>[^"]*)".*?md5 (?P<md5>[0-9A-Fa-f]{32})', re.S)


def parse_dat(text: str) -> dict[str, str]:
    return {m["md5"].upper(): m["name"] for m in _ENTRY.finditer(text)}


_STELLA_ENTRY = re.compile(r'"Cart\.MD5" "(?P<md5>[0-9A-Fa-f]{32})"(?P<body>.*?)\n""', re.S)
_STELLA_FIELD = re.compile(r'"(?P<key>[\w.]+)" "(?P<value>(?:[^"\\]|\\.)*)"')


def parse_stella(text: str) -> dict[str, tuple[str, Optional[str]]]:
    """Stella's properties: MD5 -> (name, name of the original game for its box art, if Stella gives one)."""
    entries = {}
    for m in _STELLA_ENTRY.finditer(text):
        fields = {f["key"]: f["value"] for f in _STELLA_FIELD.finditer(m["body"])}
        if "Cart.Name" in fields:
            entries[m["md5"].upper()] = (fields["Cart.Name"], fields.get("Bezel.Name"))
    return entries


def _download(url: str, target: pathlib.Path) -> pathlib.Path:
    with urllib.request.urlopen(url, timeout=TIMEOUT) as answer:
        data = answer.read()
    target.write_bytes(data)
    return target


def cover_names(title: str) -> list[str]:
    """Names to try for the box art, best first.

    The game list and the thumbnail collection do not always use the same tags: "RealSports Tennis (USA, Europe)
    (En,Fr,De,Es,It)" has its cover as "RealSports Tennis (USA)". So language tags are dropped and each region is
    tried on its own.
    """
    names = [title]
    base = re.sub(r"\s*\((?:[A-Z][a-z](?:,[A-Z][a-z])*)\)", "", title).strip()  # (En,Fr,De)
    names.append(base)
    m = re.match(r"^(.*?)\s*\(([^)]*)\)(.*)$", base)
    if m:
        name, regions, rest = m.groups()
        for region in [r.strip() for r in regions.split(",")] + ["USA", "Europe", "World"]:
            names.append(f"{name} ({region}){rest}".strip())
            names.append(f"{name} ({region})")
        names.append(name)
    unique = []
    for n in names:
        if n not in unique:
            unique.append(n)
    return unique


class GameDatabase:
    def __init__(self, folder: Optional[pathlib.Path] = None):
        self.folder = folder or cache_dir()
        self._titles: Optional[dict[str, str]] = None
        self._artwork: dict[str, str] = {}

    def _read(self, name: str, url: str, download: bool) -> Optional[str]:
        path = self.folder / name
        if not path.exists():
            if not download:
                return None
            try:
                _download(url, path)
            except OSError:
                return None
        return path.read_text(encoding="utf-8", errors="replace")

    def titles(self, download: bool = True) -> dict[str, str]:
        if self._titles is None:
            dat = self._read("atari2600.dat", DAT_URL, download)
            stella = self._read("stella.pro", STELLA_URL, download)
            if dat is None and stella is None:
                return {}
            titles = {}
            for md5, (name, original) in parse_stella(stella or "").items():
                titles[md5] = name
                if original:
                    self._artwork[name] = original
            titles.update(parse_dat(dat or ""))
            if stella is None and not download:
                return titles  # Stella's list is fetched on the next lookup that may download
            self._titles = titles
        return self._titles

    def title(self, md5: str, download: bool = True) -> Optional[str]:
        try:
            return self.titles(download).get(md5.upper())
        except OSError:
            return None

    def cover(self, title: str, download: bool = True) -> Optional[pathlib.Path]:
        covers = self.folder / "covers"
        covers.mkdir(exist_ok=True)
        # cached under the full title, whichever name the collection used
        path = covers / (re.sub(r'[&*/:`<>?\\|"]', "_", title) + ".png")
        if path.exists():
            return path
        if not download:
            return None
        names = cover_names(self._artwork[title]) if title in self._artwork else []
        for name in names + cover_names(title):
            # libretro replaces these characters in thumbnail file names
            name = re.sub(r'[&*/:`<>?\\|"]', "_", name)
            try:
                return _download(COVER_URL.format(urllib.parse.quote(name)), path)
            except OSError:
                continue
        return None
