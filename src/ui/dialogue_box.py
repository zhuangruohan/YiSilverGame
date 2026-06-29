from __future__ import annotations

import pygame

from settings import SCREEN_HEIGHT, SCREEN_WIDTH
from src.ui.fonts import load_chinese_font


class DialogueBox:
    """Bottom dialogue panel for the active NPC conversation."""

    WIDTH_RATIO = 0.78
    HEIGHT = 148
    BOTTOM_MARGIN = 24
    PADDING = 20

    def __init__(self, font: pygame.font.Font) -> None:
        self.name_font = load_chinese_font(26, font)
        self.text_font = load_chinese_font(24, font)
        self.small_font = load_chinese_font(19, font)

    def draw(self, surface: pygame.Surface, speaker: str, text: str) -> None:
        box_width = int(SCREEN_WIDTH * self.WIDTH_RATIO)
        box_rect = pygame.Rect(
            (SCREEN_WIDTH - box_width) // 2,
            SCREEN_HEIGHT - self.HEIGHT - self.BOTTOM_MARGIN,
            box_width,
            self.HEIGHT,
        )
        panel = pygame.Surface(box_rect.size, pygame.SRCALPHA)
        pygame.draw.rect(panel, (24, 22, 28, 218), panel.get_rect(), border_radius=6)
        pygame.draw.rect(panel, (215, 200, 150, 230), panel.get_rect(), 1, border_radius=6)
        surface.blit(panel, box_rect.topleft)

        name_surface = self.name_font.render(speaker or "NPC", True, (142, 232, 168))
        surface.blit(name_surface, (box_rect.x + self.PADDING, box_rect.y + 14))

        y = box_rect.y + 48
        for line in self._wrap_text(text or "……", box_rect.width - self.PADDING * 2):
            text_surface = self.text_font.render(line, True, (245, 240, 220))
            surface.blit(text_surface, (box_rect.x + self.PADDING, y))
            y += self.text_font.get_linesize()

        hint = "Enter/Space：下一句    Esc：关闭"
        hint_surface = self.small_font.render(hint, True, (190, 190, 184))
        surface.blit(hint_surface, (box_rect.x + self.PADDING, box_rect.bottom - 25))

    def _wrap_text(self, text: str, max_width: int) -> list[str]:
        lines: list[str] = []
        current = ""
        for char in text:
            candidate = f"{current}{char}"
            if current and self.text_font.size(candidate)[0] > max_width:
                lines.append(current)
                current = char
            else:
                current = candidate
        if current:
            lines.append(current)
        return lines[:3] or ["……"]
