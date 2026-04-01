import pygame
import random
import math
import sys
import requests
import unittest  # PŘIDÁNO: Knihovna pro unit testy

# Inicializace Pygame (nutné i pro testy)
pygame.init()

# Nové Konstanty (Upravené rozlišení)
WIDTH, HEIGHT = 1024, 768
FPS = 60

class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.vx = random.uniform(-5, 5)
        self.vy = random.uniform(-5, 5)
        self.life = random.randint(20, 40)
        self.color = color

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.life -= 1

    def draw(self, surface):
        if self.life > 0:
            pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), max(1, self.life // 10))

class Paddle:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 15, 80)
        self.base_speed = 5
        self.speed = self.base_speed
        self.score = 0

    def move(self, up, down):
        if up and self.rect.top > 0:
            self.rect.y -= self.speed
        if down and self.rect.bottom < HEIGHT:
            self.rect.y += self.speed

    def ai_move(self, ball, difficulty):
        if difficulty == "easy":
            ai_speed = self.speed * 0.5
        elif difficulty == "normal":
            ai_speed = self.speed * 0.85
        else: # hard
            ai_speed = self.speed * 1.2

        if self.rect.centery < ball.rect.centery and self.rect.bottom < HEIGHT:
            self.rect.y += ai_speed
        elif self.rect.centery > ball.rect.centery and self.rect.top > 0:
            self.rect.y -= ai_speed

    def draw(self, surface, color):
        pygame.draw.rect(surface, color, self.rect)

class Ball:
    def __init__(self):
        self.rect = pygame.Rect(WIDTH // 2 - 7, HEIGHT // 2 - 7, 14, 14)
        self.base_speed = 5
        self.speed = self.base_speed
        self.reset()

    def reset(self):
        self.rect.center = (WIDTH // 2, HEIGHT // 2)
        self.speed = self.base_speed
        angle = random.uniform(-math.pi / 4, math.pi / 4)
        direction = 1 if random.random() > 0.5 else -1
        self.dx = math.cos(angle) * self.speed * direction
        self.dy = math.sin(angle) * self.speed

    def update(self):
        self.rect.x += self.dx
        self.rect.y += self.dy

        if self.rect.top <= 0 or self.rect.bottom >= HEIGHT:
            self.dy *= -1

    def draw(self, surface, color):
        pygame.draw.rect(surface, color, self.rect)

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("PONGp System Archive v1.8")
        self.clock = pygame.time.Clock()
        self.font_large = pygame.font.Font(None, 74)
        self.font_small = pygame.font.Font(None, 36)
        self.font_input = pygame.font.Font(None, 24) # UPRAVENO: Menší font pro inputy

        # --- API Konfigurace ---
        self.api_url = "https://xeon.spskladno.cz/~tobolar/index_main.php" 
        self.logged_in_user = None
        self.logged_in_password = None

        # Nastavení
        self.is_dark_mode = True
        self.difficulty = "normal"
        self.state = "MENU" 
        self.winner = None

        # Herní objekty
        self.player = Paddle(30, HEIGHT // 2 - 40)
        self.opponent = Paddle(WIDTH - 45, HEIGHT // 2 - 40)
        self.ball = Ball()
        self.particles = []

        # Background AI
        self.bg_paddle1 = Paddle(30, HEIGHT // 2 - 40)
        self.bg_paddle2 = Paddle(WIDTH - 45, HEIGHT // 2 - 40)
        self.bg_ball = Ball()
        
        # Proměnné pro Login Overlay
        self.show_login_overlay = False
        self.username_text = ""
        self.password_text = ""
        self.active_input = None
        self.overlay_rects = {}

    def api_login(self, username, password):
        try:
            payload = {"username": username, "password": password}
            response = requests.post(f"{self.api_url}?api=login", json=payload)
            data = response.json()
            if data.get("success"):
                self.logged_in_user = username
                self.logged_in_password = password
                print(f"API: Hráč {username} přihlášen.")
                return True
            else:
                print("API: Neplatné přihlašovací údaje.")
                return False
        except Exception as e:
            print(f"API Chyba: {e}")
            return False

    def api_save_score(self):
        if not self.logged_in_user:
            return
        
        try:
            payload = {
                "username": self.logged_in_user,
                "password": self.logged_in_password,
                "score": self.player.score,
                "difficulty": self.difficulty
            }
            response = requests.post(f"{self.api_url}?api=savescore", json=payload)
            print("API: Skóre odesláno na server.")
        except Exception as e:
            print(f"API Chyba při ukládání: {e}")

    def get_colors(self):
        if self.is_dark_mode:
            return (10, 10, 10), (240, 240, 240)
        else:
            return (240, 240, 240), (10, 10, 10)

    def draw_dashed_line(self, surface, color):
        for y in range(0, HEIGHT, 30):
            pygame.draw.rect(surface, color, (WIDTH // 2 - 2, y, 4, 15))

    def create_particles(self, x, y, color):
        for _ in range(15):
            self.particles.append(Particle(x, y, color))

    def handle_collisions(self):
        if self.ball.rect.colliderect(self.player.rect) and self.ball.dx < 0:
            self.bounce_off_paddle(self.player)
        if self.ball.rect.colliderect(self.opponent.rect) and self.ball.dx > 0:
            self.bounce_off_paddle(self.opponent)

    def bounce_off_paddle(self, paddle):
        _, fg = self.get_colors()
        self.create_particles(self.ball.rect.centerx, self.ball.rect.centery, fg)
        
        intersect_y = paddle.rect.centery - self.ball.rect.centery
        normalized_intersect = intersect_y / (paddle.rect.height / 2)
        bounce_angle = normalized_intersect * (math.pi / 3) 
        
        self.ball.speed += 0.5
        self.player.speed = self.player.base_speed + (self.ball.speed - self.ball.base_speed) * 0.5
        self.opponent.speed = self.opponent.base_speed + (self.ball.speed - self.ball.base_speed) * 0.5

        direction = 1 if self.ball.dx < 0 else -1
        self.ball.dx = math.cos(bounce_angle) * self.ball.speed * direction
        self.ball.dy = -math.sin(bounce_angle) * self.ball.speed

    def reset_game(self):
        self.player.score = 0
        self.opponent.score = 0
        self.player.speed = self.player.base_speed
        self.opponent.speed = self.opponent.base_speed
        self.ball.reset()
        self.particles.clear()

    def update_background_ai(self):
        self.bg_ball.update()
        if self.bg_ball.rect.top <= 0 or self.bg_ball.rect.bottom >= HEIGHT:
            self.bg_ball.dy *= -1
        if self.bg_ball.rect.colliderect(self.bg_paddle1.rect) and self.bg_ball.dx < 0:
            self.bg_ball.dx *= -1
        if self.bg_ball.rect.colliderect(self.bg_paddle2.rect) and self.bg_ball.dx > 0:
            self.bg_ball.dx *= -1
        if self.bg_ball.rect.left <= 0 or self.bg_ball.rect.right >= WIDTH:
            self.bg_ball.reset()

        self.bg_paddle1.ai_move(self.bg_ball, "normal")
        self.bg_paddle2.ai_move(self.bg_ball, "normal")

    def draw_button(self, text, x, y, w, h, mouse_pos):
        bg, fg = self.get_colors()
        rect = pygame.Rect(x, y, w, h)
        color = (100, 100, 100) if rect.collidepoint(mouse_pos) else fg
        text_color = bg
        pygame.draw.rect(self.screen, color, rect, border_radius=5)
        text_surf = self.font_small.render(text, True, text_color)
        text_rect = text_surf.get_rect(center=rect.center)
        self.screen.blit(text_surf, text_rect)
        return rect

    def draw_login_overlay(self, mouse_pos, bg, fg):
        # UPRAVENO: Zmenšený a zjednodušený overlay
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180) if self.is_dark_mode else (255, 255, 255, 180))
        self.screen.blit(overlay, (0, 0))

        # Nové poloviční rozměry
        modal_w, modal_h = 250, 220
        modal_x, modal_y = WIDTH // 2 - modal_w // 2, HEIGHT // 2 - modal_h // 2
        modal_rect = pygame.Rect(modal_x, modal_y, modal_w, modal_h)
        pygame.draw.rect(self.screen, bg, modal_rect)
        pygame.draw.rect(self.screen, fg, modal_rect, 2)

        # Tlačítko pro zavření
        close_rect = pygame.Rect(modal_x + modal_w - 30, modal_y + 10, 20, 20)
        close_text = self.font_input.render("[X]", True, fg)
        self.screen.blit(close_text, close_text.get_rect(center=close_rect.center))

        # Nadpis LOGIN
        title_text = self.font_small.render("LOGIN", True, fg)
        self.screen.blit(title_text, (modal_x + 15, modal_y + 15))

        # Input boxy
        user_rect = pygame.Rect(modal_x + 15, modal_y + 55, modal_w - 30, 35)
        pass_rect = pygame.Rect(modal_x + 15, modal_y + 105, modal_w - 30, 35)

        # Vykreslení User Inputu
        pygame.draw.rect(self.screen, fg, user_rect, 2 if self.active_input != "username" else 4)
        if self.username_text == "" and self.active_input != "username":
            u_text = self.font_input.render("User", True, (100, 100, 100))
        else:
            u_text = self.font_input.render(self.username_text, True, fg)
        self.screen.blit(u_text, (user_rect.x + 10, user_rect.y + 10))

        # Vykreslení Pass Inputu
        pygame.draw.rect(self.screen, fg, pass_rect, 2 if self.active_input != "password" else 4)
        if self.password_text == "" and self.active_input != "password":
            p_text = self.font_input.render("Password", True, (100, 100, 100))
        else:
            p_text = self.font_input.render("*" * len(self.password_text), True, fg)
        self.screen.blit(p_text, (pass_rect.x + 10, pass_rect.y + 10))

        # Vykreslení Submit tlačítka
        submit_rect = pygame.Rect(modal_x + 15, modal_y + 160, modal_w - 30, 40)
        hover = submit_rect.collidepoint(mouse_pos)
        pygame.draw.rect(self.screen, fg, submit_rect, 0 if hover else 2)
        s_text = self.font_input.render("Enter", True, bg if hover else fg)
        self.screen.blit(s_text, s_text.get_rect(center=submit_rect.center))

        return {
            "close": close_rect, 
            "user": user_rect, 
            "pass": pass_rect, 
            "submit": submit_rect
        }

    def run(self):
        while True:
            bg_color, fg_color = self.get_colors()
            mouse_pos = pygame.mouse.get_pos()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.KEYDOWN:
                    if self.state == "PLAYING" and event.key == pygame.K_ESCAPE:
                        self.api_save_score()
                        self.state = "MENU"
                    
                    if self.state == "MENU" and self.show_login_overlay and self.active_input:
                        if event.key == pygame.K_BACKSPACE:
                            if self.active_input == "username":
                                self.username_text = self.username_text[:-1]
                            else:
                                self.password_text = self.password_text[:-1]
                        elif event.key == pygame.K_TAB:
                            self.active_input = "password" if self.active_input == "username" else "username"
                        elif event.unicode.isprintable():
                            if self.active_input == "username" and len(self.username_text) < 20:
                                self.username_text += event.unicode
                            elif self.active_input == "password" and len(self.password_text) < 20:
                                self.password_text += event.unicode

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.state == "MENU":
                        if self.show_login_overlay:
                            rects = self.overlay_rects
                            if rects.get("close", pygame.Rect(0,0,0,0)).collidepoint(mouse_pos):
                                self.show_login_overlay = False
                            elif rects.get("user", pygame.Rect(0,0,0,0)).collidepoint(mouse_pos):
                                self.active_input = "username"
                            elif rects.get("pass", pygame.Rect(0,0,0,0)).collidepoint(mouse_pos):
                                self.active_input = "password"
                            elif rects.get("submit", pygame.Rect(0,0,0,0)).collidepoint(mouse_pos):
                                if self.api_login(self.username_text, self.password_text):
                                    self.show_login_overlay = False
                                    self.username_text = ""
                                    self.password_text = ""
                            else:
                                self.active_input = None
                        else:
                            if self.btn_start.collidepoint(mouse_pos):
                                self.reset_game()
                                self.state = "PLAYING"
                            elif self.btn_auth.collidepoint(mouse_pos):
                                self.show_login_overlay = True
                            elif self.btn_settings.collidepoint(mouse_pos):
                                self.state = "SETTINGS"
                            elif self.btn_exit.collidepoint(mouse_pos):
                                pygame.quit()
                                sys.exit()
                            
                    elif self.state == "SETTINGS":
                        if self.btn_back.collidepoint(mouse_pos):
                            self.state = "MENU"
                        elif self.btn_theme.collidepoint(mouse_pos):
                            self.is_dark_mode = not self.is_dark_mode
                        elif self.btn_diff_easy.collidepoint(mouse_pos):
                            self.difficulty = "easy"
                        elif self.btn_diff_norm.collidepoint(mouse_pos):
                            self.difficulty = "normal"
                        elif self.btn_diff_hard.collidepoint(mouse_pos):
                            self.difficulty = "hard"

                    elif self.state == "GAME_OVER":
                        if self.btn_menu.collidepoint(mouse_pos):
                            self.state = "MENU"

            self.screen.fill(bg_color)

            if self.state in ["MENU", "SETTINGS", "GAME_OVER"]:
                self.update_background_ai()
                overlay_color = (0, 0, 0, 150) if self.is_dark_mode else (255, 255, 255, 150)
                self.draw_dashed_line(self.screen, (100, 100, 100))
                self.bg_paddle1.draw(self.screen, (100, 100, 100))
                self.bg_paddle2.draw(self.screen, (100, 100, 100))
                self.bg_ball.draw(self.screen, (100, 100, 100))
                overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                overlay.fill(overlay_color)
                self.screen.blit(overlay, (0, 0))

            if self.state == "MENU":
                title = self.font_large.render("PONG", True, fg_color)
                self.screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 150))
                
                user_label = "Nepřihlášen" if not self.logged_in_user else f"Hráč: {self.logged_in_user}"
                u_surf = self.font_small.render(user_label, True, (255, 215, 0))
                self.screen.blit(u_surf, (WIDTH // 2 - u_surf.get_width() // 2, 230))

                self.btn_start = self.draw_button("Start", WIDTH//2 - 125, 300, 250, 50, mouse_pos)
                self.btn_auth = self.draw_button("Login", WIDTH//2 - 125, 370, 250, 50, mouse_pos)
                self.btn_settings = self.draw_button("Settings", WIDTH//2 - 125, 440, 250, 50, mouse_pos)
                self.btn_exit = self.draw_button("Exit", WIDTH//2 - 125, 510, 250, 50, mouse_pos)

                if self.show_login_overlay:
                    self.overlay_rects = self.draw_login_overlay(mouse_pos, bg_color, fg_color)

            elif self.state == "SETTINGS":
                title = self.font_large.render("Settings", True, fg_color)
                self.screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 150))
                theme_text = "Light Mode" if self.is_dark_mode else "Dark Mode"
                self.btn_theme = self.draw_button(f"Switch to {theme_text}", WIDTH//2 - 150, 250, 300, 50, mouse_pos)
                diff_label = self.font_small.render(f"Difficulty: {self.difficulty.upper()}", True, fg_color)
                self.screen.blit(diff_label, (WIDTH // 2 - diff_label.get_width() // 2, 330))
                self.btn_diff_easy = self.draw_button("Easy", WIDTH//2 - 160, 380, 100, 40, mouse_pos)
                self.btn_diff_norm = self.draw_button("Normal", WIDTH//2 - 50, 380, 100, 40, mouse_pos)
                self.btn_diff_hard = self.draw_button("Hard", WIDTH//2 + 60, 380, 100, 40, mouse_pos)
                self.btn_back = self.draw_button("Back", WIDTH//2 - 100, 500, 200, 50, mouse_pos)

            elif self.state == "PLAYING":
                keys = pygame.key.get_pressed()
                self.player.move(keys[pygame.K_w] or keys[pygame.K_UP], keys[pygame.K_s] or keys[pygame.K_DOWN])
                self.opponent.ai_move(self.ball, self.difficulty)
                self.ball.update()
                self.handle_collisions()

                if self.ball.rect.left <= 0:
                    self.opponent.score += 1
                    self.ball.reset()
                if self.ball.rect.right >= WIDTH:
                    self.player.score += 1
                    self.ball.reset()

                if self.player.score >= 10:
                    self.winner = "Player"
                    self.state = "GAME_OVER"
                    self.api_save_score()
                elif self.opponent.score >= 10:
                    self.winner = "AI"
                    self.state = "GAME_OVER"
                    self.api_save_score()

                for particle in self.particles[:]:
                    particle.update()
                    if particle.life <= 0:
                        self.particles.remove(particle)

                self.draw_dashed_line(self.screen, fg_color)
                self.player.draw(self.screen, fg_color)
                self.opponent.draw(self.screen, fg_color)
                self.ball.draw(self.screen, fg_color)
                for particle in self.particles:
                    particle.draw(self.screen)

                score_p = self.font_large.render(str(self.player.score), True, fg_color)
                score_o = self.font_large.render(str(self.opponent.score), True, fg_color)
                self.screen.blit(score_p, (WIDTH // 4, 20))
                self.screen.blit(score_o, (WIDTH * 3 // 4, 20))

            elif self.state == "GAME_OVER":
                text = f"{self.winner} Wins!"
                title = self.font_large.render(text, True, fg_color)
                self.screen.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT // 2 - 100))
                self.btn_menu = self.draw_button("Return to Menu", WIDTH//2 - 125, HEIGHT // 2, 250, 50, mouse_pos)

            pygame.display.flip()
            self.clock.tick(FPS)

# ==========================================
# --- UNIT TESTY (Herní mechaniky) ---
# ==========================================
class TestPongMechanics(unittest.TestCase):
    def setUp(self):
        # Inicializace objektů před každým testem
        self.ball = Ball()
        self.paddle = Paddle(10, HEIGHT // 2)

    def test_ball_reset(self):
        """Testuje, zda se míček po resetu správně vrátí doprostřed obrazovky."""
        self.ball.rect.x = 100
        self.ball.rect.y = 100
        self.ball.reset()
        self.assertEqual(self.ball.rect.center, (WIDTH // 2, HEIGHT // 2))

    def test_paddle_movement(self):
        """Testuje, zda pálka správně reaguje na povel k pohybu dolů."""
        start_y = self.paddle.rect.y
        self.paddle.move(up=False, down=True)
        self.assertGreater(self.paddle.rect.y, start_y)

    def test_paddle_boundaries(self):
        """Testuje, zda pálka nevyjede mimo horní okraj obrazovky."""
        self.paddle.rect.y = 0
        self.paddle.move(up=True, down=False)
        self.assertEqual(self.paddle.rect.y, 0) # Neměla by se pohnout do mínusu

# ==========================================
# --- SPUŠTĚNÍ HRY NEBO TESTŮ ---
# ==========================================
if __name__ == "__main__":
    # Pokud spustíš soubor s argumentem 'test' (např. python pong_main_final.py test)
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        unittest.main(argv=['first-arg-is-ignored'])
    else:
        # Jinak se spustí normální hra
        game = Game()
        game.run()
