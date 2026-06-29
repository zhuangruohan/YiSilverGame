from __future__ import annotations

import math
from pathlib import Path

import pygame

from src.resources.animation import (
    Animation,
    StateAnimationController,
    load_first_available_animation,
)


class ShadowSpirit:
    """Lightweight shadow opponent for silver-light purification."""

    IMAGE_HEIGHT = 72
    SPRITE_DIR = Path("assets/sprites/npc")

    IDLE = "idle"
    CHASE = "chase"
    HIT = "hit"
    ATTACK_WINDUP = "attack_windup"
    DASH_ATTACK = "dash_attack"
    RECOVER = "recover"
    DEFEATED = "defeated"

    # Backward-compatible aliases for existing scene code.
    APPEAR = CHASE
    FLEE = CHASE
    CAUGHT = HIT
    DONE = DEFEATED

    def __init__(
        self,
        shadow_id: str,
        world_x: int,
        world_y: int,
        route_points: list[tuple[int, int]] | None = None,
        carried_item_id: str = "key_silver_fragment",
        reward_item_id: str = "mountain_pattern_clue",
        speed: float = 180.0,
        interact_radius: int = 96,
        hp: int = 3,
    ) -> None:
        del route_points, carried_item_id
        self.shadow_id = shadow_id
        self.world_x = float(world_x)
        self.world_y = float(world_y)
        self.start_position = (float(world_x), float(world_y))
        self.rect = pygame.Rect(0, 0, 34, 34)
        self.rect.center = (int(self.world_x), int(self.world_y))
        self.state = self.IDLE
        self.speed = speed
        self.reward_item_id = reward_item_id
        self.interact_radius = interact_radius
        self.max_hp = max(1, int(hp))
        self.hp = self.max_hp
        self.hit_pause_ms = 0
        self.flash_until = 0
        self.state_until = 0
        self.attack_direction = pygame.math.Vector2(1, 0)
        self.attack_has_hit = False
        self.has_reward_given = False
        self._flee_direction = "right"
        self._last_draw_log_at = 0
        self.animation = self._load_animation_controller()

    def start_chase(self) -> None:
        if self.state in {
            self.CHASE,
            self.HIT,
            self.ATTACK_WINDUP,
            self.DASH_ATTACK,
            self.RECOVER,
            self.DEFEATED,
        }:
            return
        previous_state = self.state
        self.state = self.CHASE
        print(f"[SHADOW] state {previous_state} -> chase")

    def start_flee(self) -> None:
        self.start_chase()

    def update(
        self,
        dt: float,
        player=None,
        collision_rects: list[pygame.Rect] | None = None,
        player_speed: float = 4.0,
    ) -> None:
        now = pygame.time.get_ticks()
        if self.state == self.HIT:
            if now >= self.hit_pause_ms:
                self.state = self.CHASE if self.hp > 0 else self.DEFEATED
            self._update_animation(dt)
            return

        if self.state == self.ATTACK_WINDUP:
            if now >= self.state_until:
                self.state = self.DASH_ATTACK
                self.state_until = now + 250
                self.attack_has_hit = False
                print("[SHADOW] dash attack")
            self._update_animation(dt)
            return

        if self.state == self.DASH_ATTACK:
            dash_speed = 260.0
            self._move(self.attack_direction.x * dash_speed * dt, self.attack_direction.y * dash_speed * dt, collision_rects or [])
            if now >= self.state_until:
                self.state = self.RECOVER
                self.state_until = now + 350
                print("[SHADOW] attack recover")
            self._update_animation(dt)
            return

        if self.state == self.RECOVER:
            if now >= self.state_until:
                self.state = self.CHASE if self.hp > 0 else self.DEFEATED
            self._update_animation(dt)
            return

        if self.state != self.CHASE or player is None:
            self._update_animation(dt)
            return

        player_center = pygame.math.Vector2(player.rect.center)
        shadow_center = pygame.math.Vector2(self.rect.center)
        delta = player_center - shadow_center
        distance = delta.length()
        if distance <= 1:
            self._update_animation(dt)
            return

        self._flee_direction = "left" if delta.x < 0 else "right"
        speed = max(self.speed, float(player_speed) * 60.0 * 0.75)
        movement = delta.normalize() * speed * dt
        if movement.length() > distance:
            movement.scale_to_length(distance)
        self._move(movement.x, movement.y, collision_rects or [])
        self._update_animation(dt)

    def begin_attack(self, target_center: tuple[int, int]) -> bool:
        if self.state != self.CHASE:
            return False
        direction = pygame.math.Vector2(target_center) - pygame.math.Vector2(self.rect.center)
        if direction.length_squared() <= 0.01:
            direction = pygame.math.Vector2(1, 0)
        self.attack_direction = direction.normalize()
        self._flee_direction = "left" if self.attack_direction.x < 0 else "right"
        self.state = self.ATTACK_WINDUP
        self.state_until = pygame.time.get_ticks() + 250
        self.attack_has_hit = False
        print("[SHADOW] attack windup")
        return True

    def mark_attack_hit(self) -> None:
        self.attack_has_hit = True
        print("[SHADOW] attack hit player")

    def draw(self, surface: pygame.Surface, camera) -> None:
        if self.state == self.DEFEATED:
            return

        screen_rect = camera.apply_rect(self.rect)
        image = self.animation.current_frame()
        draw_rect = screen_rect
        if image is not None:
            draw_rect = image.get_rect(midbottom=screen_rect.midbottom)
            if self.state == self.ATTACK_WINDUP:
                scaled = pygame.transform.smoothscale(
                    image,
                    (int(image.get_width() * 1.08), int(image.get_height() * 1.08)),
                )
                draw_rect = scaled.get_rect(midbottom=screen_rect.midbottom)
                image = scaled
            self._log_draw(surface, draw_rect)
            surface.blit(image, draw_rect)
            if self._is_flashing():
                flash = pygame.Surface(draw_rect.size, pygame.SRCALPHA)
                flash.fill((255, 255, 255, 135))
                surface.blit(flash, draw_rect.topleft)
                pygame.draw.rect(surface, (255, 255, 255), draw_rect.inflate(4, 4), 2)
            return

        placeholder_rect = pygame.Rect(0, 0, 64, 64)
        placeholder_rect.midbottom = screen_rect.midbottom
        self._log_draw(surface, placeholder_rect)
        pulse = 35 if self.state == self.CHASE and pygame.time.get_ticks() // 180 % 2 == 0 else 0
        color = (120 + pulse, 55, 180 + pulse)
        if self.state == self.ATTACK_WINDUP:
            color = (190, 115, 245)
            placeholder_rect.inflate_ip(8, 8)
        if self.state == self.HIT:
            color = (190, 180, 235)
        if self._is_flashing():
            color = (245, 245, 255)

        ghost = pygame.Surface((placeholder_rect.width + 18, placeholder_rect.height + 18), pygame.SRCALPHA)
        pygame.draw.ellipse(ghost, (*color, 150), ghost.get_rect())
        surface.blit(ghost, (placeholder_rect.x - 9, placeholder_rect.y - 9))
        pygame.draw.ellipse(surface, color, placeholder_rect)
        pygame.draw.ellipse(surface, (235, 220, 255), placeholder_rect, 2)

    def _log_draw(self, surface: pygame.Surface, screen_rect: pygame.Rect) -> None:
        now = pygame.time.get_ticks()
        if now - self._last_draw_log_at < 700:
            return
        self._last_draw_log_at = now
        visible = surface.get_rect().colliderect(screen_rect)
        print(
            f"[SHADOW_DRAW] visible={visible} screen_pos=({screen_rect.x},{screen_rect.y}) "
            f"world_pos=({self.rect.centerx},{self.rect.centery}) state={self.state}"
        )

    def take_purify_hit(
        self,
        source_center: tuple[int, int] | None = None,
        collision_rects: list[pygame.Rect] | None = None,
    ) -> bool:
        if self.state == self.DEFEATED:
            return False

        self.hp -= 1
        now = pygame.time.get_ticks()
        self.flash_until = now + 360
        self._apply_knockback(source_center, collision_rects or [])
        if self.hp <= 0:
            self.hp = 0
            self.state = self.DEFEATED
            self.has_reward_given = True
            return True

        self.state = self.HIT
        self.hit_pause_ms = now + 360
        return True

    def can_interact(self, player) -> bool:
        if self.state not in {self.CHASE, self.HIT, self.ATTACK_WINDUP, self.DASH_ATTACK, self.RECOVER}:
            return False
        return pygame.math.Vector2(player.rect.center).distance_to(self.rect.center) <= self.interact_radius

    def interact(self, player, inventory, task_manager, score_manager) -> bool:
        del player, inventory, task_manager, score_manager
        return False

    def reset_chase(self) -> None:
        if self.has_reward_given:
            self.state = self.DEFEATED
            return
        self.world_x, self.world_y = self.start_position
        self.rect.center = (int(self.world_x), int(self.world_y))
        self.hp = self.max_hp
        self.state = self.IDLE
        self.state_until = 0
        self.attack_has_hit = False

    def _move(self, dx: float, dy: float, collision_rects: list[pygame.Rect]) -> None:
        if dx == 0 and dy == 0:
            return

        next_center_x = self.world_x + dx
        next_rect = self.rect.copy()
        next_rect.centerx = int(next_center_x)
        if next_rect.collidelist(collision_rects) == -1:
            self.world_x = next_center_x
            self.rect.centerx = int(self.world_x)

        next_center_y = self.world_y + dy
        next_rect = self.rect.copy()
        next_rect.centery = int(next_center_y)
        if next_rect.collidelist(collision_rects) == -1:
            self.world_y = next_center_y
            self.rect.centery = int(self.world_y)

    def _apply_knockback(
        self,
        source_center: tuple[int, int] | None,
        collision_rects: list[pygame.Rect],
    ) -> None:
        if source_center is None:
            print("[SHADOW] knockback dx=0 dy=0")
            return

        away = pygame.math.Vector2(self.rect.center) - pygame.math.Vector2(source_center)
        if away.length_squared() <= 0.01:
            away = pygame.math.Vector2(1, 0)
        away = away.normalize() * 42

        old_center = pygame.math.Vector2(self.rect.center)
        self._move(away.x, away.y, collision_rects)
        new_center = pygame.math.Vector2(self.rect.center)
        actual = new_center - old_center
        print(f"[SHADOW] knockback dx={actual.x:.1f} dy={actual.y:.1f}")

    def _is_flashing(self) -> bool:
        return pygame.time.get_ticks() < self.flash_until

    def _load_animation_controller(self) -> StateAnimationController:
        animations = {
            "idle_front": Animation(
                load_first_available_animation(
                    self.SPRITE_DIR,
                    ["shadow_spirit_idle_front", "shadow_spirit_idle"],
                    self.IMAGE_HEIGHT,
                    required=True,
                    placeholder_color=(120, 55, 180),
                )
            ),
            "flee_left": Animation(
                load_first_available_animation(
                    self.SPRITE_DIR,
                    ["shadow_spirit_flee_left"],
                    self.IMAGE_HEIGHT,
                )
            ),
            "flee_right": Animation(
                load_first_available_animation(
                    self.SPRITE_DIR,
                    ["shadow_spirit_flee_right"],
                    self.IMAGE_HEIGHT,
                )
            ),
        }
        return StateAnimationController(animations, default_state="idle_front")

    def _update_animation(self, dt: float) -> None:
        if self.state in {self.CHASE, self.HIT, self.ATTACK_WINDUP, self.DASH_ATTACK, self.RECOVER}:
            self.animation.set_state(f"flee_{self._flee_direction}")
        else:
            self.animation.set_state("idle_front")
        self.animation.update(dt)
