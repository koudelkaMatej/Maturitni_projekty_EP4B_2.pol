# assets.py
# Načítání obrázků a fontů. Pokud obrázek chybí, funkce vrátí None
# a hra místo něj vykreslí barevný obdélník - nespadne.

import pygame
from constants import SCREEN_WIDTH, SCREEN_HEIGHT, PLAYER_WIDTH, PLAYER_HEIGHT, FALL_SIZE


def load_image(path, size):
    # Pokusí se načíst obrázek a přescalovat ho. Při chybě vrátí None.
    try:
        img = pygame.image.load(path).convert_alpha()
        return pygame.transform.scale(img, size)
    except (pygame.error, FileNotFoundError):
        return None


def load_all():
    # Načte všechny herní obrázky najednou a vrátí je jako slovník.
    # Obrázky musí být ve složce obrazky/ vedle hra/
    return {
        'background': load_image("obrazky/background.png", (SCREEN_WIDTH, SCREEN_HEIGHT)),
        'player':     load_image("obrazky/Kosik.png",       (PLAYER_WIDTH, PLAYER_HEIGHT)),
        'fruit':      load_image("obrazky/fruit.png",       (FALL_SIZE, FALL_SIZE)),
        'bomb':       load_image("obrazky/bomb.png",        (FALL_SIZE, FALL_SIZE)),
        'goldfruit':  load_image("obrazky/goldfruit.png",   (FALL_SIZE, FALL_SIZE)),
        'heart':      load_image("obrazky/heart.png",       (32, 32)),
    }


def load_fonts():
    # Tři velikosti fontů co se používají v různých částech hry
    return {
        'normal': pygame.font.SysFont(None, 42),
        'large':  pygame.font.SysFont(None, 74),
        'small':  pygame.font.SysFont(None, 36),
    }
