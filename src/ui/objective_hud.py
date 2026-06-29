from __future__ import annotations

import pygame

from src.ui.fonts import load_chinese_font


LABEL_OBJECTIVE = "\u5f53\u524d\u76ee\u6807\uff1a"
LABEL_HINT = "\u63d0\u793a\uff1a"


class ObjectiveHUD:
    """Small objective panel for player guidance."""

    WIDTH = 252
    PADDING = 8
    LEFT_MARGIN = 12
    DEFAULT_TOP = 58
    DEBUG_TOP = 148
    LINE_GAP = 4

    def __init__(self, font: pygame.font.Font) -> None:
        self.title_font = load_chinese_font(16, font)
        self.text_font = load_chinese_font(14, font)

    def draw(
        self,
        surface: pygame.Surface,
        title: str,
        hint: str,
        extra: str = "",
        avoid_debug: bool = False,
    ) -> None:
        lines = [f"{LABEL_OBJECTIVE}{title}", f"{LABEL_HINT}{hint}"]
        if extra:
            lines.append(extra)

        rendered = [
            (self.title_font if index == 0 else self.text_font).render(line, True, (242, 238, 218))
            for index, line in enumerate(lines)
        ]
        line_height = max(item.get_height() for item in rendered)
        height = self.PADDING * 2 + len(rendered) * line_height + (len(rendered) - 1) * self.LINE_GAP
        top = self.DEBUG_TOP if avoid_debug else self.DEFAULT_TOP
        rect = pygame.Rect(self.LEFT_MARGIN, top, self.WIDTH, height)

        panel = pygame.Surface(rect.size, pygame.SRCALPHA)
        pygame.draw.rect(panel, (20, 18, 22, 150), panel.get_rect(), border_radius=5)
        pygame.draw.rect(panel, (184, 150, 86, 205), panel.get_rect(), 1, border_radius=5)
        surface.blit(panel, rect.topleft)

        y = rect.y + self.PADDING
        for item in rendered:
            surface.blit(item, (rect.x + self.PADDING, y))
            y += line_height + self.LINE_GAP
