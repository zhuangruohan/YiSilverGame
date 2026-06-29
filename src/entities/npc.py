import re
from pathlib import Path

import pygame

from src.resources.animation import (
    Animation,
    StateAnimationController,
    create_placeholder_surface,
    load_first_available_animation,
    load_scaled_image,
)


class NPC:
    """Tiled object NPC with idle/dialogue animation fallback."""

    IMAGE_HEIGHT = 96
    SPRITE_DIR = Path("assets/sprites/npc")
    FRAME_SUFFIX_RE = re.compile(r"_\d+$")

    CHARACTER_IDS = (
        "shadow_spirit",
        "market_auntie",
        "festival_host",
        "silversmith",
        "elder",
        "smith",
        "host",
    )
    CHARACTER_STATES = {
        "elder": ("idle_front", "talk_front", "point"),
        "market_auntie": ("idle_front", "talk_front"),
        "smith": ("idle_front", "talk_front", "hammer_front", "hammer_work"),
        "silversmith": ("idle_front", "talk_front", "hammer_front", "hammer_work"),
        "host": ("idle_front", "introduce_front", "talk_front"),
        "festival_host": ("idle_front", "introduce_front", "talk_front"),
        "shadow_spirit": ("idle_front", "flee_left", "flee_right"),
    }
    DIALOGUE_STATE_BY_CHARACTER = {
        "host": "introduce_front",
        "festival_host": "introduce_front",
    }
    DEFAULT_SPRITE_BY_CHARACTER = {
        "elder": ("elder_idle", "elder_idle_front"),
        "silversmith": ("silversmith_idle", "silversmith_hammer_work", "silversmith_hammer_up", "silversmith_idl"),
        "smith": ("silversmith_idle", "silversmith_hammer_work", "silversmith_hammer_up", "silversmith_idl"),
        "market_auntie": ("market_auntie_idle", "market_auntie_idle_front", "market_auntie_idle "),
        "festival_host": ("festival_host_idle", "host_idle_front"),
        "host": ("festival_host_idle", "host_idle_front"),
        "shadow_spirit": ("shadow_spirit_idle_front",),
    }
    FORBIDDEN_IMAGE_PREFIXES_BY_CHARACTER = {
        "market_auntie": ("elder", "silversmith", "smith"),
        "silversmith": ("market_auntie",),
    }
    FORCED_IMAGE_FILES_BY_CHARACTER_STATE = {
        ("market_auntie", "idle_front"): (
            Path("assets/sprites/npc/market_auntie_idle.png"),
            Path("assets/sprites/npc/market_auntie_idle_front_01.png"),
            Path("assets/sprites/npc/market_auntie_idle_front_02.png"),
        ),
        ("market_auntie", "talk_front"): (
            Path("assets/sprites/npc/market_auntie_talk_front_01.png"),
            Path("assets/sprites/npc/market_auntie_talk_front_02.png"),
        ),
        ("silversmith", "idle_front"): (
            Path("assets/sprites/npc/silversmith_idle.png"),
            Path("assets/sprites/npc/silversmith_hammer_up.png"),
            Path("assets/sprites/npc/silversmith_hammer_work.png"),
            Path("assets/sprites/npc/silversmith_idl-removebg-preview.png"),
        ),
        ("silversmith", "talk_front"): (
            Path("assets/sprites/npc/silversmith_idle.png"),
            Path("assets/sprites/npc/silversmith_hammer_up.png"),
            Path("assets/sprites/npc/silversmith_hammer_work.png"),
            Path("assets/sprites/npc/silversmith_idl-removebg-preview.png"),
        ),
    }

    def __init__(
        self,
        npc_id: str,
        name: str,
        dialogue: str,
        world_x: int,
        world_y: int,
        sprite: str = "",
        character: str = "",
    ) -> None:
        self.id = npc_id
        self.name = name
        self.dialogue = dialogue
        self.world_x = world_x
        self.world_y = world_y
        self.sprite = str(sprite or "").strip()
        self.character = str(character or "").strip()
        self.character_id = self._resolve_character_id()
        self._warn_if_wrong_tiled_sprite()
        self.animation = self._load_animation_controller()
        self.animation_state = "idle_front"
        self.rect = pygame.Rect(0, 0, 32, 32)
        self.rect.midbottom = (self.world_x, self.world_y)
        self.color = (70, 190, 110)

    def update(self, dt: float, is_talking: bool = False) -> None:
        if is_talking:
            self.set_animation_state(self._dialogue_state())
        elif self.animation_state not in {"hammer_front", "hammer_work"}:
            self.set_animation_state("idle_front")
        self.animation.update(dt)

    def set_animation_state(self, state: str) -> None:
        self.animation_state = state
        self.animation.set_state(state)

    def draw(self, surface: pygame.Surface, camera) -> None:
        image = self.animation.current_frame()
        if image is not None:
            image_rect = image.get_rect(midbottom=(self.world_x, self.world_y))
            screen_rect = camera.apply_rect(image_rect)
            surface.blit(image, screen_rect)
            return

        fallback_rect = camera.apply_rect(self.rect)
        pygame.draw.rect(surface, self.color, fallback_rect)
        pygame.draw.rect(surface, (20, 90, 45), fallback_rect, 2)

    def _dialogue_state(self) -> str:
        preferred_state = self.DIALOGUE_STATE_BY_CHARACTER.get(self.character_id, "talk_front")
        if self.animation.has_state(preferred_state):
            return preferred_state
        if self.animation.has_state("talk_front"):
            return "talk_front"
        return "idle_front"

    def _load_animation_controller(self) -> StateAnimationController:
        states = self.CHARACTER_STATES.get(self.character_id, ("idle_front", "talk_front"))
        animations: dict[str, Animation] = {}

        for state in states:
            source_path, frames = self._load_frames_for_state(state)
            animations[state] = Animation(frames)
            if state == "idle_front":
                self._log_image_result(source_path)
            if self.character_id == "market_auntie":
                self._log_market_auntie_audit(state, source_path)
            elif self.character_id == "silversmith" and state == "idle_front":
                self._log_final_image_audit(source_path)

        print(
            f"[NPC] id={self.id}, name={self.name}, character={self.character_id}, "
            f"sprite={self.sprite or '(none)'}, character_property={self.character or '(none)'}, "
            f"states={list(animations)}"
        )
        return StateAnimationController(animations, default_state="idle_front")

    def _load_frames_for_state(self, state: str) -> tuple[Path | None, list[pygame.Surface]]:
        forced_files = self.FORCED_IMAGE_FILES_BY_CHARACTER_STATE.get((self.character_id, state))
        if forced_files is not None:
            source_path, frames = self._load_forced_image_files(forced_files)
            if frames:
                return source_path, frames
            if state == "idle_front":
                print(
                    f"[NPC_IMAGE][WARN] npc_id={self.id} "
                    f"missing {self.character_id} idle files fallback=placeholder"
                )
                return None, [create_placeholder_surface(self.IMAGE_HEIGHT, (70, 190, 110))]
            return None, []

        prefixes = self._prefixes_for_state(state)
        source_path = self._first_available_image_path(prefixes)
        frames = load_first_available_animation(
            self.SPRITE_DIR,
            prefixes,
            self.IMAGE_HEIGHT,
            required=state == "idle_front",
            placeholder_color=(70, 190, 110),
        )
        return source_path, frames

    def _load_forced_image_files(self, image_paths: tuple[Path, ...]) -> tuple[Path | None, list[pygame.Surface]]:
        frames: list[pygame.Surface] = []
        source_path: Path | None = None
        for image_path in image_paths:
            frame = load_scaled_image(image_path, self.IMAGE_HEIGHT)
            if frame is None:
                continue
            if source_path is None:
                source_path = image_path
            frames.append(frame)
        return source_path, frames

    def _prefixes_for_state(self, state: str) -> list[str]:
        character_id = self.character_id
        prefixes = self._explicit_sprite_prefixes(state)
        prefixes.append(f"{character_id}_{state}")

        if state == "idle_front":
            prefixes.append(f"{character_id}_idle")
            prefixes.extend(self.DEFAULT_SPRITE_BY_CHARACTER.get(character_id, ()))
        elif state == "talk_front":
            prefixes.append(f"{character_id}_talk")
        elif state == "introduce_front":
            prefixes.append(f"{character_id}_introduce")
        elif state == "hammer_front":
            prefixes.append(f"{character_id}_hammer")

        compatibility_prefixes = {
            ("market_auntie", "idle_front"): ["market_auntie_idle "],
            ("silversmith", "idle_front"): ["silversmith_hammer_work", "silversmith_hammer_up", "silversmith_idl"],
            ("silversmith", "hammer_front"): ["silversmith_hammer_up"],
            ("smith", "idle_front"): ["silversmith_hammer_work", "silversmith_hammer_up", "silversmith_idl"],
            ("smith", "hammer_work"): ["silversmith_hammer_work"],
            ("festival_host", "introduce_front"): ["host_introduce_front", "host_introduce"],
            ("festival_host", "talk_front"): ["host_talk_front", "host_talk"],
            ("festival_host", "idle_front"): ["host_idle_front"],
            ("host", "introduce_front"): ["host_introduce_front", "host_introduce"],
        }
        prefixes.extend(compatibility_prefixes.get((character_id, state), []))
        return self._filter_allowed_prefixes(self._dedupe_prefixes(prefixes))

    def _resolve_character_id(self) -> str:
        id_character = self._character_from_value(self.id)
        if id_character:
            return id_character

        raw_values = (self.character, self.sprite, self.name)
        for raw_value in raw_values:
            character_id = self._character_from_value(raw_value)
            if character_id:
                return character_id

        return str(self.id or "npc").strip().lower()

    def _character_from_value(self, raw_value) -> str | None:
        normalized = self._normalize_token(raw_value)
        if not normalized:
            return None

        if normalized == "smith" or normalized.startswith("smith_"):
            return "silversmith"

        for character_id in self.CHARACTER_IDS:
            if normalized == character_id or normalized.startswith(f"{character_id}_"):
                return character_id
        return None

    def _warn_if_wrong_tiled_sprite(self) -> None:
        if self.id != "market_auntie":
            return
        sprite_prefix = self._sprite_prefix()
        if not sprite_prefix or sprite_prefix.startswith("market_auntie"):
            return
        print(
            f"[NPC_IMAGE][WARN] npc_id=market_auntie tiled sprite looks wrong: "
            f"{self.sprite}, force character=market_auntie"
        )

    def _explicit_sprite_prefixes(self, state: str) -> list[str]:
        sprite_prefix = self._sprite_prefix()
        if not sprite_prefix:
            return []

        if self.character_id == "silversmith":
            if sprite_prefix.startswith("market_auntie") or sprite_prefix.startswith("smith_idle_front"):
                return []
        elif self.character_id == "market_auntie":
            if (
                sprite_prefix.startswith("elder")
                or sprite_prefix.startswith("silversmith")
                or sprite_prefix.startswith("smith_")
            ):
                return []

        if state == "idle_front":
            return [sprite_prefix]
        state_key = state.replace("_front", "")
        if state in sprite_prefix or state_key in sprite_prefix:
            return [sprite_prefix]
        return []

    def _sprite_prefix(self) -> str:
        if not self.sprite:
            return ""

        stem = Path(self.sprite).stem
        stem = self.FRAME_SUFFIX_RE.sub("", stem)
        return self._normalize_token(stem)

    def _normalize_token(self, raw_value) -> str:
        return str(raw_value or "").strip().lower().replace("-", "_").replace(" ", "_")

    def _dedupe_prefixes(self, prefixes: list[str]) -> list[str]:
        result = []
        seen = set()
        for prefix in prefixes:
            if not prefix or prefix in seen:
                continue
            result.append(prefix)
            seen.add(prefix)
        return result

    def _filter_allowed_prefixes(self, prefixes: list[str]) -> list[str]:
        allowed = []
        for prefix in prefixes:
            if self._is_forbidden_prefix(prefix):
                continue
            allowed.append(prefix)
        return allowed

    def _is_forbidden_prefix(self, prefix: str) -> bool:
        normalized = self._normalize_token(prefix)
        forbidden_prefixes = self.FORBIDDEN_IMAGE_PREFIXES_BY_CHARACTER.get(self.character_id, ())
        return any(normalized == item or normalized.startswith(f"{item}_") for item in forbidden_prefixes)

    def _is_forbidden_image_path(self, source_path: Path) -> bool:
        return self._is_forbidden_prefix(source_path.stem)

    def _log_market_auntie_audit(self, state: str, source_path: Path | None) -> None:
        image_text = source_path.as_posix() if source_path is not None else "placeholder"
        if state == "idle_front":
            print(f"[NPC_IMAGE_AUDIT] npc_id=market_auntie final_image={image_text}")
        print(
            "[NPC_IMAGE_AUDIT] "
            f"npc_id=market_auntie character=market_auntie state={state} image={image_text}"
        )
        lowered = image_text.lower()
        if "elder" in lowered:
            print(f"[NPC_IMAGE][ERROR] market_auntie wrongly uses elder image: {image_text}")
        if "silversmith" in lowered or "smith" in lowered:
            print(f"[NPC_IMAGE][ERROR] market_auntie wrongly uses smith image: {image_text}")

    def _log_final_image_audit(self, source_path: Path | None) -> None:
        image_text = source_path.as_posix() if source_path is not None else "placeholder"
        print(f"[NPC_IMAGE_AUDIT] npc_id={self.id} final_image={image_text}")

    def _first_available_image_path(self, prefixes: list[str]) -> Path | None:
        for prefix in prefixes:
            numbered_paths = sorted(self.SPRITE_DIR.glob(f"{prefix}_*.png"))
            numbered_paths = [path for path in numbered_paths if re.search(r"_\d+\.png$", path.name, re.IGNORECASE)]
            if numbered_paths:
                return numbered_paths[0]

            exact_path = self.SPRITE_DIR / f"{prefix}.png"
            if exact_path.exists():
                return exact_path
        return None

    def _log_image_result(self, source_path: Path | None) -> None:
        if source_path is None:
            print(
                f"[NPC_IMAGE][WARN] npc_id={self.id} "
                f"sprite={self.sprite or self.character or '(none)'} "
                "fallback=placeholder"
            )
            return

        print(
            f"[NPC_IMAGE] npc_id={self.id} "
            f"character={self.character_id} image={source_path.as_posix()}"
        )
