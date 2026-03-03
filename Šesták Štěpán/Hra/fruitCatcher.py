import pygame
import random
import sys
from dataclasses import dataclass, field

# --- Nastavení ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
PLAYER_WIDTH = 240
PLAYER_HEIGHT = 120
FALL_SIZE = 80

# Výchozí nastavení hry
settings = {'difficulty': 'Normal'}  # 'Easy', 'Normal', 'Hard'

DIFFICULTY_PARAMS = {
    'Easy':   {'fall_speed': 2,   'spawn_interval': 900},
    'Normal': {'fall_speed': 3,   'spawn_interval': 700},
    'Hard':   {'fall_speed': 4.5, 'spawn_interval': 450},
}

# Barvy
WHITE     = (255, 255, 255)
BLACK     = (0,   0,   0  )
RED       = (220, 40,  40 )
GREEN     = (50,  200, 50 )
DARK_GRAY = (50,  50,  50 )
GRAY      = (200, 200, 200)
PURPLE    = (128, 0,   128)
GOLD      = (255, 215, 0  )

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('FruitCatcher')
clock = pygame.time.Clock()
font       = pygame.font.SysFont(None, 42)
large_font = pygame.font.SysFont(None, 74)
small_font = pygame.font.SysFont(None, 36)

# --- Načítání obrázků ---
def load_image(path, size):
    """Load image safely; returns None on failure."""
    try:
        img = pygame.image.load(path).convert_alpha()
        img = pygame.transform.scale(img, size)
        # Only set colorkey for images that actually use pure white as transparency
        # (skip set_colorkey to preserve alpha channel from convert_alpha)
        return img
    except (pygame.error, FileNotFoundError):
        return None

# Obrázky – graceful fallback to None if files are missing
background = load_image("obrazky/background.png", (SCREEN_WIDTH, SCREEN_HEIGHT))
player_img = load_image("obrazky/Kosik.png",       (PLAYER_WIDTH, PLAYER_HEIGHT))
fruit_img  = load_image("obrazky/fruit.png",       (FALL_SIZE, FALL_SIZE))
bomb_img   = load_image("obrazky/bomb.png",        (FALL_SIZE, FALL_SIZE))
gold_img   = load_image("obrazky/goldfruit.png",   (FALL_SIZE, FALL_SIZE))
heart_img  = load_image("obrazky/heart.png",       (32, 32))

# --- Třídy ---
class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, speed=6):
        super().__init__()
        if player_img:
            self.image = player_img.copy()
        else:
            self.image = pygame.Surface((PLAYER_WIDTH, PLAYER_HEIGHT), pygame.SRCALPHA)
            self.image.fill(DARK_GRAY)
            pygame.draw.rect(self.image, BLACK, self.image.get_rect(), 2)

        self.rect  = self.image.get_rect(midbottom=(x, y))
        self.mask  = pygame.mask.from_surface(self.image)
        self.speed = speed

    def update(self, keys):
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.rect.x += self.speed
        self.rect.left  = max(self.rect.left, 0)
        self.rect.right = min(self.rect.right, SCREEN_WIDTH)


@dataclass
class FallingObject:
    x:      float
    y:      float
    kind:   str
    speed:  float
    width:  int              = FALL_SIZE
    height: int              = FALL_SIZE
    image:  object           = field(default=None, repr=False)  # pygame.Surface | None
    color:  tuple            = None
    # Cache the mask so it isn't rebuilt every frame
    _mask:  object           = field(default=None, init=False, repr=False)

    def get_rect(self) -> pygame.Rect:
        return pygame.Rect(int(self.x), int(self.y), self.width, self.height)

    def get_mask(self) -> pygame.mask.Mask:
        if self._mask is None:
            if self.image:
                self._mask = pygame.mask.from_surface(self.image)
            else:
                temp = pygame.Surface((self.width, self.height))
                temp.fill(self.color if self.color else GRAY)
                self._mask = pygame.mask.from_surface(temp)
        return self._mask


# --- Pomocné funkce ---
def draw_text(text, font_obj, color, surface, x, y, center=True):
    txt  = font_obj.render(text, True, color)
    rect = txt.get_rect(center=(x, y)) if center else txt.get_rect(topleft=(x, y))
    surface.blit(txt, rect)


def draw_background():
    """Fill with white first, then blit the background image on top."""
    screen.fill(WHITE)
    if background:
        screen.blit(background, (0, 0))


def spawn_object(params) -> FallingObject:
    kinds = ['fruit'] * 6 + ['bomb'] * 2 + ['goldfruit']
    kind  = random.choice(kinds)
    x     = random.randint(0, SCREEN_WIDTH - FALL_SIZE)
    speed = params['fall_speed'] + random.uniform(-0.5, 1.0)

    if kind == 'fruit':
        img   = fruit_img
        color = GREEN
    elif kind == 'bomb':
        img   = bomb_img
        color = RED
    else:
        img   = gold_img
        color = GOLD

    return FallingObject(x, 0, kind, speed, image=img, color=color)


# --- Herní smyčka ---
def game_loop():
    player      = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 40)
    objects     = []
    score       = 0
    lives       = 3
    spawn_timer = pygame.time.get_ticks()
    params      = DIFFICULTY_PARAMS[settings['difficulty']]

    while True:
        clock.tick(FPS)
        keys = pygame.key.get_pressed()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return  # back to main menu

        # Spawn nových objektů
        now = pygame.time.get_ticks()
        if now - spawn_timer > params['spawn_interval']:
            spawn_timer = now
            objects.append(spawn_object(params))

        # Update hráče
        player.update(keys)

        # Vykreslení pozadí (bílá plocha + obrázek)
        draw_background()

        # Update, kolize a vykreslení padajících objektů
        to_remove = []
        for obj in objects:
            obj.y += obj.speed
            r = obj.get_rect()

            if obj.image:
                screen.blit(obj.image, r)
            else:
                pygame.draw.rect(screen, obj.color if obj.color else GRAY, r)

            # Kolize přes masky
            offset = (r.x - player.rect.x, r.y - player.rect.y)
            if player.mask.overlap(obj.get_mask(), offset):
                if obj.kind == 'fruit':
                    score += 5
                elif obj.kind == 'goldfruit':
                    score += 100
                elif obj.kind == 'bomb':
                    lives -= 1
                to_remove.append(obj)
                continue

            # Vypadl dolů
            if obj.y > SCREEN_HEIGHT:
                to_remove.append(obj)

        # Odstranit mimo smyčku, aby nedošlo k modifikaci za iterace
        for obj in to_remove:
            if obj in objects:
                objects.remove(obj)

        # Vykresli hráče
        screen.blit(player.image, player.rect)

        # HUD – skóre
        draw_text(f"Skóre: {score}", font, BLACK, screen, 10, 10, center=False)

        # HUD – životy
        if heart_img:
            for i in range(lives):
                screen.blit(heart_img, (SCREEN_WIDTH - 40 - i * 36, 10))
        else:
            draw_text(
                f"Životy: {lives}",
                font,
                RED if lives <= 1 else BLACK,
                screen,
                SCREEN_WIDTH - 120, 10,
                center=False,
            )

        pygame.display.flip()

        if lives <= 0:
            game_over_loop(score)
            return


# --- Game Over ---
def game_over_loop(final_score):
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    game_loop()
                    return
                elif event.key == pygame.K_ESCAPE:
                    return

        draw_background()
        draw_text("GAME OVER",   large_font, RED,       screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 80)
        draw_text(f"Skóre: {final_score}", font, BLACK, screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 20)
        draw_text(
            "Stiskni R pro restart, ESC pro návrat",
            small_font, DARK_GRAY, screen,
            SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 40,
        )
        pygame.display.flip()
        clock.tick(FPS)


# --- Nastavení (obtížnost) ---
def settings_menu():
    options  = list(DIFFICULTY_PARAMS.keys())
    selected = options.index(settings['difficulty'])

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    settings['difficulty'] = options[selected]
                    return
                elif event.key in (pygame.K_LEFT, pygame.K_UP):
                    selected = (selected - 1) % len(options)
                elif event.key in (pygame.K_RIGHT, pygame.K_DOWN):
                    selected = (selected + 1) % len(options)
                elif event.key == pygame.K_RETURN:
                    settings['difficulty'] = options[selected]
                    return

        draw_background()
        draw_text("Nastavení", large_font, BLACK, screen, SCREEN_WIDTH // 2, 100)
        for i, diff in enumerate(options):
            color = PURPLE if i == selected else BLACK
            draw_text(diff, font, color, screen, SCREEN_WIDTH // 2, 250 + i * 60)
        draw_text(
            "<- -> pro změnu, ESC / Enter pro návrat",
            small_font, DARK_GRAY, screen, SCREEN_WIDTH // 2, 500,
        )
        pygame.display.flip()
        clock.tick(FPS)


# --- Hlavní menu ---
def main_menu():
    selected = 0
    options  = ["Hrát", "Nastavení", "Konec"]

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

        draw_background()
        draw_text("FruitCatcher", large_font, DARK_GRAY, screen, SCREEN_WIDTH // 2, 150)
        for i, opt in enumerate(options):
            color = PURPLE if i == selected else BLACK
            draw_text(opt, font, color, screen, SCREEN_WIDTH // 2, 300 + i * 60)
        pygame.display.flip()
        clock.tick(FPS)


if __name__ == "__main__":
    main_menu()