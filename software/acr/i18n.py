"""User-visible texts in English and German."""
from __future__ import annotations

LANGUAGES = {"en": "English", "de": "Deutsch"}

_DE = {
    "Cartridge": "Cartridge",
    "Reader": "Reader",
    "Port": "Port",
    "Connect": "Verbinden",
    "Disconnect": "Trennen",
    "Refresh": "Aktualisieren",
    "Scheme": "Bankswitching",
    "Auto (2K/4K/F8/F6/F4)": "Automatisch (2K/4K/F8/F6/F4)",
    "READ": "LESEN",
    "SAVE": "SPEICHERN",
    "PLAY": "SPIELEN",
    "Check": "Prüfen",
    "not connected": "nicht verbunden",
    "connected: firmware {version}, board {board}": "verbunden: Firmware {version}, Board {board}",
    "Orientation": "Richtung",
    "Supply": "Versorgung",
    "ok": "ok",
    "reversed: turn the cartridge round": "verkehrt herum: Cartridge umdrehen",
    "off": "aus",
    "unknown": "unbekannt",
    "Reading {done} of {total} bytes": "Lese {done} von {total} Bytes",
    "Read {size} bytes, scheme {scheme}": "{size} Bytes gelesen, Schema {scheme}",
    "Title": "Titel",
    "Size": "Größe",
    "unknown game": "unbekanntes Spiel",
    "Hex": "Hex",
    "Library": "Sammlung",
    "Go to": "Gehe zu",
    "Find bytes": "Bytes suchen",
    "Compare with file...": "Mit Datei vergleichen...",
    "{count} differences": "{count} Unterschiede",
    "identical": "identisch",
    "not found": "nicht gefunden",
    "Bank {n}": "Bank {n}",
    "Play": "Spielen",
    "Remove": "Entfernen",
    "Remove {title} from the collection?": "{title} aus der Sammlung entfernen?",
    "File": "Datei",
    "Open ROM...": "ROM öffnen...",
    "Save ROM as...": "ROM speichern unter...",
    "Quit": "Beenden",
    "Update firmware...": "Firmware aktualisieren...",
    "Settings": "Einstellungen",
    "Stella path": "Pfad zu Stella",
    "Language": "Sprache",
    "Check for updates at start": "Beim Start nach Updates suchen",
    "Download game titles and covers": "Spieltitel und Cover herunterladen",
    "Language changes apply after a restart.": "Die Sprache wechselt nach einem Neustart.",
    "Help": "Hilfe",
    "Check for updates": "Nach Updates suchen",
    "About": "Über",
    "Error": "Fehler",
    "Stella not found: set its path in the settings.": "Stella nicht gefunden: Pfad in den Einstellungen eintragen.",
    "No ROM read yet.": "Noch kein ROM gelesen.",
    "Saved to the collection: {title}": "In der Sammlung gespeichert: {title}",
    "Version {version} is available.": "Version {version} ist verfügbar.",
    "Firmware {version} is available for your reader.": "Firmware {version} ist für deinen Reader verfügbar.",
    "Everything is up to date.": "Alles ist aktuell.",
    "No release found on GitHub.": "Kein Release auf GitHub gefunden.",
    "Open download page": "Download-Seite öffnen",
    "Firmware file (.hex)": "Firmware-Datei (.hex)",
    "Board": "Board",
    "Uploading firmware...": "Firmware wird übertragen...",
    "Firmware uploaded.": "Firmware übertragen.",
    "empty = latest firmware from GitHub": "leer = neueste Firmware von GitHub",
    "No firmware for {board} in the latest GitHub release.": "Keine Firmware für {board} im neuesten GitHub-Release.",
    "Update firmware now": "Firmware jetzt aktualisieren",
    "Multicart (next game at power-on)": "Multicart (nächstes Spiel beim Einschalten)",
    "Reading game {n}...": "Lese Spiel {n}...",
    "The game is not in the game list. If this is a multicart (e.g. 32 in 1), the reader only sees the game that is active right now. Read all games of the multicart?":
        "Das Spiel steht nicht in der Spieleliste. Ist das ein Multicart (z. B. 32 in 1), sieht der Reader nur das gerade aktive Spiel. Alle Spiele des Multicarts lesen?",
    "Read as multicart": "Als Multicart lesen",
    "Demo mode: simulated reader with a demo cartridge": "Demo-Modus: simulierter Reader mit Demo-Cartridge",
    "Demo cartridge": "Demo-Cartridge",
}

_language = "en"


def set_language(code: str) -> None:
    global _language
    _language = code if code in LANGUAGES else "en"


def tr(text: str, **values: object) -> str:
    translated = _DE.get(text, text) if _language == "de" else text
    return translated.format(**values) if values else translated
