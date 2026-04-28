import pygame

class Animations:
    def __init__(self):
        self.right1 = pygame.image.load('images/3 ряд 1 поза спортсмен aseprite.png')
        self.right2 = pygame.image.load('images/3 ряд 2 поза спортсмен aseprite.png')
        self.right3 = pygame.image.load('images/3 ряд 4 поза спортсмен aseprite.png')

        self.left1 = pygame.image.load('images/2 ряд 1 поза спортсмен aseprite.png')
        self.left2 = pygame.image.load('images/2 ряд 2 поза спортсмен aseprite.png')
        self.left3 = pygame.image.load('images/2 ряд 4 поза спортсмен aseprite.png')

        self.down1 = pygame.image.load('images/1 ряд 1 поза спортсмен aseprite1.png')
        self.down2 = pygame.image.load('images/1 ряд 2 поза спортсмен aseprite1.png')
        self.down3 = pygame.image.load('images/1 ряд 4 поза спортсмен aseprite1.png')

        self.up1 = pygame.image.load('images/4 ряд 1 поза спортсмен aseprite1.png')
        self.up2 = pygame.image.load('images/4 ряд 2 поза спортсмен aseprite1.png')
        self.up3 = pygame.image.load('images/4 ряд 4 поза спортсмен aseprite1.png')

        self.frame = 0

    def get_right(self):
        self.frame += 0.25
        if int(self.frame) % 3 == 0:
            return self.right1
        elif int(self.frame) % 3 == 1:
            return self.right2
        return self.right3

    def get_left(self):
        self.frame += 0.25
        if int(self.frame) % 3 == 0:
            return self.left1
        elif int(self.frame) % 3 == 1:
            return self.left2
        return self.left3

    def get_down(self):
        self.frame += 0.25
        if int(self.frame) % 3 == 0:
            return self.down1
        elif int(self.frame) % 3 == 1:
            return self.down2
        return self.down3
    def get_up(self):
        self.frame += 0.25
        if int(self.frame) % 3 == 0:
            return self.up1
        elif int(self.frame) % 3 == 1:
            return self.up2
        return self.up3


    def get_idle(self):
        return self.down1