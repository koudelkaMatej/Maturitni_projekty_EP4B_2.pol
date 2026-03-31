import pygame  # Načte knihovnu Pygame pro tvorbu her
import os      # Načte knihovnu pro práci s cestami k souborům
import settings # Načte tvůj soubor settings.py s nastavením barev a statistik

class Player: # Definice třídy, která reprezentuje hráčovu loď
    def __init__(self, skin_filename="ship1.png"): # Funkce, která se spustí při vytvoření hráče
        self.base_dir = os.path.dirname(__file__) # Zjistí složku, kde se nachází tento skript
        self.current_skin = skin_filename # Uloží si název souboru s obrázkem lodi
        
        # Inicializace seznamu střel a časovačů
        self.bullets = [] # Vytvoří prázdný seznam pro střely, které hráč vystřelí
        self.last_shot = 0 # Uloží čas posledního výstřelu (pro kontrolu kadence)
        self.rapid_fire_timer = 0 # Časovač pro bonus "rychlá střelba"
        self.triple_shot_timer = 0 # Časovač pro bonus "trojitá střela"
        
        # Stavové proměnné
        self.shield_active = False # Informace, zda má hráč aktivní modrý štít
        self.invincible = False # Informace, zda je hráč po zásahu dočasně nesmrtelný
        self.inv_timer = 0 # Časovač pro délku trvání nesmrtelnosti
        self.visible = True # Určuje, zda je loď vidět (používá se pro blikání)
        
        # rect vytvoříme dočasný, load_skin ho správně nastaví
        self.rect = pygame.Rect(0, 0, 1, 1) # Vytvoří pomocný čtverec pro pozici lodi
        
        # TATO FUNKCE NASTAVÍ VŠE PODLE AKTUÁLNÍHO ROZLIŠENÍ
        self.load_skin(skin_filename) # Načte obrázek lodi a její vlastnosti
        self.reset() # Nastaví hráče do startovní pozice na střed

    def update_speeds(self): # Funkce pro přepočet rychlostí podle velikosti okna
        """Přepočítá rychlosti pohybu a střel pro plynulý chod v aktuálním rozlišení."""
        self.scale_f = settings.WIDTH / 800 # Vypočítá poměr zvětšení oproti základní šířce 800
        self.bullet_speed_val = 10 * (settings.HEIGHT / 600) # Upraví rychlost střel podle výšky okna
        self.vx_speed_val = 3 * self.scale_f # Upraví rychlost bočního rozletu střel (u triple shotu)
        
        if hasattr(self, 'base_speed_stat'): # Pokud už známe základní rychlost lodi...
            self.speed = self.base_speed_stat * self.scale_f # ...vynásobí ji poměrem zvětšení

    def load_bullet_assets(self): # Funkce pro načtení obrázku laseru
        """Načte a zvětší obrázek střely podle aktuálního settings.WIDTH."""
        path_laser = os.path.join(self.base_dir, "picture", "laser.png") # Sestaví cestu k obrázku laseru
        b_width = int(20 * self.scale_f) # Vypočítá šířku střely podle měřítka
        b_height = int(40 * self.scale_f) # Vypočítá výšku střely podle měřítka
        
        try: # Zkusí načíst obrázek
            img = pygame.image.load(path_laser).convert_alpha() # Načte obrázek s průhledností
            self.bullet_img = pygame.transform.scale(img, (b_width, b_height)) # Zvětší/zmenší ho
        except: # Pokud obrázek neexistuje...
            self.bullet_img = pygame.Surface((b_width, b_height)) # Vytvoří prázdnou plochu
            self.bullet_img.fill(settings.YELLOW) # Vybarví ji žlutě
        
        self.bullet_mask = pygame.mask.from_surface(self.bullet_img) # Vytvoří masku pro přesné kolize

    def load_skin(self, filename): # Funkce pro načtení vzhledu lodi a jejích statistik
        """Hlavní metoda pro načtení lodi - pokaždé přepočítá velikost."""
        self.current_skin = filename # Uloží aktuální skin
        self.update_speeds() # Přepočítá rychlosti
        self.ship_size = int(110 * self.scale_f) # Vypočítá velikost lodi podle měřítka
        
        path = os.path.join(self.base_dir, "picture", filename) # Cesta k obrázku lodi
        try: # Zkusí načíst obrázek lodi
            img = pygame.image.load(path).convert_alpha() # Načte obrázek lodi
            self.image = pygame.transform.scale(img, (self.ship_size, self.ship_size)) # Změní velikost
        except: # Pokud loď nejde načíst...
            self.image = pygame.Surface((self.ship_size, self.ship_size)) # Vytvoří modrý čtverec
            self.image.fill(settings.BLUE) # Nastaví modrou barvu
        
        self.mask = pygame.mask.from_surface(self.image) # Vytvoří masku lodi pro kolize
        self.load_bullet_assets() # Zaktualizuje i vzhled střel
        
        try: # Zkusí načíst statistiky ze souboru settings.py
            stats = settings.SKIN_STATS[filename] # Vybere data pro konkrétní loď
        except: # Pokud loď v settings není...
            stats = {"speed": 5, "lives": 3, "fire_rate": 300, "coin_mod": 1.0} # Dá základní hodnoty

        self.base_speed_stat = stats["speed"] # Uloží základní rychlost ze statistik
        self.speed = self.base_speed_stat * self.scale_f # Vypočítá aktuální rychlost pohybu
        self.max_lives = stats["lives"] # Nastaví maximální počet životů
        self.shoot_delay = stats["fire_rate"] # Nastaví prodlevu mezi výstřely
        self.coin_mod = stats["coin_mod"] # Nastaví násobič mincí

        # Pokud loď už existovala, zachová její pozici, jinak ji dá na střed
        old_center = self.rect.center if (self.rect.width > 1) else (settings.WIDTH // 2, settings.HEIGHT - 70)
        self.rect = self.image.get_rect(center=old_center) # Vytvoří nový obdélník lodi na správném místě

    def reset(self): # Funkce pro restart hráče
        """Vrátí hráče do základního stavu."""
        self.rect.centerx = settings.WIDTH // 2 # Posune loď horizontálně na střed
        self.rect.bottom = settings.HEIGHT - 20 # Posune loď kousek nad spodní okraj
        self.bullets = [] # Smaže všechny střely na obrazovce
        self.lives = self.max_lives # Obnoví životy na maximum
        self.invincible = False # Vypne nesmrtelnost
        self.inv_timer = 0 # Vynuluje časovač nesmrtelnosti
        self.visible = True # Zviditelní loď
        self.last_shot = 0 # Vynuluje časovač střelby
        self.shield_active = False # Vypne štít

    def hit(self): # Funkce, která se volá při zásahu nepřítelem nebo asteroidem
        """Zpracuje zásah lodi. Vrací True, pokud má být útočník zničen."""
        now = pygame.time.get_ticks() # Zjistí aktuální čas v milisekundách
        if self.invincible: # Pokud je hráč nesmrtelný...
            return False # ...nic se neděje, útočník není zničen

        if self.shield_active: # Pokud má hráč aktivní štít...
            self.shield_active = False # ...štít se zničí
            self.invincible = True # Hráč dostane krátkou nesmrtelnost
            self.inv_timer = now # Uloží se čas zásahu
            return True # Útočník, který do nás narazil, vybuchne

        self.lives -= 1 # Pokud nemáme štít, ubereme jeden život
        self.invincible = True # Zapne se nesmrtelnost po zásahu
        self.inv_timer = now # Uloží se čas zásahu
        return True # Útočník vybuchne

    def update(self, keys): # Funkce, která se volá každý snímek hry
        """Pohyb a logika hráče."""
        now = pygame.time.get_ticks() # Aktuální čas
        
        # Pohyby lodi podle stisknutých kláves a kontrola okrajů obrazovky
        if keys[pygame.K_LEFT] and self.rect.left > 0: self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] and self.rect.right < settings.WIDTH: self.rect.x += self.speed
        if keys[pygame.K_UP] and self.rect.top > 0: self.rect.y -= self.speed
        if keys[pygame.K_DOWN] and self.rect.bottom < settings.HEIGHT: self.rect.y += self.speed

        if keys[pygame.K_SPACE]: # Pokud hráč drží mezerník...
            self.shoot() # ...zkusí vystřelit

        # Aktualizace pozice všech střel
        for b in self.bullets[:]: # Prochází kopii seznamu střel
            b["rect"].y -= self.bullet_speed_val # Posune střelu nahoru
            b["rect"].x += b.get("vx", 0) * self.vx_speed_val # Posune střelu do strany (pokud má šikmý směr)
            if b["rect"].bottom < 0: # Pokud střela vyletí z obrazovky...
                self.bullets.remove(b) # ...smaže ji ze seznamu

        # Logika blikání a konce nesmrtelnosti
        if self.invincible: # Pokud je hráč nesmrtelný
            self.visible = (now // 150) % 2 == 0 # Každých 150ms přepne viditelnost (blikání)
            if now - self.inv_timer > 2000: # Po 2 sekundách (2000ms)...
                self.invincible, self.visible = False, True # ...nesmrtelnost skončí a loď je vidět

    def shoot(self): # Funkce pro samotné vytvoření střel
        """Vytvoří nové střely s aktuálním měřítkem."""
        now = pygame.time.get_ticks() # Aktuální čas
        # Určí prodlevu: pokud běží rapid fire, je prodleva poloviční
        current_delay = self.shoot_delay / 2 if now < self.rapid_fire_timer else self.shoot_delay
        
        if now - self.last_shot > current_delay: # Pokud uplynul dostatek času od posledního výstřelu
            self.last_shot = now # Zapamatuje si čas tohoto výstřelu
            
            if now < self.triple_shot_timer: # Pokud běží bonus trojité střelby
                positions = [ # Definice tří směrů (střed, vlevo, vpravo)
                    {"cx": self.rect.centerx, "vx": 0},
                    {"cx": self.rect.left, "vx": -1.5},
                    {"cx": self.rect.right, "vx": 1.5}
                ]
                for pos in positions: # Pro každý ze tří směrů vytvoří střelu
                    b_rect = self.bullet_img.get_rect(centerx=pos["cx"], top=self.rect.top)
                    self.bullets.append({
                        "rect": b_rect, 
                        "image": self.bullet_img, 
                        "mask": self.bullet_mask, 
                        "vx": pos["vx"]
                    })
            else: # Klasická jedna střela
                b_rect = self.bullet_img.get_rect(centerx=self.rect.centerx, top=self.rect.top)
                self.bullets.append({
                    "rect": b_rect, 
                    "image": self.bullet_img, 
                    "mask": self.bullet_mask, 
                    "vx": 0
                })

    def draw(self, screen): # Funkce pro vykreslení lodi a střel na obrazovku
        """Vykreslení všeho na obrazovku."""
        if self.visible: # Pokud má být loď vidět (nebliká zrovna pryč)
            screen.blit(self.image, self.rect) # Vykreslí obrázek lodi
            
            if self.shield_active: # Pokud je aktivní štít, vykreslí kolem lodi kruh
                inf_w = int(30 * self.scale_f) # Rozšíření štítu do šířky
                inf_h = int(40 * self.scale_f) # Rozšíření štítu do výšky
                shield_rect = self.rect.inflate(inf_w, inf_h) # Vytvoří větší obdélník pro štít
                line_w = max(1, int(4 * self.scale_f)) # Tloušťka čáry štítu
                pygame.draw.ellipse(screen, (50, 150, 255), shield_rect, width=line_w) # Vykreslí modrou elipsu

        for b in self.bullets: # Pro každou střelu v seznamu...
            screen.blit(b["image"], b["rect"]) # ...ji vykreslí na její pozici

    def apply_powerup(self, p_type, current_time): # Funkce pro sebrání bonusu
        """Aplikuje efekt powerupu přímo na hráče."""
        if p_type == 'repair': # Pokud je to oprava...
            self.lives = min(self.lives + 1, self.max_lives) # ...přidá život (maximálně do plna)
        elif p_type == 'shield': # Pokud je to štít...
            self.shield_active = True # ...zapne štít
        elif p_type == 'rapid': # Pokud je to rychlá střelba...
            self.rapid_fire_timer = current_time + 8000 # ...nastaví bonus na 8 sekund
        elif p_type == 'triple': # Pokud je to trojitá střela...
            self.triple_shot_timer = current_time + 10000 # ...nastaví bonus na 10 sekund