# screens.py
# Herní smyčky - hlavní menu, samotná hra, game over a nastavení obtížnosti.
# Každá obrazovka je jedna funkce která běží ve vlastní smyčce.

import sys
import pygame
from constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT, FPS,
    BLACK, RED, DARK_GRAY, GRAY, PURPLE, WHITE, GREEN, GOLD,
    DIFFICULTY_PARAMS, settings,
)
from sprites import Player, spawn_object
from ui import (
    draw_text, draw_background, draw_hud,
    name_input_screen, leaderboard_screen, add_to_leaderboard,
)
from web_export import export_leaderboard_html

# Barvy pro plovoucí texty při kolizích
COLOR_PLUS  = (30,  180, 30)
COLOR_MINUS = (220, 40,  40)
COLOR_COMBO = (255, 180, 0 )


# --- Plovoucí text ---

class FloatText:
    # Text co vyskočí při kolizi a pomalu vybledne (např. "+10" nebo "-5")
    def __init__(self, text, x, y, color, font):
        self.text  = text
        self.x     = float(x)
        self.y     = float(y)
        self.color = color
        self.font  = font
        self.alpha = 255   # průhlednost, 0 = neviditelný
        self.dy    = -1.8  # pohybuje se nahoru

    def update(self):
        self.y     += self.dy
        self.alpha -= 5
        self.dy    *= 0.97  # postupně zpomaluje

    def is_dead(self):
        return self.alpha <= 0

    def draw(self, surface):
        surf = self.font.render(self.text, True, self.color)
        surf.set_alpha(max(0, int(self.alpha)))
        rect = surf.get_rect(center=(int(self.x), int(self.y)))
        surface.blit(surf, rect)


# --- Hlavní herní smyčka ---

def game_loop(screen, assets, fonts, clock):
    player      = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 40, assets['player'])
    objects     = []
    float_texts = []
    score       = 0
    lives       = 3
    combo       = 0         # kolik ovoce jsem chytil za sebou bez zmeškání
    spawn_timer = pygame.time.get_ticks()
    start_time  = pygame.time.get_ticks()
    params      = DIFFICULTY_PARAMS[settings['difficulty']]

    # Červený overlay pro varování při posledním životě
    warn_surface    = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    warn_surface.fill((220, 40, 40, 45))
    warn_blink      = 0
    warn_start_time = None  # kdy začalo blikání

    while True:
        clock.tick(FPS)
        keys = pygame.key.get_pressed()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return

        # Čas od začátku hry v sekundách
        elapsed_sec = (pygame.time.get_ticks() - start_time) / 1000

        # Každých 20 sekund se hra trochu zrychlí - o kolik záleží na obtížnosti
        speed_mult = 1.0 + (elapsed_sec // 20) * params['speed_increase']

        # Spawn nového objektu každých X milisekund
        now = pygame.time.get_ticks()
        if now - spawn_timer > params['spawn_interval']:
            spawn_timer = now
            objects.append(spawn_object(params, assets, speed_mult))

        player.update(keys)
        draw_background(screen, assets)

        # Červené blikání při posledním životě - ale jen prvních 5 sekund
        if lives == 1:
            if warn_start_time is None:
                warn_start_time = pygame.time.get_ticks()
            if (pygame.time.get_ticks() - warn_start_time) / 1000 < 5:
                warn_blink += 1
                if warn_blink % 60 < 30:
                    screen.blit(warn_surface, (0, 0))
        else:
            warn_start_time = None  # reset pokud by hráč získal život zpátky

        # Update objektů, detekce kolizí, vykreslení
        to_remove = []
        for obj in objects:
            obj.y += obj.speed * speed_mult
            r = obj.get_rect()

            if obj.image:
                screen.blit(obj.image, r)
            else:
                pygame.draw.rect(screen, obj.color or GRAY, r)

            # Kolize s hráčem pomocí masek (přesná detekce po pixelech)
            offset = (r.x - player.rect.x, r.y - player.rect.y)
            if player.mask.overlap(obj.get_mask(), offset):
                cx = r.centerx

                if obj.kind == 'fruit':
                    score += 10
                    combo += 1
                    float_texts.append(FloatText("+10", cx, r.top, COLOR_PLUS, fonts['small']))

                    # Combo bonus - každých 5 chycených za sebou = +25 navíc
                    if combo % 5 == 0:
                        score += 25
                        float_texts.append(
                            FloatText(f"Combo x{combo}  +25!", cx, r.top - 30, COLOR_COMBO, fonts['normal'])
                        )

                elif obj.kind == 'goldfruit':
                    # Zlaté jablko dává hodně bodů, ale je rychlejší
                    score += 25
                    combo += 1
                    float_texts.append(FloatText("+25", cx, r.top, COLOR_COMBO, fonts['small']))

                elif obj.kind == 'bomb':
                    lives -= 1
                    combo  = 0
                    float_texts.append(FloatText("-1 zivot", cx, r.top, COLOR_MINUS, fonts['normal']))

                to_remove.append(obj)
                continue

            # Objekt vypadl mimo obrazovku
            if obj.y > SCREEN_HEIGHT:
                if obj.kind == 'fruit':
                    # Zmeškaný zelený plod = -5
                    score = max(0, score - 5)
                    combo = 0
                    float_texts.append(
                        FloatText("-5", obj.x + obj.width // 2, SCREEN_HEIGHT - 30, COLOR_MINUS, fonts['small'])
                    )
                elif obj.kind == 'goldfruit':
                    # Zmeškaný zlatý plod = -10
                    score = max(0, score - 10)
                    combo = 0
                    float_texts.append(
                        FloatText("-10", obj.x + obj.width // 2, SCREEN_HEIGHT - 30, COLOR_MINUS, fonts['small'])
                    )
                to_remove.append(obj)

        for obj in to_remove:
            if obj in objects:
                objects.remove(obj)

        screen.blit(player.image, player.rect)

        # Vykreslení plovoucích textů
        for ft in float_texts[:]:
            ft.update()
            ft.draw(screen)
            if ft.is_dead():
                float_texts.remove(ft)

        # HUD
        draw_hud(screen, assets, fonts, score, lives)

        if combo >= 3:
            draw_text(f"Combo: {combo}", fonts['small'], COLOR_COMBO,
                      screen, SCREEN_WIDTH // 2, 14, center=True)

        draw_text(f"{int(elapsed_sec)}s", fonts['small'], DARK_GRAY,
                  screen, SCREEN_WIDTH // 2, 40, center=True)

        pygame.display.flip()

        if lives <= 0:
            game_over_screen(screen, assets, fonts, clock, score, int(elapsed_sec))
            return


# --- Game Over ---

def game_over_screen(screen, assets, fonts, clock, final_score, elapsed_time=0):
    # Zobrazí input pro jméno, uloží skóre + čas, ukáže žebříček
    try:
        player_name = name_input_screen(
            screen, assets, fonts, clock,
            final_score, settings['difficulty']
        )
    except SystemExit:
        raise

    if player_name:
        add_to_leaderboard(player_name, final_score, settings['difficulty'], elapsed_time)
        export_leaderboard_html()  # aktualizuje web

    leaderboard_screen(screen, assets, fonts, clock)

    # Čekací obrazovka s možností restartu
    while True:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    game_loop(screen, assets, fonts, clock)
                    return
                elif event.key == pygame.K_ESCAPE:
                    return

        draw_background(screen, assets)
        draw_text("GAME OVER",                fonts['large'],  RED,       screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 80)
        draw_text(f"Skore: {final_score}",    fonts['normal'], BLACK,     screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 20)
        draw_text(f"Cas: {elapsed_time}s",    fonts['small'],  DARK_GRAY, screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 15)
        draw_text("R = restart   |   ESC = menu",
                  fonts['small'], DARK_GRAY,  screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 55)
        pygame.display.flip()


# --- Nastavení obtížnosti ---

def settings_menu(screen, assets, fonts, clock):
    options  = list(DIFFICULTY_PARAMS.keys())
    selected = options.index(settings['difficulty'])

    descriptions = {
        'Easy':   'Pomale padani, vice casu',
        'Normal': 'Vyvazena obtiznost',
        'Hard':   'Rychle padani, mene casu',
    }

    while True:
        clock.tick(FPS)
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

        draw_background(screen, assets)
        draw_text("Nastaveni", fonts['large'], BLACK, screen, SCREEN_WIDTH // 2, 100)
        for i, diff in enumerate(options):
            color = PURPLE if i == selected else BLACK
            draw_text(diff, fonts['normal'], color, screen, SCREEN_WIDTH // 2, 240 + i * 70)
            if i == selected:
                draw_text(descriptions[diff], fonts['small'], DARK_GRAY,
                          screen, SCREEN_WIDTH // 2, 270 + i * 70)

        draw_text("<- -> pro zmenu, ESC / Enter pro navrat",
                  fonts['small'], DARK_GRAY, screen, SCREEN_WIDTH // 2, 520)
        pygame.display.flip()


# --- Hlavní menu ---

def main_menu(screen, assets, fonts, clock):
    selected = 0
    options  = ["Hrat", "Zebricek", "Nastaveni", "Konec"]

    while True:
        clock.tick(FPS)
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
                    choice = options[selected]
                    if choice == "Hrat":
                        game_loop(screen, assets, fonts, clock)
                    elif choice == "Zebricek":
                        leaderboard_screen(screen, assets, fonts, clock)
                    elif choice == "Nastaveni":
                        settings_menu(screen, assets, fonts, clock)
                    elif choice == "Konec":
                        pygame.quit()
                        sys.exit()

        draw_background(screen, assets)
        draw_text("FruitCatcher", fonts['large'], DARK_GRAY, screen, SCREEN_WIDTH // 2, 150)
        for i, opt in enumerate(options):
            color = PURPLE if i == selected else BLACK
            draw_text(opt, fonts['normal'], color, screen, SCREEN_WIDTH // 2, 290 + i * 60)
        pygame.display.flip()
