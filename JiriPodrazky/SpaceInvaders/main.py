import pygame
import random
import math
import requests
import sys

# --- NASTAVENÍ PROPOJENÍ S WEBEM ---
URL_ULOZIT_SKORE = "https://xeon.spskladno.cz/~podrazkj/space_invaders/save_score.php"
logged_user = sys.argv[1] if len(sys.argv) > 1 else "Host"
score_sent = False


def odeslat_skore_na_web(username, score):
    try:
        requests.post(URL_ULOZIT_SKORE, data={'username': username, 'score': score}, timeout=5)
    except:
        pass


# --- INICIALIZACE ---
pygame.init()
screen_width, screen_height = 800, 600
main_screen = pygame.display.set_mode((screen_width, screen_height))
canvas = pygame.Surface((screen_width, screen_height))
pygame.display.set_caption("Space Invaders - Ultimate Evolution")

shake_timer = 0
particles, notifications, explosions = [], [], []


def trigger_shake(duration):
    global shake_timer
    shake_timer = duration


font_ui = pygame.font.Font('freesansbold.ttf', 18)
font_msg = pygame.font.Font('freesansbold.ttf', 30)
font_warn = pygame.font.Font('freesansbold.ttf', 50)
game_over_font = pygame.font.Font('freesansbold.ttf', 64)


# --- EFEKTY ---
class Particle:
    def __init__(self, x, y, color, vx=None, vy=None, size=2):
        self.x, self.y, self.color = x, y, color
        self.vx = vx if vx is not None else random.uniform(-3, 3)
        self.vy = vy if vy is not None else random.uniform(-3, 3)
        self.life, self.size = 60, size

    def update(self):
        self.x += self.vx;
        self.y += self.vy;
        self.life -= 1

    def draw(self, surface):
        if self.life > 0:
            pygame.draw.rect(surface, self.color, (int(self.x), int(self.y), self.size, self.size))


class Explosion:
    def __init__(self, x, y, color=(255, 150, 50)):
        self.x, self.y, self.radius, self.alpha, self.color = x, y, 2, 255, color

    def draw(self, surface):
        if self.alpha > 0:
            c = max(0, int(self.alpha))
            pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), int(self.radius), 2)
            self.radius += 3;
            self.alpha -= 15


class Notification:
    def __init__(self, text, color, offset_y=0):
        self.text, self.color, self.y, self.alpha = text, color, 250 + offset_y, 255

    def draw(self, surface):
        if self.alpha > 0:
            t = font_msg.render(self.text, False, self.color)
            t.set_alpha(int(self.alpha))
            surface.blit(t, (screen_width // 2 - t.get_width() // 2, self.y))
            self.y -= 0.4;
            self.alpha -= 2


def create_explosion(x, y, color, count=15):
    explosions.append(Explosion(x, y, color))
    for _ in range(count): particles.append(Particle(x, y, color))


class UpgradeCrate:
    def __init__(self):
        self.x, self.y, self.angle = random.randint(100, 700), 520, 0

    def draw(self, surface):
        self.angle += 0.1
        s = 30 + math.sin(self.angle) * 5
        pygame.draw.rect(surface, (255, 215, 0), (self.x, self.y - s / 4, s, s))
        pygame.draw.rect(surface, (255, 255, 255), (self.x, self.y - s / 4, s, s), 2)


class Boss:
    def __init__(self, level):
        self.width, self.height = 160, 80
        self.x, self.y = screen_width // 2 - 80, -200
        self.max_hp = 50 + (level * 40)
        self.hp = self.max_hp
        self.speed_x = 1.4 + (level * 0.2)
        self.speed_y = 0.05 + (level * 0.02)
        self.state = "intro"
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

    def update(self):
        if self.state == "intro":
            self.y += 1.0
            if self.y >= 80: self.state = "active"; trigger_shake(30)
        else:
            self.x += self.speed_x
            if self.x + self.width > screen_width or self.x < 0: self.speed_x *= -1
            self.y += self.speed_y
        self.rect.topleft = (self.x, self.y)

    def draw(self, surface):
        pygame.draw.rect(surface, (100, 0, 0), self.rect)
        pygame.draw.rect(surface, (255, 0, 0), self.rect, 2)
        if self.state == "active":
            pygame.draw.rect(surface, (50, 0, 0), (self.x, self.y - 30, self.width, 12))
            hp_w = int(self.width * (self.hp / self.max_hp))
            pygame.draw.rect(surface, (0, 255, 0), (self.x, self.y - 30, hp_w, 12))


# --- HERNÍ STATS ---
player_speed, bullet_speed, max_bullets = 4.8, 7.0, 1
bullet_radius = 4  # Nový stat pro velikost střel
player_shields, max_player_shields = 3, 3
minion_count, minion_cooldown, minion_timer = 0, 90, 0
score_val, game_state, upgrade_crate, selected_upgrades = 0, "playing", None, []

# VYBALANCOVANÁ PROGRESE
current_invader_speed, invader_speed_cap = 1.3, 10.0
next_speed_score = 30  # Pomalejší intervaly
next_boss_score = 250
next_crate_score, crate_gap = 50, 60

UPGRADE_POOL = [
    {"id": "bullets", "name": "VOLLEY (+1 Shot)", "color": (0, 255, 255)},
    {"id": "b_speed", "name": "PLASMA BOLT (+Speed)", "color": (255, 255, 0)},
    {"id": "b_size", "name": "WIDE BEAM (+Radius)", "color": (200, 255, 100)},
    {"id": "minion", "name": "DRONE SQUAD (+1)", "color": (255, 0, 255)},
    {"id": "p_speed", "name": "TURBO ENGINES", "color": (0, 255, 0)},
    {"id": "shield_rep", "name": "SHIELD REPAIR", "color": (255, 255, 255)},
    {"id": "shield_max", "name": "REINFORCED HULL (+Max)", "color": (150, 150, 150)}
]

invader_X, invader_Y, invader_Xchange, invader_Ychange = [], [], [], []
invader_type, invader_hp, invader_color = [], [], []


def add_invader():
    r = random.random()
    if r < 0.50:
        t, hp, col, spm = "normal", 1, (255, 50, 50), 1.0
    elif r < 0.80:
        t, hp, col, spm = "tank", 3, (50, 255, 50), 0.6
    else:
        t, hp, col, spm = "assassin", 1, (255, 255, 50), 1.9
    invader_type.append(t);
    invader_hp.append(hp);
    invader_color.append(col)
    invader_X.append(random.randint(64, 737));
    invader_Y.append(random.randint(30, 150))
    invader_Xchange.append(current_invader_speed * spm);
    invader_Ychange.append(40)


for _ in range(6): add_invader()

player_bullets, minion_bullets = [], []
player_X, player_Y, player_Xchange = 370, 523, 0
boss_mode, the_boss, boss_level, boss_warning_timer = False, None, 1, 0
stars = [[random.randint(0, 800), random.randint(0, 600), random.uniform(0.5, 4.0), random.randint(1, 3)] for _ in
         range(120)]


def draw_hud(surface):
    pygame.draw.rect(surface, (15, 15, 30), (0, 0, 800, 45))
    info = font_ui.render(
        f"SCORE: {score_val} | SHIELDS: {player_shields}/{max_player_shields} | UNITS: {len(invader_X)} | SPEED: {current_invader_speed:.1f}",
        True, (255, 255, 255))
    surface.blit(info, (20, 15))


def draw_upgrade_menu(surface):
    overlay = pygame.Surface((screen_width, screen_height));
    overlay.set_alpha(210);
    overlay.fill((0, 0, 0));
    surface.blit(overlay, (0, 0))
    t = font_msg.render("EVOLUTION SELECT:", True, (255, 215, 0))
    surface.blit(t, (screen_width // 2 - t.get_width() // 2, 120))
    for i, upg in enumerate(selected_upgrades):
        ry = 220 + i * 80;
        pygame.draw.rect(surface, upg['color'], (screen_width // 2 - 200, ry, 400, 60), 2)
        txt = font_msg.render(f"[{i + 1}] {upg['name']}", True, upg['color']);
        surface.blit(txt, (screen_width // 2 - txt.get_width() // 2, ry + 15))


# --- HLAVNÍ SMYČKA ---
if __name__ == "__main__":
    clock, running = pygame.time.Clock(), True
    while running:
        canvas.fill((5, 5, 10))
        for star in stars:
            star[1] += star[2]
            if star[1] > 600: star[1], star[0] = 0, random.randint(0, 800)
            pygame.draw.circle(canvas, (180, 180, 255), (int(star[0]), int(star[1])), star[3])

        for event in pygame.event.get():
            if event.type == pygame.QUIT: running = False
            if game_state == "playing":
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT: player_Xchange = -player_speed
                    if event.key == pygame.K_RIGHT: player_Xchange = player_speed
                    if event.key == pygame.K_SPACE and len(player_bullets) < max_bullets:
                        player_bullets.append([player_X + 16, player_Y])
                if event.type == pygame.KEYUP:
                    if event.key in (pygame.K_LEFT, pygame.K_RIGHT): player_Xchange = 0
            elif game_state == "choosing":
                if event.type == pygame.KEYDOWN:
                    idx = -1
                    if event.key == pygame.K_1:
                        idx = 0
                    elif event.key == pygame.K_2:
                        idx = 1
                    elif event.key == pygame.K_3:
                        idx = 2
                    if idx != -1:
                        u = selected_upgrades[idx]
                        if u['id'] == "bullets":
                            max_bullets = min(8, max_bullets + 1)
                        elif u['id'] == "b_speed":
                            bullet_speed = min(16, bullet_speed + 2)
                        elif u['id'] == "b_size":
                            bullet_radius = min(12, bullet_radius + 2)
                        elif u['id'] == "minion":
                            minion_count = min(6, minion_count + 1)
                        elif u['id'] == "p_speed":
                            player_speed = min(10, player_speed + 0.6)
                        elif u['id'] == "shield_rep":
                            player_shields = min(max_player_shields, player_shields + 1)
                        elif u['id'] == "shield_max":
                            max_player_shields += 1; player_shields += 1
                        notifications.append(Notification(f"UPGRADED: {u['name']}", u['color']))
                        game_state = "playing"

        if game_state == "playing":
            player_X += player_Xchange;
            player_X = max(16, min(750, player_X))

            if minion_count > 0:
                minion_timer += 1
                fire_d = (minion_timer >= minion_cooldown)
                if fire_d: minion_timer = 0
                for m in range(minion_count):
                    off = 45 * ((m // 2) + 1);
                    mx = player_X - off if m % 2 == 0 else player_X + off
                    pygame.draw.circle(canvas, (200, 50, 255), (int(mx), player_Y + 20), 8)
                    if fire_d: minion_bullets.append([mx, player_Y])

            pygame.draw.line(canvas, (255, 50, 50), (0, 450), (800, 450), 1)

            if boss_warning_timer > 0:
                boss_warning_timer -= 1;
                trigger_shake(2)
                if (boss_warning_timer // 10) % 2 == 0:
                    w_t = font_warn.render("BOSS INCOMING", False, (255, 0, 0))
                    canvas.blit(w_t, (screen_width // 2 - w_t.get_width() // 2, 250))
                if boss_warning_timer == 0: boss_mode, the_boss = True, Boss(boss_level)

            elif boss_mode:
                the_boss.update();
                the_boss.draw(canvas)
                if the_boss.y + the_boss.height > 450:
                    player_shields -= 1;
                    boss_mode = False;
                    trigger_shake(35)
                    if player_shields <= 0: game_state = "game_over"
                if the_boss.state == "active":
                    for blist in [player_bullets, minion_bullets]:
                        for b in blist[:]:
                            if the_boss.rect.collidepoint(b[0], b[1]):
                                create_explosion(b[0], b[1], (255, 100, 0), 5);
                                the_boss.hp -= 1;
                                trigger_shake(2)
                                if b in blist: blist.remove(b)
                                if the_boss.hp <= 0:
                                    create_explosion(the_boss.x + 80, the_boss.y + 40, (255, 255, 0), 100)
                                    score_val += 200;
                                    boss_level += 1;
                                    boss_mode = False
                                    next_boss_score = score_val + 400
                                    for _ in range(8): add_invader()

            else:
                if len(invader_X) < 5: add_invader()
                if upgrade_crate:
                    upgrade_crate.draw(canvas)
                    if abs(player_X - upgrade_crate.x) < 40:
                        upgrade_crate = None
                        selected_upgrades = random.sample(UPGRADE_POOL, 3);
                        game_state = "choosing"

                nb = False
                for i in range(len(invader_X) - 1, -1, -1):
                    if invader_Y[i] > 450:
                        player_shields -= 1;
                        trigger_shake(30)
                        invader_X.pop(i);
                        invader_Y.pop(i);
                        invader_Xchange.pop(i);
                        invader_Ychange.pop(i);
                        invader_type.pop(i);
                        invader_hp.pop(i);
                        invader_color.pop(i)
                        add_invader()
                        if player_shields <= 0: game_state = "game_over"
                        break

                    invader_X[i] += invader_Xchange[i]
                    if invader_X[i] <= 0:
                        invader_X[i] = 1; invader_Xchange[i] *= -1; invader_Y[i] += invader_Ychange[i]
                    elif invader_X[i] >= 736:
                        invader_X[i] = 735; invader_Xchange[i] *= -1; invader_Y[i] += invader_Ychange[i]

                    rem = False
                    for blist in [player_bullets, minion_bullets]:
                        for b in blist[:]:
                            # Detekce kolize upravena o bullet_radius
                            if math.sqrt(math.pow(invader_X[i] - b[0], 2) + math.pow(invader_Y[i] - b[1], 2)) < (
                                    30 + bullet_radius):
                                if b in blist: blist.remove(b)
                                invader_hp[i] -= 1;
                                trigger_shake(2)
                                if invader_hp[i] <= 0:
                                    create_explosion(invader_X[i] + 16, invader_Y[i] + 16, invader_color[i])
                                    score_val += 1
                                    invader_X.pop(i);
                                    invader_Y.pop(i);
                                    invader_Xchange.pop(i);
                                    invader_Ychange.pop(i);
                                    invader_type.pop(i);
                                    invader_hp.pop(i);
                                    invader_color.pop(i)
                                    add_invader()

                                    # JEMNĚJŠÍ PROGRESE RYCHLOSTI
                                    if score_val >= next_speed_score:
                                        if current_invader_speed < invader_speed_cap:
                                            current_invader_speed += 0.1  # Zpomaleno z 0.4
                                            for j in range(len(invader_Xchange)):
                                                invader_Xchange[j] = math.copysign(current_invader_speed,
                                                                                   invader_Xchange[j])
                                        next_speed_score += 30  # Prodloužen interval

                                    if score_val % 10 == 0:
                                        add_invader()
                                        notifications.append(Notification("INVASION RISES!", (0, 255, 0)))

                                    if score_val >= next_boss_score: nb = True
                                    if score_val >= next_crate_score:
                                        upgrade_crate = UpgradeCrate();
                                        crate_gap = int(crate_gap * 1.25);
                                        next_crate_score = score_val + crate_gap
                                    rem = True;
                                    break
                        if rem: break
                    if not rem:
                        c = invader_color[i];
                        x, y = invader_X[i], invader_Y[i]
                        pygame.draw.polygon(canvas, c,
                                            [(x + 16, y), (x + 32, y + 16), (x + 24, y + 32), (x + 8, y + 32),
                                             (x, y + 16)])

                if nb: boss_warning_timer = 200; invader_X, invader_Y, invader_Xchange, invader_Ychange, invader_type, invader_hp, invader_color = [], [], [], [], [], [], []

            for b in player_bullets[:]:
                pygame.draw.circle(canvas, (255, 100, 100), (int(b[0]), int(b[1])), bullet_radius);
                b[1] -= bullet_speed
                if b[1] <= 0: player_bullets.remove(b)
            for b in minion_bullets[:]:
                pygame.draw.circle(canvas, (200, 100, 255), (int(b[0]), int(b[1])), 3);
                b[1] -= bullet_speed
                if b[1] <= 0: minion_bullets.remove(b)

            pygame.draw.polygon(canvas, (0, 200, 255),
                                [(player_X, player_Y), (player_X - 16, player_Y + 32), (player_X + 16, player_Y + 32)])
            draw_hud(canvas)

        elif game_state == "choosing":
            draw_upgrade_menu(canvas)
        elif game_state == "game_over":
            canvas.blit(game_over_font.render("SYSTEM FAILURE", False, (255, 0, 0)), (140, 250))
            if not score_sent: odeslat_skore_na_web(logged_user, score_val); score_sent = True

        for p in particles[:]:
            p.update();
            p.draw(canvas)
            if p.life <= 0: particles.remove(p)
        for e in explosions[:]:
            e.draw(canvas)
            if e.alpha <= 0: explosions.remove(e)
        for n in notifications[:]:
            n.draw(canvas)
            if n.alpha <= 0: notifications.remove(n)

        sx, sy = (random.randint(-7, 7), random.randint(-7, 7)) if shake_timer > 0 else (0, 0)
        if shake_timer > 0: shake_timer -= 1
        main_screen.blit(canvas, (sx, sy))
        pygame.display.update();
        clock.tick(120)
    pygame.quit()