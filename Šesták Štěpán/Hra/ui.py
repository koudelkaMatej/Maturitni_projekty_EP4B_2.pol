# ui.py
# Stará se o vykreslování UI ve hře - texty, HUD, žebříček a input pro jméno.
# Taky tady je veškerá logika pro práci s databází (leaderboard.json).

import json
import os
import pygame
from constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT,
    WHITE, BLACK, RED, DARK_GRAY, GRAY, PURPLE, GOLD,
)

# Cesta k databázi - leaderboard.json leží ve složce web/
_HERE            = os.path.dirname(os.path.abspath(__file__))
LEADERBOARD_FILE = os.path.join(_HERE, "..", "web", "leaderboard.json")


def draw_text(text, font_obj, color, surface, x, y, center=True):
    # Vykreslí text na zadané souřadnice, defaultně zarovnaný na střed
    txt  = font_obj.render(text, True, color)
    rect = txt.get_rect(center=(x, y)) if center else txt.get_rect(topleft=(x, y))
    surface.blit(txt, rect)


def draw_background(screen, assets):
    # Nejdřív vyplní bílou, pak překryje obrázkem pozadí (pokud existuje)
    screen.fill(WHITE)
    if assets.get('background'):
        screen.blit(assets['background'], (0, 0))


def draw_hud(screen, assets, fonts, score, lives):
    # Skóre vlevo nahoře, životy vpravo nahoře
    draw_text(f"Skore: {score}", fonts['normal'], BLACK, screen, 10, 10, center=False)

    if assets.get('heart'):
        for i in range(lives):
            screen.blit(assets['heart'], (SCREEN_WIDTH - 40 - i * 36, 10))
    else:
        color = RED if lives <= 1 else BLACK
        draw_text(f"Zivoty: {lives}", fonts['normal'], color,
                  screen, SCREEN_WIDTH - 120, 10, center=False)


# --- Databáze ---

def load_leaderboard():
    # Načte záznamy z JSON souboru. Pokud soubor neexistuje nebo je poškozený,
    # vrátí prázdný seznam - hra tím pádem nespadne.
    if os.path.exists(LEADERBOARD_FILE):
        try:
            with open(LEADERBOARD_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data if isinstance(data, list) else []
        except (json.JSONDecodeError, IOError):
            return []
    return []


def save_leaderboard(board):
    # Uloží celý žebříček zpátky do souboru
    with open(LEADERBOARD_FILE, "w", encoding="utf-8") as f:
        json.dump(board, f, ensure_ascii=False, indent=2)


def add_to_leaderboard(name, score, difficulty, elapsed_time=0):
    # Přidá nový záznam, seřadí od nejvyššího skóre a uchová max. 100 záznamů.
    # Stará data se nepřepisují, jen se přidá nový řádek.
    board = load_leaderboard()

    board.append({
        "name":       name,
        "score":      score,
        "difficulty": difficulty,
        "time":       elapsed_time   # čas hry v sekundách
    })

    board.sort(key=lambda e: e["score"], reverse=True)
    board = board[:100]

    save_leaderboard(board)
    return board


# --- Obrazovka: zadání jména po Game Over ---

def name_input_screen(screen, assets, fonts, clock, final_score, difficulty):
    # Zobrazí textový input kde hráč napíše jméno.
    # Enter = uložit, ESC = přeskočit (vrátí prázdný řetězec)
    name         = ""
    MAX_LEN      = 16
    active       = True
    cursor_vis   = True
    cursor_timer = pygame.time.get_ticks()

    INPUT_W, INPUT_H = 320, 52
    input_rect = pygame.Rect(
        (SCREEN_WIDTH - INPUT_W) // 2,
        SCREEN_HEIGHT // 2 + 10,
        INPUT_W, INPUT_H,
    )

    while active:
        clock.tick(60)

        # Blikání kurzoru každých 500 ms
        now = pygame.time.get_ticks()
        if now - cursor_timer > 500:
            cursor_vis   = not cursor_vis
            cursor_timer = now

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return ""
                elif event.key == pygame.K_RETURN and name.strip():
                    active = False
                elif event.key == pygame.K_BACKSPACE:
                    name = name[:-1]
                else:
                    char = event.unicode
                    if char.isprintable() and len(name) < MAX_LEN:
                        name += char

        draw_background(screen, assets)
        draw_text("GAME OVER",                   fonts['large'],  RED,       screen, SCREEN_WIDTH // 2, 130)
        draw_text(f"Tvoje skore: {final_score}",  fonts['normal'], BLACK,     screen, SCREEN_WIDTH // 2, 210)
        draw_text("Zadej sve jmeno:",             fonts['small'],  DARK_GRAY, screen, SCREEN_WIDTH // 2, 295)

        pygame.draw.rect(screen, WHITE,  input_rect, border_radius=8)
        pygame.draw.rect(screen, PURPLE, input_rect, 2, border_radius=8)

        display_text = name + ("|" if cursor_vis else " ")
        draw_text(display_text, fonts['normal'], BLACK,
                  screen, input_rect.centerx, input_rect.centery)

        draw_text("Enter = ulozit   |   ESC = preskocit",
                  fonts['small'], GRAY, screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 90)
        pygame.display.flip()

    return name.strip()


# --- Obrazovka: žebříček ve hře ---

def leaderboard_screen(screen, assets, fonts, clock):
    # Zobrazí top 10 přímo v pygame okně. ESC nebo Enter = zpět.
    board   = load_leaderboard()
    running = True

    while running:
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_RETURN):
                    running = False

        draw_background(screen, assets)
        draw_text("Zebricek", fonts['large'], DARK_GRAY,
                  screen, SCREEN_WIDTH // 2, 55)

        if not board:
            draw_text("Zatim zadne zaznamy.", fonts['small'], GRAY,
                      screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        else:
            # Hlavička tabulky
            draw_text(
                f"{'Poradi':<5}  {'Jmeno':<16}  {'Skore':>6}  {'Cas':>6}  {'Obtiznost'}",
                fonts['small'], DARK_GRAY,
                screen, SCREEN_WIDTH // 2, 100
            )

            for rank, entry in enumerate(board[:10], 1):
                color = GOLD if rank == 1 else (GRAY if rank > 3 else BLACK)

                # Čas ve formátu M:SS
                t   = entry.get("time", 0)
                cas = f"{t // 60}:{t % 60:02d}" if t else "–"

                line = f"{rank:<5}  {entry['name']:<16}  {entry['score']:>6}  {cas:>6}  [{entry['difficulty']}]"
                draw_text(line, fonts['small'], color,
                          screen, SCREEN_WIDTH // 2, 130 + rank * 38)

        draw_text("ESC / Enter = zpet", fonts['small'], GRAY,
                  screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT - 36)
        pygame.display.flip()
