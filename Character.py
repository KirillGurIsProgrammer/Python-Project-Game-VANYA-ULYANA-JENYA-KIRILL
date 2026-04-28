import pygame
from animations import Animations

class Character:
    def __init__(self, screen):
        self.screen = screen
        self.x = 500
        self.y = 200
        self.speed = 4

        self.animations = Animations()
        self.image = self.animations.get_idle()

    def movement(self):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_d]:
            self.x += self.speed
            self.image = self.animations.get_right()

        elif keys[pygame.K_a]:
            self.x -= self.speed
            self.image = self.animations.get_left()

        elif keys[pygame.K_s]:
            self.y += self.speed
            self.image = self.animations.get_down()

        elif keys[pygame.K_w]:
            self.y -= self.speed
            self.image = self.animations.get_up()

        else:
            self.image = self.animations.get_idle()

    def draw(self, camera_x, camera_y):
        self.screen.blit(
            self.image,
            (self.x - camera_x, self.y - camera_y)
        )


class Nerd(Character):
    def __init__(self, screen):
        super().__init__(screen)