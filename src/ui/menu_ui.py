from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pygame

from settings import SCREEN_HEIGHT, SCREEN_WIDTH
from src.ui.fonts import load_chinese_font


TITLE_MAIN = "银纹秘境"
TITLE_SUB = "彝饰守护者"
TAGLINE = "一场关于银饰、纹样与传承的旅程"
FOOTER_HINT = "WASD/方向键移动 / E/Enter交互 / B背包 / Esc返回"
MAKER_TEXT = "制作：银纹工坊 / 基于 Pygame 开发"


@dataclass
class MenuButton:
    text: str
    action: str
    rect: pygame.Rect

    def draw(self, surface: pygame.Surface, font: pygame.font.Font, hovered: bool) -> None:
        panel = pygame.Surface(self.rect.size, pygame.SRCALPHA)
        base = (116, 42, 34, 218) if not hovered else (158, 62, 46, 238)
        border = (214, 202, 176, 218) if not hovered else (245, 238, 214, 255)
        pygame.draw.rect(panel, base, panel.get_rect(), border_radius=6)
        pygame.draw.rect(panel, (62, 24, 20, 190), panel.get_rect().inflate(-8, -8), 1, border_radius=4)
        pygame.draw.rect(panel, border, panel.get_rect(), 2, border_radius=6)

        left_gem = pygame.Rect(14, self.rect.height // 2 - 8, 16, 16)
        right_gem = pygame.Rect(self.rect.width - 30, self.rect.height // 2 - 8, 16, 16)
        pygame.draw.ellipse(panel, (230, 226, 210, 220), left_gem)
        pygame.draw.ellipse(panel, (230, 226, 210, 220), right_gem)
        pygame.draw.ellipse(panel, (78, 70, 66, 220), left_gem, 1)
        pygame.draw.ellipse(panel, (78, 70, 66, 220), right_gem, 1)

        surface.blit(panel, self.rect.topleft)
        color = (255, 247, 224) if hovered else (242, 232, 210)
        text_surface = font.render(self.text, True, color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)


class MenuUI:
    """Draws and handles the start menu without owning game state."""

    def __init__(
        self,
        title_font: pygame.font.Font,
        menu_font: pygame.font.Font,
        small_font: pygame.font.Font,
    ) -> None:
        self.title_font = load_chinese_font(68, title_font)
        self.subtitle_font = load_chinese_font(30, menu_font)
        self.menu_font = load_chinese_font(28, menu_font)
        self.small_font = load_chinese_font(18, small_font)
        self.help_title_font = load_chinese_font(34, title_font)
        self.help_section_font = load_chinese_font(24, menu_font)
        self.help_font = load_chinese_font(22, small_font)
        self.help_hint_font = load_chinese_font(20, small_font)
        self.show_help = False
        self.background = self._load_background()
        self.buttons = self._create_buttons()

    def handle_event(self, event: pygame.event.Event) -> str | None:
        if event.type == pygame.KEYDOWN:
            if self.show_help:
                if event.key in (pygame.K_ESCAPE, pygame.K_RETURN):
                    self.show_help = False
                    return "handled"
                return None
            if event.key == pygame.K_RETURN:
                return "start"
            if event.key == pygame.K_ESCAPE:
                return "quit"

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.show_help:
                self.show_help = False
                return "handled"
            for button in self.buttons:
                if button.rect.collidepoint(event.pos):
                    if button.action == "help":
                        self.show_help = True
                        return "handled"
                    return button.action
        return None

    def draw(self, surface: pygame.Surface) -> None:
        mouse_pos = pygame.mouse.get_pos()
        self._draw_background(surface)
        self._draw_corner_ornaments(surface)
        self._draw_title(surface)
        if not self.show_help:
            self._draw_buttons(surface, mouse_pos)
            self._draw_footer(surface)
        if self.show_help:
            self._draw_help_panel(surface)

    def _create_buttons(self) -> list[MenuButton]:
        width = 246
        height = 48
        left = SCREEN_WIDTH // 2 - width // 2
        top = 338
        gap = 16
        return [
            MenuButton("开始游戏", "start", pygame.Rect(left, top, width, height)),
            MenuButton("游戏说明", "help", pygame.Rect(left, top + height + gap, width, height)),
            MenuButton("退出游戏", "quit", pygame.Rect(left, top + (height + gap) * 2, width, height)),
        ]

    def _load_background(self) -> pygame.Surface | None:
        path = Path("assets/images/village_hub.png")
        if not path.exists():
            return None
        try:
            image = pygame.image.load(str(path)).convert()
        except pygame.error as exc:
            print(f"[MENU][WARN] background load failed path={path} error={exc}")
            return None
        return pygame.transform.smoothscale(image, (SCREEN_WIDTH, SCREEN_HEIGHT))

    def _draw_background(self, surface: pygame.Surface) -> None:
        if self.background is not None:
            surface.blit(self.background, (0, 0))
            shade = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            pygame.draw.rect(shade, (8, 10, 14, 152), shade.get_rect())
            pygame.draw.rect(shade, (44, 16, 20, 50), pygame.Rect(0, 300, SCREEN_WIDTH, 300))
            surface.blit(shade, (0, 0))
            return

        for y in range(SCREEN_HEIGHT):
            ratio = y / SCREEN_HEIGHT
            r = int(16 + ratio * 24)
            g = int(18 + ratio * 12)
            b = int(24 + ratio * 8)
            pygame.draw.line(surface, (r, g, b), (0, y), (SCREEN_WIDTH, y))
        pygame.draw.circle(surface, (84, 84, 98), (620, 118), 84, 1)
        pygame.draw.polygon(surface, (18, 24, 28), [(0, 238), (120, 150), (230, 232), (360, 128), (800, 248), (800, 600), (0, 600)])

    def _draw_corner_ornaments(self, surface: pygame.Surface) -> None:
        color = (215, 214, 204)
        dim = (160, 150)
        margin = 13
        for flip_x, flip_y in ((False, False), (True, False), (False, True), (True, True)):
            corner = pygame.Surface(dim, pygame.SRCALPHA)
            self._draw_single_corner(corner, color)
            if flip_x:
                corner = pygame.transform.flip(corner, True, False)
            if flip_y:
                corner = pygame.transform.flip(corner, False, True)
            x = margin if not flip_x else SCREEN_WIDTH - dim[0] - margin
            y = margin if not flip_y else SCREEN_HEIGHT - dim[1] - margin
            surface.blit(corner, (x, y))
        pygame.draw.rect(surface, (210, 210, 198), pygame.Rect(10, 10, SCREEN_WIDTH - 20, SCREEN_HEIGHT - 20), 1)
        pygame.draw.rect(surface, (92, 86, 76), pygame.Rect(16, 16, SCREEN_WIDTH - 32, SCREEN_HEIGHT - 32), 1)

    def _draw_single_corner(self, surface: pygame.Surface, color: tuple[int, int, int]) -> None:
        pygame.draw.lines(surface, color, False, [(0, 48), (0, 0), (70, 0)], 3)
        pygame.draw.arc(surface, color, pygame.Rect(20, 18, 68, 68), 3.15, 6.15, 2)
        pygame.draw.circle(surface, color, (34, 34), 13, 2)
        pygame.draw.circle(surface, color, (34, 34), 5, 1)
        pygame.draw.line(surface, color, (34, 48), (34, 116), 2)
        for y in (68, 88, 108):
            pygame.draw.circle(surface, color, (34, y), 7, 2)
        pygame.draw.line(surface, color, (70, 18), (150, 18), 1)
        pygame.draw.arc(surface, color, pygame.Rect(84, 0, 50, 50), 1.6, 3.1, 2)

    def _draw_title(self, surface: pygame.Surface) -> None:
        self._draw_glow_text(surface, TITLE_MAIN, self.title_font, SCREEN_WIDTH // 2, 154)
        subtitle = self.subtitle_font.render(TITLE_SUB, True, (236, 226, 205))
        surface.blit(subtitle, subtitle.get_rect(center=(SCREEN_WIDTH // 2, 224)))
        self._draw_divider(surface, 258)
        tagline = self.small_font.render(TAGLINE, True, (238, 224, 184))
        surface.blit(tagline, tagline.get_rect(center=(SCREEN_WIDTH // 2, 290)))

    def _draw_glow_text(self, surface: pygame.Surface, text: str, font: pygame.font.Font, x: int, y: int) -> None:
        for radius, alpha in ((8, 40), (5, 62), (2, 92)):
            glow = font.render(text, True, (230, 232, 226))
            glow.set_alpha(alpha)
            for ox, oy in ((-radius, 0), (radius, 0), (0, -radius), (0, radius)):
                surface.blit(glow, glow.get_rect(center=(x + ox, y + oy)))
        for ox, oy in ((-2, 0), (2, 0), (0, -2), (0, 2)):
            outline = font.render(text, True, (45, 38, 34))
            surface.blit(outline, outline.get_rect(center=(x + ox, y + oy)))
        main = font.render(text, True, (244, 244, 238))
        surface.blit(main, main.get_rect(center=(x, y)))

    def _draw_divider(self, surface: pygame.Surface, y: int) -> None:
        center_x = SCREEN_WIDTH // 2
        pygame.draw.line(surface, (186, 172, 136), (center_x - 110, y), (center_x - 28, y), 1)
        pygame.draw.line(surface, (186, 172, 136), (center_x + 28, y), (center_x + 110, y), 1)
        pygame.draw.polygon(surface, (220, 214, 194), [(center_x, y - 7), (center_x + 9, y), (center_x, y + 7), (center_x - 9, y)])

    def _draw_buttons(self, surface: pygame.Surface, mouse_pos: tuple[int, int]) -> None:
        for button in self.buttons:
            button.draw(surface, self.menu_font, button.rect.collidepoint(mouse_pos))

    def _draw_footer(self, surface: pygame.Surface) -> None:
        hint = self.small_font.render(FOOTER_HINT, True, (210, 204, 188))
        surface.blit(hint, hint.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 34)))
        maker_panel = pygame.Surface((232, 40), pygame.SRCALPHA)
        pygame.draw.rect(maker_panel, (12, 10, 12, 142), maker_panel.get_rect(), border_radius=5)
        pygame.draw.rect(maker_panel, (126, 112, 88, 180), maker_panel.get_rect(), 1, border_radius=5)
        maker = self.small_font.render(MAKER_TEXT, True, (206, 196, 176))
        maker_panel.blit(maker, (12, 11))
        surface.blit(maker_panel, (28, SCREEN_HEIGHT - 70))

    def _draw_help_panel(self, surface: pygame.Surface) -> None:
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        pygame.draw.rect(overlay, (0, 0, 0, 190), overlay.get_rect())
        surface.blit(overlay, (0, 0))
        rect = pygame.Rect((SCREEN_WIDTH - 520) // 2, (SCREEN_HEIGHT - 380) // 2, 520, 380)
        panel = pygame.Surface(rect.size, pygame.SRCALPHA)
        pygame.draw.rect(panel, (22, 16, 19, 242), panel.get_rect(), border_radius=8)
        pygame.draw.rect(panel, (221, 211, 184, 230), panel.get_rect(), 2, border_radius=8)
        pygame.draw.rect(panel, (96, 42, 34, 92), panel.get_rect().inflate(-14, -14), 1, border_radius=6)
        surface.blit(panel, rect.topleft)

        title = self.help_title_font.render("游戏说明", True, (246, 238, 216))
        surface.blit(title, title.get_rect(center=(rect.centerx, rect.y + 31)))

        x = rect.x + 30
        y = rect.y + 64
        max_width = rect.width - 60
        section_color = (238, 226, 192)
        body_color = (226, 216, 196)
        muted_color = (204, 194, 174)

        y = self._draw_help_section_title(surface, "故事背景", x, y, section_color)
        story = (
            "凉山村寨的节庆将至，祖传银饰上的纹样却逐渐黯淡。"
            "作为年轻的银纹守护者，你需要寻找纹样线索，净化混乱影纹，"
            "并在节庆前守护银饰展示台，让失光的银饰重新焕发光彩。"
        )
        for line in self._wrap_text(story, self.help_font, max_width):
            rendered = self.help_font.render(line, True, body_color)
            surface.blit(rendered, (x, y))
            y += 25

        y += 7
        y = self._draw_help_section_title(surface, "操作说明", x, y, section_color)
        controls = [
            "移动：WASD / 方向键",
            "交互：E / Enter",
            "银光净化：Space",
            "背包：B",
            "调试面板：F3",
        ]
        for control in controls:
            rendered = self.help_font.render(control, True, body_color)
            surface.blit(rendered, (x, y))
            y += 24

        hint = self.help_hint_font.render("Enter / Esc：返回", True, muted_color)
        surface.blit(hint, hint.get_rect(center=(rect.centerx, rect.bottom - 24)))

    def _draw_help_section_title(
        self,
        surface: pygame.Surface,
        text: str,
        x: int,
        y: int,
        color: tuple[int, int, int],
    ) -> int:
        rendered = self.help_section_font.render(text, True, color)
        surface.blit(rendered, (x, y))
        pygame.draw.line(surface, (160, 132, 96), (x, y + 25), (x + 94, y + 25), 1)
        return y + 31

    def _wrap_text(self, text: str, font: pygame.font.Font, max_width: int) -> list[str]:
        lines: list[str] = []
        current = ""
        for char in text:
            candidate = current + char
            if current and font.size(candidate)[0] > max_width:
                lines.append(current)
                current = char
            else:
                current = candidate
        if current:
            lines.append(current)
        return lines
