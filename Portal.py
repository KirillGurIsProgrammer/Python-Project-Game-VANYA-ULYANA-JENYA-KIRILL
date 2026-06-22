import pygame
import math
import random


class Portal:
    """
    Портал появляется в центре указанной комнаты после очистки всех комнат.
    Анимируется вращающимися кольцами.
    При касании игрока возвращает True из метода update().
    """

    RADIUS = 30
    TOUCH_RADIUS = 32

    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y
        self._angle = 0.0
        # Частицы для эффекта
        self._particles = [
            [random.uniform(0, 360), random.uniform(10, self.RADIUS)]
            for _ in range(12)
        ]

    def update(self, player_rect: pygame.Rect) -> bool:
        """Обновляет анимацию. Возвращает True если игрок вошёл в портал."""
        self._angle = (self._angle + 3) % 360
        for p in self._particles:
            p[0] = (p[0] + 2) % 360  # вращаем частицу

        cx = player_rect.centerx
        cy = player_rect.centery
        return math.hypot(cx - self.x, cy - self.y) < self.TOUCH_RADIUS

    def draw(self, screen: pygame.Surface, camera_x: int, camera_y: int):
        sx = int(self.x - camera_x)
        sy = int(self.y - camera_y)

        # Полупрозрачная заливка
        surf = pygame.Surface((self.RADIUS * 2 + 4, self.RADIUS * 2 + 4), pygame.SRCALPHA)
        pygame.draw.circle(surf, (100, 0, 220, 110),
                           (self.RADIUS + 2, self.RADIUS + 2), self.RADIUS)
        screen.blit(surf, (sx - self.RADIUS - 2, sy - self.RADIUS - 2))

        # Три вращающихся кольца разного цвета и размера
        rings = [
            (self.RADIUS,      (180,  60, 255), self._angle),
            (self.RADIUS - 9,  (100, 180, 255), -self._angle * 1.5),
            (self.RADIUS - 18, (255, 255, 255), self._angle * 2),
        ]
        for r, color, angle in rings:
            ox = int(math.cos(math.radians(angle)) * 3)
            oy = int(math.sin(math.radians(angle)) * 3)
            pygame.draw.circle(screen, color, (sx + ox, sy + oy), r, 3)

        # Вращающиеся частицы вокруг портала
        for angle_deg, dist in self._particles:
            px = sx + int(math.cos(math.radians(angle_deg)) * dist)
            py = sy + int(math.sin(math.radians(angle_deg)) * dist)
            pygame.draw.circle(screen, (200, 150, 255), (px, py), 2)