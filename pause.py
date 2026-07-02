import pygame
from Screens import Button

class PauseWindow:
    def __init__(self, screen, width, height):
        self.screen = screen
        self.width = width
        self.height = height
        
        self.font_title = pygame.font.SysFont(None, 72)
        self.font = pygame.font.SysFont(None, 48)
        self.font_small = pygame.font.SysFont(None, 32)
        
        # Создаём кнопки
        self.button_continue = Button(
            width // 2 - 120, height // 2 - 20, 240, 60,
            "Continue", self.font,
            (50, 100, 150), (80, 140, 200), (255, 255, 255)
        )
        
        self.button_menu = Button(
            width // 2 - 120, height // 2 + 60, 240, 60,
            "Main Menu", self.font,
            (150, 50, 50), (200, 80, 80), (255, 255, 255)
        )
        
        # Полупрозрачный фон
        self.overlay = pygame.Surface((width, height))
        self.overlay.set_alpha(180)
        self.overlay.fill((0, 0, 0))
    
    def reset(self):
        # Сброс состояния при открытии паузы
        pass
    
    def handle_events(self, events):
        for event in events:
            if self.button_continue.handle_event(event):
                return "continue"
            if self.button_menu.handle_event(event):
                return "menu"
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return "continue"
        return None
    
    def draw(self):
        self.screen.blit(self.overlay, (0, 0))
        
        # Заголовок
        title = self.font_title.render("PAUSE", True, (255, 255, 255))
        title_rect = title.get_rect(center=(self.width // 2, 150))
        self.screen.blit(title, title_rect)
        
        # Подзаголовок
        sub = self.font.render("Game is paused", True, (200, 200, 200))
        sub_rect = sub.get_rect(center=(self.width // 2, 220))
        self.screen.blit(sub, sub_rect)
        
        # Кнопки
        self.button_continue.draw(self.screen)
        self.button_menu.draw(self.screen)
        
        # Подсказка
        hint = self.font_small.render(
            "Press ESC to resume", True, (150, 150, 150)
        )
        hint_rect = hint.get_rect(center=(self.width // 2, self.height - 50))
        self.screen.blit(hint, hint_rect)
    
    def run(self):
        clock = pygame.time.Clock()
        result = None
        
        while result is None:
            events = pygame.event.get()
            
            # Обработка закрытия окна
            for event in events:
                if event.type == pygame.QUIT:
                    return "quit"
            
            result = self.handle_events(events)
            self.draw()
            pygame.display.flip()
            clock.tick(60)
        
        return result