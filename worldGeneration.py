import pygame
import random

TILE_EMPTY = 0
TILE_FLOOR = 1
TILE_WALL  = 2


class WorldGeneration:
    TILE_SIZE = 50

    def __init__(self, cameraX=0, cameraY=0):
        self.cameraX  = cameraX
        self.cameraY  = cameraY
        self.map_w    = 80
        self.map_h    = 80
        self.tile_map = []
        self.rooms    = []
        self.spawn    = (0, 0)

        self.floor = pygame.image.load("/Users/kirillgurev/PycharmProjects/ProjectFefuBridge/images/ah604tyj1y951.jpg")
        self.floor = pygame.transform.scale(self.floor, (self.TILE_SIZE, self.TILE_SIZE))

        self.grass = pygame.image.load("/Users/kirillgurev/PycharmProjects/ProjectFefuBridge/images/png-klev-club-adfx-p-pikselnaya-trava-png-4.png")
        self.grass = pygame.transform.scale(self.grass, (self.TILE_SIZE, self.TILE_SIZE))

        self.generation()

    def generation(self):
        self.tile_map = [[TILE_EMPTY] * self.map_w for _ in range(self.map_h)]
        self.rooms = []

        room_sizes = [(random.randint(11, 14), random.randint(11, 14)) for _ in range(4)]
        gap = 5
        ox = 20
        oy = 20

        rw0, rh0 = room_sizes[0]
        rw1, rh1 = room_sizes[1]
        rw2, rh2 = room_sizes[2]
        rw3, rh3 = room_sizes[3]

        col1_x = ox
        col2_x = ox + max(rw0, rw2) + gap
        row1_y = oy
        row2_y = oy + max(rh0, rh1) + gap

        positions = [
            (col1_x, row1_y, rw0, rh0),
            (col2_x, row1_y, rw1, rh1),
            (col1_x, row2_y, rw2, rh2),
            (col2_x, row2_y, rw3, rh3),
        ]

        for (rx, ry, rw, rh) in positions:
            room = pygame.Rect(rx, ry, rw, rh)
            self.rooms.append(room)
            for y in range(ry, ry + rh):
                for x in range(rx, rx + rw):
                    if 0 <= y < self.map_h and 0 <= x < self.map_w:
                        self.tile_map[y][x] = TILE_FLOOR

        r0, r1, r2, r3 = self.rooms
        self._carve_corridor(r0.centerx, r0.centery, r1.centerx, r1.centery)
        self._carve_corridor(r2.centerx, r2.centery, r3.centerx, r3.centery)
        self._carve_corridor(r0.centerx, r0.centery, r2.centerx, r2.centery)
        self._carve_corridor(r1.centerx, r1.centery, r3.centerx, r3.centery)

        self._build_walls()

        r = self.rooms[0]
        self.spawn = (r.centerx * self.TILE_SIZE, r.centery * self.TILE_SIZE)

    def _carve_corridor(self, x1, y1, x2, y2):
        x, y = x1, y1
        while x != x2:
            step = 1 if x2 > x else -1
            for dy in range(2):
                ny = y + dy
                if 0 <= ny < self.map_h and 0 <= x < self.map_w:
                    self.tile_map[ny][x] = TILE_FLOOR
            x += step
        while y != y2:
            step = 1 if y2 > y else -1
            for dx in range(2):
                nx = x + dx
                if 0 <= y < self.map_h and 0 <= nx < self.map_w:
                    self.tile_map[y][nx] = TILE_FLOOR
            y += step

    def _build_walls(self):
        directions = [(-1,0),(1,0),(0,-1),(0,1),(-1,-1),(1,-1),(-1,1),(1,1)]
        for y in range(self.map_h):
            for x in range(self.map_w):
                if self.tile_map[y][x] == TILE_EMPTY:
                    for dy, dx in directions:
                        ny, nx = y + dy, x + dx
                        if 0 <= ny < self.map_h and 0 <= nx < self.map_w and self.tile_map[ny][nx] == TILE_FLOOR:
                            self.tile_map[y][x] = TILE_WALL
                            break

    def is_wall(self, world_x, world_y):
        ts = self.TILE_SIZE
        tx = int(world_x) // ts
        ty = int(world_y) // ts
        if 0 <= ty < self.map_h and 0 <= tx < self.map_w:
            return self.tile_map[ty][tx] == TILE_WALL
        return True

    def drawing(self, screen):
        ts = self.TILE_SIZE
        sw = screen.get_width()
        sh = screen.get_height()

        start_x = max(0, self.cameraX // ts - 1)
        start_y = max(0, self.cameraY // ts - 1)
        end_x   = min(self.map_w, start_x + sw // ts + 3)
        end_y   = min(self.map_h, start_y + sh // ts + 3)

        for ty in range(start_y, end_y):
            for tx in range(start_x, end_x):
                tile = self.tile_map[ty][tx]
                px   = tx * ts - self.cameraX
                py   = ty * ts - self.cameraY

                if tile == TILE_FLOOR:
                    screen.blit(self.floor, (px, py))
                elif tile == TILE_WALL:
                    pygame.draw.rect(screen, (60, 55, 70), (px, py, ts, ts))
                    pygame.draw.rect(screen, (40, 38, 50), (px, py, ts, ts), 2)
                else:
                    screen.blit(self.grass, (px, py))

        left_gap  = start_x * ts - self.cameraX
        top_gap   = start_y * ts - self.cameraY
        right_gap = end_x * ts - self.cameraX
        bot_gap   = end_y * ts - self.cameraY

        if left_gap > 0:
            screen.fill((0, 0, 0), (0, 0, left_gap, sh))
        if top_gap > 0:
            screen.fill((0, 0, 0), (0, 0, sw, top_gap))
        if right_gap < sw:
            screen.fill((0, 0, 0), (right_gap, 0, sw - right_gap, sh))
        if bot_gap < sh:
            screen.fill((0, 0, 0), (0, bot_gap, sw, sh - bot_gap))

    def get_spawn(self):
        return self.spawn