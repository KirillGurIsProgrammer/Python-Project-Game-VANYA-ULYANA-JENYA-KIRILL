import pygame
import math

from Character import Nerd
from Enemy import Zombie
from Gun import Gun, MagicStick
from Portal import Portal
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

font = pygame.font.SysFont(None, 36)
font_small = pygame.font.SysFont(None, 26)

#  Вспомогательные функции                                            #

def spawn_zombies(world, screen, spawn_x, spawn_y,
                  count_per_room=3, safe_radius=200.0):
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


def load_level(level_num, hero=None):
    world = WorldGeneration()
    spawn_x, spawn_y = world.get_spawn()
    if hero is None:
        hero = Nerd(screen)
    hero.world = world
    hero.x, hero.y = float(spawn_x), float(spawn_y)
    zombies = spawn_zombies(world, screen, spawn_x, spawn_y)
    return world, hero, zombies, None   # portal = None


def draw_weapon_hud(screen, weapons, current_idx, font_small):
    """Рисует панель выбора оружия внизу экрана."""
    slot_w, slot_h = 120, 40
    gap = 10
    total_w = len(weapons) * (slot_w + gap) - gap
    start_x = (WIDTH - total_w) // 2
    y = HEIGHT - slot_h - 15

    for i, (name, _) in enumerate(weapons):
        x = start_x + i * (slot_w + gap)
        color = (80, 80, 200) if i == current_idx else (50, 50, 50)
        border = (200, 200, 255) if i == current_idx else (120, 120, 120)
        pygame.draw.rect(screen, color,  (x, y, slot_w, slot_h), border_radius=6)
        pygame.draw.rect(screen, border, (x, y, slot_w, slot_h), 2, border_radius=6)
        label = font_small.render(f"[{i+1}] {name}", True, (255, 255, 255))
        screen.blit(label, (x + slot_w//2 - label.get_width()//2,
                             y + slot_h//2 - label.get_height()//2))

#  Оружия: список (имя, объект)                                       #

weapons = [
    ("Пули",    Gun()),
    ("Заморозка",  MagicStick()),
]
weapon_idx = 0   # текущее оружие

#  Старт игры                                                          #

level = 1
world, hero, zombies, portal = load_level(level)
projectiles = []

ZOMBIE_ATTACK_INTERVAL = 0.8   # секунд между ударами
zombie_hit_timers = {}          # zombie -> время до следующего удара

#  Игровой цикл                                                       #

run = True
while run:
    dt = clock.tick(60) / 1000.0

    # Портал появляется когда все комнаты очищены
    if portal is None and world.all_rooms_cleared():
        px, py = world.get_portal_position()
        portal = Portal(px, py)

    # События
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

        if event.type == pygame.KEYDOWN:
            # Стрелки влево/вправо — переключение оружия
            if event.key == pygame.K_RIGHT:
                weapon_idx = (weapon_idx + 1) % len(weapons)
            if event.key == pygame.K_LEFT:
                weapon_idx = (weapon_idx - 1) % len(weapons)

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            cam_x = int(hero.x) - WIDTH  // 2
            cam_y = int(hero.y) - HEIGHT // 2
            mx, my = pygame.mouse.get_pos()
            gun = weapons[weapon_idx][1]
            new_bullets = gun.shoot(
                hero.x + hero.hb_ox + hero.hb_w // 2,
                hero.y + hero.hb_oy + hero.hb_h // 2,
                mx + cam_x, my + cam_y,
            )
            projectiles.extend(new_bullets)

    # --- Обновление ---
    # Кулдаун обоих оружий
    for _, gun in weapons:
        gun.update_cooldown(dt)

    hero.handle_input()

    alive_zombies = [z for z in zombies if z.is_alive]
    for zombie in alive_zombies:
        zombie.update(hero, alive_zombies)
        zombie.update_frozen()

    # Пули → попадание в зомби
    for p in projectiles:
        p.update(world)
        for zombie in alive_zombies:
            if zombie.is_alive and zombie.rect.colliderect(p.rect):
                # Заморозка только от MagicStick (синие пули)
                if p.color == (0, 0, 255):
                    zombie.hit_by_ice()
                else:
                    zombie.take_damage(p.damage)
                p.alive = False
                break

    projectiles = [p for p in projectiles if p.alive]

    # Урон от зомби по таймеру — раз в ZOMBIE_ATTACK_INTERVAL секунд
    for zombie in alive_zombies:
        if not zombie.is_touching(hero.rect):
            # Не касается — сбрасываем таймер чтобы следующий удар был мгновенным
            zombie_hit_timers[id(zombie)] = 0.0
            continue
        # Касается — считаем время
        timer = zombie_hit_timers.get(id(zombie), 0.0)
        timer -= dt
        if timer <= 0:
            hero.take_damage(zombie.attack)   # фиксированный удар
            timer = ZOMBIE_ATTACK_INTERVAL
        zombie_hit_timers[id(zombie)] = timer

    # Чистим таймеры мёртвых зомби
    alive_ids = {id(z) for z in alive_zombies}
    zombie_hit_timers = {k: v for k, v in zombie_hit_timers.items() if k in alive_ids}

    # Портал
    if portal is not None:
        entered = portal.update(hero.rect)
        if entered:
            level += 1
            world, hero, zombies, portal = load_level(level, hero)
            projectiles = []
            zombie_hit_timers = {}

    world.update_doors(
        hero.x + hero.hb_ox + hero.hb_w / 2,
        hero.y + hero.hb_oy + hero.hb_h / 2,
        hero.hb_w / 2,
        hero.hb_h / 2,
    )

    # --- Камера ---
    cam_x = int(hero.x) - WIDTH  // 2
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

    # HUD — здоровье
    pygame.draw.rect(screen, (150, 0, 0),    (20, 20, 200, 18))
    hp_w = int(200 * hero.hp / hero.max_hp)
    pygame.draw.rect(screen, (0, 200, 0),    (20, 20, hp_w, 18))
    pygame.draw.rect(screen, (255, 255, 255),(20, 20, 200, 18), 2)
    hp_text = font_small.render(f"HP: {int(hero.hp)}", True, (255, 255, 255))
    screen.blit(hp_text, (26, 22))

    # HUD — уровень
    level_text = font.render(f"Level {level}", True, (255, 255, 255))
    screen.blit(level_text, (WIDTH - level_text.get_width() - 20, 20))

    # HUD — панель оружий
    draw_weapon_hud(screen, weapons, weapon_idx, font_small)

    pygame.display.update()

pygame.quit()