from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import pygame


FONT_CANDIDATES = (
    Path("assets/fonts/msyh.ttc"),
    Path("assets/fonts/simhei.ttf"),
    Path("assets/fonts/simsun.ttc"),
    Path("C:/Windows/Fonts/msyh.ttc"),
    Path("C:/Windows/Fonts/simhei.ttf"),
    Path("C:/Windows/Fonts/simsun.ttc"),
)

_warned_missing_chinese_font = False


@lru_cache(maxsize=32)
def _load_font_from_path(path_text: str, size: int) -> pygame.font.Font:
    return pygame.font.Font(path_text, size)


def find_chinese_font_path() -> Path | None:
    for font_path in FONT_CANDIDATES:
        if font_path.exists():
            return font_path
    return None


def load_chinese_font(size: int, fallback: pygame.font.Font | None = None) -> pygame.font.Font:
    global _warned_missing_chinese_font

    font_path = find_chinese_font_path()
    if font_path is not None:
        return _load_font_from_path(str(font_path), size)

    if not _warned_missing_chinese_font:
        print("[FONT][WARN] Chinese font not found, fallback may show garbled text")
        _warned_missing_chinese_font = True

    try:
        return pygame.font.Font(None, size)
    except pygame.error:
        if fallback is not None:
            return fallback
        raise
