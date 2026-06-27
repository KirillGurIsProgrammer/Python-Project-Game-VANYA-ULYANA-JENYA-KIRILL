import pygame
import math
from abc import ABC, abstractmethod


class Projectile:
    SIZE = 7

    def __init__(self, x, y, dx, dy, damage, color, speed=12.0,
                 max_range=1500.0, kind="bullet"):
        self.x, self.y = x, y
        self.dx, self.dy = dx, dy
        self.damage = damage
        self.speed = speed
        self.max_range = max_range
        self.traveled = 0.0
        self.alive = True
        self.rect = pygame.Rect(int(x), int(y), self.SIZE, self.SIZE)
        self.color = color
        self.kind = kind   # "bullet" | "ice" | "fear"

    def update(self, world=None):
        self.x += self.dx * self.speed
        self.y += self.dy * self.speed
        self.traveled += self.speed
        self.rect.topleft = (int(self.x) - self.SIZE // 2,
                             int(self.y) - self.SIZE // 2)
        if (world and world.is_wall(self.x, self.y)) or \
                self.traveled >= self.max_range:
            self.alive = False

    def draw(self, screen, camera_x, camera_y):
        cx = int(self.x - camera_x)
        cy = int(self.y - camera_y)
        r = self.SIZE // 2

        if self.kind == "ice":
            pygame.draw.circle(screen, (160, 220, 255), (cx, cy), r + 2)
            pygame.draw.circle(screen, (0, 120, 255),   (cx, cy), r)
            pygame.draw.circle(screen, (255, 255, 255), (cx, cy), r, 1)
        elif self.kind == "fear":
            pygame.draw.circle(screen, (120, 0, 180),   (cx, cy), r + 4)
            pygame.draw.circle(screen, (200, 100, 255), (cx, cy), r)
            pygame.draw.circle(screen, (255, 200, 255), (cx, cy), max(1, r-2))
        else:
            pygame.draw.circle(screen, (255, 200, 0),   (cx, cy), r)
            pygame.draw.circle(screen, (255, 255, 180), (cx, cy), max(1, r-1))


#  Базовый класс

class Weapon(ABC):
    def __init__(self, damage, fire_rate):
        self.damage = damage
        self.fire_rate = fire_rate
        self._cooldown = 0.0

    def update_cooldown(self, dt):
        if self._cooldown > 0:
            self._cooldown -= dt

    @property
    def ready(self):
        return self._cooldown <= 0

    def _make_projectile(self, ox, oy, tx, ty):
        dx, dy = tx - ox, ty - oy
        dist = math.hypot(dx, dy)
        if dist == 0:
            return None
        return Projectile(ox, oy, dx/dist, dy/dist,
                          self.damage, color=(255, 200, 0), kind="bullet")

    def shoot(self, ox, oy, tx, ty):
        if not self.ready:
            return []
        p = self._make_projectile(ox, oy, tx, ty)
        if p is None:
            return []
        self._cooldown = 1.0 / self.fire_rate
        return [p]


#  Gun - обойма 8 патронов, перезарядка 2 с, +1 патрон каждые 15 с

class Gun(Weapon):
    MAG_SIZE      = 8      # размер обоймы
    RELOAD_TIME   = 2.0    # секунды перезарядки
    REGEN_INTERVAL = 15.0  # секунды между авто-патронами

    def __init__(self, damage=10, fire_rate=5.0):
        super().__init__(damage, fire_rate)
        self.ammo          = self.MAG_SIZE   # патроны в обойме
        self.reloading     = False
        self._reload_timer = 0.0
        self._regen_timer  = 0.0            # таймер авто-патрона

    # Вызывается вручную (клавиша R) или автоматически при 0 патронов
    def start_reload(self):
        if not self.reloading and self.ammo < self.MAG_SIZE:
            self.reloading     = True
            self._reload_timer = self.RELOAD_TIME

    def update_cooldown(self, dt):
        super().update_cooldown(dt)

        # Перезарядка
        if self.reloading:
            self._reload_timer -= dt
            if self._reload_timer <= 0:
                self.ammo      = self.MAG_SIZE
                self.reloading = False

        # Авто-патрон каждые 15 с (до лимита обоймы, не прерывает перезарядку)
        if not self.reloading:
            self._regen_timer += dt
            if self._regen_timer >= self.REGEN_INTERVAL:
                self._regen_timer = 0.0
                if self.ammo < self.MAG_SIZE:
                    self.ammo += 1

    @property
    def ready(self):
        return self._cooldown <= 0 and self.ammo > 0 and not self.reloading

    def _make_projectile(self, ox, oy, tx, ty):
        dx, dy = tx - ox, ty - oy
        dist = math.hypot(dx, dy)
        if dist == 0:
            return None
        return Projectile(ox, oy, dx/dist, dy/dist,
                          self.damage, color=(255, 200, 0),
                          speed=14.0, kind="bullet")

    def shoot(self, ox, oy, tx, ty):
        if not self.ready:
            # Пустая обойма — сразу начать перезарядку
            if self.ammo == 0 and not self.reloading:
                self.start_reload()
            return []
        p = self._make_projectile(ox, oy, tx, ty)
        if p is None:
            return []
        self._cooldown  = 1.0 / self.fire_rate
        self.ammo      -= 1
        if self.ammo == 0:
            self.start_reload()
        return [p]

    # Прогресс перезарядки 0.0–1.0 для HUD
    @property
    def reload_progress(self):
        if not self.reloading:
            return 1.0
        return 1.0 - self._reload_timer / self.RELOAD_TIME

    # Прогресс авто-патрона 0.0–1.0 для HUD
    @property
    def regen_progress(self):
        return self._regen_timer / self.REGEN_INTERVAL


#  MagicStick — 3 заряда, автоперезарядка, 1 разовая регенерация

class MagicStick(Weapon):
    MAX_CHARGES    = 3
    CHARGE_REGEN   = 4.0    # секунд на 1 заряд
    HEAL_AMOUNT    = 40     # HP за использование регенерации
    heal_used      = False  # одна на всю игру (классовая переменная)

    def __init__(self, damage=5, fire_rate=2.5):
        super().__init__(damage, fire_rate)
        self.charges       = self.MAX_CHARGES
        self._charge_timer = 0.0

    def update_cooldown(self, dt):
        super().update_cooldown(dt)
        # Авто-восстановление заряда
        if self.charges < self.MAX_CHARGES:
            self._charge_timer += dt
            if self._charge_timer >= self.CHARGE_REGEN:
                self._charge_timer -= self.CHARGE_REGEN
                self.charges += 1

    @property
    def ready(self):
        return self._cooldown <= 0 and self.charges > 0

    def _make_projectile(self, ox, oy, tx, ty):
        dx, dy = tx - ox, ty - oy
        dist   = math.hypot(dx, dy)
        if dist == 0:
            return None
        return Projectile(ox, oy, dx/dist, dy/dist,
                          self.damage, color=(0, 120, 255),
                          speed=11.0, kind="ice")

    def shoot(self, ox, oy, tx, ty):
        if not self.ready:
            return []
        p = self._make_projectile(ox, oy, tx, ty)
        if p is None:
            return []
        self._cooldown  = 1.0 / self.fire_rate
        self.charges   -= 1
        return [p]

    # Прогресс восстановления следующего заряда 0.0–1.0
    @property
    def charge_regen_progress(self):
        if self.charges >= self.MAX_CHARGES:
            return 1.0
        return self._charge_timer / self.CHARGE_REGEN

    # Использовать регенерацию (1 раз на всю игру)
    @classmethod
    def use_heal(cls, hero) -> bool:
        if cls.heal_used:
            return False
        cls.heal_used = True
        hero.hp = min(hero.max_hp, hero.hp + cls.HEAL_AMOUNT)
        return True


#  Fear — 3 заряда, автоперезарядка

class Fear(Weapon):
    MAX_CHARGES = 3
    CHARGE_REGEN = 5.0    # секунд на 1 заряд

    def __init__(self, damage=0, fire_rate=2.0):
        super().__init__(damage, fire_rate)
        self.charges = self.MAX_CHARGES
        self._charge_timer = 0.0

    def update_cooldown(self, dt):
        super().update_cooldown(dt)
        if self.charges < self.MAX_CHARGES:
            self._charge_timer += dt
            if self._charge_timer >= self.CHARGE_REGEN:
                self._charge_timer -= self.CHARGE_REGEN
                self.charges += 1

    @property
    def ready(self):
        return self._cooldown <= 0 and self.charges > 0

    def _make_projectile(self, ox, oy, tx, ty):
        dx, dy = tx - ox, ty - oy
        dist = math.hypot(dx, dy)
        if dist == 0:
            return None
        return Projectile(ox, oy, dx/dist, dy/dist,
                          self.damage, color=(180, 0, 255),
                          speed=10.0, max_range=800.0, kind="fear")

    def shoot(self, ox, oy, tx, ty):
        if not self.ready:
            return []
        p = self._make_projectile(ox, oy, tx, ty)
        if p is None:
            return []
        self._cooldown = 1.0 / self.fire_rate
        self.charges -= 1
        return [p]

    @property
    def charge_regen_progress(self):
        if self.charges >= self.MAX_CHARGES:
            return 1.0
        return self._charge_timer / self.CHARGE_REGEN



class HealOrb(Weapon):
    HEAL_AMOUNT = 40
    heal_used   = False   # классовая переменная — 1 раз на игру

    def __init__(self):
        super().__init__(damage=0, fire_rate=1.0)

    def update_cooldown(self, dt):
        pass   # кулдаун не нужен, заряд одноразовый

    @property
    def ready(self):
        return not HealOrb.heal_used

    def shoot(self, ox, oy, tx, ty):
        """Не стреляет снарядом — лечит сразу при вызове."""
        return []   # лечение происходит в main через use_heal

    def use_heal(self, hero) -> bool:
        if HealOrb.heal_used:
            return False
        HealOrb.heal_used = True
        hero.hp = min(hero.max_hp, hero.hp + self.HEAL_AMOUNT)
        return True