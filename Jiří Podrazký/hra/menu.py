import pygame
import sys
import subprocess
import requests
import os

# =============================================================================
# 1. GLOBÁLNÍ KONFIGURACE A DX (DEVELOPER EXPERIENCE)
# =============================================================================
# Tato sekce obsahuje síťové parametry a inicializaci grafického subsystému.

URL_CHECK_LOGIN = "https://xeon.spskladno.cz/~podrazkj/space_invaders/check_login.php"

pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Invaders - Enterprise Interface")

# Barevná paleta v modelu RGB - standardizace vizuálního stylu
WHITE, RED, GREEN, GRAY = (255, 255, 255), (255, 77, 77), (77, 255, 77), (50, 50, 50)
LIGHT_GRAY, BLACK, CYAN, GOLD = (150, 150, 150), (10, 10, 20), (0, 255, 255), (255, 215, 0)

# Typografie - inicializace systémových fontů
font_title = pygame.font.Font('freesansbold.ttf', 50)
font_text = pygame.font.Font('freesansbold.ttf', 28)
font_small = pygame.font.Font('freesansbold.ttf', 18)

# =============================================================================
# 2. ASSET MANAGEMENT (SPRÁVA ZDROJŮ)
# =============================================================================
# Dynamické načítání herních dat ze složky /data/.
# Tento přístup umožňuje snadné přidávání dalších modelů bez zásahu do logiky.

# Definice názvů souborů
BASE_NAMES = [
    "playerShip1_blue.png", "playerShip1_green.png", "playerShip1_orange.png", "playerShip1_red.png",
    "playerShip2_blue.png", "playerShip2_green.png", "playerShip2_orange.png", "playerShip2_red.png",
    "playerShip3_blue.png", "playerShip3_green.png", "playerShip3_orange.png", "playerShip3_red.png"
]

# Rekonstrukce cest k souborům: přidání prefixu 'data/'
SHIP_FILES = [os.path.join("data", f) for f in BASE_NAMES]

# Buffer pro uložení načtených textur (zabraňuje opakovanému čtení z disku)
ship_images = {}
for file_path in SHIP_FILES:
    if os.path.exists(file_path):
        # convert_alpha() optimalizuje obrázek pro rychlejší blitting v Pygame
        img = pygame.image.load(file_path).convert_alpha()
        # Škálování textury pro náhled v Hangáru
        ship_images[file_path] = pygame.transform.scale(img, (60, 50))

# =============================================================================
# 3. LOGICKÉ MODULY A STAVOVÉ PROMĚNNÉ
# =============================================================================

selected_ship = SHIP_FILES[0]  # Reference na aktuálně vybraný model lodi
username = ""
password = ""
active_field = "user"  # Kurzorem vybraný vstupní prvek
logged_in = False  # Příznak autorizace
current_screen = "login"  # Řídicí proměnná stavového automatu: login, menu, hangar
error_msg = ""
error_color = RED


def verify_login(u, p):
    """Abstraktní vrstva pro komunikaci s autentizačním API."""
    if not u or not p: return "EMPTY"
    try:
        # Synchronní POST požadavek na validační server
        r = requests.post(URL_CHECK_LOGIN, data={'username': u, 'password': p}, timeout=3)
        return "SUCCESS" if r.text.strip() == "OK" else "WRONG_CREDENTIALS"
    except Exception:
        return "OFFLINE"


def draw_button(text, x, y, w, h, color, text_color=WHITE):
    """Univerzální renderovací funkce pro UI komponentu 'Tlačítko'."""
    # Vykreslení těla tlačítka s definovaným zaoblením hran
    pygame.draw.rect(screen, color, (x, y, w, h), border_radius=10)
    # Centrování textového labelu uvnitř Rectu tlačítka
    label = font_text.render(text, True, text_color)
    screen.blit(label, (x + (w - label.get_width()) // 2, y + (h - label.get_height()) // 2))


# =============================================================================
# 4. MAIN LOOP (HLAVNÍ CYKLUS APLIKACE)
# =============================================================================

def main_menu():
    global username, password, active_field, logged_in, error_msg, error_color, current_screen, selected_ship

    clock = pygame.time.Clock()

    while True:
        screen.fill(BLACK)  # Resetování bufferu obrazovky
        mx, my = pygame.mouse.get_pos()  # Snímání souřadnic kurzoru pro detekci kolizí (Hover)

        # --- EVENT HANDLING (ZPRACOVÁNÍ UDÁLOSTÍ) ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit();
                sys.exit()

            # STAV: LOGIN (Autentizační rozhraní)
            if current_screen == "login":
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_TAB:
                        active_field = "pass" if active_field == "user" else "user"
                    elif event.key == pygame.K_BACKSPACE:
                        if active_field == "user":
                            username = username[:-1]
                        else:
                            password = password[:-1]
                    elif event.key == pygame.K_RETURN:
                        res = verify_login(username, password)
                        if res == "SUCCESS":
                            logged_in = True;
                            current_screen = "menu"
                        else:
                            error_msg = res;
                            error_color = RED
                    else:
                        # Omezení délky vstupu (Buffer overflow prevention)
                        if len(username if active_field == "user" else password) < 15:
                            if event.unicode.isprintable():
                                if active_field == "user":
                                    username += event.unicode
                                else:
                                    password += event.unicode

            # STAV: MENU (Navigační rozcestník)
            elif current_screen == "menu":
                if event.type == pygame.MOUSEBUTTONDOWN:
                    # Definice interakčních zón (Rect collision)
                    if 300 <= mx <= 500 and 200 <= my <= 260:  # Spuštění herního modulu
                        # Předání parametrů relace do externího procesu pomocí stejného interpretu (venv)
                        subprocess.run([sys.executable, "main.py", username, selected_ship])
                        sys.exit()
                    if 300 <= mx <= 500 and 280 <= my <= 340:  # Přechod do Hangáru
                        current_screen = "hangar"
                    if 300 <= mx <= 500 and 360 <= my <= 420:  # Ukončení aplikace
                        pygame.quit();
                        sys.exit()

            # STAV: HANGAR (Výběr parametrů entity)
            elif current_screen == "hangar":
                if event.type == pygame.MOUSEBUTTONDOWN:
                    # Iterace mřížkou objektů pro detekci výběru (Grid Collision)
                    for i, file_path in enumerate(SHIP_FILES):
                        ix = 150 + (i % 4) * 130  # Výpočet horizontální pozice v mřížce
                        iy = 180 + (i // 4) * 100  # Výpočet vertikální pozice v mřížce
                        if ix <= mx <= ix + 100 and iy <= my <= iy + 80:
                            selected_ship = file_path
                    if 300 <= mx <= 500 and 500 <= my <= 550:  # Návrat do menu
                        current_screen = "menu"

        # --- RENDERER (VYKRESLOVACÍ PIPELINE) ---
        if current_screen == "login":
            img_title = font_title.render("SPACE INVADERS", True, CYAN)
            screen.blit(img_title, (WIDTH // 2 - img_title.get_width() // 2, 80))

            u_col = CYAN if active_field == "user" else GRAY
            pygame.draw.rect(screen, u_col, (250, 200, 300, 45), 2, border_radius=5)
            screen.blit(font_text.render(f"Jméno: {username}", True, WHITE), (260, 208))

            p_col = CYAN if active_field == "pass" else GRAY
            pygame.draw.rect(screen, p_col, (250, 280, 300, 45), 2, border_radius=5)
            screen.blit(font_text.render(f"Heslo: {'*' * len(password)}", True, WHITE), (260, 288))

            if error_msg:
                err = font_small.render(error_msg, True, error_color)
                screen.blit(err, (WIDTH // 2 - err.get_width() // 2, 350))

        elif current_screen == "menu":
            welcome = font_title.render(f"VÍTEJ, {username.upper()}!", True, GREEN)
            screen.blit(welcome, (WIDTH // 2 - welcome.get_width() // 2, 80))

            # Preview vybraného modelu
            txt = font_small.render("AKTIVNÍ KONFIGURACE:", True, LIGHT_GRAY)
            screen.blit(txt, (WIDTH // 2 - txt.get_width() // 2, 145))
            if selected_ship in ship_images:
                screen.blit(ship_images[selected_ship], (WIDTH // 2 - 30, 165))

            draw_button("HRÁT", 300, 200, 200, 60, GRAY if not (300 <= mx <= 500 and 200 <= my <= 260) else GREEN)
            draw_button("HANGÁR", 300, 280, 200, 60, GRAY if not (300 <= mx <= 500 and 280 <= my <= 340) else CYAN)
            draw_button("KONEC", 300, 360, 200, 60, GRAY if not (300 <= mx <= 500 and 360 <= my <= 420) else RED)

        elif current_screen == "hangar":
            title = font_title.render("HANGÁR", True, GOLD)
            screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 50))

            for i, file_path in enumerate(SHIP_FILES):
                ix = 150 + (i % 4) * 130
                iy = 180 + (i // 4) * 100

                # Vizualizace výběru (Highlighter)
                bg_col = GOLD if selected_ship == file_path else GRAY
                pygame.draw.rect(screen, bg_col, (ix, iy, 100, 80), border_radius=10)

                if file_path in ship_images:
                    screen.blit(ship_images[file_path], (ix + 20, iy + 15))

            draw_button("ZPĚT", 300, 500, 200, 50, RED)

        pygame.display.flip()  # Překlopení bufferu do GPU (Frame refresh)
        clock.tick(30)  # Omezení snímkové frekvence (CPU throttling)


if __name__ == "__main__":
    main_menu()