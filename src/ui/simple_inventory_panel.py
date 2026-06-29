from __future__ import annotations

from pathlib import Path

import pygame

from src.ui.fonts import load_chinese_font


ITEM_LABELS = (
    ("silver_thread", "\u94f6\u4e1d\u6750\u6599"),
    ("flower_bird_pattern_clue", "\u82b1\u9e1f\u7eb9\u6837\u7ebf\u7d22"),
    ("pattern_wooden_plaque", "\u7eb9\u6837\u6728\u724c"),
    ("mountain_pattern_clue", "\u5c71\u7eb9\u7ebf\u7d22"),
)
ITEM_SPRITES = {
    "silver_thread": "assets/sprites/items/silver_thread.png",
    "flower_bird_pattern_clue": "assets/sprites/items/flower_bird_pattern_clue.png",
    "pattern_wooden_plaque": "assets/sprites/items/pattern_wooden_plaque.png",
}

LEVEL_LABELS = (
    ("market_collect", "\u96c6\u5e02\u5bfb\u6e90"),
    ("shadow_challenge", "\u6cb3\u8c37\u51c0\u5316"),
    ("festival_defense", "\u8282\u5e86\u5b88\u62a4"),
)


class SimpleInventoryPanel:
    """Compact read-only clue and progress panel for demo flow."""

    def __init__(self, font: pygame.font.Font) -> None:
        self.visible = False
        self.title_font = load_chinese_font(18, font)
        self.text_font = load_chinese_font(16, font)
        self.muted_color = (194, 188, 170)
        self.text_color = (244, 238, 220)
        self.done_color = (190, 235, 190)
        self.icon_size = 30
        self.icons = self._load_icons()

    def toggle(self) -> None:
        self.visible = not self.visible
        print(f"[INVENTORY] show={self.visible}")

    def draw(
        self,
        surface: pygame.Surface,
        quest_manager,
        player_light: int | None = None,
        max_player_light: int | None = None,
    ) -> None:
        if not self.visible:
            return

        items = quest_manager.get_items()
        completed = quest_manager.get_completed_levels()
        if player_light is None:
            player_light = getattr(quest_manager, "player_light", None)
        if max_player_light is None:
            max_player_light = getattr(quest_manager, "max_player_light", None)
        light_text = "--" if player_light is None or max_player_light is None else f"{player_light}/{max_player_light}"

        width = 360
        row_height = 34
        section_gap = 14
        title_height = 24
        footer_height = 26
        height = (
            18
            + title_height
            + len(ITEM_LABELS) * row_height
            + section_gap
            + title_height
            + len(LEVEL_LABELS) * 24
            + section_gap
            + title_height
            + 24
            + footer_height
            + 18
        )
        rect = pygame.Rect(12, surface.get_height() - height - 16, width, height)
        panel = pygame.Surface(rect.size, pygame.SRCALPHA)
        pygame.draw.rect(panel, (18, 17, 22, 190), panel.get_rect(), border_radius=7)
        pygame.draw.rect(panel, (185, 152, 86, 220), panel.get_rect(), 1, border_radius=7)
        surface.blit(panel, rect.topleft)

        y = rect.y + 12
        y = self._draw_section_title(surface, "\u6536\u96c6\u7269", rect.x + 16, y)
        for item_id, label in ITEM_LABELS:
            acquired = item_id in items
            self._draw_item_row(surface, rect.x + 16, y, item_id, label, acquired)
            y += row_height

        y += section_gap - 4
        y = self._draw_section_title(surface, "\u5173\u5361\u8fdb\u5ea6", rect.x + 16, y)
        for level_id, label in LEVEL_LABELS:
            done = level_id in completed
            state = "\u5b8c\u6210" if done else "\u672a\u5b8c\u6210"
            color = self.done_color if done else self.muted_color
            text = self.text_font.render(f"{label}\uff1a{state}", True, color)
            surface.blit(text, (rect.x + 22, y))
            y += 24

        y += section_gap - 4
        y = self._draw_section_title(surface, "\u94f6\u5149\u72b6\u6001", rect.x + 16, y)
        light = self.text_font.render(f"\u94f6\u5149\uff1a{light_text}", True, self.text_color)
        surface.blit(light, (rect.x + 22, y))
        hint = self.text_font.render("B\uff1a\u5173\u95ed", True, self.muted_color)
        surface.blit(hint, (rect.right - hint.get_width() - 18, rect.bottom - 30))

    def _load_icons(self) -> dict[str, pygame.Surface]:
        icons = {}
        for item_id, sprite_path in ITEM_SPRITES.items():
            path = Path(sprite_path)
            if not path.exists():
                continue
            try:
                image = pygame.image.load(str(path)).convert_alpha()
                icons[item_id] = pygame.transform.smoothscale(image, (self.icon_size, self.icon_size))
            except pygame.error as exc:
                print(f"[INVENTORY][WARN] icon load failed item={item_id} sprite={sprite_path} error={exc}")
        return icons

    def _draw_section_title(self, surface: pygame.Surface, title: str, x: int, y: int) -> int:
        text = self.title_font.render(title, True, self.text_color)
        surface.blit(text, (x, y))
        return y + 26

    def _draw_item_row(self, surface: pygame.Surface, x: int, y: int, item_id: str, label: str, acquired: bool) -> None:
        icon_rect = pygame.Rect(x, y + 1, self.icon_size, self.icon_size)
        icon = self.icons.get(item_id)
        if icon is not None:
            if acquired:
                surface.blit(icon, icon_rect)
            else:
                dim_icon = icon.copy()
                dim_icon.fill((60, 60, 60, 130), special_flags=pygame.BLEND_RGBA_MULT)
                surface.blit(dim_icon, icon_rect)
        else:
            pygame.draw.rect(surface, (68, 62, 70), icon_rect, border_radius=4)
            pygame.draw.rect(surface, (170, 150, 108), icon_rect, 1, border_radius=4)
            placeholder = self.text_font.render("?", True, self.muted_color)
            surface.blit(placeholder, placeholder.get_rect(center=icon_rect.center))

        color = self.done_color if acquired else self.muted_color
        state = "\u5df2\u83b7\u5f97" if acquired else "\u672a\u83b7\u5f97"
        text = self.text_font.render(f"{label}  {state}", True, color)
        surface.blit(text, (x + self.icon_size + 12, y + 6))
