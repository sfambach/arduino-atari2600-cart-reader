"""Where the program keeps its data (library, downloaded game list and covers)."""
from __future__ import annotations

import os
import pathlib
import sys

APP = "AtariCartReader"


def data_dir() -> pathlib.Path:
    if sys.platform == "win32":
        base = pathlib.Path(os.environ.get("APPDATA", pathlib.Path.home() / "AppData" / "Roaming"))
    else:
        base = pathlib.Path(os.environ.get("XDG_DATA_HOME", pathlib.Path.home() / ".local" / "share"))
    path = base / APP
    path.mkdir(parents=True, exist_ok=True)
    return path


def cache_dir() -> pathlib.Path:
    if sys.platform == "win32":
        base = pathlib.Path(os.environ.get("LOCALAPPDATA", pathlib.Path.home() / "AppData" / "Local"))
    else:
        base = pathlib.Path(os.environ.get("XDG_CACHE_HOME", pathlib.Path.home() / ".cache"))
    path = base / APP
    path.mkdir(parents=True, exist_ok=True)
    return path
