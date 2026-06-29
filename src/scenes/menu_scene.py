import pygame

from src.scenes.base_scene import BaseScene
from src.ui.menu_ui import MenuUI


class MenuScene(BaseScene):
    """Start menu scene. Game decides what Enter/Esc means globally."""

    def __init__(
        self,
        title_font: pygame.font.Font,
        menu_font: pygame.font.Font,
        small_font: pygame.font.Font,
        start_callback=None,
        quit_callback=None,
    ) -> None:
        self.ui = MenuUI(title_font, menu_font, small_font)
        self.start_callback = start_callback
        self.quit_callback = quit_callback

    def handle_event(self, event: pygame.event.Event) -> bool:
        action = self.ui.handle_event(event)
        if action is None:
            return False
        if action == "start" and self.start_callback is not None:
            self.start_callback()
            return True
        if action == "quit" and self.quit_callback is not None:
            self.quit_callback()
            return True
        return True

    def draw(self, surface: pygame.Surface) -> None:
        self.ui.draw(surface)
