import pygame


class BaseScene:
    """Common interface for all scenes controlled by SceneManager."""

    def handle_event(self, event: pygame.event.Event) -> bool:
        return False

    def update(self, dt: float) -> None:
        return None

    def draw(self, surface: pygame.Surface) -> None:
        return None
