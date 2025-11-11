# main.py
import pygame
from settings import *
from menu import Menu
from player import Player

class Game:
    def __init__(self, screen):
        self.screen = screen
        self.player = Player()

    def update(self, keys):
        self.player.update(keys)

    def draw(self):
        self.screen.fill(BLACK)
        self.player.draw(self.screen)

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption(TITLE)
clock = pygame.time.Clock()

state = "menu"
menu = Menu(screen)
game = Game(screen)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if state == "menu":
            new_state = menu.handle_event(event)
            if new_state == "play":
                state = "play"
            elif new_state == "settings":
                state = "settings"
            elif new_state == "exit":
                running = False

        
        if state == "play" and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                game.player.shoot()

    keys = pygame.key.get_pressed()

    if state == "menu":
        menu.draw()
    elif state == "play":
        game.update(keys)
        game.draw()
        if keys[pygame.K_ESCAPE]:
            state = "menu"
    elif state == "settings":
        screen.fill(BLACK)
        font = pygame.font.Font(None, 60)
        text = font.render("SETTINGS - ESC pro návrat", True, WHITE)
        screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - text.get_height() // 2))
        if keys[pygame.K_ESCAPE]:
            state = "menu"

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
