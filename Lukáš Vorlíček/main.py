import pygame
import random
import settings
import database
from game_elements import Button, Piece

# Inicializace Pygame a fontů
pygame.init()


def draw_text(win, text, font, color, x, y, shadow=True):
    """Pomocná funkce pro vykreslení textu se stínem pro lepší čitelnost."""
    if shadow:
        shadow_surf = font.render(text, True, (0, 0, 0))
        win.blit(shadow_surf, shadow_surf.get_rect(center=(x + 2, y + 2)))
    surf = font.render(text, True, color)
    win.blit(surf, surf.get_rect(center=(x, y)))


class Bag:
    """Implementace 7-Bag systému pro férové generování kostek."""

    def __init__(self):
        self.content = []

    def get_piece(self, grid):
        if not self.content:
            self.content = list(range(len(settings.SHAPES)))
            random.shuffle(self.content)
        return Piece(grid, self.content.pop())


def load_bg(win):
    """Načte a přeškáluje pozadí podle aktuální velikosti okna."""
    try:
        img = pygame.image.load("static/background.png").convert()
        return pygame.transform.scale(img, (win.get_width(), win.get_height()))
    except Exception as e:
        print(f"Chyba při načítání pozadí: {e}")
        fallback = pygame.Surface((win.get_width(), win.get_height()))
        fallback.fill((10, 10, 10))
        return fallback


# --- HERNÍ OBRAZOVKY (STAVY) ---

def auth_screen(win, bg_img):
    """Obrazovka pro přihlášení a registraci."""
    f_title = pygame.font.SysFont("Arial", 32, bold=True)
    f_ui = pygame.font.SysFont("Arial", 20)
    u, p, field, mode, err = "", "", "u", "LOGIN", ""
    cx = win.get_width() // 2

    u_box = pygame.Rect(cx - 100, 180, 200, 40)
    p_box = pygame.Rect(cx - 100, 240, 200, 40)

    
    pygame.key.set_repeat(0)

    while True:
        win.blit(bg_img, (0, 0))
        overlay = pygame.Surface((win.get_width(), win.get_height()), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 210))  # Tmavší překryv pro formulář
        win.blit(overlay, (0, 0))

        draw_text(win, mode, f_title, settings.PRIMARY, cx, 100)

        # Vykreslení vstupních polí
        pygame.draw.rect(win, settings.PRIMARY if field == "u" else (60, 60, 60), u_box, 2, border_radius=5)
        draw_text(win, u if u else "Uživatel...", f_ui, (150, 150, 150), cx, 200)

        pygame.draw.rect(win, settings.PRIMARY if field == "p" else (60, 60, 60), p_box, 2, border_radius=5)
        draw_text(win, "*" * len(p) if p else "Heslo...", f_ui, (150, 150, 150), cx, 260)

        sub_btn = Button(cx - 100, 320, 200, 45, "POTVRDIT", f_ui, settings.SECONDARY)
        mod_btn = Button(cx - 100, 380, 200, 40, "PŘEPNOUT", f_ui, (120, 120, 120))

        for b in [sub_btn, mod_btn]: b.draw(win)
        if err: draw_text(win, err, f_ui, settings.ACCENT, cx, 305)

        for e in pygame.event.get():
            if e.type == pygame.QUIT: return None

            if e.type == pygame.MOUSEBUTTONDOWN:
                if u_box.collidepoint(e.pos): field = "u"
                if p_box.collidepoint(e.pos): field = "p"

            if sub_btn.is_clicked(e) or (e.type == pygame.KEYDOWN and e.key == pygame.K_RETURN):
                if not u or not p:
                    err = "Vyplňte všechna pole!"
                    continue
                if mode == "LOGIN":
                    uid = database.login_user(u, p)
                    if uid: return (uid, u)
                    err = "Chybné jméno nebo heslo!"
                else:
                    if database.register_user(u, p):
                        mode = "LOGIN"
                        err = "Registrace úspěšná!"
                    else:
                        err = "Uživatel již existuje!"

            if mod_btn.is_clicked(e):
                mode = "REGISTRACE" if mode == "LOGIN" else "LOGIN"
                err = ""

            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_BACKSPACE:
                    if field == "u":
                        u = u[:-1]
                    else:
                        p = p[:-1]
                elif e.key == pygame.K_TAB:
                    field = "p" if field == "u" else "u"
                elif e.unicode.isprintable() and e.key != pygame.K_RETURN:
                    if field == "u":
                        u += e.unicode
                    else:
                        p += e.unicode

        pygame.display.update()


def settings_menu(win, bg_img):
    """Menu pro výběr rozlišení."""
    f_title = pygame.font.SysFont("Arial", 30, bold=True)
    f_ui = pygame.font.SysFont("Arial", 18)
    cx = win.get_width() // 2

    while True:
        win.blit(bg_img, (0, 0))
        overlay = pygame.Surface((win.get_width(), win.get_height()), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        win.blit(overlay, (0, 0))

        draw_text(win, "NASTAVENÍ VELIKOSTI", f_title, settings.PRIMARY, cx, 100)

        btn_s = Button(cx - 100, 180, 200, 45, "MALÉ (300x600)", f_ui, settings.PRIMARY)
        btn_m = Button(cx - 100, 240, 200, 45, "STŘEDNÍ (400x800)", f_ui, settings.SECONDARY)
        btn_l = Button(cx - 100, 300, 200, 45, "VELKÉ (500x1000)", f_ui, settings.ACCENT)
        btn_back = Button(cx - 100, 400, 200, 45, "ZPĚT", f_ui, (150, 150, 150))

        for b in [btn_s, btn_m, btn_l, btn_back]: b.draw(win)

        for e in pygame.event.get():
            if e.type == pygame.QUIT: return "QUIT"
            if btn_s.is_clicked(e): return 30
            if btn_m.is_clicked(e): return 40
            if btn_l.is_clicked(e): return 50
            if btn_back.is_clicked(e): return "BACK"

        pygame.display.update()


def start_menu(win, bg_img, uname):
    """Hlavní rozcestník po přihlášení."""
    f_title = pygame.font.SysFont("Arial", 36, bold=True)
    f_ui = pygame.font.SysFont("Arial", 24)
    cx = win.get_width() // 2
    while True:
        win.blit(bg_img, (0, 0))
        overlay = pygame.Surface((win.get_width(), win.get_height()), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        win.blit(overlay, (0, 0))

        draw_text(win, "NEON TETRIS 2026", f_title, settings.PRIMARY, cx, 120)
        draw_text(win, f"Hráč: {uname}", f_ui, (255, 255, 255), cx, 180)

        play_btn = Button(cx - 90, 250, 180, 50, "HRÁT", f_ui, settings.SECONDARY)
        set_btn = Button(cx - 90, 320, 180, 50, "NASTAVENÍ", f_ui, (100, 100, 100))
        logout_btn = Button(cx - 90, 390, 180, 50, "ODHLÁSIT", f_ui, settings.ACCENT)

        for b in [play_btn, set_btn, logout_btn]: b.draw(win)

        for e in pygame.event.get():
            if e.type == pygame.QUIT: return "QUIT"
            if play_btn.is_clicked(e): return "PLAY"
            if set_btn.is_clicked(e): return "SETTINGS"
            if logout_btn.is_clicked(e): return "LOGOUT"

        pygame.display.update()


def game_over_screen(win, bg_img, score):
    """Obrazovka po skončení hry."""
    f_title = pygame.font.SysFont("Arial", 40, bold=True)
    f_ui = pygame.font.SysFont("Arial", 24)
    cx = win.get_width() // 2
    while True:
        win.blit(bg_img, (0, 0))
        overlay = pygame.Surface((win.get_width(), win.get_height()), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        win.blit(overlay, (0, 0))

        draw_text(win, "GAME OVER", f_title, settings.ACCENT, cx, 150)
        draw_text(win, f"KONEČNÉ SKÓRE: {score}", f_ui, (255, 255, 255), cx, 220)

        again_btn = Button(cx - 90, 320, 180, 50, "HRÁT ZNOVU", f_ui, settings.PRIMARY)
        menu_btn = Button(cx - 90, 390, 180, 50, "HLAVNÍ MENU", f_ui, settings.SECONDARY)

        for b in [again_btn, menu_btn]: b.draw(win)

        for e in pygame.event.get():
            if e.type == pygame.QUIT: return "QUIT"
            if again_btn.is_clicked(e): return "PLAY"
            if menu_btn.is_clicked(e): return "MENU"

        pygame.display.update()


# --- HLAVNÍ LOGIKA ---

def main():
    database.init_db()
    win = pygame.display.set_mode((settings.WIDTH, settings.HEIGHT))
    pygame.display.set_caption("Neon Tetris 2026")

    bg_img = load_bg(win)

    while True:  # Smyčka celé aplikace
        auth = auth_screen(win, bg_img)
        if not auth: break
        uid, uname = auth

        run_app = True
        while run_app:  # Smyčka po přihlášení
            choice = start_menu(win, bg_img, uname)

            if choice == "SETTINGS":
                res = settings_menu(win, bg_img)
                if isinstance(res, int):
                    settings.BLOCK_SIZE = res
                    settings.WIDTH = settings.COLUMNS * res
                    settings.HEIGHT = settings.ROWS * res
                    win = pygame.display.set_mode((settings.WIDTH, settings.HEIGHT))
                    bg_img = load_bg(win)
                continue

            if choice == "LOGOUT": break
            if choice == "QUIT": return

            playing = True
            while playing:  # Smyčka samotného hraní
                # Zapnutí DAS systému (Delayed Auto Shift)
                pygame.key.set_repeat(200, 50)

                grid = [[0 for _ in range(settings.COLUMNS)] for _ in range(settings.ROWS)]
                score, lvl, fall_time, clock = 0, 1, 0, pygame.time.Clock()

                tetris_bag = Bag()
                piece = tetris_bag.get_piece(grid)

                game_active = True
                while game_active:
                    # Výpočet rychlosti pádu podle levelu
                    fall_speed = max(100, 1000 // (lvl + 2))
                    fall_time += clock.get_rawtime()
                    clock.tick()

                    for e in pygame.event.get():
                        if e.type == pygame.QUIT: pygame.quit(); return
                        if e.type == pygame.KEYDOWN:
                            if e.key == pygame.K_LEFT and piece.valid(dx=-1): piece.x -= 1
                            if e.key == pygame.K_RIGHT and piece.valid(dx=1): piece.x += 1
                            if e.key == pygame.K_DOWN and piece.valid(dy=1): piece.y += 1
                            if e.key == pygame.K_UP: piece.rotate()
                            if e.key == pygame.K_SPACE:  # Hard Drop
                                while piece.valid(dy=1): piece.y += 1

                    # Logika volného pádu
                    if fall_time >= fall_speed:
                        if piece.valid(dy=1):
                            piece.y += 1
                        else:
                            piece.place()
                            # Detekce a mazání řad
                            full_rows = [i for i, r in enumerate(grid) if all(c != 0 for c in r)]
                            if full_rows:
                                for i in full_rows:
                                    del grid[i]
                                    grid.insert(0, [0 for _ in range(settings.COLUMNS)])

                                # Nelineární bodování
                                cleared = len(full_rows)
                                mult = {1: 100, 2: 300, 3: 700, 4: 1500}
                                score += mult.get(cleared, 0) * lvl

                                lvl = score // settings.LEVEL_UP_SCORE + 1

                            piece = tetris_bag.get_piece(grid)
                            if not piece.valid():  # Game Over
                                database.save_score(uid, uname, score, lvl)
                                game_active = False
                        fall_time = 0

                    # --- VYKRESLOVÁNÍ ---
                    win.blit(bg_img, (0, 0))

                    # Mřížka a položené bloky
                    for y in range(settings.ROWS):
                        for x in range(settings.COLUMNS):
                            rect = (x * settings.BLOCK_SIZE, y * settings.BLOCK_SIZE,
                                    settings.BLOCK_SIZE, settings.BLOCK_SIZE)
                            if grid[y][x]:
                                pygame.draw.rect(win, grid[y][x], rect)
                            pygame.draw.rect(win, (50, 50, 50), rect, 1)

                    # Aktivní kostka s obrysem
                    for y, row in enumerate(piece.shape):
                        for x, cell in enumerate(row):
                            if cell:
                                rect = ((piece.x + x) * settings.BLOCK_SIZE,
                                        (piece.y + y) * settings.BLOCK_SIZE,
                                        settings.BLOCK_SIZE, settings.BLOCK_SIZE)
                                pygame.draw.rect(win, piece.color, rect)
                                pygame.draw.rect(win, (255, 255, 255), rect, 1)

                    # Horní UI lišta (průhledná)
                    ui_bar = pygame.Surface((win.get_width(), 50), pygame.SRCALPHA)
                    ui_bar.fill((0, 0, 0, 150))
                    win.blit(ui_bar, (0, 0))

                    f_stats = pygame.font.SysFont("Arial", 16, bold=True)
                    draw_text(win, f"HRÁČ: {uname}", f_stats, settings.PRIMARY, win.get_width() // 2, 15)
                    draw_text(win, f"SKÓRE: {score} | LEVEL: {lvl}", f_stats, (255, 255, 255), win.get_width() // 2, 35)

                    pygame.display.update()

                # Stavy po skončení hry
                res = game_over_screen(win, bg_img, score)
                if res == "MENU": playing = False
                if res == "QUIT": return


if __name__ == "__main__":
    main()
