import pygame


class HUD:
    def __init__(self, screen, width: int, height: int):
        self.screen = screen
        self.width = width
        self.height = height

        self.font       = pygame.font.SysFont(None, 36)
        self.font_small = pygame.font.SysFont(None, 26)



    def draw(self, hero, level: int, score: int,
             game_started: bool, level_start_time: int,
             difficulty: str | None) -> None:
        self._draw_hp_bar(hero)
        self._draw_score(score)
        self._draw_time(game_started, level_start_time)
        self._draw_difficulty(difficulty)
        self._draw_level(level)


    def _draw_hp_bar(self, hero) -> None:
        bar_x, bar_y, bar_w, bar_h = 20, 20, 220, 22

        # фон
        pygame.draw.rect(self.screen, (60, 10, 10),
                         (bar_x, bar_y, bar_w, bar_h), border_radius=6)

        # заливка
        hp_fill = int(bar_w * hero.hp / hero.max_hp)
        if hero.hp > hero.max_hp * 0.5:
            hp_color = (50, 200, 80)
        elif hero.hp > hero.max_hp * 0.25:
            hp_color = (220, 160, 0)
        else:
            hp_color = (220, 40, 40)

        if hp_fill > 0:
            pygame.draw.rect(self.screen, hp_color,
                             (bar_x, bar_y, hp_fill, bar_h), border_radius=6)

        # рамка
        pygame.draw.rect(self.screen, (200, 200, 200),
                         (bar_x, bar_y, bar_w, bar_h), 2, border_radius=6)

        # текст
        hp_text = self.font_small.render(
            f"HP  {int(hero.hp)} / {hero.max_hp}", True, (255, 255, 255))
        self.screen.blit(hp_text, (bar_x + 6, bar_y + 3))

    def _draw_score(self, score: int) -> None:
        text = self.font_small.render(f"Score: {score}", True, (255, 255, 200))
        self.screen.blit(text, (20, 55))

    def _draw_time(self, game_started: bool, level_start_time: int) -> None:
        if game_started and level_start_time > 0:
            elapsed = (pygame.time.get_ticks() - level_start_time) / 1000.0
            label = f"Time: {elapsed:.1f}s"
        else:
            label = "Time: 0.0s"
        text = self.font_small.render(label, True, (255, 255, 200))
        self.screen.blit(text, (20, 85))

    def _draw_difficulty(self, difficulty: str | None) -> None:
        label = difficulty.upper() if difficulty else "N/A"
        text = self.font_small.render(f"Difficulty: {label}", True, (255, 255, 200))
        self.screen.blit(text, (20, 115))

    def _draw_level(self, level: int) -> None:
        text = self.font.render(f"Level {level}", True, (255, 255, 255))
        self.screen.blit(text, (self.width - text.get_width() - 20, 20))