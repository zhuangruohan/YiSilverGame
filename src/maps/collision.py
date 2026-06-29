import pygame


class CollisionMap:
    """Utility wrapper around world-space collision rectangles."""

    def __init__(self, rects: list[pygame.Rect] | None = None) -> None:
        self.rects = rects or []

    def blocks(self, rect: pygame.Rect) -> bool:
        return rect.collidelist(self.rects) != -1
