from __future__ import annotations

from collections.abc import Callable

import pygame

from src.entities.player import Player
from src.entities.shadow_spirit import ShadowSpirit


STATUS_CHASE = "\u5f71\u7eb9\u8ffd\u9010\u4e2d\uff0c\u6309 Space \u91ca\u653e\u94f6\u5149\u51c0\u5316"
STATUS_COOLDOWN = "\u94f6\u5149\u51b7\u5374\u4e2d"
STATUS_CANCEL = "\u5f71\u7eb9\u8ffd\u9010\u5df2\u53d6\u6d88"
STATUS_PLAYER_HIT = "\u88ab\u5f71\u7eb9\u6270\u52a8\uff0c\u94f6\u5149\u51cf\u5f31\uff01"
STATUS_DEFEATED = "\u5f71\u7eb9\u5df2\u51c0\u5316\uff0c\u83b7\u5f97\u5c71\u7eb9\u7ebf\u7d22"
STATUS_FAILED = "\u94f6\u5149\u6682\u65f6\u6697\u6de1\uff0c\u8bf7\u91cd\u65b0\u5c1d\u8bd5"
TEXT_PURIFY_DAMAGE = "\u51c0\u5316 -1"
TEXT_LIGHT_DAMAGE = "\u94f6\u5149 -1"


class ShadowChaseManager:
    """Runs the stable demo version of the shadow chase challenge."""

    PLAYER_MAX_LIGHT = 3
    DETECT_RADIUS = 220
    ATTACK_TRIGGER_RADIUS = 90
    PURIFY_RADIUS = 110
    PURIFY_COOLDOWN_MS = 800
    PLAYER_INVINCIBLE_MS = 1200
    RESET_DISTANCE = 640
    DEFEATED_HUD_MS = 2200
    FAILED_HUD_MS = 2200
    REWARD_ID = "mountain_pattern_clue"
    SHADOW_SCENES = {"river_valley", "mountain"}

    def __init__(
        self,
        status_callback: Callable[[str], None] | None = None,
        reset_player_callback: Callable[[], None] | None = None,
        defeated_callback: Callable[[str], None] | None = None,
        hit_effect_callback: Callable[[tuple[int, int]], None] | None = None,
        defeat_effect_callback: Callable[[tuple[int, int]], None] | None = None,
        floating_text_callback: Callable[[str, tuple[int, int], tuple[int, int, int]], None] | None = None,
        shake_callback: Callable[[int, int], None] | None = None,
        sfx_callback: Callable[[str], None] | None = None,
    ) -> None:
        self.status_callback = status_callback
        self.reset_player_callback = reset_player_callback
        self.defeated_callback = defeated_callback
        self.hit_effect_callback = hit_effect_callback
        self.defeat_effect_callback = defeat_effect_callback
        self.floating_text_callback = floating_text_callback
        self.shake_callback = shake_callback
        self.sfx_callback = sfx_callback
        self.shadows: list[ShadowSpirit] = []
        self.player_light = self.PLAYER_MAX_LIGHT
        self.last_hit_at = -self.PLAYER_INVINCIBLE_MS
        self.player_invincible_until = 0
        self.last_purify_at = -self.PURIFY_COOLDOWN_MS
        self.purify_effect_started_at = 0
        self.purify_effect_until = 0
        self.purify_effect_center: tuple[int, int] | None = None
        self.active = False
        self.scene_name = ""
        self.hud_mode = "hidden"
        self.defeated_hud_until = 0
        self.failed_hud_until = 0

    def configure(self, scene_name: str, shadows: list[ShadowSpirit]) -> None:
        self.scene_name = scene_name
        self.shadows = shadows
        self.player_light = self.PLAYER_MAX_LIGHT
        self.last_hit_at = -self.PLAYER_INVINCIBLE_MS
        self.player_invincible_until = 0
        self.last_purify_at = -self.PURIFY_COOLDOWN_MS
        self.purify_effect_started_at = 0
        self.purify_effect_until = 0
        self.purify_effect_center = None
        self.active = any(shadow.state == ShadowSpirit.CHASE for shadow in shadows)
        self.defeated_hud_until = 0
        self.failed_hud_until = 0
        self._update_hud_mode(pygame.time.get_ticks())

    def update(
        self,
        dt: float,
        player: Player,
        collision_rects: list[pygame.Rect],
    ) -> None:
        now = pygame.time.get_ticks()
        self.active = False
        player_speed = float(getattr(player, "speed", 4.0))

        for shadow in self.shadows:
            if shadow.state == ShadowSpirit.DEFEATED:
                continue

            distance = pygame.math.Vector2(player.rect.center).distance_to(shadow.rect.center)
            if shadow.state == ShadowSpirit.IDLE and distance <= self.DETECT_RADIUS:
                shadow.start_chase()
                self._set_status(STATUS_CHASE)

            if shadow.state == ShadowSpirit.CHASE and distance <= self.ATTACK_TRIGGER_RADIUS:
                shadow.begin_attack(player.rect.center)

            if shadow.state == ShadowSpirit.CHASE and distance > self.RESET_DISTANCE:
                shadow.reset_chase()

            shadow.update(dt, player, collision_rects, player_speed)
            if shadow.state in {
                ShadowSpirit.CHASE,
                ShadowSpirit.HIT,
                ShadowSpirit.ATTACK_WINDUP,
                ShadowSpirit.DASH_ATTACK,
                ShadowSpirit.RECOVER,
            }:
                self.active = True
            if (
                shadow.state == ShadowSpirit.DASH_ATTACK
                and not shadow.attack_has_hit
                and shadow.rect.colliderect(player.rect)
            ):
                shadow.mark_attack_hit()
                self._hit_player(now, player, shadow.rect.center, collision_rects)

        self._update_hud_mode(now)

    def purify(self, player: Player, collision_rects: list[pygame.Rect] | None = None) -> bool:
        if not self.shadows or self.scene_name not in self.SHADOW_SCENES:
            return False

        now = pygame.time.get_ticks()
        if now - self.last_purify_at < self.PURIFY_COOLDOWN_MS:
            print("[SHADOW] purify miss")
            self._set_status(STATUS_COOLDOWN)
            return True

        self.last_purify_at = now
        self.purify_effect_started_at = now
        self.purify_effect_until = now + 280
        self.purify_effect_center = player.rect.center
        self._play_sfx("purify")
        print(f"[PURIFY_EFFECT] start pos=({player.rect.centerx},{player.rect.centery})")

        target = self._nearest_purifiable_shadow(player)
        if target is None:
            print("[SHADOW] purify miss")
            return True

        target.take_purify_hit(player.rect.center, collision_rects or [])
        self._play_sfx("hit_shadow")
        print(f"[SHADOW] purify hit shadow_hp={target.hp}")
        if self.hit_effect_callback is not None:
            self.hit_effect_callback(target.rect.center)
        if self.floating_text_callback is not None:
            self.floating_text_callback(TEXT_PURIFY_DAMAGE, (target.rect.centerx, target.rect.top - 18), (235, 230, 255))
        if self.shake_callback is not None:
            self.shake_callback(120, 4)
        if target.hp <= 0:
            self._defeat_shadow(target)
        self._update_hud_mode(now)
        return True

    def cancel_chase(self) -> bool:
        active_shadow = False
        for shadow in self.shadows:
            if shadow.state in {
                ShadowSpirit.CHASE,
                ShadowSpirit.HIT,
                ShadowSpirit.ATTACK_WINDUP,
                ShadowSpirit.DASH_ATTACK,
                ShadowSpirit.RECOVER,
            }:
                shadow.reset_chase()
                active_shadow = True
        if active_shadow:
            self.active = False
            self._set_status(STATUS_CANCEL)
            self._update_hud_mode(pygame.time.get_ticks())
        return active_shadow

    def is_purify_ready(self) -> bool:
        return pygame.time.get_ticks() - self.last_purify_at >= self.PURIFY_COOLDOWN_MS

    def strongest_shadow(self) -> ShadowSpirit | None:
        available = [shadow for shadow in self.shadows if shadow.state != ShadowSpirit.DEFEATED]
        if not available:
            return None
        return min(available, key=lambda shadow: shadow.hp)

    def should_show_hud(self) -> bool:
        return self.hud_mode != "hidden"

    def is_player_invincible(self) -> bool:
        return pygame.time.get_ticks() < self.player_invincible_until

    def _update_hud_mode(self, now: int) -> None:
        if not self.shadows or self.scene_name not in self.SHADOW_SCENES:
            self.hud_mode = "hidden"
            return

        if now < self.failed_hud_until:
            self.hud_mode = "failed"
            return

        if now < self.defeated_hud_until:
            self.hud_mode = "defeated"
            return

        if any(
            shadow.state
            in {
                ShadowSpirit.CHASE,
                ShadowSpirit.HIT,
                ShadowSpirit.ATTACK_WINDUP,
                ShadowSpirit.DASH_ATTACK,
                ShadowSpirit.RECOVER,
            }
            for shadow in self.shadows
        ):
            self.hud_mode = "active"
            return

        if any(shadow.state != ShadowSpirit.DEFEATED for shadow in self.shadows):
            self.hud_mode = "ready"
            return

        self.hud_mode = "hidden"

    def _nearest_purifiable_shadow(self, player: Player) -> ShadowSpirit | None:
        player_center = pygame.math.Vector2(player.rect.center)
        candidates: list[tuple[float, ShadowSpirit]] = []
        for shadow in self.shadows:
            if shadow.state not in {
                ShadowSpirit.CHASE,
                ShadowSpirit.HIT,
                ShadowSpirit.ATTACK_WINDUP,
                ShadowSpirit.DASH_ATTACK,
                ShadowSpirit.RECOVER,
            }:
                continue
            distance = player_center.distance_to(shadow.rect.center)
            if distance <= self.PURIFY_RADIUS:
                candidates.append((distance, shadow))
        if not candidates:
            return None
        candidates.sort(key=lambda item: item[0])
        return candidates[0][1]

    def _hit_player(
        self,
        now: int,
        player: Player,
        source_center: tuple[int, int],
        collision_rects: list[pygame.Rect],
    ) -> None:
        if now - self.last_hit_at < self.PLAYER_INVINCIBLE_MS:
            return
        self.last_hit_at = now
        self.player_invincible_until = now + self.PLAYER_INVINCIBLE_MS
        self.player_light = max(0, self.player_light - 1)
        print(f"[SHADOW] player hit hp={self.player_light}")
        self._play_sfx("player_hit")
        self._knockback_player(player, source_center, collision_rects)
        self._set_status(STATUS_PLAYER_HIT)
        if self.floating_text_callback is not None:
            self.floating_text_callback(TEXT_LIGHT_DAMAGE, (player.rect.centerx, player.rect.top - 16), (255, 210, 220))
        if self.shake_callback is not None:
            self.shake_callback(150, 5)
        if self.player_light <= 0:
            self._fail_challenge()

    def _defeat_shadow(self, shadow: ShadowSpirit) -> None:
        defeated_pos = shadow.rect.center
        shadow.state = ShadowSpirit.DEFEATED
        shadow.has_reward_given = True
        self.defeated_hud_until = pygame.time.get_ticks() + self.DEFEATED_HUD_MS
        print(f"[SHADOW] defeated reward={self.REWARD_ID}")
        self._play_sfx("victory")
        self._set_status(STATUS_DEFEATED)
        if self.defeat_effect_callback is not None:
            self.defeat_effect_callback(defeated_pos)
        if self.defeated_callback is not None:
            self.defeated_callback(self.REWARD_ID)

    def _fail_challenge(self) -> None:
        print("[SHADOW] challenge failed reset")
        self._play_sfx("fail")
        self.active = False
        self.player_light = self.PLAYER_MAX_LIGHT
        self.failed_hud_until = pygame.time.get_ticks() + self.FAILED_HUD_MS
        self._set_status(STATUS_FAILED)
        if self.reset_player_callback is not None:
            self.reset_player_callback()

    def _set_status(self, message: str) -> None:
        if self.status_callback is not None:
            self.status_callback(message)

    def _play_sfx(self, name: str) -> None:
        if self.sfx_callback is not None:
            self.sfx_callback(name)

    def _knockback_player(
        self,
        player: Player,
        source_center: tuple[int, int],
        collision_rects: list[pygame.Rect],
    ) -> None:
        away = pygame.math.Vector2(player.rect.center) - pygame.math.Vector2(source_center)
        if away.length_squared() <= 0.01:
            away = pygame.math.Vector2(1, 0)
        away = away.normalize() * 26
        old_center = pygame.math.Vector2(player.rect.center)
        next_rect = player.rect.move(int(away.x), int(away.y))
        if next_rect.collidelist(collision_rects) == -1:
            player.rect = next_rect
            player.world_x = player.rect.x
            player.world_y = player.rect.y
        actual = pygame.math.Vector2(player.rect.center) - old_center
        print(f"[SHADOW] player knockback dx={actual.x:.1f} dy={actual.y:.1f}")
