from Character import Nerd
from Gun import Gun
from worldGeneration import WorldGeneration
import pygame
from Enemy import Zombie

pygame.init()
clock = pygame.time.Clock()

WIDTH, HEIGHT = 1024, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Running throw the fog DVFU EDITION")

icon = pygame.image.load('images/golden-gate.png')
pygame.display.set_icon(icon)

worldGeneration = WorldGeneration(0, 0)

hero = Nerd(screen)
hero.world = worldGeneration
spawn_x, spawn_y = worldGeneration.get_spawn()
hero.x = float(spawn_x)
hero.y = float(spawn_y)

gun    = Gun(screen, 0, 0)
zombie = Zombie(screen)
zombie.world = worldGeneration
zombie.x = float(spawn_x) + 200.0
zombie.y = float(spawn_y)

run = True
while run:
    clock.tick(60)

    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            run = False
        if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
            gun.startBulletMovement(hero.x, hero.y)

    hero.movement()
    zombie.position(hero.x, hero.y)
    zombie.check_collision(hero.rect, hero)

    camera_x = int(hero.x) - WIDTH  // 2
    camera_y = int(hero.y) - HEIGHT // 2

    worldGeneration.cameraX = camera_x
    worldGeneration.cameraY = camera_y
    gun.camerax = camera_x
    gun.cameray = camera_y

    worldGeneration.drawing(screen)
    hero.draw(camera_x, camera_y)
    zombie.drawing(camera_x, camera_y, hero.x, hero.y)
    gun.bulletMove()

    pygame.display.update()

pygame.quit()