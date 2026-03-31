# ================================================================= #
# BLOK 1: IMPORTY A NAHRÁVÁNÍ MODULŮ                                #
# Tento odstavec připojuje všechny potřebné knihovny a tvé vlastní  #
# soubory (.py), aby s nimi mohl hlavní program pracovat.           #
# ================================================================= #
import unittest
import sys
import pygame  # Importuje základní knihovnu Pygame pro tvorbu her
import os  # Importuje modul os pro práci se souborovými cestami
import settings  # Importuje tvůj soubor settings.py s konfigurací
import auth  # Importuje tvůj modul auth.py pro přihlašování a skóre
import random  # Importuje modul pro generování náhodných čísel
from player import Player  # Importuje třídu Player z tvého souboru player.py
from asteroid import Asteroid  # Importuje třídu Asteroid ze souboru asteroid.py
from enemy import Enemy, EnemyBullet  # Importuje třídy pro nepřátele a jejich střely
from menu import Menu  # Importuje tvůj systém pro vykreslování menu
from powerup import PowerUp  # Importuje systém pro bonusy (powerupy)

# ================================================================= #
# BLOK 2: NASTAVENÍ HRY PŘI SPUŠTĚNÍ (INICIALIZACE)                #
# Tento odstavec připravuje okno hry, načítá obrázek pozadí a       #
# nastavuje základní proměnné (mince, skiny, stavy menu).           #
# ================================================================= #

#TEST
try:
    import test_game
    print("Spouštím automatické testy...")
    
    # Vytvoříme testovací sadu z tvé třídy v test_game.py
    suite = unittest.TestLoader().loadTestsFromModule(test_game)
    # Spustíme testy (tichý režim, aby to nezdržovalo v konzoli)
    result = unittest.TextTestRunner(verbosity=0).run(suite)
    
    if not result.wasSuccessful():
        print("CHYBA: Testy selhaly! Hra se nespustí, dokud neopravíš chyby.")
        sys.exit(1) # Ukončí program, pokud testy neprojdou
    else:
        print("Testy v pořádku. Spouštím hru...")
except ImportError:
    print("Varování: Soubor test_game.py nebyl nalezen, přeskakuji testy.")
 
#-------------------------------------------------------------------------------

class GameController:  # Definice hlavní třídy, která řídí celou hru
    def __init__(self):  # Inicializační metoda, která se spustí při startu
        pygame.init()  # Zapne všechny vnitřní systémy knihovny Pygame
        self.width = getattr(settings, 'WIDTH', 800)  # Načte šířku okna ze settings nebo nastaví 800
        self.height = getattr(settings, 'HEIGHT', 600)  # Načte výšku okna ze settings nebo nastaví 600
        self.fps = getattr(settings, 'FPS', 60)  # Načte snímkovou frekvenci ze settings nebo nastaví 60
        self.screen = pygame.display.set_mode((self.width, self.height))  # Vytvoří herní okno v daném rozlišení
        pygame.display.set_caption("SPACE SHOOTER")  # Nastaví text v horní liště okna
        self.clock = pygame.time.Clock()  # Vytvoří objekt pro hlídání rychlosti hry (FPS)
        self.font = pygame.font.Font(None, 36)  # Nastaví základní font pro texty v UI
        base_dir = os.path.dirname(__file__)  # Zjistí cestu ke složce, kde je tento soubor
        bg_path = os.path.join(base_dir, "picture", "background.png")  # Vytvoří cestu k obrázku pozadí
        try:  # Blok pro ošetření chyby při načítání obrázku
            self.bg_img = pygame.image.load(bg_path).convert()  # Načte obrázek pozadí do paměti
            self.bg_img = pygame.transform.scale(self.bg_img, (self.width, self.height))  # Upraví velikost pozadí podle okna
        except:  # Spustí se, pokud obrázek pozadí neexistuje
            self.bg_img = pygame.Surface((self.width, self.height))  # Vytvoří prázdnou plochu místo obrázku
            self.bg_img.fill((0, 0, 20))  # Vyplní náhradní plochu tmavě modrou barvou
        self.bg_y = 0  # Nastaví počáteční svislou pozici pozadí pro rolování
        self.total_coins = 10000  # Nastaví počáteční stav mincí pro testování
        self.unlocked_skins = ["ship1.png"]  # Seznam skinů, které má hráč od začátku dostupné
        self.current_skin = "ship1.png"  # Název aktuálně nasazeného skinu lodi
        self.shop_scroll = 0  # Výchozí pozice posuvníku v obchodě se skiny
        self.state = "login"  # Nastaví výchozí stav hry na přihlašovací obrazovku
        self.logged_user = None  # Proměnná pro uložení jména přihlášeného hráče
        self.user_input = ""  # Pomocná proměnná pro ukládání psaného jména
        self.pass_input = ""  # Pomocná proměnná pro ukládání psaného hesla
        self.active_field = "user"  # Určuje, do kterého pole (jméno/heslo) se právě píše
        self.login_error = ""  # Textové pole pro zobrazení chyby přihlášení
        self.is_logging_in = False  # Logická hodnota značící probíhající dotaz na server
        self.menu = Menu(self.screen)  # Vytvoří objekt menu a předá mu plochu okna
        self.player = Player(self.current_skin)  # Vytvoří objekt hráče s vybraným skinem
        self.menu_buttons = {"shop": [], "settings": ([], []), "pause": (None, None), "game_over": (None, None)}  # Slovník pro uložení pozic tlačítek
        self.reset_game()  # Zavolá funkci pro nastavení startovních hodnot hry

# ================================================================= #
# BLOK 3: RESETOVÁNÍ A PŘÍPRAVA NOVÉHO KOLA                        #
# Tento odstavec vymaže staré objekty (nepřátele, střely) a         #
# nastaví herní parametry podle zvolené obtížnosti (Easy/Medium...).#
# ================================================================= #
    def reset_game(self):  # Funkce pro vyčištění scény a restart parametrů
        self.player.load_skin(self.current_skin)  # Načte aktuálně zvolený vzhled lodi
        self.player.reset()  # Vrátí hráče na startovní pozici a obnoví životy
        self.asteroids = []  # Vymaže seznam asteroidů
        self.enemies = []  # Vymaže seznam nepřátel
        self.en_bullets = []  # Vymaže seznam nepřátelských střel
        self.powerups = []  # Vymaže všechny bonusy z obrazovky
        self.score = 0  # Vynuluje aktuální skóre
        self.last_ast = 0  # Vynuluje časovač pro spawn asteroidů
        self.last_en = 0  # Vynuluje časovač pro spawn nepřátel
        self.start_ticks = pygame.time.get_ticks()  # Uloží čas startu aktuálního kola
        diff_settings = settings.DIFFICULTIES.get(settings.CURRENT_DIFF, settings.DIFFICULTIES["MEDIUM"])  # Načte nastavení podle obtížnosti
        self.ast_spawn_time = diff_settings.get("ast_spawn", 1000)  # Nastaví rychlost objevování asteroidů
        self.en_spawn_time = diff_settings.get("en_spawn", 3500)  # Nastaví rychlost objevování nepřátel
        self.en_shoot_time = diff_settings.get("en_shoot", 2500)  # Nastaví prodlevu střelby nepřátel
        self.en_speed = diff_settings.get("en_speed", 3)  # Nastaví základní rychlost pohybu nepřátel
        self.scaling_factor = diff_settings.get("scaling", 0.05)  # Nastaví, jak rychle poroste obtížnost

# ================================================================= #
# BLOK 4: POMOCNÉ FUNKCE (BONUSY A POZADÍ)                         #
# Tento odstavec obsahuje logiku pro náhodné vytváření bonusů a     #
# stará se o to, aby se pozadí vesmíru neustále hýbalo.             #
# ================================================================= #
    def spawn_powerup(self, x, y):  # Funkce pro náhodné vytvoření bonusu na pozici
        if random.random() < 0.20:  # Šance 20%, že po zničení objektu vypadne bonus
            types = ['repair', 'shield', 'rapid', 'triple']  # Seznam možných typů bonusů
            weights = [50, 30, 15, 5]  # Pravděpodobnost výskytu (repair nejčastější)
            p_type = random.choices(types, weights=weights, k=1)[0]  # Vybere jeden bonus podle vah
            self.powerups.append(PowerUp(x, y, p_type))  # Přidá vybraný bonus do hry

    def draw_background(self):  # Funkce pro efekt nekonečného rolování vesmíru
        self.bg_y += 2  # Posune obrázek pozadí o 2 pixely dolů
        if self.bg_y >= self.bg_img.get_height():  # Pokud obrázek odjel celý dolů
            self.bg_y = 0  # Resetuje pozici zpět na nulu
        self.screen.blit(self.bg_img, (0, self.bg_y))  # Vykreslí první kopii pozadí
        self.screen.blit(self.bg_img, (0, self.bg_y - self.bg_img.get_height()))  # Vykreslí druhou kopii nad první

# ================================================================= #
# BLOK 5: HLAVNÍ SMYČKA A ZPRACOVÁNÍ UDÁLOSTÍ (INPUT)              #
# Nejdůležitější část, která běží pořád dokola. Sleduje, jestli     #
# hráč kliká myší, píše jméno nebo stiskl klávesu ESC.              #
# ================================================================= #
    def run(self):  # Hlavní řídící smyčka programu
        while True:  # Nekonečný cyklus běhu aplikace
            now = pygame.time.get_ticks()  # Zjistí aktuální systémový čas v milisekundách
            for e in pygame.event.get():  # Prochází všechny nové události (klávesy, myš)
                if e.type == pygame.QUIT:  # Pokud hráč zavře okno
                    return  # Ukončí funkci a hru
                
                if self.state == "login":  # Logika pokud je hráč v přihlašování
                    if e.type == pygame.KEYDOWN:  # Pokud hráč stiskl klávesu
                        if e.key == pygame.K_RETURN:  # Pokud stiskl Enter
                            if self.user_input and self.pass_input:  # Pokud jsou obě pole vyplněna
                                self.is_logging_in = True  # Nastaví indikátor přihlašování
                                self.menu.draw_login(self.user_input, self.pass_input, self.active_field, self.is_logging_in, self.login_error)  # Překreslí menu
                                pygame.display.flip()  # Okamžitě zobrazí změny
                                res = auth.login_user(self.user_input, self.pass_input)  # Ověří údaje v databázi
                                self.is_logging_in = False  # Zruší indikátor přihlašování
                                if res.get("status") == "success":  # Pokud se přihlášení povedlo
                                    self.logged_user = res["username"]  # Uloží jméno uživatele
                                    self.state = "menu"  # Přepne hru do hlavního menu
                                    self.login_error = ""  # Vymaže případnou předchozí chybu
                                else:  # Pokud se přihlášení nepovedlo
                                    self.login_error = res.get("message", "Error")  # Uloží chybovou zprávu
                            else:  # Pokud nejsou pole vyplněna
                                self.login_error = "Please fill in all fields!"  # Upozorní hráče
                        elif e.key == pygame.K_TAB:  # Pokud stiskl Tabulátor
                            self.active_field = "pass" if self.active_field == "user" else "user"  # Přepne pole pro psaní
                        elif e.key == pygame.K_BACKSPACE:  # Pokud stiskl Backspace (mazání)
                            if self.active_field == "user": 
                                self.user_input = self.user_input[:-1]  # Smaže znak ve jméně
                            else: 
                                self.pass_input = self.pass_input[:-1]  # Smaže znak v hesle
                        else:  # Pokud píše běžné znaky
                            if e.unicode.isprintable():  # Pokud je znak tisknutelný
                                if self.active_field == "user":  # Pokud píše do jména
                                    if len(self.user_input) < 15: 
                                        self.user_input += e.unicode  # Přidá znak do jména
                                else:  # Pokud píše do hesla
                                    if len(self.pass_input) < 20: 
                                        self.pass_input += e.unicode  # Přidá znak do hesla
                
                elif self.state == "menu":  # Logika pro hlavní menu
                    res = self.menu.handle_event(e)  # Předá událost objektu menu a získá výsledek
                    if res == "play": 
                        self.reset_game()
                        self.state = "play"  # Spustí hru
                    elif res == "settings": 
                        self.state = "settings"  # Otevře nastavení
                    elif res == "shop": 
                        self.state = "shop"
                        self.shop_scroll = 0  # Otevře obchod
                    elif res == "exit": 
                        return  # Ukončí program
                
                elif self.state == "shop" and e.type == pygame.MOUSEBUTTONDOWN:  # Logika klikání v obchodě
                    if e.button == 4: 
                        self.shop_scroll = min(0, self.shop_scroll + 30)  # Scroll nahoru kolečkem
                    elif e.button == 5: 
                        self.shop_scroll -= 30  # Scroll dolů kolečkem
                    elif e.button == 1:  # Levé kliknutí myší
                        sb, back = self.menu_buttons["shop"]  # Načte pozice tlačítek v obchodě
                        if back.collidepoint(e.pos): 
                            self.state = "menu"  # Návrat do menu po kliku na zpět
                        else:  # Kliknutí na položku zboží
                            for r, d in sb:  # Prochází všechna zboží
                                if r.collidepoint(e.pos) and 110 < r.centery < settings.HEIGHT - 90:  # Pokud klikl v oblasti
                                    skin_filename, price = d[0], d[1]  # Zjistí název skinu a cenu
                                    if skin_filename in self.unlocked_skins: 
                                        self.current_skin = skin_filename  # Vybere už koupený
                                    elif self.total_coins >= price:  # Pokud má dost peněz
                                        self.total_coins -= price  # Odečte mince
                                        self.unlocked_skins.append(skin_filename)  # Odemkne skin
                                        self.current_skin = skin_filename  # Nastaví ho jako aktivní
                                    break  # Ukončí hledání kliku
                
                elif self.state == "play":  # Logika během samotného hraní
                    if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:  # Pokud stiskl ESC
                        self.pause_start = pygame.time.get_ticks()
                        self.state = "pause"  # Uloží čas a zapne pauzu
                
                elif self.state == "pause" and e.type == pygame.MOUSEBUTTONDOWN:  # Logika v pauze
                    bc, bm = self.menu_buttons["pause"]  # Načte tlačítka v pauze
                    if bc and bc.collidepoint(e.pos):  # Pokud klikl na Pokračovat
                        pd = pygame.time.get_ticks() - self.pause_start  # Spočítá délku pauzy
                        self.start_ticks += pd
                        self.last_ast += pd
                        self.last_en += pd
                        self.state = "play"  # Opraví časy
                    elif bm and bm.collidepoint(e.pos): 
                        self.state = "menu"  # Pokud klikl na Menu
                
                elif self.state == "game_over" and e.type == pygame.MOUSEBUTTONDOWN:  # Logika po prohře
                    br, bm = self.menu_buttons["game_over"]  # Načte tlačítka konce hry
                    if br and br.collidepoint(e.pos): 
                        self.reset_game()
                        self.state = "play"  # Restart hry
                    elif bm and bm.collidepoint(e.pos): 
                        self.state = "menu"  # Návrat do menu
                
                elif self.state == "settings" and e.type == pygame.MOUSEBUTTONDOWN:  # Logika v nastavení
                    db, rb, back = self.menu_buttons["settings"]  # Načte tlačítka nastavení
                    for r, d in db:  # Prochází tlačítka obtížnosti
                        if r.collidepoint(e.pos): 
                            settings.CURRENT_DIFF = d  # Změní obtížnost
                    for r, res in rb:  # Prochází tlačítka rozlišení
                        if r.collidepoint(e.pos):  # Pokud klikl na rozlišení
                            settings.WIDTH, settings.HEIGHT = res  # Změní hodnoty v settings
                            self.screen = pygame.display.set_mode(res)  # Změní velikost okna
                            self.bg_img = pygame.transform.scale(self.bg_img, (settings.WIDTH, settings.HEIGHT))  # Upraví pozadí
                            self.menu.update_buttons()  # Přepočítá pozice tlačítek v menu
                    if back and back.collidepoint(e.pos): 
                        self.state = "menu"  # Návrat do menu

# ================================================================= #
# BLOK 6: FYZIKA, POHYB A KOLIZE (SAMOTNÉ HRANÍ)                   #
# Tento odstavec počítá pohyb střel, nepřátel, zjišťuje nárazy do   #
# lodi a postupně zvyšuje obtížnost hry.                            #
# ================================================================= #
            if self.state == "play":  # Výpočty probíhající jen při aktivní hře
                play_time_sec = (now - self.start_ticks) / 1000  # Spočítá délku aktuálního pokusu v sekundách
                scaling = 1 + (play_time_sec * self.scaling_factor)  # Vypočítá aktuální koeficient obtížnosti
                current_ast_interval = max(300, self.ast_spawn_time / scaling)  # Zkrátí interval asteroidů
                current_en_interval = max(800, self.en_spawn_time / scaling)  # Zkrátí interval nepřátel
                current_en_speed = self.en_speed * (1 + play_time_sec * 0.01)  # Zvýší rychlost nepřátel
                current_en_shoot = max(500, self.en_shoot_time / scaling)  # Zrychlí střelbu nepřátel
                
                if now - self.last_ast > current_ast_interval:  # Pokud je čas na nový asteroid
                    max_ast = max(1, int(scaling))  # Určí kolik asteroidů najednou může vyletět
                    for _ in range(random.randint(1, min(3, max_ast))):  # Vygeneruje 1 až 3 kusy
                        new_ast = Asteroid()
                        new_ast.speed *= (1 + play_time_sec * 0.01)
                        self.asteroids.append(new_ast)  # Přidá asteroid
                    self.last_ast = now  # Uloží čas posledního spawnutí
                
                if now - self.last_en > current_en_interval:  # Pokud je čas na nového nepřítele
                    for _ in range(random.randint(1, min(2, max(1, int(scaling * 0.8) + 1)))):  # Určí počet nepřátel
                        new_enemy = Enemy()
                        new_enemy.speed = current_en_speed
                        new_enemy.shoot_delay = current_en_shoot  # Nastaví mu parametry
                        self.enemies.append(new_enemy)  # Přidá nepřítele do seznamu
                    self.last_en = now  # Uloží čas posledního nepřítele
                
                self.player.update(pygame.key.get_pressed())  # Pohne hráčem podle stisknutých kláves
                
                for b in self.player.bullets[:]:  # Prochází všechny střely hráče
                    if b["rect"].bottom < 0: 
                        self.player.bullets.remove(b)  # Smaže střelu, co vyletěla nahoru
                
                for p in self.powerups[:]:  # Prochází bonusy na ploše
                    p.update()  # Pohne bonusem dolů
                    if p.rect.colliderect(self.player.rect):  # Pokud ho hráč sebral
                        self.player.apply_powerup(p.type, now)
                        self.powerups.remove(p)  # Aktivuje efekt a smaže bonus
                    elif p.rect.top > self.height: 
                        self.powerups.remove(p)  # Smaže bonus, co propadl dolů
                
                for en in self.enemies[:]:  # Prochází nepřátelské lodě
                    en.update()  # Pohne lodí nepřítele
                    if now - en.last_shot > en.shoot_delay:  # Pokud má nepřítel nabito
                        self.en_bullets.append(EnemyBullet(en.rect.centerx, en.rect.bottom))  # Vytvoří nepřátelskou střelu
                        en.last_shot = now  # Resetuje časovač střelby nepřítele
                    if en.rect.colliderect(self.player.rect):  # Kolize nepřítele s hráčem
                        if self.player.mask.overlap(en.mask, (en.rect.x - self.player.rect.x, en.rect.y - self.player.rect.y)):  # Přesná kolize pixelů
                            self.player.hit()
                            self.spawn_powerup(en.rect.centerx, en.rect.centery)
                            self.enemies.remove(en)  # Hráč dostane hit, nepřítel zmizí
                
                for eb in self.en_bullets[:]:  # Prochází střely nepřátel
                    eb.update()  # Pohne střelou dolů
                    if eb.rect.colliderect(self.player.rect):  # Pokud trefila hráče
                        if self.player.mask.overlap(eb.mask, (eb.rect.x - self.player.rect.x, eb.rect.y - self.player.rect.y)):  # Přesná kolize
                            self.player.hit()
                            self.en_bullets.remove(eb)  # Hráč dostane hit, střela zmizí
                    elif eb.rect.top > self.height: 
                        self.en_bullets.remove(eb)  # Smaže střelu pod obrazovkou
                
                for a in self.asteroids[:]:  # Prochází asteroidy
                    a.update()  # Pohne asteroidem dolů
                    if a.rect.colliderect(self.player.rect):  # Kolize asteroidu s hráčem
                        if self.player.mask.overlap(a.mask, (a.rect.x - self.player.rect.x, a.rect.y - self.player.rect.y)):  # Přesná kolize
                            if self.player.hit(): 
                                self.spawn_powerup(a.rect.centerx, a.rect.centery)
                                self.asteroids.remove(a)  # Hit a smazání asteroidu
                    
                    for b in self.player.bullets[:]:  # Zásah asteroidu střelou hráče
                        if a.rect.colliderect(b["rect"]):  # Rychlá kontrola čtverců
                            if "mask" in b and a.mask.overlap(b["mask"], (b["rect"].x - a.rect.x, b["rect"].y - a.rect.y)):  # Přesná kolize
                                if a in self.asteroids: 
                                    self.spawn_powerup(a.rect.centerx, a.rect.centery)
                                    self.asteroids.remove(a)  # Zničí asteroid
                                if b in self.player.bullets: 
                                    self.player.bullets.remove(b)  # Smaže střelu
                                self.score += 100
                                self.total_coins += int(10 * self.player.coin_mod)
                                break  # Přidá body a mince
                    
                    if a in self.asteroids and a.rect.top > self.height: 
                        self.asteroids.remove(a)  # Smaže propadlý asteroid
                
                for en in self.enemies[:]:  # Zásah nepřítele střelou hráče
                    for b in self.player.bullets[:]:  # Prochází střely
                        if en.rect.colliderect(b["rect"]):  # Rychlá kontrola zásahu
                            if "mask" in b and en.mask.overlap(b["mask"], (b["rect"].x - en.rect.x, b["rect"].y - en.rect.y)):  # Přesná kolize
                                if en in self.enemies: 
                                    self.spawn_powerup(en.rect.centerx, en.rect.centery)
                                    self.enemies.remove(en)  # Zničí nepřítele
                                if b in self.player.bullets: 
                                    self.player.bullets.remove(b)  # Smaže střelu
                                self.score += 500
                                self.total_coins += int(50 * self.player.coin_mod)
                                break  # Bonus body za nepřítele

# ================================================================= #
# BLOK 7: VYKRESLOVÁNÍ GRAFIKY NA OBRAZOVKU                        #
# Tento odstavec bere všechna vypočítaná data a kreslí je na monitor.#
# Stará se o pozadí, loď, nepřátele i texty se skóre.               #
# ================================================================= #
                self.draw_background()  # Nakreslí hvězdné nebe
                self.player.draw(self.screen)  # Nakreslí loď hráče a jeho střely
                for p in self.powerups: 
                    p.draw(self.screen)  # Nakreslí všechny aktivní bonusy
                for x in self.asteroids + self.enemies + self.en_bullets: 
                    x.draw(self.screen)  # Nakreslí všechny ostatní objekty
                
                sec = (now - self.start_ticks) // 1000  # Spočítá uplynulé sekundy
                ui_txt = f"SCORE: {self.score}   DANGER: x{round(scaling, 1)}   LIVES: {self.player.lives}   TIME: {sec//60:02d}:{sec%60:02d}"  # Text pro UI
                s = pygame.Surface((self.width, 50), pygame.SRCALPHA)
                s.fill((0, 0, 0, 150))
                self.screen.blit(s, (0,0))  # UI lišta
                self.screen.blit(self.font.render(ui_txt, True, (255,255,255)), (20, 13))  # Vykreslí text UI
                
                if self.player.lives <= 0:  # Kontrola zda hráč neprohrál
                    if self.logged_user: 
                        auth.update_high_score(self.logged_user, self.score)  # Uloží skóre do DB
                    self.state = "game_over"  # Přepne do obrazovky prohry

# ================================================================= #
# BLOK 8: PŘEPÍNÁNÍ MEZI OBRAZOVKAMI (MENU, OBCHOD, ATD.)          #
# Tento odstavec říká Pygame, jakou nabídku má zrovna kreslit       #
# (přihlašování, nastavení, obchod nebo pauzu).                     #
# ================================================================= #
            elif self.state == "login": 
                self.menu.draw_login(self.user_input, self.pass_input, self.active_field, self.is_logging_in, self.login_error)  # Kreslí login
            elif self.state == "menu": 
                self.menu.draw(self.total_coins)  # Kreslí hlavní menu
            elif self.state == "settings": 
                self.menu_buttons["settings"] = self.menu.draw_settings()  # Kreslí nastavení
            elif self.state == "shop": 
                self.menu_buttons["shop"] = self.menu.draw_shop(self.total_coins, self.unlocked_skins, self.current_skin, self.shop_scroll)  # Kreslí shop
            elif self.state == "game_over": 
                self.menu_buttons["game_over"] = self.menu.draw_game_over(self.score)  # Kreslí prohru
            elif self.state == "pause": 
                self.menu_buttons["pause"] = self.menu.draw_pause()  # Kreslí pauzu
            
            pygame.display.flip()  # Aktualizuje celou obrazovku monitoru
            self.clock.tick(self.fps)  # Udržuje hru ve zvoleném FPS

# ================================================================= #
# BLOK 9: SPUŠTĚNÍ A OŠETŘENÍ CHYB                                 #
# Finální odstavec, který vytvoří celou hru a spustí ji. Pokud se   #
# něco pokazí, vypíše chybu do konzole, aby se dala opravit.        #
# ================================================================= #
if __name__ == "__main__":  # Pokud je tento skript spuštěn přímo
    try: 
        GameController().run()  # Vytvoří kontrolér a spustí hru
    except Exception as e:  # Ošetření nečekané chyby
        import traceback
        print(f"CRITICAL ERROR: {e}")
        traceback.print_exc()
        pygame.quit()  # Vypíše chybu a ukončí Pygame