from Character import Nerd
from Gun import Gun
import pygame

pygame.init()
screen = pygame.display.set_mode((1024, 700))
pygame.display.set_caption("Running throw the fog DVFU EDITION")
icon = pygame.image.load('golden-gate.png')
backGround = pygame.image.load('ChatGPT Image 1 марта 2026 г., 23_28_25.png')

pygame.display.set_icon(icon)
run = True

hero = Nerd()
gun = Gun(hero.showTheMovementX(), hero.showTheMovementY(), screen)

while run:
    screen.blit(backGround, (0, 0))
    screen.blit(hero.showTheImage(), (hero.showTheMovementX(), hero.showTheMovementY()))

    hero.movement()


    if gun.showTheStatus():
        gun.bulletMove()
        if gun.x > 1024:
            gun.bulletStatus = False

    pygame.display.update()

    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            run = False
        if e.type == pygame.MOUSEBUTTONDOWN:
            if e.button == 1:
                gun.startBulletMovement(hero.showTheMovementX(), hero.showTheMovementY())

pygame.quit()
