from __future__ import annotations

import pygame

from src.ui.fonts import load_chinese_font


SCENE_DISPLAY_NAMES = {
    "village": "\u6751\u5be8\u5165\u53e3",
    "village_hub": "\u6751\u5be8\u5165\u53e3",
    "workshop": "\u94f6\u9970\u5de5\u574a",
    "workshop_exterior": "\u94f6\u9970\u5de5\u574a",
    "workshop_interior": "\u94f6\u9970\u5de5\u574a",
    "village_market": "\u5c71\u5730\u96c6\u5e02",
    "market": "\u5c71\u5730\u96c6\u5e02",
    "river_valley": "\u6cb3\u8c37\u5bfb\u6e90",
    "mountain": "\u5c71\u5730\u81ea\u7136\u573a\u666f",
    "festival": "\u8282\u5e86\u5e7f\u573a",
    "festival_square": "\u8282\u5e86\u5e7f\u573a",
}
LOCK_HINT_DEFAULT = "\u5f53\u524d\u8fd8\u4e0d\u80fd\u524d\u5f80"


class NavigationPanel:
    """Compact bottom-right navigation and interaction hints."""

    WIDTH = 232
    PADDING = 7
    LINE_GAP = 2
    BOTTOM_MARGIN = 10
    RIGHT_MARGIN = 10
    MAX_EXITS = 3

    def __init__(self, font: pygame.font.Font, small_font: pygame.font.Font | None = None) -> None:
        self.font = load_chinese_font(18, font)
        self.small_font = load_chinese_font(16, small_font or font)
        self.expanded = False
        self.text_color = (235, 230, 210)
        self.muted_color = (184, 180, 162)
        self.highlight_color = (255, 218, 120)
        self.border_color = (170, 138, 78)
        self.background_color = (14, 16, 20, 152)

    def toggle_expanded(self) -> None:
        self.expanded = not self.expanded

    def draw(
        self,
        surface: pygame.Surface,
        current_scene_id: str,
        nearby_exits: list[dict],
        selected_exit: dict | None,
        nearby_npc=None,
        nearby_item=None,
    ) -> None:
        lines = self._build_lines(current_scene_id, nearby_exits, selected_exit, nearby_npc, nearby_item)
        rendered = [(self._font_for(line), self._color_for(line), line) for line in lines]
        max_text_width = self.WIDTH - self.PADDING * 2
        text_surfaces = [
            self._render_line(font, self._strip_marker(line), color, max_text_width)
            for font, color, line in rendered
        ]
        line_height = max(surface_item.get_height() for surface_item in text_surfaces)
        panel_height = self.PADDING * 2 + len(text_surfaces) * line_height + (len(text_surfaces) - 1) * self.LINE_GAP
        panel_rect = pygame.Rect(
            surface.get_width() - self.WIDTH - self.RIGHT_MARGIN,
            surface.get_height() - panel_height - self.BOTTOM_MARGIN,
            self.WIDTH,
            panel_height,
        )

        panel_surface = pygame.Surface(panel_rect.size, pygame.SRCALPHA)
        pygame.draw.rect(panel_surface, self.background_color, panel_surface.get_rect(), border_radius=5)
        pygame.draw.rect(panel_surface, self.border_color, panel_surface.get_rect(), 1, border_radius=5)
        surface.blit(panel_surface, panel_rect.topleft)

        y = panel_rect.y + self.PADDING
        for text_surface in text_surfaces:
            surface.blit(text_surface, (panel_rect.x + self.PADDING, y))
            y += line_height + self.LINE_GAP

    def _build_lines(
        self,
        current_scene_id: str,
        nearby_exits: list[dict],
        selected_exit: dict | None,
        nearby_npc,
        nearby_item,
    ) -> list[str]:
        scene_name = self.scene_name(current_scene_id)
        if self.expanded:
            return self._build_expanded_lines(scene_name, nearby_exits, selected_exit, nearby_npc, nearby_item)
        return self._build_compact_lines(scene_name, nearby_exits, selected_exit, nearby_npc, nearby_item)

    def _build_compact_lines(
        self,
        scene_name: str,
        nearby_exits: list[dict],
        selected_exit: dict | None,
        nearby_npc,
        nearby_item,
    ) -> list[str]:
        lines = [f"\u5f53\u524d\u4f4d\u7f6e\uff1a{scene_name}"]
        if nearby_exits:
            if len(nearby_exits) == 1:
                lines.append(f"\u51fa\u53e3\uff1a{self._exit_label(nearby_exits[0])}")
                if nearby_exits[0].get("_quest_locked"):
                    lines.append(f"!{nearby_exits[0].get('_quest_lock_hint', LOCK_HINT_DEFAULT)}")
                    lines.append("*E/Enter\uff1a\u67e5\u770b\u63d0\u793a")
                else:
                    lines.append("*E/Enter\uff1a\u8fdb\u5165")
            else:
                lines.append("\u591a\u4e2a\u51fa\u53e3")
                lines.append("*1/2/3\uff1a\u9009\u62e9")
                if selected_exit is not None and selected_exit.get("_quest_locked"):
                    lines.append(f"!{selected_exit.get('_quest_lock_hint', LOCK_HINT_DEFAULT)}")
                    lines.append("*E/Enter\uff1a\u67e5\u770b\u63d0\u793a")
                else:
                    lines.append("*E/Enter\uff1a\u8fdb\u5165")
        elif nearby_npc is not None:
            npc_name = getattr(nearby_npc, "name", None) or getattr(nearby_npc, "id", "NPC")
            lines.extend([f"NPC\uff1a{npc_name}", "*E/Enter\uff1a\u5bf9\u8bdd"])
        elif nearby_item is not None:
            item_name = getattr(nearby_item, "name", None) or getattr(nearby_item, "id", "\u9053\u5177")
            lines.extend([f"\u9053\u5177\uff1a{item_name}", "*E/Enter\uff1a\u4ea4\u4e92"])
        else:
            lines.extend(["\u65b9\u5411\u952e\uff1a\u79fb\u52a8", "*E/Enter\uff1a\u4ea4\u4e92"])
        return lines

    def _build_expanded_lines(
        self,
        scene_name: str,
        nearby_exits: list[dict],
        selected_exit: dict | None,
        nearby_npc,
        nearby_item,
    ) -> list[str]:
        lines = [f"\u5f53\u524d\u4f4d\u7f6e\uff1a{scene_name}"]
        if nearby_exits:
            if len(nearby_exits) == 1:
                lines.append(f"\u51fa\u53e3\uff1a{self._exit_label(nearby_exits[0])}")
                if nearby_exits[0].get("_quest_locked"):
                    lines.extend([
                        f"!{nearby_exits[0].get('_quest_lock_hint', LOCK_HINT_DEFAULT)}",
                        "*E/Enter\uff1a\u67e5\u770b\u63d0\u793a",
                        "F1\u6536\u8d77",
                    ])
                else:
                    lines.extend(["*E/Enter\uff1a\u8fdb\u5165", "F1\u6536\u8d77"])
            else:
                lines.append("\u591a\u4e2a\u51fa\u53e3")
                for index, scene_exit in enumerate(nearby_exits[: self.MAX_EXITS], start=1):
                    prefix = "> " if self._same_exit(scene_exit, selected_exit) else "  "
                    lines.append(f"{prefix}[{index}] {self._exit_label(scene_exit)}")
                lines.append("*1/2/3\uff1a\u9009\u62e9")
                if selected_exit is not None and selected_exit.get("_quest_locked"):
                    lines.append(f"!{selected_exit.get('_quest_lock_hint', LOCK_HINT_DEFAULT)}")
                    lines.append("*E/Enter\uff1a\u67e5\u770b\u63d0\u793a")
                else:
                    lines.append("*E/Enter\uff1a\u8fdb\u5165")
                lines.append("F1\u6536\u8d77")
        elif nearby_npc is not None:
            npc_name = getattr(nearby_npc, "name", None) or getattr(nearby_npc, "id", "NPC")
            lines.extend([f"NPC\uff1a{npc_name}", "*E/Enter\uff1a\u5bf9\u8bdd", "F1\u6536\u8d77"])
        elif nearby_item is not None:
            item_name = getattr(nearby_item, "name", None) or getattr(nearby_item, "id", "\u9053\u5177")
            lines.extend([f"\u9053\u5177\uff1a{item_name}", "*E/Enter\uff1a\u4ea4\u4e92", "F1\u6536\u8d77"])
        else:
            lines.extend(["\u65b9\u5411\u952e\uff1a\u79fb\u52a8", "*E/Enter\uff1a\u4ea4\u4e92", "F1\u6536\u8d77"])
        return lines

    def _exit_label(self, scene_exit: dict | None) -> str:
        if scene_exit is None:
            return "\u65e0"
        label = self.scene_name(str(scene_exit.get("target_scene") or ""))
        if scene_exit.get("_quest_locked"):
            return f"{label}\uff08\u672a\u89e3\u9501\uff09"
        return label

    def scene_name(self, scene_id: str) -> str:
        return SCENE_DISPLAY_NAMES.get(scene_id, scene_id or "\u672a\u77e5\u573a\u666f")

    def _same_exit(self, left: dict | None, right: dict | None) -> bool:
        if left is None or right is None:
            return False
        return str(left.get("id")) == str(right.get("id"))

    def _font_for(self, line: str) -> pygame.font.Font:
        return self.font if not line.startswith((">", "  ", "*", "!")) else self.small_font

    def _color_for(self, line: str) -> tuple[int, int, int]:
        if line.startswith(">") or line.startswith("*"):
            return self.highlight_color
        if line.startswith("!") or line.startswith("  "):
            return self.muted_color
        return self.text_color

    def _strip_marker(self, line: str) -> str:
        if line.startswith("*") or line.startswith("!"):
            return line[1:]
        return line

    def _render_line(
        self,
        font: pygame.font.Font,
        text: str,
        color: tuple[int, int, int],
        max_width: int,
    ) -> pygame.Surface:
        if font.size(text)[0] <= max_width:
            return font.render(text, True, color)

        ellipsis = "..."
        trimmed = text
        while trimmed and font.size(f"{trimmed}{ellipsis}")[0] > max_width:
            trimmed = trimmed[:-1]
        return font.render(f"{trimmed}{ellipsis}", True, color)
