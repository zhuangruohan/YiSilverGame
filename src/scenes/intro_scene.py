from __future__ import annotations

from pathlib import Path
from typing import Callable

import pygame

from settings import SCREEN_HEIGHT, SCREEN_WIDTH
from src.scenes.base_scene import BaseScene
from src.ui.fonts import load_chinese_font


class IntroScene(BaseScene):
    """Optional intro cutscene wrapper.

    Pygame does not provide reliable MP4 playback without external backends.
    This scene safely detects the configured video and falls back to gameplay.
    """

    VIDEO_PATH = Path("assets/cutscenes/intro/intro.mp4")

    def __init__(
        self,
        font: pygame.font.Font,
        finish_callback: Callable[[], None],
    ) -> None:
        self.font = load_chinese_font(24, font)
        self.small_font = load_chinese_font(18, font)
        self.finish_callback = finish_callback
        self.finished = False
        self._logged_fallback = False
        self._fallback_delay_ms = 120
        self._started_at = pygame.time.get_ticks()
        self.video_found = self.VIDEO_PATH.exists()

        print(f"[INTRO] video path={self.VIDEO_PATH.as_posix()}")
        print(f"[INTRO] video found={self.video_found}")
        if not self.video_found:
            print("[INTRO] skip -> village_hub")
        else:
            print("[INTRO][WARN] video playback unsupported, skip intro")

    def handle_event(self, event: pygame.event.Event) -> bool:
        if event.type != pygame.KEYDOWN:
            return False
        if event.key in (pygame.K_RETURN, pygame.K_ESCAPE):
            self._finish("skip")
            return True
        return True

    def update(self, dt: float) -> None:
        if self.finished:
            return
        elapsed_ms = pygame.time.get_ticks() - self._started_at
        if elapsed_ms >= self._fallback_delay_ms:
            self._finish("skip")

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill((8, 8, 12))
        title = self.font.render("银纹秘境", True, (238, 238, 230))
        hint = self.small_font.render("开场视频准备中，按 Enter / Esc 跳过", True, (198, 190, 172))
        surface.blit(title, title.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 18)))
        surface.blit(hint, hint.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 28)))

    def _finish(self, reason: str) -> None:
        if self.finished:
            return
        self.finished = True
        if reason == "finished":
            print("[INTRO] finished -> village_hub")
        else:
            print("[INTRO] skip -> village_hub")
        self.finish_callback()
