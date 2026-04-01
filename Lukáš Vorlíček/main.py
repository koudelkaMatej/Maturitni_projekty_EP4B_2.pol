import pygame
import random
import settings
import database
from game_elements import Button, Piece

pygame.init()

def draw_text(win, text, font, color, x, y, shadow=True):
    if shadow:
        shadow_surf = font.render(text, True, (0, 0, 0))
        win.blit(shadow_surf, shadow_surf.get_rect(center=(x + 2, y + 2)))
    surf = font.render(text, True, color)
    win.blit(surf, surf.get_rect(center=(x, y)))

class Bag:
    def __init__(self):
        self.content = []

    def get_piece(self, grid):
        if not self.content:
            self.content = list(range(len(settings.SHAPES)))
            random.shuffle(self.content)
        return Piece(grid, self.content.pop())

def load_bg(win):
    try:
        img = pygame.image.load("static/background.png").convert()
        return pygame.transform.scale(img, (win.get_width(), win.get_height()))
    except Exception:
        fallback = pygame.Surface((win.get_width(), win.get_height()))
        fallback.fill((10, 10, 10))
        return fallback

def auth_screen(win, bg_img):
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
        overlay.fill((0, 0, 0, 210))
        win.blit(overlay, (0, 0))
        draw_text(win, mode, f_title, settings.PRIMARY, cx, 100)
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
                    err = "Vyplňte pole!"
                    continue
                if mode == "LOGIN":
                    uid = database.login_user(u, p)
                    if uid: return (uid, u)
                    err = "Chybné údaje!"
                else:
                    if database.register_user(u, p): mode, err = "LOGIN", "Registrace OK!"
                    else: err = "Uživatel existuje!"
            if mod_btn.is_clicked(e): mode, err = ("REGISTRACE" if mode == "LOGIN" else "LOGIN"), ""
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_BACKSPACE:
                    if field == "u": u = u[:-1]
                    else: p = p[:-1]
                elif e.key == pygame.K_TAB: field = "p" if field == "u" else "u"
                elif e.unicode.isprintable() and e.key != pygame.K_RETURN:
                    if field == "u": u += e.unicode
                    else: p += e.unicode
        pygame.display.update()

def start_menu(win, bg_img, uname):
    f_title = pygame.font.SysFont("Arial", 36, bold=True)
    f_ui = pygame.font.SysFont("Arial", 24)
    cx = win.get_width() // 2
    while True:
        win.blit(bg_img, (0, 0))
        draw_text(win, "NEON TETRIS 2026", f_title, settings.PRIMARY, cx, 120)
        draw_text(win, f"Hráč: {uname}", f_ui, (255, 255, 255), cx, 180)
        play_btn = Button(cx - 90, 250, 180, 50, "HRÁT", f_ui, settings.SECONDARY)
        logout_btn = Button(cx - 90, 320, 180, 50, "ODHLÁSIT", f_ui, settings.ACCENT)
        for b in [play_btn, logout_btn]: b.draw(win)
        for e in pygame.event.get():
            if e.type == pygame.QUIT: return "QUIT"
            if play_btn.is_clicked(e): return "PLAY"
            if logout_btn.is_clicked(e): return "LOGOUT"
        pygame.display.update()

def game_over_screen(win, bg_img, score):
    f_title = pygame.font.SysFont("Arial", 40, bold=True)
    f_ui = pygame.font.SysFont("Arial", 24)
    cx = win.get_width() // 2
    while True:
        win.blit(bg_img, (0, 0))
        overlay = pygame.Surface((win.get_width(), win.get_height()), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        win.blit(overlay, (0, 0))
        draw_text(win, "GAME OVER", f_title, settings.ACCENT, cx, 150)
        draw_text(win, f"SKÓRE: {score}", f_ui, (255, 255, 255), cx, 220)
        again_btn = Button(cx - 90, 320, 180, 50, "ZNOVU", f_ui, settings.PRIMARY)
        menu_btn = Button(cx - 90, 390, 180, 50, "MENU", f_ui, settings.SECONDARY)
        for b in [again_btn, menu_btn]: b.draw(win)
        for e in pygame.event.get():
            if e.type == pygame.QUIT: return "QUIT"
            if again_btn.is_clicked(e): return "PLAY"
            if menu_btn.is_clicked(e): return "MENU"
        pygame.display.update()

def main():
    database.init_db()
    win = pygame.display.set_mode((settings.WIDTH, settings.HEIGHT))
    bg_img = load_bg(win)

    while True:
        auth = auth_screen(win, bg_img)
        if not auth: break
        uid, uname = auth

        run_app = True
        while run_app:
            choice = start_menu(win, bg_img, uname)
            if choice == "LOGOUT": break
            if choice == "QUIT": return

            playing = True
            while playing:
                pygame.key.set_repeat(200, 50)
                grid = [[0 for _ in range(settings.COLUMNS)] for _ in range(settings.ROWS)]
                score, lvl, fall_time, clock = 0, 1, 0, pygame.time.Clock()
                tetris_bag = Bag()
                piece = tetris_bag.get_piece(grid)

                game_active = True
                while game_active:
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
                            if e.key == pygame.K_SPACE:
                                while piece.valid(dy=1): piece.y += 1

                    if fall_time >= fall_speed:
                        if piece.valid(dy=1): piece.y += 1
                        else:
                            piece.place()
                            full_rows = [i for i, r in enumerate(grid) if all(c != 0 for c in r)]
                            if full_rows:
                                for i in full_rows:
                                    del grid[i]
                                    grid.insert(0, [0 for _ in range(settings.COLUMNS)])
                                mult = {1: 100, 2: 300, 3: 700, 4: 1500}
                                score += mult.get(len(full_rows), 0) * lvl
                                lvl = score // settings.LEVEL_UP_SCORE + 1
                            piece = tetris_bag.get_piece(grid)
                            if not piece.valid():
                                database.save_score(uid, uname, score, lvl)
                                game_active = False
                        fall_time = 0

                    win.blit(bg_img, (0, 0))
                    for y in range(settings.ROWS):
                        for x in range(settings.COLUMNS):
                            rect = (x * settings.BLOCK_SIZE, y * settings.BLOCK_SIZE, settings.BLOCK_SIZE, settings.BLOCK_SIZE)
                            if grid[y][x]: pygame.draw.rect(win, grid[y][x], rect)
                            pygame.draw.rect(win, (40, 40, 40), rect, 1)

                    for y, row in enumerate(piece.shape):
                        for x, cell in enumerate(row):
                            if cell:
                                rect = ((piece.x + x) * settings.BLOCK_SIZE, (piece.y + y) * settings.BLOCK_SIZE, settings.BLOCK_SIZE, settings.BLOCK_SIZE)
                                pygame.draw.rect(win, piece.color, rect)
                                pygame.draw.rect(win, (255, 255, 255), rect, 1)

                    ui_bar = pygame.Surface((win.get_width(), 50), pygame.SRCALPHA)
                    ui_bar.fill((0, 0, 0, 160))
                    win.blit(ui_bar, (0, 0))
                    draw_text(win, f"SCORE: {score} | LVL: {lvl}", pygame.font.SysFont("Arial", 18, bold=True), (255, 255, 255), win.get_width() // 2, 25)
                    pygame.display.update()

                res = game_over_screen(win, bg_img, score)
                if res == "MENU": playing = False
                if res == "QUIT": return

if __name__ == "__main__":
    main()