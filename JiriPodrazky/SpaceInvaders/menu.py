import pygame
import sys
import subprocess
import requests

# --- KONFIGURACE ---
# Ujisti se, že tato URL odpovídá tvému nastavení na Apache
URL_CHECK_LOGIN = "https://xeon.spskladno.cz/~podrazkj/space_invaders/check_login.php"

pygame.init()

# Nastavení okna
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Invaders - Login & Menu")

# Barvy
WHITE = (255, 255, 255)
RED = (255, 77, 77)
GREEN = (77, 255, 77)
GRAY = (50, 50, 50)
LIGHT_GRAY = (150, 150, 150)
BLACK = (10, 10, 20)
CYAN = (0, 255, 255)

# Fonty
font_title = pygame.font.Font('freesansbold.ttf', 50)
font_text = pygame.font.Font('freesansbold.ttf', 28)
font_small = pygame.font.Font('freesansbold.ttf', 18)

# Proměnné
username = ""
password = ""
active_field = "user"  # "user" nebo "pass"
logged_in = False
error_msg = ""
error_color = RED


def verify_login(u, p):
    """Komunikace s PHP serverem s debug informacemi."""
    if not u or not p:
        return "EMPTY"

    try:
        payload = {'username': u, 'password': p}
        # Timeout 3s - pokud server neběží, nečekáme dlouho
        r = requests.post(URL_CHECK_LOGIN, data=payload, timeout=3)

        if r.status_code == 200:
            if r.text.strip() == "OK":
                return "SUCCESS"
            else:
                return "WRONG_CREDENTIALS"
        else:
            return f"SERVER_ERROR_{r.status_code}"

    except requests.exceptions.ConnectionError:
        return "OFFLINE"
    except requests.exceptions.Timeout:
        return "TIMEOUT"
    except Exception as e:
        return f"UNKNOWN_{str(e)}"


def draw_button(text, x, y, w, h, color):
    pygame.draw.rect(screen, color, (x, y, w, h), border_radius=10)
    label = font_text.render(text, True, WHITE)
    screen.blit(label, (x + (w - label.get_width()) // 2, y + (h - label.get_height()) // 2))


def main_menu():
    global username, password, active_field, logged_in, error_msg, error_color

    clock = pygame.time.Clock()

    while True:
        screen.fill(BLACK)
        mx, my = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if not logged_in:
                # --- OVLÁDÁNÍ PŘIHLÁŠENÍ ---
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_TAB:
                        active_field = "pass" if active_field == "user" else "user"
                    elif event.key == pygame.K_BACKSPACE:
                        if active_field == "user":
                            username = username[:-1]
                        else:
                            password = password[:-1]
                    elif event.key == pygame.K_RETURN:
                        # Pokus o přihlášení
                        res = verify_login(username, password)
                        if res == "SUCCESS":
                            logged_in = True
                            error_msg = "Přihlášení úspěšné!"
                            error_color = GREEN
                        elif res == "WRONG_CREDENTIALS":
                            error_msg = "Chybné jméno nebo heslo!"
                            error_color = RED
                        elif res == "OFFLINE":
                            error_msg = "CHYBA: Server neběží (XAMPP vypnut?)"
                            error_color = RED
                        elif res == "EMPTY":
                            error_msg = "Vyplň všechna pole!"
                            error_color = RED
                        else:
                            error_msg = f"DEBUG: {res}"
                            error_color = RED
                    else:
                        # Psaní (omezeno na 15 znaků)
                        if len(username if active_field == "user" else password) < 15:
                            if event.unicode.isprintable():
                                if active_field == "user":
                                    username += event.unicode
                                else:
                                    password += event.unicode
            else:
                # --- OVLÁDÁNÍ MENU PO PŘIHLÁŠENÍ ---
                if event.type == pygame.MOUSEBUTTONDOWN:
                    # Tlačítko HRÁT
                    if 300 <= mx <= 500 and 250 <= my <= 310:
                        pygame.quit()
                        # Spustíme hru a pošleme jméno jako parametr
                        subprocess.run(["python", "main.py", username])
                        sys.exit()
                    # Tlačítko KONEC
                    if 300 <= mx <= 500 and 350 <= my <= 410:
                        pygame.quit()
                        sys.exit()

        # --- VYKRESLOVÁNÍ ---
        if not logged_in:
            # Nadpis
            img_title = font_title.render("SPACE INVADERS", True, CYAN)
            screen.blit(img_title, (WIDTH // 2 - img_title.get_width() // 2, 80))

            # Instrukce
            instr = font_small.render("TAB pro přepnutí, ENTER pro vstup", True, LIGHT_GRAY)
            screen.blit(instr, (WIDTH // 2 - instr.get_width() // 2, 140))

            # Pole pro jméno
            u_col = CYAN if active_field == "user" else GRAY
            pygame.draw.rect(screen, u_col, (250, 200, 300, 45), 2, border_radius=5)
            u_label = font_text.render(f"Jméno: {username}", True, WHITE)
            screen.blit(u_label, (260, 208))

            # Pole pro heslo
            p_col = CYAN if active_field == "pass" else GRAY
            pygame.draw.rect(screen, p_col, (250, 280, 300, 45), 2, border_radius=5)
            stars = "*" * len(password)
            p_label = font_text.render(f"Heslo: {stars}", True, WHITE)
            screen.blit(p_label, (260, 288))

            # Chybová hláška (DEBUG)
            if error_msg:
                err_img = font_small.render(error_msg, True, error_color)
                screen.blit(err_img, (WIDTH // 2 - err_img.get_width() // 2, 350))
        else:
            # Menu po přihlášení
            welcome = font_title.render(f"VÍTEJ, {username.upper()}!", True, GREEN)
            screen.blit(welcome, (WIDTH // 2 - welcome.get_width() // 2, 100))

            btn_play_col = RED if 300 <= mx <= 500 and 250 <= my <= 310 else GRAY
            draw_button("HRÁT", 300, 250, 200, 60, btn_play_col)

            btn_exit_col = RED if 300 <= mx <= 500 and 350 <= my <= 410 else GRAY
            draw_button("KONEC", 300, 350, 200, 60, btn_exit_col)

        pygame.display.flip()
        clock.tick(30)


if __name__ == "__main__":
    main_menu()