from __future__ import annotations

import math
from pathlib import Path
from dataclasses import dataclass

import pygame

from src.ui.fonts import load_chinese_font


COLLECT_LABELS = {
    "silver_thread": "\u94f6\u4e1d\u6750\u6599",
    "flower_bird_pattern_clue": "\u82b1\u9e1f\u7eb9\u6837\u7ebf\u7d22",
    "pattern_wooden_plaque": "\u7eb9\u6837\u6728\u724c",
}
COLLECT_ACTIONS = {
    "silver_thread": "\u6536\u96c6",
    "flower_bird_pattern_clue": "\u67e5\u770b",
    "pattern_wooden_plaque": "\u67e5\u770b",
}
ITEM_SPRITES = {
    "silver_thread": "assets/sprites/items/silver_thread.png",
    "flower_bird_pattern_clue": "assets/sprites/items/flower_bird_pattern_clue.png",
    "pattern_wooden_plaque": "assets/sprites/items/pattern_wooden_plaque.png",
}
ITEM_ID_ALIASES = {
    "bird_pattern_clue": "flower_bird_pattern_clue",
    "market_pattern_board": "pattern_wooden_plaque",
}
MARKET_HIT_TEXT = "\u88ab\u5f71\u7eb9\u6270\u52a8\uff0c\u94f6\u5149\u51cf\u5f31\uff01"
MARKET_SHADOW_SPRITES = (
    "assets/sprites/npc/shadow_spirit_idle_front_01.png",
    "assets/sprites/npc/shadow_spirit_idle_front_02.png",
    "assets/sprites/npc/shadow_spirit_flee_left_01.png",
    "assets/sprites/npc/shadow_spirit_flee_left_02.png",
    "assets/sprites/npc/shadow_spirit_flee_right_01.png",
    "assets/sprites/npc/shadow_spirit_flee_right_02.png",
)


@dataclass
class MarketCollectPoint:
    item_id: str
    label: str
    action: str
    rect: pygame.Rect
    sprite_path: str
    collected: bool = False


class _PromptObject:
    def __init__(self, point: MarketCollectPoint) -> None:
        self.id = point.item_id
        self.name = f"{point.action} {point.label}"
        self.type = "collectible"


class MarketCollectManager:
    """Lightweight collectible level for village_market."""

    REQUIRED_ITEMS = ("silver_thread", "flower_bird_pattern_clue", "pattern_wooden_plaque")
    SCENE_IDS = {"village_market", "market"}
    INTERACT_DISTANCE = 58
    SHADOW_HIT_COOLDOWN_MS = 1200

    def __init__(
        self,
        font: pygame.font.Font,
        status_callback=None,
        floating_text_callback=None,
        shake_callback=None,
        sfx_callback=None,
    ) -> None:
        self.font = load_chinese_font(15, font)
        self.status_callback = status_callback
        self.floating_text_callback = floating_text_callback
        self.shake_callback = shake_callback
        self.sfx_callback = sfx_callback
        self.active = False
        self.points: list[MarketCollectPoint] = []
        self.nearby_point: MarketCollectPoint | None = None
        self.shadow_rect = pygame.Rect(0, 0, 28, 28)
        self.shadow_frames: list[pygame.Surface] = []
        self.item_images: dict[str, pygame.Surface] = {}
        self.shadow_origin_x = 0.0
        self.shadow_phase = 0.0
        self.invincible_until = 0
        self._shadow_sprite_logged = False

    def configure(self, scene_id: str, tile_map, player, quest_manager) -> None:
        self.active = scene_id in self.SCENE_IDS
        self.points = []
        self.nearby_point = None
        if not self.active:
            return

        records = [
            record for record in getattr(tile_map, "object_records", [])
            if record.type in {"collectible", "material", "pattern_source"}
        ]
        for record in records:
            raw_item_id = str(
                record.properties.get("item_id")
                or record.properties.get("reward_item")
                or record.properties.get("pattern_id")
                or record.id
            )
            item_id = self._normalize_item_id(raw_item_id)
            if item_id not in self.REQUIRED_ITEMS:
                continue
            self.points.append(
                MarketCollectPoint(
                    item_id=item_id,
                    label=str(record.properties.get("display_name") or COLLECT_LABELS[item_id]),
                    action=COLLECT_ACTIONS.get(item_id, "\u6536\u96c6"),
                    rect=record.rect.copy(),
                    sprite_path=ITEM_SPRITES[item_id],
                    collected=quest_manager.has_item(item_id),
                )
            )

        if not self.points:
            self._create_demo_points(player, tile_map, quest_manager)

        self._load_item_images()
        self._load_shadow_frames()
        self._create_demo_shadow(player, tile_map)

    def update(self, dt: float, player, quest_manager) -> None:
        if not self.active:
            return
        self._update_nearby(player)
        self._update_patrol_shadow(dt, player, quest_manager)

    def draw(self, surface: pygame.Surface, camera) -> None:
        if not self.active:
            return
        now = pygame.time.get_ticks()
        for point in self.points:
            if point.collected:
                continue
            center = camera.world_to_screen(point.rect.centerx, point.rect.centery)
            bob = int(math.sin(now / 260.0 + point.rect.x * 0.01) * 5)
            pulse = int(24 + math.sin(now / 180.0) * 4)
            glow = pygame.Surface((pulse * 2 + 8, pulse * 2 + 8), pygame.SRCALPHA)
            pygame.draw.circle(glow, (238, 210, 112, 64), (pulse + 4, pulse + 4), pulse)
            pygame.draw.circle(glow, (255, 236, 160, 150), (pulse + 4, pulse + 4), 9)
            surface.blit(glow, (center[0] - pulse - 4, center[1] - pulse - 4 + 8))
            image = self.item_images.get(point.item_id)
            if image is not None:
                image_rect = image.get_rect(center=(center[0], center[1] + bob))
                surface.blit(image, image_rect)
            else:
                pygame.draw.circle(surface, (255, 236, 160), (center[0], center[1] + bob), 12)
            if point is self.nearby_point:
                label = self.font.render(f"E\uff1a{point.action} {point.label}", True, (255, 239, 178))
                surface.blit(label, (center[0] - label.get_width() // 2, center[1] - 48))

        self._draw_shadow(surface, camera)

    def handle_confirm(self, quest_manager) -> bool:
        point = self.nearby_point
        if not self.active or point is None or point.collected:
            return False
        point.collected = True
        quest_manager.add_item(point.item_id)
        if self.status_callback is not None:
            self.status_callback(f"\u83b7\u5f97\uff1a{point.label}")
        if self.sfx_callback is not None:
            self.sfx_callback("collect")
        print(f"[COLLECT] item={point.item_id} sprite={point.sprite_path}")
        self._complete_if_ready(quest_manager)
        return True

    def nearby_prompt_object(self):
        if not self.active or self.nearby_point is None or self.nearby_point.collected:
            return None
        return _PromptObject(self.nearby_point)

    def _create_demo_points(self, player, tile_map, quest_manager) -> None:
        base_x = player.rect.centerx + 160
        base_y = player.rect.centery + 64
        offsets = ((0, 0), (120, 56), (48, 144))
        map_rect = pygame.Rect(24, 24, tile_map.drawable_width - 48, tile_map.drawable_height - 48)
        for item_id, (offset_x, offset_y) in zip(self.REQUIRED_ITEMS, offsets):
            rect = pygame.Rect(base_x + offset_x, base_y + offset_y, 34, 34)
            rect.clamp_ip(map_rect)
            self.points.append(
                MarketCollectPoint(
                    item_id=item_id,
                    label=COLLECT_LABELS[item_id],
                    action=COLLECT_ACTIONS[item_id],
                    rect=rect,
                    sprite_path=ITEM_SPRITES[item_id],
                    collected=quest_manager.has_item(item_id),
                )
            )
        print("[MARKET] no tiled collectibles found; created demo collect points")

    def _normalize_item_id(self, item_id: str) -> str:
        return ITEM_ID_ALIASES.get(item_id, item_id)

    def _load_item_images(self) -> None:
        for item_id, sprite_path in ITEM_SPRITES.items():
            if item_id in self.item_images:
                continue
            path = Path(sprite_path)
            if not path.exists():
                print(f"[COLLECT][WARN] missing sprite item={item_id} sprite={sprite_path}")
                continue
            try:
                image = pygame.image.load(str(path)).convert_alpha()
                self.item_images[item_id] = pygame.transform.smoothscale(image, (52, 52))
            except pygame.error as exc:
                print(f"[COLLECT][WARN] failed load sprite item={item_id} sprite={sprite_path} error={exc}")

    def _create_demo_shadow(self, player, tile_map) -> None:
        self.shadow_rect.size = (56, 56)
        self.shadow_rect.center = (
            min(max(player.rect.centerx + 120, 48), max(48, tile_map.drawable_width - 48)),
            min(max(player.rect.centery + 190, 48), max(48, tile_map.drawable_height - 48)),
        )
        self.shadow_origin_x = float(self.shadow_rect.centerx)
        self.shadow_phase = 0.0
        print(f"[MARKET] patrol shadow spawned pos={self.shadow_rect.center}")

    def _load_shadow_frames(self) -> None:
        if self.shadow_frames:
            return

        for sprite_path in MARKET_SHADOW_SPRITES:
            path = Path(sprite_path)
            if not path.exists():
                continue
            try:
                image = pygame.image.load(str(path)).convert_alpha()
                self.shadow_frames.append(pygame.transform.smoothscale(image, (56, 56)))
                if not self._shadow_sprite_logged:
                    print(f"[MARKET_SHADOW] use sprite={path.name}")
                    self._shadow_sprite_logged = True
            except pygame.error as exc:
                print(f"[MARKET_SHADOW][WARN] failed load sprite={sprite_path} error={exc}")

        if not self.shadow_frames:
            print("[MARKET_SHADOW][WARN] shadow_spirit sprites unavailable; using purple placeholder")

    def _draw_shadow(self, surface: pygame.Surface, camera) -> None:
        screen_rect = camera.apply_rect(self.shadow_rect)
        if self.shadow_frames:
            frame_index = (pygame.time.get_ticks() // 220) % len(self.shadow_frames)
            image = self.shadow_frames[frame_index]
            image_rect = image.get_rect(center=screen_rect.center)
            surface.blit(image, image_rect)
            return

        shadow_layer = pygame.Surface((screen_rect.width + 14, screen_rect.height + 14), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow_layer, (124, 60, 178, 95), shadow_layer.get_rect())
        pygame.draw.ellipse(shadow_layer, (90, 42, 130), pygame.Rect(7, 7, screen_rect.width, screen_rect.height))
        pygame.draw.ellipse(shadow_layer, (210, 170, 255), pygame.Rect(7, 7, screen_rect.width, screen_rect.height), 2)
        surface.blit(shadow_layer, (screen_rect.x - 7, screen_rect.y - 7))

    def _update_nearby(self, player) -> None:
        self.nearby_point = None
        best_distance = self.INTERACT_DISTANCE
        player_center = pygame.math.Vector2(player.rect.center)
        for point in self.points:
            if point.collected:
                continue
            distance = player_center.distance_to(point.rect.center)
            if distance <= best_distance:
                best_distance = distance
                self.nearby_point = point

    def _update_patrol_shadow(self, dt: float, player, quest_manager) -> None:
        self.shadow_phase += max(dt, 0.016) * 1.8
        self.shadow_rect.centerx = int(self.shadow_origin_x + math.sin(self.shadow_phase) * 72)
        if not self.shadow_rect.colliderect(player.rect):
            return
        now = pygame.time.get_ticks()
        if now < self.invincible_until:
            return
        self.invincible_until = now + self.SHADOW_HIT_COOLDOWN_MS
        hp = quest_manager.damage_light(1)
        if self.status_callback is not None:
            self.status_callback(MARKET_HIT_TEXT)
        if self.sfx_callback is not None:
            self.sfx_callback("player_hit")
        if self.floating_text_callback is not None:
            self.floating_text_callback("\u94f6\u5149 -1", player.rect.midtop, (255, 180, 190))
        if self.shake_callback is not None:
            self.shake_callback(120, 3)
        print(f"[MARKET_SHADOW] player hit light={hp}")

    def _complete_if_ready(self, quest_manager) -> None:
        if all(quest_manager.has_item(item_id) for item_id in self.REQUIRED_ITEMS):
            quest_manager.complete_level("market_collect")
            if quest_manager.stage == "market_collect":
                quest_manager.advance_to("go_river")
