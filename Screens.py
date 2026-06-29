import pygame

class Button:
    def __init__(self, x, y, width, height, text, font, color, hover_color, text_color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = font
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.is_hovered = False

    def draw(self, screen):
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(screen, color, self.rect, border_radius=10)
        pygame.draw.rect(screen, (255, 255, 255), self.rect, 2, border_radius=10)
        text_surf = self.font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.is_hovered:
                return True
        return False


class StartScreen:
    def __init__(self, screen, width, height):
        self.screen = screen
        self.width = width
        self.height = height
        self.font_title = pygame.font.SysFont(None, 72)
        self.font = pygame.font.SysFont(None, 48)
        self.font_small = pygame.font.SysFont(None, 32)
        
        # Выбранная сложность (по умолчанию None)
        self.selected_difficulty = None
        
        # Кнопка "Start"
        self.button_start = Button(width // 2 - 100, height // 2 + 120, 200, 60,
                                   "Start", self.font,
                                   (50, 150, 50), (80, 200, 80), (255, 255, 255))
        
        # Кнопки выбора сложности
        self.button_easy = Button(width // 2 - 160, height // 2 + 30, 130, 50,
                                  "Easy", self.font_small,
                                  (50, 150, 50), (80, 200, 80), (255, 255, 255))
        
        self.button_hard = Button(width // 2 + 30, height // 2 + 30, 130, 50,
                                  "Hard", self.font_small,
                                  (255, 36, 0), (200, 80, 80), (255, 255, 255))

    def handle_events(self, events):
        for event in events:
            # Обработка кнопки Easy
            if self.button_easy.handle_event(event):
                self.selected_difficulty = "easy"
                # Визуально выделяем выбранную кнопку
                self.button_easy.color = (30, 200, 30)
                self.button_hard.color = (150, 50, 50)
                return "difficulty_selected"
            
            # Обработка кнопки Hard
            if self.button_hard.handle_event(event):
                self.selected_difficulty = "hard"
                self.button_hard.color = (200, 30, 30)
                self.button_easy.color = (50, 150, 50)
                return "difficulty_selected"
            
            # Обработка кнопки Start (только если выбрана сложность)
            if self.button_start.handle_event(event):
                if self.selected_difficulty is not None:
                    return "start"
        return None

    def draw(self):
        self.screen.fill((20, 20, 40))
        
        # Заголовок
        title = self.font_title.render("Running through the fog", True, (255, 255, 200))
        title_rect = title.get_rect(center=(self.width // 2, self.height // 4))
        self.screen.blit(title, title_rect)
        
        sub = self.font.render("DVFU EDITION", True, (200, 200, 150))
        sub_rect = sub.get_rect(center=(self.width // 2, self.height // 4 + 60))
        self.screen.blit(sub, sub_rect)
        
        # Текст "Выберите сложность"
        diff_text = self.font_small.render("Select difficulty:", True, (255, 255, 255))
        diff_rect = diff_text.get_rect(center=(self.width // 2, self.height // 2 - 10))
        self.screen.blit(diff_text, diff_rect)
        
        # Кнопки сложности
        self.button_easy.draw(self.screen)
        self.button_hard.draw(self.screen)
        
        # Кнопка Start
        self.button_start.draw(self.screen)
        
        # Если сложность выбрана, показываем подсказку
        if self.selected_difficulty is not None:
            hint = self.font_small.render(f"Selected: {self.selected_difficulty.upper()}", 
                                          True, (100, 255, 100) if self.selected_difficulty == "easy" else (255, 36, 0))
            hint_rect = hint.get_rect(center=(self.width // 2, self.height // 2 + 100))
            self.screen.blit(hint, hint_rect)
        else:
            hint = self.font_small.render("Choose difficulty to start!", 
                                          True, (255, 200, 100))
            hint_rect = hint.get_rect(center=(self.width // 2, self.height // 2 + 100))
            self.screen.blit(hint, hint_rect)


class EndScreen:

    def __init__(self, screen: pygame.Surface, width: int, height: int):
        self.screen = screen
        self.width = width
        self.height = height
        self.font_title = pygame.font.SysFont(None, 72)
        self.font_stats = pygame.font.SysFont(None, 48)
        self.font_button = pygame.font.SysFont(None, 36)
        
        # Кнопка возврата в меню
        self.button_menu = Button(
            width // 2 - 120, height // 2 + 100, 240, 60,
            "Back to Menu", self.font_button,
            (50, 100, 150), (80, 140, 200), (255, 255, 255)
        )

    def handle_events(self, events):
        for event in events:
            if self.button_menu.handle_event(event):
                return "menu"
        return None

    def draw(self, final_score: int):
        self.screen.fill((30, 15, 50))
        
        # Заголовок
        title = self.font_title.render("THE END", True, (255, 215, 0))  # Золотой цвет
        title_rect = title.get_rect(center=(self.width // 2, self.height // 4))
        self.screen.blit(title, title_rect)
        
        sub_title = self.font_stats.render("You survived!", True, (200, 200, 250))
        sub_title_rect = sub_title.get_rect(center=(self.width // 2, self.height // 4 + 60))
        self.screen.blit(sub_title, sub_title_rect)
        
        # Отображение финальных очков
        score_text = self.font_stats.render(f"Final Score: {final_score}", True, (255, 255, 200))
        score_rect = score_text.get_rect(center=(self.width // 2, self.height // 2))
        self.screen.blit(score_text, score_rect)
        
        # Кнопка меню
        self.button_menu.draw(self.screen)


class GameOverScreen:

    def __init__(self, screen, width, height):
        self.screen = screen
        self.width = width
        self.height = height
        self.font_title = pygame.font.SysFont(None, 72)
        self.font_subtitle = pygame.font.SysFont(None, 36)
        self.font_stats = pygame.font.SysFont(None, 48)
        self.font_button = pygame.font.SysFont(None, 36)
        
        # Кнопка возврата в меню
        self.button_menu = Button(
            width // 2 - 120, height // 2 + 120, 240, 60,
            "Back to Menu", self.font_button,
            (150, 50, 50), (200, 80, 80), (255, 255, 255)
        )

    def handle_events(self, events):
        for event in events:
            if self.button_menu.handle_event(event):
                return "menu"
        return None

    def draw(self, final_score):
        self.screen.fill((40, 10, 10))
        
        # Заголовок
        title = self.font_title.render("YOU DIED", True, (220, 40, 40))
        title_rect = title.get_rect(center=(self.width // 2, self.height // 4))
        self.screen.blit(title, title_rect)

        subtitle = self.font_subtitle.render("Game over. Try again", True, (180, 150, 150))
        subtitle_rect = subtitle.get_rect(center=(self.width // 2, self.height // 4 + 60))
        self.screen.blit(subtitle, subtitle_rect)
        
        # Показ заработанных очков
        score_text = self.font_stats.render(f"Final Score: {final_score}", True, (255, 255, 200))
        score_rect = score_text.get_rect(center=(self.width // 2, self.height // 2 + 20))
        self.screen.blit(score_text, score_rect)
        
        # Кнопка меню
        self.button_menu.draw(self.screen)
