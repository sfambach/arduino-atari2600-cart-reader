"""Multicarts that switch to the next game at every power-on (e.g. the Atari 32 in 1).

The reader powers the cartridge only while a command runs, so every read shows the next game. Reading until
the first game comes back yields all games; the counter's starting point is unknown, so the order is
rotated until the whole image matches the game list (Stella's 2IN1 ... 128IN1 format: games one after another).
"""
from __future__ import annotations

import time
from typing import Callable, Optional

from .reader import Reader, ReaderError
from .rom import md5

MAX_GAMES = 128
PAUSE = 0.5  # s with the supply off between two reads, so the cartridge's power-on counter steps


def _one_game(reader: Reader) -> bytes:
    data = reader.dump("4K")
    return data[:0x800] if data[:0x800] == data[0x800:] else data


def read_all(reader: Reader, progress: Optional[Callable[[int, int], None]] = None,
             pause: float = PAUSE) -> list[bytes]:
    games = [_one_game(reader)]
    while len(games) < MAX_GAMES:
        time.sleep(pause)
        game = _one_game(reader)
        if game == games[0]:
            break
        if len(game) != len(games[0]):
            raise ReaderError("games of different size: not a power-on multicart")
        games.append(game)
        if progress:
            progress(len(games), 32 if len(games) <= 32 else MAX_GAMES)
    if len(games) == 1:
        raise ReaderError("the same game after switching off and on: not a power-on multicart")
    return games


def scheme(games: list[bytes]) -> str:
    n = len(games)
    return f"{n}IN1" if n in (2, 4, 8, 16, 32, 64, 128) else "4K"


def assemble(games: list[bytes], known: dict[str, str]) -> tuple[bytes, Optional[str]]:
    """Join the games, rotated so the image matches the game list when it can; returns image and title."""
    for k in range(len(games)):
        image = b"".join(games[k:] + games[:k])
        title = known.get(md5(image))
        if title:
            return image, title
    return b"".join(games), None
