from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class DialogueManager:
    """Loads simple NPC dialogue lines and tracks the active conversation."""

    DEFAULT_TEXT = "……"
    NPC_NAME_MAP = {
        "elder": "村寨长者",
        "silversmith": "银匠",
        "smith": "银匠",
        "market_auntie": "集市阿姨",
        "festival_host": "节庆主持人",
        "host": "节庆主持人",
        "child": "小朋友",
        "shadow_spirit": "影纹",
    }

    def __init__(self, path: Path | str = "data/dialogues.json") -> None:
        self.path = Path(path)
        self.dialogues = self._load_dialogues()
        self.active_npc_id = ""
        self.active_name = ""
        self.active_lines: list[str] = []
        self.active_voices: list[str] = []
        self.active_index = 0
        self.last_missing_dialogue = False

    def start(self, npc_id: str, fallback_name: str = "NPC", fallback_line: str = "") -> tuple[str, str]:
        self.active_npc_id = str(npc_id)
        record = self.dialogues.get(self.active_npc_id)
        self.active_name = self.resolve_name(self.active_npc_id, fallback_name)
        self.active_lines = []
        self.active_voices = []

        if isinstance(record, dict):
            raw_lines = record.get("default", [])
            if isinstance(raw_lines, (str, dict)):
                raw_lines = [raw_lines]
            if isinstance(raw_lines, list):
                self._load_lines(raw_lines)

        if not self.active_lines and fallback_line:
            self.active_lines = [str(fallback_line)]
            self.active_voices = [""]

        self.last_missing_dialogue = not self.active_lines
        if self.last_missing_dialogue:
            self.active_lines = [self.DEFAULT_TEXT]
            self.active_voices = [""]
        self.active_index = 0
        return self.current()

    def resolve_name(self, npc_id: str, fallback_name: str = "") -> str:
        npc_id = str(npc_id or "")
        fallback_name = str(fallback_name or "").strip()
        invalid_names = {"", "none", "null", "npc"}
        if fallback_name.lower() not in invalid_names:
            return fallback_name

        record = self.dialogues.get(npc_id)
        if isinstance(record, dict):
            dialogue_name = str(record.get("name") or "").strip()
            if dialogue_name:
                return dialogue_name

        mapped_name = self.NPC_NAME_MAP.get(npc_id)
        if mapped_name:
            return mapped_name
        return npc_id or "NPC"

    def current(self) -> tuple[str, str]:
        if not self.active_lines:
            return self.active_name or "NPC", self.DEFAULT_TEXT
        return self.active_name or "NPC", self.active_lines[self.active_index]

    def current_voice(self) -> str:
        if not self.active_voices or self.active_index >= len(self.active_voices):
            return ""
        return self.active_voices[self.active_index]

    def next(self) -> bool:
        """Advance to the next line. Returns False when the dialogue is complete."""

        if not self.active_lines:
            return False
        if self.active_index + 1 >= len(self.active_lines):
            return False
        self.active_index += 1
        return True

    def close(self) -> None:
        self.active_npc_id = ""
        self.active_name = ""
        self.active_lines = []
        self.active_voices = []
        self.active_index = 0
        self.last_missing_dialogue = False

    def _load_lines(self, raw_lines: list[Any]) -> None:
        for raw_line in raw_lines:
            if isinstance(raw_line, str):
                text = raw_line.strip()
                voice = ""
            elif isinstance(raw_line, dict):
                text = str(raw_line.get("text") or "").strip()
                voice = str(raw_line.get("voice") or "").strip()
            else:
                text = str(raw_line).strip()
                voice = ""
            if not text:
                continue
            self.active_lines.append(text)
            self.active_voices.append(voice)

    def _load_dialogues(self) -> dict:
        if not self.path.exists():
            print(f"[DialogueManager][WARN] missing dialogue file: {self.path}")
            return {}

        try:
            with self.path.open("r", encoding="utf-8") as file:
                data = json.load(file)
        except (OSError, json.JSONDecodeError) as exc:
            print(f"[DialogueManager][WARN] failed to load {self.path}: {exc}")
            return {}

        if not isinstance(data, dict):
            print(f"[DialogueManager][WARN] invalid dialogue root: {self.path}")
            return {}
        return data
