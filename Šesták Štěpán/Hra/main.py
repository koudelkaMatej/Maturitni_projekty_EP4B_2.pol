# main.py
# Vstupní bod celé hry. Inicializuje pygame a spustí hlavní menu.

import pygame
import assets as asset_loader
from screens import main_menu
from constants import SCREEN_WIDTH, SCREEN_HEIGHT


def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("FruitCatcher")
    clock = pygame.time.Clock()

    # Načteme obrázky a fonty
    loaded_assets = asset_loader.load_all()
    fonts         = asset_loader.load_fonts()

    main_menu(screen, loaded_assets, fonts, clock)


if __name__ == "__main__":
    main()
