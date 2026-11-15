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
LINUX_PATHS = ["/usr/games/stella", "/usr/local/games/stella", "/snap/bin/stella"]
FLATPAK_ID = "io.github.stella_emu.Stella"
FLATPAK = "flatpak:" + FLATPAK_ID


def find_stella(configured: str = "") -> Optional[str]:
    if configured and os.path.isfile(configured):
        return configured
    found = shutil.which("stella") or shutil.which("Stella")
    if found:
        return found
    for path in WINDOWS_PATHS if sys.platform == "win32" else LINUX_PATHS:
        if os.path.isfile(path):
            return path
    flatpak = shutil.which("flatpak")
    if flatpak and subprocess.run([flatpak, "info", FLATPAK_ID], capture_output=True).returncode == 0:
        return FLATPAK
    return None


def launch(rom: bytes, scheme: str, title: str, stella: str) -> subprocess.Popen:
    folder = cache_dir() / "play"
    folder.mkdir(exist_ok=True)
    name = re.sub(r"[^\w\- ()!.,']", "_", title).strip() or "cartridge"
    path: pathlib.Path = folder / f"{name}.a26"
    path.write_bytes(rom)
    command = ["flatpak", "run", f"--filesystem={folder}", FLATPAK_ID] if stella == FLATPAK else [stella]
    log = folder / "stella.log"
    with open(log, "wb") as out:
        process = subprocess.Popen(command + ["-bs", scheme, str(path)], stdout=out, stderr=subprocess.STDOUT)
    try:
        code = process.wait(timeout=2)
    except subprocess.TimeoutExpired:
        return process  # still running: Stella is up
    if code != 0:
        raise RuntimeError(f"Stella ended with code {code}:\n" + log.read_text(errors="replace")[-1500:])
    return process
