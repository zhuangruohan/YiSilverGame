import json
from pathlib import Path

from settings import DISABLED_SCENE_MAPS, SCENE_ALIASES, SCENE_MAPS, SCENES_CONFIG_PATH


class SceneRegistry:
    """Reads active/disabled scene configuration without moving map files."""

    def __init__(self, config_path: str = SCENES_CONFIG_PATH) -> None:
        self.config_path = Path(config_path)
        self.active_scenes = dict(SCENE_MAPS)
        self.disabled_scenes = dict(DISABLED_SCENE_MAPS)
        self.aliases = dict(SCENE_ALIASES)
        self._load_config()
        self._report_festival_scene()
        self._report_missing_scene_files()

    def canonical_name(self, scene_name: str) -> str:
        if scene_name in self.active_scenes or scene_name in self.disabled_scenes:
            return scene_name
        return self.aliases.get(scene_name, scene_name)

    def get_map_path(self, scene_name: str) -> str | None:
        canonical_scene_name = self.canonical_name(scene_name)
        return self.active_scenes.get(canonical_scene_name) or self.disabled_scenes.get(canonical_scene_name)

    def is_active(self, scene_name: str) -> bool:
        canonical_scene_name = self.canonical_name(scene_name)
        return canonical_scene_name in self.active_scenes or canonical_scene_name in self.disabled_scenes

    def _load_config(self) -> None:
        if not self.config_path.exists():
            print(f"[SceneRegistry] scenes config not found, using settings.py: {self.config_path}")
            return

        try:
            data = json.loads(self.config_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            print(f"[SceneRegistry] scenes config read failed, using settings.py: {exc}")
            return

        self.active_scenes = data.get("active_scenes", self.active_scenes)
        self.disabled_scenes = data.get("disabled_scenes", self.disabled_scenes)
        self.aliases = data.get("aliases", self.aliases)

    def _report_festival_scene(self) -> None:
        festival_key = "festival" if "festival" in self.active_scenes else ""
        festival_map = self.active_scenes.get("festival", "")
        if not festival_key:
            for scene_name, map_path in {**self.active_scenes, **self.disabled_scenes}.items():
                lower_name = scene_name.lower()
                lower_path = str(map_path).lower()
                if any(token in lower_name or token in lower_path for token in ("festival", "plaza", "square")):
                    festival_key = scene_name
                    festival_map = map_path
                    break

        if festival_key and festival_map:
            print(f"[FESTIVAL] detected scene_key={festival_key} map={festival_map}")

        for alias in ("festival_square", "festival_plaza", "festival_scene", "plaza"):
            if self.aliases.get(alias) == "festival":
                print(f"[FESTIVAL] alias {alias} -> festival")

    def _report_missing_scene_files(self) -> None:
        for scene_name, map_path in {**self.active_scenes, **self.disabled_scenes}.items():
            if not Path(map_path).exists():
                print(f"[SceneRegistry] warning: scene file not found: {scene_name} -> {map_path}")
