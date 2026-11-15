"""ROM handling: bankswitch detection, checksums, comparison."""
from __future__ import annotations

import hashlib
from dataclasses import dataclass

BANK = 0x1000
PROBE_SCHEME = "F4"  # 8 hotspots $1FF4-$1FFB: a read with them reveals 4K, F8, F6 and F4 cartridges
COMPARED = 0xFF0
AUTO_SCHEMES = ("2K", "4K", "F8", "F6", "F4")
# schemes of firmware protocol 1; the connected reader's own list replaces this one
SCHEMES = ("2K", "4K", "F8", "F8SC", "F6", "F6SC", "F4", "F4SC", "E0", "E7", "FA", "FE", "3F")


@dataclass
class Detection:
    scheme: str
    rom: bytes


def detect(probe: bytes) -> Detection:
    """Derive scheme and ROM from a 32K read with the F4 hotspots.

    The firmware selects bank b by touching $1FF4+b before every byte. A hotspot that does not exist on the
    cartridge leaves the current bank in place, so the eight 4K windows repeat in a pattern:
    4K: all equal; F8: only $1FF8/$1FF9 switch -> 2 distinct; F6: $1FF6-$1FF9 -> 4 distinct; F4: 8 distinct.
    The windows are compared below $FF0 only: reading the hotspots themselves switches banks mid-window.
    The ROM is taken from the windows whose hotspot exists. Hotspot bytes of other banks cannot be read
    without switching, so they show the bank they select (as a real 2600 sees them).
    """
    if len(probe) != 8 * BANK:
        raise ValueError("probe must be 32K")
    banks = [probe[i * BANK:(i + 1) * BANK] for i in range(8)]
    distinct = len({b[:COMPARED] for b in banks})
    if distinct == 1:
        if banks[0][:0x800] == banks[0][0x800:]:
            return Detection("2K", banks[0][:0x800])
        return Detection("4K", banks[0])
    if distinct == 2:
        return Detection("F8", banks[4] + banks[5])
    if distinct <= 4:
        return Detection("F6", b"".join(banks[2:6]))
    return Detection("F4", probe)


def md5(rom: bytes) -> str:
    return hashlib.md5(rom).hexdigest().upper()


def differences(a: bytes, b: bytes) -> list[int]:
    """Offsets where two dumps differ; a length difference counts from the shorter end."""
    n = min(len(a), len(b))
    diff = [i for i in range(n) if a[i] != b[i]]
    diff.extend(range(n, max(len(a), len(b))))
    return diff


def reset_vector(rom: bytes) -> int:
    return rom[-4] | rom[-3] << 8
