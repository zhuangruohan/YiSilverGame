import pygame

from src.resources.animation import AnimationController


PLAYER_IMAGE_OFFSET_X = 0
PLAYER_IMAGE_OFFSET_Y = 0


class Player:
    """Player owns movement, collision rect and four-direction animation state."""

    IMAGE_HEIGHT = 72

    def __init__(self, x: int, y: int) -> None:
        self.rect = pygame.Rect(x, y, 32, 32)
        self.world_x = x
        self.world_y = y
        self.speed = 4
        self.color = (230, 230, 245)
        self.facing = "down"
        self.direction = "down"
        self.animation_state = "idle"
        self.animation = AnimationController.for_player(self.IMAGE_HEIGHT)

    def update(
        self,
        collision_rects: list[pygame.Rect],
        map_width: int,
        map_height: int,
        dt: float = 0,
    ) -> None:
        keys = pygame.key.get_pressed()
        dx = 0
        dy = 0

        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            dx -= self.speed
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            dx += self.speed
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            dy -= self.speed
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            dy += self.speed

        self._update_facing(dx, dy)
        self._move_axis(dx, 0, collision_rects, map_width, map_height)
        self._move_axis(0, dy, collision_rects, map_width, map_height)
        self.world_x = self.rect.x
        self.world_y = self.rect.y
        self.direction = self.facing
        self.animation_state = "walk" if dx != 0 or dy != 0 else "idle"
        self.animation.set_motion(self.direction, self.animation_state == "walk")
        self.animation.update(dt)

    def _update_facing(self, dx: int, dy: int) -> None:
        if abs(dx) > abs(dy):
            self.facing = "left" if dx < 0 else "right"
        elif dy < 0:
            self.facing = "up"
        elif dy > 0:
            self.facing = "down"

    def _move_axis(
        self,
        dx: int,
        dy: int,
        collision_rects: list[pygame.Rect],
        map_width: int,
        map_height: int,
    ) -> None:
        if dx == 0 and dy == 0:
            return

        next_rect = self.rect.move(dx, dy)
        next_rect.clamp_ip(pygame.Rect(0, 0, map_width, map_height))

        if next_rect.collidelist(collision_rects) != -1:
            return

        self.rect = next_rect

    def draw(self, surface: pygame.Surface, camera) -> None:
        image = self.animation.current_frame()
        if image is not None:
            screen_rect = camera.apply_rect(self.rect)
            image_rect = image.get_rect(midbottom=screen_rect.midbottom)
            image_rect.x += PLAYER_IMAGE_OFFSET_X
            image_rect.y += PLAYER_IMAGE_OFFSET_Y
            surface.blit(image, image_rect)
            return

        self.draw_collision_debug(surface, camera)

    def draw_collision_debug(self, surface: pygame.Surface, camera) -> None:
        screen_rect = camera.apply_rect(self.rect)
        pygame.draw.rect(surface, self.color, screen_rect)
        pygame.draw.rect(surface, (70, 60, 90), screen_rect, 2)
