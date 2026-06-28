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
                                  (150, 50, 50), (200, 80, 80), (255, 255, 255))

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
                                          True, (100, 255, 100))
            hint_rect = hint.get_rect(center=(self.width // 2, self.height // 2 + 100))
            self.screen.blit(hint, hint_rect)
        else:
            hint = self.font_small.render("Choose difficulty to start!", 
                                          True, (255, 200, 100))
            hint_rect = hint.get_rect(center=(self.width // 2, self.height // 2 + 100))
            self.screen.blit(hint, hint_rect)