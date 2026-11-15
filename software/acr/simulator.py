"""A simulated reader with a cartridge, for the demo mode and the tests (speaks protocol 1)."""
from __future__ import annotations

import zlib
from typing import Optional

from .rom import BANK

SCHEMES = [("2K", 2), ("4K", 4), ("F8", 8), ("F8SC", 8), ("F6", 16), ("F6SC", 16), ("F4", 32), ("F4SC", 32),
           ("E0", 8), ("E7", 16), ("FA", 12), ("FE", 8), ("3F", 8)]
HOTSPOT = {"F8": 0x1FF8, "F6": 0x1FF6, "F4": 0x1FF4}
BANKS = {"F8": 2, "F6": 4, "F4": 8}


class SimulatedCartridge:
    """A 2K/4K/F8/F6/F4 cartridge: answers bank selection through the Fx hotspots like the hardware."""

    def __init__(self, rom: bytes, reversed_: bool = False):
        self.rom = rom
        self.reversed = reversed_
        self.bank = 0

    def _own_scheme(self) -> Optional[str]:
        return {8 * 1024: "F8", 16 * 1024: "F6", 32 * 1024: "F4"}.get(len(self.rom))

    def touch(self, addr: int) -> None:
        own = self._own_scheme()
        if own:
            first = HOTSPOT[own]
            if first <= addr < first + BANKS[own]:
                self.bank = addr - first

    def peek(self, addr: int) -> int:
        self.touch(addr)
        offset = addr & 0x0FFF
        if len(self.rom) <= BANK:
            return self.rom[offset % len(self.rom)]
        return self.rom[self.bank * BANK + offset]


class SimulatedSerial:
    def __init__(self, cartridge: SimulatedCartridge, board: str = "UNO_MCP23017", version: str = "0.2.1"):
        self.cart = cartridge
        self.timeout: Optional[float] = 1
        self.out = bytearray(f"READY Atari 2600 Cart Reader\r\nHELLO AtariCartReader {version} {board} 1\r\n".encode())
        self._line = bytearray()
        self.hello = f"HELLO AtariCartReader {version} {board} 1"

    def _answer(self, text: str) -> None:
        self.out += (text + "\r\n").encode()

    def write(self, data: bytes) -> int:
        for b in data:
            if b == 0x0A:
                self._command(self._line.decode().strip())
                self._line.clear()
            else:
                self._line.append(b)
        return len(data)

    def _command(self, line: str) -> None:
        if not line:
            return
        cmd, arg = line[0].upper(), line[1:].strip()
        if cmd == "H":
            self._answer(self.hello)
        elif cmd == "L":
            for name, kb in SCHEMES:
                self._answer(f"{name} {kb}K")
            self._answer("END")
        elif cmd == "S":
            self._answer("STATUS FB reversed -1" if self.cart.reversed else "STATUS FF ok 984")
        elif cmd == "D":
            self._dump(arg.split()[0].upper() if arg else "")
        else:
            self._answer("ERR cmd")

    def _dump(self, scheme: str) -> None:
        sizes = dict(SCHEMES)
        if scheme not in sizes:
            self._answer("ERR scheme")
            return
        if self.cart.reversed:
            self._answer("ERR cartridge inserted the wrong way round")
            return
        data = bytearray()
        if scheme in ("2K", "4K"):
            data += bytes(self.cart.peek(0x1000 + a) for a in range(sizes[scheme] * 1024))
        elif scheme[:2] in HOTSPOT:
            for b in range(BANKS[scheme[:2]]):
                for a in range(0x1000, 0x2000):
                    self.cart.touch(HOTSPOT[scheme[:2]] + b)
                    data.append(self.cart.peek(a))
        else:
            data += bytes(0xFF for _ in range(sizes[scheme] * 1024))
        self._answer(f"OK {len(data)}")
        self.out += data
        self._answer(f"CRC {zlib.crc32(data):X}")

    def readline(self) -> bytes:
        i = self.out.find(b"\n")
        if i < 0:
            line, self.out = bytes(self.out), bytearray()
            return line
        line, self.out = bytes(self.out[:i + 1]), self.out[i + 1:]
        return line

    def read(self, size: int) -> bytes:
        data, self.out = bytes(self.out[:size]), self.out[size:]
        return data

    def reset_input_buffer(self) -> None:
        self.out.clear()

    def close(self) -> None:
        pass
