import pygame
import math

from Character import Nerd
from Enemy import Zombie
from Gun import Gun, MagicStick
from Portal import Portal
from worldGeneration import WorldGeneration

#  Инициализация                                                       #

pygame.init()
clock = pygame.time.Clock()

WIDTH, HEIGHT = 1024, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Running through the fog — DVFU EDITION")
pygame.display.set_icon(pygame.image.load("images/golden-gate.png"))

font = pygame.font.SysFont(None, 36)

#  Вспомогательные функции                                            #

def spawn_zombies(world: WorldGeneration, screen: pygame.Surface,
                  spawn_x: float, spawn_y: float,
                  count_per_room: int = 3,
                  safe_radius: float = 200.0) -> list:
    zombies = []
    for i, room in enumerate(world.rooms):
        points = room.get_random_spawns(count_per_room, world.TILE_SIZE)
        for sx, sy in points:
            if i == 0 and math.hypot(sx - spawn_x, sy - spawn_y) < safe_radius:
                continue
            z = Zombie(screen)
            z.world = world
            z.x, z.y = sx, sy
            z._update_rect()
            zombies.append(z)
            room.enemies.append(z)
    return zombies


def load_level(level_num: int, hero=None):
    """Создаёт новый мир, спавнит зомби, сохраняет HP героя между уровнями."""
    world = WorldGeneration()
    spawn_x, spawn_y = world.get_spawn()

    if hero is None:
        hero = Nerd(screen)
    # Переставляем героя на новый спавн, мир и HP не трогаем
    hero.world = world
    hero.x, hero.y = float(spawn_x), float(spawn_y)

    zombies = spawn_zombies(world, screen, spawn_x, spawn_y)
    portal = None   # появится когда все комнаты очищены

    return world, hero, zombies, portal

#  Старт игры                                                          #

level = 1
world, hero, zombies, portal = load_level(level)
gun = MagicStick()
projectiles: list = []

#  Игровой цикл                                                       #

run = True
while run:
    dt = clock.tick(60) / 1000.0

    # --- Портал: появляется когда все комнаты очищены ---
    if portal is None and world.all_rooms_cleared():
        px, py = world.get_portal_position()
        portal = Portal(px, py)

    # --- События ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            cam_x = int(hero.x) - WIDTH  // 2
            cam_y = int(hero.y) - HEIGHT // 2
            mx, my = pygame.mouse.get_pos()
            new_bullets = gun.shoot(
                hero.x + hero.hb_ox + hero.hb_w // 2,
                hero.y + hero.hb_oy + hero.hb_h // 2,
                mx + cam_x, my + cam_y,
            )
            projectiles.extend(new_bullets)

    # --- Обновление ---
    gun.update_cooldown(dt)
    hero.handle_input()

    alive_zombies = [z for z in zombies if z.is_alive]
    for zombie in alive_zombies:
        zombie.update(hero, alive_zombies)

    for p in projectiles:
        p.update(world)
        for zombie in alive_zombies:
            if zombie.is_alive and zombie.rect.colliderect(p.rect):
                zombie.take_damage(p.damage)
                p.alive = False
                break

    for zombie in alive_zombies:
        if zombie.is_touching(hero.rect):
            hero.take_damage(zombie.attack * dt)

    projectiles = [p for p in projectiles if p.alive]

    # Портал: обновляем и проверяем вход игрока
    if portal is not None:
        entered = portal.update(hero.rect)
        if entered:
            level += 1
            world, hero, zombies, portal = load_level(level, hero)
            projectiles = []
            gun.update_cooldown(0)  # сбрасываем кулдаун

    world.update_doors(
        hero.x + hero.hb_ox + hero.hb_w / 2,
        hero.y + hero.hb_oy + hero.hb_h / 2,
        hero.hb_w / 2,
        hero.hb_h / 2,
    )

    # --- Камера ---
    cam_x = int(hero.x) - WIDTH // 2
    cam_y = int(hero.y) - HEIGHT // 2
    world.cameraX = cam_x
    world.cameraY = cam_y

    # --- Отрисовка ---
    world.draw(screen)

    if portal is not None:
        portal.draw(screen, cam_x, cam_y)

    hero.draw(cam_x, cam_y)

    for zombie in alive_zombies:
        zombie.draw(cam_x, cam_y)

    for p in projectiles:
        p.draw(screen, cam_x, cam_y)

    # HUD
    pygame.draw.rect(screen, (150, 0, 0), (20, 20, 200, 18))
    hp_w = int(200 * hero.hp / hero.max_hp)
    pygame.draw.rect(screen, (0, 200, 0), (20, 20, hp_w, 18))
    pygame.draw.rect(screen, (255, 255, 255), (20, 20, 200, 18), 2)

    level_text = font.render(f"Level {level}", True, (255, 255, 255))
    screen.blit(level_text, (WIDTH - level_text.get_width() - 20, 20))

    pygame.display.update()

pygame.quit()