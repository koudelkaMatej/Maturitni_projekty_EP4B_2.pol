import pygame  # Importuje základní knihovnu Pygame pro grafiku
import random  # Importuje modul pro náhodná čísla (pozice, rychlost, rotace)
import os  # Importuje modul pro práci se souborovými cestami
import settings  # Importuje tvůj soubor settings.py pro přístup k rozlišení

class Asteroid:  # Definice třídy pro padající asteroidy
    def __init__(self):  # Inicializační metoda, která se spustí při vytvoření každého asteroidu
        # Výpočet měřítka podle aktuální šířky okna
        self.scale_factor = settings.WIDTH / 800  # Zjistí, kolikrát je okno větší/menší než základ (800px)
        self.base_size = 60  # Nastaví základní velikost asteroidu na 60 pixelů
        self.current_size = int(self.base_size * self.scale_factor)  # Přepočítá velikost podle rozlišení

        base_dir = os.path.dirname(__file__)  # Najde cestu ke složce, kde se nachází tento skript
        path = os.path.join(base_dir, "picture", "asteroid.png")  # Vytvoří cestu k obrázku asteroidu
        
        try:  # Pokusí se nahrát obrázek asteroidu
            img = pygame.image.load(path).convert_alpha()  # Nahraje obrázek s průhledností
            self.image_orig = pygame.transform.scale(img, (self.current_size, self.current_size))  # Zvětší/zmenší ho
        except:  # Pokud se nahrávání nepovede (obrázek chybí)
            self.image_orig = pygame.Surface((self.current_size, self.current_size))  # Vytvoří prázdný čtverec
            self.image_orig.fill((139, 69, 19))  # Vyplní ho hnědou barvou (jako kámen)
            
        self.rect = self.image_orig.get_rect()  # Vytvoří neviditelný obdélník kolem obrázku pro pohyb
        self.rect.x = random.randint(0, max(0, settings.WIDTH - self.rect.width))  # Umístí ho na náhodnou X pozici
        self.rect.y = -self.rect.height  # Umístí ho těsně nad horní okraj obrazovky (aby se plynule objevil)
        
        # Základní rychlost pádu
        self.speed = random.uniform(2, 5) * (settings.HEIGHT / 600)  # Nastaví náhodnou rychlost pádu dolů
        
        # Nastavení rotace
        self.angle = 0  # Počáteční úhel natočení asteroidu
        self.rot_speed = random.randint(-4, 4)  # Náhodná rychlost otáčení (kladná doprava, záporná doleva)
        self.mask = pygame.mask.from_surface(self.image_orig)  # Vytvoří masku pro přesné kolize (podle pixelů)

    def update(self):  # Metoda pro aktualizaci stavu v každém snímku hry
        self.rect.y += self.speed  # Posune asteroid směrem dolů po ose Y
        self.angle = (self.angle + self.rot_speed) % 360  # Změní úhel natočení (udržuje ho v rozmezí 0-359 stupňů)

    def draw(self, screen):  # Metoda pro vykreslení asteroidu na obrazovku
        # Otočí originální obrázek o aktuální úhel
        rotated_image = pygame.transform.rotate(self.image_orig, self.angle)  # Vytvoří novou, otočenou verzi obrázku
        # Tento řádek zajistí, že asteroid při rotaci neposkakuje (vycentruje otočený obrázek na střed původního)
        new_rect = rotated_image.get_rect(center=self.rect.center)  # Spočítá nový obdélník pro vycentrovanou rotaci
        screen.blit(rotated_image, new_rect)  # Vykreslí otočený asteroid na vypočítanou pozici