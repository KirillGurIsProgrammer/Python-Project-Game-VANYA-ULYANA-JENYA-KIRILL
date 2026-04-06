import pygame
class Gun:
    def __init__(self, x, y, screen):
        self.screen = screen
        self.bullet = pygame.Surface((7, 7))
        self.bullet.fill((252, 252, 3))
        self.startX = x
        self.startY = y
        self.x = x
        self.y = y
        self.bulletStatus = False

    def bulletMove(self):
        if self.bulletStatus:
            self.screen.blit(self.bullet, (self.x, self.y))
            self.x += 0.5
    def startBulletMovement(self, playerX, playerY):
        if not self.bulletStatus:
            self.x = playerX + 50
            self.y = playerY + 25
            self.bulletStatus = True

    def showTheStatus(self):
        return self.bulletStatus