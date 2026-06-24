from pathlib import Path

import pygame

from settings import FPS, SCREEN_HEIGHT, SCREEN_WIDTH, TITLE


class Game:
    """游戏主类，负责窗口、状态和主循环。"""

    def __init__(self) -> None:
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        self.running = True
        self.state = "MENU"

        # 使用系统中文字体，缺失时回退到 pygame 默认字体。
        self.title_font = self._load_font(48)
        self.menu_font = self._load_font(28)
        self.small_font = self._load_font(24)

    def run(self) -> None:
        """主循环入口。"""
        while self.running:
            self.handle_events()
            self.update()
            self.draw()

        pygame.quit()

    def handle_events(self) -> None:
        """处理退出和状态切换输入。"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.quit()
                elif self.state == "MENU" and event.key == pygame.K_RETURN:
                    self.state = "PLAYING"

    def update(self) -> None:
        """当前阶段只控制帧率，后续阶段再加入游戏逻辑。"""
        self.clock.tick(FPS)

    def draw(self) -> None:
        """根据当前状态绘制菜单或占位游戏界面。"""
        if self.state == "MENU":
            self._draw_menu()
        elif self.state == "PLAYING":
            self._draw_playing_placeholder()

        pygame.display.flip()

    def quit(self) -> None:
        """标记退出，交由主循环统一关闭 pygame。"""
        self.running = False

    def _draw_menu(self) -> None:
        self.screen.fill((28, 25, 34))
        self._draw_center_text(TITLE, self.title_font, (230, 220, 190), SCREEN_HEIGHT // 2 - 90)
        self._draw_center_text("按 Enter 开始游戏", self.menu_font, (245, 245, 245), SCREEN_HEIGHT // 2 + 10)
        self._draw_center_text("按 Esc 退出游戏", self.small_font, (190, 190, 190), SCREEN_HEIGHT // 2 + 55)

    def _draw_playing_placeholder(self) -> None:
        self.screen.fill((38, 48, 43))
        self._draw_center_text("游戏场景占位，后续将加载 Tiled 地图", self.menu_font, (240, 240, 225), SCREEN_HEIGHT // 2)

    def _draw_center_text(
        self,
        text: str,
        font: pygame.font.Font,
        color: tuple[int, int, int],
        center_y: int,
    ) -> None:
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, center_y))
        self.screen.blit(text_surface, text_rect)

    def _load_font(self, size: int) -> pygame.font.Font:
        font_candidates = [
            Path("C:/Windows/Fonts/msyh.ttc"),
            Path("C:/Windows/Fonts/simhei.ttf"),
            Path("C:/Windows/Fonts/simsun.ttc"),
        ]

        for font_path in font_candidates:
            if font_path.exists():
                return pygame.font.Font(str(font_path), size)

        return pygame.font.Font(None, size)
