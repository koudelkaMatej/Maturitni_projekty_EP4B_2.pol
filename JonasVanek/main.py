import pygame
import random
import sys
import json
import urllib.request
import urllib.error
import urllib.parse
from pathlib import Path

# ============================================================================
# KONFIGURACE PŘIPOJENÍ K DATABÁZI/SERVERU
# ============================================================================
# Nastavení pro lokální XAMPP server
SCORE_SERVER_URL = "http://localhost/flappy_palach/submit_score.php"
LOGIN_URL = "http://localhost/flappy_palach/login.php"
REGISTER_URL = "http://localhost/flappy_palach/register.php"

# Globální proměnné pro přihlášeného uživatele
current_user_id = None
current_username = None

# ============================================================================
# INICIALIZACE PYGAME A ZÁKLADNÍ KONSTANTY
# ============================================================================

pygame.init()  # Spustí všechny pygame moduly
WIDTH, HEIGHT = 600, 800  # Rozměry herního okna
WIN = pygame.display.set_mode((WIDTH, HEIGHT))  # Vytvoří okno
pygame.display.set_caption("Flappy Palach")  # Nadpis okna

# Barvy (RGB formát)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Fonty pro vykreslování textu
FONT = pygame.font.SysFont("Arial", 40)
SMALL_FONT = pygame.font.SysFont("Arial", 28)

# ============================================================================
# FYZIKÁLNÍ KONSTANTY HRY
# ============================================================================
gravity = 0.5  # Gravitace - přidává se každý snímek k rychlosti ptáčka
jump_strength = -10  # Síla skoku (záporná = nahoru)
clock = pygame.time.Clock()  # Hodiny pro řízení FPS

# ============================================================================
# NAČÍTÁNÍ OBRÁZKŮ
# ============================================================================

# Najdeme složku s obrázky relativně k tomuto souboru
BASE_DIR = Path(__file__).resolve().parent
IMG_DIR = BASE_DIR / "img"


def load_image_safe(path: Path, convert_alpha=True):
    """
    Bezpečně načte obrázek - pokud selže, vrátí fallback surface.
    convert_alpha=True zachovává průhlednost obrázku.
    """
    try:
        if convert_alpha:
            return pygame.image.load(str(path)).convert_alpha()
        else:
            return pygame.image.load(str(path)).convert()
    except Exception:
        # Fallback: malý červený čtverec s okrajem
        surf = pygame.Surface((50, 50), pygame.SRCALPHA)
        pygame.draw.rect(surf, (255, 0, 0), surf.get_rect(), width=2)
        return surf


# --- NAČTENÍ POZADÍ ---
bg_path = IMG_DIR / "pozadi.png"
try:
    bg_img = pygame.image.load(str(bg_path)).convert()
    bg_img = pygame.transform.scale(bg_img, (WIDTH, HEIGHT))
except Exception:
    # Fallback pozadí: světle modrá barva
    bg_img = pygame.Surface((WIDTH, HEIGHT))
    bg_img.fill((180, 220, 255))

# --- NAČTENÍ ANIMACE PTÁČKA (3 snímky pro mávání křídly) ---
bird_frame_files = [IMG_DIR / "bird1.png", IMG_DIR / "bird2.png", IMG_DIR / "bird3.png"]
bird_frames = []  # Seznam surface objektů pro animaci
BIRD_SIZE = (50, 50)  # Velikost ptáčka

for fname in bird_frame_files:
    try:
        img = pygame.image.load(str(fname)).convert_alpha()
        img = pygame.transform.smoothscale(img, BIRD_SIZE)
    except Exception:
        # Fallback: žlutý ovál s černým okem
        img = pygame.Surface(BIRD_SIZE, pygame.SRCALPHA)
        pygame.draw.ellipse(img, (255, 200, 0), img.get_rect())
        pygame.draw.circle(img, (0, 0, 0), (int(BIRD_SIZE[0] * 0.65), int(BIRD_SIZE[1] * 0.35)), 3)
    bird_frames.append(img)

# Index neutrálního snímku (ptáček bez mávání)
NEUTRAL_FRAME_IDX = 1 if len(bird_frames) > 1 else 0

# Proměnné pro animaci mávání křídly
bird_frame_index = NEUTRAL_FRAME_IDX
FLAP_DURATION_MS = 240  # Celková délka animace mávnutí (ms)
FLAP_FRAME_INTERVAL_MS = 80  # Čas mezi snímky animace (ms)
flap_timer = 0  # Časovač pro celkovou dobu mávnutí
flap_frame_timer = 0  # Časovač pro přepínání snímků
flap_active = False  # Je animace mávání aktivní?

# --- NAČTENÍ OBRÁZKU TRUBKY ---
pipe_path = IMG_DIR / "palachvez.png"
try:
    pipe_img = pygame.image.load(str(pipe_path)).convert_alpha()
    PIPE_WIDTH = 80
    pipe_img = pygame.transform.smoothscale(pipe_img, (PIPE_WIDTH, pipe_img.get_height()))
except Exception:
    # Fallback: zelený obdélník
    PIPE_WIDTH = 80
    pipe_img = pygame.Surface((PIPE_WIDTH, 200), pygame.SRCALPHA)
    pygame.draw.rect(pipe_img, (60, 180, 60), pipe_img.get_rect())

# Otočená trubka pro horní překážku
pipe_img_flipped = pygame.transform.flip(pipe_img, False, True)

# --- NAČTENÍ GAME OVER OBRÁZKU ---
gameover_path = IMG_DIR / "gameover.png"
try:
    gameover_img = pygame.image.load(str(gameover_path)).convert_alpha()
    gameover_img = pygame.transform.smoothscale(gameover_img, (min(500, WIDTH - 40), 140))
except Exception:
    gameover_img = FONT.render("Game Over!", True, BLACK)

# --- NAČTENÍ ČÍSLIC 0-9 PRO ZOBRAZENÍ SKÓRE ---
digit_images = {}  # Slovník {znak: surface}
DIGIT_BASE_HEIGHT = 80  # Základní výška číslic

for d in range(0, 10):
    fname = IMG_DIR / f"{d}.png"
    key = str(d)
    try:
        img = pygame.image.load(str(fname)).convert_alpha()
        # Přeškálování zachovává poměr stran
        iw, ih = img.get_size()
        scale = DIGIT_BASE_HEIGHT / ih if ih != 0 else 1
        img = pygame.transform.smoothscale(img, (max(1, int(iw * scale)), DIGIT_BASE_HEIGHT))
        digit_images[key] = img
    except Exception:
        # Fallback: vyrenderovaný text
        surf = FONT.render(key, True, BLACK)
        if surf.get_height() < DIGIT_BASE_HEIGHT:
            bg = pygame.Surface((surf.get_width() + 20, DIGIT_BASE_HEIGHT), pygame.SRCALPHA)
            bg.fill((255, 255, 255, 0))
            bg.blit(surf, (10, (DIGIT_BASE_HEIGHT - surf.get_height()) // 2))
            digit_images[key] = bg
        else:
            digit_images[key] = surf

# ============================================================================
# PROFILY OBTÍŽNOSTI
# ============================================================================
# Každý profil definuje, jak se mění rychlost a mezera mezi trubkami
DIFFICULTY_PROFILES = {
    "lehka": {
        "label": "Lehká",
        "speed_inc": 0.0,  # O kolik se zvyšuje rychlost po každých X bodech
        "gap_dec": 0,  # O kolik pixelů se zmenšuje mezera mezi trubkami
        "score_step": 3  # Po kolika bodech se mění obtížnost
    },
    "stredni": {
        "label": "Střední",
        "speed_inc": 0.25,
        "gap_dec": 3,
        "score_step": 3
    },
    "tezka": {
        "label": "Těžká",
        "speed_inc": 0.5,
        "gap_dec": 6,
        "score_step": 3
    }
}


# ============================================================================
# POMOCNÉ FUNKCE
# ============================================================================

def wait_for_mouse_release():
    """
    Počká, dokud hráč neuvolní tlačítko myši.
    Zabraňuje náhodným kliknutím při přechodu mezi obrazovkami.
    """
    pygame.event.clear()
    while any(pygame.mouse.get_pressed()):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit();
                sys.exit()
        clock.tick(60)


def _draw_vertical_gradient(surf, rect, top_color, bottom_color, radius):
    """
    Vykreslí vertikální gradient s kulatými rohy.
    Používá se pro tlačítka.
    """
    x, y, w, h = rect
    gradient = pygame.Surface((w, h), pygame.SRCALPHA)
    # Projdeme každou řádku a interpolujeme barvu
    for i in range(h):
        t = i / max(1, h - 1)  # Procento (0.0 - 1.0)
        r = int(top_color[0] + (bottom_color[0] - top_color[0]) * t)
        g = int(top_color[1] + (bottom_color[1] - top_color[1]) * t)
        b = int(top_color[2] + (bottom_color[2] - top_color[2]) * t)
        a = int(top_color[3] + (bottom_color[3] - top_color[3]) * t)
        pygame.draw.line(gradient, (r, g, b, a), (0, i), (w, i))
    # Aplikujeme masku pro kulaté rohy
    mask = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255), (0, 0, w, h), border_radius=radius)
    gradient.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(gradient, (x, y))


def _render_text_fit(text, max_w, max_h, base_size=28, min_size=14):
    """
    Vyrenderuje text tak, aby se vešel do dané oblasti.
    Postupně zmenšuje font, dokud se text nevejde.
    """
    size = base_size
    while size >= min_size:
        font = pygame.font.SysFont("Arial", size)
        ts = font.render(text, True, BLACK)
        tw, th = ts.get_size()
        if tw <= max_w and th <= max_h:
            return ts, font
        size -= 1
    # Pokud se text ani s nejmenším fontem nevejde, ořežeme ho
    font = pygame.font.SysFont("Arial", min_size)
    text_trim = text
    ts = font.render(text_trim, True, BLACK)
    while ts.get_width() > max_w and len(text_trim) > 3:
        text_trim = text_trim[:-1]
        ts = font.render(text_trim + "...", True, BLACK)
    return ts, font


def draw_button(text, center_x, y, w, h, alpha=255):
    """
    Vykreslí interaktivní tlačítko s gradientem.

    Parametry:
    - text: Text na tlačítku
    - center_x: Horizontální střed tlačítka
    - y: Vertikální pozice (horní hrana)
    - w, h: Šířka a výška
    - alpha: Průhlednost (0-255)

    Vrací: True pokud je na tlačítko kliknuto
    """
    padding_x, padding_y = 20, 12
    min_w, min_h = 160, 56
    w_eff = max(w, min_w)
    h_eff = max(h, min_h)
    max_button_w = min(WIDTH - 40, 460)

    # Zjistíme, jestli je myš nad tlačítkem
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()
    rect = pygame.Rect(center_x - w_eff // 2, y, w_eff, h_eff)
    hovered = rect.collidepoint(mouse)

    # Barvy se mění podle toho, jestli je tlačítko "hovered"
    if hovered:
        top = (40, 120, 255, alpha)
        bottom = (250, 210, 60, alpha)
        border = (20, 60, 140)
        shadow_alpha = 110
    else:
        top = (70, 160, 255, alpha)
        bottom = (255, 225, 90, alpha)
        border = (30, 80, 160)
        shadow_alpha = 90

    radius = 16

    # Vykreslíme text a případně upravíme velikost tlačítka
    max_text_w = w_eff - 2 * padding_x
    max_text_h = h_eff - 2 * padding_y
    ts, _ = _render_text_fit(text, max_text_w, max_text_h, base_size=28, min_size=14)
    tw, th = ts.get_size()

    if tw > max_text_w or th > max_text_h:
        w_eff = min(max_button_w, max(w_eff, tw + 2 * padding_x))
        h_eff = max(h_eff, th + 2 * padding_y)
        rect = pygame.Rect(center_x - w_eff // 2, y, w_eff, h_eff)
        max_text_w = w_eff - 2 * padding_x
        max_text_h = h_eff - 2 * padding_y
        ts, _ = _render_text_fit(text, max_text_w, max_text_h, base_size=28, min_size=14)
        tw, th = ts.get_size()

    # Vykreslíme stín tlačítka
    shadow = pygame.Surface((w_eff + 8, h_eff + 8), pygame.SRCALPHA)
    pygame.draw.rect(shadow, (0, 0, 0, shadow_alpha), shadow.get_rect(), border_radius=radius + 2)
    WIN.blit(shadow, (center_x - (w_eff // 2) + 2, y + 4))

    # Vykreslíme gradient tlačítka
    _draw_vertical_gradient(WIN, rect, top, bottom, radius)

    # Vykreslíme okraj tlačítka
    pygame.draw.rect(WIN, border, rect, width=3, border_radius=radius)

    # Vykreslíme text doprostřed
    WIN.blit(ts, (rect.centerx - tw // 2, rect.centery - th // 2))

    # Pokud je na tlačítko kliknuto, počkáme chvíli (efekt) a vrátíme True
    if hovered and click[0]:
        pygame.time.wait(180)
        return True
    return False


def draw_text_center(text, font, color, y_offset=0):
    """Vykreslí text na střed obrazovky s volitelným vertikálním posunem."""
    text_surface = font.render(text, True, color)
    rect = text_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2 + y_offset))
    WIN.blit(text_surface, rect)


def sanitize_name(s: str) -> str:
    """
    Vyčistí jméno hráče - odstraní neprintovatelné znaky a whitespace.
    """
    s = s.strip()
    s = "".join(ch for ch in s if ch.isprintable() and ch not in "\n\r\t")
    return s


# ============================================================================
# FUNKCE PRO PŘIHLÁŠENÍ A REGISTRACI
# ============================================================================

def login_user(username, password):
    """
    Přihlásí uživatele na server.

    Vrací: (success: bool, user_id: int, message: str)
    """
    try:
        data = urllib.parse.urlencode({
            "username": username,
            "password": password
        }).encode("utf-8")

        req = urllib.request.Request(
            url=LOGIN_URL,
            data=data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            method="POST"
        )

        with urllib.request.urlopen(req, timeout=10) as resp:
            response = json.loads(resp.read().decode('utf-8'))

            if response.get('success'):
                user_data = response.get('data', {})
                return True, user_data.get('user_id'), response.get('message', 'Přihlášení úspěšné')
            else:
                return False, None, response.get('message', 'Přihlášení selhalo')

    except Exception as e:
        return False, None, f"Chyba připojení: {str(e)}"


def register_user(username, password):
    """
    Zaregistruje nového uživatele na serveru.

    Vrací: (success: bool, user_id: int, message: str)
    """
    try:
        data = urllib.parse.urlencode({
            "username": username,
            "password": password
        }).encode("utf-8")

        req = urllib.request.Request(
            url=REGISTER_URL,
            data=data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            method="POST"
        )

        with urllib.request.urlopen(req, timeout=10) as resp:
            response = json.loads(resp.read().decode('utf-8'))

            if response.get('success'):
                user_data = response.get('data', {})
                return True, user_data.get('user_id'), response.get('message', 'Registrace úspěšná')
            else:
                return False, None, response.get('message', 'Registrace selhala')

    except Exception as e:
        return False, None, f"Chyba připojení: {str(e)}"


# ============================================================================
# OBRAZOVKY HRY
# ============================================================================

def draw_input_field(label_text, value, y_pos, active, cursor_show, is_password=False):
    """
    Vykreslí popis + input pole.
    Vrací: pygame.Rect input pole (pro detekci kliku)
    """
    # Popis pole
    label_surf = SMALL_FONT.render(label_text, True, BLACK)
    WIN.blit(label_surf, (WIDTH // 2 - 150, y_pos))

    # Zobrazitný text (heslo se maskuje hvězdičkami)
    display_text = ("*" * len(value)) if is_password else value
    if active and cursor_show:
        display_text += "|"
    if not display_text:
        display_text = " "

    # Obdélník pole – modrá pozadí pokud aktivní
    field_rect = pygame.Rect(WIDTH // 2 - 150, y_pos + 28, 300, 38)
    bg_color = (180, 210, 255) if active else (220, 220, 220)
    pygame.draw.rect(WIN, bg_color, field_rect, border_radius=8)
    pygame.draw.rect(WIN, (30, 80, 160) if active else BLACK, field_rect, width=2, border_radius=8)

    # Text do pole
    text_surf = SMALL_FONT.render(display_text, True, BLACK)
    WIN.blit(text_surf, (field_rect.x + 10, field_rect.y + 7))

    return field_rect


def login_register_screen():
    """
    Obrazovka pro přihlášení nebo registraci uživatele.
    Obsahuje dvě pole: jméno a heslo.
    Hráč může přepínat mezi módem přihlášení a registrace.

    Vrací: (user_id: int, username: str)
    """
    global current_user_id, current_username

    mode = "login"  # "login" nebo "register"
    username = ""
    password = ""
    active_field = "username"  # "username" nebo "password"
    cursor_show = True
    cursor_timer = 0
    message = ""  # zpráva (chyba / úspěch)
    message_color = (255, 0, 0)
    message_timer = 0

    wait_for_mouse_release()

    while True:
        dt = clock.tick(60)
        WIN.blit(bg_img, (0, 0))

        # ---- nadpis ----
        title = "Přihlášení" if mode == "login" else "Registrace"
        draw_text_center(title, FONT, BLACK, -220)

        # ---- blikající kurzor ----
        cursor_timer += dt
        if cursor_timer > 500:
            cursor_show = not cursor_show
            cursor_timer = 0

        # ---- zobrazení zprávy (chyba / úspěch) ----
        if message:
            message_timer += dt
            if message_timer > 3500:
                message = ""
                message_timer = 0
            msg_surf = SMALL_FONT.render(message, True, message_color)
            WIN.blit(msg_surf, (WIDTH // 2 - msg_surf.get_width() // 2, HEIGHT // 2 - 155))

        # ---- input pole: jméno ----
        username_rect = draw_input_field(
            "Jméno:", username,
            y_pos=HEIGHT // 2 - 110,
            active=(active_field == "username"),
            cursor_show=cursor_show,
            is_password=False
        )

        # ---- input pole: heslo ----
        password_rect = draw_input_field(
            "Heslo:", password,
            y_pos=HEIGHT // 2 - 15,
            active=(active_field == "password"),
            cursor_show=cursor_show,
            is_password=True
        )

        # ---- hlavní tlačítko (Přihlásit / Registrovat) ----
        btn_label = "Přihlásit se" if mode == "login" else "Registrovat"
        if draw_button(btn_label, WIDTH // 2, HEIGHT // 2 + 70, 240, 55):
            # validace na klientu
            if len(username) < 3:
                message = "Jméno musí mít alespoň 3 znaky"
                message_color = (255, 0, 0)
                message_timer = 0
            elif len(password) < 4:
                message = "Heslo musí mít alespoň 4 znaky"
                message_color = (255, 0, 0)
                message_timer = 0
            else:
                # odeslání na server
                if mode == "login":
                    success, uid, msg = login_user(username, password)
                else:
                    success, uid, msg = register_user(username, password)

                if success:
                    current_user_id = uid
                    current_username = username
                    wait_for_mouse_release()
                    return uid, username
                else:
                    message = msg
                    message_color = (255, 0, 0)
                    message_timer = 0

            wait_for_mouse_release()

        # ---- přepínací tlačítko (login <-> register) ----
        if mode == "login":
            switch_label = "Nemáte účet? Registrovat"
        else:
            switch_label = "Máte účet? Přihlásit se"

        if draw_button(switch_label, WIDTH // 2, HEIGHT // 2 + 145, 310, 50):
            mode = "register" if mode == "login" else "login"
            message = ""
            password = ""
            active_field = "username"
            wait_for_mouse_release()

        pygame.display.update()

        # ---- zpracování událostí ----
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit();
                sys.exit()

            # kliknutí na pole myšem
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if username_rect.collidepoint(event.pos):
                    active_field = "username"
                elif password_rect.collidepoint(event.pos):
                    active_field = "password"

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_TAB:
                    active_field = "password" if active_field == "username" else "username"

                elif event.key == pygame.K_RETURN:
                    if active_field == "username":
                        active_field = "password"

                elif event.key == pygame.K_BACKSPACE:
                    if active_field == "username":
                        username = username[:-1]
                    else:
                        password = password[:-1]

                else:
                    ch = event.unicode
                    if ch and ch.isprintable() and ch not in "\n\r\t":
                        if active_field == "username" and len(username) < 30:
                            username += ch
                        elif active_field == "password" and len(password) < 50:
                            password += ch


def difficulty_screen(current_key="stredni"):
    """
    Obrazovka pro výběr obtížnosti.

    Parametr:
    - current_key: Aktuálně vybraná obtížnost

    Vrací: Klíč vybrané obtížnosti ("lehka", "stredni", "tezka")
    """
    wait_for_mouse_release()
    keys = ["lehka", "stredni", "tezka"]
    current_idx = keys.index(current_key) if current_key in keys else 1

    while True:
        clock.tick(60)
        WIN.blit(bg_img, (0, 0))
        draw_text_center("Vyber obtížnost", FONT, BLACK, -160)

        # Vykreslíme tlačítka pro každou obtížnost
        y0 = HEIGHT // 2 - 40
        h = 60
        w = 280
        labels = [DIFFICULTY_PROFILES[k]["label"] for k in keys]

        for i, label in enumerate(labels):
            y = y0 + i * 80
            if draw_button(label, WIDTH // 2, y, w, h):
                wait_for_mouse_release()
                return keys[i]

        # Tlačítko Zpět
        if draw_button("Zpět", WIDTH // 2, HEIGHT // 2 + 210, 200, 60):
            wait_for_mouse_release()
            return keys[current_idx]

        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit();
                sys.exit()


def menu_screen(show_change_name=True, show_change_difficulty=True, difficulty_key="stredni"):
    """
    Hlavní menu hry.

    Parametry:
    - show_change_name: Zobrazit tlačítko pro změnu jména
    - show_change_difficulty: Zobrazit tlačítko pro změnu obtížnosti
    - difficulty_key: Aktuální obtížnost

    Vrací: String určující akci ("start", "change_name", "change_difficulty")
    """
    alpha = 0  # Pro fade-in efekt
    wait_for_mouse_release()

    while True:
        clock.tick(60)
        WIN.blit(bg_img, (0, 0))
        draw_text_center("Flappy Palach", FONT, BLACK, -200)

        # Zobrazení aktuální obtížnosti
        diff_label = DIFFICULTY_PROFILES.get(difficulty_key, DIFFICULTY_PROFILES["stredni"])["label"]
        info = SMALL_FONT.render(f"Aktuální obtížnost: {diff_label}", True, BLACK)
        WIN.blit(info, (WIDTH // 2 - info.get_width() // 2, HEIGHT // 2 - 90))

        # Fade-in efekt
        if alpha < 255:
            alpha += 5

        # Tlačítko Start
        if draw_button("Start", WIDTH // 2, HEIGHT // 2 - 30, 220, 60, alpha):
            wait_for_mouse_release()
            return "start"

        # Další tlačítka (dynamicky podle parametrů)
        y = HEIGHT // 2 + 60
        if show_change_name:
            if draw_button("Změnit jméno", WIDTH // 2, y, 260, 60, alpha):
                wait_for_mouse_release()
                return "change_name"
            y += 90

        if show_change_difficulty:
            if draw_button("Změnit obtížnost", WIDTH // 2, y, 280, 60, alpha):
                wait_for_mouse_release()
                return "change_difficulty"
            y += 90

        # Tlačítko Ukončit
        if draw_button("Ukončit", WIDTH // 2, y, 220, 60, alpha):
            pygame.quit();
            sys.exit()

        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit();
                sys.exit()


def pause_menu():
    """
    Pauza hra - zobrazí se po stisknutí ESC během hry.
    """
    wait_for_mouse_release()
    while True:
        clock.tick(60)
        WIN.blit(bg_img, (0, 0))
        draw_text_center("PAUZA", FONT, BLACK, -150)

        if draw_button("Pokračovat", WIDTH // 2, HEIGHT // 2 - 30, 240, 60):
            wait_for_mouse_release()
            return

        if draw_button("Ukončit", WIDTH // 2, HEIGHT // 2 + 60, 220, 60):
            pygame.quit();
            sys.exit()

        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit();
                sys.exit()


def submit_score(player_name, score, difficulty_key):
    """
    Odešle skóre hráče na lokální XAMPP server.
    Pokud selže, nic se nestane - hra pokračuje.
    Posílá: user_id, username, score, difficulty
    Server ukládá jen nejlepší skóre na dané obtížnosti.
    """
    if SCORE_SERVER_URL is None or current_user_id is None:
        print("✗ Skóre neodesláno – nejsi přihlášen nebo chyba URL.")
        return

    try:
        # Připravíme data k odeslání
        data = urllib.parse.urlencode({
            "user_id": current_user_id,
            "username": player_name,
            "score": int(score),
            "difficulty": difficulty_key  # "lehka", "stredni", "tezka"
        }).encode("utf-8")

        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": "FlappyPalach/1.0"
        }

        req = urllib.request.Request(
            url=SCORE_SERVER_URL,
            data=data,
            headers=headers,
            method="POST"
        )

        with urllib.request.urlopen(req, timeout=10) as resp:
            response = json.loads(resp.read().decode('utf-8'))
            if response.get('success'):
                print(f"✓ {response.get('message')}")
            else:
                print(f"✗ {response.get('message')}")

    except Exception as e:
        print(f"✗ Odeslání skóre selhalo: {e}")
        print("  Zkontrolujte, že XAMPP Apache a MySQL běží.")


def dead_screen(score, player_name, difficulty_key):
    """
    Obrazovka "Game Over" - zobrazí se po smrti hráče.
    Zobrazuje skóre pomocí obrázků číslic a nabízí možnosti:
    - Hrát znovu
    - Zpět do menu
    - Ukončit

    Vrací: "restart" nebo "menu"
    """
    submit_score(player_name, score, difficulty_key)  # Odešle skóre s obtížností
    wait_for_mouse_release()

    while True:
        clock.tick(60)
        WIN.blit(bg_img, (0, 0))

        # Vykreslení Game Over obrázku
        if isinstance(gameover_img, pygame.Surface):
            go_rect = gameover_img.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 140))
            WIN.blit(gameover_img, go_rect)
        else:
            draw_text_center("Game Over!", FONT, BLACK, -170)

        # Vykreslení skóre pomocí obrázků číslic
        score_str = str(int(score))
        digit_surfaces = []
        total_w = 0
        max_h = 0

        # Připravíme všechny cifry
        for ch in score_str:
            surf = digit_images.get(ch)
            if surf is None:
                surf = FONT.render(ch, True, BLACK)
            digit_surfaces.append(surf)
            total_w += surf.get_width()
            if surf.get_height() > max_h:
                max_h = surf.get_height()

        # Mezera mezi ciframi
        spacing = 8
        total_w += spacing * (len(digit_surfaces) - 1) if len(digit_surfaces) > 1 else 0

        # Vykreslíme cifry na střed
        start_x = WIDTH // 2 - total_w // 2
        y_pos = HEIGHT // 2 - 40

        x = start_x
        for surf in digit_surfaces:
            y_off = y_pos + (max_h - surf.get_height()) // 2
            WIN.blit(surf, (x, y_off))
            x += surf.get_width() + spacing

        # Tlačítka
        if draw_button("Hrát znovu", WIDTH // 2, HEIGHT // 2 + 60, 240, 60):
            wait_for_mouse_release()
            return "restart"

        if draw_button("Zpět do menu", WIDTH // 2, HEIGHT // 2 + 140, 260, 60):
            wait_for_mouse_release()
            return "menu"

        if draw_button("Ukončit", WIDTH // 2, HEIGHT // 2 + 220, 220, 60):
            pygame.quit();
            sys.exit()

        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit();
                sys.exit()


def render_score_with_images(score, top_left_x, top_left_y, target_height=40, spacing=6):
    """
    Vykreslí skóre pomocí obrázků číslic v HUD.

    Parametry:
    - score: Číslo k vykreslení
    - top_left_x, top_left_y: Pozice levého horního rohu
    - target_height: Požadovaná výška číslic
    - spacing: Mezera mezi ciframi
    """
    score_str = str(int(score))
    surfaces = []
    total_w = 0
    max_h = 0

    # Přeškálujeme všechny cifry na požadovanou výšku
    for ch in score_str:
        base = digit_images.get(ch)
        if base is None:
            base = FONT.render(ch, True, BLACK)

        # Zachováme poměr stran
        bw, bh = base.get_size()
        scale = target_height / bh if bh != 0 else 1
        new_w = max(1, int(bw * scale))
        surf = pygame.transform.smoothscale(base, (new_w, target_height))

        surfaces.append(surf)
        total_w += surf.get_width()
        if surf.get_height() > max_h:
            max_h = surf.get_height()

    total_w += spacing * (len(surfaces) - 1) if len(surfaces) > 1 else 0

    # Vykreslení
    x = top_left_x
    for surf in surfaces:
        WIN.blit(surf, (x, top_left_y + (max_h - surf.get_height()) // 2))
        x += surf.get_width() + spacing


def check_collision(bird_rect, pipe_x, pipe_height, gap):
    """
    Kontroluje kolizi ptáčka s překážkami nebo okrajem obrazovky.

    Parametry:
    - bird_rect: Obdélník ptáčka (pygame.Rect)
    - pipe_x: X pozice trubky
    - pipe_height: Výška horní trubky
    - gap: Velikost mezery mezi trubkami

    Vrací: True pokud došlo ke kolizi, jinak False
    """
    # Horní trubka
    top_rect = pygame.Rect(pipe_x, 0, PIPE_WIDTH, pipe_height)
    # Spodní trubka
    bottom_rect = pygame.Rect(pipe_x, pipe_height + gap, PIPE_WIDTH, HEIGHT)

    # Kontrola kolize s trubkami
    if bird_rect.colliderect(top_rect) or bird_rect.colliderect(bottom_rect):
        return True

    # Kontrola kolize s okrajem obrazovky
    if bird_rect.top < 0 or bird_rect.bottom > HEIGHT:
        return True

    return False


def draw_game(bird_image_rotated, bird_rect, pipe_x, pipe_height, score, player_name, gap, pipe_speed, difficulty_key):
    """
    Vykreslí celou herní scénu.

    Zahrnuje:
    - Pozadí
    - Rotovaného ptáčka
    - Trubky (horní a spodní)
    - HUD (skóre, jméno, obtížnost, rychlost, mezeru)
    """
    WIN.blit(bg_img, (0, 0))

    # Vykreslení rotovaného ptáčka
    WIN.blit(bird_image_rotated, bird_rect)

    # Přeškálování trubek podle výšky
    try:
        top_pipe = pygame.transform.smoothscale(pipe_img_flipped, (PIPE_WIDTH, max(1, pipe_height)))
        bottom_height = max(1, HEIGHT - pipe_height - gap)
        bottom_pipe = pygame.transform.smoothscale(pipe_img, (PIPE_WIDTH, bottom_height))
    except Exception:
        # Fallback
        top_pipe = pygame.Surface((PIPE_WIDTH, max(1, pipe_height)))
        top_pipe.fill((60, 180, 60))
        bottom_height = max(1, HEIGHT - pipe_height - gap)
        bottom_pipe = pygame.Surface((PIPE_WIDTH, bottom_height))
        bottom_pipe.fill((60, 180, 60))

    # Vykreslení trubek
    WIN.blit(top_pipe, (pipe_x, 0))
    WIN.blit(bottom_pipe, (pipe_x, pipe_height + gap))

    # HUD - skóre pomocí obrázků číslic
    HUD_X = 10
    HUD_Y = 10
    HUD_DIGIT_HEIGHT = 36
    render_score_with_images(score, HUD_X, HUD_Y, target_height=HUD_DIGIT_HEIGHT, spacing=6)

    # Jméno hráče
    name_s = SMALL_FONT.render(f"Hráč: {player_name}", True, BLACK)
    WIN.blit(name_s, (10, 60))

    # Obtížnost
    diff_label = DIFFICULTY_PROFILES.get(difficulty_key, DIFFICULTY_PROFILES["stredni"])["label"]
    diff = SMALL_FONT.render(f"Obtížnost: {diff_label}", True, BLACK)
    WIN.blit(diff, (10, 100))

    # Rychlost a mezera
    speed_gap = SMALL_FONT.render(f"Rychlost: {pipe_speed:.1f}   Mezera: {gap}px", True, BLACK)
    WIN.blit(speed_gap, (10, 140))

    pygame.display.update()


# ============================================================================
# HLAVNÍ HERNÍ SMYČKA
# ============================================================================

def main_game(player_name, difficulty_key):
    """
    Hlavní herní smyčka - zde probíhá vlastní hra.

    Parametry:
    - player_name: Jméno hráče
    - difficulty_key: Klíč obtížnosti

    Vrací: "restart" (hrát znovu) nebo "menu" (návrat do menu)
    """
    global flap_active, flap_timer, flap_frame_timer, bird_frame_index

    # Inicializace ptáčka
    bird_y = HEIGHT // 2  # Pozice Y
    bird_velocity = 0  # Rychlost padání

    # Inicializace první trubky
    pipe_x = WIDTH
    pipe_height = random.randint(100, 500)

    # Herní parametry
    pipe_speed = 4.0  # Rychlost pohybu trubek
    GAP = 180  # Mezera mezi trubkami
    MIN_GAP = 120  # Minimální mezera

    # Načtení profilu obtížnosti
    profile = DIFFICULTY_PROFILES.get(difficulty_key, DIFFICULTY_PROFILES["stredni"])
    SCORE_STEP = profile["score_step"]  # Po kolika bodech se mění obtížnost
    SPEED_INC = profile["speed_inc"]  # Přírůstek rychlosti
    GAP_DEC = profile["gap_dec"]  # Úbytek mezery

    score = 0  # Skóre hráče

    # Parametry rotace ptáčka
    ROTATION_FACTOR = 3.0  # Kolik stupňů na jednotku rychlosti
    MAX_UP_ANGLE = -40  # Maximální úhel nahoru
    MAX_DOWN_ANGLE = 60  # Maximální úhel dolů

    # Reset animace mávání
    bird_frame_index = NEUTRAL_FRAME_IDX
    flap_active = False
    flap_timer = 0
    flap_frame_timer = 0

    while True:
        dt = clock.tick(60)  # 60 FPS, dt = čas od posledního snímku

        # ========== FYZIKA ==========
        bird_velocity += gravity  # Gravitace přidává rychlost
        bird_y += bird_velocity  # Rychlost posunuje ptáčka

        # ========== POHYB TRUBEK ==========
        pipe_x -= pipe_speed  # Trubky se pohybují doleva

        # Když trubka zmizí z obrazovky, vytvoříme novou
        if pipe_x + PIPE_WIDTH < 0:
            pipe_x = WIDTH
            pipe_height = random.randint(100, 500)
            score += 1  # Přidáme bod

            # Každých SCORE_STEP bodů zvýšíme obtížnost
            if SCORE_STEP > 0 and (score % SCORE_STEP == 0):
                pipe_speed += SPEED_INC  # Zvýšíme rychlost
                GAP = max(MIN_GAP, GAP - GAP_DEC)  # Zmenšíme mezeru

        # ========== ANIMACE MÁVÁNÍ ==========
        if flap_active:
            flap_timer += dt
            flap_frame_timer += dt

            # Přepnutí snímku animace
            if flap_frame_timer >= FLAP_FRAME_INTERVAL_MS:
                flap_frame_timer = 0
                bird_frame_index = (bird_frame_index + 1) % len(bird_frames)

            # Konec animace
            if flap_timer >= FLAP_DURATION_MS:
                flap_active = False
                flap_timer = 0
                flap_frame_timer = 0
                bird_frame_index = NEUTRAL_FRAME_IDX
        else:
            bird_frame_index = NEUTRAL_FRAME_IDX

        # ========== ROTACE PTÁČKA ==========
        # Vybereme aktuální snímek
        current_bird_img = bird_frames[bird_frame_index]

        # Spočítáme úhel podle rychlosti
        # Záporná rychlost (letí nahoru) = záporný úhel
        # Kladná rychlost (padá) = kladný úhel
        angle = -bird_velocity * ROTATION_FACTOR
        if angle < MAX_UP_ANGLE:
            angle = MAX_UP_ANGLE
        if angle > MAX_DOWN_ANGLE:
            angle = MAX_DOWN_ANGLE

        # Rotujeme obrázek
        bird_image_rotated = pygame.transform.rotate(current_bird_img, angle)
        bird_rect = bird_image_rotated.get_rect(center=(150, int(bird_y)))

        # ========== ZPRACOVÁNÍ UDÁLOSTÍ ==========
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit();
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    # Mezerník = skok
                    bird_velocity = jump_strength
                    # Spustíme animaci mávání
                    flap_active = True
                    flap_timer = 0
                    flap_frame_timer = 0
                    bird_frame_index = 0

                elif event.key == pygame.K_ESCAPE:
                    # ESC = pauza
                    pause_menu()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Levé tlačítko myši
                    # Kliknutí = skok
                    bird_velocity = jump_strength
                    flap_active = True
                    flap_timer = 0
                    flap_frame_timer = 0
                    bird_frame_index = 0

        # ========== KONTROLA KOLIZE ==========
        if check_collision(bird_rect, pipe_x, pipe_height, GAP):
            # Hráč zemřel - zobrazíme Game Over obrazovku
            choice = dead_screen(score, player_name, difficulty_key)
            if choice == "restart":
                return "restart"  # Hráč chce hrát znovu
            else:
                return "menu"  # Hráč chce zpět do menu

        # ========== VYKRESLENÍ ==========
        draw_game(bird_image_rotated, bird_rect, pipe_x, pipe_height, score, player_name, GAP, pipe_speed,
                  difficulty_key)


# ============================================================================
# HLAVNÍ FUNKCE - VSTUPNÍ BOD PROGRAMU
# ============================================================================

def main():
    """
    Hlavní funkce programu - řídí tok mezi jednotlivými obrazovkami.
    """
    global current_user_id, current_username

    # Přihlášení / registrace (místo старého name_input_screen)
    user_id, player_name = login_register_screen()
    current_user_id = user_id
    current_username = player_name

    # Pak vybereme obtížnost
    difficulty_key = difficulty_screen(current_key="stredni")

    # Hlavní smyčka programu
    while True:
        # Zobrazíme menu – "Změnit jméno" je vypnuté, protože máme login
        action = menu_screen(show_change_name=False, show_change_difficulty=True, difficulty_key=difficulty_key)

        if action == "start":
            # Hráč zmáčkl Start - spustíme hru
            while True:
                result = main_game(player_name, difficulty_key)
                if result == "restart":
                    # Hráč chce hrát znovu - spustíme novou hru
                    wait_for_mouse_release()
                    continue
                else:
                    # Hráč chce zpět do menu
                    wait_for_mouse_release()
                    break

        elif action == "change_difficulty":
            # Hráč chce změnit obtížnost
            difficulty_key = difficulty_screen(current_key=difficulty_key)

        else:
            # Jiná akce = konec programu
            pygame.quit();
            sys.exit()


# ============================================================================
# SPUŠTĚNÍ PROGRAMU
# ============================================================================
if __name__ == "__main__":
    main()