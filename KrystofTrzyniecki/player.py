# player.py
import pygame
from settings import *

class Player:
    def __init__(self):
        
        self.original_image = pygame.image.load("picture/ship1.png").convert_alpha()
        self.image = pygame.transform.scale(self.original_image, (100, 100))

        self.rect = self.image.get_rect()
        self.rect.centerx = WIDTH // 2
        self.rect.bottom = HEIGHT - 20
        self.speed = 5

        
        self.bullet_image = pygame.image.load("picture/laser.png").convert_alpha()
        self.bullet_image = pygame.transform.scale(self.bullet_image, (20, 40))
        self.bullets = []  

    def update(self, keys):
        
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] and self.rect.right < WIDTH:
            self.rect.x += self.speed
        if keys[pygame.K_UP] and self.rect.top > 0:
            self.rect.y -= self.speed
        if keys[pygame.K_DOWN] and self.rect.bottom < HEIGHT:
            self.rect.y += self.speed

        
        for bullet in self.bullets[:]:
            bullet["rect"].y -= 10
            if bullet["rect"].bottom < 0:
                self.bullets.remove(bullet)

    def shoot(self):
        
        bullet_rect = self.bullet_image.get_rect()
        bullet_rect.centerx = self.rect.centerx
        bullet_rect.top = self.rect.top - 10
        self.bullets.append({"rect": bullet_rect, "image": self.bullet_image})

    def draw(self, screen):
        
        screen.blit(self.image, self.rect)

        for bullet in self.bullets:
            screen.blit(bullet["image"], bullet["rect"])
