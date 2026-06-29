import math

from Character import Nerd
from Enemy import Zombie
from worldGeneration import WorldGeneration


class GameManager:


    SAFE_RADIUS = 200.0
    ZOMBIES_PER_ROOM = 3

    def __init__(self, screen):
        self.screen = screen

        self.world = None
        self.hero = None
        self.zombies = []
        self.portal = None
        self.level = 1


    def start(self) -> None:
        """Загружает первый уровень с нуля."""
        self.level = 1
        self._load_level(reuse_hero=False)

    def next_level(self) -> None:
        """Переходит на следующий уровень, сохраняя героя."""
        self.level += 1
        self._load_level(reuse_hero=True)



    def _load_level(self, reuse_hero: bool) -> None:
        world = WorldGeneration()
        spawn_x, spawn_y = world.get_spawn()

        if not reuse_hero or self.hero is None:
            hero = Nerd(self.screen)
        else:
            hero = self.hero

        hero.world = world
        hero.x = float(spawn_x)
        hero.y = float(spawn_y)

        zombies = self._spawn_zombies(world, spawn_x, spawn_y)

        self.world = world
        self.hero = hero
        self.zombies = zombies
        self.portal = None

    def _spawn_zombies(self, world, spawn_x: float, spawn_y: float) -> list:
        zombies = []
        for i, room in enumerate(world.rooms):
            points = room.get_random_spawns(self.ZOMBIES_PER_ROOM, world.TILE_SIZE)
            for sx, sy in points:
                if (i == 0 and
                        math.hypot(sx - spawn_x, sy - spawn_y) < self.SAFE_RADIUS):
                    continue
                z = Zombie(self.screen)
                z.world = world
                z.x, z.y = sx, sy
                z._update_rect()
                zombies.append(z)
                room.enemies.append(z)
        return zombies