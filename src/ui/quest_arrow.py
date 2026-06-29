from __future__ import annotations

import math

import pygame

from src.ui.fonts import load_chinese_font


class QuestArrow:
    """Small objective arrow that points at the current main-quest target."""

    EDGE_MARGIN = 34
    TARGET_MARGIN = 40

    def __init__(self, font: pygame.font.Font) -> None:
        self.font = load_chinese_font(15, font)
        self.color = (248, 222, 112)
        self.glow_color = (255, 246, 190, 78)
        self.edge_color = (226, 210, 255)
        self._last_target_signature: tuple[str, str, int, int] | None = None
        self._warned_missing_stages: set[str] = set()

    def draw(
        self,
        surface: pygame.Surface,
        camera,
        stage: str,
        target_id: str | None,
        world_pos: tuple[int, int] | None,
    ) -> None:
        if world_pos is None:
            if stage not in self._warned_missing_stages:
                print(f"[QUEST_ARROW][WARN] target not found stage={stage}")
                self._warned_missing_stages.add(stage)
            return

        self._log_target(stage, target_id or "target", world_pos)
        screen_x, screen_y = camera.world_to_screen(world_pos[0], world_pos[1])
        visible_rect = surface.get_rect().inflate(-self.TARGET_MARGIN * 2, -self.TARGET_MARGIN * 2)
        if visible_rect.collidepoint(screen_x, screen_y):
            self._draw_target_marker(surface, (screen_x, screen_y))
        else:
            self._draw_edge_arrow(surface, (screen_x, screen_y))

    def _log_target(self, stage: str, target_id: str, world_pos: tuple[int, int]) -> None:
        signature = (stage, target_id, int(world_pos[0]), int(world_pos[1]))
        if signature == self._last_target_signature:
            return
        self._last_target_signature = signature
        print(
            f"[QUEST_ARROW] stage={stage} target={target_id} "
            f"pos=({int(world_pos[0])},{int(world_pos[1])})"
        )

    def _draw_target_marker(self, surface: pygame.Surface, screen_pos: tuple[int, int]) -> None:
        now = pygame.time.get_ticks()
        bob = int(math.sin(now / 210.0) * 5)
        x, y = screen_pos
        tip_y = y - 42 + bob
        glow = pygame.Surface((36, 36), pygame.SRCALPHA)
        pygame.draw.circle(glow, self.glow_color, (18, 18), 17)
        surface.blit(glow, (x - 18, tip_y - 25))
        points = [(x, tip_y), (x - 11, tip_y - 18), (x + 11, tip_y - 18)]
        pygame.draw.polygon(surface, self.color, points)
        pygame.draw.polygon(surface, (92, 70, 34), points, 1)
        pygame.draw.circle(surface, (255, 246, 190), (x, y - 10 + bob), 4)

    def _draw_edge_arrow(self, surface: pygame.Surface, target_screen_pos: tuple[int, int]) -> None:
        rect = surface.get_rect()
        center = pygame.math.Vector2(rect.center)
        target = pygame.math.Vector2(target_screen_pos)
        direction = target - center
        if direction.length_squared() <= 0.01:
            direction = pygame.math.Vector2(1, 0)
        direction = direction.normalize()

        edge_x = max(self.EDGE_MARGIN, min(rect.width - self.EDGE_MARGIN, center.x + direction.x * rect.width))
        edge_y = max(self.EDGE_MARGIN + 18, min(rect.height - self.EDGE_MARGIN - 18, center.y + direction.y * rect.height))
        edge = pygame.math.Vector2(edge_x, edge_y)
        angle = math.atan2(direction.y, direction.x)
        points = self._triangle_points(edge, angle)
        pygame.draw.polygon(surface, self.edge_color, points)
        pygame.draw.polygon(surface, (78, 58, 120), points, 1)

        label = self.font.render("前往目标", True, (246, 238, 210))
        label_rect = label.get_rect(center=(int(edge.x), int(edge.y + 24)))
        label_rect.clamp_ip(rect.inflate(-12, -12))
        bg_rect = label_rect.inflate(12, 6)
        bg = pygame.Surface(bg_rect.size, pygame.SRCALPHA)
        pygame.draw.rect(bg, (18, 16, 24, 150), bg.get_rect(), border_radius=4)
        surface.blit(bg, bg_rect)
        surface.blit(label, label_rect)

    def _triangle_points(self, center: pygame.math.Vector2, angle: float) -> list[tuple[int, int]]:
        tip = center + pygame.math.Vector2(math.cos(angle), math.sin(angle)) * 15
        left = center + pygame.math.Vector2(math.cos(angle + 2.45), math.sin(angle + 2.45)) * 12
        right = center + pygame.math.Vector2(math.cos(angle - 2.45), math.sin(angle - 2.45)) * 12
        return [(int(tip.x), int(tip.y)), (int(left.x), int(left.y)), (int(right.x), int(right.y))]
