import pygame
import random
import sys
from dataclasses import dataclass

# Nastavení
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
PLAYER_WIDTH = 80
PLAYER_HEIGHT = 20
FALL_SIZE = 30
FONT_NAME = None

# Výchozí nastavení hry
settings = {
    'difficulty': 'Normal',  # 'Easy', 'Normal', 'Hard'
}

# Obtížnosti
DIFFICULTY_PARAMS = {
    'Easy': {'fall_speed': 3, 'spawn_interval': 900},
    'Normal': {'fall_speed': 4.5, 'spawn_interval': 700},
    'Hard': {'fall_speed': 6, 'spawn_interval': 450},
}

# Barvy
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (50, 200, 50)
RED = (220, 40, 40)
GRAY = (200, 200, 200)
DARK_GRAY = (50, 50, 50)

# pygame
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('FruitCatcher')
clock = pygame.time.Clock()
font = pygame.font.SysFont(FONT_NAME, 28)
large_font = pygame.font.SysFont(FONT_NAME, 48)
small_font = pygame.font.SysFont(FONT_NAME, 20)

# Třídy
class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, speed=6):
        super().__init__()
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
    size: int
    color: tuple
    kind: str
    speed: float

    def rect(self):
        return pygame.Rect(int(self.x), int(self.y), self.size, self.size)

# Herní funkce
def draw_text(text, font, color, surface, x, y, center=True):
    txt = font.render(text, True, color)
    rect = txt.get_rect(center=(x, y)) if center else txt.get_rect(topleft=(x, y))
    surface.blit(txt, rect)

def game_loop():
    player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 40, PLAYER_WIDTH, PLAYER_HEIGHT)
    objects = []
    score = 0
    running = True
    spawn_timer = pygame.time.get_ticks()
    params = DIFFICULTY_PARAMS[settings['difficulty']]

    while running:
        dt = clock.tick(FPS)
        screen.fill(WHITE)
        keys = pygame.key.get_pressed()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False

        # Spawn nového objektu
        if pygame.time.get_ticks() - spawn_timer > params['spawn_interval']:
            spawn_timer = pygame.time.get_ticks()
            kind = random.choice(['fruit'] * 3 + ['bomb'])
            color = GREEN if kind == 'fruit' else RED
            x = random.randint(0, SCREEN_WIDTH - FALL_SIZE)
            obj = FallingObject(x, 0, FALL_SIZE, color, kind, params['fall_speed'])
            objects.append(obj)

        # Aktualizace hráče
        player.update(keys)
        screen.blit(player.image, player.rect)

        # Aktualizace objektů
        for obj in objects[:]:
            obj.y += obj.speed
            pygame.draw.rect(screen, obj.color, obj.rect())
            if obj.rect().colliderect(player.rect):
                if obj.kind == 'fruit':
                    score += 1
                else:
                    score = max(0, score - 2)
                objects.remove(obj)
            elif obj.y > SCREEN_HEIGHT:
                objects.remove(obj)

        draw_text(f"Skóre: {score}", font, BLACK, screen, 80, 30, center=False)
        pygame.display.flip()

def settings_menu():
    selected = list(DIFFICULTY_PARAMS.keys()).index(settings['difficulty'])
    options = list(DIFFICULTY_PARAMS.keys())
    while True:
        screen.fill(WHITE)
        draw_text("Nastavení", large_font, BLACK, screen, SCREEN_WIDTH // 2, 100)
        for i, diff in enumerate(options):
            color = GREEN if i == selected else BLACK
            draw_text(diff, font, color, screen, SCREEN_WIDTH // 2, 250 + i * 60)
        draw_text("<- -> pro změnu, ESC pro návrat", small_font, DARK_GRAY, screen, SCREEN_WIDTH // 2, 500)

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

        pygame.display.flip()
        clock.tick(FPS)

def main_menu():
    selected = 0
    options = ["Hrát", "Nastavení", "Konec"]

    while True:
        screen.fill(WHITE)
        draw_text("FruitCatcher ", large_font, DARK_GRAY, screen, SCREEN_WIDTH // 2, 150)
        for i, opt in enumerate(options):
            color = GREEN if i == selected else BLACK
            draw_text(opt, font, color, screen, SCREEN_WIDTH // 2, 300 + i * 60)
        pygame.display.flip()

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

        clock.tick(FPS)

# Spuštění
if __name__ == "__main__":
    main_menu()
