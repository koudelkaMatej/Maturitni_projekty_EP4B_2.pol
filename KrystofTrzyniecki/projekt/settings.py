# settings.py
import pygame

# --- ZÁKLADNÍ NASTAVENÍ DISPLEJE ---
WIDTH = 800   # Šířka okna v pixelech
HEIGHT = 600  # Výška okna v pixelech
FPS = 60      # Počet snímků za sekundu (ovlivňuje rychlost hry)

# --- DEFINICE BAREV (RGB FORMÁT) ---
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (50, 100, 255)
GRAY = (100, 100, 100)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)

# Možnosti rozlišení pro nastavení v menu
RES_OPTIONS = [(800, 600), (1024, 768), (1280, 720)]

# --- NASTAVENÍ OBTÍŽNOSTÍ ---
# ast_spawn: jak často padají asteroidy (menší číslo = častěji)
# en_spawn: jak často se objevují nepřátelé
# en_shoot: jak rychle nepřátelé střílí
# en_speed: rychlost pohybu nepřátel
# scaling: koeficient, jak moc se obtížnost zvyšuje časem
DIFFICULTIES = {
    "EASY": {
        "ast_spawn": 2000,   
        "en_spawn": 6000,    
        "en_shoot": 3500,
        "en_speed": 2,
        "scaling": 0.02  
    },
    "MEDIUM": {
        "ast_spawn": 1400,   
        "en_spawn": 4500,    
        "en_shoot": 2500,
        "en_speed": 3,
        "scaling": 0.04      
    },
    "HARD": {
        "ast_spawn": 900,    
        "en_spawn": 3000,    
        "en_shoot": 1500,
        "en_speed": 5,
        "scaling": 0.07,
    }
}
CURRENT_DIFF = "MEDIUM" # Výchozí nastavená obtížnost

# --- OBCHOD SE SKINY ---
# Formát: "Název v menu": ["soubor_obrazku.png", cena_v_mincich]
SKIN_DATA = {
    "Základní loď": ["ship1.png", 0],
    "Rychlý letec": ["ship2.png", 500],
    "Těžký křižník": ["ship3.png", 1200],
    "Prototyp X": ["ship4.png", 3000]
}

# --- STATISTIKY JEDNOTLIVÝCH LODÍ ---
# speed: rychlost pohybu hráče
# lives: počet životů na začátku
# fire_rate: prodleva mezi výstřely (menší = střílí rychleji)
# coin_mod: násobič získaných mincí (např. 2.0 = dvojnásobek mincí)
SKIN_STATS = {
    "ship1.png": {"speed": 5, "lives": 3, "fire_rate": 400, "coin_mod": 1.0},
    "ship2.png": {"speed": 8, "lives": 2, "fire_rate": 300, "coin_mod": 1.2},
    "ship3.png": {"speed": 3, "lives": 5, "fire_rate": 500, "coin_mod": 1.5},
    "ship4.png": {"speed": 6, "lives": 4, "fire_rate": 200, "coin_mod": 2.0}
}