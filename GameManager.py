import math
import random

from Character import Nerd
from Enemy import Zombie, Bandit
from worldGeneration import WorldGeneration


class GameManager:


    SAFE_RADIUS = 200.0
    ZOMBIES_PER_ROOM = 3

    BANDIT_MIN_LEVEL = 2
    BANDIT_CHANCE = 0.5

    def __init__(self, screen, difficulty):
        self.screen = screen
        self.difficulty = difficulty

        self.world = None
        self.hero = None
        self.enemies = []
        self.portal = None
        self.level = 1


    def start(self) -> None:
        self.level = 1
        self._load_level(reuse_hero=False)

    def next_level(self) -> None:
        self.level += 1
        self._load_level(reuse_hero=True)

    def _load_level(self, reuse_hero: bool) -> None:
        world = WorldGeneration()
        spawn_x, spawn_y = world.get_spawn()

        if not reuse_hero or self.hero is None:
            if self.difficulty == "easy":
                hero = Nerd(self.screen, hp=150, damage=50)
            else:
                hero = Nerd(self.screen, hp=100, damage=30)
        else:
            hero = self.hero

        hero.world = world
        hero.x = float(spawn_x)
        hero.y = float(spawn_y)

        enemies = self._spawn_enemies(world, spawn_x, spawn_y)

        self.world = world
        self.hero = hero
        self.enemies = enemies
        self.portal = None

    def _spawn_enemies(self, world, spawn_x: float, spawn_y: float) -> list:
        enemies = []
        for i, room in enumerate(world.rooms):
            points = room.get_random_spawns(self.ZOMBIES_PER_ROOM, world.TILE_SIZE)
            for sx, sy in points:
                if (i == 0 and
                        math.hypot(sx - spawn_x, sy - spawn_y) < self.SAFE_RADIUS):
                    continue

                if (self.level >= self.BANDIT_MIN_LEVEL and
                        random.random() < self.BANDIT_CHANCE):
                    e = Bandit(self.screen)
                else:
                    e = Zombie(self.screen)

                e.world = world
                e.x, e.y = sx, sy
                e._update_rect()
                enemies.append(e)
                room.enemies.append(e)
        return enemies