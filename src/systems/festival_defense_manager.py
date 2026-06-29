from __future__ import annotations

import math
import random
from pathlib import Path
from dataclasses import dataclass

import pygame

from src.ui.fonts import load_chinese_font


TEXT_STAND = "\u94f6\u9970\u5c55\u793a\u53f0"
TEXT_PURIFY = "\u51c0\u5316 +1"
TEXT_STAND_HIT = "\u94f6\u9970\u5149\u8292\u53d7\u5230\u6270\u52a8\uff01"
TEXT_FAILED = "\u94f6\u9970\u5149\u8292\u6682\u65f6\u6697\u6de1\n\u8bf7\u91cd\u65b0\u5b88\u62a4"
TEXT_VICTORY = "\u8282\u5e86\u5c55\u793a\u5b8c\u6210\n\u94f6\u9970\u91cd\u65b0\u6062\u590d\u5149\u8292"
SHADOW_SPRITES = (
    "assets/sprites/npc/shadow_spirit_idle_front_01.png",
    "assets/sprites/npc/shadow_spirit_idle_front_02.png",
    "assets/sprites/npc/shadow_spirit_flee_left_01.png",
    "assets/sprites/npc/shadow_spirit_flee_left_02.png",
    "assets/sprites/npc/shadow_spirit_flee_right_01.png",
    "assets/sprites/npc/shadow_spirit_flee_right_02.png",
)


@dataclass
class FestivalShadow:
    rect: pygame.Rect
    pos: pygame.math.Vector2
    velocity: pygame.math.Vector2


class FestivalDefenseManager:
    """Small festival defense encounter driven by the main quest stage."""

    SCENE_IDS = {"festival", "festival_square", "festival_plaza"}
    MAX_STAND_LIGHT = 5
    TARGET_PURIFIED = 5
    DURATION_MS = 30000
    PURIFY_RADIUS = 120
    PURIFY_COOLDOWN_MS = 600

    def __init__(
        self,
        font: pygame.font.Font,
        status_callback=None,
        hit_effect_callback=None,
        floating_text_callback=None,
        shake_callback=None,
        sfx_callback=None,
    ) -> None:
        self.font = load_chinese_font(17, font)
        self.small_font = load_chinese_font(15, font)
        self.status_callback = status_callback
        self.hit_effect_callback = hit_effect_callback
        self.floating_text_callback = floating_text_callback
        self.shake_callback = shake_callback
        self.sfx_callback = sfx_callback
        self.active = False
        self.stand_rect = pygame.Rect(0, 0, 82, 54)
        self.shadows: list[FestivalShadow] = []
        self.stand_light = self.MAX_STAND_LIGHT
        self.purified_count = 0
        self.started_at = 0
        self.next_purify_at = 0
        self.purify_effect_center: tuple[int, int] | None = None
        self.purify_effect_until = 0
        self.result_message_until = 0
        self.result_mode = ""
        self.shadow_frames: list[pygame.Surface] = []
        self._shadow_sprite_logged = False
        self.stand_flash_until = 0
        self.success_effect_started_at = 0
        self.success_effect_until = 0

    def configure(self, scene_id: str, tile_map, player, quest_manager) -> None:
        self.active = scene_id in self.SCENE_IDS and quest_manager.stage == "festival_defense"
        self.result_mode = ""
        self.result_message_until = 0
        if not self.active:
            self.shadows = []
            return
        print("[FESTIVAL] defense manager active=True")
        self._load_shadow_frames()

        center_x = min(max(player.rect.centerx + 170, 80), max(80, tile_map.drawable_width - 80))
        center_y = min(max(player.rect.centery + 70, 80), max(80, tile_map.drawable_height - 80))
        self.stand_rect.center = (center_x, center_y)
        self.stand_light = self.MAX_STAND_LIGHT
        self.purified_count = 0
        self.started_at = pygame.time.get_ticks()
        self.next_purify_at = 0
        self.stand_flash_until = 0
        self.success_effect_started_at = 0
        self.success_effect_until = 0
        self._spawn_wave()
        print(f"[FESTIVAL] altar spawned pos={self.stand_rect.center}")
        print(f"[FESTIVAL] defense start stand={self.stand_rect.center}")

    def update(self, dt: float, player, quest_manager) -> None:
        if not self.active:
            return
        if quest_manager.stage != "festival_defense":
            self.active = False
            self.shadows = []
            return

        speed_dt = max(dt, 0.016)
        for shadow in list(self.shadows):
            direction = pygame.math.Vector2(self.stand_rect.center) - shadow.pos
            if direction.length_squared() > 0:
                shadow.velocity = direction.normalize() * 62
                shadow.pos += shadow.velocity * speed_dt
                shadow.rect.center = (int(shadow.pos.x), int(shadow.pos.y))
            if shadow.rect.colliderect(self.stand_rect):
                self._damage_stand(shadow, quest_manager)

        while len(self.shadows) < 3:
            self._spawn_shadow()

        elapsed = pygame.time.get_ticks() - self.started_at
        if self.purified_count >= self.TARGET_PURIFIED or elapsed >= self.DURATION_MS:
            self._complete(quest_manager)

    def purify(self, player, quest_manager) -> bool:
        if not self.active:
            return False
        now = pygame.time.get_ticks()
        if now < self.next_purify_at:
            return True
        self.next_purify_at = now + self.PURIFY_COOLDOWN_MS
        center = player.rect.center
        self.purify_effect_center = center
        self.purify_effect_until = now + 260
        self._play_sfx("purify")

        target = self._nearest_shadow(center)
        if target is None:
            if self.status_callback is not None:
                self.status_callback("Space\uff1a\u672a\u547d\u4e2d\u5f71\u7eb9")
            return True

        self.shadows.remove(target)
        self.purified_count += 1
        self._play_sfx("hit_shadow")
        if self.hit_effect_callback is not None:
            self.hit_effect_callback(target.rect.center)
        if self.floating_text_callback is not None:
            self.floating_text_callback(TEXT_PURIFY, target.rect.midtop, (235, 225, 255))
        if self.shake_callback is not None:
            self.shake_callback(120, 4)
        print(f"[FESTIVAL] purify hit count={self.purified_count}")
        if self.purified_count >= self.TARGET_PURIFIED:
            self._complete(quest_manager)
        return True

    def draw_ground(self, surface: pygame.Surface, camera) -> None:
        if not self.active and pygame.time.get_ticks() >= self.result_message_until:
            return
        stand_screen = camera.apply_rect(self.stand_rect)
        now = pygame.time.get_ticks()
        pulse = 1.0 + math.sin(now / 260.0) * 0.08
        light_ratio = max(0.2, self.stand_light / max(1, self.MAX_STAND_LIGHT))
        center = stand_screen.center

        outer_w = int(150 * pulse)
        outer_h = int(82 * pulse)
        glow = pygame.Surface((outer_w + 36, outer_h + 36), pygame.SRCALPHA)
        glow_rect = glow.get_rect()
        alpha = int(70 + 70 * light_ratio)
        pygame.draw.ellipse(glow, (224, 226, 255, alpha // 2), glow_rect)
        pygame.draw.ellipse(glow, (244, 238, 210, alpha), glow_rect.inflate(-18, -20), 2)
        pygame.draw.ellipse(glow, (180, 154, 98, 105), glow_rect.inflate(-42, -38), 1)
        surface.blit(glow, (center[0] - glow_rect.width // 2, center[1] - glow_rect.height // 2 + 10))

        core_rect = pygame.Rect(0, 0, 58, 26)
        core_rect.center = (center[0], center[1] + 7)
        core = pygame.Surface((core_rect.width + 22, core_rect.height + 18), pygame.SRCALPHA)
        pygame.draw.ellipse(core, (255, 250, 220, int(118 * light_ratio)), core.get_rect())
        pygame.draw.ellipse(core, (235, 235, 246, 220), pygame.Rect(11, 9, core_rect.width, core_rect.height))
        pygame.draw.ellipse(core, (255, 248, 214, 230), pygame.Rect(11, 9, core_rect.width, core_rect.height), 1)
        surface.blit(core, (core_rect.x - 11, core_rect.y - 9))

        for index in range(6):
            angle = now / 520.0 + index * math.tau / 6
            sparkle_x = center[0] + int(math.cos(angle) * 46)
            sparkle_y = center[1] + 10 + int(math.sin(angle) * 19)
            sparkle_alpha = int(92 + math.sin(now / 180.0 + index) * 50)
            pygame.draw.circle(surface, (246, 242, 220, max(40, sparkle_alpha)), (sparkle_x, sparkle_y), 2)

        label = self.small_font.render(TEXT_STAND, True, (255, 248, 220))
        surface.blit(label, (center[0] - label.get_width() // 2, center[1] - 48))

        if self.purify_effect_center is not None and now < self.purify_effect_until:
            progress = 1.0 - (self.purify_effect_until - now) / 260
            radius = int(34 + self.PURIFY_RADIUS * progress)
            alpha = int(145 * (1.0 - progress))
            layer = pygame.Surface((radius * 2 + 4, radius * 2 + 4), pygame.SRCALPHA)
            pygame.draw.circle(layer, (226, 220, 255, alpha), (radius + 2, radius + 2), radius, 3)
            screen_center = camera.world_to_screen(*self.purify_effect_center)
            surface.blit(layer, (screen_center[0] - radius - 2, screen_center[1] - radius - 2))

        if now < self.stand_flash_until:
            progress = 1.0 - (self.stand_flash_until - now) / 360
            flash_w = int(176 + progress * 28)
            flash_h = int(94 + progress * 16)
            flash = pygame.Surface((flash_w + 12, flash_h + 12), pygame.SRCALPHA)
            flash_alpha = int(150 * (1.0 - progress))
            pygame.draw.ellipse(
                flash,
                (255, 118, 160, flash_alpha),
                pygame.Rect(6, 6, flash_w, flash_h),
                3,
            )
            surface.blit(flash, (center[0] - flash.get_width() // 2, center[1] - flash.get_height() // 2 + 10))

        if now < self.success_effect_until:
            duration = max(1, self.success_effect_until - self.success_effect_started_at)
            progress = max(0.0, min(1.0, (now - self.success_effect_started_at) / duration))
            radius = int(34 + 160 * progress)
            alpha = int(190 * (1.0 - progress))
            burst = pygame.Surface((radius * 2 + 10, radius * 2 + 10), pygame.SRCALPHA)
            pygame.draw.circle(burst, (255, 252, 222, alpha), (radius + 5, radius + 5), radius, 4)
            pygame.draw.circle(burst, (215, 210, 255, max(35, alpha // 3)), (radius + 5, radius + 5), max(8, radius - 20), 2)
            surface.blit(burst, (center[0] - radius - 5, center[1] - radius - 5))

    def draw_entities(self, surface: pygame.Surface, camera) -> None:
        if not self.active:
            return
        now = pygame.time.get_ticks()
        for shadow in self.shadows:
            screen_rect = camera.apply_rect(shadow.rect)
            if self.shadow_frames:
                frame_index = (now // 220) % len(self.shadow_frames)
                image = self.shadow_frames[frame_index]
                image_rect = image.get_rect(center=screen_rect.center)
                surface.blit(image, image_rect)
                continue
            layer = pygame.Surface((screen_rect.width + 14, screen_rect.height + 14), pygame.SRCALPHA)
            pulse = int(55 + math.sin(now / 120.0) * 18)
            pygame.draw.ellipse(layer, (118, 48, 158, pulse), layer.get_rect())
            pygame.draw.ellipse(layer, (75, 35, 115), pygame.Rect(7, 7, screen_rect.width, screen_rect.height))
            pygame.draw.ellipse(layer, (210, 176, 255), pygame.Rect(7, 7, screen_rect.width, screen_rect.height), 2)
            surface.blit(layer, (screen_rect.x - 7, screen_rect.y - 7))

    def draw_hud(self, surface: pygame.Surface) -> None:
        if not self.active and pygame.time.get_ticks() >= self.result_message_until:
            return
        if self.result_mode and pygame.time.get_ticks() < self.result_message_until:
            lines = TEXT_VICTORY.splitlines() if self.result_mode == "victory" else TEXT_FAILED.splitlines()
        elif self.active:
            remaining = max(0, (self.DURATION_MS - (pygame.time.get_ticks() - self.started_at)) // 1000)
            lines = [
                "\u5b88\u62a4\u94f6\u9970\u5c55\u793a\u53f0",
                f"\u94f6\u9970\u5149\u8292\uff1a{self.stand_light}/{self.MAX_STAND_LIGHT}",
                f"\u5df2\u51c0\u5316\u5f71\u7eb9\uff1a{self.purified_count}/{self.TARGET_PURIFIED}",
                f"\u5269\u4f59\u65f6\u95f4\uff1a{remaining}s",
                "Space\uff1a\u94f6\u5149\u51c0\u5316",
            ]
        else:
            return

        rendered = [self.font.render(line, True, (244, 238, 220)) for line in lines]
        width = max(item.get_width() for item in rendered) + 22
        height = len(rendered) * 21 + 16
        rect = pygame.Rect(surface.get_width() - width - 12, 118, width, height)
        panel = pygame.Surface(rect.size, pygame.SRCALPHA)
        pygame.draw.rect(panel, (22, 18, 26, 162), panel.get_rect(), border_radius=6)
        pygame.draw.rect(panel, (190, 164, 96, 210), panel.get_rect(), 1, border_radius=6)
        surface.blit(panel, rect.topleft)
        y = rect.y + 8
        for item in rendered:
            surface.blit(item, (rect.x + 11, y))
            y += 21

    def _nearest_shadow(self, center: tuple[int, int]) -> FestivalShadow | None:
        origin = pygame.math.Vector2(center)
        best_shadow = None
        best_distance = self.PURIFY_RADIUS
        for shadow in self.shadows:
            distance = origin.distance_to(shadow.rect.center)
            if distance <= best_distance:
                best_distance = distance
                best_shadow = shadow
        return best_shadow

    def _spawn_wave(self) -> None:
        self.shadows = []
        for _ in range(3):
            self._spawn_shadow()
        print(f"[FESTIVAL] shadow spawned count={len(self.shadows)}")

    def _spawn_shadow(self) -> None:
        angle = random.choice((0.0, math.pi * 0.6, math.pi, math.pi * 1.35, math.pi * 1.75))
        distance = random.randint(190, 260)
        center = pygame.math.Vector2(self.stand_rect.center) + pygame.math.Vector2(
            math.cos(angle) * distance,
            math.sin(angle) * distance,
        )
        rect = pygame.Rect(0, 0, 48, 48)
        rect.center = (int(center.x), int(center.y))
        self.shadows.append(FestivalShadow(rect, pygame.math.Vector2(rect.center), pygame.math.Vector2()))

    def _load_shadow_frames(self) -> None:
        if self.shadow_frames:
            return

        for sprite_path in SHADOW_SPRITES:
            path = Path(sprite_path)
            if not path.exists():
                continue
            try:
                image = pygame.image.load(str(path)).convert_alpha()
                self.shadow_frames.append(pygame.transform.smoothscale(image, (48, 48)))
                if not self._shadow_sprite_logged:
                    print(f"[FESTIVAL_SHADOW] use sprite={path.name}")
                    self._shadow_sprite_logged = True
            except pygame.error as exc:
                print(f"[FESTIVAL_SHADOW][WARN] failed load sprite={sprite_path} error={exc}")

        if not self.shadow_frames:
            print("[FESTIVAL_SHADOW][WARN] shadow_spirit sprites unavailable; using purple placeholder")

    def _damage_stand(self, shadow: FestivalShadow, quest_manager) -> None:
        if shadow in self.shadows:
            self.shadows.remove(shadow)
        self.stand_light = max(0, self.stand_light - 1)
        self._play_sfx("player_hit")
        if self.status_callback is not None:
            self.status_callback(TEXT_STAND_HIT)
        self.stand_flash_until = pygame.time.get_ticks() + 360
        if self.floating_text_callback is not None:
            self.floating_text_callback("\u5149\u8292\u53d7\u6270", self.stand_rect.midtop, (255, 205, 210))
        if self.shake_callback is not None:
            self.shake_callback(150, 4)
        print(f"[FESTIVAL] altar_light={self.stand_light}")
        if self.stand_light <= 0:
            self._fail(quest_manager)

    def _complete(self, quest_manager) -> None:
        if not self.active:
            return
        quest_manager.complete_level("festival_defense")
        if quest_manager.stage == "festival_defense":
            quest_manager.advance_to("ending")
        self.active = False
        self.shadows = []
        self.result_mode = "victory"
        self.result_message_until = pygame.time.get_ticks() + 3000
        self._play_sfx("festival_success")
        self.success_effect_started_at = pygame.time.get_ticks()
        self.success_effect_until = self.success_effect_started_at + 900
        if self.shake_callback is not None:
            self.shake_callback(180, 3)
        if self.status_callback is not None:
            self.status_callback(TEXT_VICTORY.replace("\n", " / "))
        print("[FESTIVAL] defense complete -> ending")

    def _fail(self, quest_manager) -> None:
        print("[FESTIVAL] defense failed reset")
        self._play_sfx("fail")
        self.stand_light = self.MAX_STAND_LIGHT
        self.purified_count = 0
        self.started_at = pygame.time.get_ticks()
        self.result_mode = "failed"
        self.result_message_until = pygame.time.get_ticks() + 2200
        if self.status_callback is not None:
            self.status_callback(TEXT_FAILED.replace("\n", " / "))
        self._spawn_wave()

    def _play_sfx(self, name: str) -> None:
        if self.sfx_callback is not None:
            self.sfx_callback(name)
