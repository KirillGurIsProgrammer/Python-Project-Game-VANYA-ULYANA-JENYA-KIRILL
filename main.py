import pygame

from Gun import Gun, Freeze, Fear, HealOrb
from Portal import Portal
from Screens import StartScreen, EndScreen, GameOverScreen
from Enemy import Bandit

from HUD import HUD
from WeaponHUD import WeaponHUD
from GameManager import GameManager
from CombatSystem import CombatSystem
from pause import PauseWindow
from sound_manager import SoundManager


pygame.init()
clock = pygame.time.Clock()

WIDTH, HEIGHT = 1024, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Running through the fog — DVFU EDITION")
pygame.display.set_icon(pygame.image.load("images/golden-gate.png"))


start_screen = StartScreen(screen, WIDTH, HEIGHT)
end_screen = EndScreen(screen, WIDTH, HEIGHT)
game_over_screen = GameOverScreen(screen, WIDTH, HEIGHT)
pause_window = PauseWindow(screen, WIDTH, HEIGHT)
game_state = "menu"
difficulty = None


hud = HUD(screen, WIDTH, HEIGHT)
weapon_hud = WeaponHUD(screen, WIDTH, HEIGHT)
manager = GameManager(screen, difficulty)
combat = CombatSystem()
sound_manager = SoundManager()


gun = Gun()
magic = Freeze()
fear_wep = Fear()
heal_orb = HealOrb()

weapons = [
    ("Пули",      gun),
    ("Заморозка", magic),
    ("Страх",     fear_wep),
    ("Лечение",   heal_orb),
]
weapon_idx = 0

MUSIC_PATH = "sounds/background_music.mp3"

score = 0
level_start_time = 0
game_started = False
final_time = 0.0


manager.start()
projectiles = []
enemy_projectiles = []


run = True
while run:
    dt = clock.tick(60) / 1000.0
    events = pygame.event.get()

    for event in events:
        if event.type == pygame.QUIT:
            run = False

    if game_state == "menu":
        action = start_screen.handle_events(events)
        if action == "start":
            difficulty = start_screen.selected_difficulty
            manager.difficulty = difficulty
            game_state = "playing"
            level_start_time = pygame.time.get_ticks()
            game_started = True
            score = 0  # Сбрасываем очки перед новой игрой
            final_time = 0.0
            manager.start()
            projectiles = []
            enemy_projectiles = []
            combat.reset()
            HealOrb.heal_used = False
            sound_manager.play_music(MUSIC_PATH, volume=0.3)
        start_screen.draw()
        pygame.display.update()
        continue

    if game_state == "end":
        action = end_screen.handle_events(events)
        if action == "menu":
            game_state = "menu"
            sound_manager.stop_music()
        end_screen.draw(score, final_time)
        pygame.display.update()
        continue

    if game_state == "game_over":
        action = game_over_screen.handle_events(events)
        if action == "menu":
            game_state = "menu"
            sound_manager.stop_music()
        game_over_screen.draw(score)
        pygame.display.update()
        continue

    escape_pressed = any(
        event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE
        for event in events
    )

    if escape_pressed:
        sound_manager.pause_music()
        pause_result = pause_window.run()

        if pause_result == "quit":
            run = False
            continue
        elif pause_result == "menu":
            game_state = "menu"
            sound_manager.stop_music()
            continue
        else:
            sound_manager.unpause_music()
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
            if event.key == pygame.K_r:
                gun.start_reload()
        if event.type == pygame.MOUSEWHEEL:
            if event.y > 0:
                weapon_idx = (weapon_idx + 1) % len(weapons)
            elif event.y < 0:
                weapon_idx = (weapon_idx - 1) % len(weapons)

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            cam_x = int(manager.hero.x) - WIDTH // 2
            cam_y = int(manager.hero.y) - HEIGHT // 2
            mx, my = pygame.mouse.get_pos()
            current_weapon = weapons[weapon_idx][1]

            if isinstance(current_weapon, HealOrb):
                healed = current_weapon.use_heal(manager.hero)
                if healed:
                    sound_manager.play_heal()
            else:
                hero = manager.hero
                new_bullets = current_weapon.shoot(
                    hero.x + hero.hb_ox + hero.hb_w // 2,
                    hero.y + hero.hb_oy + hero.hb_h // 2,
                    mx + cam_x, my + cam_y,
                )
                if new_bullets:
                    sound_manager.play_attack()
                projectiles.extend(new_bullets)


    hero = manager.hero
    world = manager.world

    if not hero.is_alive:
        sound_manager.play_death()
        sound_manager.stop_music()
        game_state = "game_over"
        continue

    for _, w in weapons:
        w.update_cooldown(dt)

    hero.handle_input()

    alive_enemies = [e for e in manager.enemies if e.is_alive]
    for enemy in alive_enemies:
        enemy.update(hero, alive_enemies)
        enemy.update_frozen()
        enemy.update_fear()

        if isinstance(enemy, Bandit):
            enemy.update_weapon_cooldown(dt)
            enemy_projectiles.extend(enemy.try_shoot(hero))

    for p in projectiles:
        p.update(world)

    for p in enemy_projectiles:
        p.update(world)

    score += combat.update(dt, hero, alive_enemies, projectiles, enemy_projectiles)
    projectiles = [p for p in projectiles if p.alive]
    enemy_projectiles = [p for p in enemy_projectiles if p.alive]

    if manager.portal is None and world.all_rooms_cleared():
        px, py = world.get_portal_position()
        manager.portal = Portal(px, py)

    if manager.portal is not None:
        entered = manager.portal.update(hero.rect)
        if entered:
            sound_manager.play_portal()
            manager.next_level()
            if manager.level == 4:
                game_state = "end"
                sound_manager.stop_music()
                final_time = (pygame.time.get_ticks() - level_start_time) / 1000.0
            else:
                sound_manager.play_level_up()
            projectiles = []
            enemy_projectiles = []
            combat.reset()

    world.update_doors(
        hero.x + hero.hb_ox + hero.hb_w / 2,
        hero.y + hero.hb_oy + hero.hb_h / 2,
        hero.hb_w / 2,
        hero.hb_h / 2,
    )

    cam_x = int(hero.x) - WIDTH // 2
    cam_y = int(hero.y) - HEIGHT // 2
    world.cameraX = cam_x
    world.cameraY = cam_y
    world.draw(screen)

    if manager.portal is not None:
        manager.portal.draw(screen, cam_x, cam_y)

    hero.draw(cam_x, cam_y)

    for enemy in alive_enemies:
        enemy.draw(cam_x, cam_y)

    for p in projectiles:
        p.draw(screen, cam_x, cam_y)

    for p in enemy_projectiles:
        p.draw(screen, cam_x, cam_y)

    hud.draw(hero, manager.level, score,
             game_started, level_start_time, difficulty)

    weapon_hud.draw(weapons, weapon_idx)

    pygame.display.update()

pygame.quit()