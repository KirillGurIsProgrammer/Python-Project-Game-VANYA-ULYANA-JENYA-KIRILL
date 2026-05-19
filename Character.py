import pygame
from animations import Animations

class Character:
    def __init__(self, screen, hp):
        self.hp = hp
        self.screen = screen
        self.x = 500
        self.y = 200
        self.speed = 4

        self.animations = Animations()
        self.image = self.animations.get_idle()
        self.rect = self.image.get_rect(topleft=(self.x, self.y)).inflate(-20, -10)

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

        self.rect.topleft = (self.x + 10, self.y + 5)


    def draw(self, camera_x, camera_y):
        self.screen.blit(
            self.image,
            (self.x - camera_x, self.y - camera_y)
        )
        pygame.draw.rect(self.screen, (0, 255, 0), self.rect.move(-camera_x, -camera_y), 2)



class Nerd(Character):
    def __init__(self, screen):
        super().__init__(screen, 100)