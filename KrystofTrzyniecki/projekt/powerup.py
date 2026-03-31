import pygame
import os

class PowerUp:
    def __init__(self, x, y, p_type):
        # Typ bonusu (např. 'repair' pro opravu, 'shield' pro štít)
        self.type = p_type  
        # Vytvoření obdélníku pro kolize (umístění x, y a velikost 40x40)
        self.rect = pygame.Rect(x, y, 40, 40)
        # Rychlost, jakou bonus padá dolů po obrazovce
        self.speed = 3
        
        # Cesta k obrázkům ve složce "picture"
        base_dir = os.path.dirname(__file__)
        img_path = os.path.join(base_dir, "picture", f"{p_type}.png")
        
        try:
            # Pokus o načtení obrázku podle typu bonusu
            self.image = pygame.image.load(img_path).convert_alpha()
            self.image = pygame.transform.scale(self.image, (40, 40))
        except:
            # Pokud obrázek chybí, vytvoří se barevný čtverec jako náhrada
            self.image = pygame.Surface((40, 40))
            colors = {
                'repair': (255, 0, 0),    # Červená
                'shield': (0, 0, 255),    # Modrá
                'rapid': (255, 255, 0),   # Žlutá
                'triple': (0, 255, 0)     # Zelená
            }
            self.image.fill(colors.get(p_type, (255, 255, 255)))

    def update(self):
        # Posun bonusu směrem dolů (přičítání k souřadnici Y)
        self.rect.y += self.speed

    def draw(self, screen):
        # Vykreslení obrázku bonusu na zadanou plochu (obrazovku)
        screen.blit(self.image, self.rect)