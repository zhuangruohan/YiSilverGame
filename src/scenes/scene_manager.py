from src.scenes.base_scene import BaseScene


class SceneManager:
    """Owns the current scene and keeps scene switching out of main.py."""

    def __init__(self) -> None:
        self.current_name = ""
        self.current_scene: BaseScene | None = None

    def set_scene(self, name: str, scene: BaseScene) -> None:
        self.current_name = name
        self.current_scene = scene

    def handle_event(self, event) -> bool:
        if self.current_scene is None:
            return False
        return self.current_scene.handle_event(event)

    def update(self, dt: float) -> None:
        if self.current_scene is not None:
            self.current_scene.update(dt)

    def draw(self, surface) -> None:
        if self.current_scene is not None:
            self.current_scene.draw(surface)
