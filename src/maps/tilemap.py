from pathlib import Path

import pygame
from pytmx import TiledImageLayer, TiledObjectGroup, TiledTileLayer, load_pygame
from src.maps.object_loader import ObjectLoader, ObjectRecord


class TileMap:
    """负责加载和绘制 Tiled TMX 地图。"""

    PREFERRED_TILE_LAYERS = ("background", "ground", "decoration", "foreground")
    FUNCTION_LAYER_NAMES = {
        "collision",
        "npc",
        "npc_points",
        "interaction",
        "transition",
        "trigger_points",
        "object_points",
        "pattern_points",
        "clue_points",
        "checkpoint_points",
    }
    NPC_LAYER_NAMES = {"npc", "npc_points"}
    TRANSITION_LAYER_NAMES = {"trigger_points", "transition"}
    DEFAULT_NPC_DIALOGUE = "孩子，银饰失去了光泽，去寻找银纹的线索吧。"
    NPC_ID_TO_SPRITE = {
        "elder": "elder_idle",
        "silversmith": "silversmith_idle",
        "smith": "silversmith_idle",
        "market_auntie": "market_auntie_idle",
        "festival_host": "festival_host_idle",
        "host": "host_idle_front",
        "shadow_spirit": "shadow_spirit_idle_front",
    }
    MAP_NPC_DEFAULT_IDS = {
        "village_entrance": ("elder", "silversmith", "market_auntie", "festival_host", "smith", "host"),
        "village_market": ("market_auntie",),
        "river_valley": ("shadow_spirit", "elder"),
        "festival_square": ("festival_host",),
        "workshop_exterior": ("silversmith", "smith"),
        "workshop_interior": ("silversmith", "smith", "elder", "market_auntie"),
    }

    def __init__(self, map_path: str) -> None:
        self.map_path = Path(map_path)
        self.tmx_data = None
        self.error_message = ""
        self.loaded = False
        self.width = 0
        self.height = 0
        self.drawable_width = 0
        self.drawable_height = 0
        self.tile_width = 32
        self.tile_height = 32
        self.layer_names: list[str] = []
        self.collision_rects: list[pygame.Rect] = []
        self.object_records: list[ObjectRecord] = []
        self.visible_object_records: list[ObjectRecord] = []
        self.npc_data: list[dict] = []
        self.scene_exits: list[dict] = []
        self.spawn_points: dict[str, tuple[int, int]] = {}
        self.spawn_rects: dict[str, pygame.Rect] = {}
        self.spawn_order: list[str] = []
        self._reported_missing_layers = False
        self._reported_fallback_layers = False
        self._reported_render_diagnostics = False

        self.load()

    def load(self) -> None:
        print(f"[TileMap] 尝试加载地图: {self.map_path}")

        if not self.map_path.exists():
            self.error_message = f"地图文件不存在: {self.map_path}"
            print(f"[TileMap] 加载失败: {self.error_message}")
            return

        try:
            self.tmx_data = load_pygame(str(self.map_path))
            self.tile_width = self.tmx_data.tilewidth
            self.tile_height = self.tmx_data.tileheight
            self.width = self.tmx_data.width * self.tile_width
            self.height = self.tmx_data.height * self.tile_height
            self.layer_names = [layer.name for layer in self.tmx_data.layers]
            self._calculate_drawable_size()
            self.loaded = True

            print("[TileMap] TMX 加载成功")
            print(f"[TileMap] TMX 地图总宽高: {self.width} x {self.height}")
            print(f"[TileMap] 可显示地图范围: {self.drawable_width} x {self.drawable_height}")
            print(f"[TileMap] 瓦片宽高: {self.tile_width} x {self.tile_height}")
            print(f"[TileMap] 图层列表: {self.layer_names}")
            self._report_render_layers()
            self._load_collision_rects()
            self._load_npc_data()
            self._load_transition_data()
            self._load_object_records()
        except Exception as exc:
            self.error_message = f"地图加载失败: {exc}"
            print(f"[TileMap] 加载失败: {self.error_message}")

    def _load_object_records(self) -> None:
        self.object_records.clear()
        self.visible_object_records.clear()
        if self.tmx_data is None:
            return

        self.object_records = ObjectLoader(self.tmx_data).load()
        visible_types = {
            "item",
            "hidden_collectible",
            "repair_table",
            "display_table",
            "silver_part_display",
            "pattern_source",
            "clue",
            "pattern_checkpoint",
            "task_trigger",
            "shadow_fragment_trigger",
        }
        self.visible_object_records = [
            record for record in self.object_records if record.type in visible_types
        ]

    def _calculate_drawable_size(self) -> None:
        self.drawable_width = self.width
        self.drawable_height = self.height

        background_layer = self._find_layer_by_name("background")
        if background_layer is None:
            print("[TileMap] 未找到 background 层，可显示范围回退到 TMX 总尺寸")
            return

        if isinstance(background_layer, TiledImageLayer):
            image = getattr(background_layer, "image", None)
            if image is not None:
                self.drawable_width = image.get_width()
                self.drawable_height = image.get_height()
                return

        if isinstance(background_layer, TiledTileLayer):
            tile_bounds = self._calculate_tile_layer_bounds(background_layer)
            if tile_bounds is not None:
                self.drawable_width, self.drawable_height = tile_bounds
                return

        print("[TileMap] background 层范围无法计算，可显示范围回退到 TMX 总尺寸")

    def _calculate_tile_layer_bounds(self, layer: TiledTileLayer) -> tuple[int, int] | None:
        max_tile_x = -1
        max_tile_y = -1

        for tile_x, tile_y, tile_image in layer.tiles():
            if tile_image is None:
                continue
            max_tile_x = max(max_tile_x, tile_x)
            max_tile_y = max(max_tile_y, tile_y)

        if max_tile_x < 0 or max_tile_y < 0:
            return None

        return (max_tile_x + 1) * self.tile_width, (max_tile_y + 1) * self.tile_height

    def _report_render_layers(self) -> None:
        if self._reported_render_diagnostics or self.tmx_data is None:
            return

        self._reported_render_diagnostics = True
        drawable_layers = 0
        image_layers = 0
        tile_layers = 0

        for layer in self.tmx_data.layers:
            if not self._is_draw_layer(layer):
                continue
            if not bool(getattr(layer, "visible", True)):
                print(f"[MAP_RENDER][WARN] layer hidden name={layer.name}")
                continue

            drawable_layers += 1
            if isinstance(layer, TiledTileLayer):
                tile_layers += 1
            elif isinstance(layer, TiledImageLayer):
                image_layers += 1
                if getattr(layer, "image", None) is None:
                    print(f"[MAP_RENDER][ERROR] missing image={self._image_layer_source(layer)}")

        if drawable_layers == 0:
            print(f"[MAP_RENDER][ERROR] no drawable map layers in {self.map_path.name}")

        print(
            f"[MAP_RENDER] scene={self._scene_log_name()} layer_count={drawable_layers} "
            f"image_layers={image_layers} tile_layers={tile_layers}"
        )

    def _scene_log_name(self) -> str:
        if self.map_path.stem == "village_hub":
            return "village"
        return self.map_path.stem

    def _image_layer_source(self, layer: TiledImageLayer) -> str:
        for attr in ("source", "image_source", "filename"):
            value = getattr(layer, attr, None)
            if value:
                return str(value)
        return "(unknown)"

    def _find_layer_by_name(self, layer_name: str):
        if self.tmx_data is None:
            return None

        normalized_name = layer_name.strip().lower()
        for layer in self.tmx_data.layers:
            if layer.name.strip().lower() == normalized_name:
                return layer

        return None

    def _load_collision_rects(self) -> None:
        if self.tmx_data is None:
            return

        self.collision_rects.clear()
        collision_layer = self._find_collision_object_layer()
        if collision_layer is None:
            print("[TileMap] 未找到 collision 对象层，本地图暂不启用碰撞矩形")
            return

        skipped_count = 0
        for obj in collision_layer:
            if self._is_rect_object(obj):
                rect = pygame.Rect(
                    int(round(obj.x)),
                    int(round(obj.y)),
                    int(round(obj.width)),
                    int(round(obj.height)),
                )
                self.collision_rects.append(rect)
            else:
                skipped_count += 1
                print(f"[TileMap] 跳过非矩形 collision 对象: id={getattr(obj, 'id', 'unknown')}")

        print(f"[TileMap] collision 矩形数量: {len(self.collision_rects)}")
        if skipped_count:
            print(f"[TileMap] 跳过非矩形 collision 对象数量: {skipped_count}")

    def _load_npc_data(self) -> None:
        if self.tmx_data is None:
            return

        self.npc_data.clear()
        npc_layers = self._find_npc_object_layers()
        if not npc_layers:
            print("[TileMap] 未找到 npc / npc_points 对象层，本地图暂不生成 NPC")
            return

        for layer in npc_layers:
            print(f"[TileMap] 当前读取到的 NPC 图层名: {layer.name}")
            for obj in layer:
                npc_index = len(self.npc_data) + 1
                npc_id = self._get_npc_id(obj, npc_index)
                npc_id = self._resolve_npc_id(npc_id, npc_index)
                name = self._get_npc_display_name(obj)
                dialogue = self._get_object_value(obj, "dialogue", self.DEFAULT_NPC_DIALOGUE)
                character = self._get_object_property(obj, "character", "")
                if not character:
                    character = self._get_object_property(obj, "character_id", "")
                sprite = self._get_object_property(obj, "sprite", "")
                if not sprite:
                    sprite_key = str(character or npc_id).strip().lower()
                    sprite = self.NPC_ID_TO_SPRITE.get(sprite_key, "")
                width = int(round(getattr(obj, "width", 0) or 32))
                height = int(round(getattr(obj, "height", 0) or 32))
                rect = pygame.Rect(
                    int(round(obj.x)),
                    int(round(obj.y)),
                    width,
                    height,
                )

                self.npc_data.append(
                    {
                        "id": str(npc_id),
                        "name": str(name),
                        "dialogue": str(dialogue),
                        "sprite": str(sprite),
                        "character": str(character),
                        "rect": rect,
                        "world_x": int(round(obj.x)),
                        "world_y": int(round(obj.y)),
                    }
                )
                image_path = f"assets/sprites/npc/{sprite}.png" if sprite else "(none)"
                print(
                    f"[TileMap] NPC: id={npc_id}, name={name}, character={character or '(none)'}, "
                    f"sprite={sprite or '(none)'}, "
                    f"image_path={image_path}, x={rect.x}, y={rect.y}"
                )

        print(f"[TileMap] NPC 数量: {len(self.npc_data)}")

    def _load_transition_data(self) -> None:
        if self.tmx_data is None:
            return

        self.scene_exits.clear()
        self.spawn_points.clear()
        self.spawn_rects.clear()
        self.spawn_order.clear()
        transition_layers = self._find_transition_object_layers()
        if not transition_layers:
            print("[TileMap] 未找到 trigger_points / transition / Transition 对象层")
            return

        for layer in transition_layers:
            print(f"[TileMap] 当前读取到的出口/出生点图层名: {layer.name}")
            for obj in layer:
                if self._is_spawn_object(obj):
                    self._add_spawn_point(obj)
                elif self._is_scene_exit_object(obj):
                    self._add_scene_exit(obj)

        print(f"[TileMap] spawn 数量: {len(self.spawn_points)}")
        print(f"[TileMap] 出口数量: {len(self.scene_exits)}")
        if not self.scene_exits:
            print("[TileMap] 当前地图没有可用 scene_exit 出口对象")

    def _find_transition_object_layers(self) -> list[TiledObjectGroup]:
        if self.tmx_data is None:
            return []

        transition_layers = []
        for layer in self.tmx_data.layers:
            layer_name = layer.name.strip().lower()
            if self._is_old_layer(layer.name):
                continue
            if layer_name in self.TRANSITION_LAYER_NAMES and isinstance(layer, TiledObjectGroup):
                transition_layers.append(layer)

        return transition_layers

    def _add_spawn_point(self, obj) -> None:
        spawn_id = self._get_object_property(obj, "spawn_id", "")
        if not spawn_id:
            spawn_id = self._get_object_property(obj, "id", "")
        if not spawn_id:
            spawn_id = getattr(obj, "name", "") or f"spawn_{len(self.spawn_points) + 1}"

        x = int(round(getattr(obj, "x", 0)))
        y = int(round(getattr(obj, "y", 0)))
        width = int(round(getattr(obj, "width", 0) or 32))
        height = int(round(getattr(obj, "height", 0) or 32))
        self.spawn_points[str(spawn_id)] = (x, y)
        self.spawn_rects[str(spawn_id)] = pygame.Rect(x, y, width, height)
        self.spawn_order.append(str(spawn_id))
        print(f"[TileMap] Spawn: id={spawn_id}, x={x}, y={y}, rect={self.spawn_rects[str(spawn_id)]}")

    def _add_scene_exit(self, obj) -> None:
        target_scene = self._get_object_value(obj, "target_scene", "")
        exit_id = self._get_exit_id(obj)
        if not target_scene:
            print(f"[TileMap] 出口缺少 target_scene，已跳过: id={exit_id}")
            return

        width = getattr(obj, "width", 0) or 0
        height = getattr(obj, "height", 0) or 0
        if width <= 0 or height <= 0:
            print(f"[TileMap] 出口缺少 width/height，已跳过: id={exit_id}")
            return

        rect = pygame.Rect(
            int(round(getattr(obj, "x", 0))),
            int(round(getattr(obj, "y", 0))),
            int(round(width)),
            int(round(height)),
        )
        target_spawn = self._get_object_value(obj, "target_spawn", "")
        locked_message = self._get_object_value(obj, "locked_message", "")
        scene_exit = {
            "id": str(exit_id),
            "type": self._get_object_value(obj, "type", "scene_exit"),
            "target_scene": str(target_scene),
            "target_spawn": str(target_spawn),
            "locked_message": str(locked_message),
            "rect": rect,
        }
        self.scene_exits.append(scene_exit)
        print(
            f"[TileMap] 出口: id={scene_exit['id']}, target_scene={scene_exit['target_scene']}, "
            f"target_spawn={scene_exit['target_spawn'] or '(none)'}, rect={rect}"
        )

    def _get_exit_id(self, obj) -> str:
        exit_id = self._get_object_property(obj, "id", "")
        if exit_id:
            return exit_id

        object_name = getattr(obj, "name", None)
        if object_name:
            return object_name

        return str(getattr(obj, "id", f"exit_{len(self.scene_exits) + 1}"))

    def _is_spawn_object(self, obj) -> bool:
        object_type = self._get_object_value(obj, "type", "").strip().lower()
        return object_type == "spawn"

    def _is_scene_exit_object(self, obj) -> bool:
        object_type = self._get_object_value(obj, "type", "").strip().lower()
        object_id = self._get_object_property(obj, "id", "")
        object_name = getattr(obj, "name", "") or ""
        return (
            object_type == "scene_exit"
            or "exit" in str(object_id).lower()
            or "exit" in str(object_name).lower()
        )

    def _find_npc_object_layers(self) -> list[TiledObjectGroup]:
        if self.tmx_data is None:
            return []

        npc_layers = []
        for layer in self.tmx_data.layers:
            layer_name = layer.name.strip().lower()
            if self._is_old_layer(layer.name):
                continue
            if layer_name in self.NPC_LAYER_NAMES and isinstance(layer, TiledObjectGroup):
                npc_layers.append(layer)

        return npc_layers

    def _get_object_value(self, obj, key: str, default: str) -> str:
        properties = getattr(obj, "properties", {}) or {}
        value = properties.get(key)
        if value not in (None, ""):
            return value

        value = getattr(obj, key, None)
        if value not in (None, ""):
            return value

        return default

    def _get_npc_id(self, obj, npc_index: int) -> str:
        npc_id = self._get_object_property(obj, "id", "")
        if npc_id:
            return npc_id

        object_name = getattr(obj, "name", None)
        if object_name:
            return object_name

        return f"npc_{npc_index}"

    def _resolve_npc_id(self, npc_id: str, npc_index: int) -> str:
        if not str(npc_id).startswith("npc_"):
            return npc_id

        map_defaults = self.MAP_NPC_DEFAULT_IDS.get(self.map_path.stem, ())
        default_index = npc_index - 1
        if 0 <= default_index < len(map_defaults):
            return map_defaults[default_index]
        return npc_id

    def _get_npc_display_name(self, obj) -> str:
        properties = getattr(obj, "properties", {}) or {}
        for key in ("name", "display_name"):
            value = properties.get(key)
            if value not in (None, ""):
                return value

        return "NPC"

    def _get_object_property(self, obj, key: str, default: str) -> str:
        properties = getattr(obj, "properties", {}) or {}
        value = properties.get(key)
        if value not in (None, ""):
            return value

        return default

    def _find_collision_object_layer(self):
        if self.tmx_data is None:
            return None

        for layer in self.tmx_data.layers:
            layer_name = layer.name.strip().lower()
            if layer_name == "collision" and isinstance(layer, TiledObjectGroup):
                return layer

        return None

    def _is_rect_object(self, obj) -> bool:
        has_size = getattr(obj, "width", 0) and getattr(obj, "height", 0)
        has_shape_data = any(
            getattr(obj, attr, None)
            for attr in ("ellipse", "points", "polygon", "polyline")
        )
        return bool(has_size) and not has_shape_data

    def draw(self, surface: pygame.Surface, camera) -> None:
        if not self.loaded or self.tmx_data is None:
            return

        visible_draw_layers = [
            layer
            for layer in self.tmx_data.visible_layers
            if self._is_draw_layer(layer)
        ]
        layers_by_name = {layer.name.strip().lower(): layer for layer in visible_draw_layers}
        drawn_layer_names: set[str] = set()

        for layer_name in self.PREFERRED_TILE_LAYERS:
            layer = layers_by_name.get(layer_name.strip().lower())
            if layer is None:
                if not self._reported_missing_layers:
                    print(f"[TileMap] 缺少标准瓦片层: {layer_name}")
                continue

            self._draw_layer(surface, layer, camera)
            drawn_layer_names.add(layer.name)

        self._reported_missing_layers = True

        if not drawn_layer_names:
            if not self._reported_fallback_layers:
                print("[TileMap] 未找到标准瓦片层，回退绘制所有可见瓦片层")
                self._reported_fallback_layers = True
            for layer in visible_draw_layers:
                self._draw_layer(surface, layer, camera)
                drawn_layer_names.add(layer.name)

    def _draw_layer(self, surface: pygame.Surface, layer, camera) -> None:
        if isinstance(layer, TiledTileLayer):
            self._draw_tile_layer(surface, layer, camera)
        elif isinstance(layer, TiledImageLayer):
            self._draw_image_layer(surface, layer, camera)

    def _draw_tile_layer(self, surface: pygame.Surface, layer: TiledTileLayer, camera) -> None:
        for x, y, tile_image in layer.tiles():
            if tile_image is None:
                continue

            screen_x, screen_y = camera.world_to_screen(x * self.tile_width, y * self.tile_height)
            surface.blit(tile_image, (screen_x, screen_y))

    def _draw_image_layer(self, surface: pygame.Surface, layer: TiledImageLayer, camera) -> None:
        image = getattr(layer, "image", None)
        if image is None:
            return

        layer_x = int(round(getattr(layer, "x", 0)))
        layer_y = int(round(getattr(layer, "y", 0)))
        screen_x, screen_y = camera.world_to_screen(layer_x, layer_y)
        surface.blit(image, (screen_x, screen_y))

    def draw_collision_debug(self, surface: pygame.Surface, camera) -> None:
        for rect in self.collision_rects:
            pygame.draw.rect(surface, (255, 64, 64), camera.apply_rect(rect), 2)

    def _is_old_layer(self, layer_name: str) -> bool:
        return layer_name.strip().lower().startswith("old_")

    def _is_function_layer(self, layer_name: str) -> bool:
        return layer_name.strip().lower() in self.FUNCTION_LAYER_NAMES

    def _is_draw_layer(self, layer) -> bool:
        if not isinstance(layer, (TiledTileLayer, TiledImageLayer)):
            return False

        return not self._is_old_layer(layer.name) and not self._is_function_layer(layer.name)
