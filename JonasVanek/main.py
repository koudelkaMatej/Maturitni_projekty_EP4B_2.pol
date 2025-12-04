import pygame
import random
import sys
import json
import urllib.request
import urllib.error
import urllib.parse

pygame.init()
WIDTH, HEIGHT = 600, 800
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Flappy Palach")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

FONT = pygame.font.SysFont("Arial", 40)
SMALL_FONT = pygame.font.SysFont("Arial", 28)

## fyzika
gravity = 0.5
jump_strength = -10
clock = pygame.time.Clock()

## cesta k adresari s obrazky
IMG_DIR = "img/"

## assety (všechny obrázky se načítají z IMG_DIR)
# pozadí
bg_img = pygame.image.load(IMG_DIR + "pozadi.png").convert()
bg_img = pygame.transform.scale(bg_img, (WIDTH, HEIGHT))

# --- načtení 3 snímků ptáčka pro animaci mávání (z img/) ---
bird_frame_files = [IMG_DIR + "bird1.png", IMG_DIR + "bird2.png", IMG_DIR + "bird3.png"]
bird_frames = []
BIRD_SIZE = (50, 50)
for fname in bird_frame_files:
    img = pygame.image.load(fname).convert_alpha()
    img = pygame.transform.scale(img, BIRD_SIZE)
    bird_frames.append(img)

# index neutrálního snímku (když pták není v animaci)
NEUTRAL_FRAME_IDX = 1

# animace mávnutí
bird_frame_index = NEUTRAL_FRAME_IDX
FLAP_DURATION_MS = 240
FLAP_FRAME_INTERVAL_MS = 80
flap_timer = 0
flap_frame_timer = 0
flap_active = False

# trubka
pipe_img = pygame.image.load(IMG_DIR + "palachvez.png").convert_alpha()
PIPE_WIDTH = 80
pipe_img = pygame.transform.scale(pipe_img, (PIPE_WIDTH, 500))
pipe_img_flipped = pygame.transform.flip(pipe_img, False, True)

# načtení game over obrázku (z img/)
try:
    gameover_img = pygame.image.load(IMG_DIR + "gameover.png").convert_alpha()
    gameover_img = pygame.transform.smoothscale(gameover_img, (min(500, WIDTH - 40), 140))
except Exception:
    gameover_img = FONT.render("Game Over!", True, BLACK)

# načtení obrázků číslic 0-9 z img/; pokud chybí, fallback na renderovanou číslici
digit_images = {}
DIGIT_BASE_HEIGHT = 80  # výchozí výška pro obrazky, můžeme je zmenšit při vykreslování HUD
for d in range(0, 10):
    fname = f"{IMG_DIR}{d}.png"
    key = str(d)
    try:
        img = pygame.image.load(fname).convert_alpha()
        iw, ih = img.get_size()
        scale = DIGIT_BASE_HEIGHT / ih
        img = pygame.transform.smoothscale(img, (int(iw * scale), DIGIT_BASE_HEIGHT))
        digit_images[key] = img
    except Exception:
        surf = FONT.render(key, True, BLACK)
        if surf.get_height() < DIGIT_BASE_HEIGHT:
            bg = pygame.Surface((surf.get_width() + 20, DIGIT_BASE_HEIGHT), pygame.SRCALPHA)
            bg.fill((255, 255, 255, 0))
            bg.blit(surf, (10, (DIGIT_BASE_HEIGHT - surf.get_height()) // 2))
            digit_images[key] = bg
        else:
            digit_images[key] = surf

## profily obtiznosti (klice bez diakritiky)
DIFFICULTY_PROFILES = {
    "lehka": {
        "label": "Lehká",
        "speed_inc": 0.0,
        "gap_dec": 0,
        "score_step": 3
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

## pomocne
def wait_for_mouse_release():
    ## vyckani na uvolneni tlacitka mysi
    pygame.event.clear()
    while any(pygame.mouse.get_pressed()):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
        clock.tick(60)


def _draw_vertical_gradient(surf, rect, top_color, bottom_color, radius):
    x, y, w, h = rect
    gradient = pygame.Surface((w, h), pygame.SRCALPHA)
    for i in range(h):
        t = i / max(1, h - 1)
        r = int(top_color[0] + (bottom_color[0] - top_color[0]) * t)
        g = int(top_color[1] + (bottom_color[1] - top_color[1]) * t)
        b = int(top_color[2] + (bottom_color[2] - top_color[2]) * t)
        a = int(top_color[3] + (bottom_color[3] - top_color[3]) * t)
        pygame.draw.line(gradient, (r, g, b, a), (0, i), (w, i))
    mask = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255), (0, 0, w, h), border_radius=radius)
    gradient.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(gradient, (x, y))


def _render_text_fit(text, max_w, max_h, base_size=28, min_size=14):
    size = base_size
    while size >= min_size:
        font = pygame.font.SysFont("Arial", size)
        ts = font.render(text, True, BLACK)
        tw, th = ts.get_size()
        if tw <= max_w and th <= max_h:
            return ts, font
        size -= 1
    font = pygame.font.SysFont("Arial", min_size)
    text_trim = text
    ts = font.render(text_trim, True, BLACK)
    while ts.get_width() > max_w and len(text_trim) > 3:
        text_trim = text_trim[:-1]
        ts = font.render(text_trim + "...", True, BLACK)
    return ts, font


def draw_button(text, center_x, y, w, h, alpha=255):
    padding_x, padding_y = 20, 12
    min_w, min_h = 160, 56
    w_eff = max(w, min_w)
    h_eff = max(h, min_h)

    max_button_w = min(WIDTH - 40, 460)

    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()
    rect = pygame.Rect(center_x - w_eff // 2, y, w_eff, h_eff)
    hovered = rect.collidepoint(mouse)

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

    shadow = pygame.Surface((w_eff + 8, h_eff + 8), pygame.SRCALPHA)
    pygame.draw.rect(shadow, (0, 0, 0, shadow_alpha), shadow.get_rect(), border_radius=radius + 2)
    WIN.blit(shadow, (center_x - (w_eff // 2) + 2, y + 4))

    _draw_vertical_gradient(WIN, rect, top, bottom, radius)
    pygame.draw.rect(WIN, border, rect, width=3, border_radius=radius)

    WIN.blit(ts, (rect.centerx - tw // 2, rect.centery - th // 2))

    if hovered and click[0]:
        pygame.time.wait(180)
        return True
    return False


def draw_text_center(text, font, color, y_offset=0):
    text_surface = font.render(text, True, color)
    rect = text_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2 + y_offset))
    WIN.blit(text_surface, rect)


def sanitize_name(s: str) -> str:
    s = s.strip()
    s = "".join(ch for ch in s if ch.isprintable() and ch not in "\n\r\t")
    return s


## obrazovky
def name_input_screen():
    name = ""
    cursor_show = True
    cursor_timer = 0
    wait_for_mouse_release()
    while True:
        dt = clock.tick(60)
        WIN.blit(bg_img, (0, 0))
        draw_text_center("Zadej své jméno", FONT, BLACK, -120)
        hint = SMALL_FONT.render("Enter = potvrdit, Backspace = smazat", True, BLACK)
        WIN.blit(hint, (WIDTH // 2 - hint.get_width() // 2, HEIGHT // 2 + 20))

        display = name if len(name) > 0 else ""
        cursor_timer += dt
        if cursor_timer > 500:
            cursor_show = not cursor_show
            cursor_timer = 0
        if cursor_show:
            display += "|"

        input_surf = SMALL_FONT.render(display, True, BLACK)
        rect = input_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 30))
        pygame.draw.rect(WIN, (220, 220, 220), rect.inflate(20, 14), border_radius=8)
        pygame.draw.rect(WIN, BLACK, rect.inflate(20, 14), width=2, border_radius=8)
        WIN.blit(input_surf, rect)

        if draw_button("Potvrdit", WIDTH // 2, HEIGHT // 2 + 70, 200, 60):
            candidate = sanitize_name(name)
            if 1 <= len(candidate) <= 30:
                wait_for_mouse_release()
                return candidate

        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    candidate = sanitize_name(name)
                    if 1 <= len(candidate) <= 30:
                        return candidate
                elif event.key == pygame.K_BACKSPACE:
                    name = name[:-1]
                else:
                    ch = event.unicode
                    if ch and ch.isprintable() and ch not in "\n\r\t":
                        if len(name) < 30:
                            name += ch


def difficulty_screen(current_key="stredni"):
    wait_for_mouse_release()
    keys = ["lehka", "stredni", "tezka"]
    current_idx = keys.index(current_key) if current_key in keys else 1

    while True:
        clock.tick(60)
        WIN.blit(bg_img, (0, 0))
        draw_text_center("Vyber obtížnost", FONT, BLACK, -160)

        y0 = HEIGHT // 2 - 40
        h = 60
        w = 280
        labels = [DIFFICULTY_PROFILES[k]["label"] for k in keys]

        for i, label in enumerate(labels):
            y = y0 + i * 80
            if draw_button(label, WIDTH // 2, y, w, h):
                wait_for_mouse_release()
                return keys[i]

        if draw_button("Zpět", WIDTH // 2, HEIGHT // 2 + 210, 200, 60):
            wait_for_mouse_release()
            return keys[current_idx]

        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()


def menu_screen(show_change_name=True, show_change_difficulty=True, difficulty_key="stredni"):
    alpha = 0
    wait_for_mouse_release()
    while True:
        clock.tick(60)
        WIN.blit(bg_img, (0, 0))
        draw_text_center("Flappy Palach", FONT, BLACK, -200)

        diff_label = DIFFICULTY_PROFILES.get(difficulty_key, DIFFICULTY_PROFILES["stredni"])["label"]
        info = SMALL_FONT.render(f"Aktuální obtížnost: {diff_label}", True, BLACK)
        WIN.blit(info, (WIDTH // 2 - info.get_width() // 2, HEIGHT // 2 - 90))

        if alpha < 255:
            alpha += 5

        if draw_button("Start", WIDTH // 2, HEIGHT // 2 - 30, 220, 60, alpha):
            wait_for_mouse_release()
            return "start"

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

        if draw_button("Ukončit", WIDTH // 2, y, 220, 60, alpha):
            pygame.quit(); sys.exit()

        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()


def pause_menu():
    wait_for_mouse_release()
    while True:
        clock.tick(60)
        WIN.blit(bg_img, (0, 0))
        draw_text_center("PAUZA", FONT, BLACK, -150)
        if draw_button("Pokračovat", WIDTH // 2, HEIGHT // 2 - 30, 240, 60):
            wait_for_mouse_release()
            return
        if draw_button("Ukončit", WIDTH // 2, HEIGHT // 2 + 60, 220, 60):
            pygame.quit(); sys.exit()
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()


def submit_score(player_name, score):
    try:
        safe_name = sanitize_name(player_name)[:30] if player_name else "Neznámý"
        data = urllib.parse.urlencode({
            "name": safe_name,
            "score": int(score)
        }).encode("utf-8")

        req = urllib.request.Request(
            data=data,
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
                "User-Agent": "FlappyPalach/1.0"
            },
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            _ = resp.read()
    except Exception as e:
        print("Submit score failed:", e)


def dead_screen(score, player_name):
    """
    Obrazovka po prohre:
    - vykreslí obrázek gameover_img (pokud existuje)
    - místo textového skóre vykreslí sekvenci obrázků číslic (0-9)
    - nabídne tlačítka: Hrát znovu, Zpět do menu, Ukončit
    """
    submit_score(player_name, score)
    wait_for_mouse_release()

    while True:
        clock.tick(60)
        WIN.blit(bg_img, (0, 0))

        # vykresli gameover obrázek (je centrován)
        if isinstance(gameover_img, pygame.Surface):
            go_rect = gameover_img.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 140))
            WIN.blit(gameover_img, go_rect)
        else:
            draw_text_center("Game Over!", FONT, BLACK, -170)

        # vykreslení skóre pomocí obrázků číslic
        score_str = str(int(score))
        digit_surfaces = []
        total_w = 0
        max_h = 0
        for ch in score_str:
            surf = digit_images.get(ch)
            if surf is None:
                surf = FONT.render(ch, True, BLACK)
            digit_surfaces.append(surf)
            total_w += surf.get_width()
            if surf.get_height() > max_h:
                max_h = surf.get_height()

        # mezera mezi ciframi
        spacing = 8
        total_w += spacing * (len(digit_surfaces) - 1) if len(digit_surfaces) > 1 else 0

        # pozice - vystředěno horizontálně, umístěno trochu pod Game Over
        start_x = WIDTH // 2 - total_w // 2
        y_pos = HEIGHT // 2 - 40

        x = start_x
        for surf in digit_surfaces:
            # vertikální centrování podle max_h
            y_off = y_pos + (max_h - surf.get_height()) // 2
            WIN.blit(surf, (x, y_off))
            x += surf.get_width() + spacing

        # tlacitka
        if draw_button("Hrát znovu", WIDTH // 2, HEIGHT // 2 + 60, 240, 60):
            wait_for_mouse_release()
            return "restart"
        if draw_button("Zpět do menu", WIDTH // 2, HEIGHT // 2 + 140, 260, 60):
            wait_for_mouse_release()
            return "menu"
        if draw_button("Ukončit", WIDTH // 2, HEIGHT // 2 + 220, 220, 60):
            pygame.quit(); sys.exit()

        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()


def render_score_with_images(score, top_left_x, top_left_y, target_height=40, spacing=6):
    """
    Vykreslí celé skóre jako posloupnost obrázků číslic.
    - pokud chybí obrázek pro cifru, použije fallback z digit_images (který může být textový).
    - target_height určuje výšku každé cifry (upraví se proporčně).
    """
    score_str = str(int(score))
    # připravíme povrchy (přeskálované na target_height)
    surfaces = []
    total_w = 0
    max_h = 0
    for ch in score_str:
        base = digit_images.get(ch)
        if base is None:
            base = FONT.render(ch, True, BLACK)
        # přepočet škálování - zachovat poměr stran
        bw, bh = base.get_size()
        scale = target_height / bh
        new_w = max(1, int(bw * scale))
        surf = pygame.transform.smoothscale(base, (new_w, target_height))
        surfaces.append(surf)
        total_w += surf.get_width()
        if surf.get_height() > max_h:
            max_h = surf.get_height()
    total_w += spacing * (len(surfaces) - 1) if len(surfaces) > 1 else 0

    # vykreslení - vystředěno vertikálně podle target_height
    x = top_left_x
    for surf in surfaces:
        WIN.blit(surf, (x, top_left_y + (max_h - surf.get_height()) // 2))
        x += surf.get_width() + spacing


def check_collision(bird_rect, pipe_x, pipe_height, gap):
    top_rect = pygame.Rect(pipe_x, 0, PIPE_WIDTH, pipe_height)
    bottom_rect = pygame.Rect(pipe_x, pipe_height + gap, PIPE_WIDTH, HEIGHT)
    if bird_rect.colliderect(top_rect) or bird_rect.colliderect(bottom_rect):
        return True
    if bird_rect.top < 0 or bird_rect.bottom > HEIGHT:
        return True
    return False


def draw_game(bird_image_rotated, bird_rect, pipe_x, pipe_height, score, player_name, gap, pipe_speed, difficulty_key):
    """
    Hlavní vykreslovací funkce:
    - odstraněn text 'Skóre: {score}'
    - místo něj vykreslíme obrázky číslic (render_score_with_images) v levém horním rohu
    - ostatní HUD prvky zůstanou
    """
    WIN.blit(bg_img, (0, 0))

    # vykreslit rotovaný snímek ptáčka
    WIN.blit(bird_image_rotated, bird_rect)

    # trubky
    top_pipe = pygame.transform.scale(pipe_img_flipped, (PIPE_WIDTH, max(1, pipe_height)))
    bottom_height = max(1, HEIGHT - pipe_height - gap)
    bottom_pipe = pygame.transform.scale(pipe_img, (PIPE_WIDTH, bottom_height))

    WIN.blit(top_pipe, (pipe_x, 0))
    WIN.blit(bottom_pipe, (pipe_x, pipe_height + gap))

    # HUD: místo textového skóre vykreslíme obrazy číslic
    HUD_X = 10
    HUD_Y = 10
    HUD_DIGIT_HEIGHT = 36  # výška číslic v HUD
    render_score_with_images(score, HUD_X, HUD_Y, target_height=HUD_DIGIT_HEIGHT, spacing=6)

    # jméno hráče a ostatní HUD (zůstávají)
    name_s = SMALL_FONT.render(f"Hráč: {player_name}", True, BLACK)
    WIN.blit(name_s, (10, 60))

    diff_label = DIFFICULTY_PROFILES.get(difficulty_key, DIFFICULTY_PROFILES["stredni"])["label"]
    diff = SMALL_FONT.render(f"Obtížnost: {diff_label}", True, BLACK)
    WIN.blit(diff, (10, 100))

    speed_gap = SMALL_FONT.render(f"Rychlost: {pipe_speed:.1f}   Mezera: {gap}px", True, BLACK)
    WIN.blit(speed_gap, (10, 140))

    pygame.display.update()


def main_game(player_name, difficulty_key):
    global flap_active, flap_timer, flap_frame_timer, bird_frame_index

    bird_y = HEIGHT // 2
    bird_velocity = 0

    pipe_x = WIDTH
    pipe_height = random.randint(100, 500)

    pipe_speed = 4.0
    GAP = 180
    MIN_GAP = 120

    profile = DIFFICULTY_PROFILES.get(difficulty_key, DIFFICULTY_PROFILES["stredni"])
    SCORE_STEP = profile["score_step"]
    SPEED_INC = profile["speed_inc"]
    GAP_DEC = profile["gap_dec"]

    score = 0

    # rotace: parametry
    ROTATION_FACTOR = 3.0
    MAX_UP_ANGLE = -40
    MAX_DOWN_ANGLE = 60

    bird_frame_index = NEUTRAL_FRAME_IDX
    flap_active = False
    flap_timer = 0
    flap_frame_timer = 0

    while True:
        dt = clock.tick(60)

        # fyzika
        bird_velocity += gravity
        bird_y += bird_velocity

        # trubky
        pipe_x -= pipe_speed

        if pipe_x + PIPE_WIDTH < 0:
            pipe_x = WIDTH
            pipe_height = random.randint(100, 500)
            score += 1

            if SCORE_STEP > 0 and (score % SCORE_STEP == 0):
                pipe_speed += SPEED_INC
                GAP = max(MIN_GAP, GAP - GAP_DEC)

        # animace mávnutí
        if flap_active:
            flap_timer += dt
            flap_frame_timer += dt
            if flap_frame_timer >= FLAP_FRAME_INTERVAL_MS:
                flap_frame_timer = 0
                bird_frame_index = (bird_frame_index + 1) % len(bird_frames)
            if flap_timer >= FLAP_DURATION_MS:
                flap_active = False
                flap_timer = 0
                flap_frame_timer = 0
                bird_frame_index = NEUTRAL_FRAME_IDX
        else:
            bird_frame_index = NEUTRAL_FRAME_IDX

        # vyber aktuálního snímku (neotoceno)
        current_bird_img = bird_frames[bird_frame_index]

        # spočítat úhel podle rychlosti
        angle = -bird_velocity * ROTATION_FACTOR
        if angle < MAX_UP_ANGLE:
            angle = MAX_UP_ANGLE
        if angle > MAX_DOWN_ANGLE:
            angle = MAX_DOWN_ANGLE

        # rotovat obrazek kolem středu
        bird_image_rotated = pygame.transform.rotate(current_bird_img, angle)
        bird_rect = bird_image_rotated.get_rect(center=(150, int(bird_y)))

        # události
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    bird_velocity = jump_strength
                    # animace mávnutí
                    flap_active = True
                    flap_timer = 0
                    flap_frame_timer = 0
                    bird_frame_index = 0
                elif event.key == pygame.K_ESCAPE:
                    pause_menu()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    bird_velocity = jump_strength
                    flap_active = True
                    flap_timer = 0
                    flap_frame_timer = 0
                    bird_frame_index = 0

        # kontrola kolize (používáme rect rotovaného obrázku)
        if check_collision(bird_rect, pipe_x, pipe_height, GAP):
            choice = dead_screen(score, player_name)
            if choice == "restart":
                return "restart"
            else:
                return "menu"

        draw_game(bird_image_rotated, bird_rect, pipe_x, pipe_height, score, player_name, GAP, pipe_speed, difficulty_key)


def main():
    player_name = name_input_screen()
    difficulty_key = difficulty_screen(current_key="stredni")

    while True:
        action = menu_screen(show_change_name=True, show_change_difficulty=True, difficulty_key=difficulty_key)

        if action == "start":
            while True:
                result = main_game(player_name, difficulty_key)
                if result == "restart":
                    wait_for_mouse_release()
                    continue
                else:
                    wait_for_mouse_release()
                    break

        elif action == "change_name":
            player_name = name_input_screen()

        elif action == "change_difficulty":
            difficulty_key = difficulty_screen(current_key=difficulty_key)

        else:
            pygame.quit(); sys.exit()


if __name__ == "__main__":
    main()
