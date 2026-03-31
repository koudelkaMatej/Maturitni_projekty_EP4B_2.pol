import pygame  # Importuje základní knihovnu Pygame pro grafiku a okna
import random  # Importuje modul pro generování náhodných čísel (pozice spawnu)
import os  # Importuje modul pro práci s cestami k souborům (obrázky)
import settings  # Importuje tvůj soubor settings.py pro přístup k obtížnosti a rozlišení

class Enemy:  # Definice třídy pro nepřátelskou loď
    def __init__(self):  # Inicializační metoda, spustí se při vytvoření nepřítele
        # Škálování nepřítele
        self.scale_factor = settings.WIDTH / 800  # Vypočítá poměr zvětšení podle šířky okna
        self.current_size = int(70 * self.scale_factor)  # Určí velikost nepřítele (základ je 70px)
        
        base_dir = os.path.dirname(__file__)  # Najde cestu ke složce, kde je tento skript
        path = os.path.join(base_dir, "picture", "enemy.png")  # Vytvoří cestu k obrázku nepřítele
        
        try:  # Pokusí se načíst obrázek
            img = pygame.image.load(path).convert_alpha()  # Nahraje obrázek s podporou průhlednosti
            self.image = pygame.transform.scale(img, (self.current_size, self.current_size))  # Upraví velikost obrázku
        except:  # Pokud obrázek chybí, vytvoří náhradní grafiku
            self.image = pygame.Surface((self.current_size, self.current_size))  # Vytvoří prázdný čtverec
            self.image.fill(settings.RED)  # Vyplní ho červenou barvou ze settings
            
        self.rect = self.image.get_rect()  # Vytvoří neviditelný obdélník kolem obrázku pro detekci pohybu
        self.mask = pygame.mask.from_surface(self.image)  # Vytvoří masku pro přesnou kolizi podle pixelů
        
        self.rect.x = random.randint(0, max(0, settings.WIDTH - self.rect.width))  # Umístí nepřítele na náhodnou X pozici
        self.rect.y = random.randint(50, 150)  # Umístí nepřítele do horní části obrazovky (Y pozice)
        
        # Nastavení rychlosti a střelby podle aktuálně zvolené obtížnosti
        diff = settings.DIFFICULTIES.get(settings.CURRENT_DIFF, settings.DIFFICULTIES["MEDIUM"])  # Načte data z tabulky v settings
        self.speed = diff["en_speed"] * self.scale_factor  # Nastaví rychlost pohybu do stran
        self.shoot_delay = diff["en_shoot"]  # Nastaví, jak dlouho nepřítel čeká mezi výstřely
        
        self.direction = 1  # Určuje směr pohybu (1 = doprava, -1 = doleva)
        self.last_shot = pygame.time.get_ticks()  # Uloží čas vytvoření, aby nezačal střílet okamžitě

    def update(self):  # Metoda pro aktualizaci pohybu v každém snímku
        self.rect.x += self.speed * self.direction  # Posune nepřítele po ose X podle rychlosti a směru
        
        # Odraz od pravého kraje obrazovky
        if self.rect.right >= settings.WIDTH:  # Pokud pravý okraj nepřítele narazí na konec okna
            self.direction = -1  # Změní směr na doleva
            self.rect.right = settings.WIDTH  # Zarovná nepřítele přesně k okraji
            self.rect.y += 20  # Posune nepřítele o kousek dolů (blíže k hráči)
            
        # Odraz od levého kraje obrazovky
        elif self.rect.left <= 0:  # Pokud levý okraj nepřítele narazí na začátek okna
            self.direction = 1  # Změní směr na doprava
            self.rect.left = 0  # Zarovná nepřítele k levému okraji
            self.rect.y += 20  # Posune nepřítele o kousek dolů

    def draw(self, screen):  # Metoda pro vykreslení nepřítele na obrazovku
        screen.blit(self.image, self.rect)  # Vykreslí obrázek nepřítele na jeho aktuální souřadnice

class EnemyBullet:  # Definice třídy pro střelu, kterou vypálí nepřítel
    def __init__(self, x, y):  # Inicializace střely na pozici (x, y)
        scale_f = settings.WIDTH / 800  # Zjistí poměr škálování pro střely
        base_dir = os.path.dirname(__file__)  # Najde cestu k aktuální složce
        path = os.path.join(base_dir, "picture", "enemy_laser.png")  # Cesta k obrázku laseru
        
        try:  # Pokus o načtení obrázku laseru
            img = pygame.image.load(path).convert_alpha()  # Nahraje obrázek s průhledností
            self.image = pygame.transform.scale(img, (int(15 * scale_f), int(30 * scale_f)))  # Nastaví velikost laseru
        except:  # Náhradní grafika, pokud obrázek laseru neexistuje
            self.image = pygame.Surface((int(10 * scale_f), int(20 * scale_f)))  # Vytvoří malý čtvereček
            self.image.fill((255, 100, 100))  # Vyplní ho světle červenou barvou
            
        self.rect = self.image.get_rect(centerx=x, top=y)  # Umístí střelu přesně tam, kde je loď nepřítele
        self.mask = pygame.mask.from_surface(self.image)  # Vytvoří masku pro detekci zásahu hráče
        self.speed = 5 * (settings.HEIGHT / 600)  # Nastaví rychlost letu střely dolů

    def update(self):  # Metoda pro pohyb střely
        self.rect.y += self.speed  # Posouvá střelu směrem dolů po ose Y

    def draw(self, screen):  # Metoda pro vykreslení střely
        screen.blit(self.image, self.rect)  # Vykreslí laser na obrazovku