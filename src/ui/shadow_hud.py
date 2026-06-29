from __future__ import annotations

import pygame

from src.entities.shadow_spirit import ShadowSpirit
from src.ui.fonts import load_chinese_font


TEXT_READY_TITLE = "\u5f71\u7eb9\u6311\u6218"
TEXT_READY_HINT = "\u9760\u8fd1\u5f71\u7eb9\u5f00\u59cb"
TEXT_PURIFY_FULL = "Space\uff1a\u94f6\u5149\u51c0\u5316"
TEXT_DEFEATED = "\u5f71\u7eb9\u5df2\u51c0\u5316"
TEXT_REWARD = "\u83b7\u5f97\u5c71\u7eb9\u7ebf\u7d22"
TEXT_FAILED = "\u94f6\u5149\u6682\u65f6\u6697\u6de1"
TEXT_RETRY = "\u8bf7\u91cd\u65b0\u5c1d\u8bd5"
TEXT_CHASE = "\u5f71\u7eb9\u8ffd\u9010\u4e2d"
TEXT_HIT = "\u94f6\u5149\u547d\u4e2d"
TEXT_LIGHT = "\u94f6\u5149"
TEXT_SHADOW = "\u5f71\u7eb9"
TEXT_PURIFY = "Space\uff1a\u51c0\u5316"
TEXT_COOLDOWN = "Space\uff1a\u51b7\u5374\u4e2d"


class ShadowHUD:
    """Small top-right HUD for the demo shadow chase challenge."""

    WIDTH = 188
    PADDING = 8
    RIGHT_MARGIN = 12
    TOP_MARGIN = 14
    LINE_GAP = 3

    def __init__(self, font: pygame.font.Font) -> None:
        self.font = load_chinese_font(17, font)
        self.small_font = load_chinese_font(15, font)

    def draw(self, surface: pygame.Surface, manager) -> None:
        lines = self._build_lines(manager)
        if not lines:
            return

        rendered = [
            (self.font if index == 0 else self.small_font).render(line, True, (242, 238, 218))
            for index, line in enumerate(lines)
        ]
        line_height = max(item.get_height() for item in rendered)
        height = self.PADDING * 2 + len(rendered) * line_height + (len(rendered) - 1) * self.LINE_GAP
        rect = pygame.Rect(
            surface.get_width() - self.WIDTH - self.RIGHT_MARGIN,
            self.TOP_MARGIN,
            self.WIDTH,
            height,
        )
        panel = pygame.Surface(rect.size, pygame.SRCALPHA)
        pygame.draw.rect(panel, (18, 16, 24, 158), panel.get_rect(), border_radius=5)
        pygame.draw.rect(panel, (168, 128, 220, 210), panel.get_rect(), 1, border_radius=5)
        surface.blit(panel, rect.topleft)

        y = rect.y + self.PADDING
        for item in rendered:
            surface.blit(item, (rect.x + self.PADDING, y))
            y += line_height + self.LINE_GAP

    def _build_lines(self, manager) -> list[str]:
        if manager.hud_mode == "ready":
            return [TEXT_READY_TITLE, TEXT_READY_HINT, TEXT_PURIFY_FULL]

        if manager.hud_mode == "defeated":
            return [TEXT_DEFEATED, TEXT_REWARD]

        if manager.hud_mode == "failed":
            return [TEXT_FAILED, TEXT_RETRY]

        if manager.hud_mode != "active":
            return []

        shadow = manager.strongest_shadow()
        shadow_hp = shadow.hp if shadow is not None else 0
        shadow_max_hp = shadow.max_hp if shadow is not None else 3
        action_text = TEXT_PURIFY if manager.is_purify_ready() else TEXT_COOLDOWN
        state_text = TEXT_CHASE
        if shadow is not None and shadow.state == ShadowSpirit.HIT:
            state_text = TEXT_HIT
        return [
            state_text,
            f"{TEXT_LIGHT}\uff1a{manager.player_light}/{manager.PLAYER_MAX_LIGHT}",
            f"{TEXT_SHADOW}\uff1a{shadow_hp}/{shadow_max_hp}",
            action_text,
        ]
