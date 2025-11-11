# menu.py
import pygame
from settings import *

class Menu:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.Font(None, 74)
        self.small_font = pygame.font.Font(None, 50)

        
        self.play_button = pygame.Rect(WIDTH // 2 - 100, 200, 200, 60)
        self.settings_button = pygame.Rect(WIDTH // 2 - 100, 300, 200, 60)
        self.exit_button = pygame.Rect(WIDTH // 2 - 100, 400, 200, 60)

    def draw(self):
        self.screen.fill(BLACK)
        title_text = self.font.render("SPACE SHOOTER", True, WHITE)
        self.screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, 100))

       
        pygame.draw.rect(self.screen, BLUE, self.play_button)
        play_text = self.small_font.render("PLAY", True, WHITE)
        self.screen.blit(play_text, (
            WIDTH // 2 - play_text.get_width() // 2,
            self.play_button.y + 10
        ))

        
        pygame.draw.rect(self.screen, GRAY, self.settings_button)
        settings_text = self.small_font.render("SETTINGS", True, WHITE)
        self.screen.blit(settings_text, (
            WIDTH // 2 - settings_text.get_width() // 2,
            self.settings_button.y + 10
        ))

        
        pygame.draw.rect(self.screen, GRAY, self.exit_button)
        exit_text = self.small_font.render("EXIT", True, WHITE)
        self.screen.blit(exit_text, (
            WIDTH // 2 - exit_text.get_width() // 2,
            self.exit_button.y + 10
        ))

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.play_button.collidepoint(event.pos):
                return "play"
            elif self.settings_button.collidepoint(event.pos):
                return "settings"
            elif self.exit_button.collidepoint(event.pos):
                return "exit"
        return "menu"
