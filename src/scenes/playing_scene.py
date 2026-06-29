from __future__ import annotations

from pathlib import Path

import pygame

from settings import DEBUG_COLLISION, DEBUG_OVERLAY, DEFAULT_SCENE, SCREEN_HEIGHT, SCREEN_WIDTH
from src.entities.interactable import Interactable
from src.entities.npc import NPC
from src.entities.player import Player
from src.entities.shadow_spirit import ShadowSpirit
from src.maps.camera import Camera
from src.maps.tilemap import TileMap
from src.scenes.base_scene import BaseScene
from src.scenes.scene_registry import SceneRegistry
from src.systems.audio_manager import AudioManager
from src.systems.dialogue_manager import DialogueManager
from src.systems.combat_effect_manager import CombatEffectManager
from src.systems.festival_defense_manager import FestivalDefenseManager
from src.systems.inventory import Inventory
from src.systems.main_quest_manager import MainQuestManager
from src.systems.market_collect_manager import MarketCollectManager
from src.systems.score_manager import ScoreManager
from src.systems.shadow_chase_manager import ShadowChaseManager
from src.systems.task_manager import TaskManager
from src.ui.dialogue_box import DialogueBox
from src.ui.ending_panel import EndingPanel
from src.ui.fonts import load_chinese_font
from src.ui.navigation_panel import NavigationPanel
from src.ui.objective_hud import ObjectiveHUD
from src.ui.quest_arrow import QuestArrow
from src.ui.scene_transition import SceneTransitionManager
from src.ui.shadow_hud import ShadowHUD
from src.ui.simple_inventory_panel import SimpleInventoryPanel


OBJ_TALK_ELDER = "\u4e0e\u6751\u5be8\u957f\u8005\u5bf9\u8bdd"
OBJ_TALK_ELDER_HINT = "\u4e86\u89e3\u94f6\u9970\u5931\u5149\u7684\u539f\u56e0"
OBJ_GO_RIVER = "\u524d\u5f80\u6cb3\u8c37"
OBJ_GO_RIVER_HINT = "\u5bfb\u627e\u6df7\u4e71\u5f71\u7eb9"
OBJ_PURIFY_SHADOW = "\u51c0\u5316\u5f71\u7eb9"
OBJ_PURIFY_HINT = "\u9760\u8fd1\u5f71\u7eb9\u540e\u6309 Space \u91ca\u653e\u94f6\u5149"
OBJ_SHADOW_INTRO = "\u4e00\u56e2\u6df7\u4e71\u5f71\u7eb9\u6b63\u5728\u9760\u8fd1\u2026\u2026"
OBJ_DODGE_PURIFY = "\u8eb2\u907f\u5f71\u7eb9\u5e76\u5b8c\u6210\u51c0\u5316"
OBJ_DODGE_PURIFY_HINT = "Space\uff1a\u94f6\u5149\u51c0\u5316"
OBJ_RETURN_SMITH = "\u8fd4\u56de\u5de5\u574a\u627e\u94f6\u5320"
OBJ_REWARD_HINT = "\u5df2\u83b7\u5f97\u5c71\u7eb9\u7ebf\u7d22"
STATUS_SHADOW_TELEPORT = "\u5f71\u7eb9\u5df2\u4f20\u9001\u5230\u9644\u8fd1"
STATUS_LOCKED_EXIT = "\u5f53\u524d\u8fd8\u4e0d\u80fd\u524d\u5f80\u8fd9\u91cc\n\u8bf7\u5148\u5b8c\u6210\u524d\u7f6e\u76ee\u6807"
DEBUG_SKIP_NOTICE = "[DEBUG] \u5f53\u524d\u4e3a\u6f14\u793a\u8df3\u5173\u6a21\u5f0f"
TOAST_LOCK_TITLE = "\u6682\u4e0d\u80fd\u524d\u5f80"


class PlayingScene(BaseScene):
    """Main gameplay scene: map, player, objects, NPCs, and scene transitions."""

    FALLBACK_SCENE = "village"
    EXIT_INTERACTION_DISTANCE = 50
    EXIT_DISTANCE_TIE_THRESHOLD = 12
    NPC_INTERACTION_DISTANCE = 50
    NPC_INTERACT_RADIUS = 110
    TRANSITION_COOLDOWN_MS = 500
    INPUT_COOLDOWN_MS = 120
    CONFIRM_KEYS = (pygame.K_e, pygame.K_RETURN)
    DIALOGUE_NEXT_KEYS = (pygame.K_RETURN, pygame.K_SPACE)
    FORCE_SCENE_KEYS = {
        pygame.K_1: "village",
        pygame.K_KP1: "village",
        pygame.K_2: "mountain",
        pygame.K_KP2: "mountain",
        pygame.K_3: "workshop",
        pygame.K_KP3: "workshop",
        pygame.K_4: "mountain",
        pygame.K_KP4: "mountain",
        pygame.K_5: "pattern_mountain",
        pygame.K_KP5: "pattern_mountain",
        pygame.K_6: "festival",
        pygame.K_KP6: "festival",
    }
    EXIT_SELECTION_KEYS = {
        pygame.K_1: 0,
        pygame.K_KP1: 0,
        pygame.K_2: 1,
        pygame.K_KP2: 1,
        pygame.K_3: 2,
        pygame.K_KP3: 2,
    }
    DEBUG_STAGE_KEYS = {
        pygame.K_F4: "market_collect",
        pygame.K_F5: "shadow_challenge",
        pygame.K_F6: "festival_defense",
    }

    def __init__(self, font: pygame.font.Font) -> None:
        self.font = load_chinese_font(24, font)
        self.debug_font = pygame.font.Font(None, 18)
        self.debug_overlay_visible = False
        self.scene_registry = SceneRegistry()
        self.dialogue_box = DialogueBox(font)
        self.dialogue_manager = DialogueManager()
        self.navigation_panel = NavigationPanel(font, font)
        self.objective_hud = ObjectiveHUD(font)
        self.quest_arrow = QuestArrow(font)
        self.ending_panel = EndingPanel(font)
        self.shadow_hud = ShadowHUD(font)
        self.scene_transition = SceneTransitionManager()
        self.audio_manager = AudioManager()
        self.combat_effect_manager = CombatEffectManager(font)
        self.main_quest_manager = MainQuestManager()
        self.market_collect_manager = MarketCollectManager(
            font,
            status_callback=self._set_status_message,
            floating_text_callback=self.combat_effect_manager.spawn_floating_text,
            shake_callback=self.combat_effect_manager.shake,
            sfx_callback=self._play_sfx,
        )
        self.festival_defense_manager = FestivalDefenseManager(
            font,
            status_callback=self._set_status_message,
            hit_effect_callback=self.combat_effect_manager.spawn_hit_spark,
            floating_text_callback=self.combat_effect_manager.spawn_floating_text,
            shake_callback=self.combat_effect_manager.shake,
            sfx_callback=self._play_sfx,
        )
        self.simple_inventory_panel = SimpleInventoryPanel(font)
        self.inventory = Inventory()
        self.task_manager = TaskManager()
        self.score_manager = ScoreManager()
        self.shadow_chase_manager = ShadowChaseManager(
            status_callback=self._set_status_message,
            reset_player_callback=self._reset_player_after_shadow_failure,
            defeated_callback=self.on_shadow_defeated,
            hit_effect_callback=self.combat_effect_manager.spawn_hit_spark,
            defeat_effect_callback=self.combat_effect_manager.spawn_defeat_burst,
            floating_text_callback=self.combat_effect_manager.spawn_floating_text,
            shake_callback=self.combat_effect_manager.shake,
            sfx_callback=self._play_sfx,
        )

        self.tile_map: TileMap | None = None
        self.camera: Camera | None = None
        self.player: Player | None = None
        self.npcs: list[NPC] = []
        self.interactables: list[Interactable] = []
        self.shadow_spirits: list[ShadowSpirit] = []
        self.shadow_triggers: list[pygame.Rect] = []
        self.nearby_shadow: ShadowSpirit | None = None
        self.nearby_shadow_trigger: pygame.Rect | None = None
        self.nearby_npc: NPC | None = None
        self.nearby_item: Interactable | None = None
        self.nearby_exit: dict | None = None
        self.nearby_exits: list[dict] = []
        self.active_npc: NPC | None = None
        self.current_scene_name = ""
        self.current_spawn_position: tuple[int, int] = (0, 0)
        self.error_message = ""
        self.status_message = ""
        self.status_message_until = 0
        self.quest_lock_toast_hint = ""
        self.quest_lock_toast_until = 0
        self.elder_dialogue_finished = False
        self.debug_skip_mode = False
        self.ending_panel_dismissed = False
        self.shadow_intro_until = 0
        self._last_purify_effect_radius_log = -1

        self._last_prompt_npc_id: str | None = None
        self._last_prompt_item_id: str | None = None
        self._last_prompt_exit_id: str | None = None
        self.selected_exit_id: str | None = None
        self.manual_exit_index: int | None = None
        self.manual_selected_exit_id: str | None = None
        self.manual_exit_selection_active = False
        self._last_exit_debug_signature: tuple | None = None
        self._last_exit_debug_at = 0
        self._last_dialogue_box_signature: tuple[str, str] | None = None
        self.transition_cooldown_until = 0
        self.input_cooldown_until = 0
        self._prev_keys: dict[int, bool] = {}

        self._load_initial_scene()

    def _load_initial_scene(self) -> None:
        if self.load_scene(DEFAULT_SCENE):
            return

        print(f"[Scene] default scene failed, trying fallback: {self.FALLBACK_SCENE}")
        if self.load_scene(self.FALLBACK_SCENE):
            return

        self.error_message = "Map load failed; check assets/maps and assets/tilesets."

    def load_scene(self, scene_name: str, spawn_id: str | None = None) -> bool:
        requested_scene_name = scene_name
        scene_name = self.scene_registry.canonical_name(scene_name)
        map_path = self.scene_registry.get_map_path(scene_name)
        print(f"[SCENE] change_scene request = {requested_scene_name} -> {scene_name}")
        print(f"[SCENE] target_scene registered = {map_path is not None}")
        if map_path is None:
            self.error_message = f"鏈厤缃垨鏈惎鐢ㄥ満鏅? {scene_name}"
            self._set_status_message(self.error_message)
            print(f"[ERROR] target_scene not registered: {scene_name}")
            return False

        print(f"[SCENE] map_path = {map_path}")
        tile_map = TileMap(map_path)
        if not tile_map.loaded:
            self.error_message = tile_map.error_message
            self._set_status_message(self.error_message)
            if "not found" in self.error_message:
                print(f"[ERROR] target map file not found: {map_path}")
            print(f"[ERROR] load_scene failed: {self.error_message}")
            return False

        spawn_x, spawn_y = self._resolve_spawn_position(tile_map, spawn_id)
        if self.player is None:
            self.player = Player(spawn_x, spawn_y)
        else:
            self._move_player_to(spawn_x, spawn_y)
        self.current_spawn_position = (spawn_x, spawn_y)

        self.tile_map = tile_map
        self.camera = Camera(tile_map.drawable_width, tile_map.drawable_height)
        self._nudge_player_out_of_exit(tile_map)
        self.current_spawn_position = self.player.rect.topleft
        self.current_scene_name = scene_name
        self.npcs = [
            NPC(
                data["id"],
                data["name"],
                data["dialogue"],
                data["world_x"],
                data["world_y"],
                data["sprite"],
                data.get("character", ""),
            )
            for data in tile_map.npc_data
            if self._is_playable_npc_record(data)
        ]
        for npc in self.npcs:
            npc.name = self.dialogue_manager.resolve_name(npc.id, npc.name)
        self._ensure_festival_host()
        self.interactables = [
            Interactable.from_record(record)
            for record in tile_map.visible_object_records
        ]
        self._load_shadow_chase_objects(tile_map, scene_name)
        self._place_shadows_for_demo(tile_map)
        if scene_name in {"river_valley", "mountain"} and self.shadow_spirits:
            self.shadow_intro_until = pygame.time.get_ticks() + 2000
        self.error_message = ""
        self._clear_interaction_state()
        self._sync_main_quest_for_scene()
        self.market_collect_manager.configure(scene_name, tile_map, self.player, self.main_quest_manager)
        self.festival_defense_manager.configure(scene_name, tile_map, self.player, self.main_quest_manager)
        self.shadow_chase_manager.configure(scene_name, self.shadow_spirits)
        self._print_festival_route_status(tile_map)
        self._update_scene_bgm()
        self.transition_cooldown_until = pygame.time.get_ticks() + self.TRANSITION_COOLDOWN_MS
        self.camera.update(self.player.rect)

        print(f"[Scene] 鏂板湴鍥惧姞杞芥垚鍔? {scene_name}")
        print(f"[Scene] current_scene = {self.current_scene_name}")
        print(f"[Scene] map_path = {map_path}")
        print(f"[Scene] collision count = {len(tile_map.collision_rects)}")
        print(f"[Scene] npc count = {len(self.npcs)}")
        print(f"[Scene] object count = {len(self.interactables)}")
        print(f"[Scene] shadow count = {len(self.shadow_spirits)}")
        print(f"[Scene] exit count = {len(tile_map.scene_exits)}")
        print(f"[Scene] player position = ({self.player.rect.x}, {self.player.rect.y})")
        return True

    def update(self, dt: float = 0) -> None:
        if self.player is None or self.camera is None:
            return

        self.scene_transition.update(dt)
        if self.scene_transition.is_blocking_input():
            self._remember_current_key_state()
            return

        self._handle_fallback_input()
        self._sync_main_quest_for_scene()
        if self.main_quest_manager.stage != "ending":
            self.ending_panel_dismissed = False
        self._update_npc_animations(dt)
        if self._is_ending_panel_open():
            self.combat_effect_manager.update()
            self.camera.update(self.player.rect)
            return
        if self.active_npc is not None:
            self.combat_effect_manager.update()
            return

        collision_rects = self.tile_map.collision_rects if self.tile_map is not None else []
        map_width = self.tile_map.drawable_width if self.tile_map is not None else SCREEN_WIDTH
        map_height = self.tile_map.drawable_height if self.tile_map is not None else SCREEN_HEIGHT

        self.player.update(collision_rects, map_width, map_height, dt)
        if self.main_quest_manager.stage != "ending":
            self.market_collect_manager.update(dt, self.player, self.main_quest_manager)
            self.shadow_chase_manager.update(dt, self.player, collision_rects)
            self.festival_defense_manager.update(dt, self.player, self.main_quest_manager)
        self.combat_effect_manager.update()
        self.camera.update(self.player.rect)
        self._update_nearby_npc()
        self._update_nearby_shadow()
        self._update_nearby_item()
        self._update_nearby_exit()

    def handle_event(self, event: pygame.event.Event) -> bool:
        if event.type != pygame.KEYDOWN:
            return False

        key_name = pygame.key.name(event.key)
        print(f"[Scene] KEYDOWN received: {key_name}")
        if event.key in self.CONFIRM_KEYS:
            print(f"[EVENT] confirm keydown received in PlayingScene: {self._confirm_key_name(event.key)}")

        if self.scene_transition.is_blocking_input():
            self._mark_input_handled()
            return True

        if self._is_ending_panel_open():
            return self._handle_ending_panel_key(event.key)

        if event.key == pygame.K_F1:
            self.navigation_panel.toggle_expanded()
            print(f"[UI] navigation panel expanded: {self.navigation_panel.expanded}")
            self._mark_input_handled()
            return True

        if event.key == pygame.K_F3:
            self.debug_overlay_visible = not self.debug_overlay_visible
            print(f"[DEBUG_UI] show_debug={self.debug_overlay_visible}")
            self._mark_input_handled()
            return True

        debug_stage = self.DEBUG_STAGE_KEYS.get(event.key)
        if debug_stage is not None:
            self.debug_skip_mode = True
            self._set_status_message(DEBUG_SKIP_NOTICE)
            self.main_quest_manager.force_stage(debug_stage)
            self._configure_level_managers_for_current_scene()
            self._mark_input_handled()
            return True

        if event.key == pygame.K_b and self.active_npc is None:
            self.simple_inventory_panel.toggle()
            self._play_sfx("inventory")
            self._mark_input_handled()
            return True

        if event.key == pygame.K_h:
            if self._debug_teleport_shadow_near_player():
                self._set_status_message(STATUS_SHADOW_TELEPORT)
                self._mark_input_handled()
                return True

        if self.active_npc is not None:
            if event.key in self.DIALOGUE_NEXT_KEYS:
                self._advance_dialogue("[Input]")
                self._mark_input_handled()
                return True
            if event.key == pygame.K_ESCAPE:
                self._close_dialogue("[Input]", finished=False)
                self._mark_input_handled()
                return True
            self._mark_input_handled()
            return True

        if event.key == pygame.K_SPACE:
            collision_rects = self.tile_map.collision_rects if self.tile_map is not None else []
            handled = self.festival_defense_manager.purify(self.player, self.main_quest_manager)
            if handled:
                self._mark_input_handled()
                return True
            handled = self.shadow_chase_manager.purify(self.player, collision_rects)
            if handled:
                self._mark_input_handled()
                return True

        if event.key == pygame.K_ESCAPE and self.shadow_chase_manager.cancel_chase():
            self._mark_input_handled()
            return True

        if event.key in self.EXIT_SELECTION_KEYS:
            self._update_nearby_exit()
            if len(self.nearby_exits) > 1:
                return self._handle_exit_selection_key(event.key, "[Input]")
            if len(self.nearby_exits) == 1:
                print("[EXIT_SELECT] ignored; only one nearby exit")
                self._mark_input_handled()
                return True

        force_scene = self.FORCE_SCENE_KEYS.get(event.key)
        if force_scene is not None:
            self._force_load_scene(force_scene, "[Debug]")
            return True

        if event.key in self.CONFIRM_KEYS:
            return self._handle_interact_key("[Input]", self._confirm_key_name(event.key))

        return False

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill((32, 36, 38))

        if self.tile_map is None or self.camera is None or self.player is None:
            self._draw_error(surface)
            return

        world_surface = pygame.Surface(surface.get_size())
        world_surface.fill((32, 36, 38))

        self.tile_map.draw(world_surface, self.camera)
        self._draw_purify_effect(world_surface)
        self.market_collect_manager.draw(world_surface, self.camera)
        self.festival_defense_manager.draw_ground(world_surface, self.camera)
        for interactable in self.interactables:
            interactable.draw(world_surface, self.camera, self.debug_font)
        for shadow in self.shadow_spirits:
            shadow.draw(world_surface, self.camera)
        self.festival_defense_manager.draw_entities(world_surface, self.camera)
        for npc in self.npcs:
            npc.draw(world_surface, self.camera)
        self.player.draw(world_surface, self.camera)
        self._draw_player_hit_feedback(world_surface)
        if DEBUG_COLLISION:
            self.tile_map.draw_collision_debug(world_surface, self.camera)
            self.player.draw_collision_debug(world_surface, self.camera)

        self.combat_effect_manager.draw(world_surface, self.camera, self.shadow_spirits)
        shake_offset = self.combat_effect_manager.get_shake_offset()
        surface.blit(world_surface, shake_offset)

        if self.active_npc is None and not self._is_ending_panel_open():
            target_id, target_pos = self._quest_arrow_target()
            self.quest_arrow.draw(
                surface,
                self.camera,
                self.main_quest_manager.stage,
                target_id,
                target_pos,
            )

        if self.active_npc is None and self.nearby_npc is not None:
            self._draw_interaction_prompt(surface)
        elif self.nearby_exit is not None:
            self._draw_enter_prompt(surface)

        self._draw_status_message(surface)
        self._draw_quest_lock_toast(surface)
        if self.active_npc is None and self.shadow_chase_manager.should_show_hud():
            self.shadow_hud.draw(surface, self.shadow_chase_manager)
        if self.active_npc is None:
            self.festival_defense_manager.draw_hud(surface)
        if self.active_npc is None:
            self._draw_objective_hud(surface)
        if self.active_npc is None:
            market_prompt = self.market_collect_manager.nearby_prompt_object()
            panel_exits = [] if market_prompt is not None else self.nearby_exits
            panel_selected_exit = None if market_prompt is not None else self.nearby_exit
            self.navigation_panel.draw(
                surface,
                self.current_scene_name,
                panel_exits,
                panel_selected_exit,
                self.nearby_npc,
                market_prompt or self.nearby_item,
            )
        if self.active_npc is None:
            self.simple_inventory_panel.draw(
                surface,
                self.main_quest_manager,
                player_light=self._current_player_light_for_panel(),
                max_player_light=self._current_max_player_light_for_panel(),
            )
        self._draw_debug_overlay(surface)
        if (
            self.active_npc is None
            and self.main_quest_manager.stage == "ending"
            and not self.ending_panel_dismissed
        ):
            self.ending_panel.draw(
                surface,
                self.main_quest_manager,
                stand_light=self.festival_defense_manager.stand_light,
                max_stand_light=self.festival_defense_manager.MAX_STAND_LIGHT,
                player_light=self._current_player_light_for_panel() or 0,
                max_player_light=self._current_max_player_light_for_panel() or 3,
            )
        if self.active_npc is not None:
            speaker, text = self.dialogue_manager.current()
            signature = (self.active_npc.id, text)
            if signature != self._last_dialogue_box_signature:
                print(f"[DIALOGUE_BOX] draw npc_id={self.active_npc.id} text={text}")
                self._last_dialogue_box_signature = signature
            self.dialogue_box.draw(surface, speaker, text)
        self.scene_transition.draw(surface)

    def _handle_fallback_input(self) -> None:
        if self.scene_transition.is_blocking_input():
            self._remember_current_key_state()
            return
        if self._is_ending_panel_open():
            self._remember_current_key_state()
            return
        if self._input_on_cooldown():
            self._remember_current_key_state()
            return

        for key, index in self.EXIT_SELECTION_KEYS.items():
            pressed = pygame.key.get_pressed()[key]
            if pressed and not self._prev_keys.get(key, False):
                if len(self.nearby_exits) > 1:
                    self._select_nearby_exit_by_index(index, "[FallbackInput]")
                    self._remember_current_key_state()
                    return
                if len(self.nearby_exits) == 1:
                    print("[EXIT_SELECT] ignored; only one nearby exit")
                    self._mark_input_handled()
                    self._remember_current_key_state()
                    return

        for key, scene_name in self.FORCE_SCENE_KEYS.items():
            pressed = pygame.key.get_pressed()[key]
            if pressed and not self._prev_keys.get(key, False):
                self._force_load_scene(scene_name, "[FallbackInput]")
                self._remember_current_key_state()
                return

        confirm_key = self._pressed_confirm_key()
        if confirm_key is not None and not self._prev_keys.get(confirm_key, False):
            if self.active_npc is not None:
                self._advance_dialogue("[FallbackInput]")
                self._mark_input_handled()
                self._remember_current_key_state()
                return
            else:
                self._handle_interact_key("[FallbackInput]", self._confirm_key_name(confirm_key))

        self._remember_current_key_state()

    def _remember_current_key_state(self) -> None:
        keys = pygame.key.get_pressed()
        for key in (*self.FORCE_SCENE_KEYS.keys(), *self.CONFIRM_KEYS, pygame.K_SPACE, pygame.K_ESCAPE):
            self._prev_keys[key] = keys[key]

    def _pressed_confirm_key(self) -> int | None:
        keys = pygame.key.get_pressed()
        for key in self.CONFIRM_KEYS:
            if keys[key]:
                return key
        return None

    def _confirm_key_name(self, key: int) -> str:
        if key == pygame.K_RETURN:
            return "return"
        if key == pygame.K_e:
            return "e"
        return pygame.key.name(key)

    def _current_player_light_for_panel(self) -> int | None:
        if self.current_scene_name in {"river_valley", "mountain"}:
            return self.shadow_chase_manager.player_light
        return getattr(self.main_quest_manager, "player_light", None)

    def _current_max_player_light_for_panel(self) -> int | None:
        if self.current_scene_name in {"river_valley", "mountain"}:
            return self.shadow_chase_manager.PLAYER_MAX_LIGHT
        return getattr(self.main_quest_manager, "max_player_light", None)

    def _handle_exit_selection_key(self, key: int, source: str) -> bool:
        index = self.EXIT_SELECTION_KEYS[key]
        return self._select_nearby_exit_by_index(index, source)

    def _select_nearby_exit_by_index(self, index: int, source: str) -> bool:
        self._update_nearby_exit()
        if index >= len(self.nearby_exits):
            print(f"[EXIT_SELECT] {source} index={index + 1} ignored; candidates={len(self.nearby_exits)}")
            self._mark_input_handled()
            return True

        selected_exit = self.nearby_exits[index]
        self.manual_exit_index = index
        self.selected_exit_id = str(selected_exit.get("id"))
        self.manual_selected_exit_id = self.selected_exit_id
        self.manual_exit_selection_active = True
        self.nearby_exit = selected_exit
        print(
            f"[EXIT_SELECT] manual index={index + 1} selected_exit={self.selected_exit_id} "
            f"target_scene={selected_exit.get('target_scene')} "
            f"target_spawn={selected_exit.get('target_spawn') or '(none)'}"
        )
        self._mark_input_handled()
        return True

    def _force_load_scene(self, scene_name: str, source: str) -> bool:
        if self.scene_transition.is_active():
            self._mark_input_handled()
            return True
        self.debug_skip_mode = True
        self._set_status_message(DEBUG_SKIP_NOTICE)
        print(
            f"[SCENE][DEBUG forced scene change] "
            f"from={self.current_scene_name or '(none)'} to={scene_name} source={source}"
        )
        def switch_scene() -> None:
            loaded = self.load_scene(scene_name)
            print(f"[Scene] debug load_scene returned: {loaded}")

        self.scene_transition.start(switch_scene, target_scene=scene_name)
        self._mark_input_handled()
        return True

    def _handle_interact_key(self, source: str, confirm_key: str = "e") -> bool:
        print(f"[INTERACT] confirm_key={confirm_key}")
        realtime_npc = self._find_nearest_npc_for_interaction()
        self.nearby_npc = realtime_npc
        self._update_nearby_exit()
        self._update_nearby_item()

        nearby_npc_id = realtime_npc.id if realtime_npc is not None else "None"
        nearby_exit_id = self.nearby_exit.get("id") if self.nearby_exit is not None else "None"
        nearby_item_id = self.nearby_item.id if self.nearby_item is not None else "None"
        print(
            f"[INTERACT] realtime_nearby_npc={nearby_npc_id} "
            f"nearby_exit={nearby_exit_id} nearby_item={nearby_item_id}"
        )

        if realtime_npc is not None:
            self._start_dialogue(realtime_npc, source, confirm_key)
            self._mark_input_handled()
            return True

        if self.market_collect_manager.handle_confirm(self.main_quest_manager):
            self._mark_input_handled()
            return True

        if self.nearby_exit is not None:
            print(
                "[EXIT] "
                f"id/type/target_scene/target_spawn = "
                f"{self.nearby_exit.get('id')}/"
                f"{self.nearby_exit.get('type')}/"
                f"{self.nearby_exit.get('target_scene')}/"
                f"{self.nearby_exit.get('target_spawn') or '(none)'}"
            )
            print(
                f"[Scene] confirm on exit: {self.nearby_exit['id']} -> "
                f"{self.nearby_exit['target_scene']}"
            )
            self._enter_scene_exit(self.nearby_exit, confirm_key)
            self._mark_input_handled()
            return True

        if self.nearby_item is not None:
            print(f"[INTERACT] nearby_item={self.nearby_item.id} no pickup handler registered")
            self._mark_input_handled()
            return True

        if self.nearby_exits:
            print(
                "[EXIT][AMBIGUOUS] confirm ignored because no stable selected_exit exists. "
                f"candidates=[{', '.join(self._format_exit_candidate_for_log(item) for item in self.nearby_exits)}]"
            )
            self._mark_input_handled()
            return True

        self._update_nearby_shadow()
        if self.nearby_shadow is not None:
            if self.nearby_shadow.interact(self.player, self.inventory, self.task_manager, self.score_manager):
                self._set_status_message("Shadow reward already claimed")
            self._mark_input_handled()
            return True

        if self.nearby_shadow_trigger is not None:
            self._start_shadow_chase()
            self._mark_input_handled()
            return True

        print("[INTERACT] no nearby object")
        self._mark_input_handled()
        return False

    def _start_dialogue(self, npc: NPC, source: str, confirm_key: str = "e") -> None:
        self._play_sfx("ui_confirm")
        self.active_npc = npc
        self._last_dialogue_box_signature = None
        speaker, text = self.dialogue_manager.start(npc.id, npc.name, npc.dialogue)
        npc.name = speaker
        lines_count = len(self.dialogue_manager.active_lines)
        print(
            f"[DIALOGUE] start npc_id={npc.id} name={speaker} "
            f"lines={lines_count} confirm_key={confirm_key}"
        )
        if self.dialogue_manager.last_missing_dialogue:
            print(f"[DIALOGUE][WARN] missing dialogue npc_id={npc.id} fallback=ellipsis")
        print(f"[DIALOGUE] current text={text}")
        self._play_current_dialogue_voice()

    def _advance_dialogue(self, source: str) -> None:
        if self.active_npc is None:
            return

        self._play_sfx("ui_confirm")
        npc_id = self.active_npc.id
        if self.dialogue_manager.next():
            self.audio_manager.stop_voice()
            _, text = self.dialogue_manager.current()
            print(
                f"[DIALOGUE] next source={source} npc_id={npc_id} "
                f"line={self.dialogue_manager.active_index + 1}/"
                f"{len(self.dialogue_manager.active_lines)} text={text}"
            )
            self._play_current_dialogue_voice()
            return

        self._close_dialogue(source, finished=True)

    def _close_dialogue(self, source: str, finished: bool) -> None:
        self.audio_manager.stop_voice()
        if self.active_npc is None:
            self.dialogue_manager.close()
            return

        npc_id = self.active_npc.id
        self.active_npc = None
        self._last_dialogue_box_signature = None
        self.dialogue_manager.close()
        print(f"[DIALOGUE] close source={source} npc_id={npc_id} finished={finished}")
        if finished:
            self.on_dialogue_finished(npc_id)

    def on_dialogue_finished(self, npc_id: str) -> None:
        print(f"[DIALOGUE] finished npc_id={npc_id}")
        if npc_id == "elder":
            self.elder_dialogue_finished = True
            if self.main_quest_manager.stage == "intro":
                self.main_quest_manager.advance_to("go_market")

    def _play_current_dialogue_voice(self) -> None:
        if self.active_npc is None:
            return
        voice_path = self.dialogue_manager.current_voice()
        if voice_path:
            self.audio_manager.play_voice(voice_path)

    def on_shadow_defeated(self, reward_id: str) -> None:
        print(f"[SHADOW] reward hook reward={reward_id}")
        self.main_quest_manager.add_item(reward_id or "mountain_pattern_clue")
        self.main_quest_manager.complete_level("shadow_challenge")
        if self.main_quest_manager.stage == "shadow_challenge":
            self.main_quest_manager.advance_to("go_festival")

    def _restart_main_quest(self) -> None:
        print("[ENDING] restart game")
        if self.scene_transition.is_active():
            return

        def restart() -> None:
            self.main_quest_manager = MainQuestManager()
            self.elder_dialogue_finished = False
            self.debug_skip_mode = False
            self.ending_panel_dismissed = True
            self.market_collect_manager.active = False
            self.festival_defense_manager.active = False
            self.shadow_chase_manager.configure("", [])
            loaded = self.load_scene(DEFAULT_SCENE, "start")
            print(f"[Scene] ending restart load_scene returned: {loaded}")

        self.scene_transition.start(restart, target_scene=DEFAULT_SCENE, target_spawn="start")

    def _is_ending_panel_open(self) -> bool:
        return (
            self.active_npc is None
            and self.main_quest_manager.stage == "ending"
            and not self.ending_panel_dismissed
        )

    def _handle_ending_panel_key(self, key: int) -> bool:
        if key == pygame.K_RETURN:
            self.ending_panel_dismissed = True
            self._play_sfx("ui_confirm")
            print("[ENDING] close panel by enter")
            self._mark_input_handled()
            return True
        if key == pygame.K_ESCAPE:
            self.ending_panel_dismissed = True
            self._play_sfx("ui_confirm")
            print("[ENDING] close panel by esc")
            self._mark_input_handled()
            return True
        if key == pygame.K_r:
            self._play_sfx("ui_confirm")
            self._restart_main_quest()
            self._mark_input_handled()
            return True
        self._mark_input_handled()
        return True

    def _draw_objective_hud(self, surface: pygame.Surface) -> None:
        title, hint, extra = self._current_objective_text()
        self.objective_hud.draw(surface, title, hint, extra, avoid_debug=self.debug_overlay_visible)

    def _quest_arrow_target(self) -> tuple[str | None, tuple[int, int] | None]:
        stage = self.main_quest_manager.stage
        if stage == "ending":
            return None, None
        if stage == "intro":
            return self._quest_arrow_npc_target("elder")
        if stage == "go_market":
            return self._quest_arrow_exit_target("exit_to_village_market", "market")
        if stage == "market_collect":
            return self._quest_arrow_market_collect_target()
        if stage == "go_river":
            return self._quest_arrow_exit_target("exit_to_river_valley", "mountain")
        if stage == "shadow_challenge":
            return self._quest_arrow_shadow_target()
        if stage == "go_festival":
            return self._quest_arrow_exit_target("exit_to_festival", "festival")
        if stage == "festival_defense":
            return self._quest_arrow_festival_target()
        return None, None

    def _quest_arrow_npc_target(self, npc_id: str) -> tuple[str | None, tuple[int, int] | None]:
        for npc in self.npcs:
            if npc.id == npc_id:
                return npc_id, npc.rect.midtop
        return None, None

    def _quest_arrow_exit_target(
        self,
        exit_id: str,
        target_scene: str,
    ) -> tuple[str | None, tuple[int, int] | None]:
        if self.tile_map is None:
            return None, None
        for scene_exit in self.tile_map.scene_exits:
            raw_target = str(scene_exit.get("target_scene") or "")
            canonical_target = self.scene_registry.canonical_name(raw_target)
            if scene_exit.get("id") == exit_id or canonical_target == target_scene:
                rect = scene_exit.get("rect")
                if isinstance(rect, pygame.Rect):
                    return str(scene_exit.get("id") or exit_id), rect.center
        if self.current_scene_name != "village":
            for scene_exit in self.tile_map.scene_exits:
                raw_target = str(scene_exit.get("target_scene") or "")
                if self.scene_registry.canonical_name(raw_target) == "village":
                    rect = scene_exit.get("rect")
                    if isinstance(rect, pygame.Rect):
                        return str(scene_exit.get("id") or "return_to_village"), rect.center
        return None, None

    def _quest_arrow_market_collect_target(self) -> tuple[str | None, tuple[int, int] | None]:
        if self.player is None:
            return None, None
        candidates = [
            point for point in self.market_collect_manager.points
            if not point.collected
        ]
        if not candidates:
            return None, None
        player_center = pygame.math.Vector2(self.player.rect.center)
        point = min(candidates, key=lambda item: player_center.distance_to(item.rect.center))
        return point.item_id, point.rect.midtop

    def _quest_arrow_shadow_target(self) -> tuple[str | None, tuple[int, int] | None]:
        available = [
            shadow for shadow in self.shadow_spirits
            if shadow.state != ShadowSpirit.DEFEATED
        ]
        if not available:
            return None, None
        if self.player is not None:
            player_center = pygame.math.Vector2(self.player.rect.center)
            shadow = min(available, key=lambda item: player_center.distance_to(item.rect.center))
        else:
            shadow = available[0]
        return shadow.shadow_id, shadow.rect.midtop

    def _quest_arrow_festival_target(self) -> tuple[str | None, tuple[int, int] | None]:
        if self.festival_defense_manager.shadows:
            if self.player is not None:
                player_center = pygame.math.Vector2(self.player.rect.center)
                shadow = min(
                    self.festival_defense_manager.shadows,
                    key=lambda item: player_center.distance_to(item.rect.center),
                )
            else:
                shadow = self.festival_defense_manager.shadows[0]
            return "festival_shadow", shadow.rect.midtop
        if self.festival_defense_manager.active:
            return "festival_altar", self.festival_defense_manager.stand_rect.center
        return None, None

    def _current_objective_text(self) -> tuple[str, str, str]:
        title, hint = self.main_quest_manager.get_objective()
        extra = ""
        if (
            self.current_scene_name in {"river_valley", "mountain"}
            and self.main_quest_manager.stage == "shadow_challenge"
            and pygame.time.get_ticks() < self.shadow_intro_until
        ):
            extra = OBJ_SHADOW_INTRO
        if self.debug_skip_mode and self.main_quest_manager.stage != "ending":
            extra = DEBUG_SKIP_NOTICE if not extra else f"{extra} / {DEBUG_SKIP_NOTICE}"
        return title, hint, extra

    def _sync_main_quest_for_scene(self) -> None:
        if self.main_quest_manager.stage == "ending":
            return
        if self.current_scene_name in {"village_market", "market"}:
            if self.main_quest_manager.stage == "go_market":
                self.main_quest_manager.advance_to("market_collect")
        elif self.current_scene_name in {"river_valley", "mountain"}:
            if self.main_quest_manager.stage == "go_river":
                self.main_quest_manager.advance_to("shadow_challenge")
        elif self.current_scene_name in {"festival", "festival_square", "festival_plaza"}:
            if self.main_quest_manager.stage == "go_festival":
                self.main_quest_manager.advance_to("festival_defense")
            elif (
                self.debug_skip_mode
                and
                self.main_quest_manager.stage not in {"festival_defense", "ending"}
                and "festival_defense" not in self.main_quest_manager.get_completed_levels()
            ):
                print("[FESTIVAL][DEMO] start festival_defense without full quest progress")
                self.main_quest_manager.advance_to("festival_defense")

    def _configure_level_managers_for_current_scene(self) -> None:
        if self.tile_map is None or self.player is None:
            return
        self.market_collect_manager.configure(
            self.current_scene_name,
            self.tile_map,
            self.player,
            self.main_quest_manager,
        )
        self.festival_defense_manager.configure(
            self.current_scene_name,
            self.tile_map,
            self.player,
            self.main_quest_manager,
        )

    def _play_sfx(self, name: str) -> None:
        self.audio_manager.play_sfx(name)

    def _update_scene_bgm(self) -> None:
        bgm_path = self._bgm_for_scene()
        if bgm_path:
            self.audio_manager.play_bgm(bgm_path)

    def _bgm_for_scene(self) -> str:
        if self.main_quest_manager.stage == "ending":
            return "assets/audio/bgm/festival.wav"
        if self.current_scene_name in {"river_valley", "mountain"}:
            return "assets/audio/bgm/battle.wav"
        if self.current_scene_name in {"festival", "festival_square", "festival_plaza"}:
            return "assets/audio/bgm/festival.wav"
        if self.current_scene_name in {"village", "village_hub", "village_market", "market"}:
            return "assets/audio/bgm/village.wav"
        return ""

    def _ensure_festival_host(self) -> None:
        if self.current_scene_name not in {"festival", "festival_square", "festival_plaza"}:
            return
        existing = next((npc for npc in self.npcs if npc.id == "festival_host"), None)
        if existing is not None:
            print("[FESTIVAL] host spawned fallback=False")
            return
        if self.player is None:
            return

        host_x = self.player.rect.centerx + 260
        host_y = self.player.rect.centery + 120
        if self.tile_map is not None:
            host_x = min(max(host_x, 64), max(64, self.tile_map.drawable_width - 64))
            host_y = min(max(host_y, 64), max(64, self.tile_map.drawable_height - 64))
        self.npcs.append(
            NPC(
                "festival_host",
                "\u8282\u5e86\u4e3b\u6301\u4eba",
                "",
                host_x,
                host_y,
                "festival_host_idle",
                "festival_host",
            )
        )
        print("[FESTIVAL] host spawned fallback=True")

    def _is_playable_npc_record(self, data: dict) -> bool:
        npc_id = str(data.get("id", "")).strip().lower()
        if npc_id == "shadow_spirit":
            return False
        if npc_id.startswith("exit_to_"):
            print(f"[NPC][WARN] skipped misplaced exit object in npc layer: {npc_id}")
            return False
        generated_empty_npc = (
            npc_id.startswith("npc_")
            and not str(data.get("sprite", "")).strip()
            and not str(data.get("character", "")).strip()
        )
        if generated_empty_npc:
            print(f"[NPC][WARN] skipped empty npc placeholder: {npc_id}")
            return False
        return True

    def _print_festival_route_status(self, tile_map: TileMap) -> None:
        if self.current_scene_name in {"village", "village_hub"}:
            found = any(str(item.get("id")) == "exit_to_festival" for item in tile_map.scene_exits)
            print(f"[FESTIVAL] exit_to_festival found={found}")
        elif self.current_scene_name in {"festival", "festival_square", "festival_plaza"}:
            spawn_found = "from_village_hub" in tile_map.spawn_points
            return_exit_found = any(str(item.get("id")) == "exit_to_village_hub" for item in tile_map.scene_exits)
            print(f"[FESTIVAL] spawn from_village_hub found={spawn_found}")
            print(f"[FESTIVAL] return exit found={return_exit_found}")

    def _place_shadows_for_demo(self, tile_map: TileMap) -> None:
        if self.player is None or self.current_scene_name not in {"river_valley", "mountain"}:
            return
        if not self.shadow_spirits:
            return

        for index, shadow in enumerate(self.shadow_spirits):
            desired_center = (
                self.player.rect.centerx + 180,
                self.player.rect.centery + 80 + index * 48,
            )
            center_x, center_y = self._find_safe_shadow_center(tile_map, shadow.rect, desired_center)
            self._move_shadow_to(shadow, center_x, center_y, reset_state=True)
            print(f"[SHADOW][DEMO] spawn near player pos=({center_x},{center_y})")

    def _debug_teleport_shadow_near_player(self) -> bool:
        if self.player is None or self.tile_map is None or not self.shadow_spirits:
            return False

        shadow = next(
            (item for item in self.shadow_spirits if item.state != ShadowSpirit.DEFEATED),
            self.shadow_spirits[0],
        )
        desired_center = (self.player.rect.centerx + 180, self.player.rect.centery + 80)
        center_x, center_y = self._find_safe_shadow_center(self.tile_map, shadow.rect, desired_center)
        self._move_shadow_to(shadow, center_x, center_y, reset_state=True)
        self.shadow_chase_manager.configure(self.current_scene_name, self.shadow_spirits)
        print(f"[SHADOW][DEBUG] teleport near player pos=({center_x},{center_y})")
        return True

    def _move_shadow_to(self, shadow: ShadowSpirit, center_x: int, center_y: int, reset_state: bool) -> None:
        shadow.world_x = float(center_x)
        shadow.world_y = float(center_y)
        shadow.start_position = (float(center_x), float(center_y))
        shadow.rect.center = (center_x, center_y)
        if reset_state:
            shadow.hp = shadow.max_hp
            shadow.state = ShadowSpirit.IDLE
            shadow.has_reward_given = False

    def _find_safe_shadow_center(
        self,
        tile_map: TileMap,
        shadow_rect: pygame.Rect,
        desired_center: tuple[int, int],
    ) -> tuple[int, int]:
        map_rect = pygame.Rect(0, 0, tile_map.drawable_width, tile_map.drawable_height)

        def candidate_rect(center_x: int, center_y: int) -> pygame.Rect:
            rect = shadow_rect.copy()
            rect.center = (center_x, center_y)
            rect.clamp_ip(map_rect)
            return rect

        base_rect = candidate_rect(*desired_center)
        if base_rect.collidelist(tile_map.collision_rects) == -1:
            return base_rect.center

        offsets = (
            (0, 0),
            (40, 0),
            (-40, 0),
            (0, 40),
            (0, -40),
            (40, 40),
            (-40, 40),
            (40, -40),
            (-40, -40),
            (80, 0),
            (-80, 0),
            (0, 80),
            (0, -80),
            (120, 0),
            (0, 120),
        )
        for offset_x, offset_y in offsets:
            rect = candidate_rect(desired_center[0] + offset_x, desired_center[1] + offset_y)
            if rect.collidelist(tile_map.collision_rects) == -1:
                return rect.center

        print("[SHADOW][WARN] no nearby safe shadow spawn found; using clamped demo position")
        return base_rect.center

    def _format_exit_for_log(self, scene_exit: dict | None) -> str:
        if scene_exit is None:
            return "None"
        distance = scene_exit.get("_distance")
        distance_text = f" distance={distance:.1f}" if isinstance(distance, (int, float)) else ""
        return (
            f"{scene_exit.get('id')} type={scene_exit.get('type')} "
            f"target_scene={scene_exit.get('target_scene')} "
            f"target_spawn={scene_exit.get('target_spawn') or '(none)'}"
            f"{distance_text}"
        )

    def _load_shadow_chase_objects(self, tile_map: TileMap, scene_name: str) -> None:
        self.shadow_spirits = []
        self.shadow_triggers = []

        route_points_by_group: dict[str, list[tuple[int, tuple[int, int]]]] = {}
        spawn_records = []
        for record in tile_map.object_records:
            if record.type == "shadow_route_point":
                group = str(record.properties.get("route_group", "default_shadow_route"))
                order = int(record.properties.get("order", len(route_points_by_group.get(group, [])) + 1))
                route_points_by_group.setdefault(group, []).append((order, record.rect.center))
            elif record.type == "shadow_spirit_spawn":
                spawn_records.append(record)
            elif record.type == "npc" and record.id.strip().lower() == "shadow_spirit":
                spawn_records.append(record)
            elif record.type == "shadow_fragment_trigger":
                self.shadow_triggers.append(record.rect.copy())

        for record in spawn_records:
            group = str(record.properties.get("route_group", "default_shadow_route"))
            route_points = [
                point for _, point in sorted(route_points_by_group.get(group, []), key=lambda item: item[0])
            ]
            shadow = ShadowSpirit(
                shadow_id=str(record.properties.get("shadow_id", record.id)),
                world_x=record.rect.centerx,
                world_y=record.rect.centery,
                route_points=route_points,
                carried_item_id=str(record.properties.get("carried_item_id", "key_silver_fragment")),
                reward_item_id=str(record.properties.get("reward_item_id", "mountain_pattern_clue")),
            )
            self.shadow_spirits.append(shadow)
            print(f"[SHADOW] spawned scene={scene_name} pos=({shadow.rect.centerx},{shadow.rect.centery})")

        for data in tile_map.npc_data:
            if str(data.get("id", "")).strip().lower() != "shadow_spirit":
                continue
            shadow = ShadowSpirit(
                shadow_id=str(data.get("id", "shadow_spirit")),
                world_x=int(data.get("world_x", 0)),
                world_y=int(data.get("world_y", 0)),
                reward_item_id="mountain_pattern_clue",
            )
            self.shadow_spirits.append(shadow)
            print(f"[SHADOW] spawned scene={scene_name} pos=({shadow.rect.centerx},{shadow.rect.centery})")

        if scene_name in {"mountain", "river_valley"} and not self.shadow_spirits:
            self._create_default_shadow_chase(tile_map)

    def _create_default_shadow_chase(self, tile_map: TileMap) -> None:
        if self.player is not None:
            start_x = self.player.rect.centerx + 180
            start_y = self.player.rect.centery + 80
        else:
            start_x = 420
            start_y = 260
        start_x = min(max(start_x, 64), max(64, tile_map.drawable_width - 64))
        start_y = min(max(start_y, 64), max(64, tile_map.drawable_height - 64))
        route_points = [
            (min(start_x + 140, tile_map.drawable_width - 40), start_y),
            (min(start_x + 240, tile_map.drawable_width - 40), min(start_y + 100, tile_map.drawable_height - 40)),
            (min(start_x + 80, tile_map.drawable_width - 40), min(start_y + 180, tile_map.drawable_height - 40)),
        ]
        self.shadow_spirits.append(
            ShadowSpirit(
                "shadow_spirit_debug",
                start_x,
                start_y,
                route_points=route_points,
            )
        )
        print("[SHADOW][WARN] no shadow_spirit object found; created default test shadow")
        print(f"[SHADOW] spawned scene={self.current_scene_name or 'loading'} pos=({start_x},{start_y})")
        print("[SHADOW][WARN] default test shadow chase created")

    def _start_shadow_chase(self) -> None:
        if self._shadow_reward_already_claimed():
            self._set_status_message("Shadow reward already claimed")
            return

        available_shadow = next(
            (shadow for shadow in self.shadow_spirits if shadow.state in {ShadowSpirit.IDLE, ShadowSpirit.APPEAR}),
            None,
        )
        if available_shadow is None:
            self._set_status_message("Shadow is still chasing")
            return

        available_shadow.start_flee()
        self.task_manager.start_shadow_chase()
        self._set_status_message("Shadow chase started")

    def _shadow_reward_already_claimed(self) -> bool:
        return (
            self.inventory.has("purified_silver_fragment")
            or self.task_manager.is_completed("main_shadow_chase")
        )

    def _update_nearby_shadow(self) -> None:
        self.nearby_shadow = None
        self.nearby_shadow_trigger = None

    def _mark_input_handled(self) -> None:
        self.input_cooldown_until = pygame.time.get_ticks() + self.INPUT_COOLDOWN_MS

    def _input_on_cooldown(self) -> bool:
        return pygame.time.get_ticks() < self.input_cooldown_until

    def _resolve_spawn_position(self, tile_map: TileMap, spawn_id: str | None) -> tuple[int, int]:
        if spawn_id:
            return self._resolve_named_spawn(tile_map, spawn_id, "target_spawn")

        default_spawn_id = self._get_default_spawn_id(tile_map)
        if default_spawn_id is not None:
            return self._resolve_named_spawn(tile_map, default_spawn_id, "default_spawn")

        print("[Scene] 鏈壘鍒?spawn 鐐癸紝浣跨敤榛樿瀹夊叏鍑虹敓鐐归€昏緫")
        return self._find_safe_spawn(tile_map)

    def _get_default_spawn_id(self, tile_map: TileMap) -> str | None:
        if "start" in tile_map.spawn_points:
            print("[Scene] 鎵惧埌 spawn 鐐? start")
            return "start"

        if tile_map.spawn_order:
            spawn_id = tile_map.spawn_order[0]
            print(f"[Scene] 鏈壘鍒?spawn_id=start锛屼娇鐢ㄧ涓€涓?spawn 鐐? {spawn_id}")
            return spawn_id

        return None

    def _resolve_named_spawn(self, tile_map: TileMap, spawn_id: str, reason: str) -> tuple[int, int]:
        spawn_position = tile_map.spawn_points.get(spawn_id)
        if spawn_position is None:
            print(f"[SPAWN] target_spawn found = False, id = {spawn_id}, reason = {reason}")
            print(f"[ERROR] target_spawn not found: {spawn_id}")
            return self._find_safe_spawn(tile_map)

        x, y = spawn_position
        print(f"[SPAWN] target_spawn found = True, id = {spawn_id}, position = ({x}, {y}), reason = {reason}")
        spawn_rect = pygame.Rect(x, y, 32, 32)
        spawn_rect.clamp_ip(pygame.Rect(0, 0, tile_map.drawable_width, tile_map.drawable_height))
        if spawn_rect.collidelist(tile_map.collision_rects) == -1:
            print(f"[SPAWN] player position = ({spawn_rect.x}, {spawn_rect.y})")
            return spawn_rect.x, spawn_rect.y

        print(f"[Scene] spawn 鐐逛綅浜?collision 鍐咃紝鏀圭敤瀹夊叏鍑虹敓鐐? id={spawn_id}")
        return self._find_safe_spawn(tile_map)

    def _find_safe_spawn(self, tile_map: TileMap) -> tuple[int, int]:
        start_x = tile_map.tile_width * 5
        start_y = tile_map.tile_height * 5
        player_size = 32
        start_rect = pygame.Rect(start_x, start_y, player_size, player_size)
        if start_rect.collidelist(tile_map.collision_rects) == -1:
            print(f"[SPAWN] player position = ({start_x}, {start_y}) fallback=default")
            return start_x, start_y

        for y in range(0, max(1, tile_map.drawable_height - player_size + 1), tile_map.tile_height):
            for x in range(0, max(1, tile_map.drawable_width - player_size + 1), tile_map.tile_width):
                rect = pygame.Rect(x, y, player_size, player_size)
                if rect.collidelist(tile_map.collision_rects) == -1:
                    print(f"[SPAWN] player position = ({x}, {y}) fallback=safe_scan")
                    return x, y

        print("[SPAWN][WARN] no safe spawn found; using unsafe default")
        print(f"[SPAWN] player position = ({start_x}, {start_y}) fallback=unsafe_default")
        return start_x, start_y

    def _resolve_spawn_position(self, tile_map: TileMap, spawn_id: str | None) -> tuple[int, int]:
        requested_spawn_id = spawn_id or "start"
        reason = "target_spawn" if spawn_id else "default_start"
        print(f"[SPAWN] request scene={self.current_scene_name or '(loading)'} spawn_id={requested_spawn_id}")

        if requested_spawn_id in tile_map.spawn_points:
            return self._resolve_named_spawn(tile_map, requested_spawn_id, reason, requested_spawn_id)

        if requested_spawn_id != "start":
            fallback_position = self._find_spawn_near_matching_exit(tile_map, requested_spawn_id)
            if fallback_position is not None:
                return fallback_position

        fallback_spawn_id = self._find_fallback_spawn_id(tile_map, requested_spawn_id)
        if fallback_spawn_id is not None:
            print(
                f"[SPAWN][WARN] missing spawn_id={requested_spawn_id}; "
                f"fallback_spawn={fallback_spawn_id}"
            )
            return self._resolve_named_spawn(
                tile_map,
                fallback_spawn_id,
                f"fallback_missing_{requested_spawn_id}",
                requested_spawn_id,
            )

        print(
            f"[SPAWN][WARN] missing spawn_id={requested_spawn_id}; "
            "no spawn objects found; fallback_spawn=safe_scan_default"
        )
        return self._find_safe_spawn(
            tile_map,
            origin=None,
            requested_spawn_id=requested_spawn_id,
            fallback_spawn_id="safe_scan_default",
            reason="no_spawn_objects",
        )

    def _find_fallback_spawn_id(self, tile_map: TileMap, requested_spawn_id: str) -> str | None:
        if requested_spawn_id != "start" and "start" in tile_map.spawn_points:
            return "start"

        for candidate_spawn_id in tile_map.spawn_order:
            if candidate_spawn_id in tile_map.spawn_points:
                return candidate_spawn_id

        return None

    def _resolve_named_spawn(
        self,
        tile_map: TileMap,
        spawn_id: str,
        reason: str,
        requested_spawn_id: str,
    ) -> tuple[int, int]:
        spawn_position = tile_map.spawn_points.get(spawn_id)
        if spawn_position is None:
            print(f"[SPAWN][WARN] spawn record disappeared: id={spawn_id}, reason={reason}")
            return self._find_safe_spawn(
                tile_map,
                origin=None,
                requested_spawn_id=requested_spawn_id,
                fallback_spawn_id="safe_scan_default",
                reason=f"{reason}_missing_record",
            )

        spawn_rect = self._make_player_spawn_rect(tile_map, spawn_id, spawn_position)
        print(
            f"[SPAWN] found spawn_id={spawn_id}, requested={requested_spawn_id}, "
            f"candidate=({spawn_rect.x}, {spawn_rect.y}), reason={reason}"
        )

        if self._is_spawn_rect_safe(spawn_rect, tile_map):
            print(
                f"[SPAWN] final spawn_id={spawn_id}, requested={requested_spawn_id}, "
                f"player position=({spawn_rect.x}, {spawn_rect.y}), fallback=none"
            )
            print(
                f"[SPAWN] scene={self._map_scene_label(tile_map)} "
                f"spawn_id={spawn_id} pos=({spawn_rect.x},{spawn_rect.y})"
            )
            return spawn_rect.x, spawn_rect.y

        print(
            f"[SPAWN][WARN] spawn_id={spawn_id} is inside collision; "
            "searching nearest safe position"
        )
        return self._find_safe_spawn(
            tile_map,
            origin=spawn_rect.topleft,
            requested_spawn_id=requested_spawn_id,
            fallback_spawn_id=spawn_id,
            reason=f"{reason}_collision",
        )

    def _find_spawn_near_matching_exit(
        self,
        tile_map: TileMap,
        requested_spawn_id: str,
    ) -> tuple[int, int] | None:
        exit_id_by_spawn = {
            "from_village_market": "exit_to_village_market",
            "from_river_valley": "exit_to_river_valley",
            "from_workshop_exterior": "exit_to_workshop_exterior",
            "from_festival": "exit_to_festival",
        }
        expected_exit_id = exit_id_by_spawn.get(requested_spawn_id)
        if expected_exit_id is None:
            return None

        scene_exit = next(
            (item for item in tile_map.scene_exits if str(item.get("id")) == expected_exit_id),
            None,
        )
        if scene_exit is None:
            return None

        exit_rect = scene_exit["rect"]
        origin = (exit_rect.centerx - 16, exit_rect.bottom + 18)
        x, y = self._find_safe_spawn(
            tile_map,
            origin=origin,
            requested_spawn_id=requested_spawn_id,
            fallback_spawn_id=requested_spawn_id,
            reason=f"near_exit_{expected_exit_id}",
        )
        print(
            f"[SPAWN][WARN] missing spawn_id={requested_spawn_id} "
            f"fallback near exit={expected_exit_id} pos=({x},{y})"
        )
        return x, y

    def _map_scene_label(self, tile_map: TileMap) -> str:
        return tile_map.map_path.stem if getattr(tile_map, "map_path", None) is not None else self.current_scene_name

    def _make_player_spawn_rect(
        self,
        tile_map: TileMap,
        spawn_id: str,
        spawn_position: tuple[int, int],
    ) -> pygame.Rect:
        player_size = 32
        spawn_area = tile_map.spawn_rects.get(spawn_id)
        if spawn_area is not None and spawn_area.width > 0 and spawn_area.height > 0:
            x = spawn_area.centerx - player_size // 2
            y = spawn_area.centery - player_size // 2
        else:
            x, y = spawn_position

        spawn_rect = pygame.Rect(int(x), int(y), player_size, player_size)
        spawn_rect.clamp_ip(self._spawn_map_rect(tile_map, player_size))
        return spawn_rect

    def _find_safe_spawn(
        self,
        tile_map: TileMap,
        origin: tuple[int, int] | None,
        requested_spawn_id: str,
        fallback_spawn_id: str,
        reason: str,
    ) -> tuple[int, int]:
        player_size = 32
        map_rect = self._spawn_map_rect(tile_map, player_size)
        if origin is None:
            origin = (
                min(tile_map.tile_width * 5, max(0, map_rect.width - player_size)),
                min(tile_map.tile_height * 5, max(0, map_rect.height - player_size)),
            )

        origin_rect = pygame.Rect(origin[0], origin[1], player_size, player_size)
        origin_rect.clamp_ip(map_rect)
        if self._is_spawn_rect_safe(origin_rect, tile_map):
            print(
                f"[SPAWN] final spawn_id={fallback_spawn_id}, requested={requested_spawn_id}, "
                f"player position=({origin_rect.x}, {origin_rect.y}), fallback={reason}_origin"
            )
            return origin_rect.x, origin_rect.y

        step = max(8, min(tile_map.tile_width, tile_map.tile_height) // 2)
        max_x = max(0, map_rect.width - player_size)
        max_y = max(0, map_rect.height - player_size)
        x_values = self._scan_axis_values(max_x, step, origin_rect.x)
        y_values = self._scan_axis_values(max_y, step, origin_rect.y)

        best_rect: pygame.Rect | None = None
        best_distance = float("inf")
        origin_center = pygame.math.Vector2(origin_rect.center)
        for y in y_values:
            for x in x_values:
                candidate = pygame.Rect(x, y, player_size, player_size)
                if not self._is_spawn_rect_safe(candidate, tile_map):
                    continue
                distance = origin_center.distance_squared_to(candidate.center)
                if distance < best_distance:
                    best_distance = distance
                    best_rect = candidate

        if best_rect is not None:
            print(
                f"[SPAWN] final spawn_id={fallback_spawn_id}, requested={requested_spawn_id}, "
                f"player position=({best_rect.x}, {best_rect.y}), fallback={reason}_nearest_safe"
            )
            return best_rect.x, best_rect.y

        print(
            f"[SPAWN][WARN] no safe spawn found; requested={requested_spawn_id}, "
            f"fallback_spawn={fallback_spawn_id}, using unsafe origin"
        )
        return origin_rect.x, origin_rect.y

    def _scan_axis_values(self, max_value: int, step: int, origin_value: int) -> list[int]:
        values = set(range(0, max_value + 1, step))
        values.add(max_value)
        values.add(max(0, min(origin_value, max_value)))
        return sorted(values)

    def _spawn_map_rect(self, tile_map: TileMap, player_size: int) -> pygame.Rect:
        return pygame.Rect(
            0,
            0,
            max(player_size, tile_map.drawable_width),
            max(player_size, tile_map.drawable_height),
        )

    def _is_spawn_rect_safe(self, rect: pygame.Rect, tile_map: TileMap) -> bool:
        return rect.collidelist(tile_map.collision_rects) == -1

    def _move_player_to(self, x: int, y: int) -> None:
        if self.player is None:
            return

        self.player.rect.topleft = (x, y)
        self.player.world_x = self.player.rect.x
        self.player.world_y = self.player.rect.y

    def _reset_player_after_shadow_failure(self) -> None:
        if self.player is None:
            return

        spawn_x, spawn_y = self.current_spawn_position
        self._move_player_to(spawn_x, spawn_y)
        if self.tile_map is not None:
            self._place_shadows_for_demo(self.tile_map)
        if self.camera is not None:
            self.camera.update(self.player.rect)
        print(f"[SHADOW] reset player position=({spawn_x},{spawn_y})")

    def _nudge_player_out_of_exit(self, tile_map: TileMap) -> None:
        if self.player is None:
            return

        if not any(self.player.rect.colliderect(scene_exit["rect"]) for scene_exit in tile_map.scene_exits):
            return

        original_position = self.player.rect.topleft
        offsets = ((0, 40), (40, 0), (-40, 0), (0, -40), (40, 40), (-40, 40), (80, 0), (0, 80))
        map_rect = pygame.Rect(0, 0, tile_map.drawable_width, tile_map.drawable_height)
        for offset_x, offset_y in offsets:
            candidate = self.player.rect.move(offset_x, offset_y)
            candidate.clamp_ip(map_rect)
            in_exit = any(candidate.colliderect(scene_exit["rect"]) for scene_exit in tile_map.scene_exits)
            in_collision = candidate.collidelist(tile_map.collision_rects) != -1
            if not in_exit and not in_collision:
                self._move_player_to(candidate.x, candidate.y)
                print(f"[Scene] spawn 鐐硅惤鍦ㄥ嚭鍙ｅ唴锛屽凡鍋忕Щ鐜╁浣嶇疆: {original_position} -> {self.player.rect.topleft}")
                return

        print("[Scene] spawn 鐐硅惤鍦ㄥ嚭鍙ｅ唴锛屼絾鏈壘鍒板彲鍋忕Щ浣嶇疆锛屼繚鎸佸師鍧愭爣")

    def _clear_interaction_state(self) -> None:
        self.nearby_npc = None
        self.nearby_item = None
        self.nearby_exit = None
        self.nearby_exits = []
        self.nearby_shadow = None
        self.nearby_shadow_trigger = None
        self.active_npc = None
        self._last_prompt_npc_id = None
        self._last_prompt_item_id = None
        self._last_prompt_exit_id = None
        self._last_exit_debug_signature = None
        self.selected_exit_id = None
        self.manual_exit_index = None
        self.manual_selected_exit_id = None
        self.manual_exit_selection_active = False

    def _update_nearby_npc(self) -> None:
        if self.player is None:
            self.nearby_npc = None
            return

        self.nearby_npc = None
        for npc in self.npcs:
            distance = pygame.math.Vector2(self.player.rect.center).distance_to((npc.world_x, npc.world_y))
            if distance < self.NPC_INTERACTION_DISTANCE:
                self.nearby_npc = npc
                if self._last_prompt_npc_id != npc.id:
                    print(f"[Scene] 鐜╁闈犺繎 NPC: {npc.id}")
                    self._last_prompt_npc_id = npc.id
                return

        self._last_prompt_npc_id = None

    def _find_nearest_npc_for_interaction(self) -> NPC | None:
        if self.player is None:
            print("[NPC_INTERACT] selected=None")
            return None

        player_center = pygame.math.Vector2(self.player.rect.center)
        selected_npc: NPC | None = None
        selected_distance: float | None = None
        for npc in self.npcs:
            npc_center = getattr(npc, "rect", None).center if hasattr(npc, "rect") else (npc.world_x, npc.world_y)
            distance = player_center.distance_to(npc_center)
            print(f"[NPC_INTERACT] candidate npc_id={npc.id} distance={distance:.1f}")
            if distance > self.NPC_INTERACT_RADIUS:
                continue
            if selected_distance is None or distance < selected_distance:
                selected_npc = npc
                selected_distance = distance

        if selected_npc is None:
            print("[NPC_INTERACT] selected=None")
            return None

        print(f"[NPC_INTERACT] selected npc_id={selected_npc.id} distance={selected_distance:.1f}")
        return selected_npc

    def _update_npc_animations(self, dt: float) -> None:
        for npc in self.npcs:
            npc.update(dt, is_talking=npc is self.active_npc)

    def _update_nearby_item(self) -> None:
        if self.player is None:
            self.nearby_item = None
            return

        self.nearby_item = None
        item_types = {"item", "hidden_collectible"}
        for interactable in self.interactables:
            if interactable.type not in item_types:
                continue
            distance = pygame.math.Vector2(self.player.rect.center).distance_to(interactable.rect.center)
            if self.player.rect.colliderect(interactable.rect) or distance < self.NPC_INTERACTION_DISTANCE:
                self.nearby_item = interactable
                if self._last_prompt_item_id != interactable.id:
                    print(f"[Scene] player near item: {interactable.id}")
                    self._last_prompt_item_id = interactable.id
                return

        self._last_prompt_item_id = None

    def _update_nearby_exit(self) -> None:
        if self.player is None or self.tile_map is None:
            self.nearby_exit = None
            return
        if self._transition_on_cooldown():
            self.nearby_exit = None
            self._last_prompt_exit_id = None
            return

        self.nearby_exit = None
        for scene_exit in self.tile_map.scene_exits:
            exit_rect = scene_exit["rect"]
            distance = pygame.math.Vector2(self.player.rect.center).distance_to(exit_rect.center)
            if self.player.rect.colliderect(exit_rect) or distance < self.EXIT_INTERACTION_DISTANCE:
                self.nearby_exit = scene_exit
                if self._last_prompt_exit_id != scene_exit["id"]:
                    print(f"[Scene] 鐜╁闈犺繎鍑哄彛: {scene_exit['id']}")
                    self._last_prompt_exit_id = scene_exit["id"]
                return

        self._last_prompt_exit_id = None

    def _update_nearby_exit(self) -> None:
        if self.player is None or self.tile_map is None:
            self.nearby_exit = None
            self.nearby_exits = []
            return
        if self._transition_on_cooldown():
            self.nearby_exit = None
            self.nearby_exits = []
            self._last_prompt_exit_id = None
            return

        self.nearby_exit = None
        candidates: list[dict] = []
        for scene_exit in self.tile_map.scene_exits:
            exit_rect = scene_exit["rect"]
            distance = pygame.math.Vector2(self.player.rect.center).distance_to(exit_rect.center)
            if self.player.rect.colliderect(exit_rect) or distance < self.EXIT_INTERACTION_DISTANCE:
                candidate = dict(scene_exit)
                candidate["_distance"] = distance
                lock_info = self._quest_lock_for_exit(candidate)
                if lock_info is not None:
                    candidate.update(lock_info)
                candidates.append(candidate)

        candidates.sort(key=lambda item: (item["_distance"], str(item.get("id", ""))))
        self.nearby_exits = candidates
        if not candidates:
            self._last_prompt_exit_id = None
            self._last_exit_debug_signature = None
            self.selected_exit_id = None
            self.manual_exit_index = None
            self.manual_selected_exit_id = None
            self.manual_exit_selection_active = False
            return

        ambiguous = (
            len(candidates) > 1
            and abs(candidates[1]["_distance"] - candidates[0]["_distance"]) <= self.EXIT_DISTANCE_TIE_THRESHOLD
        )
        manual_selected_exit = None
        if self.manual_exit_selection_active and self.manual_selected_exit_id is not None:
            manual_selected_exit = next(
                (candidate for candidate in candidates if str(candidate.get("id")) == self.manual_selected_exit_id),
                None,
            )
            if manual_selected_exit is None:
                self.selected_exit_id = None
                self.manual_exit_index = None
                self.manual_selected_exit_id = None
                self.manual_exit_selection_active = False

        if manual_selected_exit is not None:
            self.nearby_exit = manual_selected_exit
            self.selected_exit_id = str(manual_selected_exit.get("id"))
        elif not ambiguous:
            self.nearby_exit = candidates[0]
            self.selected_exit_id = str(self.nearby_exit.get("id"))
        else:
            self.selected_exit_id = None

        prompt_id = self.nearby_exit["id"] if self.nearby_exit is not None else "AMBIGUOUS"
        if self._last_prompt_exit_id != prompt_id:
            print(f"[Scene] player near exits: selected={prompt_id}")
            self._last_prompt_exit_id = prompt_id

        self._log_exit_candidates(candidates, self.nearby_exit, ambiguous)

    def _log_exit_candidates(self, candidates: list[dict], selected_exit: dict | None, ambiguous: bool) -> None:
        if self.player is None:
            return

        now = pygame.time.get_ticks()
        candidate_signature = tuple(
            (item.get("id"), int(item.get("_distance", 0) // 8))
            for item in candidates
        )
        selected_id = selected_exit.get("id") if selected_exit is not None else None
        signature = (
            self.current_scene_name,
            self.player.rect.x // 16,
            self.player.rect.y // 16,
            candidate_signature,
            selected_id,
            ambiguous,
        )
        if signature == self._last_exit_debug_signature and now - self._last_exit_debug_at < 1000:
            return

        self._last_exit_debug_signature = signature
        self._last_exit_debug_at = now
        candidate_text = ", ".join(self._format_exit_candidate_for_log(item) for item in candidates)
        if not candidate_text:
            candidate_text = "[]"
        if selected_exit is None:
            selected_text = "None (ambiguous)" if ambiguous else "None"
            selected_target_scene = "(none)"
            selected_target_spawn = "(none)"
        else:
            selected_text = str(selected_exit.get("id"))
            selected_target_scene = str(selected_exit.get("target_scene"))
            selected_target_spawn = str(selected_exit.get("target_spawn") or "(none)")

        print(
            "[EXIT_DEBUG] "
            f"current_scene={self.current_scene_name}, "
            f"player=({self.player.rect.x}, {self.player.rect.y}), "
            f"nearby_exits=[{candidate_text}], "
            f"selected_exit={selected_text}, "
            f"selected_exit.target_scene={selected_target_scene}, "
            f"selected_exit.target_spawn={selected_target_spawn}"
        )
        if ambiguous and selected_exit is None:
            print(
                "[EXIT][WARN] multiple exits have nearly equal distance; "
                "E transition is disabled until a single selected_exit is available"
            )

    def _format_exit_candidate_for_log(self, scene_exit: dict) -> str:
        return (
            f"{scene_exit.get('id')}"
            f"(distance={scene_exit.get('_distance', 0):.1f}, "
            f"target_scene={scene_exit.get('target_scene')}, "
            f"target_spawn={scene_exit.get('target_spawn') or '(none)'})"
        )

    def _quest_lock_for_exit(self, scene_exit: dict) -> dict | None:
        if self.debug_skip_mode:
            return None
        stage = self.main_quest_manager.stage
        if stage == "ending":
            return None

        raw_target = str(scene_exit.get("target_scene") or "")
        target_scene = self.scene_registry.canonical_name(raw_target)
        lock_specs = {
            "market": {
                "allowed": {"go_market", "market_collect"},
                "required": "go_market",
                "hint": "\u8bf7\u5148\u4e0e\u6751\u5be8\u957f\u8005\u5bf9\u8bdd",
            },
            "mountain": {
                "allowed": {"go_river", "shadow_challenge"},
                "required": "go_river",
                "hint": "\u8bf7\u5148\u5b8c\u6210\u96c6\u5e02\u5bfb\u6e90",
            },
            "festival": {
                "allowed": {"go_festival", "festival_defense"},
                "required": "go_festival",
                "hint": "\u8bf7\u5148\u51c0\u5316\u6cb3\u8c37\u5f71\u7eb9",
            },
        }
        spec = lock_specs.get(target_scene)
        if spec is None or stage in spec["allowed"]:
            return None
        return {
            "_quest_locked": True,
            "_quest_required_stage": spec["required"],
            "_quest_lock_hint": spec["hint"],
        }

    def _block_quest_locked_exit(self, scene_exit: dict) -> None:
        required = scene_exit.get("_quest_required_stage", "(unknown)")
        print(
            f"[QUEST_LOCK] blocked exit={scene_exit.get('id')} "
            f"stage={self.main_quest_manager.stage} required={required}"
        )
        hint = scene_exit.get("_quest_lock_hint", "\u8bf7\u5148\u5b8c\u6210\u524d\u7f6e\u76ee\u6807")
        self._show_quest_lock_toast(str(hint))

    def _transition_on_cooldown(self) -> bool:
        return pygame.time.get_ticks() < self.transition_cooldown_until

    def _enter_scene_exit(self, scene_exit: dict, confirm_key: str = "e") -> None:
        if self.scene_transition.is_active():
            return
        lock_info = self._quest_lock_for_exit(scene_exit)
        if lock_info is not None:
            scene_exit.update(lock_info)
        if scene_exit.get("_quest_locked"):
            self._block_quest_locked_exit(scene_exit)
            return

        self._play_sfx("ui_confirm")
        raw_target_scene = scene_exit.get("target_scene", "")
        target_scene = self.scene_registry.canonical_name(raw_target_scene)
        target_spawn = scene_exit.get("target_spawn") or None
        from_scene = self.current_scene_name
        print(
            f"[SCENE][scene_exit real transition] "
            f"confirm_key={confirm_key}, selected_exit={scene_exit.get('id')}, "
            f"exit_id={scene_exit.get('id')}, from={from_scene}, "
            f"raw_target_scene={raw_target_scene}, target_scene={target_scene}, "
            f"target_spawn={target_spawn or '(none)'}"
        )
        print(f"[SCENE] change_scene {from_scene} -> {target_scene}")
        print(
            f"[Scene] _enter_scene_exit: from_scene={from_scene}, "
            f"target_scene={target_scene}, target_spawn={target_spawn or '(none)'}"
        )
        registered = self.scene_registry.is_active(target_scene)
        map_path = self.scene_registry.get_map_path(target_scene)
        print(f"[SCENE] target_scene registered = {registered}")
        print(f"[SCENE] map_path = {map_path or '(none)'}")
        if not registered:
            self.error_message = f"鐩爣鍦烘櫙鏈敞鍐屾垨鏈惎鐢? {raw_target_scene} -> {target_scene}"
            self._set_status_message(self.error_message)
            print(f"[ERROR] target_scene not registered: {raw_target_scene} -> {target_scene}")
            return
        if map_path is None or not Path(map_path).exists():
            self.error_message = f"鐩爣鍦板浘鏂囦欢涓嶅瓨鍦? {map_path or target_scene}"
            self._set_status_message(self.error_message)
            print(f"[ERROR] target map file not found: {map_path or target_scene}")
            return

        def switch_scene() -> None:
            loaded = self.load_scene(target_scene, target_spawn)
            print(f"[Scene] load_scene returned: {loaded}")
            if not loaded:
                self._set_status_message(self.error_message or "鍦烘櫙鍒囨崲澶辫触")
                print(f"[Scene] 鍦烘櫙鍒囨崲澶辫触: {from_scene} -> {target_scene}")

        self.scene_transition.start(
            switch_scene,
            target_scene=target_scene,
            target_spawn=target_spawn,
        )

    def _draw_purify_effect(self, surface: pygame.Surface) -> None:
        if self.camera is None:
            return
        now = pygame.time.get_ticks()
        if now >= self.shadow_chase_manager.purify_effect_until:
            self._last_purify_effect_radius_log = -1
            return
        center = self.shadow_chase_manager.purify_effect_center
        if center is None:
            return

        screen_center = self.camera.world_to_screen(center[0], center[1])
        started_at = self.shadow_chase_manager.purify_effect_started_at
        duration = max(1, self.shadow_chase_manager.purify_effect_until - started_at)
        progress = max(0.0, min(1.0, (now - started_at) / duration))
        radius = int(30 + (self.shadow_chase_manager.PURIFY_RADIUS - 30) * progress)
        alpha = int(120 * (1.0 - progress)) + 35
        effect = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(effect, (225, 235, 255, max(28, alpha // 2)), (radius, radius), radius)
        pygame.draw.circle(effect, (245, 248, 255, alpha), (radius, radius), radius, 3)
        if abs(radius - self._last_purify_effect_radius_log) >= 18 or self._last_purify_effect_radius_log < 0:
            print(f"[PURIFY_EFFECT] draw radius={radius}")
            self._last_purify_effect_radius_log = radius
        surface.blit(effect, (screen_center[0] - radius, screen_center[1] - radius))

    def _draw_player_hit_feedback(self, surface: pygame.Surface) -> None:
        if self.player is None or self.camera is None:
            return
        if not self.shadow_chase_manager.is_player_invincible():
            return
        if pygame.time.get_ticks() // 110 % 2 == 0:
            return

        rect = self.camera.apply_rect(self.player.rect).inflate(10, 10)
        flash = pygame.Surface(rect.size, pygame.SRCALPHA)
        flash.fill((255, 230, 235, 95))
        surface.blit(flash, rect.topleft)
        pygame.draw.rect(surface, (255, 220, 230), rect, 2)

    def _draw_interaction_prompt(self, surface: pygame.Surface) -> None:
        self._draw_prompt(surface, self.font.render("E/Enter：对话", True, (255, 245, 210)))

    def _draw_enter_prompt(self, surface: pygame.Surface) -> None:
        self._draw_prompt(surface, self.font.render("E/Enter：进入", True, (255, 245, 210)))

    def _draw_shadow_reclaim_prompt(self, surface: pygame.Surface) -> None:
        self._draw_prompt(surface, self.font.render("E/Enter：交互", True, (255, 235, 250)))

    def _draw_shadow_trigger_prompt(self, surface: pygame.Surface) -> None:
        self._draw_prompt(surface, self.font.render("Press E to start shadow chase", True, (235, 220, 255)))

    def _draw_prompt(self, surface: pygame.Surface, prompt_surface: pygame.Surface) -> None:
        prompt_rect = prompt_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 60))
        bg_rect = prompt_rect.inflate(28, 16)
        pygame.draw.rect(surface, (24, 24, 28), bg_rect)
        pygame.draw.rect(surface, (220, 200, 140), bg_rect, 2)
        surface.blit(prompt_surface, prompt_rect)

    def _set_status_message(self, message: str, duration_ms: int = 2200) -> None:
        self.status_message = message
        self.status_message_until = pygame.time.get_ticks() + duration_ms
        print(f"[HUD] {message}")

    def _show_quest_lock_toast(self, hint: str, duration_ms: int = 1800) -> None:
        self.quest_lock_toast_hint = hint
        self.quest_lock_toast_until = pygame.time.get_ticks() + duration_ms

    def _draw_status_message(self, surface: pygame.Surface) -> None:
        if not self.status_message or pygame.time.get_ticks() >= self.status_message_until:
            return
        lines = [line for line in self.status_message.splitlines() if line]
        rendered = [self.font.render(line, True, (245, 245, 225)) for line in lines]
        width = max(item.get_width() for item in rendered)
        height = sum(item.get_height() for item in rendered) + max(0, len(rendered) - 1) * 4
        bg_rect = pygame.Rect(0, 0, width + 30, height + 14)
        bg_rect.center = (SCREEN_WIDTH // 2, 42)
        pygame.draw.rect(surface, (24, 20, 32), bg_rect)
        pygame.draw.rect(surface, (160, 120, 220), bg_rect, 2)
        y = bg_rect.y + 7
        for item in rendered:
            surface.blit(item, item.get_rect(center=(SCREEN_WIDTH // 2, y + item.get_height() // 2)))
            y += item.get_height() + 4

    def _draw_quest_lock_toast(self, surface: pygame.Surface) -> None:
        now = pygame.time.get_ticks()
        if not self.quest_lock_toast_hint or now >= self.quest_lock_toast_until:
            return

        remaining = self.quest_lock_toast_until - now
        fade = min(1.0, remaining / 300.0)
        title_surface = self.font.render(TOAST_LOCK_TITLE, True, (255, 238, 196))
        hint_font = load_chinese_font(18, self.font)
        hint_surface = hint_font.render(self.quest_lock_toast_hint, True, (226, 220, 204))
        width = min(420, max(title_surface.get_width(), hint_surface.get_width()) + 42)
        height = 82
        rect = pygame.Rect((SCREEN_WIDTH - width) // 2, 86, width, height)
        alpha = int(205 * fade)
        panel = pygame.Surface(rect.size, pygame.SRCALPHA)
        pygame.draw.rect(panel, (18, 16, 24, alpha), panel.get_rect(), border_radius=6)
        pygame.draw.rect(panel, (214, 178, 92, int(210 * fade)), panel.get_rect(), 1, border_radius=6)
        surface.blit(panel, rect.topleft)
        title_surface.set_alpha(int(255 * fade))
        hint_surface.set_alpha(int(235 * fade))
        surface.blit(title_surface, title_surface.get_rect(center=(rect.centerx, rect.y + 25)))
        surface.blit(hint_surface, hint_surface.get_rect(center=(rect.centerx, rect.y + 56)))

    def _draw_debug_overlay(self, surface: pygame.Surface) -> None:
        if not self.debug_overlay_visible or self.player is None:
            return

        map_label = "None"
        if self.tile_map is not None:
            map_label = Path(self.tile_map.map_path).name
        nearby_exit_id = self.nearby_exit["id"] if self.nearby_exit is not None else "None"
        nearby_exit_count = len(self.nearby_exits)
        lines = [
            f"Scene: {self.current_scene_name or 'None'}",
            f"Map: {map_label}",
            f"Exit selected: {nearby_exit_id}",
            f"Exit candidates: {nearby_exit_count}",
            f"Player: ({self.player.rect.x}, {self.player.rect.y})",
            f"Task: {self.task_manager.current_task_id}",
            f"Items: {len(self.inventory.items)}",
            f"Silver: {self.score_manager.silver_light}",
        ]

        rendered_lines = [self.debug_font.render(line, True, (245, 245, 225)) for line in lines]
        width = max(line.get_width() for line in rendered_lines) + 12
        height = len(rendered_lines) * 16 + 8
        overlay = pygame.Surface((width, height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        surface.blit(overlay, (6, 6))
        pygame.draw.rect(surface, (210, 210, 160), pygame.Rect(6, 6, width, height), 1)

        for index, line_surface in enumerate(rendered_lines):
            surface.blit(line_surface, (12, 10 + index * 16))

    def _draw_error(self, surface: pygame.Surface) -> None:
        message = self.error_message or "地图加载失败，请检查 Tiled 地图。"
        lines = [
            "地图加载失败",
            message,
            "请查看终端输出的详细错误信息。",
        ]

        start_y = SCREEN_HEIGHT // 2 - 50
        for index, line in enumerate(lines):
            text_surface = self.font.render(line, True, (245, 230, 210))
            text_rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, start_y + index * 38))
            surface.blit(text_surface, text_rect)
