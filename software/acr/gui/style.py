"""Atari look: black console, wood panels, the rainbow stripes and a pixel font (Press Start 2P, OFL)."""
from __future__ import annotations

import pathlib

from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import QColor, QFont, QFontDatabase, QPainter
from PySide6.QtWidgets import QWidget

ASSETS = pathlib.Path(__file__).resolve().parent / "assets"
STRIPES = ["#e03c28", "#f27b1a", "#f7b512", "#f9e04b"]
PIXEL_FAMILY = "Press Start 2P"

QSS = """
QMainWindow, QDialog { background: #16110d; }
QWidget { color: #e8dcc8; font-size: 10pt; }
QGroupBox {
  background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #4a2c14, stop:0.35 #6b4423, stop:0.6 #553418, stop:1 #3d240f);
  border: 2px solid #2a1a0c; border-radius: 6px; margin-top: 18px; padding: 10px 8px 8px 8px;
}
QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 4px; color: #f7b512;
  font-family: "Press Start 2P"; font-size: 8pt; }
QPushButton {
  background: #111; color: #d9d9d9; border: 2px solid #7a7a7a; border-radius: 4px; padding: 7px 12px;
  font-family: "Press Start 2P"; font-size: 8pt;
}
QPushButton:hover { border-color: #f27b1a; color: #fff; }
QPushButton:pressed { background: #2a2a2a; }
QPushButton:disabled { color: #555; border-color: #3a3a3a; }
QPushButton#primary { background: #f27b1a; color: #111; border-color: #f7b512; }
QPushButton#primary:hover { background: #f7b512; }
QPushButton#primary:disabled { background: #3a2a1a; color: #6b5a4a; border-color: #3a2a1a; }
QComboBox, QLineEdit, QSpinBox {
  background: #0d0d0d; color: #e8dcc8; border: 1px solid #6b4423; border-radius: 3px; padding: 4px;
}
QTabWidget::pane { border: 2px solid #2a1a0c; background: #0d0a08; }
QTabBar::tab { background: #2a1a0c; color: #c9b79c; padding: 8px 14px; font-family: "Press Start 2P"; font-size: 8pt;
  border-top-left-radius: 4px; border-top-right-radius: 4px; margin-right: 2px; }
QTabBar::tab:selected { background: #6b4423; color: #f9e04b; }
QProgressBar { background: #0d0d0d; border: 1px solid #6b4423; border-radius: 3px; text-align: center; color: #fff; }
QProgressBar::chunk { background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
  stop:0 #e03c28, stop:0.33 #f27b1a, stop:0.66 #f7b512, stop:1 #f9e04b); }
QPlainTextEdit#hex { background: #050505; color: #ffb000; border: none; selection-background-color: #6b4423; }
QListWidget { background: #0d0a08; border: none; }
QListWidget::item:selected { background: #6b4423; }
QLabel#title { font-family: "Press Start 2P"; font-size: 12pt; color: #f9e04b; }
QLabel#dim { color: #9c8b72; }
QStatusBar { background: #0d0a08; color: #c9b79c; }
QMenuBar { background: #0d0a08; } QMenuBar::item:selected { background: #6b4423; }
QMenu { background: #1d1510; border: 1px solid #6b4423; } QMenu::item:selected { background: #6b4423; }
QCheckBox { spacing: 8px; }
"""


def load_fonts() -> None:
    QFontDatabase.addApplicationFont(str(ASSETS / "PressStart2P-Regular.ttf"))


def pixel_font(size: float) -> QFont:
    font = QFont(PIXEL_FAMILY)
    font.setPointSizeF(size)
    return font


class Banner(QWidget):
    """Black header with the four rainbow stripes and the program name."""

    def __init__(self, text: str, parent: QWidget | None = None):
        super().__init__(parent)
        self.text = text
        self.setFixedHeight(82)

    def paintEvent(self, event) -> None:
        p = QPainter(self)
        p.fillRect(self.rect(), QColor("#0a0a0a"))
        p.setPen(QColor("#f2f2f2"))
        p.setFont(pixel_font(15))
        p.drawText(QRectF(18, 8, self.width() - 36, 34), Qt.AlignVCenter | Qt.AlignLeft, self.text)
        y = 48.0
        for i, colour in enumerate(reversed(STRIPES)):  # yellow on top, thicker red at the bottom
            height = 3 + i * 1.5
            p.fillRect(QRectF(0, y, self.width(), height), QColor(colour))
            y += height + 3
        p.end()
