import pygame
import math
class Enemy:
    def __init__(self, screen, hp, attack, speed):
        self.image = pygame.image.load("/Users/kirillgurev/PycharmProjects/ProjectFefuBridge/images/tumblr_mjpz8fWmWp1r413h3o1_400.jpg")
        self.screen = screen
        self.hp = hp
        self.attack = attack
        self.x = 450
        self.y = 200
        self.speed = speed
        img_w = self.image.get_width()
        img_h = self.image.get_height()
        self.hitbox = pygame.Rect(self.x, self.y, img_w - 20, img_h - 10)
    def position(self, object_x, object_y):
        dx = object_x - self.x
        dy = object_y - self.y
        distance = math.hypot(dx, dy)
        if distance != 0:
            self.x += (dx / distance)*self.speed
            self.y += (dy / distance)*self.speed
        self.hitbox.topleft = (self.x + 10, self.y + 5)

class Zombie(Enemy):
    def __init__(self, screen):
        super().__init__(screen, 50,5,1.5)
    def drawing(self, camera_x, camera_y, xCharacter, yCharacter):
        self.screen.blit(
            self.image,
            (self.x - camera_x, self.y - camera_y)
        )
        pygame.draw.rect(
            self.screen,
            (255, 0, 0),
            self.hitbox.move(-camera_x, -camera_y),
            2
        )

    def check_collision(self, player_rect):
        if self.hitbox.colliderect(player_rect):
            dx = self.hitbox.centerx - player_rect.centerx
            dy = self.hitbox.centery - player_rect.centery
            distance = math.hypot(dx, dy)
            if distance != 0:
                self.x += (dx / distance) * self.speed
                self.y += (dy / distance) * self.speed
                self.hitbox.topleft = (self.x + 10, self.y + 5)

    def is_hit(self, projectile_rect):
        return self.hitbox.colliderect(projectile_rect)












