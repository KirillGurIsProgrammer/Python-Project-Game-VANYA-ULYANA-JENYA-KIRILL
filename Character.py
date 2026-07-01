import pygame
from animations import Animations
from Entity import Entity


class Character(Entity):
    """Управляемый персонаж. Движение через WASD, анимации."""

    def __init__(self, screen: pygame.Surface, hp: int, damage: int, speed: float = 4.0):
        super().__init__(screen, hp, speed)
        self.damage = damage

        self.animations = Animations()
        self.image = self.animations.get_idle()

        # Хитбокс уже спрайта по ширине чтобы проходить в узкие коридоры
        self._setup_hitbox_from_image(margin_x=12, margin_y=4)

    def handle_input(self):
        keys = pygame.key.get_pressed()
        dx, dy = 0.0, 0.0

        if keys[pygame.K_d]:
            dx = self.speed
            self.image = self.animations.get_right()
        elif keys[pygame.K_a]:
            dx = -self.speed
            self.image = self.animations.get_left()
        elif keys[pygame.K_s]:
            dy = self.speed
            self.image = self.animations.get_down()
        elif keys[pygame.K_w]:
            dy = -self.speed
            self.image = self.animations.get_up()
        else:
            self.image = self.animations.get_idle()

        self.try_move(dx, dy)

    def draw(self, camera_x: int, camera_y: int):
        super().draw(camera_x, camera_y)
        self.draw_hitbox(camera_x, camera_y, color=(0, 255, 0))


class Nerd(Character):
    def __init__(self, screen: pygame.Surface, hp, damage):
        super().__init__(screen, hp, damage)