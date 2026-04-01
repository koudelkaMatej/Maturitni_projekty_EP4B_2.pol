import pygame  # Hlavní knihovna pro tvorbu 2D her (vykreslování, okno, události)
import random  # Knihovna pro generování náhodných čísel (spawnování, jiskry)
import math  # Matematické funkce (sinus pro levitaci bedny, copysign pro vektory)
import sys  # Přístup k systémovým parametrům (příjem argumentů z menu)
import os  # Práce se souborovým systémem (skládání cest k obrázkům)
try:
    import requests  # Knihovna pro odesílání dat na server (uložení skóre)
except ImportError:
    requests = None  # Pokud knihovna chybí, budeme simulovat offline režim
import unittest  # Modul pro integrované diagnostické testy (ověřování logiky)

# =============================================================================
# 1. KONFIGURACE BALANCU HRY (PARAMETRY SIMULACE)
# =============================================================================
# Zde jsou definovány všechny konstanty. Změnou těchto čísel ladíš hru.
# Slovo "CFG" znamená Configuration (Nastavení).

# --- ZÁKLADNÍ PARAMETRY DISPLEJE ---
WIDTH, HEIGHT = 1280, 720  # Rozlišení Viewportu (HD)
FPS = 120  # Snímková frekvence (120x za sekundu se překreslí obrazovka)

# --- PRIMÁRNÍ AKTÉR (HRÁČ) ---
CFG_PLAYER_SPEED = 6.0  # Jak rychle se loď hýbe do stran (Pixelů za snímek)
CFG_PLAYER_SHIELDS = 3  # Strukturální integrita (Počet životů hráče)
CFG_BULLET_SPEED = 10.0  # Jak rychle letí hráčova střela nahoru
CFG_BULLET_SIZE = 4  # Poloměr (velikost) střely
CFG_BULLET_MAX = 1  # Kolik střel může mít hráč současně na obrazovce

# --- UMĚLÁ INTELIGENCE (NEPŘÁTELÉ) ---
CFG_ENEMY_START_SPEED = 1.5  # Výchozí rychlost pohybu ufonů na začátku hry
CFG_ENEMY_MAX_SPEED = 7.0  # Maximální rychlost, na kterou mohou ufoni zrychlit (Strop)
CFG_ENEMY_SPEED_BOOST = 0.05  # O kolik se ufoni zrychlí po dosažení milníku skóre
CFG_ENEMY_START_COUNT = 6  # Kolik ufonů má být minimálně na obrazovce v jednu chvíli
CFG_ENEMY_SPAWN_DELAY = 15  # Jak dlouho (v počtu snímků) se čeká na spawn dalšího ufona

# --- DYNAMICKÁ PROGRESE ---
CFG_SCORE_SPEEDUP_GAP = 40  # Každých 40 bodů se ufoni plošně zrychlí
CFG_SCORE_MORE_ENEMIES = 15  # Každých 15 bodů se zvýší počet ufonů na obrazovce o 1

# --- SYSTÉM ODMĚN A ELITNÍ JEDNOTKY ---
CFG_FIRST_CRATE_SCORE = 40  # Skóre, kdy spadne první bedna s upgradem
CFG_CRATE_GAP = 45  # Každých dalších 45 bodů spadne další bedna
CFG_FIRST_BOSS_SCORE = 100  # Skóre, kdy přiletí první Boss
CFG_BOSS_GAP = 250  # Po kolika bodech (od smrti předchozího) přiletí další Boss
CFG_BOSS_BASE_HP = 40  # Startovní životy prvního Bosse
CFG_BOSS_HP_INCREMENT = 30  # Každý další Boss má o 30 životů více

# =============================================================================
# 2. SYSTÉMOVÉ PROMĚNNÉ A ASSETY
# =============================================================================

# Získání jména hráče z menu.py. Pokud bylo spuštěno přes test, nastav "Operator".
USER = sys.argv[1] if len(sys.argv) > 1 and sys.argv[1] != "--test" else "Operator"
# Cesta k obrázku vybrané lodi. Defaultně se nastaví modrá loď z adresáře data.
CHOSEN_SHIP = sys.argv[2] if len(sys.argv) > 2 else os.path.join("data", "playerShip1_blue.png")

# Výpočet pevných souřadnic Y (výšky) na obrazovce. Výhoda: funguje na jakémkoliv rozlišení.
PLAYER_Y = HEIGHT - 80  # Pozice, kde létá loď hráče
DEFENSE_LINE_Y = HEIGHT - 120  # Červená čára - pokud ji ufoni podletí, hráč ztrácí život

# Seznam barevných témat. Každá fáze hry má jiné barvy pozadí a hvězd. Formát: RGB.
THEMES = [
    ((5, 5, 15), (150, 150, 255)),  # Fáze 1: Tmavě modrý vesmír
    ((15, 5, 15), (255, 150, 255)),  # Fáze 2: Fialová anomálie
    ((5, 15, 10), (150, 255, 150)),  # Fáze 3: Zelená mlhovina
]

# Definice technologického stromu (možná vylepšení z beden)
UPGRADES = [
    {"id": "bullets", "name": "VOLLEY (+1 Střela)", "col": (0, 255, 255)},  # Zvýší b_max
    {"id": "b_speed", "name": "PLASMA (+Rychlost střel)", "col": (255, 255, 0)},  # Zvýší b_speed
    {"id": "b_size", "name": "WIDE BEAM (+Rozptyl)", "col": (200, 255, 100)},  # Zvýší b_rad
    {"id": "minion", "name": "DRONE SQUAD (+1 Dron)", "col": (255, 0, 255)},  # Zvýší minions
    {"id": "p_speed", "name": "TURBO ENGINES (+Rychlost lodi)", "col": (0, 255, 0)},  # Zvýší p_speed
    {"id": "shield_rep", "name": "SHIELD REPAIR (+1 Integrita)", "col": (255, 255, 255)}  # Zvýší shields
]

URL_SAVE_SCORE = "https://xeon.spskladno.cz/~podrazkj/space_invaders/save_score.php"


# =============================================================================
# 3. VIZUÁLNÍ SUBSYSTÉMY (VFX ENGINE) - Částice a efekty
# =============================================================================

class Particle:
    """Fyzikální částice. Používá se pro jiskry, kouř a plameny motorů."""

    def __init__(self, x, y, color, vx=0.0, vy=0.0, life=30, size=3.0, friction=0.95):
        self.x, self.y = x, y  # Souřadnice částice
        self.color = color  # Barva (RGB)
        self.vx, self.vy = vx, vy  # Vektory rychlosti (horizontální a vertikální)
        self.life, self.max_life = life, life  # Jak dlouho (ve snímcích) částice existuje
        self.size = size  # Aktuální velikost
        self.friction = friction  # Kinetické tření (hodnota pod 1.0 částici postupně zpomaluje)

    def update(self):
        """Přepočet fyziky. Volá se každý snímek hry."""
        self.vx *= self.friction  # Zpomalení pohybu na ose X
        self.vy *= self.friction  # Zpomalení pohybu na ose Y
        self.x += self.vx;
        self.y += self.vy  # Posun částice
        self.size *= 0.95  # Částice se zmenšuje (vypařuje se)
        self.life -= 1  # Částice stárne

    def draw(self, surface):
        """Vykreslení částice na obrazovku s plynulým blednutím (Alpha)."""
        if self.life > 0 and self.size > 0.5:
            # Alpha je průhlednost: 255 je plně viditelné, 0 je neviditelné.
            # Jak life klesá, alpha se zmenšuje (částice bledne).
            alpha = max(0, min(255, int((self.life / self.max_life) * 255)))
            s = pygame.Surface((int(self.size), int(self.size)), pygame.SRCALPHA)
            s.fill((*self.color, alpha))  # Aplikace barvy a průhlednosti
            surface.blit(s, (int(self.x), int(self.y)))


class Explosion:
    """Šířící se rázová vlna (Shockwave). Efekt při zničení ufa nebo příletu z warpu."""

    def __init__(self, x, y, color=(255, 150, 50)):
        self.x, self.y = x, y
        self.color = color
        self.radius, self.alpha = 2.0, 255.0  # Začíná jako malý, plně viditelný kruh

    def draw(self, surface):
        if self.alpha > 0:
            surf = pygame.Surface((int(self.radius * 2), int(self.radius * 2)), pygame.SRCALPHA)
            pygame.draw.circle(surf, (*self.color, int(self.alpha)), (int(self.radius), int(self.radius)),
                               int(self.radius), 2)
            surface.blit(surf, (self.x - self.radius, self.y - self.radius))
            self.radius += 5.0  # Kruh se každým snímkem zvětší o 5 pixelů
            self.alpha -= 15.0  # Kruh každým snímkem výrazně zbledne


class Notification:
    """Plovoucí text na obrazovce (HUD Overlay), např. "INVASION RISES!"."""

    def __init__(self, text, color, font, y_offset=0):
        self.img = font.render(text, True, color)  # Vykreslí text do obrázku
        self.x = WIDTH // 2 - self.img.get_width() // 2  # Centrování na střed obrazovky
        self.y = HEIGHT // 2 - 50 + y_offset
        self.alpha = 255

    def draw(self, surface):
        if self.alpha > 0:
            self.y -= 0.5  # Text pomalu stoupá nahoru
            self.alpha -= 2.5  # Text pomalu bledne
            self.img.set_alpha(int(self.alpha))
            surface.blit(self.img, (self.x, self.y))


# =============================================================================
# 4. ENTITY ENGINE (OBJEKTY A JEJICH LOGIKA)
# =============================================================================

class Entity:
    """Základní stavební kámen každého fyzického objektu ve hře."""

    def __init__(self, x, y, w, h):
        self.x, self.y = x, y
        # Rect je obdélník, který se používá k detekci, jestli se objekty srazily (Hitbox)
        self.rect = pygame.Rect(x, y, w, h)


class UpgradeCrate(Entity):
    """Interaktivní bedna s upgradem (Lootbox). Dědí z třídy Entity."""

    def __init__(self):
        # Spawnuje se náhodně na ose X, na ose Y je přesně na pozici hráče
        super().__init__(random.randint(100, WIDTH - 100), PLAYER_Y, 30, 30)
        self.angle = 0  # Úhel pro výpočet levitace

    def draw(self, surface):
        self.angle += 0.1
        # Pomocí matematického sinusu se hodnota cyklicky mění (nahoru/dolů)
        s = 30 + math.sin(self.angle) * 5
        # Vykreslení zlaté bedny
        pygame.draw.rect(surface, (255, 215, 0), (self.x, self.y - s / 4, s, s))
        pygame.draw.rect(surface, (255, 255, 255), (self.x, self.y - s / 4, s, s), 2)


class Enemy(Entity):
    """Architektura nepřátelské jednotky s podporou Hyperprostoru (Warp-in)."""

    def __init__(self, speed_base, stage=1):
        self.target_y = random.randint(40, 150)  # Bojová výška (kam ufo letí)
        # Spawn probíhá extrémně vysoko v záporných hodnotách (aby to vypadalo, že letí z hlubin)
        super().__init__(random.randint(50, WIDTH - 50), random.randint(-600, -200), 32, 32)

        r = random.random()  # Náhodné číslo 0.0 až 1.0 pro výběr typu
        # Určení typu: Normal (50%), Tank (30%), Assassin (20%)
        if r < 0.50:
            self.type, self.hp, self.col, self.spm = "normal", 1, (255, 255, 0), 1.0
        elif r < 0.80:
            self.type, self.hp, self.col, self.spm = "tank", 3, (0, 255, 0), 0.6
        else:
            self.type, self.hp, self.col, self.spm = "assassin", 1, (100, 100, 100), 1.8

        self.max_hp = self.hp  # Uložíme max HP pro výpočet délky healthbaru
        # Určení směru (vx): doleva nebo doprava
        self.vx = speed_base * self.spm * (1 if random.random() > 0.5 else -1)
        self.vy = 40  # O kolik klesne, když narazí do zdi
        self.flash = 0  # Počitadlo pro efekt zbělení při zásahu

        self.state = "warping"  # Počáteční stav
        self.warp_speed = random.uniform(20.0, 35.0)  # Rychlost pádu z hyperprostoru
        self.just_warped = False  # Kontrolní vlajka, že ufo právě vystoupilo z warpu

    def update(self):
        """Stavový automat řídící pohyb ufa."""
        if self.state == "warping":
            self.y += self.warp_speed  # Padá rychle dolů
            if self.y >= self.target_y:
                self.y = self.target_y
                self.state = "active"  # Po dosažení výšky začne bojovat
                self.flash = 12  # Bílý záblesk
                self.just_warped = True  # Způsobí rázovou vlnu
        else:
            self.x += self.vx  # Běžný let do strany
            # Detekce nárazu na okraj obrazovky
            if self.x <= 0 or self.x >= WIDTH - 32:
                self.vx *= -1  # Obrácení směru rychlosti (Odraz)
                self.y += self.vy  # Pokles dolů k hráči
        self.rect.topleft = (self.x, self.y)  # Aktualizace kolizního boxu
        if self.flash > 0: self.flash -= 1


class Boss(Entity):
    """Elitní jednotka s vícestupňovou fází."""

    def __init__(self, level):
        super().__init__(WIDTH // 2 - 80, -200, 160, 80)
        self.max_hp = CFG_BOSS_BASE_HP + (level * CFG_BOSS_HP_INCREMENT)
        self.hp = self.max_hp
        self.vx = 2.0 + (level * 0.1)  # Boss je s každým levelem nepatrně rychlejší
        self.vy = 0.05  # Boss velmi pomalu a neustále klesá
        self.state, self.flash = "intro", 0

    def update(self):
        if self.state == "intro":
            self.y += 1.5
            if self.y >= 80: self.state = "active"  # Jakmile sletí do obrazovky, aktivuje se
        else:
            self.x += self.vx
            if self.x <= 0 or self.x >= WIDTH - 160: self.vx *= -1  # Odraz od stěn
            self.y += self.vy
        self.rect.topleft = (self.x, self.y)
        if self.flash > 0: self.flash -= 1


# =============================================================================
# 5. HLAVNÍ SYSTÉM (CORE SYSTEMS MANAGER)
# =============================================================================

class Game:
    def __init__(self):
        """Spouští se při startu hry. Zapne Pygame, okno a načte data."""
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.canvas = pygame.Surface(
            (WIDTH, HEIGHT))  # Kreslíme na plátno (canvas), které se pak celé zkopíruje na screen
        self.clock = pygame.time.Clock()

        self.load_assets()

        # Načtení systémových fontů v různých velikostech
        self.font_ui = pygame.font.Font('freesansbold.ttf', 20)
        self.font_msg = pygame.font.Font('freesansbold.ttf', 36)
        self.font_warn = pygame.font.Font('freesansbold.ttf', 60)
        self.reset()  # Načtení herní logiky

    def load_assets(self):
        """Dekódování a uložení obrázků lodí z disku do paměti grafické karty."""
        self.player_img = None
        if os.path.exists(CHOSEN_SHIP):
            img = pygame.image.load(CHOSEN_SHIP).convert_alpha()
            self.player_img = pygame.transform.scale(img, (55, 50))  # Zvětšení pro HD

        self.enemy_imgs = {}
        mapping = {"normal": "enemyYellowNormal.png", "tank": "enemyGreenTank.png", "assassin": "enemyBlackScout.png"}
        for key, filename in mapping.items():
            path = os.path.join("data", filename)
            if os.path.exists(path):
                self.enemy_imgs[key] = pygame.transform.scale(pygame.image.load(path).convert_alpha(), (40, 40))

    def reset(self):
        """Tato metoda uvede hru do výchozího stavu nebo na další level."""
        # Aplikace konfiguračních parametrů z hlavičky kódu
        self.player_x, self.player_vx = WIDTH // 2, 0
        self.p_speed = CFG_PLAYER_SPEED
        self.b_speed = CFG_BULLET_SPEED
        self.b_max = CFG_BULLET_MAX
        self.b_rad = CFG_BULLET_SIZE
        self.shields, self.max_shields = CFG_PLAYER_SHIELDS, CFG_PLAYER_SHIELDS

        self.minions, self.m_timer, self.m_cd = 0, 0, 70
        self.score, self.stage, self.state = 0, 1, "playing"
        self.score_sent = False  # Příznak, zda už bylo skóre odesláno na server

        self.invader_speed = CFG_ENEMY_START_SPEED
        self.target_enemy_count = CFG_ENEMY_START_COUNT
        self.next_speed_score = CFG_SCORE_SPEEDUP_GAP
        self.spawn_timer = 0

        # Určení bodů, kdy se stanou speciální události
        self.next_boss_score = CFG_FIRST_BOSS_SCORE
        self.boss_level = 1
        self.next_crate_score = CFG_FIRST_CRATE_SCORE

        self.shake, self.boss_timer, self.muzzle_flash = 0, 0, 0
        self.boss, self.crate = None, None

        # Kolekce (seznamy) pro držení aktuálních objektů na mapě
        self.enemies, self.bullets, self.m_bullets = [], [], []
        self.particles, self.explosions, self.notifs = [], [], []

        # Generování parallaxního pozadí (Hvězdy). Z je hloubka.
        self.stars = []
        for _ in range(180):
            depth = random.uniform(0.2, 1.0)
            self.stars.append([random.randint(0, WIDTH), random.randint(0, HEIGHT), depth * 5.0, int(depth * 2) + 1])

        self.spawn_wave()  # Vyvolání první vlny

    def spawn_wave(self):
        """Vytvoří na mapě počáteční počet nepřátel."""
        for _ in range(self.target_enemy_count):
            self.enemies.append(Enemy(self.invader_speed))

    def handle_events(self):
        """Naslouchá klávesnici a událostem operačního systému (např. zavření křížkem)."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT: return False
            if self.state == "playing":
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT: self.player_vx = -self.p_speed  # Let vlevo
                    if event.key == pygame.K_RIGHT: self.player_vx = self.p_speed  # Let vpravo
                    if event.key == pygame.K_SPACE:
                        if len(self.bullets) < self.b_max:
                            # Výstřel - přidá nový Rect do seznamu bullets
                            self.bullets.append(pygame.Rect(self.player_x + 22, PLAYER_Y, self.b_rad * 2, 16))
                            self.muzzle_flash = 4  # Způsobí záblesk hlavně
                # Zastavení lodi při puštění šipky
                if event.type == pygame.KEYUP and event.key in (pygame.K_LEFT, pygame.K_RIGHT):
                    self.player_vx = 0

            # Stav, kdy si hráč vybírá vylepšení z nabídky
            elif self.state == "choosing" and event.type == pygame.KEYDOWN:
                keys = {pygame.K_1: 0, pygame.K_2: 1, pygame.K_3: 2, pygame.K_4: 3, pygame.K_5: 4}
                if event.key in keys and keys[event.key] < len(self.sel_upgrades):
                    self.apply_upgrade(keys[event.key])  # Potvrzení výběru
        return True

    def apply_upgrade(self, idx):
        """Aplikace modifikátoru na schopnosti lodi hráče podle výběru v menu."""
        u = self.sel_upgrades[idx]
        if u['id'] == "bullets":
            self.b_max = min(8, self.b_max + 1)
        elif u['id'] == "b_speed":
            self.b_speed += 2.0
        elif u['id'] == "b_size":
            self.b_rad += 2
        elif u['id'] == "p_speed":
            self.p_speed += 1.0
        elif u['id'] == "shield_rep":
            self.shields = min(self.max_shields, self.shields + 1)
        elif u['id'] == "minion":
            self.minions += 1
        self.state = "playing"  # Návrat do hry

    def update(self):
        """Centrální mozek: Počítá matematiku pohybu a detekuje kolize. Nebreslí obraz!"""
        if self.state == "game_over" and not self.score_sent:
            self.send_score()

        if self.state != "playing": return

        # 1. Omezení hráče, aby nevyletěl z obrazovky (Clamping)
        self.player_x = max(10, min(WIDTH - 60, self.player_x + self.player_vx))
        if self.muzzle_flash > 0: self.muzzle_flash -= 1

        # 2. Kolize s Lootboxem (Změření vzdálenosti mezi středem lodi a bednou)
        if self.crate:
            if abs(self.player_x - self.crate.x) < 60:
                self.crate = None
                self.state = "choosing"  # Pauza hry
                self.sel_upgrades = random.sample(UPGRADES, 3)  # Náhodný výběr 3 upgradů
                self.stage += 1  # Posun prostředí o 1 úroveň
                self.next_crate_score = self.score + CFG_CRATE_GAP  # Výpočet skóre pro další bednu

        # 3. Generování částic pro efekt trysek lodě (srší oranžová plasma pod lodí)
        for _ in range(2):
            px = self.player_x + 27 + random.uniform(-6, 6)
            col = random.choice([(255, 100, 0), (255, 200, 50), (100, 200, 255)])
            self.particles.append(
                Particle(px, PLAYER_Y + 40, col, vx=0, vy=random.uniform(2.0, 4.0), life=20, size=3.5))

        # 4. Chování podpůrných Dronů (Automaticky střílejí ze stran)
        if self.minions > 0:
            self.m_timer += 1
            if self.m_timer >= self.m_cd:
                self.m_timer = 0  # Reset časovače palby
                for m in range(self.minions):
                    off = 55 * ((m // 2) + 1)
                    # Rozmístění dronů rovnoměrně na levou a pravou stranu
                    mx = self.player_x - off if m % 2 == 0 else self.player_x + off + 45
                    self.m_bullets.append(pygame.Rect(mx, PLAYER_Y + 10, 6, 8))

        # 5. Pohyb hráčových projektilů vzhůru
        for b in self.bullets[:]:
            b.y -= self.b_speed  # Odečítáním y projektil letí nahoru
            # Vizuální stopa (Kouř/Plazma) za střelou
            self.particles.append(Particle(b.centerx, b.bottom, (100, 200, 255), vx=0, vy=0, life=10, size=2.5))
            if b.y < 0: self.bullets.remove(b)  # Smazání střely mimo okno

        for mb in self.m_bullets[:]:
            mb.y -= self.b_speed
            if mb.y < 0: self.m_bullets.remove(mb)

        # 6. Systém Bosse
        if self.boss_timer > 0:
            self.boss_timer -= 1
            self.shake = 2  # Zemětřesení oznamující příchod bosse
            if self.boss_timer == 0:
                self.boss = Boss(self.boss_level)  # Vytvoření instance bosse
                # Zničení všech malých ufonů na obrazovce, aby byl klid na bossfight
                for e in self.enemies:
                    self.explosions.append(Explosion(e.x, e.y, e.col))
                self.enemies.clear()

        elif self.boss:
            self.boss.update()

            # Animace dvou velkých raketových motorů bosse (Emiťáky)
            for _ in range(3):
                px1 = self.boss.x + 30 + random.uniform(-6, 6)
                px2 = self.boss.x + 130 + random.uniform(-6, 6)
                col = random.choice([(255, 50, 0), (200, 100, 0)])
                self.particles.append(
                    Particle(px1, self.boss.y - 5, col, vx=0, vy=-random.uniform(2, 4), life=25, size=4.0))
                self.particles.append(
                    Particle(px2, self.boss.y - 5, col, vx=0, vy=-random.uniform(2, 4), life=25, size=4.0))

            # Pokud boss proletí obranou (Konec hry/ztráta života)
            if self.boss.y + self.boss.rect.height > DEFENSE_LINE_Y:
                self.shields -= 1;
                self.shake = 40;
                self.boss = None
                if self.shields <= 0: self.state = "game_over"

            if self.boss and self.boss.state == "active":
                # Kolize s bossem
                for b in self.bullets + self.m_bullets:
                    # Funkce colliderect kontroluje, zda se obdélníky překrývají
                    if self.boss.rect.colliderect(b):
                        self.boss.hp -= 1;
                        self.boss.flash = 3
                        self.shake = 2
                        # Jiskry ze zásahu
                        for _ in range(5): self.particles.append(Particle(b.x, b.y, (255, 150, 0), size=3.0))

                        # Odstranění střely, která už trefila cíl
                        if b in self.bullets:
                            self.bullets.remove(b)
                        elif b in self.m_bullets:
                            self.m_bullets.remove(b)

                        if self.boss.hp <= 0:
                            # Masivní exploze při zničení bosse
                            self.explosions.append(Explosion(self.boss.x + 80, self.boss.y + 40, (255, 255, 255)))
                            for _ in range(50): self.particles.append(
                                Particle(self.boss.x + 80, self.boss.y + 40, (255, 255, 0), vx=random.uniform(-8, 8),
                                         vy=random.uniform(-8, 8), life=60, size=5.0))
                            self.score += 150;
                            self.boss = None;
                            self.boss_level += 1
                            self.next_boss_score = self.score + CFG_BOSS_GAP
                            break
        else:
            # 7. Běžní nepřátelé (Spawnování vln)
            self.spawn_timer += 1
            # Pokud je ufounů málo, vytvoříme dalšího
            if len(self.enemies) < self.target_enemy_count and self.spawn_timer > CFG_ENEMY_SPAWN_DELAY:
                self.enemies.append(Enemy(self.invader_speed))
                self.spawn_timer = 0

            # Procházení všech aktivních nepřátel
            for e in self.enemies[:]:
                e.update()

                # Zobrazení plamenů trysek u ufonů, kteří už normálně letí (nejsou ve warpu)
                if e.state == "active":
                    for _ in range(1):
                        px1 = e.x + 12 + random.uniform(-2, 2)
                        px2 = e.x + 28 + random.uniform(-2, 2)
                        col = random.choice([(255, 100, 0), (255, 50, 0)])
                        self.particles.append(
                            Particle(px1, e.y, col, vx=0, vy=-random.uniform(1.5, 3.0), life=15, size=2.5))

                # Pokud právě ufo vystoupilo z hyperprostoru, udělá modrou explozi (efekt)
                if e.just_warped:
                    e.just_warped = False
                    self.explosions.append(Explosion(e.x + 16, e.y + 16, (0, 255, 255)))

                # Ufon prorazil spodní obranu hráče
                if e.y > DEFENSE_LINE_Y:
                    self.shields -= 1;
                    self.shake = 30;
                    self.enemies.remove(e)
                    # Gigantický rudý výboj podél celé obranné linie (Simulace přetížení štítu)
                    for _ in range(50):
                        self.particles.append(
                            Particle(random.randint(0, WIDTH), DEFENSE_LINE_Y, (255, 0, 0), vx=random.uniform(-2, 2),
                                     vy=random.uniform(-5, 0), life=40, size=5.0))
                    if self.shields <= 0: self.state = "game_over"
                    continue

                # Systém zásahů (Ufona lze zasáhnout jen v active fázi, ne ve warpu)
                for b in self.bullets + self.m_bullets:
                    # Funkce inflate() nafoukne malou tečku střely na větší obdélník, aby se hráč lépe trefoval
                    if e.rect.colliderect(b.inflate(self.b_rad * 2, self.b_rad * 2)) and e.state == "active":
                        e.hp -= 1;
                        e.flash = 3
                        for _ in range(5): self.particles.append(Particle(b.centerx, b.top, (255, 255, 255), size=2.5))

                        if b in self.bullets:
                            self.bullets.remove(b)
                        elif b in self.m_bullets:
                            self.m_bullets.remove(b)

                        if e.hp <= 0:  # Ufon zemřel
                            self.explosions.append(Explosion(e.x + 16, e.y + 16, e.col))
                            for _ in range(15): self.particles.append(
                                Particle(e.x + 16, e.y + 16, e.col, vx=random.uniform(-4, 4), vy=random.uniform(-4, 4),
                                         size=4.0))
                            self.score += 1;
                            self.enemies.remove(e)

                            # --- MODUL OBTÍŽNOSTI (PROGRESE) ---
                            # Logika odemykání beden a zrychlování po zabití ufona
                            if self.score >= self.next_crate_score and not self.crate:
                                self.crate = UpgradeCrate()

                            if self.score % CFG_SCORE_MORE_ENEMIES == 0:
                                self.target_enemy_count += 1
                                self.notifs.append(Notification("INVASION RISES!", (255, 50, 50), self.font_warn))

                            if self.score >= self.next_speed_score:
                                if self.invader_speed < CFG_ENEMY_MAX_SPEED:
                                    self.invader_speed += CFG_ENEMY_SPEED_BOOST
                                    # Okamžitá aplikace rychlosti na živé ufony s pomocí copysign (aby si zachovali směr doleva/doprava)
                                    for en in self.enemies: en.vx = math.copysign(self.invader_speed * en.spm, en.vx)
                                self.next_speed_score += CFG_SCORE_SPEEDUP_GAP

                            if self.score >= self.next_boss_score:
                                self.boss_timer = 150  # Spustí odpočet příletu bosse
                            break

        # Smazání starých/mrtvých částic z paměti (Garbage Collection pro úsporu RAM)
        for p in self.particles[:]:
            p.update()
            if p.life <= 0: self.particles.remove(p)

    def draw(self):
        """Grafická Pipeline (Render). Zde se pouze kreslí to, co spočítala funkce Update.
        Kreslí se zespodu nahoru (Z-Indexing)."""
        theme = THEMES[(self.stage - 1) % len(THEMES)]
        self.canvas.fill(theme[0])  # Vykreslení modré/fialové plochy vesmíru

        # Vrstva 0: Hvězdy (Vytváří iluzi hloubky - Parallax efekt)
        for s in self.stars:
            s[1] = (s[1] + s[2]) % HEIGHT
            color_mod = max(50, min(255, int(s[2] * 70)))  # Pomalejší hvězdy jsou tmavší
            pygame.draw.circle(self.canvas, (color_mod, color_mod, theme[1][2]), (int(s[0]), int(s[1])), s[3])

        # Perimetr obrany
        pygame.draw.line(self.canvas, (255, 50, 50), (0, DEFENSE_LINE_Y), (WIDTH, DEFENSE_LINE_Y), 2)

        # Vrstva 1: Interaktivní objekty a Částice vzadu
        if self.crate: self.crate.draw(self.canvas)
        for p in self.particles: p.draw(self.canvas)

        # Vrstva 2: Droni (Nakreslíme tečku a okolo ní bílý kruh)
        for m in range(self.minions):
            off = 55 * ((m // 2) + 1)
            mx = self.player_x - off if m % 2 == 0 else self.player_x + off + 45
            pygame.draw.circle(self.canvas, (200, 50, 255), (int(mx), PLAYER_Y + 20), 8)
            pygame.draw.circle(self.canvas, (255, 255, 255), (int(mx), PLAYER_Y + 20), 3)

        # Vrstva 3: Loď hráče a vizuální naklánění
        if self.player_img:
            angle = -self.player_vx * 1.5  # Loď se nakloní podle toho, jak rychle letí do boku
            # Rotozoom se používá, protože zabraňuje ošklivému zubatému zubatění okrajů po rotaci
            rotated_img = pygame.transform.rotozoom(self.player_img, angle, 1)
            new_rect = rotated_img.get_rect(center=(self.player_x + 27, PLAYER_Y + 20))
            self.canvas.blit(rotated_img, new_rect.topleft)

            # Vykreslení záblesku u ústí zbraně, když hráč vystřelí
            if self.muzzle_flash > 0:
                pygame.draw.circle(self.canvas, (255, 255, 200), (int(self.player_x + 27), PLAYER_Y - 5), 10)
        else:
            pygame.draw.polygon(self.canvas, (0, 200, 255),
                                [(self.player_x + 27, PLAYER_Y), (self.player_x, PLAYER_Y + 40),
                                 (self.player_x + 54, PLAYER_Y + 40)])

        # Vrstva 4: Architektura nepřátel
        for e in self.enemies:
            img = self.enemy_imgs.get(e.type)
            if img:
                # Během hyperprostoru vykreslíme protaženou mlhu
                if e.state == "warping":
                    stretched = pygame.transform.scale(img, (20, 160))  # Protažení obrázku
                    pygame.draw.line(self.canvas, (0, 255, 255), (e.x + 16, e.y), (e.x + 16, e.y - 250), 3)
                    glow = stretched.copy()
                    glow.fill((100, 255, 255, 200), special_flags=pygame.BLEND_RGBA_ADD)  # ADD = Aditivní záření plazmy
                    self.canvas.blit(glow, (e.x + 6, e.y - 80))
                else:
                    enemy_angle = e.vx * 3.5
                    rotated_enemy = pygame.transform.rotozoom(img, enemy_angle, 1)
                    enemy_rect = rotated_enemy.get_rect(center=(e.x + 20, e.y + 20))

                    # Speciální Ghost/Phantom trail pro zabijáky, vykreslený kousek ZA lodí
                    if e.type == "assassin" and e.state == "active":
                        ghost = rotated_enemy.copy()
                        ghost.fill((150, 150, 150, 100), special_flags=pygame.BLEND_RGBA_MULT)
                        self.canvas.blit(ghost, (enemy_rect.x - e.vx * 3, enemy_rect.y - e.vy * 0.5))

                    self.canvas.blit(rotated_enemy, enemy_rect.topleft)

                    # Zbělení lodě při poškození
                    if e.flash > 0:
                        f = rotated_enemy.copy()
                        f.fill((255, 255, 255, 180), special_flags=pygame.BLEND_RGBA_MULT)
                        self.canvas.blit(f, enemy_rect.topleft)

                    # Ukazatel zranění (Healthbar) pro tanky, pod nakresleným ufonem
                    if e.max_hp > 1 and e.hp < e.max_hp:
                        bar_w, bar_h = 32, 4
                        fill_w = int((e.hp / e.max_hp) * bar_w)
                        pygame.draw.rect(self.canvas, (255, 0, 0), (e.x + 4, e.y + 42, bar_w, bar_h))  # Červené pozadí
                        pygame.draw.rect(self.canvas, (0, 255, 0),
                                         (e.x + 4, e.y + 42, fill_w, bar_h))  # Zelená aktuální HP
            else:
                pygame.draw.rect(self.canvas, (255, 255, 255) if e.flash else e.col, e.rect)

        # Vrstva 5: Elitní aktér (Boss)
        if self.boss:
            angle = -self.boss.vx * 2.0
            boss_surface = pygame.Surface((self.boss.rect.w, self.boss.rect.h), pygame.SRCALPHA)
            pygame.draw.rect(boss_surface, (100, 0, 0), (0, 0, self.boss.rect.w, self.boss.rect.h))
            pygame.draw.rect(boss_surface, (255, 0, 0), (0, 0, self.boss.rect.w, self.boss.rect.h), 2)

            rotated_boss = pygame.transform.rotate(boss_surface, angle)
            boss_rect = rotated_boss.get_rect(
                center=(self.boss.x + self.boss.rect.w // 2, self.boss.y + self.boss.rect.h // 2))

            self.canvas.blit(rotated_boss, boss_rect.topleft)

            if self.boss.state == "active":
                pygame.draw.rect(self.canvas, (50, 0, 0), (self.boss.x, self.boss.y - 15, self.boss.rect.w, 8))
                pygame.draw.rect(self.canvas, (0, 255, 0), (
                self.boss.x, self.boss.y - 15, int(self.boss.rect.w * (self.boss.hp / self.boss.max_hp)), 8))

        # Vrstva 6: Střely a projektily (S vnějším červeným okrajem a bílým horkým středem)
        for b in self.bullets:
            pygame.draw.circle(self.canvas, (255, 50, 50), b.center, self.b_rad)
            pygame.draw.circle(self.canvas, (255, 255, 255), b.center, self.b_rad // 2)

        for mb in self.m_bullets:
            pygame.draw.circle(self.canvas, (200, 50, 255), mb.center, 4)

        # Vrstva 7: Exploze a informační nápisy vykreslené nad vším ostatním
        for e in self.explosions[:]:
            e.draw(self.canvas)
            if e.alpha <= 0: self.explosions.remove(e)

        for n in self.notifs[:]:
            n.draw(self.canvas)
            if n.alpha <= 0: self.notifs.remove(n)

        # Přeblikávající varování před bossem
        if self.boss_timer > 0 and (self.boss_timer // 15) % 2 == 0:
            txt = self.font_warn.render("WARNING: CRITICAL ENTITY INCOMING", True, (255, 0, 0))
            self.canvas.blit(txt, (WIDTH // 2 - txt.get_width() // 2, HEIGHT // 2 - 100))

        self.draw_hud()  # Vykreslení telemetrického panelu
        if self.state == "choosing": self.draw_upgrade_menu()
        if self.state == "game_over":
            txt = self.font_warn.render("SYSTEM FAILURE", True, (255, 0, 0))
            self.canvas.blit(txt, (WIDTH // 2 - txt.get_width() // 2, HEIGHT // 2 - 50))

        # Finální operace: Zkopírování plátna na monitor a případný posun způsobený otřesem (Camera Shake)
        off_x = random.randint(-self.shake, self.shake) if self.shake > 0 else 0
        off_y = random.randint(-self.shake, self.shake) if self.shake > 0 else 0
        if self.shake > 0: self.shake -= 1
        self.screen.blit(self.canvas, (off_x, off_y))
        pygame.display.flip()

    def send_score(self):
        """Odešle aktuální skóre na server k uložení do databáze."""
        self.score_sent = True
        try:
            r = requests.post(URL_SAVE_SCORE, data={'username': USER, 'score': self.score}, timeout=5)
            if r.text.strip() == "OK":
                self.notifs.append(Notification("SCORE SYNCED!", (0, 255, 0), self.font_msg))
            else:
                print(f"[ERROR] Server return: {r.text}")
                self.notifs.append(Notification("SYNC FAILED", (255, 0, 0), self.font_msg))
        except Exception as e:
            print(f"[ERROR] Sync error: {e}")
            self.notifs.append(Notification("OFFLINE - NOT SAVED", (255, 0, 0), self.font_msg))

    def draw_hud(self):
        """Kreslí ukazatele nahoře vlevo (Skóre, HP atd.)."""
        pygame.draw.rect(self.canvas, (15, 15, 30), (0, 0, WIDTH, 45))
        txt = self.font_ui.render(
            f"SCORE: {self.score} | STAGE: {self.stage} | INTEGRITY: {self.shields}/{self.max_shields} | OP: {USER}",
            True, (255, 255, 255))
        self.canvas.blit(txt, (20, 15))

    def draw_upgrade_menu(self):
        """Kreslí černé poloprůhledné menu pro výběr upgradů."""
        overlay = pygame.Surface((WIDTH, HEIGHT));
        overlay.set_alpha(200);
        overlay.fill((0, 0, 0))
        self.canvas.blit(overlay, (0, 0))
        txt = self.font_msg.render("EVOLUTION SELECT:", True, (255, 215, 0))
        self.canvas.blit(txt, (WIDTH // 2 - txt.get_width() // 2, HEIGHT // 2 - 200))

        start_y = HEIGHT // 2 - 100
        for i, upg in enumerate(self.sel_upgrades):
            ry = start_y + i * 80;
            pygame.draw.rect(self.canvas, upg['col'], (WIDTH // 2 - 200, ry, 400, 60), 2)
            u_txt = self.font_msg.render(f"[{i + 1}] {upg['name']}", True, upg['col'])
            self.canvas.blit(u_txt, (WIDTH // 2 - u_txt.get_width() // 2, ry + 15))

    def run(self):
        """Hlavní nekonečná smyčka hry (Game Loop). Točí se do vypnutí hry."""
        while True:
            if not self.handle_events(): break  # Načetl klávesnici (když false, tak končíme)
            self.update()  # Spočítal pozice a kolize
            self.draw()  # Nakreslil to na obrazovku
            self.clock.tick(FPS)  # Počkal zlomek sekundy, aby jela hra přesně na FPS
        pygame.quit()


# =============================================================================
# 6. INTEGROVANÉ DIAGNOSTICKÉ TESTY (UNIT TESTS)
# =============================================================================
# Tyto testy zkontrolují matematickou a fyzikální stabilitu kódu, aniž by
# musely pouštět grafické okno. To je známka Enterprise a profi vývoje.
# Spouští se v terminálu příkazem: python main.py --test

class TestGameLogic(unittest.TestCase):

    def test_particle_kinetics_and_degradation(self):
        """
        TEST 1: Termodynamika částic
        Ověřuje matematický přepočet tření (zpomalení) a velikosti (vypařování).
        """
        p = Particle(x=0, y=0, color=(255, 0, 0), vx=10.0, vy=0.0, life=30, size=10.0, friction=0.9)
        p.update()  # Vyvoláme 1 krok

        # Test třecí síly (10.0 * 0.9 by mělo být přesně 9.0)
        self.assertAlmostEqual(p.vx, 9.0, msg="Kritická chyba: Výpočet kinetického tření selhal.")
        # Test stárnutí částice
        self.assertEqual(p.life, 29, msg="Kritická chyba: Životnost částice nebyla snížena.")
        # Test zmenšování objemu (10.0 * 0.95 = 9.5)
        self.assertAlmostEqual(p.size, 9.5, msg="Kritická chyba: Částice nemění svůj objem v čase.")

    def test_enemy_boundary_collision(self):
        """
        TEST 2: Modelování kolizí s okrajovou oblastí (Screen Boundary)
        Ověřuje, zda se ufon správně odrazí od stěny a přesune se blíž k hráči.
        """
        enemy = Enemy(speed_base=5.0, stage=1)

        # Nastavíme ufona tak, aby v dalším framu prorazil pravou stěnu
        enemy.state = "active"
        enemy.x = WIDTH - 30
        enemy.y = 100
        enemy.vx = 5.0
        enemy.vy = 40

        enemy.update()  # Ufon narazí do stěny!

        # Očekáváme, že se vx otočí na zápornou hodnotu (letí zpět doleva)
        self.assertTrue(enemy.vx < 0, "Kritická chyba: Nepřítel se neodrazil od okraje obrazovky.")
        # Očekáváme, že klesl o hodnotu vy (100 + 40 = 140)
        self.assertEqual(enemy.y, 140, "Kritická chyba: Nepřítel po odrazu neprovedl taktický sestup.")


# =============================================================================
# BOOTSTRAPPER (Rozcestník)
# =============================================================================
if __name__ == "__main__":
    # Pokud program spustíme přes příkazový řádek s textem "--test", zapnou se testy.
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        print("\n[SYSTÉM] Inicializuji integrované diagnostické testy...\n")
        unittest.main(argv=['first-arg-is-ignored'])
    else:
        # Jinak se normálně spustí herní engine
        Game().run()