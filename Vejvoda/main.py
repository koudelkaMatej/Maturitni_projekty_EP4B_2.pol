import pygame
import sys
import random

# --- ZÁKLADNÍ NASTAVENÍ ---
pygame.init()
WIDTH, HEIGHT = 400, 600
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Flappy Bird (Pygame)")

FPS = 60
CLOCK = pygame.time.Clock()

# --- BARVY ---
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BG_COLOR = (25, 25, 35)
BIRD_COLOR = (255, 230, 0)
PIPE_COLOR = (50, 200, 100)

# --- FONTY ---
FONT_BIG = pygame.font.SysFont("arial", 40, bold=True)
FONT_MED = pygame.font.SysFont("arial", 28, bold=True)
FONT_SMALL = pygame.font.SysFont("arial", 20)

# --- PTÁK ---
BIRD_SIZE = 30
bird_x = 100
bird_y = HEIGHT // 2
bird_vel_y = 0
gravity = 0.4
jump_power = -8

# --- TRUBKY ---
pipe_width = 60
pipe_gap = 150
pipe_speed = 3
pipes = []  # list (x, top_height)

PIPE_SPAWN_TIME = 1500  # ms
pygame.time.set_timer(pygame.USEREVENT + 1, PIPE_SPAWN_TIME)

# --- SKÓRE / STAV HRY ---
score = 0
best_score = 0
game_state = "MENU"  # "MENU" | "PLAYING" | "GAME_OVER"

def reset_game():
    global bird_y, bird_vel_y, pipes, score
    bird_y = HEIGHT // 2
    bird_vel_y = 0
    pipes = []
    score = 0

def spawn_pipe():
    # náhodně posuneme mezeru nahoru/dolů
    min_top = 50
    max_top = HEIGHT - pipe_gap - 50
    top_height = random.randint(min_top, max_top)
    pipes.append([WIDTH, top_height])  # x, top_height

def draw_text_center(text, font, color, y):
    surf = font.render(text, True, color)
    rect = surf.get_rect(center=(WIDTH // 2, y))
    WIN.blit(surf, rect)

def draw_game():
    WIN.fill(BG_COLOR)

    # trubky
    for x, top_height in pipes:
        # horní
        top_rect = pygame.Rect(x, 0, pipe_width, top_height)
        # spodní
        bottom_rect = pygame.Rect(x, top_height + pipe_gap, pipe_width, HEIGHT)
        pygame.draw.rect(WIN, PIPE_COLOR, top_rect, border_radius=5)
        pygame.draw.rect(WIN, PIPE_COLOR, bottom_rect, border_radius=5)

    # pták
    bird_rect = pygame.Rect(bird_x, int(bird_y), BIRD_SIZE, BIRD_SIZE)
    pygame.draw.rect(WIN, BIRD_COLOR, bird_rect, border_radius=10)

    # skóre
    score_surf = FONT_MED.render(f"Skóre: {score}", True, WHITE)
    WIN.blit(score_surf, (10, 10))

def check_collision():
    # náraz o horní/spodní okraj
    if bird_y <= 0 or bird_y + BIRD_SIZE >= HEIGHT:
        return True

    bird_rect = pygame.Rect(bird_x, int(bird_y), BIRD_SIZE, BIRD_SIZE)

    for x, top_height in pipes:
        top_rect = pygame.Rect(x, 0, pipe_width, top_height)
        bottom_rect = pygame.Rect(x, top_height + pipe_gap, pipe_width, HEIGHT)
        if bird_rect.colliderect(top_rect) or bird_rect.colliderect(bottom_rect):
            return True

    return False

def update_score():
    global score
    bird_center_x = bird_x + BIRD_SIZE // 2
    for x, _ in pipes:
        # když pták proletí středem trubky
        if x + pipe_width // 2 == bird_center_x:
            score += 1

def handle_menu():
    WIN.fill(BG_COLOR)
    draw_text_center("Flappy Bird", FONT_BIG, WHITE, HEIGHT // 3)
    draw_text_center("Stiskni SPACE pro start", FONT_MED, WHITE, HEIGHT // 3 + 60)
    if best_score > 0:
        draw_text_center(f"Nejlepší skóre: {best_score}", FONT_SMALL, WHITE, HEIGHT // 3 + 110)

def handle_game_over():
    WIN.fill(BG_COLOR)
    draw_text_center("KONEC HRY", FONT_BIG, WHITE, HEIGHT // 3)
    draw_text_center(f"Skóre: {score}", FONT_MED, WHITE, HEIGHT // 3 + 60)
    draw_text_center(f"Nejlepší skóre: {best_score}", FONT_SMALL, WHITE, HEIGHT // 3 + 100)
    draw_text_center("SPACE = znovu | ESC = konec", FONT_SMALL, WHITE, HEIGHT // 3 + 150)

# --- HLAVNÍ CYKLUS ---
running = True
while running:
    CLOCK.tick(FPS)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # spawn trubek jen při hraní
        if event.type == pygame.USEREVENT + 1 and game_state == "PLAYING":
            spawn_pipe()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if game_state == "PLAYING":
                    # ESC během hry = návrat do menu
                    game_state = "MENU"
                    reset_game()
                else:
                    running = False

            if event.key == pygame.K_SPACE:
                if game_state == "MENU":
                    reset_game()
                    game_state = "PLAYING"
                elif game_state == "PLAYING":
                    bird_vel_y = jump_power
                elif game_state == "GAME_OVER":
                    reset_game()
                    game_state = "PLAYING"

    # --- LOGIKA PODLE STAVU ---
    if game_state == "MENU":
        handle_menu()

    elif game_state == "PLAYING":
        # fyzika ptáka
        bird_vel_y += gravity
        bird_y += bird_vel_y

        # posun trubek
        for pipe in pipes:
            pipe[0] -= pipe_speed

        # odstraníme trubky mimo obraz
        pipes = [p for p in pipes if p[0] + pipe_width > 0]

        # kontrola skóre
        update_score()

        # kolize
        if check_collision():
            game_state = "GAME_OVER"
            if score > best_score:
                best_score = score

        # kreslení hry
        draw_game()

    elif game_state == "GAME_OVER":
        handle_game_over()

    pygame.display.flip()

pygame.quit()
sys.exit()
