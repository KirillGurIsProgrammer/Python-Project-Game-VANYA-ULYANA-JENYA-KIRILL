import pygame
from animations import Animations
from Entity import Entity
from sound_manager import SoundManager


class Character(Entity):
    STEP_INTERVAL_FRAMES = 18

    def __init__(self, screen: pygame.Surface, hp: int, damage: int, speed: float = 4.0):
        super().__init__(screen, hp, speed)
        self.damage = damage

        self.animations = Animations()
        self.image = self.animations.get_idle()

        self.sound = SoundManager()
        self._step_counter = 0

        self._setup_hitbox_from_image(margin_x=12, margin_y=4)

    def handle_input(self):
        keys = pygame.key.get_pressed()
        dx, dy = 0.0, 0.0
        moving = False

        if keys[pygame.K_d]:
            dx = self.speed
            self.image = self.animations.get_right()
            moving = True
        elif keys[pygame.K_a]:
            dx = -self.speed
            self.image = self.animations.get_left()
            moving = True
        elif keys[pygame.K_s]:
            dy = self.speed
            self.image = self.animations.get_down()
            moving = True
        elif keys[pygame.K_w]:
            dy = -self.speed
            self.image = self.animations.get_up()
            moving = True
        else:
            self.image = self.animations.get_idle()

        if moving:
            self._step_counter += 1
            if self._step_counter >= self.STEP_INTERVAL_FRAMES:
                self._step_counter = 0
                self.sound.play_step()
        else:
            self._step_counter = 0

        self.try_move(dx, dy)

    def draw(self, camera_x: int, camera_y: int):
        super().draw(camera_x, camera_y)
        #self.draw_hitbox(camera_x, camera_y, color=(0, 255, 0))


class Nerd(Character):
    def __init__(self, screen: pygame.Surface, hp, damage):
        super().__init__(screen, hp, damage)