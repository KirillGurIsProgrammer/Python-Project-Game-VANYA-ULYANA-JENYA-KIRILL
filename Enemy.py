import pygame
import math


class Enemy:
    def __init__(self, screen, hp, attack, speed):
        self.image = pygame.image.load("/Users/kirillgurev/PycharmProjects/ProjectFefuBridge/images/tumblr_mjpz8fWmWp1r413h3o1_400.jpg")
        self.screen = screen
        self.hp = hp
        self.attack = attack
        self.x = 450.0
        self.y = 200.0
        self.speed = speed
        self.world = None

        iw = self.image.get_width()
        ih = self.image.get_height()
        self.hb_ox = 10
        self.hb_oy = 5
        self.hb_w  = iw - 20
        self.hb_h  = ih - 10
        self.hitbox = pygame.Rect(int(self.x) + self.hb_ox, int(self.y) + self.hb_oy, self.hb_w, self.hb_h)

    def _can_move(self, nx, ny):
        if self.world is None:
            return True
        m = 2
        x0 = nx + self.hb_ox + m
        y0 = ny + self.hb_oy + m
        x1 = nx + self.hb_ox + self.hb_w - m
        y1 = ny + self.hb_oy + self.hb_h - m
        for cx, cy in [(x0, y0), (x1, y0), (x0, y1), (x1, y1)]:
            if self.world.is_wall(cx, cy):
                return False
        return True

    def position(self, object_x, object_y):
        dx = object_x - self.x
        dy = object_y - self.y
        distance = math.hypot(dx, dy)
        if distance == 0:
            return
        nx = (dx / distance) * self.speed
        ny = (dy / distance) * self.speed

        if self._can_move(self.x + nx, self.y):
            self.x += nx
        if self._can_move(self.x, self.y + ny):
            self.y += ny

        self.hitbox.topleft = (int(self.x) + self.hb_ox, int(self.y) + self.hb_oy)


class Zombie(Enemy):
    def __init__(self, screen):
        super().__init__(screen, 50, 5, 1.5)

    def drawing(self, camera_x, camera_y, xCharacter, yCharacter):
        self.screen.blit(self.image, (self.x - camera_x, self.y - camera_y))
        pygame.draw.rect(self.screen, (255, 0, 0), self.hitbox.move(-camera_x, -camera_y), 2)

    def check_collision(self, player_rect, player):
        if not self.hitbox.colliderect(player_rect):
            return

        dx = self.hitbox.centerx - player_rect.centerx
        dy = self.hitbox.centery - player_rect.centery
        distance = math.hypot(dx, dy)

        if distance == 0:
            dx, dy, distance = 1.0, 0.0, 1.0

        nx = dx / distance
        ny = dy / distance

        push = self.speed

        new_zx = self.x + nx * push
        new_zy = self.y + ny * push
        if self._can_move(new_zx, self.y):
            self.x = new_zx
        if self._can_move(self.x, new_zy):
            self.y = new_zy
        self.hitbox.topleft = (int(self.x) + self.hb_ox, int(self.y) + self.hb_oy)

    def is_hit(self, projectile_rect):
        return self.hitbox.colliderect(projectile_rect)