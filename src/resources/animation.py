from __future__ import annotations

import re
from pathlib import Path

import pygame


DEFAULT_FRAME_DURATION = 0.14
FRAME_INDEX_RE = re.compile(r"_(\d+)\.png$", re.IGNORECASE)


class Animation:
    """Looping frame animation driven by dt."""

    def __init__(
        self,
        frames: list[pygame.Surface],
        frame_duration: float = DEFAULT_FRAME_DURATION,
    ) -> None:
        self.frames = frames
        self.frame_duration = frame_duration
        self.elapsed = 0.0
        self.index = 0

    def update(self, dt: float) -> None:
        if len(self.frames) <= 1:
            return
        self.elapsed += dt
        while self.elapsed >= self.frame_duration:
            self.elapsed -= self.frame_duration
            self.index = (self.index + 1) % len(self.frames)

    def current_frame(self) -> pygame.Surface | None:
        if not self.frames:
            return None
        return self.frames[self.index]

    def get_image(self) -> pygame.Surface | None:
        return self.current_frame()

    def reset(self) -> None:
        self.elapsed = 0.0
        self.index = 0


class StateAnimationController:
    """Selects named animations and falls back to an idle state."""

    def __init__(
        self,
        animations: dict[str, Animation],
        default_state: str = "idle_front",
    ) -> None:
        self.animations = animations
        self.default_state = default_state
        self.current_state = default_state

    def set_state(self, state: str) -> None:
        next_state = state if self._has_frames(state) else self.default_state
        if not self._has_frames(next_state):
            next_state = self._first_available_state()
        if next_state == self.current_state:
            return
        self.current_state = next_state
        animation = self.animations.get(self.current_state)
        if animation is not None:
            animation.reset()

    def update(self, dt: float) -> None:
        animation = self.animations.get(self.current_state)
        if animation is not None:
            animation.update(dt)

    def current_frame(self) -> pygame.Surface | None:
        animation = self.animations.get(self.current_state)
        if animation is None:
            return None
        return animation.current_frame()

    def has_state(self, state: str) -> bool:
        return self._has_frames(state)

    def _has_frames(self, state: str) -> bool:
        animation = self.animations.get(state)
        return animation is not None and bool(animation.frames)

    def _first_available_state(self) -> str:
        for state, animation in self.animations.items():
            if animation.frames:
                return state
        return self.default_state


class AnimationController:
    """Selects idle/walk animation by movement state and direction."""

    DIRECTIONS = ("down", "up", "left", "right")

    def __init__(self, animations: dict[str, Animation]) -> None:
        self.animations = animations
        self.direction = "down"
        self.moving = False
        self.current_key = "idle_down"

    def set_motion(self, direction: str, moving: bool) -> None:
        if direction not in self.DIRECTIONS:
            direction = self.direction
        self.direction = direction
        self.moving = moving
        next_key = f"{'walk' if moving else 'idle'}_{self.direction}"
        if next_key != self.current_key:
            self.current_key = next_key
            if self.current_key in self.animations:
                self.animations[self.current_key].reset()

    def update(self, dt: float) -> None:
        animation = self.animations.get(self.current_key)
        if animation is not None:
            animation.update(dt)

    def current_frame(self) -> pygame.Surface | None:
        animation = self.animations.get(self.current_key)
        if animation is None:
            return None
        return animation.current_frame()

    @classmethod
    def for_player(cls, target_height: int = 72) -> "AnimationController":
        sprite_dir = Path("assets/sprites/player")
        animations: dict[str, Animation] = {}

        for direction in cls.DIRECTIONS:
            idle_frames = load_animation_frames(
                sprite_dir,
                f"player_idle_{direction}",
                target_height,
                required=True,
                placeholder_color=(80, 120, 220),
            )
            animations[f"idle_{direction}"] = Animation(idle_frames)

            walk_frames = load_animation_frames(
                sprite_dir,
                f"player_walk_{direction}",
                target_height,
                required=True,
                placeholder_color=(70, 150, 230),
            )
            animations[f"walk_{direction}"] = Animation(walk_frames)

        return cls(animations)

    @staticmethod
    def _load_scaled(path: Path, target_height: int) -> pygame.Surface | None:
        return load_scaled_image(path, target_height)

    @staticmethod
    def _oriented_frame(frame: pygame.Surface, direction: str) -> pygame.Surface:
        if direction == "right":
            return pygame.transform.flip(frame, True, False)
        return frame.copy()


def load_animation_frames(
    directory: Path,
    prefix: str,
    target_height: int,
    frame_duration: float = DEFAULT_FRAME_DURATION,
    required: bool = False,
    placeholder_color: tuple[int, int, int] = (180, 80, 180),
) -> list[pygame.Surface]:
    """Load prefix_NN.png frames, plus an exact prefix.png single-frame fallback."""

    del frame_duration
    paths = _find_frame_paths(directory, prefix)
    frames = [load_scaled_image(path, target_height) for path in paths]
    frames = [frame for frame in frames if frame is not None]
    if frames:
        return frames

    if required:
        print(
            f"[Animation] warning: missing frames for {directory / (prefix + '_NN.png')}; "
            "using placeholder."
        )
        return [create_placeholder_surface(target_height, placeholder_color)]

    return []


def load_first_available_animation(
    directory: Path,
    prefixes: list[str],
    target_height: int,
    required: bool = False,
    placeholder_color: tuple[int, int, int] = (180, 80, 180),
) -> list[pygame.Surface]:
    for prefix in prefixes:
        frames = load_animation_frames(directory, prefix, target_height)
        if frames:
            return frames

    if required:
        joined = ", ".join(prefixes)
        print(f"[Animation] warning: missing frames for [{joined}]; using placeholder.")
        return [create_placeholder_surface(target_height, placeholder_color)]

    return []


def load_scaled_image(path: Path, target_height: int) -> pygame.Surface | None:
    if not path.exists():
        return None

    try:
        image = pygame.image.load(str(path))
        if pygame.display.get_surface() is not None:
            image = image.convert_alpha()
    except pygame.error as exc:
        print(f"[Animation] warning: image load failed: {path}, error={exc}")
        return None

    width, height = image.get_size()
    if height <= 0:
        return image

    scale = target_height / height
    return pygame.transform.smoothscale(
        image,
        (max(1, int(width * scale)), target_height),
    )


def create_placeholder_surface(
    target_height: int,
    color: tuple[int, int, int] = (180, 80, 180),
) -> pygame.Surface:
    width = max(24, int(target_height * 0.55))
    surface = pygame.Surface((width, target_height), pygame.SRCALPHA)
    rect = surface.get_rect()
    pygame.draw.rect(surface, (*color, 230), rect)
    pygame.draw.rect(surface, (30, 30, 36, 255), rect, 2)
    return surface


def _find_frame_paths(directory: Path, prefix: str) -> list[Path]:
    if not directory.exists():
        return []

    numbered_paths = list(directory.glob(f"{prefix}_*.png"))
    numbered_paths = [path for path in numbered_paths if FRAME_INDEX_RE.search(path.name)]
    numbered_paths.sort(key=_frame_sort_key)
    if numbered_paths:
        return numbered_paths

    exact_path = directory / f"{prefix}.png"
    if exact_path.exists():
        return [exact_path]

    return []


def _frame_sort_key(path: Path) -> tuple[int, str]:
    match = FRAME_INDEX_RE.search(path.name)
    if match is None:
        return (0, path.name)
    return (int(match.group(1)), path.name)
