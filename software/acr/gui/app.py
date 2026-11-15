"""Main window: connect the reader, read a cartridge, save it, look at it in hex, play it in Stella."""
from __future__ import annotations

import argparse
import pathlib
import sys
from typing import Callable, Optional

from PySide6.QtCore import QObject, QSettings, QSize, Qt, QThread, QTimer, QUrl, Signal
from PySide6.QtGui import QAction, QDesktopServices, QIcon, QPixmap
from PySide6.QtWidgets import (QApplication, QCheckBox, QComboBox, QDialog, QDialogButtonBox, QFileDialog,
                               QFormLayout, QGridLayout, QGroupBox, QHBoxLayout, QLabel, QLineEdit,
                               QListWidget, QListWidgetItem, QMainWindow, QMessageBox, QProgressBar,
                               QPushButton, QTabWidget, QVBoxLayout, QWidget)

from .. import __version__, bootloader, emulator, rom as romlib, updates
from ..demo_rom import build as build_demo_rom
from ..gamedb import GameDatabase
from ..i18n import LANGUAGES, set_language, tr
from ..library import Game, Library
from ..reader import Reader, list_ports
from ..simulator import SimulatedCartridge, SimulatedSerial
from .hexview import HexView
from .style import QSS, Banner, load_fonts

DEMO_PORT = "demo"
AUTO = "auto"


class Worker(QObject):
    """Runs one function off the GUI thread; the serial port is used only by one worker at a time."""
    progress = Signal(int, int)
    done = Signal(object)
    failed = Signal(str)

    def __init__(self, job: Callable[["Worker"], object], callback: Callable[[object], None]):
        super().__init__()
        self.job = job
        self.callback = callback

    def run(self) -> None:
        try:
            self.done.emit((self.callback, self.job(self)))
        except Exception as e:  # any error must reach the GUI, otherwise the thread never ends
            self.failed.emit(str(e) or type(e).__name__)


class Light(QLabel):
    COLOURS = {"ok": "#58c43a", "bad": "#e03c28", "off": "#4a4a4a"}

    def set(self, state: str, text: str) -> None:
        self.setText(f"<span style='color:{self.COLOURS[state]}'>&#9679;</span> {text}")


class SettingsDialog(QDialog):
    def __init__(self, settings: QSettings, parent: QWidget):
        super().__init__(parent)
        self.setWindowTitle(tr("Settings"))
        self.settings = settings
        self.stella = QLineEdit(settings.value("stella", ""))
        browse = QPushButton("...")
        browse.clicked.connect(self._browse)
        row = QHBoxLayout()
        row.addWidget(self.stella)
        row.addWidget(browse)
        self.language = QComboBox()
        for code, name in LANGUAGES.items():
            self.language.addItem(name, code)
        self.language.setCurrentIndex(max(0, self.language.findData(settings.value("language", "en"))))
        self.updates = QCheckBox(tr("Check for updates at start"))
        self.updates.setChecked(settings.value("check_updates", True, type=bool))
        self.titles = QCheckBox(tr("Download game titles and covers"))
        self.titles.setChecked(settings.value("download_titles", True, type=bool))
        form = QFormLayout(self)
        form.addRow(tr("Stella path"), row)
        form.addRow(tr("Language"), self.language)
        form.addRow(QLabel(tr("Language changes apply after a restart."), objectName="dim"))
        form.addRow(self.updates)
        form.addRow(self.titles)
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self._save)
        buttons.rejected.connect(self.reject)
        form.addRow(buttons)

    def _browse(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, tr("Stella path"))
        if path:
            self.stella.setText(path)

    def _save(self) -> None:
        self.settings.setValue("stella", self.stella.text())
        self.settings.setValue("language", self.language.currentData())
        self.settings.setValue("check_updates", self.updates.isChecked())
        self.settings.setValue("download_titles", self.titles.isChecked())
        self.accept()


class MainWindow(QMainWindow):
    def __init__(self, settings: QSettings, demo: bool = False):
        super().__init__()
        self.settings = settings
        self.reader: Optional[Reader] = None
        self.rom: Optional[bytes] = None
        self.scheme = ""
        self.title = ""
        self.cover: Optional[pathlib.Path] = None
        self.library = Library()
        self.gamedb = GameDatabase()
        self._threads: list[tuple[QThread, Worker]] = []
        self.setWindowTitle("Atari 2600 Cart Reader")
        self.resize(980, 680)

        self._build_menu()
        central = QWidget()
        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.addWidget(Banner("ATARI 2600 CART READER"))
        body = QHBoxLayout()
        body.setContentsMargins(12, 8, 12, 12)
        body.addWidget(self._build_side(), 0)
        self.tabs = QTabWidget()
        self.tabs.addTab(self._build_cartridge_tab(), tr("Cartridge"))
        self.hex = HexView()
        self.tabs.addTab(self.hex, tr("Hex"))
        self.tabs.addTab(self._build_library_tab(), tr("Library"))
        body.addWidget(self.tabs, 1)
        root.addLayout(body)
        self.setCentralWidget(central)
        self.progress = QProgressBar()
        self.progress.setMaximumWidth(280)
        self.progress.hide()
        self.statusBar().addPermanentWidget(self.progress)

        self._auto_reconnect = False
        self.refresh_ports(select=DEMO_PORT if demo else self.settings.value("port", ""))
        self._port_timer = QTimer(self, interval=2000, timeout=self._watch_ports)
        self._port_timer.start()
        self.refresh_library()
        self._update_buttons()
        if demo:
            self.connect_reader()
        if self.settings.value("check_updates", True, type=bool):
            self.check_updates(quiet=True)

    # ------------------------------------------------------------------ layout
    def _build_menu(self) -> None:
        file_menu = self.menuBar().addMenu(tr("File"))
        self._action(file_menu, tr("Open ROM..."), self.open_rom)
        self.save_action = self._action(file_menu, tr("Save ROM as..."), self.save_rom_as)
        file_menu.addSeparator()
        self._action(file_menu, tr("Quit"), self.close)
        reader_menu = self.menuBar().addMenu(tr("Reader"))
        self._action(reader_menu, tr("Update firmware..."), self.update_firmware)
        self._action(self.menuBar().addMenu(tr("Settings")), tr("Settings") + "...", self.edit_settings)
        help_menu = self.menuBar().addMenu(tr("Help"))
        self._action(help_menu, tr("Check for updates"), lambda: self.check_updates(quiet=False))
        self._action(help_menu, tr("About"), self.about)

    def _action(self, menu, text: str, slot) -> QAction:
        action = QAction(text, self)
        action.triggered.connect(slot)
        menu.addAction(action)
        return action

    def _build_side(self) -> QWidget:
        side = QWidget()
        side.setFixedWidth(290)
        layout = QVBoxLayout(side)
        layout.setContentsMargins(0, 0, 0, 0)

        box = QGroupBox(tr("Reader"))
        grid = QGridLayout(box)
        self.ports = QComboBox()
        refresh = QPushButton("↻")
        refresh.setToolTip(tr("Refresh"))
        refresh.setFixedWidth(40)
        refresh.clicked.connect(lambda: self.refresh_ports(self.ports.currentData()))
        self.connect_button = QPushButton(tr("Connect"))
        self.connect_button.clicked.connect(self.toggle_connection)
        self.reader_light = Light()
        self.reader_light.set("off", tr("not connected"))
        self.reader_light.setWordWrap(True)
        grid.addWidget(QLabel(tr("Port")), 0, 0)
        grid.addWidget(self.ports, 0, 1)
        grid.addWidget(refresh, 0, 2)
        grid.addWidget(self.connect_button, 1, 0, 1, 3)
        grid.addWidget(self.reader_light, 2, 0, 1, 3)
        layout.addWidget(box)

        box = QGroupBox(tr("Cartridge"))
        grid = QGridLayout(box)
        self.orientation_light = Light()
        self.supply_light = Light()
        self.orientation_light.set("off", tr("Orientation"))
        self.supply_light.set("off", tr("Supply"))
        self.check_button = QPushButton(tr("Check"))
        self.check_button.clicked.connect(self.check_cartridge)
        self.schemes = QComboBox()
        self.schemes.addItem(tr("Auto (2K/4K/F8/F6/F4)"), AUTO)
        self.read_button = QPushButton(tr("READ"), objectName="primary")
        self.read_button.setMinimumHeight(48)
        self.read_button.clicked.connect(self.read_cartridge)
        self.save_button = QPushButton(tr("SAVE"))
        self.save_button.clicked.connect(self.save_to_library)
        self.play_button = QPushButton(tr("PLAY"))
        self.play_button.clicked.connect(self.play_current)
        grid.addWidget(self.orientation_light, 0, 0, 1, 2)
        grid.addWidget(self.supply_light, 1, 0, 1, 2)
        grid.addWidget(self.check_button, 2, 0, 1, 2)
        grid.addWidget(QLabel(tr("Scheme")), 3, 0, 1, 2)
        grid.addWidget(self.schemes, 4, 0, 1, 2)
        grid.addWidget(self.read_button, 5, 0, 1, 2)
        grid.addWidget(self.save_button, 6, 0)
        grid.addWidget(self.play_button, 6, 1)
        layout.addWidget(box)
        layout.addStretch(1)
        return side

    def _build_cartridge_tab(self) -> QWidget:
        tab = QWidget()
        layout = QHBoxLayout(tab)
        self.cover_label = QLabel(alignment=Qt.AlignCenter)
        self.cover_label.setFixedSize(260, 340)
        self.cover_label.setStyleSheet("background:#1d1510; border:2px solid #2a1a0c;")
        info = QVBoxLayout()
        self.title_label = QLabel(tr("No ROM read yet."), objectName="title", wordWrap=True)
        self.facts = QLabel(objectName="dim", wordWrap=True)
        self.facts.setTextInteractionFlags(Qt.TextSelectableByMouse)
        info.addWidget(self.title_label)
        info.addWidget(self.facts)
        info.addStretch(1)
        layout.addWidget(self.cover_label)
        layout.addLayout(info, 1)
        return tab

    def _build_library_tab(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        self.games = QListWidget()
        self.games.setViewMode(QListWidget.IconMode)
        self.games.setIconSize(QSize(120, 156))
        self.games.setGridSize(QSize(150, 210))
        self.games.setResizeMode(QListWidget.Adjust)
        self.games.setWordWrap(True)
        self.games.itemDoubleClicked.connect(lambda item: self.play_game(item.data(Qt.UserRole)))
        buttons = QHBoxLayout()
        play = QPushButton(tr("Play"))
        play.clicked.connect(lambda: self._with_selected(self.play_game))
        show = QPushButton(tr("Hex"))
        show.clicked.connect(lambda: self._with_selected(self.load_game))
        remove = QPushButton(tr("Remove"))
        remove.clicked.connect(lambda: self._with_selected(self.remove_game))
        for b in (play, show, remove):
            buttons.addWidget(b)
        buttons.addStretch(1)
        layout.addWidget(self.games)
        layout.addLayout(buttons)
        return tab

    # ------------------------------------------------------------------ helpers
    def _run(self, job: Callable[[Worker], object], done: Callable[[object], None], busy: bool = True) -> None:
        thread = QThread()
        worker = Worker(job, done)
        worker.moveToThread(thread)
        thread.started.connect(worker.run)
        worker.progress.connect(self._on_progress)
        if busy:
            for signal in (worker.done, worker.failed):
                signal.connect(self._end_busy)
            self._set_busy(True)
        worker.done.connect(self._dispatch)
        worker.failed.connect(self._on_error)
        for signal in (worker.done, worker.failed):
            signal.connect(thread.quit)
        thread.finished.connect(self._cleanup)
        self._threads.append((thread, worker))
        thread.start()

    def _dispatch(self, payload: tuple) -> None:
        callback, result = payload
        callback(result)

    def _cleanup(self) -> None:
        thread = self.sender()
        thread.wait()  # "finished" arrives before the thread has fully stopped; dropping it earlier aborts Qt
        self._threads = [(t, w) for t, w in self._threads if t is not thread]

    def _set_busy(self, busy: bool) -> None:
        self.busy = busy
        if not busy:
            self.progress.hide()
        self._update_buttons()

    def _end_busy(self, *_):
        self._progress_text = None
        self._set_busy(False)

    def _on_progress(self, done: int, total: int) -> None:
        self.progress.show()
        self.progress.setMaximum(total)
        self.progress.setValue(done)
        text = getattr(self, "_progress_text", None)
        self.statusBar().showMessage(text or tr("Reading {done} of {total} bytes", done=done, total=total))

    def _on_error(self, message: str) -> None:
        self.statusBar().showMessage(message)
        QMessageBox.warning(self, tr("Error"), message)

    def _update_buttons(self) -> None:
        busy = getattr(self, "busy", False)
        connected = self.reader is not None
        for b in (self.check_button, self.read_button):
            b.setEnabled(connected and not busy)
        for b in (self.save_button, self.play_button):
            b.setEnabled(self.rom is not None and not busy)
        self.save_action.setEnabled(self.rom is not None)
        self.connect_button.setEnabled(not busy)
        self.connect_button.setText(tr("Disconnect") if connected else tr("Connect"))

    # ------------------------------------------------------------------ reader
    def refresh_ports(self, select: str = "") -> None:
        try:
            ports = list_ports()
        except Exception:  # serial.tools may fail on exotic systems; the demo port still works
            ports = []
        self._port_list = ports
        self.ports.clear()
        for port in ports:
            label = port.device if port.description == port.device else f"{port.device} – {port.description}"
            self.ports.addItem(label, port.device)
        self.ports.addItem(tr("Demo cartridge"), DEMO_PORT)
        index = self.ports.findData(select)
        if index < 0:  # renamed after a reset (ttyUSB0 -> ttyUSB1): find the same reader by its USB id
            key = self.settings.value("port_key", "")
            same = [p.device for p in ports if key and p.key == key]
            index = self.ports.findData(same[0]) if same else 0
        self.ports.setCurrentIndex(index)

    def _watch_ports(self) -> None:
        """Every 2 s: notice a reader that vanished or came back under another name."""
        if getattr(self, "busy", False):
            return
        try:
            ports = list_ports()
        except Exception:
            return
        if [p.device for p in ports] == [p.device for p in getattr(self, "_port_list", [])]:
            return
        connected = self.reader is not None and self.settings.value("port", "") != DEMO_PORT
        current = self.settings.value("port", "")
        if connected and current not in [p.device for p in ports]:
            self.reader.close()
            self.reader = None
            self.reader_light.set("off", tr("not connected"))
        self.refresh_ports(current if self.reader else self.ports.currentData())
        key = self.settings.value("port_key", "")
        if self.reader is None and key and any(p.key == key for p in ports) and self._auto_reconnect:
            self.connect_reader()
        self._update_buttons()

    def toggle_connection(self) -> None:
        if self.reader:
            self._auto_reconnect = False
            self.reader.close()
            self.reader = None
            self.reader_light.set("off", tr("not connected"))
            self._update_buttons()
        else:
            self.connect_reader()

    def connect_reader(self) -> None:
        port = self.ports.currentData()

        def job(_w: Worker) -> Reader:
            if port == DEMO_PORT:
                reader = Reader(SimulatedSerial(SimulatedCartridge(build_demo_rom())))
                reader.connect()
                return reader
            return Reader.open(port)

        def done(reader: Reader) -> None:
            self.reader = reader
            self._auto_reconnect = port != DEMO_PORT
            self.settings.setValue("port", port)
            key = [p.key for p in getattr(self, "_port_list", []) if p.device == port]
            if key and key[0]:
                self.settings.setValue("port_key", key[0])
            h = reader.hello
            self.reader_light.set("ok", tr("connected: firmware {version}, board {board}", version=h.version,
                                           board=h.board))
            names = [s.name for s in reader.schemes()]
            current = self.schemes.currentData()
            self.schemes.clear()
            self.schemes.addItem(tr("Auto (2K/4K/F8/F6/F4)"), AUTO)
            for n in names:
                self.schemes.addItem(n, n)
            self.schemes.setCurrentIndex(max(0, self.schemes.findData(current)))
            if port == DEMO_PORT:
                self.statusBar().showMessage(tr("Demo mode: simulated reader with a demo cartridge"))
            self._update_buttons()
            self.check_cartridge()
            if port != DEMO_PORT and self.settings.value("check_updates", True, type=bool):
                self.check_updates(quiet=True, firmware_only=True)  # now the firmware version is known

        self._run(job, done)

    def check_cartridge(self) -> None:
        reader = self.reader

        def done(status) -> None:
            if status.orientation_ok:
                self.orientation_light.set("ok", f"{tr('Orientation')}: {tr('ok')}")
                volts = (status.supply or 0) * 5 / 1023
                self.supply_light.set("ok" if (status.supply or 0) >= 900 else "bad",
                                      f"{tr('Supply')}: {volts:.2f} V")
            else:
                self.orientation_light.set("bad", tr("reversed: turn the cartridge round"))
                self.supply_light.set("off", f"{tr('Supply')}: {tr('off')}")

        self._run(lambda w: reader.status(), done)

    def read_cartridge(self) -> None:
        reader = self.reader
        choice = self.schemes.currentData()
        download = self.settings.value("download_titles", True, type=bool)

        def job(w: Worker):
            progress = lambda d, t: w.progress.emit(d, t)
            if choice == AUTO:
                found = romlib.detect(reader.dump(romlib.PROBE_SCHEME, progress=progress))
                scheme, data = found.scheme, found.rom
            else:
                scheme, data = choice, reader.dump(choice, progress=progress)
            title = self.gamedb.title(romlib.md5(data), download)
            cover = self.gamedb.cover(title, download) if title else None
            return data, scheme, title, cover

        self._run(job, lambda result: self.show_rom(*result))

    def show_rom(self, data: bytes, scheme: str, title: Optional[str], cover: Optional[pathlib.Path]) -> None:
        self.rom, self.scheme, self.cover = data, scheme, cover
        if not title and self.ports.currentData() == DEMO_PORT and data == build_demo_rom():
            title = tr("Demo cartridge")
        self.title = title or tr("unknown game")
        self.title_label.setText(self.title)
        md5 = romlib.md5(data)
        self.facts.setText(
            f"{tr('Scheme')}: {scheme}<br>{tr('Size')}: {len(data)} bytes ({len(data) // 1024}K)<br>"
            f"MD5: {md5}<br>Reset: ${romlib.reset_vector(data):04X}")
        pixmap = QPixmap(str(cover)) if cover else QPixmap()
        if pixmap.isNull():
            self.cover_label.setPixmap(QPixmap())
            self.cover_label.setText("🕹")
            self.cover_label.setStyleSheet("background:#1d1510; border:2px solid #2a1a0c; font-size:72pt;")
        else:
            self.cover_label.setPixmap(pixmap.scaled(self.cover_label.size(), Qt.KeepAspectRatio,
                                                     Qt.SmoothTransformation))
        self.hex.set_data(data)
        self.statusBar().showMessage(tr("Read {size} bytes, scheme {scheme}", size=len(data), scheme=scheme))
        self.tabs.setCurrentIndex(0)
        self._update_buttons()

    # ------------------------------------------------------------------ files, library, emulator
    def open_rom(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, tr("Open ROM..."), "", "ROM (*.a26 *.bin);;* (*)")
        if not path:
            return
        data = pathlib.Path(path).read_bytes()
        scheme = {2048: "2K", 4096: "4K", 8192: "F8", 16384: "F6", 32768: "F4"}.get(len(data), "4K")
        title = self.gamedb.title(romlib.md5(data), download=False) or pathlib.Path(path).stem
        self.show_rom(data, scheme, title, self.gamedb.cover(title, download=False))

    def save_rom_as(self) -> None:
        if self.rom is None:
            return
        path, _ = QFileDialog.getSaveFileName(self, tr("Save ROM as..."), f"{self.title}.a26", "ROM (*.a26 *.bin)")
        if path:
            pathlib.Path(path).write_bytes(self.rom)

    def save_to_library(self) -> None:
        if self.rom is None:
            return
        self.library.add(self.rom, self.title, self.scheme, self.cover)
        self.refresh_library()
        self.statusBar().showMessage(tr("Saved to the collection: {title}", title=self.title))

    def refresh_library(self) -> None:
        self.games.clear()
        for game in self.library.games():
            cover = game.cover or self.gamedb.cover(game.title, download=False)  # found after saving
            pixmap = QPixmap(str(cover)) if cover else QPixmap()
            item = QListWidgetItem(QIcon(pixmap) if not pixmap.isNull() else QIcon(), game.title)
            item.setData(Qt.UserRole, game)
            item.setToolTip(f"{game.title}\n{game.scheme}, {game.saved}")
            self.games.addItem(item)

    def _with_selected(self, action: Callable[[Game], None]) -> None:
        item = self.games.currentItem()
        if item:
            action(item.data(Qt.UserRole))

    def load_game(self, game: Game) -> None:
        cover = pathlib.Path(game.cover) if game.cover else None
        self.show_rom(self.library.rom(game), game.scheme, game.title, cover)
        self.tabs.setCurrentWidget(self.hex)

    def remove_game(self, game: Game) -> None:
        if QMessageBox.question(self, tr("Remove"), tr("Remove {title} from the collection?", title=game.title)) \
                == QMessageBox.Yes:
            self.library.remove(game)
            self.refresh_library()

    def play_game(self, game: Game) -> None:
        self._play(self.library.rom(game), game.scheme, game.title)

    def play_current(self) -> None:
        if self.rom is not None:
            self._play(self.rom, self.scheme, self.title)

    def _play(self, data: bytes, scheme: str, title: str) -> None:
        stella = emulator.find_stella(self.settings.value("stella", ""))
        if not stella:
            self._on_error(tr("Stella not found: set its path in the settings."))
            return
        try:
            emulator.launch(data, scheme, title, stella)
        except (OSError, RuntimeError) as e:
            self._on_error(str(e))

    # ------------------------------------------------------------------ settings, updates
    def edit_settings(self) -> None:
        SettingsDialog(self.settings, self).exec()

    def check_updates(self, quiet: bool, firmware_only: bool = False) -> None:
        board = self.reader.hello.board if self.reader else None
        firmware = self.reader.hello.version if self.reader else None
        port = self.settings.value("port", "")

        def done(release) -> None:
            if release is None:
                if not quiet:
                    QMessageBox.information(self, tr("Check for updates"), tr("No release found on GitHub."))
                return
            notes = []
            if not firmware_only and updates.newer(release.version, __version__):
                notes.append(tr("Version {version} is available.", version=release.version))
            if board and firmware and updates.firmware_asset(release, board) and \
                    updates.newer(release.version, firmware):
                notes.append(tr("Firmware {version} is available for your reader.", version=release.version))
            if not notes:
                if not quiet:
                    QMessageBox.information(self, tr("Check for updates"), tr("Everything is up to date."))
                return
            box = QMessageBox(QMessageBox.Information, tr("Check for updates"), "\n".join(notes), parent=self)
            flash_now = None
            if board and firmware and updates.firmware_asset(release, board) and \
                    updates.newer(release.version, firmware):
                flash_now = box.addButton(tr("Update firmware now"), QMessageBox.AcceptRole)
            open_page = box.addButton(tr("Open download page"), QMessageBox.AcceptRole)
            box.addButton(QMessageBox.Close)
            box.exec()
            if flash_now is not None and box.clickedButton() is flash_now:
                self._flash(port, board, "")
            elif box.clickedButton() is open_page:
                QDesktopServices.openUrl(QUrl(release.url))

        self._run(lambda w: updates.latest_release(), done, busy=False)

    def update_firmware(self) -> None:
        port = self.ports.currentData()
        if port == DEMO_PORT:
            return
        board = self.reader.hello.board if self.reader else None
        boards = list(bootloader.TARGETS)
        dialog = QDialog(self)
        dialog.setWindowTitle(tr("Update firmware..."))
        form = QFormLayout(dialog)
        board_box = QComboBox()
        board_box.addItems(boards)
        if board in boards:
            board_box.setCurrentText(board)
        hex_path = QLineEdit(placeholderText=tr("empty = latest firmware from GitHub"))
        browse = QPushButton("...")
        browse.clicked.connect(lambda: hex_path.setText(
            QFileDialog.getOpenFileName(dialog, tr("Firmware file (.hex)"), "", "HEX (*.hex)")[0] or hex_path.text()))
        row = QHBoxLayout()
        row.addWidget(hex_path)
        row.addWidget(browse)
        form.addRow(tr("Board"), board_box)
        form.addRow(tr("Firmware file (.hex)"), row)
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        form.addRow(buttons)
        if dialog.exec() != QDialog.Accepted:
            return
        self._flash(port, board_box.currentText(), hex_path.text())

    def _flash(self, port: str, board: str, hex_file: str) -> None:
        if self.reader:
            self.toggle_connection()  # the upload needs the port; it resets the board into its bootloader

        def job(w: Worker) -> str:
            path = pathlib.Path(hex_file) if hex_file else None
            if path is None:
                release = updates.latest_release()
                url = updates.firmware_asset(release, board) if release else None
                if not url:
                    raise RuntimeError(tr("No firmware for {board} in the latest GitHub release.", board=board))
                path = updates.download(url)
            bootloader.flash(path.read_text(), port, board,
                             lambda phase, done, total: w.progress.emit(done, total))
            return ""

        def done(_log: str) -> None:
            self.statusBar().showMessage(tr("Firmware uploaded."))
            self.connect_reader()

        self._progress_text = tr("Uploading firmware...")
        self._run(job, done)

    def about(self) -> None:
        QMessageBox.about(self, tr("About"),
                          f"<b>Atari 2600 Cart Reader</b> {__version__}<br>"
                          "Stefan Fambach (SteFam), https://www.fambach.net<br>"
                          "GPLv3 · Press Start 2P font: SIL OFL 1.1<br>"
                          "Game titles and covers: libretro-database / libretro-thumbnails")

    def closeEvent(self, event) -> None:
        if self.reader:
            self.reader.close()
        super().closeEvent(event)


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(prog="acr")
    parser.add_argument("--demo", action="store_true", help="simulated reader with a demo cartridge")
    parser.add_argument("--screenshot", help=argparse.SUPPRESS)
    args = parser.parse_args(argv if argv is not None else sys.argv[1:])
    app = QApplication(sys.argv[:1])
    app.setOrganizationName("SteFam")
    app.setApplicationName("AtariCartReader")
    settings = QSettings()
    set_language(settings.value("language", "en"))
    load_fonts()
    app.setStyleSheet(QSS)
    window = MainWindow(settings, demo=args.demo)
    window.show()
    if args.screenshot:
        from PySide6.QtCore import QTimer

        def shoot() -> None:
            if window.rom is None and window.reader is not None and not getattr(window, "busy", False):
                window.read_cartridge()
            if window.rom is not None and not getattr(window, "busy", False):
                window.grab().save(args.screenshot)
                app.quit()
            else:
                QTimer.singleShot(300, shoot)

        QTimer.singleShot(500, shoot)
    return app.exec()
