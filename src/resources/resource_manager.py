from pathlib import Path

import pygame

from src.ui.fonts import load_chinese_font


class ResourceManager:
    """Loads shared resources with safe fallbacks."""

    def load_font(self, size: int) -> pygame.font.Font:
        return load_chinese_font(size)

    def load_image(self, path: Path, size: tuple[int, int] | None = None) -> pygame.Surface | None:
        if not path.exists():
            print(f"[ResourceManager] warning: 图片不存在: {path}")
            return None
        try:
            image = pygame.image.load(str(path)).convert_alpha()
        except pygame.error as exc:
            print(f"[ResourceManager] warning: 图片加载失败: {path}, error={exc}")
            return None
        if size is not None:
            return pygame.transform.smoothscale(image, size)
        return image
