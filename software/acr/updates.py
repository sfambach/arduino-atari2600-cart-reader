"""Update check against the GitHub releases, and firmware upload with avrdude."""
from __future__ import annotations

import json
import pathlib
import shutil
import subprocess
import urllib.request
from dataclasses import dataclass
from typing import Optional

from .paths import cache_dir

REPO = "sfambach/arduino-atari2600-cart-reader"
RELEASES = f"https://api.github.com/repos/{REPO}/releases/latest"
TIMEOUT = 10

# avrdude part and programmer per board (Arduino bootloaders); the Nano tries the old bootloader too
AVRDUDE = {
    "MEGA": [("m2560", "wiring", 115200)],
    "UNO": [("m328p", "arduino", 115200)],
    "UNO_MCP23017": [("m328p", "arduino", 115200)],
    "NANO": [("m328p", "arduino", 115200), ("m328p", "arduino", 57600)],
    "NANO_MCP23017": [("m328p", "arduino", 115200), ("m328p", "arduino", 57600)],
}


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


def find_avrdude() -> Optional[str]:
    return shutil.which("avrdude")


def flash(hex_file: pathlib.Path, port: str, board: str, avrdude: str) -> str:
    """Upload a .hex through the Arduino bootloader; returns avrdude's output, raises on failure."""
    log = []
    for part, programmer, baud in AVRDUDE[board]:
        cmd = [avrdude, "-p", part, "-c", programmer, "-P", port, "-b", str(baud), "-D",
               "-U", f"flash:w:{hex_file}:i"]
        result = subprocess.run(cmd, capture_output=True, text=True)
        log.append(result.stdout + result.stderr)
        if result.returncode == 0:
            return "\n".join(log)
    raise RuntimeError("\n".join(log))
