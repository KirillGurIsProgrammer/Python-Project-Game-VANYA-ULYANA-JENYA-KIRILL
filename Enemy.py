import pygame
import math
from Entity import Entity


class Zombie(Entity):

    image_path = "images/zombie.png"
    frozen_zombie_path = "images/frozen_zombie.png"

    vision_radius = 400   # пикселей — дистанция обнаружения
    lose_radius = 1000   # пикселей — дистанция потери цели

    def __init__(self, screen: pygame.Surface):
        super().__init__(screen, hp=50, speed=1.5)
        self.attack = 5
        self.aggressive = False   # True = зомби видит игрока и преследует
        self.is_frozen = False
        self.freeze_timer = 0


        self.image = pygame.image.load(self.image_path)
        # Хитбокс уже спрайта чтобы зомби не застревали в проходах
        self._setup_hitbox_from_image(margin_x=12, margin_y=4)

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
                self.speed = 1.5
                self.image = pygame.image.load(self.image_path)

    def update(self, player: "Entity", all_zombies: list):
        """Вся логика зомби за один кадр."""
        if not self.is_alive:
            return

        dist = self.distance_to(player)

        # Агрится только если игрок вошёл в радиус видимости
        if dist <= self.vision_radius:
            self.aggressive = True

        # Сразу теряет агр если игрок вышел из комнаты зомби
        if self.world is not None:
            zombie_room = self.world.get_room(self.x, self.y)
            player_room = self.world.get_room(player.x, player.y)
            if zombie_room is not None and zombie_room is not player_room:
                self.aggressive = False

        # Преследование только если агрессивен
        if self.aggressive:
            self.move_toward(player.x, player.y)
            self._push_away_from(player.rect)

        self._separate_from_others(all_zombies)

    def _push_away_from(self, player_rect: pygame.Rect):
        """Отталкивается от игрока при наложении хитбоксов."""
        if not self.rect.colliderect(player_rect):
            return
        dx = self.rect.centerx - player_rect.centerx
        dy = self.rect.centery - player_rect.centery
        dist = math.hypot(dx, dy) or 1.0
        self.try_move(dx / dist * self.speed, dy / dist * self.speed)

    def _separate_from_others(self, others: list):
        """Не накладывается на других зомби."""
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
        # inflate(8,8) надувает прямоугольник на 4px с каждой стороны —
        # pygame.colliderect не засчитывает касание краями без перекрытия
        return self.rect.inflate(8, 8).colliderect(player_rect)

    #  жесткий рендер                                                           #

    def draw(self, camera_x: int, camera_y: int):
        if not self.is_alive:
            return
        super().draw(camera_x, camera_y)
        self.draw_hitbox(camera_x, camera_y)
        self.draw_health_bar(camera_x, camera_y)