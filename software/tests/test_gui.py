import os

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
pytest.importorskip("PySide6")

from PySide6.QtCore import QSettings
from PySide6.QtWidgets import QApplication, QMessageBox

from acr.gui.app import MainWindow
from acr.gui.hexview import HexView, line_of, render


@pytest.fixture(scope="module")
def app():
    return QApplication.instance() or QApplication([])


def wait(app, condition, steps=200):
    import time
    for _ in range(steps):
        app.processEvents()
        if condition():
            return True
        time.sleep(0.02)
    return False


def test_hex_layout():
    text = render(bytes(range(256)) * 32).splitlines()
    assert text[0].startswith("----")
    assert text[line_of(0x1000)].startswith("01000")
    assert text[line_of(0x10)].startswith("00010  10 11")


def test_compare(app):
    view = HexView()
    view.set_data(bytes(4096))
    assert view.compare_with(bytes(4095) + b"\x01") == [4095]


def test_demo_read(app, tmp_path, monkeypatch):
    monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path))
    monkeypatch.setenv("XDG_CACHE_HOME", str(tmp_path))
    settings = QSettings(str(tmp_path / "s.ini"), QSettings.IniFormat)
    settings.setValue("check_updates", False)
    settings.setValue("download_titles", False)
    window = MainWindow(settings, demo=True)
    assert wait(app, lambda: window.reader is not None and not window.busy)
    window.read_cartridge()
    assert wait(app, lambda: window.rom is not None and not window.busy)
    assert window.scheme == "4K" and len(window.rom) == 4096
    window.save_to_library()
    assert window.games.count() == 1
    window.close()


def test_renamed_port_is_found_again(app, tmp_path, monkeypatch):
    from acr.gui import app as app_module
    from acr.reader import Port
    monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path))
    monkeypatch.setenv("XDG_CACHE_HOME", str(tmp_path))
    settings = QSettings(str(tmp_path / "p.ini"), QSettings.IniFormat)
    settings.setValue("check_updates", False)
    settings.setValue("port", "/dev/ttyUSB0")
    settings.setValue("port_key", "1A86:7523:")
    monkeypatch.setattr(app_module, "list_ports", lambda: [Port("/dev/ttyUSB1", "USB Serial", "1A86:7523:")])
    window = MainWindow(settings)
    assert window.ports.currentData() == "/dev/ttyUSB1"
    window.close()


def test_split_multicart(app, tmp_path, monkeypatch):
    monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path))
    monkeypatch.setenv("XDG_CACHE_HOME", str(tmp_path))
    settings = QSettings(str(tmp_path / "s.ini"), QSettings.IniFormat)
    settings.setValue("check_updates", False)
    settings.setValue("download_titles", False)
    window = MainWindow(settings)
    games = [bytes([n]) * 0x800 for n in range(4)]
    window.show_rom(b"".join(games), "4IN1", "Test 4 in 1", None)
    assert window.split_action.isEnabled()
    window.split_multicart()
    assert wait(app, lambda: window.games.count() == 4 and not window.busy)
    assert {g.title for g in window.library.games()} == {f"Test 4 in 1, game {n}" for n in range(1, 5)}
    window.close()


def test_clear_library_asks_first(app, tmp_path, monkeypatch):
    monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path))
    monkeypatch.setenv("XDG_CACHE_HOME", str(tmp_path))
    settings = QSettings(str(tmp_path / "s.ini"), QSettings.IniFormat)
    settings.setValue("check_updates", False)
    window = MainWindow(settings)
    window.library.add(bytes(0x800), "Test game", "2K")
    window.refresh_library()
    monkeypatch.setattr(QMessageBox, "warning", lambda *a, **k: QMessageBox.Cancel)
    window.clear_library()
    assert window.games.count() == 1
    monkeypatch.setattr(QMessageBox, "warning", lambda *a, **k: QMessageBox.Yes)
    window.clear_library()
    assert window.games.count() == 0 and not list(window.library.folder.glob("*.a26"))
    window.close()
