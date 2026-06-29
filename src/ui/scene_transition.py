from __future__ import annotations

from collections.abc import Callable

import pygame


class SceneTransitionManager:
    """Full-screen black fade transition with a switch callback."""

    IDLE = "idle"
    FADE_OUT = "fade_out"
    SWITCHING = "switching"
    FADE_IN = "fade_in"

    def __init__(self, duration: float = 0.4) -> None:
        self.duration = max(0.05, float(duration))
        self.state = self.IDLE
        self.elapsed = 0.0
        self.alpha = 0
        self._callback: Callable[[], object] | None = None
        self._target_scene = ""
        self._target_spawn = ""

    def start(
        self,
        callback: Callable[[], object],
        target_scene: str = "",
        target_spawn: str | None = None,
        duration: float | None = None,
    ) -> bool:
        if self.is_active():
            return False

        if duration is not None:
            self.duration = max(0.05, float(duration))
        self._callback = callback
        self._target_scene = target_scene
        self._target_spawn = target_spawn or ""
        self.elapsed = 0.0
        self.alpha = 0
        self.state = self.FADE_OUT
        print(f"[TRANSITION] fade_out start target_scene={target_scene or '(callback)'}")
        return True

    def update(self, dt: float) -> None:
        if self.state == self.IDLE:
            return

        self.elapsed += max(0.0, float(dt))
        progress = min(1.0, self.elapsed / self.duration)

        if self.state == self.FADE_OUT:
            self.alpha = int(255 * progress)
            if progress >= 1.0:
                self._switch_scene()
            return

        if self.state == self.FADE_IN:
            self.alpha = int(255 * (1.0 - progress))
            if progress >= 1.0:
                self.state = self.IDLE
                self.elapsed = 0.0
                self.alpha = 0
                self._callback = None
                print("[TRANSITION] done")

    def draw(self, surface: pygame.Surface) -> None:
        if self.state == self.IDLE or self.alpha <= 0:
            return
        overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, max(0, min(255, self.alpha))))
        surface.blit(overlay, (0, 0))

    def is_active(self) -> bool:
        return self.state != self.IDLE

    def is_blocking_input(self) -> bool:
        return self.is_active()

    def _switch_scene(self) -> None:
        self.state = self.SWITCHING
        target_scene = self._target_scene or "(callback)"
        target_spawn = self._target_spawn or "(none)"
        print(f"[TRANSITION] switching scene target_scene={target_scene} spawn={target_spawn}")
        if self._callback is not None:
            self._callback()
        self.state = self.FADE_IN
        self.elapsed = 0.0
        self.alpha = 255
        print("[TRANSITION] fade_in start")
