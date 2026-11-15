"""Firmware upload through the Arduino bootloader, without avrdude.

Uno and Nano (Optiboot / ATmegaBOOT) speak STK500 version 1, the Mega 2560 (wiring bootloader) STK500 version 2.
Opening the port with DTR pulsed resets the board into its bootloader, which waits about a second for a host.
"""
from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Callable, Optional

Progress = Optional[Callable[[str, int, int], None]]  # phase ("write"/"verify"), done, total


class UploadError(Exception):
    """The bootloader did not answer, answered wrongly, or the verify read back other bytes."""


@dataclass
class Target:
    protocol: int            # STK500 version 1 or 2
    signature: bytes
    page: int                # flash page size in bytes
    flash: int               # application flash in bytes (bootloader excluded)
    bauds: tuple[int, ...]


TARGETS = {
    "MEGA": Target(2, bytes([0x1E, 0x98, 0x01]), 256, 253952, (115200,)),
    "UNO": Target(1, bytes([0x1E, 0x95, 0x0F]), 128, 32256, (115200,)),
    "UNO_MCP23017": Target(1, bytes([0x1E, 0x95, 0x0F]), 128, 32256, (115200,)),
    # Nano: new bootloader 115200, old one 57600
    "NANO": Target(1, bytes([0x1E, 0x95, 0x0F]), 128, 30720, (115200, 57600)),
    "NANO_MCP23017": Target(1, bytes([0x1E, 0x95, 0x0F]), 128, 30720, (115200, 57600)),
}


def parse_hex(text: str) -> bytes:
    """Intel HEX to a flat image starting at address 0 (gaps filled with 0xFF)."""
    image = bytearray()
    base = 0
    for number, line in enumerate(text.splitlines(), 1):
        line = line.strip()
        if not line:
            continue
        if not line.startswith(":"):
            raise ValueError(f"line {number}: not Intel HEX")
        raw = bytes.fromhex(line[1:])
        if sum(raw) & 0xFF:
            raise ValueError(f"line {number}: checksum")
        length, addr, kind, data = raw[0], raw[1] << 8 | raw[2], raw[3], raw[4:4 + raw[0]]
        if len(data) != length:
            raise ValueError(f"line {number}: length")
        if kind == 0x00:
            start = base + addr
            if len(image) < start + length:
                image.extend(b"\xFF" * (start + length - len(image)))
            image[start:start + length] = data
        elif kind == 0x01:
            break
        elif kind == 0x02:
            base = (data[0] << 8 | data[1]) << 4
        elif kind == 0x04:
            base = (data[0] << 8 | data[1]) << 16
    return bytes(image)


def _pages(image: bytes, size: int) -> list[tuple[int, bytes]]:
    padded = image + b"\xFF" * (-len(image) % size)
    return [(a, padded[a:a + size]) for a in range(0, len(padded), size)]


class Stk500v1:
    OK, INSYNC, EOP = 0x10, 0x14, 0x20

    def __init__(self, port):
        self.port = port

    def _cmd(self, body: bytes, answer: int = 0) -> bytes:
        self.port.write(body + bytes([self.EOP]))
        reply = self.port.read(answer + 2)
        if len(reply) != answer + 2 or reply[0] != self.INSYNC or reply[-1] != self.OK:
            raise UploadError(f"bootloader answered {reply.hex() or 'nothing'} to {body[:1].hex()}")
        return reply[1:-1]

    def sync(self) -> None:
        for _ in range(8):
            self.port.reset_input_buffer()
            try:
                self._cmd(b"\x30")
                return
            except UploadError:
                time.sleep(0.05)
        raise UploadError("no answer from the bootloader")

    def signature(self) -> bytes:
        return self._cmd(b"\x75", 3)

    def enter(self) -> None:
        self._cmd(b"\x50")

    def leave(self) -> None:
        self._cmd(b"\x51")

    def _address(self, byte_addr: int) -> None:
        word = byte_addr >> 1
        self._cmd(bytes([0x55, word & 0xFF, word >> 8]))

    def write_page(self, addr: int, data: bytes) -> None:
        self._address(addr)
        self._cmd(bytes([0x64, len(data) >> 8, len(data) & 0xFF, ord("F")]) + data)

    def read_page(self, addr: int, length: int) -> bytes:
        self._address(addr)
        return self._cmd(bytes([0x74, length >> 8, length & 0xFF, ord("F")]), length)


class Stk500v2:
    START, TOKEN = 0x1B, 0x0E

    def __init__(self, port):
        self.port = port
        self.seq = 0

    def _cmd(self, body: bytes) -> bytes:
        frame = bytes([self.START, self.seq, len(body) >> 8, len(body) & 0xFF, self.TOKEN]) + body
        checksum = 0
        for b in frame:
            checksum ^= b
        self.port.write(frame + bytes([checksum]))
        head = self.port.read(5)
        if len(head) != 5 or head[0] != self.START or head[1] != self.seq or head[4] != self.TOKEN:
            raise UploadError(f"bootloader answered {head.hex() or 'nothing'} to {body[:1].hex()}")
        size = head[2] << 8 | head[3]
        rest = self.port.read(size + 1)
        if len(rest) != size + 1:
            raise UploadError("bootloader answer cut off")
        checksum = 0
        for b in head + rest:
            checksum ^= b
        if checksum:
            raise UploadError("bootloader answer damaged (checksum)")
        self.seq = (self.seq + 1) & 0xFF
        answer = rest[:-1]
        if answer[0] != body[0] or answer[1] != 0x00:
            raise UploadError(f"bootloader refused command {body[0]:02x} (status {answer[1]:02x})")
        return answer[2:]

    def sync(self) -> None:
        for _ in range(8):
            self.port.reset_input_buffer()
            try:
                self._cmd(b"\x01")
                return
            except UploadError:
                time.sleep(0.05)
        raise UploadError("no answer from the bootloader")

    def signature(self) -> bytes:
        return bytes(self._cmd(bytes([0x1B, 0x04, 0x30, 0x00, i, 0x00]))[0] for i in range(3))

    def enter(self) -> None:
        self._cmd(bytes([0x10, 200, 100, 25, 32, 0, 0x53, 3, 0xAC, 0x53, 0, 0]))

    def leave(self) -> None:
        self._cmd(bytes([0x11, 1, 1]))

    def _address(self, byte_addr: int) -> None:
        word = byte_addr >> 1
        self._cmd(bytes([0x06, 0x80 | (word >> 24 & 0x7F), word >> 16 & 0xFF, word >> 8 & 0xFF, word & 0xFF]))

    def write_page(self, addr: int, data: bytes) -> None:
        self._address(addr)
        self._cmd(bytes([0x13, len(data) >> 8, len(data) & 0xFF, 0xC1, 10, 0x40, 0x4C, 0x20, 0, 0]) + data)

    def read_page(self, addr: int, length: int) -> bytes:
        self._address(addr)
        return self._cmd(bytes([0x14, length >> 8, length & 0xFF, 0x20]))[:length]


def open_bootloader(device: str, baud: int):
    """Open the port and reset the board into its bootloader (DTR/RTS pulse)."""
    import serial
    port = serial.Serial()
    port.port, port.baudrate, port.timeout = device, baud, 1
    port.dtr = port.rts = False
    port.open()
    time.sleep(0.05)
    port.dtr = port.rts = True   # pulls RESET low through the 100 nF on the Arduino
    time.sleep(0.1)
    port.dtr = port.rts = False
    time.sleep(0.05)
    return port


def upload(image: bytes, target: Target, port, progress: Progress = None) -> None:
    """Write and verify an image on an open port whose board sits in its bootloader."""
    if len(image) > target.flash:
        raise UploadError(f"firmware has {len(image)} bytes, the board takes {target.flash}")
    proto = Stk500v1(port) if target.protocol == 1 else Stk500v2(port)
    proto.sync()
    signature = proto.signature()
    if signature != target.signature:
        raise UploadError(f"wrong board: signature {signature.hex()} instead of {target.signature.hex()}")
    proto.enter()
    pages = _pages(image, target.page)
    for i, (addr, data) in enumerate(pages, 1):
        proto.write_page(addr, data)
        if progress:
            progress("write", i, len(pages))
    for i, (addr, data) in enumerate(pages, 1):
        if proto.read_page(addr, len(data)) != data:
            raise UploadError(f"verify failed at 0x{addr:05X}")
        if progress:
            progress("verify", i, len(pages))
    proto.leave()


def flash(hex_text: str, device: str, board: str, progress: Progress = None) -> None:
    target = TARGETS[board]
    image = parse_hex(hex_text)
    errors = []
    for baud in target.bauds:
        port = open_bootloader(device, baud)
        try:
            upload(image, target, port, progress)
            return
        except UploadError as e:
            errors.append(f"{baud} baud: {e}")
        finally:
            port.close()
    raise UploadError("; ".join(errors))
