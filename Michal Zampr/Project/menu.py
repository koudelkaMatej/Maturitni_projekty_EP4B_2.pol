# menu.py
import pygame
import sys

pygame.init()
WIDTH, HEIGHT = 480, 640
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Tetris - Menu")
CLOCK = pygame.time.Clock()
FPS = 60

# Colors
BG = (18, 18, 30)
CARD = (28, 28, 45)
HOVER = (70, 130, 180)
TEXT = (240, 240, 245)
ACCENT = (100, 200, 255)

# Fonts
TITLE_FONT = pygame.font.SysFont("verdana", 48, bold=True)
BTN_FONT = pygame.font.SysFont("verdana", 28)
SMALL_FONT = pygame.font.SysFont("verdana", 18)

class Button:
    def __init__(self, rect, text, callback):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.callback = callback
        self.hovered = False

    def draw(self, surf):
        color = HOVER if self.hovered else CARD
        pygame.draw.rect(surf, color, self.rect, border_radius=10)
        pygame.draw.rect(surf, (50, 50, 70), self.rect, width=2, border_radius=10)
        txt = BTN_FONT.render(self.text, True, TEXT)
        txt_rect = txt.get_rect(center=self.rect.center)
        surf.blit(txt, txt_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.callback()

def center_rect(w, h, y_offset=0):
    return (WIDTH//2 - w//2, HEIGHT//2 - h//2 + y_offset, w, h)

# Placeholder callbacks
def start_game():
    print("Start game pressed — implement Tetris here.")
    flash_screen("Starting...")

def open_settings():
    settings_loop()

def quit_game():
    pygame.quit()
    sys.exit()

def flash_screen(message, time_ms=600):
    end = pygame.time.get_ticks() + time_ms
    while pygame.time.get_ticks() < end:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        SCREEN.fill(BG)
        txt = TITLE_FONT.render(message, True, ACCENT)
        SCREEN.blit(txt, txt.get_rect(center=(WIDTH//2, HEIGHT//2)))
        pygame.display.flip()
        CLOCK.tick(FPS)

# Create buttons
btn_w, btn_h = 260, 60
spacing = 18
play_btn = Button(center_rect(btn_w, btn_h, -btn_h - spacing), "Play", start_game)
settings_btn = Button(center_rect(btn_w, btn_h, 0), "Settings", open_settings)
quit_btn = Button(center_rect(btn_w, btn_h, btn_h + spacing), "Quit", quit_game)
buttons = [play_btn, settings_btn, quit_btn]

def draw_menu():
    SCREEN.fill(BG)
    title_surf = TITLE_FONT.render("TETRIS", True, ACCENT)
    title_rect = title_surf.get_rect(center=(WIDTH//2, HEIGHT//4))
    SCREEN.blit(title_surf, title_rect)

    for b in buttons:
        b.draw(SCREEN)

def menu_loop():
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit_game()
            for b in buttons:
                b.handle_event(event)

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    quit_game()
                elif event.key == pygame.K_RETURN:
                    start_game()
                elif event.key == pygame.K_s:
                    open_settings()

        draw_menu()
        pygame.display.flip()
        CLOCK.tick(FPS)

# Simple settings screen with one toggle demo
def settings_loop():
    sound_on = True
    back_btn = Button((20, HEIGHT - 80, 120, 50), "Back", lambda: None)
    toggle_btn = Button((WIDTH//2 - 100, HEIGHT//2 - 30, 200, 50),
                        "Sound: ON" if sound_on else "Sound: OFF",
                        lambda: None)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit_game()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if back_btn.rect.collidepoint(event.pos):
                    return
                if toggle_btn.rect.collidepoint(event.pos):
                    sound_on = not sound_on
                    toggle_btn.text = "Sound: ON" if sound_on else "Sound: OFF"

            if event.type == pygame.MOUSEMOTION:
                back_btn.hovered = back_btn.rect.collidepoint(event.pos)
                toggle_btn.hovered = toggle_btn.rect.collidepoint(event.pos)

        SCREEN.fill(BG)
        hdr = TITLE_FONT.render("Settings", True, ACCENT)
        SCREEN.blit(hdr, hdr.get_rect(center=(WIDTH//2, HEIGHT//6)))
        toggle_btn.draw(SCREEN)
        back_btn.draw(SCREEN)

        hint = SMALL_FONT.render("Esc = Back", True, (150, 160, 170))
        SCREEN.blit(hint, (WIDTH - 110, HEIGHT - 30))

        pygame.display.flip()
        CLOCK.tick(FPS)

if __name__ == "__main__":
    menu_loop()
