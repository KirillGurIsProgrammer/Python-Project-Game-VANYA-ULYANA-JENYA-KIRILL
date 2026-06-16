import pygame
import math

from Character import Nerd
from Enemy import Zombie
from Gun import Gun
from worldGeneration import WorldGeneration

# ------------------------------------------------------------------ #
#  Инициализация                                                       #
# ------------------------------------------------------------------ #

pygame.init()
clock = pygame.time.Clock()

WIDTH, HEIGHT = 1024, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Running through the fog — DVFU EDITION")
pygame.display.set_icon(pygame.image.load("images/golden-gate.png"))

# ------------------------------------------------------------------ #
#  Вспомогательные функции                                            #
# ------------------------------------------------------------------ #

def spawn_zombies(world: WorldGeneration, screen: pygame.Surface,
                  spawn_x: float, spawn_y: float,
                  count_per_room: int = 3,
                  safe_radius: float = 200.0) -> list:
    """Создаёт зомби во всех комнатах и привязывает их к комнатам."""
    zombies = []
    for i, room in enumerate(world.rooms):
        points = room.get_random_spawns(count_per_room, world.TILE_SIZE)
        for sx, sy in points:
            # В стартовой комнате не спавним слишком близко к игроку
            if i == 0 and math.hypot(sx - spawn_x, sy - spawn_y) < safe_radius:
                continue
            z = Zombie(screen)
            z.world = world
            z.x, z.y = sx, sy
            z._update_rect()
            zombies.append(z)
            room.enemies.append(z)
    return zombies


def world_to_screen(wx: float, wy: float, cam_x: int, cam_y: int) -> tuple:
    return wx - cam_x, wy - cam_y


# ------------------------------------------------------------------ #
#  Создание мира и персонажа                                          #
# ------------------------------------------------------------------ #

world = WorldGeneration()

hero = Nerd(screen)
hero.world = world
spawn_x, spawn_y = world.get_spawn()
hero.x, hero.y = float(spawn_x), float(spawn_y)

gun = Gun(damage=10, fire_rate=5.0)
projectiles: list = []

zombies = spawn_zombies(world, screen, spawn_x, spawn_y)

#  Игровой цикл                                                       #

run = True
while run:
    dt = clock.tick(60) / 1000.0          # секунды с прошлого кадра

    #  События
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Стреляем от центра персонажа к курсору в мировых координатах
            cam_x = int(hero.x) - WIDTH  // 2
            cam_y = int(hero.y) - HEIGHT // 2
            mx, my = pygame.mouse.get_pos()
            target_wx = mx + cam_x
            target_wy = my + cam_y
            new_bullets = gun.shoot(
                hero.x + hero.hb_ox + hero.hb_w // 2,
                hero.y + hero.hb_oy + hero.hb_h // 2,
                target_wx, target_wy,
            )
            projectiles.extend(new_bullets)

    # --- Обновление ---
    gun.update_cooldown(dt)
    hero.handle_input()

    # Зомби AI
    alive_zombies = [z for z in zombies if z.is_alive]
    for zombie in alive_zombies:
        zombie.update(hero, alive_zombies)

    # Пули
    for p in projectiles:
        p.update(world)
        for zombie in alive_zombies:
            if zombie.is_alive and zombie.rect.colliderect(p.rect):
                zombie.take_damage(p.damage)
                p.alive = False
                break

    # Урон от зомби игроку
    for zombie in alive_zombies:
        if zombie.is_touching(hero.rect):
            hero.take_damage(zombie.attack * dt)   # урон в секунду

    # Чистим мёртвые снаряды
    projectiles = [p for p in projectiles if p.alive]

    # Двери — центр и полуразмер хитбокса чтобы точно знать когда игрок полностью внутри
    world.update_doors(
        hero.x + hero.hb_ox + hero.hb_w / 2,
        hero.y + hero.hb_oy + hero.hb_h / 2,
        hero.hb_w / 2,
        hero.hb_h / 2,
    )

    # Камера
    cam_x = int(hero.x) - WIDTH  // 2
    cam_y = int(hero.y) - HEIGHT // 2
    world.cameraX = cam_x
    world.cameraY = cam_y

    # Отрисовка
    world.draw(screen)
    hero.draw(cam_x, cam_y)

    for zombie in alive_zombies:
        zombie.draw(cam_x, cam_y)

    for p in projectiles:
        p.draw(screen, cam_x, cam_y)

    # HUD — здоровье игрока
    pygame.draw.rect(screen, (150, 0, 0), (20, 20, 200, 18))
    hp_w = int(200 * hero.hp / hero.max_hp)
    pygame.draw.rect(screen, (0, 200, 0), (20, 20, hp_w, 18))
    pygame.draw.rect(screen, (255, 255, 255), (20, 20, 200, 18), 2)

    pygame.display.update()

pygame.quit()