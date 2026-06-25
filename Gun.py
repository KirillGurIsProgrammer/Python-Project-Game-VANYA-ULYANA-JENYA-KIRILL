import pygame
import math
from abc import ABC, abstractmethod


class Projectile:
    """Один снаряд."""

    SIZE = 7

    def __init__(self, x: float, y: float, dx: float, dy: float,
                 damage: int, color: tuple[int, int, int], speed: float = 12.0, max_range: float = 1500.0):
        self.x, self.y = x, y
        self.dx, self.dy = dx, dy
        self.damage = damage
        self.speed = speed
        self.max_range = max_range
        self.traveled = 0.0
        self.alive = True
        self.rect = pygame.Rect(int(x), int(y), self.SIZE, self.SIZE)
        self.color = color

    def update(self, world=None):
        self.x += self.dx * self.speed
        self.y += self.dy * self.speed
        self.traveled += self.speed
        self.rect.topleft = (int(self.x) - self.SIZE // 2, int(self.y) - self.SIZE // 2)
        if (world and world.is_wall(self.x, self.y)) or self.traveled >= self.max_range:
            self.alive = False

    def draw(self, screen: pygame.Surface, camera_x: int, camera_y: int):
        pygame.draw.circle(
            screen, self.color,
            (int(self.x - camera_x), int(self.y - camera_y)),
            self.SIZE // 2,
        )


class Weapon(ABC):
    def __init__(self, damage: int, fire_rate: float):
        self.damage = damage
        self.fire_rate = fire_rate
        self._cooldown = 0.0

    @abstractmethod
    def shoot(self, ox: float, oy: float, tx: float, ty: float) -> list:
        ...

    def update_cooldown(self, dt: float):
        if self._cooldown > 0:
            self._cooldown -= dt

    @property
    def ready(self) -> bool:
        return self._cooldown <= 0


class Gun(Weapon):
    def __init__(self, damage: int = 10, fire_rate: float = 5.0):
        super().__init__(damage, fire_rate)

    def shoot(self, ox: float, oy: float, tx: float, ty: float) -> list:
        if not self.ready:
            return []
        dx, dy = tx - ox, ty - oy
        dist = math.hypot(dx, dy)
        if dist == 0:
            return []
        self._cooldown = 1.0 / self.fire_rate
        return [Projectile(ox, oy, dx / dist, dy / dist, self.damage, color = (255, 220, 0))]
class MagicStick(Weapon):
    def __init__(self, damage: int = 10,fire_rate: float = 5.0):
        super().__init__(damage, fire_rate)
    def shoot(self, ox: float, oy: float, tx: float, ty: float) -> list:
        if not self.ready:
            return []
        dx, dy = tx - ox, ty - oy
        dist = math.hypot(dx, dy)
        if dist == 0:
            return []
        self._cooldown = 1.0 / self.fire_rate
        return [Projectile(ox, oy, dx / dist, dy / dist, self.damage, (0,0,255))]




