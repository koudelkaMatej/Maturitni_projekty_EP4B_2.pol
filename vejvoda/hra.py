import pygame
import sys
import random
import json
import os
import math
import http.client
import threading

# --- KONFIGURACE ---
DB_FILE     = 'highscores.json'
LOGIN_FILE  = 'prihlaseni.json'
SERVER_HOST = '127.0.0.1'   # explicitně IPv4, ne "localhost"
SERVER_PORT = 5000

WIDTH, HEIGHT = 480, 700

OBTIZNOSTI = {
    "easy":   {"gravity": 0.3,  "flap": -7, "pipe_speed": 2.5, "pipe_gap": 180, "label": "EASY",   "color": (80, 200, 120)},
    "normal": {"gravity": 0.45, "flap": -8, "pipe_speed": 3.5, "pipe_gap": 150, "label": "NORMAL", "color": (240, 200, 60)},
    "hard":   {"gravity": 0.6,  "flap": -9, "pipe_speed": 5.0, "pipe_gap": 120, "label": "HARD",   "color": (230, 60, 60)},
}

# ── Lokální DB (fallback) ─────────────────────────────────────────────────

def inicializuj_db():
    if not os.path.exists(DB_FILE):
        with open(DB_FILE, 'w', encoding='utf-8') as f:
            json.dump([], f)

def nacti_skore_local():
    try:
        with open(DB_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return []

def nacti_uzivatele_local():
    try:
        with open(LOGIN_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return []

# ── HTTP helpers ──────────────────────────────────────────────────────────

def api_post(endpoint, payload):
    """POST JSON na server přes http.client (IPv4, žádné proxy)."""
    try:
        body = json.dumps(payload, ensure_ascii=False).encode('utf-8')
        conn = http.client.HTTPConnection(SERVER_HOST, SERVER_PORT, timeout=3)
        conn.request('POST', endpoint, body=body,
                     headers={'Content-Type': 'application/json'})
        resp = conn.getresponse()
        data = json.loads(resp.read().decode('utf-8'))
        conn.close()
        return data
    except Exception as e:
        print(f'[API] POST {endpoint} selhal: {e}')
        return None

def api_get(endpoint):
    """GET ze serveru přes http.client."""
    try:
        conn = http.client.HTTPConnection(SERVER_HOST, SERVER_PORT, timeout=3)
        conn.request('GET', endpoint)
        resp = conn.getresponse()
        data = json.loads(resp.read().decode('utf-8'))
        conn.close()
        return data
    except Exception as e:
        print(f'[API] GET {endpoint} selhal: {e}')
        return None

def server_dostupny():
    try:
        conn = http.client.HTTPConnection(SERVER_HOST, SERVER_PORT, timeout=2)
        conn.request('GET', '/')
        conn.getresponse()
        conn.close()
        return True
    except Exception:
        return False

# ── Login přes server ────────────────────────────────────────────────────

def over_login(username, password):
    """
    Vrátí (True, 'správné jméno') nebo (False, 'zpráva o chybě').
    Zkouší server; pokud není dostupný, padne zpět na lokální soubor.
    """
    result = api_post('/api/login', {'username': username, 'password': password})
    if result is not None:
        if result.get('success'):
            return True, result.get('username', username)
        else:
            return False, result.get('message', 'Chyba přihlášení.')
    # Fallback – lokální soubor
    uzivatele = nacti_uzivatele_local()
    for u in uzivatele:
        if u['username'].lower() == username.strip().lower():
            if u['password'] == password:
                return True, u['username']
            else:
                return False, 'Špatné heslo.'
    return False, 'Uživatel nenalezen. (offline fallback)'

def odeslat_skore_server(username, password, skore, obtiznost):
    """
    Odešle skóre na server v background threadu.
    Pokud server není dostupný, uloží lokálně jako fallback.
    """
    result = api_post('/api/submit_score', {
        'username':   username,
        'password':   password,
        'score':      skore,
        'difficulty': obtiznost,
    })
    if result is None:
        # Fallback: ulož lokálně
        _uloz_lokalne(username, skore, obtiznost)
    return result

def _uloz_lokalne(jmeno, skore, obtiznost):
    zaznamy = nacti_skore_local()
    nalezeno = False
    for z in zaznamy:
        if z['name'].lower() == jmeno.lower():
            nalezeno = True
            if skore > z['score']:
                z['score'] = skore
                z['difficulty'] = obtiznost
            break
    if not nalezeno:
        zaznamy.append({'name': jmeno, 'score': skore, 'difficulty': obtiznost})
    zaznamy = sorted(zaznamy, key=lambda x: x['score'], reverse=True)[:10]
    try:
        with open(DB_FILE, 'w', encoding='utf-8') as f:
            json.dump(zaznamy, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f'Chyba při lokálním zápisu skóre: {e}')

# ── Kreslení ──────────────────────────────────────────────────────────────

def kresli_ptaka(screen, x, y, uhel, frame):
    body_surf = pygame.Surface((44, 34), pygame.SRCALPHA)
    for i in range(34):
        r = int(255 - i * 1.5); g = int(220 - i * 0.5)
        pygame.draw.line(body_surf, (r, g, 0, 255), (0, i), (43, i))
    rotated = pygame.transform.rotate(body_surf, -uhel)
    rx, ry = rotated.get_rect(center=(x, y)).topleft
    screen.blit(rotated, (rx, ry))
    pygame.draw.circle(screen, (255, 255, 255), (int(x + 10), int(y - 5)), 7)
    pygame.draw.circle(screen, (0, 0, 0), (int(x + 12), int(y - 5)), 4)
    pygame.draw.polygon(screen, (255, 140, 0), [(int(x+18), int(y-2)), (int(x+28), int(y+1)), (int(x+18), int(y+5))])
    wing_y = int(math.sin(frame * 0.35) * 6)
    wing_pts = [(int(x-5), int(y+wing_y)), (int(x+8), int(y+8+wing_y)), (int(x-8), int(y+10+wing_y)), (int(x-18), int(y+4+wing_y))]
    pygame.draw.polygon(screen, (255, 180, 0), wing_pts)

def kresli_pozadi(screen, WIDTH, HEIGHT):
    for y in range(HEIGHT):
        t = y / HEIGHT
        r, g, b = int(80 + t * 40), int(160 + t * 50), int(220 - t * 60)
        pygame.draw.line(screen, (r, g, b), (0, y), (WIDTH, y))
    pygame.draw.rect(screen, (90, 170, 60), (0, HEIGHT - 80, WIDTH, 80))
    pygame.draw.rect(screen, (110, 190, 70), (0, HEIGHT - 80, WIDTH, 15))

def kresli_slunce(screen, ray_angle):
    sx, sy = 42, 52; radius = 22
    for i in range(8):
        angle = math.radians(ray_angle + i * 45)
        x1 = int(sx + math.cos(angle) * (radius + 6)); y1 = int(sy + math.sin(angle) * (radius + 6))
        x2 = int(sx + math.cos(angle) * (radius + 14)); y2 = int(sy + math.sin(angle) * (radius + 14))
        pygame.draw.line(screen, (255, 210, 50), (x1, y1), (x2, y2), 3)
    pygame.draw.circle(screen, (255, 230, 80), (sx, sy), radius)
    pygame.draw.circle(screen, (255, 245, 130), (sx - 5, sy - 5), radius // 3)

def kresli_mrak(screen, x, y, w):
    x, y, w = int(x), int(y), int(w)
    h_base = w // 3
    pygame.draw.ellipse(screen, (235, 245, 255), (x, y + h_base // 2, w, h_base))
    pygame.draw.circle(screen, (240, 248, 255), (x + w // 4, y + h_base // 2), h_base // 2 + 4)
    pygame.draw.circle(screen, (245, 250, 255), (x + w // 2, y), h_base // 2 + 8)
    pygame.draw.circle(screen, (240, 248, 255), (x + 3 * w // 4, y + h_base // 4), h_base // 2 + 5)

def kresli_trubku(screen, rect, je_horni):
    x, y, w, h = rect
    pygame.draw.rect(screen, (30, 160, 40), rect)
    cap_h = 28
    cap_y = y + h - cap_h if je_horni else y
    pygame.draw.rect(screen, (40, 180, 50), (x - 5, cap_y, w + 10, cap_h))
    pygame.draw.rect(screen, (20, 100, 20), (x - 5, cap_y, w + 10, cap_h), 2)

def kresli_panel(surf, x, y, w, h, alpha=160):
    s = pygame.Surface((w, h), pygame.SRCALPHA)
    s.fill((0, 0, 0, alpha))
    pygame.draw.rect(s, (255, 255, 255, 40), (0, 0, w, h), 2)
    surf.blit(s, (x, y))

def text_shadow(surf, txt, font, color, x, y):
    surf.blit(font.render(txt, True, (0, 0, 0)), (x + 2, y + 2))
    surf.blit(font.render(txt, True, color), (x, y))

def kresli_vstupni_pole(surf, font, text, x, y, w, h, aktivni):
    color = (255, 220, 50) if aktivni else (180, 180, 180)
    pygame.draw.rect(surf, (30, 30, 30, 200), (x, y, w, h), border_radius=8)
    pygame.draw.rect(surf, color, (x, y, w, h), 2, border_radius=8)
    rendered = font.render(text + ('|' if aktivni else ''), True, (255, 255, 255))
    surf.blit(rendered, (x + 10, y + (h - rendered.get_height()) // 2))

# ── LOGIN SCREEN ─────────────────────────────────────────────────────────

def login_screen(screen, fonts):
    """
    Zobrazí login/register obrazovku.
    Vrátí (username, password) po úspěšném přihlášení.
    """
    font_big, font_mid, font_sml, font_xs = fonts
    clock = pygame.time.Clock()

    tab          = 'login'
    fields       = {'username': '', 'password': ''}
    active_field = 'username'
    zprava       = ''
    zprava_ok    = False
    ray_angle    = 0.0
    mraky = [
        {'x': 60.0,  'y': 60, 'w': 90,  'speed': 0.3},
        {'x': 220.0, 'y': 95, 'w': 70,  'speed': 0.2},
        {'x': 370.0, 'y': 50, 'w': 100, 'speed': 0.25},
    ]

    WHITE  = (255, 255, 255)
    YELLOW = (255, 220, 0)
    GREEN  = (80, 220, 120)
    RED    = (240, 80, 80)

    # ── Rozložení panelu – všechny souřadnice na jednom místě ──
    pw, ph = 360, 330
    px     = WIDTH  // 2 - pw // 2   # 60
    py     = HEIGHT // 2 - ph // 2   # 185  (vycentrováno svisle)

    tab_w  = (pw - 30) // 2          # šířka jednoho tabu
    TAB_LOGIN    = pygame.Rect(px + 10,              py + 10, tab_w,      32)
    TAB_REGISTER = pygame.Rect(px + 20 + tab_w,     py + 10, tab_w,      32)
    FIELD_USER   = pygame.Rect(px + 16,              py + 110, pw - 32,   38)
    FIELD_PASS   = pygame.Rect(px + 16,              py + 180, pw - 32,   38)
    BTN_SUBMIT   = pygame.Rect(px + 16,              py + 250, pw - 32,   40)

    def kresli_tab_rect(surf, label, rect, aktivni):
        bg  = (50, 120, 220) if aktivni else (50, 50, 50)
        pygame.draw.rect(surf, bg, rect, border_radius=7)
        col = WHITE if aktivni else (150, 150, 150)
        t   = font_sml.render(label, True, col)
        surf.blit(t, (rect.x + (rect.w - t.get_width()) // 2,
                      rect.y + (rect.h - t.get_height()) // 2))

    def proved_akci():
        """Provede login nebo register podle aktuálního tabu."""
        nonlocal zprava, zprava_ok, tab
        u = fields['username'].strip()
        p = fields['password'].strip()
        if not u or not p:
            zprava = 'Vyplň obě pole!'; zprava_ok = False
            return None
        if tab == 'login':
            ok, msg = over_login(u, p)
            if ok:
                return (msg, p)          # ← úspěch, vrátíme tuple
            zprava = msg; zprava_ok = False
        else:
            res = api_post('/api/register', {'username': u, 'password': p})
            if res is None:
                zprava = 'Server offline! Spusť server.py'; zprava_ok = False
            elif res.get('success'):
                zprava = 'Registrace OK! Nyní se přihlaš.'; zprava_ok = True
                tab = 'login'
            else:
                zprava = res.get('message', 'Chyba'); zprava_ok = False
        return None

    while True:
        clock.tick(60)
        ray_angle += 0.4
        for m in mraky:
            m['x'] += m['speed']
            if m['x'] > WIDTH + 60:
                m['x'] = -130.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                pos = event.pos
                if TAB_LOGIN.collidepoint(pos):
                    tab = 'login';    zprava = ''
                elif TAB_REGISTER.collidepoint(pos):
                    tab = 'register'; zprava = ''
                elif FIELD_USER.collidepoint(pos):
                    active_field = 'username'
                elif FIELD_PASS.collidepoint(pos):
                    active_field = 'password'
                elif BTN_SUBMIT.collidepoint(pos):
                    vysledek = proved_akci()
                    if vysledek:
                        return vysledek

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_TAB:
                    active_field = 'password' if active_field == 'username' else 'username'
                elif event.key == pygame.K_RETURN:
                    vysledek = proved_akci()
                    if vysledek:
                        return vysledek
                elif event.key == pygame.K_BACKSPACE:
                    fields[active_field] = fields[active_field][:-1]
                else:
                    if len(fields[active_field]) < 24:
                        fields[active_field] += event.unicode

        # ── Kreslení ──────────────────────────────────────────────────────
        kresli_pozadi(screen, WIDTH, HEIGHT)
        kresli_slunce(screen, ray_angle)
        for m in mraky:
            kresli_mrak(screen, m['x'], m['y'], m['w'])

        # Panel
        kresli_panel(screen, px, py, pw, ph, 220)

        # Nadpis
        title = font_mid.render('🐦 Flappy Bird', True, YELLOW)
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, py - 44))

        # Taby
        kresli_tab_rect(screen, 'Přihlásit se',  TAB_LOGIN,    tab == 'login')
        kresli_tab_rect(screen, 'Registrovat se', TAB_REGISTER, tab == 'register')

        # Uživatelské jméno
        lbl_u = font_xs.render('Uživatelské jméno', True, (160, 160, 160))
        screen.blit(lbl_u, (FIELD_USER.x, FIELD_USER.y - 20))
        kresli_vstupni_pole(screen, font_sml, fields['username'],
                            FIELD_USER.x, FIELD_USER.y, FIELD_USER.w, FIELD_USER.h,
                            active_field == 'username')

        # Heslo
        lbl_p = font_xs.render('Heslo', True, (160, 160, 160))
        screen.blit(lbl_p, (FIELD_PASS.x, FIELD_PASS.y - 20))
        stars = '*' * len(fields['password'])
        kresli_vstupni_pole(screen, font_sml, stars,
                            FIELD_PASS.x, FIELD_PASS.y, FIELD_PASS.w, FIELD_PASS.h,
                            active_field == 'password')

        # Tlačítko
        btn_label = 'Přihlásit se' if tab == 'login' else 'Registrovat se'
        pygame.draw.rect(screen, (50, 120, 220), BTN_SUBMIT, border_radius=8)
        # hover efekt
        mx_cur, my_cur = pygame.mouse.get_pos()
        if BTN_SUBMIT.collidepoint(mx_cur, my_cur):
            pygame.draw.rect(screen, (80, 150, 255), BTN_SUBMIT, border_radius=8)
        bt = font_sml.render(btn_label, True, WHITE)
        screen.blit(bt, (BTN_SUBMIT.x + (BTN_SUBMIT.w - bt.get_width()) // 2,
                         BTN_SUBMIT.y + (BTN_SUBMIT.h - bt.get_height()) // 2))

        # Zpráva
        if zprava:
            col = GREEN if zprava_ok else RED
            zm = font_xs.render(zprava, True, col)
            screen.blit(zm, (WIDTH // 2 - zm.get_width() // 2, py + ph + 12))

        # Tip
        tip = font_xs.render('Tab = přepnout pole  ·  Enter = potvrdit', True, (110, 110, 110))
        screen.blit(tip, (WIDTH // 2 - tip.get_width() // 2, HEIGHT - 30))

        pygame.display.flip()

# ── HLAVNÍ HRA ────────────────────────────────────────────────────────────

def spust_hru():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption('Flappy Bird – Maturitní Projekt')
    clock = pygame.time.Clock()

    try:
        font_big = pygame.font.SysFont('Arial', 52, bold=True)
        font_mid = pygame.font.SysFont('Arial', 32, bold=True)
        font_sml = pygame.font.SysFont('Arial', 22)
        font_xs  = pygame.font.SysFont('Arial', 18)
    except Exception:
        font_big = pygame.font.Font(None, 58)
        font_mid = pygame.font.Font(None, 36)
        font_sml = pygame.font.Font(None, 26)
        font_xs  = pygame.font.Font(None, 22)

    fonts = (font_big, font_mid, font_sml, font_xs)
    WHITE, YELLOW, ORANGE = (255, 255, 255), (255, 220, 0), (255, 140, 0)

    # ── LOGIN ──────────────────────────────────────────────────────────────
    logged_user, logged_pass = login_screen(screen, fonts)

    # ── HERNÍ PROMĚNNÉ ──────────────────────────────────────────────────────
    stav = "MENU"
    vybrana_obtiznost = "normal"
    menu_sel = 0
    menu_polozky = ["HRÁT", "NASTAVENÍ", "ŽEBŘÍČEK"]

    bird_x, bird_y, bird_dy = 80, float(HEIGHT // 2), 0.0
    bird_frame, bird_uhel = 0, 0.0
    trubky, casovac_trubky, skore = [], 0, 0
    odpocet_timer = 0
    bg_offset = 0.0
    ray_angle = 0.0
    score_result = None      # výsledek odeslání skóre

    mraky = [
        {'x': 60.0, 'y': 60, 'w': 90, 'speed': 0.3},
        {'x': 200.0, 'y': 100, 'w': 70, 'speed': 0.2},
        {'x': 340.0, 'y': 50, 'w': 110, 'speed': 0.25},
        {'x': 420.0, 'y': 85, 'w': 75, 'speed': 0.18},
    ]

    def reset_hry():
        nonlocal bird_y, bird_dy, bird_uhel, bird_frame, trubky
        nonlocal casovac_trubky, skore, bg_offset, score_result
        bird_y = float(HEIGHT // 2)
        bird_dy = bird_uhel = bird_frame = 0.0
        trubky = []; casovac_trubky = 0; skore = 0
        bg_offset = 0.0; score_result = None

    def odesli_skore_async(us, pw, sc, diff):
        """Odešle skóre v background threadu, výsledek uloží do score_result."""
        nonlocal score_result
        res = odeslat_skore_server(us, pw, sc, diff)
        score_result = res

    # ── MAIN LOOP ──────────────────────────────────────────────────────────
    while True:
        clock.tick(60)
        bg_offset += 1.0
        ray_angle += 0.4
        for m in mraky:
            m['x'] += m['speed']
            if m['x'] > WIDTH + 60:
                m['x'] = -130.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()

            if event.type == pygame.KEYDOWN:
                if stav == "MENU":
                    if event.key in (pygame.K_UP, pygame.K_w):
                        menu_sel = (menu_sel - 1) % len(menu_polozky)
                    elif event.key in (pygame.K_DOWN, pygame.K_s):
                        menu_sel = (menu_sel + 1) % len(menu_polozky)
                    elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                        if menu_sel == 0:
                            reset_hry(); stav = "ODPOCET"
                            odpocet_timer = pygame.time.get_ticks()
                        elif menu_sel == 1:
                            stav = "NASTAVENI"
                        elif menu_sel == 2:
                            stav = "ZEBRICEK"

                elif stav == "NASTAVENI":
                    if event.key in (pygame.K_ESCAPE, pygame.K_BACKSPACE):
                        stav = "MENU"
                    elif event.key in (pygame.K_LEFT, pygame.K_a):
                        keys = list(OBTIZNOSTI.keys())
                        vybrana_obtiznost = keys[(keys.index(vybrana_obtiznost) - 1) % len(keys)]
                    elif event.key in (pygame.K_RIGHT, pygame.K_d):
                        keys = list(OBTIZNOSTI.keys())
                        vybrana_obtiznost = keys[(keys.index(vybrana_obtiznost) + 1) % len(keys)]
                    elif event.key == pygame.K_RETURN:
                        stav = "MENU"

                elif stav == "ZEBRICEK":
                    if event.key in (pygame.K_ESCAPE, pygame.K_BACKSPACE, pygame.K_SPACE):
                        stav = "MENU"

                elif stav == "HRANI":
                    if event.key in (pygame.K_SPACE, pygame.K_UP):
                        bird_dy = OBTIZNOSTI[vybrana_obtiznost]["flap"]
                        bird_uhel = -25

                elif stav == "GAME_OVER":
                    if event.key == pygame.K_SPACE:
                        stav = "MENU"
                    elif event.key == pygame.K_r:
                        reset_hry(); stav = "ODPOCET"
                        odpocet_timer = pygame.time.get_ticks()

        # ── LOGIKA HRANI ──────────────────────────────────────────────────
        if stav == "ODPOCET":
            if (pygame.time.get_ticks() - odpocet_timer) > 3500:
                stav = "HRANI"

        if stav == "HRANI":
            cfg = OBTIZNOSTI[vybrana_obtiznost]
            bird_frame += 1
            bird_dy += cfg["gravity"]
            bird_y  += bird_dy
            bird_uhel = max(-30, min(90, bird_uhel + bird_dy * 2))

            casovac_trubky += 1
            if casovac_trubky > int(90 / (cfg["pipe_speed"] / 3)):
                h = random.randint(100, HEIGHT - cfg["pipe_gap"] - 120)
                trubky.append({
                    'top_rect': pygame.Rect(WIDTH, 0, 52, h),
                    'bot_rect': pygame.Rect(WIDTH, h + cfg["pipe_gap"], 52, HEIGHT - h - cfg["pipe_gap"]),
                    'scored': False
                })
                casovac_trubky = 0

            bird_rect = pygame.Rect(bird_x - 14, int(bird_y) - 12, 28, 24)
            for t in trubky[:]:
                t['top_rect'].x -= cfg["pipe_speed"]
                t['bot_rect'].x -= cfg["pipe_speed"]
                if bird_rect.colliderect(t['top_rect']) or bird_rect.colliderect(t['bot_rect']):
                    stav = "UKLADANI"
                    # Odeslat skóre na server (background)
                    threading.Thread(
                        target=odesli_skore_async,
                        args=(logged_user, logged_pass, skore, vybrana_obtiznost),
                        daemon=True
                    ).start()
                if t['top_rect'].x + 52 < bird_x and not t['scored']:
                    skore += 1; t['scored'] = True
                if t['top_rect'].x < -60:
                    trubky.remove(t)

            if bird_y > HEIGHT - 80 or bird_y < 0:
                stav = "UKLADANI"
                threading.Thread(
                    target=odesli_skore_async,
                    args=(logged_user, logged_pass, skore, vybrana_obtiznost),
                    daemon=True
                ).start()

        # ── KRESLENÍ ──────────────────────────────────────────────────────
        kresli_pozadi(screen, WIDTH, HEIGHT)
        kresli_slunce(screen, ray_angle)
        for m in mraky:
            kresli_mrak(screen, m['x'], m['y'], m['w'])

        if stav in ("HRANI", "ODPOCET", "UKLADANI"):
            for t in trubky:
                kresli_trubku(screen, t['top_rect'], True)
                kresli_trubku(screen, t['bot_rect'], False)
            kresli_ptaka(screen, bird_x, int(bird_y), bird_uhel, bird_frame)

        # ── MENU ──────────────────────────────────────────────────────────
        if stav == "MENU":
            kresli_panel(screen, WIDTH // 2 - 180, 60, 360, 100, 140)
            text_shadow(screen, "FLAPPY BIRD", font_big, YELLOW, WIDTH // 2 - 155, 75)

            # Jméno přihlášeného
            un = font_xs.render(f"👤 {logged_user}", True, (200, 240, 200))
            screen.blit(un, (WIDTH // 2 - un.get_width() // 2, 148))

            for i, pol in enumerate(menu_polozky):
                sel = (i == menu_sel)
                kresli_panel(screen, WIDTH // 2 - 130, 270 + i * 80, 260, 55, 180 if sel else 100)
                text_shadow(screen, ("> " if sel else "  ") + pol, font_mid,
                            YELLOW if sel else WHITE, WIDTH // 2 - 110, 280 + i * 80)

            cfg = OBTIZNOSTI[vybrana_obtiznost]
            kresli_panel(screen, WIDTH // 2 - 80, 530, 160, 40, 120)
            screen.blit(font_sml.render(f"MOD: {cfg['label']}", True, cfg['color']), (WIDTH // 2 - 55, 537))

        # ── NASTAVENI ──────────────────────────────────────────────────────
        elif stav == "NASTAVENI":
            text_shadow(screen, "NASTAVENI", font_big, YELLOW, WIDTH // 2 - 135, 95)
            for i, k in enumerate(OBTIZNOSTI.keys()):
                cfg2 = OBTIZNOSTI[k]; sel = (k == vybrana_obtiznost); px2 = 40 + i * 135
                kresli_panel(screen, px2, 250, 120, 140, 200 if sel else 100)
                if sel:
                    pygame.draw.rect(screen, cfg2['color'], (px2, 250, 120, 140), 3)
                screen.blit(font_mid.render(cfg2['label'], True, cfg2['color']), (px2 + 10, 265))

        # ── ZEBRICEK ──────────────────────────────────────────────────────
        elif stav == "ZEBRICEK":
            text_shadow(screen, "ZEBRICEK", font_big, YELLOW, WIDTH // 2 - 130, 60)
            # Zkus načíst ze serveru, fallback lokálně
            data = api_get('/api/scores') or nacti_skore_local()
            kresli_panel(screen, 30, 150, WIDTH - 60, 440, 140)
            if not data:
                screen.blit(font_sml.render("Žádné záznamy", True, WHITE), (WIDTH // 2 - 80, 330))
            else:
                for i, z in enumerate(data[:8]):
                    ry = 195 + i * 48
                    col = [(255, 215, 0), (192, 192, 192), (205, 127, 50), (220, 220, 220)][min(i, 3)]
                    screen.blit(font_sml.render(f"{i+1}.", True, col), (50, ry))
                    screen.blit(font_sml.render(z['name'][:12], True, WHITE), (90, ry))
                    text_shadow(screen, str(z['score']), font_mid, YELLOW, 310, ry - 2)
            hint = font_xs.render("ESC / Mezerník = zpět", True, (150, 150, 150))
            screen.blit(hint, (WIDTH // 2 - hint.get_width() // 2, HEIGHT - 50))

        # ── ODPOCET ──────────────────────────────────────────────────────
        elif stav == "ODPOCET":
            elapsed = (pygame.time.get_ticks() - odpocet_timer) / 1000.0
            cislo = max(1, 3 - int(elapsed))
            if elapsed < 3.0:
                text_shadow(screen, str(cislo), font_big, WHITE, WIDTH // 2 - 20, HEIGHT // 2 - 60)

        # ── HRANI – skóre ─────────────────────────────────────────────────
        elif stav == "HRANI":
            text_shadow(screen, str(skore), font_big, WHITE, WIDTH // 2 - 20, 30)

        # ── UKLADANI (čeká na server) ──────────────────────────────────────
        elif stav == "UKLADANI":
            kresli_panel(screen, WIDTH // 2 - 190, HEIGHT // 2 - 80, 380, 160, 200)
            text_shadow(screen, "KONEC HRY", font_mid, ORANGE, WIDTH // 2 - 100, HEIGHT // 2 - 70)
            text_shadow(screen, f"Skóre: {skore}", font_mid, WHITE, WIDTH // 2 - 70, HEIGHT // 2 - 30)
            wait_txt = font_sml.render("Ukládám výsledek…", True, (200, 200, 200))
            screen.blit(wait_txt, (WIDTH // 2 - wait_txt.get_width() // 2, HEIGHT // 2 + 16))
            # Jakmile máme výsledek, přejdeme na GAME_OVER
            if score_result is not None:
                stav = "GAME_OVER"

        # ── GAME OVER ─────────────────────────────────────────────────────
        elif stav == "GAME_OVER":
            kresli_panel(screen, WIDTH // 2 - 195, HEIGHT // 2 - 170, 390, 340, 210)
            text_shadow(screen, "HOTOVO!", font_big, YELLOW, WIDTH // 2 - 110, HEIGHT // 2 - 160)
            text_shadow(screen, f"Skóre: {skore}", font_mid, WHITE, WIDTH // 2 - 75, HEIGHT // 2 - 90)

            if score_result:
                msg = score_result.get('message', '')
                nr  = score_result.get('new_record', False)
                col = (80, 255, 120) if nr else (200, 200, 200)
                m_s = font_sml.render(msg, True, col)
                screen.blit(m_s, (WIDTH // 2 - m_s.get_width() // 2, HEIGHT // 2 - 45))
            else:
                # server offline, lokální uložení
                m_s = font_sml.render("Uloženo lokálně.", True, (200, 200, 200))
                screen.blit(m_s, (WIDTH // 2 - m_s.get_width() // 2, HEIGHT // 2 - 45))

            # Instrukce
            i1 = font_sml.render("Mezerník = Menu", True, WHITE)
            i2 = font_xs.render("R = Hrát znovu", True, (180, 180, 180))
            screen.blit(i1, (WIDTH // 2 - i1.get_width() // 2, HEIGHT // 2 + 20))
            screen.blit(i2, (WIDTH // 2 - i2.get_width() // 2, HEIGHT // 2 + 56))

            # Skóre v žebříčku
            for event in pygame.event.get(pygame.KEYDOWN):
                if event.key == pygame.K_SPACE:
                    stav = "MENU"
                elif event.key == pygame.K_r:
                    reset_hry(); stav = "ODPOCET"
                    odpocet_timer = pygame.time.get_ticks()

        pygame.display.flip()


if __name__ == "__main__":
    inicializuj_db()
    spust_hru()