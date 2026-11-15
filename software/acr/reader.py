"""Serial protocol 1 of the AtariCartReader firmware (see firmware/AtariCartReader/AtariCartReader.ino)."""
from __future__ import annotations

import time
import zlib
from dataclasses import dataclass
from typing import Callable, Optional, Protocol

BAUD = 115200  # must match SERIAL_BAUD in firmware/AtariCartReader/config.h
PROTOCOL = 1
CHUNK = 256


class ReaderError(Exception):
    """The reader answered with an error, did not answer, or sent damaged data."""


class SerialLike(Protocol):
    timeout: Optional[float]

    def write(self, data: bytes) -> int: ...
    def readline(self) -> bytes: ...
    def read(self, size: int) -> bytes: ...
    def close(self) -> None: ...
    def reset_input_buffer(self) -> None: ...


@dataclass
class Hello:
    version: str
    board: str
    protocol: int


@dataclass
class Status:
    data_bits: int
    orientation_ok: bool
    supply: Optional[int]  # ADC counts (0-1023), None when the supply stayed off


@dataclass
class Scheme:
    name: str
    kb: int


def list_ports() -> list[tuple[str, str]]:
    from serial.tools import list_ports as lp
    return [(p.device, p.description or p.device) for p in lp.comports()]


class Reader:
    def __init__(self, port: SerialLike):
        self.port = port
        self.hello: Optional[Hello] = None

    @classmethod
    def open(cls, name: str, baud: int = BAUD) -> "Reader":
        import serial
        reader = cls(serial.Serial(name, baud, timeout=3))
        reader.connect()
        return reader

    def connect(self) -> Hello:
        # Opening the port resets most Arduinos; the firmware then prints READY and HELLO by itself.
        deadline = time.monotonic() + 4
        while time.monotonic() < deadline:
            line = self._readline(allow_empty=True)
            if line.startswith("HELLO"):
                self.hello = self._parse_hello(line)
                return self.hello
            if not line:
                break
        self.port.reset_input_buffer()
        self._send("H")
        self.hello = self._parse_hello(self._expect("HELLO"))
        return self.hello

    @staticmethod
    def _parse_hello(line: str) -> Hello:
        parts = line.split()
        if len(parts) < 5:
            raise ReaderError(f"unexpected answer: {line}")
        hello = Hello(version=parts[2], board=parts[3], protocol=int(parts[4]))
        if hello.protocol != PROTOCOL:
            raise ReaderError(f"firmware speaks protocol {hello.protocol}, this program {PROTOCOL}: update the firmware")
        return hello

    def close(self) -> None:
        self.port.close()

    def _send(self, line: str) -> None:
        self.port.write((line + "\n").encode("ascii"))

    def _readline(self, allow_empty: bool = False) -> str:
        raw = self.port.readline()
        if not raw and not allow_empty:
            raise ReaderError("no answer from the reader")
        return raw.decode("ascii", errors="replace").strip()

    def _expect(self, prefix: str) -> str:
        while True:
            line = self._readline()
            if line.startswith("ERR"):
                raise ReaderError(line[3:].strip() or "error")
            if line.startswith(prefix):
                return line

    def status(self) -> Status:
        self._send("S")
        parts = self._expect("STATUS").split()
        supply = int(parts[3])
        return Status(int(parts[1], 16), parts[2] == "ok", None if supply < 0 else supply)

    def schemes(self) -> list[Scheme]:
        self._send("L")
        result = []
        while True:
            line = self._readline()
            if line == "END":
                return result
            if line.startswith("ERR"):
                raise ReaderError(line[3:].strip())
            name, size = line.split()
            result.append(Scheme(name, int(size.rstrip("K"))))

    def dump(self, scheme: str, kb: Optional[int] = None,
             progress: Optional[Callable[[int, int], None]] = None) -> bytes:
        self._send(f"D {scheme} {kb}" if kb else f"D {scheme}")
        size = int(self._expect("OK").split()[1])
        data = bytearray()
        while len(data) < size:
            chunk = self.port.read(min(CHUNK, size - len(data)))
            if not chunk:
                raise ReaderError(f"only {len(data)} of {size} bytes received")
            data += chunk
            if progress:
                progress(len(data), size)
        crc = int(self._expect("CRC").split()[1], 16)
        if crc != zlib.crc32(data):
            raise ReaderError("checksum wrong, please read again")
        return bytes(data)
