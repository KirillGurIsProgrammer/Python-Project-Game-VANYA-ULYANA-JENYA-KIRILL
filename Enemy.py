import pygame
class Enemy:
    def __init__(self, screen, hp, attack):
        self.image = pygame.image.load("/Users/kirillgurev/PycharmProjects/ProjectFefuBridge/images/tumblr_mjpz8fWmWp1r413h3o1_400.jpg")
        self.screen = screen
        self.hp = hp
        self.attack = attack
        self.x = 450
        self.y = 200
class Zombie(Enemy):
    def __init__(self, screen):
        super().__init__(screen, 50,5)
    def drawing(self, camera_x, camera_y, xCharacter, yCharacter):
        self.screen.blit(
            self.image,
            (self.x - camera_x, self.y - camera_y)
        )











