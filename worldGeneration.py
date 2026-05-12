import pygame
import random


class WorldGeneration:
    def __init__(self, cameraX, cameraY):
        self.cameraX = cameraX
        self.cameraY = cameraY
        self.grass = pygame.image.load("/Users/kirillgurev/PycharmProjects/ProjectFefuBridge/images/png-klev-club-adfx-p-pikselnaya-trava-png-4.png")
        self.water = pygame.image.load("/Users/kirillgurev/PycharmProjects/ProjectFefuBridge/images/istockphoto-997807300-612x612.jpg")
        self.floor = pygame.image.load("/Users/kirillgurev/PycharmProjects/ProjectFefuBridge/images/ah604tyj1y951.jpg")
        self.tsize = 50
        self.sizeX = 128
        self.sizeY = 128
        self.map = []
        self.generation()

    def generation(self):
        self.map = []
        for x in range(self.sizeX):
            row = []
            for y in range(self.sizeY):
                row.append(random.choice([self.floor]))
            self.map.append(row)

    def drawing(self, screen):
        for x in range(self.sizeX):
            for y in range(self.sizeY):
                image = self.map[x][y]
                screen.blit(image, (
                    self.tsize * x - self.cameraX,
                    self.tsize * y - self.cameraY
                ))