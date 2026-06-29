import pygame

from src.entities.interactable import Interactable


class Item(Interactable):
    """Minimal item entity. Inventory pickup is intentionally left to Task 06."""

    def __init__(self, item_id: str, name: str, rect: pygame.Rect, properties: dict) -> None:
        super().__init__(item_id, "item", name, rect, properties)
