import pygame
import random
import math

TILE_EMPTY = 0
TILE_FLOOR = 1
TILE_WALL = 2


class Room:
    def __init__(self, rect: pygame.Rect):
        self.rect = rect
        self.enemies: list = []
        self.visited = False

    @property
    def cleared(self) -> bool:
        return all(not e.is_alive for e in self.enemies) if self.enemies else True



    def contains_point(self, world_x: float, world_y: float, tile_size: int) -> bool:
        tx = int(world_x) // tile_size
        ty = int(world_y) // tile_size
        return self.rect.collidepoint(tx, ty)

    def get_random_spawns(self, count: int, tile_size: int,
                          min_dist: float = 100.0, margin: int = 2) -> list:
        points = []
        attempts = 0
        while len(points) < count and attempts < 1000:
            attempts += 1
            tx = random.randint(self.rect.left + margin, self.rect.right - margin - 1)
            ty = random.randint(self.rect.top + margin, self.rect.bottom - margin - 1)
            x, y = float(tx * tile_size), float(ty * tile_size)
            if all(math.hypot(x - px, y - py) >= min_dist for px, py in points):
                points.append((x, y))
        return points


class WorldGeneration:
    TILE_SIZE = 50

    def __init__(self, camera_x: int = 0, camera_y: int = 0):
        self.cameraX = camera_x
        self.cameraY = camera_y
        self.map_w = 80
        self.map_h = 80
        self.tile_map: list[list[int]] = []
        self.rooms: list[Room] = []
        self.spawn = (0, 0)

        self._corridor_tiles: dict[tuple, list] = {}

        self.floor = pygame.transform.scale(
            pygame.image.load("images/ah604tyj1y951.jpg"),
            (self.TILE_SIZE, self.TILE_SIZE)
        )
        self.grass = pygame.transform.scale(
            pygame.image.load("images/png-klev-club-adfx-p-pikselnaya-trava-png-4.png"),
            (self.TILE_SIZE, self.TILE_SIZE)
        )

        self._generate()


    def _generate(self):
        self.tile_map = [[TILE_EMPTY] * self.map_w for _ in range(self.map_h)]
        self.rooms = []
        self._corridor_tiles = {}

        gap = 5
        ox, oy = 20, 20
        sizes = [(random.randint(15, 20), random.randint(15, 20)) for _ in range(4)]

        col1_x = ox
        col2_x = ox + max(sizes[0][0], sizes[2][0]) + gap
        row1_y = oy
        row2_y = oy + max(sizes[0][1], sizes[1][1]) + gap

        positions = [
            (col1_x, row1_y, sizes[0][0], sizes[0][1]),
            (col2_x, row1_y, sizes[1][0], sizes[1][1]),
            (col1_x, row2_y, sizes[2][0], sizes[2][1]),
            (col2_x, row2_y, sizes[3][0], sizes[3][1]),
        ]

        for rx, ry, rw, rh in positions:
            room = Room(pygame.Rect(rx, ry, rw, rh))
            self.rooms.append(room)
            for y in range(ry, ry + rh):
                for x in range(rx, rx + rw):
                    if 0 <= y < self.map_h and 0 <= x < self.map_w:
                        self.tile_map[y][x] = TILE_FLOOR

        r0, r1, r2, r3 = self.rooms
        pairs = [(0, 1, r0, r1), (2, 3, r2, r3), (0, 2, r0, r2), (1, 3, r1, r3)]
        for ia, ib, ra, rb in pairs:
            self._carve_corridor(ia, ib,
                                 ra.rect.centerx, ra.rect.centery,
                                 rb.rect.centerx, rb.rect.centery)

        self._build_walls()
        self._trim_corridor_tiles()

        self.spawn = (
            r0.rect.centerx * self.TILE_SIZE,
            r0.rect.centery * self.TILE_SIZE,
        )

    def _carve_corridor(self, ia: int, ib: int, x1: int, y1: int, x2: int, y2: int):
        walked = []
        x, y = x1, y1
        while x != x2:
            step = 1 if x2 > x else -1
            for dy in range(2):
                ny = y + dy
                if 0 <= ny < self.map_h and 0 <= x < self.map_w:
                    self.tile_map[ny][x] = TILE_FLOOR
                    walked.append((x, ny))
            x += step
        while y != y2:
            step = 1 if y2 > y else -1
            for dx in range(2):
                nx = x + dx
                if 0 <= y < self.map_h and 0 <= nx < self.map_w:
                    self.tile_map[y][nx] = TILE_FLOOR
                    walked.append((nx, y))
            y += step
        self._corridor_tiles[(min(ia, ib), max(ia, ib))] = walked

    def _build_walls(self):
        dirs = [(-1,0),(1,0),(0,-1),(0,1),(-1,-1),(1,-1),(-1,1),(1,1)]
        for y in range(self.map_h):
            for x in range(self.map_w):
                if self.tile_map[y][x] == TILE_EMPTY:
                    if any(
                        0 <= y+dy < self.map_h and 0 <= x+dx < self.map_w
                        and self.tile_map[y+dy][x+dx] == TILE_FLOOR
                        for dy, dx in dirs
                    ):
                        self.tile_map[y][x] = TILE_WALL

    def _trim_corridor_tiles(self):
        room_rects = [r.rect for r in self.rooms]
        for key, tiles in self._corridor_tiles.items():
            self._corridor_tiles[key] = [
                (tx, ty) for tx, ty in tiles
                if not any(r.collidepoint(tx, ty) for r in room_rects)
            ]


    def update_doors(self, player_cx: float, player_cy: float,
                     player_hw: float = 16, player_hh: float = 20):

        corners = [
            (player_cx - player_hw, player_cy - player_hh),
            (player_cx + player_hw, player_cy - player_hh),
            (player_cx - player_hw, player_cy + player_hh),
            (player_cx + player_hw, player_cy + player_hh),
        ]

        for room in self.rooms:
            if not room.visited:
                if all(room.contains_point(cx, cy, self.TILE_SIZE) for cx, cy in corners):
                    room.visited = True

        for (ia, ib), tiles in self._corridor_tiles.items():
            ra, rb = self.rooms[ia], self.rooms[ib]

            locked = (ra.visited and not ra.cleared) or (rb.visited and not rb.cleared)

            tile_type = TILE_WALL if locked else TILE_FLOOR
            for tx, ty in tiles:
                self.tile_map[ty][tx] = tile_type

    def get_room(self, world_x: float, world_y: float) -> "Room | None":
        for room in self.rooms:
            if room.contains_point(world_x, world_y, self.TILE_SIZE):
                return room
        return None


    def is_wall(self, world_x: float, world_y: float) -> bool:
        tx = int(world_x) // self.TILE_SIZE
        ty = int(world_y) // self.TILE_SIZE
        if 0 <= ty < self.map_h and 0 <= tx < self.map_w:
            return self.tile_map[ty][tx] == TILE_WALL
        return True

    def get_spawn(self) -> tuple:
        return self.spawn


    def draw(self, screen: pygame.Surface):
        ts = self.TILE_SIZE
        sw, sh = screen.get_width(), screen.get_height()

        start_x = max(0, self.cameraX // ts - 1)
        start_y = max(0, self.cameraY // ts - 1)
        end_x = min(self.map_w, start_x + sw // ts + 3)
        end_y = min(self.map_h, start_y + sh // ts + 3)

        for ty in range(start_y, end_y):
            for tx in range(start_x, end_x):
                tile = self.tile_map[ty][tx]
                px = tx * ts - self.cameraX
                py = ty * ts - self.cameraY
                if tile == TILE_FLOOR:
                    screen.blit(self.floor, (px, py))
                elif tile == TILE_WALL:
                    pygame.draw.rect(screen, (60, 55, 70), (px, py, ts, ts))
                    pygame.draw.rect(screen, (40, 38, 50), (px, py, ts, ts), 2)
                else:
                    screen.blit(self.grass, (px, py))

        lx = start_x * ts - self.cameraX
        ty0 = start_y * ts - self.cameraY
        rx = end_x * ts - self.cameraX
        by = end_y * ts - self.cameraY
        if lx > 0: screen.fill((0,0,0), (0,   0,   lx,      sh))
        if ty0 > 0: screen.fill((0,0,0), (0,   0,   sw,      ty0))
        if rx < sw: screen.fill((0,0,0), (rx,  0,   sw - rx, sh))
        if by < sh: screen.fill((0,0,0), (0,   by,  sw,      sh - by))
    def all_rooms_cleared(self) -> bool:
        return all(room.cleared for room in self.rooms)
    def get_portal_position(self) -> tuple:
        candidates = self.rooms[1:]
        room = random.choice(candidates)
        cx = room.rect.centerx * self.TILE_SIZE
        cy = room.rect.centery * self.TILE_SIZE
        return float(cx), float(cy)