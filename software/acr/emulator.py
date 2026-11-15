"""Start the Stella emulator with a ROM held in memory (written to a temporary file for Stella)."""
from __future__ import annotations

import os
import pathlib
import re
import shutil
import subprocess
import sys
from typing import Optional

from .paths import cache_dir

WINDOWS_PATHS = [r"C:\Program Files\Stella\Stella.exe", r"C:\Program Files (x86)\Stella\Stella.exe"]


def find_stella(configured: str = "") -> Optional[str]:
    if configured and os.path.isfile(configured):
        return configured
    found = shutil.which("stella") or shutil.which("Stella")
    if found:
        return found
    if sys.platform == "win32":
        for path in WINDOWS_PATHS:
            if os.path.isfile(path):
                return path
    return None


def launch(rom: bytes, scheme: str, title: str, stella: str) -> subprocess.Popen:
    folder = cache_dir() / "play"
    folder.mkdir(exist_ok=True)
    name = re.sub(r"[^\w\- ()!.,']", "_", title).strip() or "cartridge"
    path: pathlib.Path = folder / f"{name}.a26"
    path.write_bytes(rom)
    return subprocess.Popen([stella, "-bs", scheme, str(path)])
