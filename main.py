import pygame
import math

from Character import Nerd
from Enemy import Zombie
from Gun import Gun, MagicStick, Fear, HealOrb
from Portal import Portal
from worldGeneration import WorldGeneration
from Screens import StartScreen

#  Инициализация

pygame.init()
clock = pygame.time.Clock()

WIDTH, HEIGHT = 1024, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Running through the fog — DVFU EDITION")
pygame.display.set_icon(pygame.image.load("images/golden-gate.png"))

font       = pygame.font.SysFont(None, 36)
font_small = pygame.font.SysFont(None, 26)
font_tiny  = pygame.font.SysFont(None, 20)

# ---------- СТАРТОВОЕ ОКНО ----------
start_screen = StartScreen(screen, WIDTH, HEIGHT)
game_state = "menu"
difficulty = None  # <-- НОВАЯ ПЕРЕМЕННАЯ для хранения сложности

#  Вспомогательные функции

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
    return world, hero, zombies, None


#  Цвета и иконки

WEAPON_COLORS = {
    "Пули":      (255, 210,  50),
    "Заморозка": ( 80, 180, 255),
    "Страх":     (180,  80, 255),
    "Лечение":   ( 80, 220, 120),
}

def _draw_icon_bullet(surf, cx, cy, color):
    pygame.draw.circle(surf, color, (cx, cy), 7)
    pygame.draw.circle(surf, (255, 255, 255), (cx, cy), 7, 1)

def _draw_icon_ice(surf, cx, cy, color):
    pygame.draw.circle(surf, color, (cx, cy), 8)
    pygame.draw.circle(surf, (200, 240, 255), (cx, cy), 8, 1)
    for ang in range(0, 180, 60):
        r = math.radians(ang)
        dx, dy = int(math.cos(r)*7), int(math.sin(r)*7)
        pygame.draw.line(surf, (255,255,255), (cx-dx, cy-dy), (cx+dx, cy+dy), 2)

def _draw_icon_fear(surf, cx, cy, color):
    pygame.draw.circle(surf, color, (cx, cy), 9)
    pygame.draw.circle(surf, (230, 180, 255), (cx, cy), 9, 1)
    pygame.draw.circle(surf, (255,255,255), (cx-3, cy-1), 2)
    pygame.draw.circle(surf, (255,255,255), (cx+3, cy-1), 2)

def _draw_icon_heal(surf, cx, cy, color):
    """Зелёный крест."""
    pygame.draw.circle(surf, color, (cx, cy), 9)
    pygame.draw.circle(surf, (180, 255, 200), (cx, cy), 9, 1)
    pygame.draw.line(surf, (255,255,255), (cx, cy-6), (cx, cy+6), 3)
    pygame.draw.line(surf, (255,255,255), (cx-6, cy), (cx+6, cy), 3)

ICON_DRAW = {
    "Пули":      _draw_icon_bullet,
    "Заморозка": _draw_icon_ice,
    "Страх":     _draw_icon_fear,
    "Лечение":   _draw_icon_heal,
}

#  Отрисовка зарядов (точки)

def _draw_charges(surf, x, y, total, filled, color, dot_r=5, gap=4):
    """Ряд кружков-зарядов."""
    total_w = total * (dot_r*2) + (total-1)*gap
    sx = x - total_w // 2
    for i in range(total):
        cx = sx + i*(dot_r*2 + gap) + dot_r
        if i < filled:
            pygame.draw.circle(surf, color, (cx, y), dot_r)
        else:
            pygame.draw.circle(surf, (50, 50, 65), (cx, y), dot_r)
            pygame.draw.circle(surf, color, (cx, y), dot_r, 1)


#  HUD оружий

def draw_weapon_hud(surf, weapons, current_idx, font_s, font_t):
    slot_w  = 150
    slot_h  = 80
    gap     = 8
    padding = 12
    radius  = 10

    total_w = len(weapons) * (slot_w + gap) - gap
    start_x = (WIDTH - total_w) // 2
    y       = HEIGHT - slot_h - 16

    # фоновая панель
    panel_surf = pygame.Surface((total_w + padding*2, slot_h + padding*2),
                                pygame.SRCALPHA)
    pygame.draw.rect(panel_surf, (10, 10, 20, 190),
                     (0, 0, panel_surf.get_width(), panel_surf.get_height()),
                     border_radius=14)
    surf.blit(panel_surf, (start_x - padding, y - padding))

    for i, (name, weapon) in enumerate(weapons):
        x      = start_x + i * (slot_w + gap)
        active = (i == current_idx)
        color  = WEAPON_COLORS.get(name, (150, 150, 150))

        # фон слота
        sl = pygame.Surface((slot_w, slot_h), pygame.SRCALPHA)
        if active:
            pygame.draw.rect(sl, (color[0]//4, color[1]//4, color[2]//4, 230),
                             (0, 0, slot_w, slot_h), border_radius=radius)
            pygame.draw.rect(sl, (*color, 255),
                             (0, 0, slot_w, slot_h), 2, border_radius=radius)
        else:
            pygame.draw.rect(sl, (40, 40, 55, 180),
                             (0, 0, slot_w, slot_h), border_radius=radius)
            pygame.draw.rect(sl, (80, 80, 100, 200),
                             (0, 0, slot_w, slot_h), 1, border_radius=radius)
        surf.blit(sl, (x, y))

        icon_fn    = ICON_DRAW.get(name)
        icon_color = color if active else tuple(c//2 for c in color)
        if icon_fn:
            icon_fn(surf, x + 20, y + slot_h//2 - 4, icon_color)

        label_color = color if active else (160, 160, 180)
        label = font_s.render(name, True, label_color)
        surf.blit(label, (x + 38, y + 6))

        key_color = (220, 220, 100) if active else (90, 90, 110)
        key_lbl   = font_t.render(f"[{i+1}]", True, key_color)
        surf.blit(key_lbl, (x + 38, y + slot_h - key_lbl.get_height() - 5))

        bar_x = x + 6
        bar_y = y + slot_h - 8
        bar_w = slot_w - 12

        # ---- Gun: обойма + перезарядка ----
        if isinstance(weapon, Gun):
            # патроны точками
            _draw_charges(surf, x + slot_w//2, y + slot_h - 22,
                          Gun.MAG_SIZE, weapon.ammo, color, dot_r=4, gap=3)

            if weapon.reloading:
                # прогресс-бар перезарядки
                pygame.draw.rect(surf, (30, 30, 40), (bar_x, bar_y, bar_w, 4))
                pygame.draw.rect(surf, (220, 180, 50),
                                 (bar_x, bar_y,
                                  int(bar_w * weapon.reload_progress), 4))
                rl_txt = font_t.render("Перезарядка...", True, (220, 180, 50))
                surf.blit(rl_txt, (x + slot_w//2 - rl_txt.get_width()//2,
                                   y + slot_h - 22 - rl_txt.get_height() - 2))
            else:
                # авто-патрон: маленькая полоска под точками
                if weapon.ammo < Gun.MAG_SIZE:
                    pygame.draw.rect(surf, (30, 30, 40), (bar_x, bar_y, bar_w, 3))
                    pygame.draw.rect(surf, (180, 220, 100),
                                     (bar_x, bar_y,
                                      int(bar_w * weapon.regen_progress), 3))

        # ---- MagicStick / Fear: заряды точками ----
        elif hasattr(weapon, "MAX_CHARGES"):
            _draw_charges(surf, x + slot_w//2, y + slot_h - 22,
                          weapon.MAX_CHARGES, weapon.charges, color, dot_r=5, gap=5)
            # полоска восстановления следующего заряда
            if weapon.charges < weapon.MAX_CHARGES:
                pygame.draw.rect(surf, (30, 30, 40), (bar_x, bar_y, bar_w, 4))
                pygame.draw.rect(surf, color,
                                 (bar_x, bar_y,
                                  int(bar_w * weapon.charge_regen_progress), 4))

        # ---- HealOrb: 1 заряд (использован или нет) ----
        elif isinstance(weapon, HealOrb):
            filled = 1 if weapon.ready else 0
            _draw_charges(surf, x + slot_w//2, y + slot_h - 22,
                          1, filled, color, dot_r=7, gap=0)
            status_txt = font_t.render(
                "Готово" if weapon.ready else "Использовано",
                True, color if weapon.ready else (80, 80, 90))
            surf.blit(status_txt,
                      (x + slot_w//2 - status_txt.get_width()//2,
                       y + slot_h - 38))


#  Оружия

gun = Gun()
magic = MagicStick()
fear_wep = Fear()
heal_orb = HealOrb()

weapons = [
    ("Пули",      gun),
    ("Заморозка", magic),
    ("Страх",     fear_wep),
    ("Лечение",   heal_orb),
]
weapon_idx = 0

#  Старт игры

level = 1
world, hero, zombies, portal = load_level(level)
projectiles = []

ZOMBIE_ATTACK_INTERVAL = 0.8
zombie_hit_timers = {}

#  Игровой цикл

run = True
while run:
    dt = clock.tick(60) / 1000.0
    events = pygame.event.get()

    if portal is None and world.all_rooms_cleared():
        px, py = world.get_portal_position()
        portal = Portal(px, py)

    # ---- События ----
    for event in events:
        if event.type == pygame.QUIT:
            run = False

    # ---- СТАРТОВОЕ ОКНО ----
    if game_state == "menu":
        action = start_screen.handle_events(events)
        if action == "start":
            difficulty = start_screen.selected_difficulty  # <-- СОХРАНЯЕМ СЛОЖНОСТЬ
            print(f"Выбрана сложность: {difficulty}")      # <-- ДЛЯ ПРОВЕРКИ
            game_state = "playing"
        start_screen.draw()
        pygame.display.update()
        continue

    for event in events:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RIGHT:
                weapon_idx = (weapon_idx + 1) % len(weapons)
            if event.key == pygame.K_LEFT:
                weapon_idx = (weapon_idx - 1) % len(weapons)
            if event.key == pygame.K_1: weapon_idx = 0
            if event.key == pygame.K_2: weapon_idx = 1
            if event.key == pygame.K_3: weapon_idx = 2
            if event.key == pygame.K_4: weapon_idx = 3

            # Ручная перезарядка
            if event.key == pygame.K_r:
                gun.start_reload()

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            cam_x = int(hero.x) - WIDTH // 2
            cam_y = int(hero.y) - HEIGHT // 2
            mx, my = pygame.mouse.get_pos()
            current_weapon = weapons[weapon_idx][1]
            # HealOrb лечит мгновенно, без снаряда
            if isinstance(current_weapon, HealOrb):
                current_weapon.use_heal(hero)
            else:
                new_bullets = current_weapon.shoot(
                    hero.x + hero.hb_ox + hero.hb_w // 2,
                    hero.y + hero.hb_oy + hero.hb_h // 2,
                    mx + cam_x, my + cam_y,
                )
                projectiles.extend(new_bullets)

    # Обновление
    for _, w in weapons:
        w.update_cooldown(dt)

    hero.handle_input()

    alive_zombies = [z for z in zombies if z.is_alive]
    for zombie in alive_zombies:
        zombie.update(hero, alive_zombies)
        zombie.update_frozen()
        zombie.update_fear()

    # Пули → попадание в зомби
    for p in projectiles:
        p.update(world)
        for zombie in alive_zombies:
            if zombie.is_alive and zombie.rect.colliderect(p.rect):
                if p.kind == "ice":
                    zombie.hit_by_ice()
                    zombie.take_damage(p.damage)
                    hero.hp = min(hero.max_hp, hero.hp + MagicStick.HEAL_AMOUNT // 3)
                elif p.kind == "fear":
                    zombie.afraid()
                else:
                    zombie.take_damage(p.damage)
                p.alive = False
                break

    projectiles = [p for p in projectiles if p.alive]

    # Урон от зомби
    for zombie in alive_zombies:
        if not zombie.is_touching(hero.rect):
            zombie_hit_timers[id(zombie)] = 0.0
            continue
        timer = zombie_hit_timers.get(id(zombie), 0.0)
        timer -= dt
        if timer <= 0:
            hero.take_damage(zombie.attack)
            timer = ZOMBIE_ATTACK_INTERVAL
        zombie_hit_timers[id(zombie)] = timer

    alive_ids = {id(z) for z in alive_zombies}
    zombie_hit_timers = {k: v for k, v in zombie_hit_timers.items()
                         if k in alive_ids}

    # Портал
    if portal is not None:
        entered = portal.update(hero.rect)
        if entered:
            level += 1
            world, hero, zombies, portal = load_level(level, hero)
            projectiles     = []
            zombie_hit_timers = {}

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

    #  Отрисовка
    world.draw(screen)

    if portal is not None:
        portal.draw(screen, cam_x, cam_y)

    hero.draw(cam_x, cam_y)

    for zombie in alive_zombies:
        zombie.draw(cam_x, cam_y)

    for p in projectiles:
        p.draw(screen, cam_x, cam_y)

    # HUD — HP бар
    bar_x, bar_y, bar_w, bar_h = 20, 20, 220, 22
    pygame.draw.rect(screen, (60, 10, 10), (bar_x, bar_y, bar_w, bar_h),
                     border_radius=6)
    hp_fill  = int(bar_w * hero.hp / hero.max_hp)
    hp_color = (50, 200, 80)  if hero.hp > hero.max_hp * 0.5 else \
               (220, 160, 0) if hero.hp > hero.max_hp * 0.25 else (220, 40, 40)
    if hp_fill > 0:
        pygame.draw.rect(screen, hp_color,
                         (bar_x, bar_y, hp_fill, bar_h), border_radius=6)
    pygame.draw.rect(screen, (200, 200, 200),
                     (bar_x, bar_y, bar_w, bar_h), 2, border_radius=6)
    hp_text = font_small.render(f"HP  {int(hero.hp)} / {hero.max_hp}",
                                True, (255, 255, 255))
    screen.blit(hp_text, (bar_x + 6, bar_y + 3))

    # HUD - уровень
    level_text = font.render(f"Level {level}", True, (255, 255, 255))
    screen.blit(level_text, (WIDTH - level_text.get_width() - 20, 20))

    # HUD - панель оружий
    draw_weapon_hud(screen, weapons, weapon_idx, font_small, font_tiny)

    pygame.display.update()

pygame.quit()