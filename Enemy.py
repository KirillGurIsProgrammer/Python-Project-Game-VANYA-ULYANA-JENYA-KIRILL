import pygame
import math
from Entity import Entity


class Zombie(Entity):

    image_path = "images/zombie.png"
    frozen_zombie_path = "images/frozen_zombie.png"
    fear_zombie = "images/fearZombie.png"

    vision_radius = 400
    lose_radius   = 1000

    def __init__(self, screen: pygame.Surface):
        super().__init__(screen, hp=50, speed=1.5)
        self.attack = 5
        self.aggressive = False
        self.is_frozen = False
        self.is_afraid = False
        self.freeze_timer = 0
        self.fear_timer = 0
        self._base_speed = 1.5

        self.image = pygame.image.load(self.image_path)
        self._setup_hitbox_from_image(margin_x=12, margin_y=4)

    #  Эффекты

    def hit_by_ice(self):
        self.is_frozen = True
        self.freeze_timer = 120
        self.speed = 0.2
        self.image = pygame.image.load(self.frozen_zombie_path)

    def update_frozen(self):
        if self.is_frozen:
            self.freeze_timer -= 1
            if self.freeze_timer <= 0:
                self.is_frozen = False
                self.speed     = self._base_speed
                self.image     = pygame.image.load(self.image_path)

    def afraid(self):
        self.is_afraid  = True
        self.fear_timer = 150
        self.image      = pygame.image.load(self.fear_zombie)

    def update_fear(self):
        if self.is_afraid:
            self.fear_timer -= 1
            if self.fear_timer <= 0:
                self.is_afraid = False
                self.image     = pygame.image.load(self.image_path)

    #  Основное обновление

    def update(self, player: "Entity", all_zombies: list):
        if not self.is_alive:
            return

        dist = self.distance_to(player)

        if dist <= self.vision_radius:
            self.aggressive = True

        if self.world is not None:
            zombie_room = self.world.get_room(self.x, self.y)
            player_room = self.world.get_room(player.x, player.y)
            if zombie_room is not None and zombie_room is not player_room:
                self.aggressive = False

        if self.aggressive:
            # is_afraid передаём в move_toward — там -1 инвертирует направление
            self.move_toward(player.x, player.y, self.is_afraid)
            self._push_away_from(player.rect)

        self._separate_from_others(all_zombies)

    #  Физика разделения

    def _push_away_from(self, player_rect: pygame.Rect):
        if not self.rect.colliderect(player_rect):
            return
        dx = self.rect.centerx - player_rect.centerx
        dy = self.rect.centery - player_rect.centery
        dist = math.hypot(dx, dy) or 1.0
        self.try_move(dx / dist * self.speed, dy / dist * self.speed)

    def _separate_from_others(self, others: list):
        for other in others:
            if other is self or not other.is_alive:
                continue
            if not self.rect.colliderect(other.rect):
                continue
            dx = self.rect.centerx - other.rect.centerx
            dy = self.rect.centery - other.rect.centery
            dist = math.hypot(dx, dy) or 1.0
            self.try_move(dx / dist * self.speed, dy / dist * self.speed)

    def is_touching(self, player_rect: pygame.Rect) -> bool:
        return self.rect.inflate(8, 8).colliderect(player_rect)

    #  Отрисовка

    def draw(self, camera_x: int, camera_y: int):
        if not self.is_alive:
            return
        super().draw(camera_x, camera_y)
        self.draw_hitbox(camera_x, camera_y)
        self.draw_health_bar(camera_x, camera_y)