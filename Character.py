import pygame
from animations import Animations


class Character:
    def __init__(self, screen, hp):
        self.hp = hp
        self.screen = screen
        self.x = 500.0
        self.y = 200.0
        self.speed = 4
        self.world = None

        self.animations = Animations()
        self.image = self.animations.get_idle()

        iw = self.image.get_width()
        ih = self.image.get_height()
        self.hb_ox = 10
        self.hb_oy = 5
        self.hb_w  = iw - 20
        self.hb_h  = ih - 10
        self.rect  = pygame.Rect(int(self.x) + self.hb_ox, int(self.y) + self.hb_oy, self.hb_w, self.hb_h)

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

    def movement(self):
        keys = pygame.key.get_pressed()
        moved = False

        if keys[pygame.K_d]:
            if self._can_move(self.x + self.speed, self.y):
                self.x += self.speed
            self.image = self.animations.get_right()
            moved = True
        elif keys[pygame.K_a]:
            if self._can_move(self.x - self.speed, self.y):
                self.x -= self.speed
            self.image = self.animations.get_left()
            moved = True
        elif keys[pygame.K_s]:
            if self._can_move(self.x, self.y + self.speed):
                self.y += self.speed
            self.image = self.animations.get_down()
            moved = True
        elif keys[pygame.K_w]:
            if self._can_move(self.x, self.y - self.speed):
                self.y -= self.speed
            self.image = self.animations.get_up()
            moved = True

        if not moved:
            self.image = self.animations.get_idle()

        self.rect.topleft = (int(self.x) + self.hb_ox, int(self.y) + self.hb_oy)

    def draw(self, camera_x, camera_y):
        self.screen.blit(self.image, (self.x - camera_x, self.y - camera_y))
        pygame.draw.rect(self.screen, (0, 255, 0), self.rect.move(-camera_x, -camera_y), 2)


class Nerd(Character):
    def __init__(self, screen):
        super().__init__(screen, 100)