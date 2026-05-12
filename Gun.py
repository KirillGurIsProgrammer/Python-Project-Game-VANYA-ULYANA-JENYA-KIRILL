import pygame

class Gun:
    def __init__(self, screen, camerax, cameray):
        self.screen = screen

        self.bullet = pygame.Surface((7, 7))
        self.bullet.fill((255, 255, 0))

        self.camerax = camerax
        self.cameray = cameray

        self.bullets = []

    def startBulletMovement(self, playerX, playerY):

        mouse_x, mouse_y = pygame.mouse.get_pos()

        mouse_world_x = mouse_x + self.camerax
        mouse_world_y = mouse_y + self.cameray

        bullet_x = playerX + 50
        bullet_y = playerY + 25

        dx = mouse_world_x - bullet_x
        dy = mouse_world_y - bullet_y

        distance = (dx ** 2 + dy ** 2) ** 0.5

        dx /= distance
        dy /= distance

        bullet_data = {
            "x": bullet_x,
            "y": bullet_y,
            "dx": dx,
            "dy": dy
        }

        self.bullets.append(bullet_data)

    def bulletMove(self):

        for bullet in self.bullets[:]:

            speed = 15

            bullet["x"] += bullet["dx"] * speed
            bullet["y"] += bullet["dy"] * speed

            self.screen.blit(
                self.bullet,
                (
                    bullet["x"] - self.camerax,
                    bullet["y"] - self.cameray
                )
            )

            if (
                bullet["x"] < 0
                or bullet["x"] > 10000
                or bullet["y"] < 0
                or bullet["y"] > 10000
            ):
                self.bullets.remove(bullet)