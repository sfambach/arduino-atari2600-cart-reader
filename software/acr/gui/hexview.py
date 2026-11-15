"""Read-only hex view of a ROM, one block per 4K bank, with search, go-to and compare."""
from __future__ import annotations

from typing import Optional

from PySide6.QtGui import QColor, QFontDatabase, QTextCursor, QTextFormat
from PySide6.QtWidgets import (QFileDialog, QHBoxLayout, QLabel, QLineEdit, QPlainTextEdit, QPushButton,
                               QTextEdit, QVBoxLayout, QWidget)

from .. import rom as romlib
from ..i18n import tr

PER_LINE = 16
LINES_PER_BANK = romlib.BANK // PER_LINE


def render(data: bytes) -> str:
    lines = []
    for offset in range(0, len(data), PER_LINE):
        if offset % romlib.BANK == 0:
            lines.append(f"---- {tr('Bank {n}', n=offset // romlib.BANK)} ----")
        chunk = data[offset:offset + PER_LINE]
        hexpart = " ".join(f"{b:02X}" for b in chunk).ljust(PER_LINE * 3 - 1)
        text = "".join(chr(b) if 32 <= b < 127 else "." for b in chunk)
        lines.append(f"{offset:05X}  {hexpart}  {text}")
    return "\n".join(lines)


def line_of(offset: int) -> int:
    return offset // PER_LINE + offset // romlib.BANK + 1


def parse_hex(text: str) -> bytes:
    return bytes.fromhex(text.replace("$", "").replace(",", " "))


class HexView(QWidget):
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.data = b""
        self.view = QPlainTextEdit(objectName="hex", readOnly=True)
        self.view.setLineWrapMode(QPlainTextEdit.NoWrap)
        font = QFontDatabase.systemFont(QFontDatabase.FixedFont)
        font.setPointSize(10)
        self.view.setFont(font)

        self.goto = QLineEdit(placeholderText=tr("Go to") + " (hex)")
        self.goto.returnPressed.connect(self._goto)
        self.find = QLineEdit(placeholderText=tr("Find bytes") + " (A9 00 85)")
        self.find.returnPressed.connect(self._find)
        compare = QPushButton(tr("Compare with file..."))
        compare.clicked.connect(self._compare)
        self.info = QLabel(objectName="dim")

        bar = QHBoxLayout()
        bar.addWidget(self.goto)
        bar.addWidget(self.find)
        bar.addWidget(compare)
        layout = QVBoxLayout(self)
        layout.addLayout(bar)
        layout.addWidget(self.view)
        layout.addWidget(self.info)
        self._last_find = -1

    def set_data(self, data: bytes) -> None:
        self.data = data
        self.view.setPlainText(render(data))
        self.view.setExtraSelections([])
        self.info.setText("")
        self._last_find = -1

    def _select(self, offset: int, length: int = 1) -> None:
        block = self.view.document().findBlockByLineNumber(line_of(offset))
        cursor = QTextCursor(block)
        column = 7 + (offset % PER_LINE) * 3
        cursor.setPosition(block.position() + column)
        cursor.setPosition(block.position() + min(column + length * 3 - 1, block.length() - 1), QTextCursor.KeepAnchor)
        self.view.setTextCursor(cursor)
        self.view.centerCursor()

    def _goto(self) -> None:
        try:
            offset = int(self.goto.text().replace("$", ""), 16)
        except ValueError:
            return
        if 0 <= offset < len(self.data):
            self._select(offset)

    def _find(self) -> None:
        try:
            needle = parse_hex(self.find.text())
        except ValueError:
            self.info.setText(tr("not found"))
            return
        if not needle:
            return
        hit = self.data.find(needle, self._last_find + 1)
        if hit < 0:
            hit = self.data.find(needle)
        self._last_find = hit
        if hit < 0:
            self.info.setText(tr("not found"))
            return
        self.info.setText(f"${hit:05X}")
        self._select(hit, len(needle))

    def compare_with(self, other: bytes) -> list[int]:
        diff = romlib.differences(self.data, other)
        selections = []
        lines = sorted({line_of(o) for o in diff if o < len(self.data)})
        for line in lines[:2000]:
            sel = QTextEdit.ExtraSelection()
            sel.format.setBackground(QColor("#5a1010"))
            sel.format.setProperty(QTextFormat.FullWidthSelection, True)
            sel.cursor = QTextCursor(self.view.document().findBlockByLineNumber(line))
            selections.append(sel)
        self.view.setExtraSelections(selections)
        self.info.setText(tr("{count} differences", count=len(diff)) if diff else tr("identical"))
        if diff and diff[0] < len(self.data):
            self._select(diff[0])
        return diff

    def _compare(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, tr("Compare with file..."), "", "ROM (*.a26 *.bin);;* (*)")
        if path:
            with open(path, "rb") as f:
                self.compare_with(f.read())
