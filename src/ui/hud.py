import pygame


class HUD:
    """Minimal HUD placeholder for current scene and interaction prompts."""

    def __init__(self, font: pygame.font.Font) -> None:
        self.font = font

    def draw_label(self, surface: pygame.Surface, text: str, pos: tuple[int, int]) -> None:
        label = self.font.render(text, True, (245, 245, 225))
        surface.blit(label, pos)
