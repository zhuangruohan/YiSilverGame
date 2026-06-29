import pygame


class Entity:
    """Base world-space entity with a rectangle and debug drawing."""

    def __init__(self, entity_id: str, rect: pygame.Rect, color: tuple[int, int, int]) -> None:
        self.id = entity_id
        self.rect = rect
        self.color = color

    def draw(self, surface: pygame.Surface, camera) -> None:
        pygame.draw.rect(surface, self.color, camera.apply_rect(self.rect))
