import pygame
import math

from Gun import Gun, MagicStick, HealOrb


# ------------------------------------------------------------------ #
#  Цвета слотов                                                        #
# ------------------------------------------------------------------ #

WEAPON_COLORS = {
    "Пули":      (255, 210,  50),
    "Заморозка": ( 80, 180, 255),
    "Страх":     (180,  80, 255),
    "Лечение":   ( 80, 220, 120),
}


class WeaponHUD:
    """
    Панель оружий внизу экрана: слоты, иконки, заряды/обойма,
    полоски перезарядки/восстановления.
    """

    SLOT_W   = 150
    SLOT_H   = 80
    GAP      = 8
    PADDING  = 12
    RADIUS   = 10

    def __init__(self, screen, width: int, height: int):
        self.screen  = screen
        self.width   = width
        self.height  = height

        self.font_small = pygame.font.SysFont(None, 26)
        self.font_tiny  = pygame.font.SysFont(None, 20)



    def draw(self, weapons: list, current_idx: int) -> None:
        total_w = len(weapons) * (self.SLOT_W + self.GAP) - self.GAP
        start_x = (self.width - total_w) // 2
        y = self.height - self.SLOT_H - 16

        self._draw_background_panel(total_w, start_x, y)

        for i, (name, weapon) in enumerate(weapons):
            x      = start_x + i * (self.SLOT_W + self.GAP)
            active = (i == current_idx)
            color  = WEAPON_COLORS.get(name, (150, 150, 150))
            self._draw_slot(x, y, name, weapon, active, color, i)



    def _draw_background_panel(self, total_w: int, start_x: int, y: int) -> None:
        panel_surf = pygame.Surface(
            (total_w + self.PADDING * 2, self.SLOT_H + self.PADDING * 2),
            pygame.SRCALPHA,
        )
        pygame.draw.rect(
            panel_surf, (10, 10, 20, 190),
            (0, 0, panel_surf.get_width(), panel_surf.get_height()),
            border_radius=14,
        )
        self.screen.blit(panel_surf, (start_x - self.PADDING, y - self.PADDING))

    def _draw_slot(self, x: int, y: int, name: str,
                   weapon, active: bool, color: tuple, index: int) -> None:
        sl = pygame.Surface((self.SLOT_W, self.SLOT_H), pygame.SRCALPHA)
        if active:
            pygame.draw.rect(
                sl, (color[0]//4, color[1]//4, color[2]//4, 230),
                (0, 0, self.SLOT_W, self.SLOT_H), border_radius=self.RADIUS)
            pygame.draw.rect(
                sl, (*color, 255),
                (0, 0, self.SLOT_W, self.SLOT_H), 2, border_radius=self.RADIUS)
        else:
            pygame.draw.rect(
                sl, (40, 40, 55, 180),
                (0, 0, self.SLOT_W, self.SLOT_H), border_radius=self.RADIUS)
            pygame.draw.rect(
                sl, (80, 80, 100, 200),
                (0, 0, self.SLOT_W, self.SLOT_H), 1, border_radius=self.RADIUS)
        self.screen.blit(sl, (x, y))

        # иконка
        icon_color = color if active else tuple(c // 2 for c in color)
        self._draw_icon(name, x + 20, y + self.SLOT_H // 2 - 4, icon_color)

        # название и клавиша
        label_color = color if active else (160, 160, 180)
        label = self.font_small.render(name, True, label_color)
        self.screen.blit(label, (x + 38, y + 6))

        key_color = (220, 220, 100) if active else (90, 90, 110)
        key_lbl   = self.font_tiny.render(f"[{index + 1}]", True, key_color)
        self.screen.blit(key_lbl,
                         (x + 38, y + self.SLOT_H - key_lbl.get_height() - 5))

        # заряды / перезарядка
        self._draw_weapon_state(x, y, weapon, color)

    def _draw_weapon_state(self, x: int, y: int, weapon, color: tuple) -> None:
        bar_x = x + 6
        bar_y = y + self.SLOT_H - 8
        bar_w = self.SLOT_W - 12
        cx = x + self.SLOT_W // 2

        if isinstance(weapon, Gun):
            self._draw_charges(cx, y + self.SLOT_H - 22,
                               Gun.MAG_SIZE, weapon.ammo, color, dot_r=4, gap=3)
            if weapon.reloading:
                pygame.draw.rect(self.screen, (30, 30, 40), (bar_x, bar_y, bar_w, 4))
                pygame.draw.rect(self.screen, (220, 180, 50),
                                 (bar_x, bar_y,
                                  int(bar_w * weapon.reload_progress), 4))
                txt = self.font_tiny.render("Перезарядка...", True, (220, 180, 50))
                self.screen.blit(txt,
                                 (cx - txt.get_width() // 2,
                                  y + self.SLOT_H - 22 - txt.get_height() - 2))
            elif weapon.ammo < Gun.MAG_SIZE:
                pygame.draw.rect(self.screen, (30, 30, 40), (bar_x, bar_y, bar_w, 3))
                pygame.draw.rect(self.screen, (180, 220, 100),
                                 (bar_x, bar_y,
                                  int(bar_w * weapon.regen_progress), 3))

        elif hasattr(weapon, "MAX_CHARGES"):
            self._draw_charges(cx, y + self.SLOT_H - 22,
                               weapon.MAX_CHARGES, weapon.charges, color,
                               dot_r=5, gap=5)
            if weapon.charges < weapon.MAX_CHARGES:
                pygame.draw.rect(self.screen, (30, 30, 40), (bar_x, bar_y, bar_w, 4))
                pygame.draw.rect(self.screen, color,
                                 (bar_x, bar_y,
                                  int(bar_w * weapon.charge_regen_progress), 4))

        elif isinstance(weapon, HealOrb):
            filled = 1 if weapon.ready else 0
            self._draw_charges(cx, y + self.SLOT_H - 22,
                               1, filled, color, dot_r=7, gap=0)
            status = self.font_tiny.render(
                "Готово" if weapon.ready else "Использовано",
                True, color if weapon.ready else (80, 80, 90))
            self.screen.blit(status,
                             (cx - status.get_width() // 2,
                              y + self.SLOT_H - 38))



    def _draw_icon(self, name: str, cx: int, cy: int, color: tuple) -> None:
        draw_fn = {
            "Пули":      self._icon_bullet,
            "Заморозка": self._icon_ice,
            "Страх":     self._icon_fear,
            "Лечение":   self._icon_heal,
        }.get(name)
        if draw_fn:
            draw_fn(cx, cy, color)

    def _icon_bullet(self, cx: int, cy: int, color: tuple) -> None:
        pygame.draw.circle(self.screen, color, (cx, cy), 7)
        pygame.draw.circle(self.screen, (255, 255, 255), (cx, cy), 7, 1)

    def _icon_ice(self, cx: int, cy: int, color: tuple) -> None:
        pygame.draw.circle(self.screen, color, (cx, cy), 8)
        pygame.draw.circle(self.screen, (200, 240, 255), (cx, cy), 8, 1)
        for ang in range(0, 180, 60):
            r = math.radians(ang)
            dx, dy = int(math.cos(r) * 7), int(math.sin(r) * 7)
            pygame.draw.line(self.screen, (255, 255, 255),
                             (cx - dx, cy - dy), (cx + dx, cy + dy), 2)

    def _icon_fear(self, cx: int, cy: int, color: tuple) -> None:
        pygame.draw.circle(self.screen, color, (cx, cy), 9)
        pygame.draw.circle(self.screen, (230, 180, 255), (cx, cy), 9, 1)
        pygame.draw.circle(self.screen, (255, 255, 255), (cx - 3, cy - 1), 2)
        pygame.draw.circle(self.screen, (255, 255, 255), (cx + 3, cy - 1), 2)

    def _icon_heal(self, cx: int, cy: int, color: tuple) -> None:
        pygame.draw.circle(self.screen, color, (cx, cy), 9)
        pygame.draw.circle(self.screen, (180, 255, 200), (cx, cy), 9, 1)
        pygame.draw.line(self.screen, (255, 255, 255), (cx, cy - 6), (cx, cy + 6), 3)
        pygame.draw.line(self.screen, (255, 255, 255), (cx - 6, cy), (cx + 6, cy), 3)

    def _draw_charges(self, x: int, y: int,
                      total: int, filled: int, color: tuple,
                      dot_r: int = 5, gap: int = 4) -> None:
        total_w = total * (dot_r * 2) + (total - 1) * gap
        sx = x - total_w // 2
        for i in range(total):
            cx = sx + i * (dot_r * 2 + gap) + dot_r
            if i < filled:
                pygame.draw.circle(self.screen, color, (cx, y), dot_r)
            else:
                pygame.draw.circle(self.screen, (50, 50, 65), (cx, y), dot_r)
                pygame.draw.circle(self.screen, color, (cx, y), dot_r, 1)