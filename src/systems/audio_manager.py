from __future__ import annotations

from pathlib import Path

import pygame


class AudioManager:
    """Small safe wrapper around pygame.mixer for SFX, voice and BGM."""

    SFX_PATHS = {
        "collect": "assets/audio/sfx/collect.wav",
        "purify": "assets/audio/sfx/purify.wav",
        "hit_shadow": "assets/audio/sfx/hit_shadow.wav",
        "player_hit": "assets/audio/sfx/player_hit.wav",
        "victory": "assets/audio/sfx/victory.wav",
        "fail": "assets/audio/sfx/fail.wav",
        "inventory": "assets/audio/sfx/inventory.wav",
        "festival_success": "assets/audio/sfx/festival_success.wav",
        "ui_confirm": "assets/audio/sfx/ui_confirm.wav",
    }

    def __init__(self) -> None:
        self.enabled = False
        self.sfx_volume = 0.6
        self.voice_volume = 0.8
        self.bgm_volume = 0.35
        self._sfx_cache: dict[str, pygame.mixer.Sound] = {}
        self._warned_missing: set[str] = set()
        self._current_bgm = ""
        self._voice_channel = None
        self._init_mixer()

    def play_sfx(self, name_or_path: str) -> None:
        if not name_or_path:
            return
        path = self._resolve_sfx_path(name_or_path)
        if not self.enabled:
            return
        if not self._exists(path, "SFX"):
            return

        sound = self._sfx_cache.get(path)
        if sound is None:
            try:
                sound = pygame.mixer.Sound(path)
                self._sfx_cache[path] = sound
            except pygame.error as exc:
                self._warn_once(path, f"[SFX][WARN] failed load {path}: {exc}")
                return
        sound.set_volume(self.sfx_volume)
        sound.play()
        print(f"[SFX] play {name_or_path} path={path}")

    def play_voice(self, path: str) -> None:
        if not path:
            return
        if not self.enabled:
            return
        if not self._voice_exists(path):
            return
        try:
            sound = pygame.mixer.Sound(path)
        except pygame.error as exc:
            self._warn_once(path, f"[VOICE][WARN] failed load {path}: {exc}")
            return

        sound.set_volume(self.voice_volume)
        if self._voice_channel is None:
            self._voice_channel = pygame.mixer.Channel(15)
        self._voice_channel.stop()
        self._voice_channel.play(sound)
        print(f"[VOICE] play path={path}")

    def stop_voice(self) -> None:
        if self._voice_channel is not None:
            self._voice_channel.stop()
            print("[VOICE] stop")

    def play_bgm(self, path: str, loop: bool = True) -> None:
        if not path:
            return
        if path == self._current_bgm:
            return
        if not self.enabled:
            self._current_bgm = path
            return
        if not self._exists(path, "BGM"):
            return

        try:
            previous_bgm = self._current_bgm
            if previous_bgm:
                print(f"[BGM] switch from={previous_bgm} to={path}")
                pygame.mixer.music.fadeout(400)
            pygame.mixer.music.load(path)
            pygame.mixer.music.set_volume(self.bgm_volume)
            pygame.mixer.music.play(-1 if loop else 0)
            self._current_bgm = path
            print(f"[BGM] play path={path}")
        except pygame.error as exc:
            self._warn_once(path, f"[BGM][WARN] failed load {path}: {exc}")

    def stop_bgm(self) -> None:
        if self.enabled:
            pygame.mixer.music.stop()
        self._current_bgm = ""

    def fadeout_bgm(self, ms: int = 500) -> None:
        if self.enabled:
            pygame.mixer.music.fadeout(max(0, int(ms)))
        self._current_bgm = ""

    def set_sfx_volume(self, volume: float) -> None:
        self.sfx_volume = self._clamp_volume(volume)

    def set_voice_volume(self, volume: float) -> None:
        self.voice_volume = self._clamp_volume(volume)

    def set_bgm_volume(self, volume: float) -> None:
        self.bgm_volume = self._clamp_volume(volume)
        if self.enabled:
            pygame.mixer.music.set_volume(self.bgm_volume)

    def _init_mixer(self) -> None:
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()
            pygame.mixer.set_num_channels(max(16, pygame.mixer.get_num_channels()))
            self._voice_channel = pygame.mixer.Channel(15)
            self.enabled = True
            print("[AUDIO] mixer initialized")
        except pygame.error:
            self.enabled = False
            print("[AUDIO][WARN] mixer init failed, audio disabled")
            print("[VOICE][WARN] pygame.mixer init failed, voice disabled")

    def _resolve_sfx_path(self, name_or_path: str) -> str:
        if name_or_path in self.SFX_PATHS:
            return self.SFX_PATHS[name_or_path]
        path = Path(name_or_path)
        if path.suffix.lower() in {".wav", ".ogg"} or "/" in name_or_path or "\\" in name_or_path:
            return str(path)
        return f"assets/audio/sfx/{name_or_path}.wav"

    def _exists(self, path: str, kind: str) -> bool:
        if Path(path).exists():
            return True
        if kind == "SFX":
            self._warn_once(path, f"[SFX][WARN] missing {path}")
        elif kind == "BGM":
            self._warn_once(path, f"[BGM][WARN] missing bgm file: {path}")
        else:
            self._warn_once(path, f"[VOICE][WARN] missing {path}")
        return False

    def _voice_exists(self, path: str) -> bool:
        if Path(path).exists():
            return True
        self._warn_once(path, f"[VOICE][WARN] missing voice file: {path}")
        return False

    def _warn_once(self, key: str, message: str) -> None:
        if key in self._warned_missing:
            return
        self._warned_missing.add(key)
        print(message)

    def _clamp_volume(self, volume: float) -> float:
        return max(0.0, min(1.0, float(volume)))
