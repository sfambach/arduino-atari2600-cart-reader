import pytest

from acr import bootloader as bl


def hex_of(image: bytes) -> str:
    lines = []
    for a in range(0, len(image), 16):
        chunk = image[a:a + 16]
        rec = bytes([len(chunk), (a >> 8) & 0xFF, a & 0xFF, 0]) + chunk
        lines.append(":" + (rec + bytes([-sum(rec) & 0xFF])).hex().upper())
    lines.append(":00000001FF")
    return "\n".join(lines)


class FakeV1:
    """Optiboot-like STK500v1 bootloader with 32K flash."""

    def __init__(self, signature=bytes([0x1E, 0x95, 0x0F])):
        self.flash = bytearray(b"\xFF" * 32768)
        self.signature = signature
        self.out = bytearray()
        self.buf = bytearray()
        self.addr = 0
        self.left = False

    def reset_input_buffer(self):
        self.out.clear()

    def read(self, n):
        data, self.out = bytes(self.out[:n]), self.out[n:]
        return data

    def write(self, data):
        self.buf += data
        while self.buf:
            cmd = self.buf[0]
            need = {0x30: 2, 0x75: 2, 0x50: 2, 0x51: 2, 0x55: 4}.get(cmd)
            if cmd in (0x64, 0x74):
                if len(self.buf) < 4:
                    return
                size = self.buf[1] << 8 | self.buf[2]
                need = 5 + (size if cmd == 0x64 else 0)
            if need is None or len(self.buf) < need:
                return
            frame, self.buf = bytes(self.buf[:need]), self.buf[need:]
            assert frame[-1] == 0x20
            body = b""
            if cmd == 0x75:
                body = self.signature
            elif cmd == 0x55:
                self.addr = (frame[1] | frame[2] << 8) * 2
            elif cmd == 0x64:
                size = frame[1] << 8 | frame[2]
                self.flash[self.addr:self.addr + size] = frame[4:4 + size]
            elif cmd == 0x74:
                size = frame[1] << 8 | frame[2]
                body = bytes(self.flash[self.addr:self.addr + size])
            elif cmd == 0x51:
                self.left = True
            self.out += b"\x14" + body + b"\x10"
        return len(data)


class FakeV2:
    """Wiring-like STK500v2 bootloader of the Mega 2560."""

    def __init__(self):
        self.flash = bytearray(b"\xFF" * 262144)
        self.out = bytearray()
        self.buf = bytearray()
        self.addr = 0
        self.left = False

    def reset_input_buffer(self):
        self.out.clear()

    def read(self, n):
        data, self.out = bytes(self.out[:n]), self.out[n:]
        return data

    def write(self, data):
        self.buf += data
        while len(self.buf) >= 5:
            size = self.buf[2] << 8 | self.buf[3]
            if len(self.buf) < 6 + size:
                return
            frame, self.buf = bytes(self.buf[:6 + size]), self.buf[6 + size:]
            check = 0
            for b in frame:
                check ^= b
            assert check == 0 and frame[0] == 0x1B and frame[4] == 0x0E
            seq, body = frame[1], frame[5:5 + size]
            cmd, answer = body[0], b""
            if cmd == 0x01:
                answer = b"\x08STK500_2"
            elif cmd == 0x1B:
                answer = bytes([[0x1E, 0x98, 0x01][body[4]], 0])
            elif cmd == 0x06:
                self.addr = (int.from_bytes(body[1:5], "big") & 0x7FFFFFFF) * 2
            elif cmd == 0x13:
                n = body[1] << 8 | body[2]
                self.flash[self.addr:self.addr + n] = body[10:10 + n]
            elif cmd == 0x14:
                n = body[1] << 8 | body[2]
                answer = bytes(self.flash[self.addr:self.addr + n]) + b"\x00"
            elif cmd == 0x11:
                self.left = True
            reply = bytes([cmd, 0]) + answer
            msg = bytes([0x1B, seq, len(reply) >> 8, len(reply) & 0xFF, 0x0E]) + reply
            check = 0
            for b in msg:
                check ^= b
            self.out += msg + bytes([check])
        return len(data)


IMAGE = bytes((i * 37 + 11) & 0xFF for i in range(5000))


def test_parse_hex_roundtrip():
    assert bl.parse_hex(hex_of(IMAGE)) == IMAGE


def test_parse_hex_rejects_bad_checksum():
    text = hex_of(IMAGE[:16]).replace(":10", ":11", 1)
    with pytest.raises(ValueError):
        bl.parse_hex(text)


def test_upload_v1():
    port = FakeV1()
    seen = []
    bl.upload(IMAGE, bl.TARGETS["UNO_MCP23017"], port, lambda p, d, t: seen.append(p))
    assert bytes(port.flash[:len(IMAGE)]) == IMAGE and port.left
    assert "write" in seen and "verify" in seen


def test_upload_v1_wrong_board():
    with pytest.raises(bl.UploadError, match="wrong board"):
        bl.upload(IMAGE, bl.TARGETS["UNO"], FakeV1(signature=bytes([0x1E, 0x98, 0x01])))


def test_upload_v2():
    port = FakeV2()
    bl.upload(IMAGE, bl.TARGETS["MEGA"], port)
    assert bytes(port.flash[:len(IMAGE)]) == IMAGE and port.left


def test_too_big():
    with pytest.raises(bl.UploadError, match="takes"):
        bl.upload(bytes(40000), bl.TARGETS["UNO"], FakeV1())
