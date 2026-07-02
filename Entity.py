import pygame
import math


class Entity:

    def __init__(self, screen: pygame.Surface, hp: int, speed: float):
        self.screen = screen
        self.hp = hp
        self.max_hp = hp
        self.speed = speed
        self.x = 0.0
        self.y = 0.0
        self.world = None
        self.image: pygame.Surface | None = None

        self.hb_ox = 0
        self.hb_oy = 0
        self.hb_w = 32
        self.hb_h = 32
        self.rect = pygame.Rect(0, 0, self.hb_w, self.hb_h)
        self._update_rect()

    def _setup_hitbox_from_image(self, margin_x: int = 4, margin_y: int = 4):
        if self.image is None:
            return
        iw = self.image.get_width()
        ih = self.image.get_height() - 10
        self.hb_ox = margin_x
        self.hb_oy = margin_y
        self.hb_w = iw - margin_x * 2
        self.hb_h = ih - margin_y * 2
        self.rect = pygame.Rect(0, 0, self.hb_w, self.hb_h)
        self._update_rect()

    def _update_rect(self):
        self.rect.topleft = (int(self.x) + self.hb_ox, int(self.y) + self.hb_oy)

    def _can_move(self, nx: float, ny: float) -> bool:
        if self.world is None:
            return True
        margin = 2
        corners = [
            (nx + self.hb_ox + margin,             ny + self.hb_oy + margin),
            (nx + self.hb_ox + self.hb_w - margin, ny + self.hb_oy + margin),
            (nx + self.hb_ox + margin,             ny + self.hb_oy + self.hb_h - margin),
            (nx + self.hb_ox + self.hb_w - margin, ny + self.hb_oy + self.hb_h - margin),
        ]
        return not any(self.world.is_wall(cx, cy) for cx, cy in corners)

    def try_move(self, dx: float, dy: float):
        if self._can_move(self.x + dx, self.y):
            self.x += dx
        if self._can_move(self.x, self.y + dy):
            self.y += dy
        self._update_rect()

    def move_toward(self, target_x: float, target_y: float, fear: bool):
        dx = target_x - self.x
        dy = target_y - self.y
        dist = math.hypot(dx, dy)
        if dist == 0:
            return
        direction = -1 if fear else 1
        self.try_move(direction * dx / dist * self.speed, direction* dy / dist * self.speed)

    def take_damage(self, amount: int):
        self.hp = max(0, self.hp - amount)

    @property
    def is_alive(self) -> bool:
        return self.hp > 0

    def distance_to_point(self, x: float, y: float) -> float:
        return math.hypot(self.x - x, self.y - y)

    def distance_to(self, other: "Entity") -> float:
        return self.distance_to_point(other.x, other.y)

    def draw(self, camera_x: int, camera_y: int):
        if self.image:
            self.screen.blit(self.image, (self.x - camera_x, self.y - camera_y))

    def draw_hitbox(self, camera_x: int, camera_y: int, color=(255, 0, 0)):
        pygame.draw.rect(self.screen, color, self.rect.move(-camera_x, -camera_y), 2)

    def draw_health_bar(self, camera_x: int, camera_y: int):
        bar_w, bar_h = self.hb_w, 6
        bar_x = self.x - camera_x + self.hb_ox
        bar_y = self.y - camera_y + self.hb_oy - 10
        fill_w = int(bar_w * self.hp / self.max_hp)

        pygame.draw.rect(self.screen, (200, 0, 0),    (bar_x, bar_y, bar_w,  bar_h))
        pygame.draw.rect(self.screen, (0, 200, 0),    (bar_x, bar_y, fill_w, bar_h))
        pygame.draw.rect(self.screen, (255, 255, 255), (bar_x, bar_y, bar_w,  bar_h), 1)