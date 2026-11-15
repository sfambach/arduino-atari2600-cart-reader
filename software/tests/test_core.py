import json
import zlib

import pytest

from acr import rom, updates
from acr.demo_rom import build
from acr.gamedb import parse_dat
from acr.library import Library
from acr.reader import Reader, ReaderError
from acr.simulator import SimulatedCartridge, SimulatedSerial


def rom_of(kb):
    # every 4K bank different, 2K halves different
    return bytes((i * 7 + (i >> 11) * 13) & 0xFF for i in range(kb * 1024))


def reader_with(data, reversed_=False):
    r = Reader(SimulatedSerial(SimulatedCartridge(data, reversed_)))
    r.connect()
    return r


def test_hello_and_status():
    r = reader_with(rom_of(4))
    assert r.hello.board == "UNO_MCP23017" and r.hello.protocol == 1
    s = r.status()
    assert s.orientation_ok and s.supply == 984


def test_reversed_cartridge_is_refused():
    r = reader_with(rom_of(4), reversed_=True)
    assert not r.status().orientation_ok
    with pytest.raises(ReaderError, match="wrong way round"):
        r.dump("4K")


@pytest.mark.parametrize("kb,scheme", [(2, "2K"), (4, "4K"), (8, "F8"), (16, "F6"), (32, "F4")])
def test_auto_detection(kb, scheme):
    data = rom_of(kb)
    found = rom.detect(reader_with(data).dump(rom.PROBE_SCHEME))
    assert found.scheme == scheme
    # Reading a hotspot switches the bank, so those bytes come from the bank it selects (as on a real 2600)
    hot = {"F8": range(0xFF8, 0xFFA), "F6": range(0xFF6, 0xFFA), "F4": range(0xFF4, 0xFFC)}.get(scheme, ())
    masked = [i for i in range(len(data)) if (i & 0xFFF) not in hot]
    assert len(found.rom) == len(data)
    assert all(found.rom[i] == data[i] for i in masked)


def test_crc_mismatch_is_reported():
    serial = SimulatedSerial(SimulatedCartridge(rom_of(4)))
    r = Reader(serial)
    r.connect()
    original = serial._dump

    def broken(scheme):
        original(scheme)
        serial.out[100] ^= 0xFF
    serial._dump = broken
    with pytest.raises(ReaderError, match="checksum"):
        r.dump("4K")


def test_progress_reaches_total():
    seen = []
    reader_with(rom_of(8)).dump("F8", progress=lambda d, t: seen.append((d, t)))
    assert seen[-1] == (8192, 8192)


def test_schemes_listed():
    names = [s.name for s in reader_with(rom_of(4)).schemes()]
    assert "F8" in names and "3F" in names


def test_demo_rom_vectors():
    data = build()
    assert len(data) == 4096 and rom.reset_vector(data) == 0xF000


def test_differences():
    assert rom.differences(b"abc", b"abd") == [2]
    assert rom.differences(b"ab", b"abcd") == [2, 3]


def test_parse_dat():
    text = 'game (\n\tname "Pitfall! (USA)"\n\tregion "USA"\n\trom ( name "x.a26" size 4096 crc 1 md5 ' \
           '3e90cf23106f2e08b2781e41299de556 sha1 0 )\n)\n'
    assert parse_dat(text) == {"3E90CF23106F2E08B2781E41299DE556": "Pitfall! (USA)"}


def test_library_roundtrip(tmp_path):
    lib = Library(tmp_path)
    game = lib.add(rom_of(4), "Test: Game", "4K")
    assert lib.games()[0].md5 == game.md5
    assert lib.rom(game) == rom_of(4)
    lib.add(rom_of(4), "Test: Game", "4K")
    assert len(lib.games()) == 1
    lib.remove(game)
    assert lib.games() == []


def test_versions():
    assert updates.newer("v0.2.1", "0.2.0")
    assert not updates.newer("0.2.0", "0.2.0")
