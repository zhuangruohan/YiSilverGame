import pygame

from settings import SCREEN_HEIGHT, SCREEN_WIDTH


class Camera:
    """负责摄像机偏移、跟随和世界坐标到屏幕坐标的转换。"""

    def __init__(self, map_width: int, map_height: int) -> None:
        self.map_width = map_width
        self.map_height = map_height
        self.camera_x = 0
        self.camera_y = 0
        print(
            "[Camera] 摄像机边界范围: "
            f"0 <= x <= {max(0, self.map_width - SCREEN_WIDTH)}, "
            f"0 <= y <= {max(0, self.map_height - SCREEN_HEIGHT)}"
        )

    def update(self, target_rect: pygame.Rect) -> None:
        target_x = target_rect.centerx - SCREEN_WIDTH // 2
        target_y = target_rect.centery - SCREEN_HEIGHT // 2

        max_x = max(0, self.map_width - SCREEN_WIDTH)
        max_y = max(0, self.map_height - SCREEN_HEIGHT)

        self.camera_x = max(0, min(target_x, max_x))
        self.camera_y = max(0, min(target_y, max_y))

    def apply_rect(self, rect: pygame.Rect) -> pygame.Rect:
        return rect.move(-self.camera_x, -self.camera_y)

    def world_to_screen(self, x: int, y: int) -> tuple[int, int]:
        return x - self.camera_x, y - self.camera_y
