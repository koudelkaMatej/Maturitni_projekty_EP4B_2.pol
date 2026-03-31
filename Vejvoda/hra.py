import pygame
import sys
import random
import json
import os
import math

# --- KONFIGURACE ---
DB_FILE = 'highscores.json'
LOGIN_FILE = 'prihlaseni.json'

WIDTH, HEIGHT = 480, 700

OBTIZNOSTI = {
    "easy":   {"gravity": 0.3, "flap": -7,  "pipe_speed": 2.5, "pipe_gap": 180, "label": "EASY",   "color": (80, 200, 120)},
    "normal": {"gravity": 0.45,"flap": -8,  "pipe_speed": 3.5, "pipe_gap": 150, "label": "NORMAL", "color": (240, 200, 60)},
    "hard":   {"gravity": 0.6, "flap": -9,  "pipe_speed": 5.0, "pipe_gap": 120, "label": "HARD",   "color": (230, 60, 60)},
}

# --- DB FUNKCE ---
def inicializuj_db():
    if not os.path.exists(DB_FILE):
        with open(DB_FILE, 'w', encoding='utf-8') as f:
            json.dump([], f)

def nacti_skore():
    try:
        with open(DB_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return []
def uloz_skore(jmeno, skore, obtiznost):
    zaznamy = nacti_skore()
    nalezeno = False
    j_clean = jmeno.strip()
    
    # Projdeme existující záznamy
    for z in zaznamy:
        # Pokud hráč už v žebříčku je (nezávisle na velikosti písmen)
        if z['name'].lower() == j_clean.lower():
            nalezeno = True
            # Aktualizujeme skóre jen pokud je nové skóre VYŠŠÍ
            if skore > z['score']:
                z['score'] = skore
                z['difficulty'] = obtiznost
                z['name'] = j_clean # Aktualizace jména na verzi, kterou zadal teď
            break
    
    # Pokud hráč v žebříčku ještě vůbec není, přidáme ho
    if not nalezeno:
        zaznamy.append({"name": j_clean, "score": skore, "difficulty": obtiznost})
    
    # Seřadíme od nejlepšího a vezmeme jen TOP 10
    zaznamy = sorted(zaznamy, key=lambda x: x['score'], reverse=True)[:10]
    
    try:
        with open(DB_FILE, 'w', encoding='utf-8') as f:
            json.dump(zaznamy, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"Chyba při zápisu skóre: {e}")
def nacti_uzivatele():
    try:
        with open(LOGIN_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return []

def je_registrovan(jmeno):
    uzivatele = nacti_uzivatele()
    return any(u['username'].lower() == jmeno.strip().lower() for u in uzivatele)

# --- KRESLENÍ PTÁKA ---
def kresli_ptaka(screen, x, y, uhel, frame):
    body_surf = pygame.Surface((44, 34), pygame.SRCALPHA)
    for i in range(34):
        r = int(255 - i * 1.5)
        g = int(220 - i * 0.5)
        b = 0
        pygame.draw.line(body_surf, (r, g, b, 255), (0, i), (43, i))
    
    wing_y_offset = int(math.sin(frame * 0.35) * 6)
    rotated = pygame.transform.rotate(body_surf, -uhel)
    rx, ry = rotated.get_rect(center=(x, y)).topleft
    screen.blit(rotated, (rx, ry))

    pygame.draw.circle(screen, (255, 255, 255), (int(x + 10), int(y - 5)), 7)
    pygame.draw.circle(screen, (0, 0, 0), (int(x + 12), int(y - 5)), 4)
    pygame.draw.polygon(screen, (255, 140, 0), [(int(x + 18), int(y - 2)), (int(x + 28), int(y + 1)), (int(x + 18), int(y + 5))])

    wing_pts = [(int(x - 5), int(y + wing_y_offset)), (int(x + 8), int(y + 8 + wing_y_offset)), (int(x - 8), int(y + 10 + wing_y_offset)), (int(x - 18), int(y + 4 + wing_y_offset))]
    pygame.draw.polygon(screen, (255, 180, 0), wing_pts)

# --- POZADÍ ---
def kresli_pozadi(screen, offset, WIDTH, HEIGHT):
    for y in range(HEIGHT):
        t = y / HEIGHT
        r, g, b = int(80 + t * 40), int(160 + t * 50), int(220 - t * 60)
        pygame.draw.line(screen, (r, g, b), (0, y), (WIDTH, y))

    pygame.draw.rect(screen, (90, 170, 60), (0, HEIGHT - 80, WIDTH, 80))
    pygame.draw.rect(screen, (110, 190, 70), (0, HEIGHT - 80, WIDTH, 15))

def kresli_slunce(screen, ray_angle):
    sx, sy = 42, 52
    radius = 22
    # Paprsky (rotující)
    num_rays = 8
    for i in range(num_rays):
        angle = math.radians(ray_angle + i * (360 / num_rays))
        r1 = radius + 6
        r2 = radius + 14
        x1 = int(sx + math.cos(angle) * r1)
        y1 = int(sy + math.sin(angle) * r1)
        x2 = int(sx + math.cos(angle) * r2)
        y2 = int(sy + math.sin(angle) * r2)
        pygame.draw.line(screen, (255, 210, 50), (x1, y1), (x2, y2), 3)
    # Tělo slunce
    pygame.draw.circle(screen, (255, 230, 80), (sx, sy), radius)
    pygame.draw.circle(screen, (255, 245, 130), (sx - 5, sy - 5), radius // 3)

def kresli_mrak(screen, x, y, w):
    # Jednoduchý mrak ze skupiny kružnic
    x, y, w = int(x), int(y), int(w)
    h_base = w // 3
    # Základní obdélník
    pygame.draw.ellipse(screen, (235, 245, 255), (x, y + h_base // 2, w, h_base))
    # Kopečky nahoře
    pygame.draw.circle(screen, (240, 248, 255), (x + w // 4, y + h_base // 2), h_base // 2 + 4)
    pygame.draw.circle(screen, (245, 250, 255), (x + w // 2, y), h_base // 2 + 8)
    pygame.draw.circle(screen, (240, 248, 255), (x + 3 * w // 4, y + h_base // 4), h_base // 2 + 5)
    # Jemný obrys
    pygame.draw.ellipse(screen, (210, 230, 250), (x, y + h_base // 2, w, h_base), 1)

def kresli_trubku(screen, rect, je_horni):
    x, y, w, h = rect
    pygame.draw.rect(screen, (30, 160, 40), rect)
    cap_h = 28
    cap_y = y + h - cap_h if je_horni else y
    pygame.draw.rect(screen, (40, 180, 50), (x - 5, cap_y, w + 10, cap_h))
    pygame.draw.rect(screen, (20, 100, 20), (x - 5, cap_y, w + 10, cap_h), 2)

# --- HLAVNÍ HRA ---
def spust_hru():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption('Flappy Bird - Maturitní Projekt')
    clock = pygame.time.Clock()

    try:
        font_big = pygame.font.SysFont('Arial', 52, bold=True)
        font_mid = pygame.font.SysFont('Arial', 32, bold=True)
        font_sml = pygame.font.SysFont('Arial', 22)
        font_xs  = pygame.font.SysFont('Arial', 18)
    except:
        font_big = pygame.font.Font(None, 58)
        font_mid = pygame.font.Font(None, 36)
        font_sml = pygame.font.Font(None, 26)
        font_xs  = pygame.font.Font(None, 22)

    WHITE, YELLOW, ORANGE = (255, 255, 255), (255, 220, 0), (255, 140, 0)

    stav = "MENU"
    vybrana_obtiznost = "normal"
    menu_sel = 0
    menu_polozky = ["HRÁT", "NASTAVENÍ", "ŽEBŘÍČEK"]

    bird_x, bird_y, bird_dy = 80, float(HEIGHT // 2), 0.0
    bird_frame, bird_uhel = 0, 0.0
    trubky, casovac_trubky, skore = [], 0, 0
    jmeno, chyba_jmeno = "", ""
    odpocet, odpocet_timer = 3, 0
    bg_offset, flash, particles = 0.0, 0, []

    # --- MRAKY A SLUNCE ---
    mraky = [
        {'x': 60.0,  'y': 60,  'w': 90,  'speed': 0.3},
        {'x': 200.0, 'y': 100, 'w': 70,  'speed': 0.2},
        {'x': 340.0, 'y': 50,  'w': 110, 'speed': 0.25},
        {'x': 420.0, 'y': 85,  'w': 75,  'speed': 0.18},
    ]
    slunce_ray_angle = 0.0

    def reset_hry():
        nonlocal bird_y, bird_dy, bird_uhel, bird_frame, trubky, casovac_trubky, skore, jmeno, chyba_jmeno, bg_offset, flash, particles
        bird_y, bird_dy, bird_uhel, bird_frame, trubky, casovac_trubky, skore = float(HEIGHT // 2), 0.0, 0.0, 0, [], 0, 0
        jmeno, chyba_jmeno, bg_offset, flash, particles = "", "", 0.0, 0, []

    def kresli_panel(surf, x, y, w, h, alpha=160):
        s = pygame.Surface((w, h), pygame.SRCALPHA)
        s.fill((0, 0, 0, alpha))
        pygame.draw.rect(s, (255, 255, 255, 40), (0, 0, w, h), 2)
        surf.blit(s, (x, y))

    def text_shadow(surf, txt, font, color, x, y):
        surf.blit(font.render(txt, True, (0,0,0)), (x+2, y+2))
        surf.blit(font.render(txt, True, color), (x, y))

    while True:
        dt = clock.tick(60)
        bg_offset += 1.0
        slunce_ray_angle += 0.4

        # Pohyb mraků
        for m in mraky:
            m['x'] += m['speed']
            if m['x'] > WIDTH + 60:
                m['x'] = -130.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if stav == "MENU":
                    if event.key in (pygame.K_UP, pygame.K_w): menu_sel = (menu_sel - 1) % len(menu_polozky)
                    elif event.key in (pygame.K_DOWN, pygame.K_s): menu_sel = (menu_sel + 1) % len(menu_polozky)
                    elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                        if menu_sel == 0: reset_hry(); stav = "ODPOCET"; odpocet_timer = pygame.time.get_ticks()
                        elif menu_sel == 1: stav = "NASTAVENI"
                        elif menu_sel == 2: stav = "ZEBRICEK"
                elif stav == "NASTAVENI":
                    if event.key in (pygame.K_ESCAPE, pygame.K_BACKSPACE): stav = "MENU"
                    elif event.key in (pygame.K_LEFT, pygame.K_a):
                        keys = list(OBTIZNOSTI.keys())
                        vybrana_obtiznost = keys[(keys.index(vybrana_obtiznost) - 1) % len(keys)]
                    elif event.key in (pygame.K_RIGHT, pygame.K_d):
                        keys = list(OBTIZNOSTI.keys())
                        vybrana_obtiznost = keys[(keys.index(vybrana_obtiznost) + 1) % len(keys)]
                    elif event.key == pygame.K_RETURN: stav = "MENU"
                elif stav == "ZEBRICEK":
                    if event.key in (pygame.K_ESCAPE, pygame.K_BACKSPACE, pygame.K_SPACE): stav = "MENU"
                elif stav == "HRANI":
                    if event.key in (pygame.K_SPACE, pygame.K_UP): bird_dy = OBTIZNOSTI[vybrana_obtiznost]["flap"]; bird_uhel = -25
                elif stav == "ZADAVANI":
                    if event.key == pygame.K_RETURN:
                        j_clean = jmeno.strip()
                        if not j_clean: chyba_jmeno = "Zadejte jmeno!"
                        elif not je_registrovan(j_clean): chyba_jmeno = "Uživatel není na webu!"
                        else: uloz_skore(j_clean, skore, vybrana_obtiznost); stav = "GAME_OVER"
                    elif event.key == pygame.K_BACKSPACE: jmeno = jmeno[:-1]
                    else:
                        if len(jmeno) < 16: jmeno += event.unicode
                elif stav == "GAME_OVER":
                    if event.key == pygame.K_SPACE: stav = "MENU"
                    elif event.key == pygame.K_r: reset_hry(); stav = "ODPOCET"; odpocet_timer = pygame.time.get_ticks()

        if stav == "ODPOCET":
            if (pygame.time.get_ticks() - odpocet_timer) > 3500: stav = "HRANI"

        if stav == "HRANI":
            cfg = OBTIZNOSTI[vybrana_obtiznost]
            bird_frame += 1; bird_dy += cfg["gravity"]; bird_y += bird_dy
            bird_uhel = max(-30, min(90, bird_uhel + bird_dy * 2))
            casovac_trubky += 1
            if casovac_trubky > int(90 / (cfg["pipe_speed"] / 3)):
                h = random.randint(100, HEIGHT - cfg["pipe_gap"] - 120)
                trubky.append({'top_rect': pygame.Rect(WIDTH, 0, 52, h), 'bot_rect': pygame.Rect(WIDTH, h + cfg["pipe_gap"], 52, HEIGHT - h - cfg["pipe_gap"]), 'scored': False})
                casovac_trubky = 0
            for t in trubky[:]:
                t['top_rect'].x -= cfg["pipe_speed"]; t['bot_rect'].x -= cfg["pipe_speed"]
                if pygame.Rect(bird_x - 14, int(bird_y) - 12, 28, 24).colliderect(t['top_rect']) or pygame.Rect(bird_x - 14, int(bird_y) - 12, 28, 24).colliderect(t['bot_rect']): stav = "ZADAVANI"
                if t['top_rect'].x + 52 < bird_x and not t['scored']: skore += 1; t['scored'] = True
                if t['top_rect'].x < -60: trubky.remove(t)
            if bird_y > HEIGHT - 80 or bird_y < 0: stav = "ZADAVANI"

        kresli_pozadi(screen, bg_offset, WIDTH, HEIGHT)
        kresli_slunce(screen, slunce_ray_angle)
        for m in mraky:
            kresli_mrak(screen, m['x'], m['y'], m['w'])

        if stav in ("HRANI", "ZADAVANI", "ODPOCET"):
            for t in trubky: kresli_trubku(screen, t['top_rect'], True); kresli_trubku(screen, t['bot_rect'], False)
            kresli_ptaka(screen, bird_x, int(bird_y), bird_uhel, bird_frame)

        if stav == "MENU":
            kresli_panel(screen, WIDTH//2 - 180, 60, 360, 100, 140)
            text_shadow(screen, "FLAPPY BIRD", font_big, YELLOW, WIDTH//2 - 155, 75)
            for i, pol in enumerate(menu_polozky):
                sel = (i == menu_sel)
                kresli_panel(screen, WIDTH//2 - 130, 270 + i * 80, 260, 55, 180 if sel else 100)
                text_shadow(screen, ("> " if sel else "  ") + pol, font_mid, YELLOW if sel else WHITE, WIDTH//2 - 110, 280 + i * 80)
            cfg = OBTIZNOSTI[vybrana_obtiznost]
            kresli_panel(screen, WIDTH//2 - 80, 530, 160, 40, 120)
            screen.blit(font_sml.render(f"MOD: {cfg['label']}", True, cfg['color']), (WIDTH//2 - 55, 537))

        elif stav == "NASTAVENI":
            text_shadow(screen, "NASTAVENI", font_big, YELLOW, WIDTH//2 - 135, 95)
            for i, k in enumerate(OBTIZNOSTI.keys()):
                cfg2 = OBTIZNOSTI[k]; sel = (k == vybrana_obtiznost); px = 40 + i * 135
                kresli_panel(screen, px, 250, 120, 140, 200 if sel else 100)
                if sel: pygame.draw.rect(screen, cfg2['color'], (px, 250, 120, 140), 3)
                screen.blit(font_mid.render(cfg2['label'], True, cfg2['color']), (px + 10, 265))
                if sel: screen.blit(font_sml.render("X", True, cfg2['color']), (px + 95, 260))

        elif stav == "ZEBRICEK":
            text_shadow(screen, "ZEBRICEK", font_big, YELLOW, WIDTH//2 - 130, 60)
            data = nacti_skore()
            kresli_panel(screen, 30, 150, WIDTH - 60, 440, 140)
            if not data: screen.blit(font_sml.render("Zadné záznamy", True, WHITE), (WIDTH//2 - 80, 330))
            else:
                for i, z in enumerate(data[:8]):
                    ry = 195 + i * 48
                    col = [(255,215,0),(192,192,192),(205,127,50),(220,220,220)][min(i,3)]
                    screen.blit(font_sml.render(f"{i+1}.", True, col), (50, ry))
                    screen.blit(font_sml.render(z['name'][:10], True, WHITE), (100, ry))
                    text_shadow(screen, str(z['score']), font_mid, YELLOW, 310, ry-2)

        elif stav == "ODPOCET":
            elapsed = (pygame.time.get_ticks() - odpocet_timer) / 1000.0
            cislo = max(1, 3 - int(elapsed))
            if elapsed < 3.0: text_shadow(screen, str(cislo), font_big, WHITE, WIDTH//2 - 20, HEIGHT//2 - 60)

        elif stav == "HRANI":
            text_shadow(screen, str(skore), font_big, WHITE, WIDTH//2 - 20, 30)

        elif stav == "ZADAVANI":
            kresli_panel(screen, WIDTH//2 - 190, HEIGHT//2 - 120, 380, 240, 200)
            text_shadow(screen, "KONEC HRY", font_mid, ORANGE, WIDTH//2 - 100, HEIGHT//2 - 110)
            pygame.draw.rect(screen, YELLOW, (WIDTH//2 - 130, HEIGHT//2, 260, 42), 2)
            screen.blit(font_mid.render(jmeno + "_", True, WHITE), (WIDTH//2 - 120, HEIGHT//2 + 6))
            if chyba_jmeno: screen.blit(font_xs.render(chyba_jmeno, True, (255,80,80)), (WIDTH//2 - 140, HEIGHT//2 + 52))

        elif stav == "GAME_OVER":
            kresli_panel(screen, WIDTH//2 - 190, HEIGHT//2 - 160, 380, 320, 210)
            text_shadow(screen, "HOTOVO!", font_big, YELLOW, WIDTH//2 - 110, HEIGHT//2 - 150)
            screen.blit(font_sml.render("Ulozeno!", True, (100,255,100)), (WIDTH//2 - 40, HEIGHT//2 - 10))

        pygame.display.flip()

if __name__ == "__main__":
    inicializuj_db()
    spust_hru()