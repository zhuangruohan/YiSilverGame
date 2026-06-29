from __future__ import annotations

import math
import random
from dataclasses import dataclass

import pygame

from src.entities.shadow_spirit import ShadowSpirit
from src.ui.fonts import load_chinese_font


@dataclass
class _Particle:
    pos: pygame.math.Vector2
    velocity: pygame.math.Vector2
    color: tuple[int, int, int]
    radius: float
    born_at: int
    duration_ms: int


@dataclass
class _FloatingText:
    text: str
    pos: pygame.math.Vector2
    color: tuple[int, int, int]
    born_at: int
    duration_ms: int


@dataclass
class _ImpactRing:
    pos: pygame.math.Vector2
    color: tuple[int, int, int]
    born_at: int
    duration_ms: int
    start_radius: int
    end_radius: int
    line_width: int


class CombatEffectManager:
    """Draw-only combat feedback for the shadow challenge."""

    def __init__(self, font: pygame.font.Font) -> None:
        self.font = load_chinese_font(17, font)
        self.particles: list[_Particle] = []
        self.floating_texts: list[_FloatingText] = []
        self.impact_rings: list[_ImpactRing] = []
        self.shake_until = 0
        self.shake_magnitude = 0

    def spawn_hit_spark(self, pos: tuple[int, int]) -> None:
        now = pygame.time.get_ticks()
        colors = ((245, 248, 255), (210, 190, 255), (180, 150, 240))
        for index in range(14):
            angle = (math.tau / 14) * index + random.uniform(-0.18, 0.18)
            speed = random.uniform(95, 175)
            velocity = pygame.math.Vector2(math.cos(angle), math.sin(angle)) * speed
            self.particles.append(
                _Particle(
                    pygame.math.Vector2(pos),
                    velocity,
                    random.choice(colors),
                    random.uniform(2.0, 3.8),
                    now,
                    random.randint(350, 500),
                )
            )
        self.spawn_impact_ring(pos, start_radius=12, end_radius=54, duration_ms=190)
        print(f"[COMBAT_EFFECT] hit_spark pos=({pos[0]},{pos[1]})")

    def spawn_impact_ring(
        self,
        pos: tuple[int, int],
        color: tuple[int, int, int] = (232, 228, 255),
        start_radius: int = 10,
        end_radius: int = 48,
        duration_ms: int = 180,
        line_width: int = 3,
    ) -> None:
        self.impact_rings.append(
            _ImpactRing(
                pygame.math.Vector2(pos),
                color,
                pygame.time.get_ticks(),
                duration_ms,
                start_radius,
                end_radius,
                line_width,
            )
        )

    def spawn_defeat_burst(self, pos: tuple[int, int]) -> None:
        now = pygame.time.get_ticks()
        colors = ((250, 250, 255), (225, 210, 255), (178, 142, 236))
        for _ in range(28):
            angle = random.uniform(0, math.tau)
            speed = random.uniform(70, 210)
            velocity = pygame.math.Vector2(math.cos(angle), math.sin(angle)) * speed
            self.particles.append(
                _Particle(
                    pygame.math.Vector2(pos),
                    velocity,
                    random.choice(colors),
                    random.uniform(2.0, 4.6),
                    now,
                    random.randint(520, 760),
                )
            )
        self.spawn_impact_ring(pos, (245, 240, 255), 16, 78, 260, 4)
        self.spawn_impact_ring(pos, (198, 168, 255), 8, 46, 190, 2)
        print(f"[COMBAT_EFFECT] defeat_burst pos=({pos[0]},{pos[1]})")

    def spawn_floating_text(
        self,
        text: str,
        pos: tuple[int, int],
        color: tuple[int, int, int] = (245, 245, 235),
    ) -> None:
        self.floating_texts.append(
            _FloatingText(text, pygame.math.Vector2(pos), color, pygame.time.get_ticks(), 800)
        )

    def shake(self, duration_ms: int, magnitude: int) -> None:
        self.shake_until = max(self.shake_until, pygame.time.get_ticks() + duration_ms)
        self.shake_magnitude = max(self.shake_magnitude, magnitude)

    def get_shake_offset(self) -> tuple[int, int]:
        if pygame.time.get_ticks() >= self.shake_until:
            self.shake_magnitude = 0
            return 0, 0
        magnitude = self.shake_magnitude
        return random.randint(-magnitude, magnitude), random.randint(-magnitude, magnitude)

    def update(self) -> None:
        now = pygame.time.get_ticks()
        self.particles = [
            item for item in self.particles if now - item.born_at < item.duration_ms
        ]
        self.floating_texts = [
            item for item in self.floating_texts if now - item.born_at < item.duration_ms
        ]
        self.impact_rings = [
            item for item in self.impact_rings if now - item.born_at < item.duration_ms
        ]

    def draw(self, surface: pygame.Surface, camera, shadows: list[ShadowSpirit]) -> None:
        now = pygame.time.get_ticks()
        self._draw_impact_rings(surface, camera, now)
        self._draw_particles(surface, camera, now)
        self._draw_shadow_hp_bars(surface, camera, shadows)
        self._draw_floating_texts(surface, camera, now)

    def _draw_impact_rings(self, surface: pygame.Surface, camera, now: int) -> None:
        for ring in self.impact_rings:
            elapsed = now - ring.born_at
            progress = max(0.0, min(1.0, elapsed / ring.duration_ms))
            eased = 1.0 - (1.0 - progress) * (1.0 - progress)
            radius = int(ring.start_radius + (ring.end_radius - ring.start_radius) * eased)
            alpha = int(210 * (1.0 - progress))
            screen_pos = camera.world_to_screen(int(ring.pos.x), int(ring.pos.y))
            layer = pygame.Surface((radius * 2 + 8, radius * 2 + 8), pygame.SRCALPHA)
            pygame.draw.circle(
                layer,
                (*ring.color, alpha),
                (radius + 4, radius + 4),
                radius,
                max(1, int(ring.line_width * (1.0 - progress * 0.35))),
            )
            surface.blit(layer, (screen_pos[0] - radius - 4, screen_pos[1] - radius - 4))

    def _draw_particles(self, surface: pygame.Surface, camera, now: int) -> None:
        for particle in self.particles:
            elapsed = now - particle.born_at
            progress = max(0.0, min(1.0, elapsed / particle.duration_ms))
            world_pos = particle.pos + particle.velocity * (elapsed / 1000.0)
            screen_pos = camera.world_to_screen(int(world_pos.x), int(world_pos.y))
            alpha = int(220 * (1.0 - progress))
            radius = max(1, int(particle.radius * (1.0 - progress * 0.45)))
            layer = pygame.Surface((radius * 2 + 2, radius * 2 + 2), pygame.SRCALPHA)
            pygame.draw.circle(layer, (*particle.color, alpha), (radius + 1, radius + 1), radius)
            surface.blit(layer, (screen_pos[0] - radius - 1, screen_pos[1] - radius - 1))

    def _draw_floating_texts(self, surface: pygame.Surface, camera, now: int) -> None:
        for item in self.floating_texts:
            elapsed = now - item.born_at
            progress = max(0.0, min(1.0, elapsed / item.duration_ms))
            eased = 1.0 - (1.0 - progress) * (1.0 - progress)
            world_pos = item.pos + pygame.math.Vector2(math.sin(progress * math.pi) * 6, -46 * eased)
            screen_pos = camera.world_to_screen(int(world_pos.x), int(world_pos.y))
            alpha = int(255 * (1.0 - progress * progress))
            shadow_surface = self.font.render(item.text, True, (28, 20, 34))
            shadow_surface.set_alpha(min(160, alpha))
            text_surface = self.font.render(item.text, True, item.color)
            text_surface.set_alpha(alpha)
            rect = text_surface.get_rect(center=screen_pos)
            surface.blit(shadow_surface, rect.move(2, 2))
            surface.blit(text_surface, rect)

    def _draw_shadow_hp_bars(self, surface: pygame.Surface, camera, shadows: list[ShadowSpirit]) -> None:
        for shadow in shadows:
            if shadow.state == ShadowSpirit.DEFEATED:
                continue
            screen_x, screen_y = camera.world_to_screen(shadow.rect.centerx, shadow.rect.top - 10)
            width = 56
            height = 6
            hp_ratio = 0 if shadow.max_hp <= 0 else max(0, min(1, shadow.hp / shadow.max_hp))
            bg_rect = pygame.Rect(screen_x - width // 2, screen_y, width, height)
            fg_rect = pygame.Rect(bg_rect.x, bg_rect.y, int(width * hp_ratio), height)
            pygame.draw.rect(surface, (40, 24, 44), bg_rect, border_radius=3)
            pygame.draw.rect(surface, (196, 160, 255), fg_rect, border_radius=3)
            pygame.draw.rect(surface, (245, 238, 255), bg_rect, 1, border_radius=3)
