"""Update check against the GitHub releases (the firmware upload itself is in bootloader.py)."""
from __future__ import annotations

import json
import pathlib
import urllib.request
from dataclasses import dataclass
from typing import Optional

from .paths import cache_dir

REPO = "sfambach/arduino-atari2600-cart-reader"
RELEASES = f"https://api.github.com/repos/{REPO}/releases/latest"
TIMEOUT = 10


@dataclass
class Release:
    version: str
    url: str
    assets: dict[str, str]  # file name -> download URL


def version_tuple(version: str) -> tuple[int, ...]:
    return tuple(int(p) for p in version.lstrip("v").split(".") if p.isdigit())


def newer(candidate: str, current: str) -> bool:
    return version_tuple(candidate) > version_tuple(current)


def latest_release() -> Optional[Release]:
    request = urllib.request.Request(RELEASES, headers={"Accept": "application/vnd.github+json"})
    try:
        with urllib.request.urlopen(request, timeout=TIMEOUT) as answer:
            data = json.load(answer)
    except OSError:
        return None
    return Release(data.get("tag_name", ""), data.get("html_url", ""),
                   {a["name"]: a["browser_download_url"] for a in data.get("assets", [])})


def firmware_asset(release: Release, board: str) -> Optional[str]:
    return release.assets.get(f"AtariCartReader-{board}.hex")


def download(url: str) -> pathlib.Path:
    path = cache_dir() / url.rsplit("/", 1)[-1]
    with urllib.request.urlopen(url, timeout=60) as answer:
        path.write_bytes(answer.read())
    return path
