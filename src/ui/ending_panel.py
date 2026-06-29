from __future__ import annotations

import math

import pygame

from src.ui.fonts import load_chinese_font


ENDING_TITLE = "银饰重焕光彩"
ENDING_BADGE = "修复完成"
ENDING_BODY = (
    "恭喜你完成了纹样寻源与银饰守护之旅！",
    "你收集了修复线索，净化了混乱影纹，也守护了节庆银饰的展示台。",
    "在你的努力下，银纹秘境重新恢复了光芒。",
)
COLLECT_ITEMS = (
    "silver_thread",
    "flower_bird_pattern_clue",
    "pattern_wooden_plaque",
    "mountain_pattern_clue",
)


class EndingPanel:
    """Compact final result panel shown when the main quest reaches ending."""

    def __init__(self, font: pygame.font.Font) -> None:
        self.title_font = load_chinese_font(30, font)
        self.text_font = load_chinese_font(18, font)
        self.small_font = load_chinese_font(16, font)

    def draw(
        self,
        surface: pygame.Surface,
        quest_manager,
        stand_light: int,
        max_stand_light: int,
        player_light: int,
        max_player_light: int,
    ) -> None:
        overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        pygame.draw.rect(overlay, (0, 0, 0, 120), overlay.get_rect())
        surface.blit(overlay, (0, 0))

        rect = pygame.Rect(82, 72, surface.get_width() - 164, surface.get_height() - 132)
        panel = pygame.Surface(rect.size, pygame.SRCALPHA)
        pygame.draw.rect(panel, (22, 18, 22, 232), panel.get_rect(), border_radius=9)
        pygame.draw.rect(panel, (226, 218, 190, 235), panel.get_rect(), 2, border_radius=9)
        pygame.draw.rect(panel, (126, 92, 58, 180), panel.get_rect().inflate(-12, -12), 1, border_radius=7)
        surface.blit(panel, rect.topleft)

        self._draw_completion_glow(surface, rect)
        title = self.title_font.render(ENDING_TITLE, True, (248, 246, 232))
        surface.blit(title, title.get_rect(center=(rect.centerx, rect.y + 38)))

        badge = self.small_font.render(ENDING_BADGE, True, (255, 248, 220))
        badge_rect = badge.get_rect(center=(rect.centerx, rect.y + 68))
        badge_bg = badge_rect.inflate(24, 8)
        pygame.draw.rect(surface, (106, 72, 48), badge_bg, border_radius=badge_bg.height // 2)
        pygame.draw.rect(surface, (226, 214, 176), badge_bg, 1, border_radius=badge_bg.height // 2)
        surface.blit(badge, badge_rect)

        y = rect.y + 102
        for line in ENDING_BODY:
            rendered = self.text_font.render(line, True, (232, 224, 204))
            surface.blit(rendered, (rect.x + 42, y))
            y += 30

        completed = quest_manager.get_completed_levels()
        items = quest_manager.get_items()
        collected_count = sum(1 for item_id in COLLECT_ITEMS if item_id in items)
        rating = self._rating(completed, collected_count, stand_light, max_stand_light, player_light, max_player_light)
        summary_lines = [
            f"集市寻源：{self._done_text('market_collect' in completed)}",
            f"河谷净化：{self._done_text('shadow_challenge' in completed)}",
            f"节庆守护：{self._done_text('festival_defense' in completed)}",
            f"收集材料数：{collected_count} / {len(COLLECT_ITEMS)}",
            f"剩余银光：{player_light} / {max_player_light}",
            f"展示台光芒：{stand_light} / {max_stand_light}",
            f"综合评价：{rating}",
        ]
        y += 8
        for line in summary_lines:
            rendered = self.text_font.render(line, True, (244, 232, 190))
            surface.blit(rendered, (rect.x + 72, y))
            y += 27

        hint = self.small_font.render("Enter：关闭结算    R：重新体验    Esc：返回游戏", True, (204, 198, 182))
        surface.blit(hint, hint.get_rect(center=(rect.centerx, rect.bottom - 28)))

    def _draw_completion_glow(self, surface: pygame.Surface, rect: pygame.Rect) -> None:
        now = pygame.time.get_ticks()
        pulse = 0.5 + 0.5 * math.sin(now / 360.0)
        center = (rect.centerx, rect.y + 42)
        for index, radius in enumerate((46, 70, 94)):
            alpha = int((58 - index * 14) + pulse * 22)
            glow = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(glow, (238, 232, 196, alpha), (radius, radius), radius)
            surface.blit(glow, (center[0] - radius, center[1] - radius))

    def _done_text(self, done: bool) -> str:
        return "完成" if done else "未完成"

    def _rating(
        self,
        completed: set[str],
        collected_count: int,
        stand_light: int,
        max_stand_light: int,
        player_light: int,
        max_player_light: int,
    ) -> str:
        required = {"market_collect", "shadow_challenge", "festival_defense"}
        if not required.issubset(completed):
            return "纹样守护完成"
        if (
            collected_count >= len(COLLECT_ITEMS)
            and stand_light >= max(1, max_stand_light - 1)
            and player_light >= max_player_light
        ):
            return "优秀守护者"
        if collected_count >= 3 and stand_light >= 3 and player_light >= 2:
            return "银饰修复学徒"
        return "纹样守护完成"
