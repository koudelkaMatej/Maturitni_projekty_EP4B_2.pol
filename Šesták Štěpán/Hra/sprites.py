# sprites.py
# Herní objekty - hráč (košík) a padající předměty (ovoce, bomby).
# Taky tady je funkce spawn_object která vytváří nové padající objekty.

import random
import pygame
from dataclasses import dataclass, field
from constants import (
    SCREEN_WIDTH, PLAYER_WIDTH, PLAYER_HEIGHT,
    FALL_SIZE, DARK_GRAY, BLACK, GREEN, RED, GOLD, GRAY
)


class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, player_img, speed=6):
        super().__init__()

        # Pokud se obrázek nenačetl, použijeme šedý obdélník jako náhradu
        if player_img:
            self.image = player_img.copy()
        else:
            self.image = pygame.Surface((PLAYER_WIDTH, PLAYER_HEIGHT), pygame.SRCALPHA)
            self.image.fill(DARK_GRAY)
            pygame.draw.rect(self.image, BLACK, self.image.get_rect(), 2)

        self.rect  = self.image.get_rect(midbottom=(x, y))
        self.mask  = pygame.mask.from_surface(self.image)  # pro přesné kolize
        self.speed = speed

    def update(self, keys):
        # Pohyb doleva/doprava pomocí šipek nebo WASD
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.rect.x += self.speed

        # Hráč nesmí vyjet mimo obrazovku
        self.rect.left  = max(self.rect.left,  0)
        self.rect.right = min(self.rect.right, SCREEN_WIDTH)


@dataclass
class FallingObject:
    # Padající objekt (ovoce/bomba). Používám dataclass protože je to jednodušší
    # než klasická třída a pole se inicializují automaticky.
    x:      float
    y:      float
    kind:   str         # 'fruit', 'goldfruit' nebo 'bomb'
    speed:  float
    width:  int    = FALL_SIZE
    height: int    = FALL_SIZE
    image:  object = field(default=None, repr=False)
    color:  tuple  = None
    _mask:  object = field(default=None, init=False, repr=False)  # cache masky

    def get_rect(self):
        return pygame.Rect(int(self.x), int(self.y), self.width, self.height)

    def get_mask(self):
        # Maska se vytvoří jen jednou a pak se cachuje, aby se nemusela počítat každý frame
        if self._mask is None:
            if self.image:
                self._mask = pygame.mask.from_surface(self.image)
            else:
                temp = pygame.Surface((self.width, self.height))
                temp.fill(self.color if self.color else GRAY)
                self._mask = pygame.mask.from_surface(temp)
        return self._mask


def spawn_object(params, assets, speed_mult=1.0):
    # Náhodně vybere typ objektu - ovoce má vyšší šanci než bomba nebo zlaté
    # 6x fruit, 2x bomb, 1x goldfruit
    kinds = ['fruit'] * 6 + ['bomb'] * 2 + ['goldfruit']
    kind  = random.choice(kinds)
    x     = random.randint(0, SCREEN_WIDTH - FALL_SIZE)

    # Rychlost je základní + náhodná odchylka, celé pak vynásobeno speed_mult
    speed = (params['fall_speed'] + random.uniform(-0.5, 1.0)) * speed_mult

    mapping = {
        'fruit':     (assets['fruit'],     GREEN),
        'bomb':      (assets['bomb'],      RED),
        'goldfruit': (assets['goldfruit'], GOLD),
    }
    img, color = mapping[kind]
    return FallingObject(x, 0, kind, speed, image=img, color=color)
