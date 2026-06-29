from __future__ import annotations

import math
import random
import struct
import wave
from pathlib import Path


SAMPLE_RATE = 44100
OUT_DIR = Path("assets/audio/sfx")


def envelope(index: int, total: int, attack: float = 0.05, release: float = 0.28) -> float:
    progress = index / max(1, total - 1)
    if progress < attack:
        return progress / max(attack, 0.001)
    if progress > 1.0 - release:
        return max(0.0, (1.0 - progress) / max(release, 0.001))
    return 1.0


def tone(duration: float, start_freq: float, end_freq: float | None = None, volume: float = 0.35) -> list[float]:
    count = int(SAMPLE_RATE * duration)
    end = start_freq if end_freq is None else end_freq
    phase = 0.0
    samples: list[float] = []
    for index in range(count):
        progress = index / max(1, count - 1)
        freq = start_freq + (end - start_freq) * progress
        phase += math.tau * freq / SAMPLE_RATE
        samples.append(math.sin(phase) * envelope(index, count) * volume)
    return samples


def noise_burst(duration: float, volume: float = 0.25) -> list[float]:
    count = int(SAMPLE_RATE * duration)
    return [(random.uniform(-1.0, 1.0) * envelope(index, count, 0.01, 0.65) * volume) for index in range(count)]


def mix(*tracks: list[float]) -> list[float]:
    length = max((len(track) for track in tracks), default=0)
    output = [0.0] * length
    for track in tracks:
        for index, value in enumerate(track):
            output[index] += value
    peak = max((abs(value) for value in output), default=1.0)
    scale = 0.82 / peak if peak > 0.82 else 1.0
    return [value * scale for value in output]


def concat(*tracks: list[float]) -> list[float]:
    output: list[float] = []
    for track in tracks:
        output.extend(track)
    return output


def write_wav(path: Path, samples: list[float]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(path), "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(SAMPLE_RATE)
        frames = bytearray()
        for sample in samples:
            value = int(max(-1.0, min(1.0, sample)) * 32767)
            frames.extend(struct.pack("<h", value))
        wav.writeframes(frames)
    print(f"[SFX_GEN] generated {path.as_posix()}")


def make_collect() -> list[float]:
    return concat(tone(0.07, 760, 1080, 0.32), tone(0.10, 1120, 1550, 0.26))


def make_purify() -> list[float]:
    shimmer = mix(tone(0.42, 360, 920, 0.28), tone(0.42, 720, 1380, 0.14))
    return shimmer


def make_hit_shadow() -> list[float]:
    return mix(noise_burst(0.16, 0.35), tone(0.18, 180, 95, 0.28), tone(0.10, 860, 420, 0.16))


def make_player_hit() -> list[float]:
    return mix(tone(0.24, 170, 72, 0.42), noise_burst(0.10, 0.18))


def make_victory() -> list[float]:
    return concat(tone(0.16, 520, 620, 0.30), tone(0.16, 660, 760, 0.30), tone(0.25, 880, 1180, 0.34))


def make_fail() -> list[float]:
    return concat(tone(0.18, 360, 240, 0.34), tone(0.30, 230, 105, 0.38))


def make_inventory() -> list[float]:
    return mix(tone(0.12, 420, 520, 0.22), tone(0.12, 840, 740, 0.10))


def make_festival_success() -> list[float]:
    return concat(
        mix(tone(0.18, 520, 720, 0.26), tone(0.18, 1040, 1260, 0.10)),
        mix(tone(0.18, 660, 880, 0.28), tone(0.18, 1320, 1520, 0.12)),
        mix(tone(0.36, 880, 1320, 0.32), tone(0.36, 1760, 2050, 0.12)),
    )


def make_ui_confirm() -> list[float]:
    return tone(0.08, 900, 1180, 0.18)


def main() -> None:
    generators = {
        "collect.wav": make_collect,
        "purify.wav": make_purify,
        "hit_shadow.wav": make_hit_shadow,
        "player_hit.wav": make_player_hit,
        "victory.wav": make_victory,
        "fail.wav": make_fail,
        "inventory.wav": make_inventory,
        "festival_success.wav": make_festival_success,
        "ui_confirm.wav": make_ui_confirm,
    }
    for filename, generator in generators.items():
        write_wav(OUT_DIR / filename, generator())


if __name__ == "__main__":
    main()
