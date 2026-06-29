from __future__ import annotations

import pygame

from src.entities.entity import Entity


OBJECT_COLORS = {
    "item": (230, 190, 70),
    "hidden_collectible": (230, 190, 70),
    "repair_table": (160, 120, 230),
    "display_table": (120, 190, 230),
    "silver_part_display": (190, 210, 220),
    "pattern_source": (235, 120, 120),
    "clue": (120, 220, 190),
    "pattern_checkpoint": (220, 160, 80),
    "task_trigger": (180, 180, 80),
    "shadow_fragment_trigger": (170, 80, 210),
}


class Interactable(Entity):
    """Basic world-space object parsed from a Tiled object layer."""

    def __init__(
        self,
        object_id: str,
        object_type: str,
        name: str,
        rect: pygame.Rect,
        properties: dict,
    ) -> None:
        super().__init__(object_id, rect, OBJECT_COLORS.get(object_type, (170, 170, 170)))
        self.type = object_type
        self.name = name
        self.properties = properties

    @classmethod
    def from_record(cls, record) -> "Interactable":
        return cls(record.id, record.type, record.name, record.rect.copy(), dict(record.properties))

    def draw(self, surface: pygame.Surface, camera, font: pygame.font.Font | None = None) -> None:
        screen_rect = camera.apply_rect(self.rect)
        pygame.draw.rect(surface, self.color, screen_rect, 2)
        if font is not None:
            label = font.render(self.type, True, self.color)
            surface.blit(label, (screen_rect.x, screen_rect.y - 14))
