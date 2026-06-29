from __future__ import annotations

import math
import random
import struct
import sys
import wave
from pathlib import Path


SAMPLE_RATE = 22050
OUTPUT_DIR = Path("assets/audio/bgm")


def clamp_sample(value: float) -> int:
    return max(-32767, min(32767, int(value * 32767)))


def sine(freq: float, t: float) -> float:
    return math.sin(2.0 * math.pi * freq * t)


def soft_square(freq: float, t: float) -> float:
    return math.tanh(2.2 * sine(freq, t))


def note_freq(note: int) -> float:
    return 440.0 * (2.0 ** ((note - 69) / 12.0))


def envelope(local_t: float, length: float, attack: float = 0.03, release: float = 0.08) -> float:
    if local_t < attack:
        return local_t / max(attack, 0.001)
    remaining = length - local_t
    if remaining < release:
        return max(0.0, remaining / max(release, 0.001))
    return 1.0


def write_wav(path: Path, samples: list[float], force: bool = False) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and path.stat().st_size > 0 and not force:
        print(f"[BGM_GEN] exists {path.as_posix()}")
        return
    temp_path = path.with_suffix(path.suffix + ".tmp")
    with wave.open(str(temp_path), "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(SAMPLE_RATE)
        frames = b"".join(struct.pack("<h", clamp_sample(sample)) for sample in samples)
        wav_file.writeframes(frames)
    temp_path.replace(path)
    print(f"[BGM_GEN] generated {path.as_posix()}")


def mix_chord(t: float, notes: tuple[int, ...], octave_shift: int = 0) -> float:
    total = 0.0
    for index, note in enumerate(notes):
        freq = note_freq(note + octave_shift)
        total += sine(freq, t) * (0.55 / (index + 1))
    return total / max(1, len(notes))


def generate_village(duration: float = 20.0) -> list[float]:
    chords = [
        (57, 60, 64),
        (55, 59, 62),
        (53, 57, 60),
        (55, 59, 62),
    ]
    melody = [72, 74, 76, 79, 76, 74, 72, 69]
    samples: list[float] = []
    for i in range(int(duration * SAMPLE_RATE)):
        t = i / SAMPLE_RATE
        bar = int(t // 3.0) % len(chords)
        beat_t = t % 3.0
        chord = mix_chord(t, chords[bar]) * 0.18
        bass = sine(note_freq(chords[bar][0] - 12), t) * 0.08
        step = int((t * 2.0) % len(melody))
        pluck_t = (t * 2.0) % 1.0
        pluck_env = math.exp(-pluck_t * 5.0) * envelope(pluck_t, 1.0, 0.01, 0.2)
        pluck = sine(note_freq(melody[step]), t) * 0.12 * pluck_env
        shimmer = sine(1760.0, t) * 0.015 * (0.5 + 0.5 * sine(0.25, t + beat_t))
        samples.append((chord + bass + pluck + shimmer) * 0.55)
    return samples


def generate_battle(duration: float = 20.0) -> list[float]:
    random.seed(22)
    pulse_notes = [45, 45, 48, 43, 45, 50, 48, 43]
    samples: list[float] = []
    for i in range(int(duration * SAMPLE_RATE)):
        t = i / SAMPLE_RATE
        step = int(t * 4.0) % len(pulse_notes)
        step_t = (t * 4.0) % 1.0
        bass_env = math.exp(-step_t * 4.0)
        bass = soft_square(note_freq(pulse_notes[step]), t) * 0.24 * bass_env
        drone = sine(note_freq(33), t) * 0.09 + sine(note_freq(45), t) * 0.05
        tick = 0.0
        if step_t < 0.07:
            noise = random.uniform(-1.0, 1.0)
            tick = noise * (1.0 - step_t / 0.07) * 0.07
        tension = sine(note_freq(69), t) * 0.025 * (0.5 + 0.5 * sine(0.6, t))
        samples.append((bass + drone + tick + tension) * 0.62)
    return samples


def generate_festival(duration: float = 20.0) -> list[float]:
    chords = [
        (60, 64, 67),
        (62, 65, 69),
        (67, 71, 74),
        (64, 67, 72),
    ]
    melody = [72, 76, 79, 84, 83, 79, 76, 74]
    samples: list[float] = []
    for i in range(int(duration * SAMPLE_RATE)):
        t = i / SAMPLE_RATE
        bar = int(t // 2.0) % len(chords)
        chord = mix_chord(t, chords[bar]) * 0.2
        bass = sine(note_freq(chords[bar][0] - 12), t) * 0.09
        step = int(t * 3.0) % len(melody)
        step_t = (t * 3.0) % 1.0
        bell_env = math.exp(-step_t * 4.2)
        bell = (
            sine(note_freq(melody[step]), t) * 0.12
            + sine(note_freq(melody[step] + 12), t) * 0.045
        ) * bell_env
        hand_drum = 0.0
        drum_t = (t * 2.0) % 1.0
        if drum_t < 0.12:
            hand_drum = sine(95.0, t) * (1.0 - drum_t / 0.12) * 0.08
        samples.append((chord + bass + bell + hand_drum) * 0.58)
    return samples


def main() -> None:
    force = "--force" in sys.argv
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    write_wav(OUTPUT_DIR / "village.wav", generate_village(), force)
    write_wav(OUTPUT_DIR / "battle.wav", generate_battle(), force)
    write_wav(OUTPUT_DIR / "festival.wav", generate_festival(), force)


if __name__ == "__main__":
    main()
