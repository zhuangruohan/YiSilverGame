from enum import Enum


class GameState(str, Enum):
    """Top-level game states shared by core and scenes."""

    MENU = "MENU"
    PLAYING = "PLAYING"
    DIALOGUE = "DIALOGUE"
    INVENTORY = "INVENTORY"
    CODEX = "CODEX"
    PATTERN_REALM = "PATTERN_REALM"
    REPAIR_MINIGAME = "REPAIR_MINIGAME"
    ENDING = "ENDING"
