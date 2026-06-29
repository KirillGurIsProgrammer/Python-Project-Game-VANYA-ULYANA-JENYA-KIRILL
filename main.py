import pygame

from Gun import Gun, MagicStick, Fear, HealOrb
from Portal import Portal
from Screens import StartScreen, EndScreen, GameOverScreen

from HUD import HUD
from WeaponHUD import WeaponHUD
from GameManager import GameManager
from CombatSystem import CombatSystem

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
#  Окна                                                                #
# ------------------------------------------------------------------ #

start_screen = StartScreen(screen, WIDTH, HEIGHT)
end_screen = EndScreen(screen, WIDTH, HEIGHT)
game_over_screen = GameOverScreen(screen, WIDTH, HEIGHT)
game_state   = "menu"
difficulty   = None

# ------------------------------------------------------------------ #
#  Подсистемы                                                          #
# ------------------------------------------------------------------ #

hud        = HUD(screen, WIDTH, HEIGHT)
weapon_hud = WeaponHUD(screen, WIDTH, HEIGHT)
manager    = GameManager(screen)
combat     = CombatSystem()

# ------------------------------------------------------------------ #
#  Оружия                                                              #
# ------------------------------------------------------------------ #

gun      = Gun()
magic    = MagicStick()
fear_wep = Fear()
heal_orb = HealOrb()

weapons = [
    ("Пули",      gun),
    ("Заморозка", magic),
    ("Страх",     fear_wep),
    ("Лечение",   heal_orb),
]
weapon_idx = 0

# ------------------------------------------------------------------ #
#  Статистика                                                          #
# ------------------------------------------------------------------ #

score            = 0
level_start_time = 0
game_started     = False

# ------------------------------------------------------------------ #
#  Первый уровень                                                      #
# ------------------------------------------------------------------ #

manager.start()
projectiles = []

# ------------------------------------------------------------------ #
#  Игровой цикл                                                        #
# ------------------------------------------------------------------ #

run = True
while run:
    dt     = clock.tick(60) / 1000.0
    events = pygame.event.get()

    # ---- Всегда обрабатываем QUIT ----
    for event in events:
        if event.type == pygame.QUIT:
            run = False

    # ---- Стартовый экран ----
    if game_state == "menu":
        action = start_screen.handle_events(events)
        if action == "start":
            difficulty       = start_screen.selected_difficulty
            game_state       = "playing"
            level_start_time = pygame.time.get_ticks()
            game_started     = True
            score            = 0  # Сбрасываем очки перед новой игрой
            # --- Перезапуск ---
            manager.start() 
            projectiles = []
            combat.reset()
            from Gun import HealOrb
            HealOrb.heal_used = False
            # ------------------------------------------
        start_screen.draw()
        pygame.display.update()
        continue

    # ---- Финальный экран ----
    if game_state == "end":
        action = end_screen.handle_events(events)
        if action == "menu":
            game_state = "menu"
        end_screen.draw(score)
        pygame.display.update()
        continue

    # ---- Экран смерти ----
    if game_state == "game_over":
        action = game_over_screen.handle_events(events)
        if action == "menu":
            game_state = "menu"
        game_over_screen.draw(score)
        pygame.display.update()
        continue

    # ------------------------------------------------------------------ #
    #  Ввод (playing)                                                      #
    # ------------------------------------------------------------------ #

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
            if event.key == pygame.K_r:
                gun.start_reload()

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            cam_x = int(manager.hero.x) - WIDTH  // 2
            cam_y = int(manager.hero.y) - HEIGHT // 2
            mx, my = pygame.mouse.get_pos()
            current_weapon = weapons[weapon_idx][1]

            if isinstance(current_weapon, HealOrb):
                current_weapon.use_heal(manager.hero)
            else:
                hero = manager.hero
                new_bullets = current_weapon.shoot(
                    hero.x + hero.hb_ox + hero.hb_w // 2,
                    hero.y + hero.hb_oy + hero.hb_h // 2,
                    mx + cam_x, my + cam_y,
                )
                projectiles.extend(new_bullets)

    # ------------------------------------------------------------------ #
    #  Обновление                                                          #
    # ------------------------------------------------------------------ #

    hero  = manager.hero
    world = manager.world

    if not hero.is_alive:
        game_state = "game_over"
        continue

    for _, w in weapons:
        w.update_cooldown(dt)

    hero.handle_input()

    alive_zombies = [z for z in manager.zombies if z.is_alive]
    for zombie in alive_zombies:
        zombie.update(hero, alive_zombies)
        zombie.update_frozen()
        zombie.update_fear()

    for p in projectiles:
        p.update(world)

    score += combat.update(dt, hero, alive_zombies, projectiles)
    projectiles = [p for p in projectiles if p.alive]

    # Портал: появляется когда все комнаты зачищены
    if manager.portal is None and world.all_rooms_cleared():
        px, py = world.get_portal_position()
        manager.portal = Portal(px, py)

    if manager.portal is not None:
        entered = manager.portal.update(hero.rect)
        if entered:
            manager.next_level()
            if manager.level > 5:
                game_state = "end"
            projectiles      = []
            combat.reset()
            level_start_time = pygame.time.get_ticks()

    world.update_doors(
        hero.x + hero.hb_ox + hero.hb_w / 2,
        hero.y + hero.hb_oy + hero.hb_h / 2,
        hero.hb_w / 2,
        hero.hb_h / 2,
    )

    # ------------------------------------------------------------------ #
    #  Камера                                                              #
    # ------------------------------------------------------------------ #

    cam_x = int(hero.x) - WIDTH  // 2
    cam_y = int(hero.y) - HEIGHT // 2
    world.cameraX = cam_x
    world.cameraY = cam_y

    # ------------------------------------------------------------------ #
    #  Отрисовка                                                           #
    # ------------------------------------------------------------------ #

    world.draw(screen)

    if manager.portal is not None:
        manager.portal.draw(screen, cam_x, cam_y)

    hero.draw(cam_x, cam_y)

    for zombie in alive_zombies:
        zombie.draw(cam_x, cam_y)

    for p in projectiles:
        p.draw(screen, cam_x, cam_y)

    hud.draw(hero, manager.level, score,
             game_started, level_start_time, difficulty)

    weapon_hud.draw(weapons, weapon_idx)

    pygame.display.update()

pygame.quit()
