import pygame
class Character:
    def __init__(self, name, image, speed):
        self.name = name
        self.x = 500
        self.y = 200
        self.image = image
        self.speed = speed

    def movement(self):
        clicked = pygame.key.get_pressed()
        if clicked[pygame.K_d]:
            self.x += self.speed
        if clicked[pygame.K_a]:
            self.x -= self.speed
        if clicked[pygame.K_w]:
            self.y -= self.speed
        if clicked[pygame.K_s]:
            self.y += self.speed


class Nerd(Character):
    def __init__(self):
        super().__init__(name="Ботан",
                         image=pygame.image.load('Снимок экрана 2026-03-01 в 23.36.28.png'),
                         speed=0.3)

    def showTheMovementX(self):
        return self.x

    def showTheMovementY(self):
        return self.y

    def showTheImage(self):
        return self.image