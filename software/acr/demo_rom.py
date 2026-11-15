"""A tiny 4K demo program (rainbow background), written for this project and free to use.

Used by the demo mode, so the program can be tried without a reader or a cartridge.
"""

VSYNC, VBLANK, WSYNC, COLUBK = 0x00, 0x01, 0x02, 0x09
ORIGIN = 0xF000


def build() -> bytes:
    code = bytearray()
    labels: dict[str, int] = {}

    def emit(*b: int) -> None:
        code.extend(b)

    def label(name: str) -> None:
        labels[name] = ORIGIN + len(code)

    def bne(name: str) -> None:
        offset = labels[name] - (ORIGIN + len(code) + 2)
        emit(0xD0, offset & 0xFF)

    emit(0x78, 0xD8, 0xA2, 0xFF, 0x9A, 0xA9, 0x00)   # sei, cld, ldx #$FF, txs, lda #0
    label("clear")
    emit(0x95, 0x00, 0xCA)                             # sta 0,x / dex
    bne("clear")
    label("frame")
    emit(0xA9, 0x02, 0x85, VSYNC, 0x85, WSYNC, 0x85, WSYNC, 0x85, WSYNC, 0xA9, 0x00, 0x85, VSYNC)
    emit(0xA2, 37)
    label("vblank")
    emit(0x85, WSYNC, 0xCA)
    bne("vblank")
    emit(0x85, VBLANK, 0xA2, 192)                      # A = 0: picture on, 192 lines
    label("picture")
    emit(0x86, COLUBK, 0x85, WSYNC, 0xCA)              # line number = colour
    bne("picture")
    emit(0xA9, 0x02, 0x85, VBLANK, 0xA2, 30)
    label("overscan")
    emit(0x85, WSYNC, 0xCA)
    bne("overscan")
    emit(0x4C, labels["frame"] & 0xFF, labels["frame"] >> 8)

    rom = bytearray(code) + bytes(0x1000 - len(code))
    rom[0xFFC:0x1000] = bytes([ORIGIN & 0xFF, ORIGIN >> 8] * 2)
    return bytes(rom)
