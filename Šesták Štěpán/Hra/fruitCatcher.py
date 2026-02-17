import pygame
import random
import sys
from dataclasses import dataclass

# --- Nastavení ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
PLAYER_WIDTH = 80
PLAYER_HEIGHT = 20
FALL_SIZE = 30

# Výchozí nastavení hry
settings = {
    'difficulty': 'Normal',  # 'Easy', 'Normal', 'Hard'
}

DIFFICULTY_PARAMS = {
    'Easy': {'fall_speed': 2, 'spawn_interval': 900},
    'Normal': {'fall_speed': 3, 'spawn_interval': 700},
    'Hard': {'fall_speed': 4.5, 'spawn_interval': 450},
}

# Barvy
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (50, 200, 50)
RED = (220, 40, 40)
DARK_GRAY = (50, 50, 50)
GRAY = (200, 200, 200)
ORANGE = (255, 140, 0)


pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('FruitCatcher')
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 28)
large_font = pygame.font.SysFont(None, 48)
small_font = pygame.font.SysFont(None, 20)

# --- Načítání obrázků (s fallback) ---
def load_image(path, size=None):
    try:
        img = pygame.image.load(path).convert_alpha()
        if size is not None:
            img = pygame.transform.smoothscale(img, size)
        return img
    except Exception:
        return None

# pozadí
background = load_image("obrazky/background.png", (SCREEN_WIDTH, SCREEN_HEIGHT))


# objekty
player_img = load_image("obrazky/Kosik.png", (120, 70))
fruit_img = load_image("obrazky/fruit.png", (FALL_SIZE, FALL_SIZE))
bomb_img = load_image("obrazky/bomb.png", (FALL_SIZE, FALL_SIZE))
gold_img = load_image("obrazky/goldfruit.png", (FALL_SIZE, FALL_SIZE))
heart_img = load_image("obrazky/heart.png", (32, 32))

# --- Třídy ---
class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, speed=6):
        super().__init__()
        if player_img:
            self.image = player_img
        else:
            self.image = pygame.Surface((width, height))
            self.image.fill(DARK_GRAY)
            pygame.draw.rect(self.image, BLACK, self.image.get_rect(), 2)
        self.rect = self.image.get_rect(midbottom=(x, y))
        self.speed = speed

    def update(self, keys):
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.rect.x += self.speed
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH

@dataclass
class FallingObject:
    x: float
    y: float
    width: int
    height: int
    kind: str            # 'fruit', 'bomb', 'goldfruit'
    speed: float
    image: pygame.Surface = None
    color: tuple = None

    def rect(self):
        return pygame.Rect(int(self.x), int(self.y), self.width, self.height)

# --- Pomocné funkce ---
def draw_text(text, font_obj, color, surface, x, y, center=True):
    txt = font_obj.render(text, True, color)
    rect = txt.get_rect(center=(x, y)) if center else txt.get_rect(topleft=(x, y))
    surface.blit(txt, rect)

def spawn_object(params):
    kinds = ['fruit'] * 6 + ['bomb'] * 2 + ['goldfruit']  # váhy
    kind = random.choice(kinds)
    x = random.randint(0, SCREEN_WIDTH - FALL_SIZE)
    speed = params['fall_speed'] + random.uniform(-0.5, 1.0)
    if kind == 'fruit':
        img = fruit_img
        color = GREEN
    elif kind == 'bomb':
        img = bomb_img
        color = RED
    else:
        img = gold_img
        color = (255, 215, 0)  # zlatá pokud není obrázek
    return FallingObject(x, 0, FALL_SIZE, FALL_SIZE, kind, speed, image=img, color=color)

# --- HERNÍ SMYČKA ---
def game_loop():
    player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 40, PLAYER_WIDTH, PLAYER_HEIGHT)
    objects = []
    score = 0
    lives = 3
    running = True
    spawn_timer = pygame.time.get_ticks()
    params = DIFFICULTY_PARAMS[settings['difficulty']]

    while running:
        dt = clock.tick(FPS)
        keys = pygame.key.get_pressed()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return  # návrat do menu

        # spawn
        if pygame.time.get_ticks() - spawn_timer > params['spawn_interval']:
            spawn_timer = pygame.time.get_ticks()
            objects.append(spawn_object(params))

        # update hráče
        player.update(keys)

        # vykreslení pozadí hry
        if background:
            screen.blit(background, (0, 0))
        else:
            screen.fill(WHITE)

        # aktualizace a vykreslení objektů
        for obj in objects[:]:
            obj.y += obj.speed
            r = obj.rect()
            if obj.image:
                screen.blit(obj.image, r)
            else:
                pygame.draw.rect(screen, obj.color if obj.color else GRAY, r)

            # kolize s hráčem
            if r.colliderect(player.rect):
                if obj.kind == 'fruit':
                    score += 5
                elif obj.kind == 'goldfruit':
                    score += 100
                elif obj.kind == 'bomb':
                    lives -= 1
                objects.remove(obj)
                continue

            # pokud spadne dolů
            if obj.y > SCREEN_HEIGHT:
                # uvažuj penalizaci pokud chceš (zatím žádná)
                objects.remove(obj)

        # vykresli hráče
        screen.blit(player.image, player.rect)

        # HUD: skóre a životy
        draw_text(f"Skóre: {score}", font, BLACK, screen, 80, 30, center=False)
        # životy: buď ikony nebo text
        if heart_img:
            for i in range(lives):
                screen.blit(heart_img, (SCREEN_WIDTH - 40 - i*36, 10))
        else:
            draw_text(f"Životy: {lives}", font, RED if lives<=1 else BLACK, screen, SCREEN_WIDTH - 120, 30, center=False)

        pygame.display.flip()

        # konečnost hry
        if lives <= 0:
            game_over_loop(score)
            return  # po Game Over návrat do menu

def game_over_loop(final_score):
    # zobrazení Game Over a nabídka restart/menu
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:  # restart hry hned
                    game_loop()
                    return
                elif event.key == pygame.K_ESCAPE:  # návrat do menu
                    return

        if background:
            screen.blit(background, (0, 0))
        else:
            screen.fill((30, 30, 30))

        draw_text("GAME OVER", large_font, RED, screen, SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 80)
        draw_text(f"Skóre: {final_score}", font, BLACK, screen, SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 20)
        draw_text("Stiskni R pro restart, ESC pro návrat do menu", small_font, DARK_GRAY, screen, SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 40)

        pygame.display.flip()
        clock.tick(FPS)

# --- NASTAVENÍ MENU ---
def settings_menu():
    selected = list(DIFFICULTY_PARAMS.keys()).index(settings['difficulty'])
    options = list(DIFFICULTY_PARAMS.keys())
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    settings['difficulty'] = options[selected]
                    return
                elif event.key == pygame.K_LEFT:
                    selected = (selected - 1) % len(options)
                elif event.key == pygame.K_RIGHT:
                    selected = (selected + 1) % len(options)

        if background:
            screen.blit(background, (0, 0))
        else:
            screen.fill(WHITE)

        draw_text("Nastavení", large_font, BLACK, screen, SCREEN_WIDTH // 2, 100)
        for i, diff in enumerate(options):
            color = ORANGE if i == selected else BLACK
            draw_text(diff, font, color, screen, SCREEN_WIDTH // 2, 250 + i * 60)
        draw_text("<- -> pro změnu, ESC pro návrat", small_font, DARK_GRAY, screen, SCREEN_WIDTH // 2, 500)

        pygame.display.flip()
        clock.tick(FPS)

# --- HLAVNÍ MENU ---
def main_menu():
    selected = 0
    options = ["Hrát", "Nastavení", "Konec"]

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected = (selected - 1) % len(options)
                elif event.key == pygame.K_DOWN:
                    selected = (selected + 1) % len(options)
                elif event.key == pygame.K_RETURN:
                    if options[selected] == "Hrát":
                        game_loop()
                    elif options[selected] == "Nastavení":
                        settings_menu()
                    elif options[selected] == "Konec":
                        pygame.quit()
                        sys.exit()

        if background:
             screen.blit(background, (0, 0))
        else:
            screen.fill(WHITE)

        draw_text("FruitCatcher", large_font, DARK_GRAY, screen, SCREEN_WIDTH // 2, 150)
        for i, opt in enumerate(options):
            color = ORANGE if i == selected else BLACK
            draw_text(opt, font, color, screen, SCREEN_WIDTH // 2, 300 + i * 60)

        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    main_menu()
