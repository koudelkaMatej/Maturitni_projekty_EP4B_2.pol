"""
test_game.py - Automatizované testy pro Flappy Palach hru

Testuje: Kolizní detekci ptáčka s trubkami a okraji obrazovky
"""

import unittest
import pygame
import sys
import os

# Přidáme cestu k hlavnímu souboru
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Importujeme funkci z hlavního souboru
from flappy_palach_commented import check_collision

class TestGameCollision(unittest.TestCase):
    """
    Test suite pro kolizní detekci ve hře Flappy Palach.
    
    Testuje různé scénáře:
    - Ptáček mezi trubkami (bez kolize)
    - Ptáček narazil do horní trubky
    - Ptáček narazil do spodní trubky
    - Ptáček mimo obrazovku nahoře
    - Ptáček mimo obrazovku dole
    """
    
    def setUp(self):
        """Spustí se před každým testem - připraví testovací data"""
        # Inicializace pygame (potřebné pro Rect objekty)
        pygame.init()
        
        # Konstanty z hry
        self.PIPE_WIDTH = 80
        self.HEIGHT = 800
    
    def test_no_collision_between_pipes(self):
        """Test: Ptáček mezi trubkami - NEMÁ být kolize"""
        # Ptáček uprostřed mezery
        bird_rect = pygame.Rect(150, 400, 50, 50)
        pipe_x = 300
        pipe_height = 200
        gap = 180
        
        result = check_collision(bird_rect, pipe_x, pipe_height, gap)
        
        self.assertFalse(result, "Ptáček mezi trubkami by neměl mít kolizi")
    
    def test_collision_with_top_pipe(self):
        """Test: Ptáček narazil do horní trubky - MÁ být kolize"""
        # Ptáček vysoko, kde je horní trubka
        bird_rect = pygame.Rect(320, 100, 50, 50)
        pipe_x = 300
        pipe_height = 200
        gap = 180
        
        result = check_collision(bird_rect, pipe_x, pipe_height, gap)
        
        self.assertTrue(result, "Ptáček v horní trubce by měl mít kolizi")
    
    def test_collision_with_bottom_pipe(self):
        """Test: Ptáček narazil do spodní trubky - MÁ být kolize"""
        # Ptáček nízko, kde je spodní trubka
        bird_rect = pygame.Rect(320, 600, 50, 50)
        pipe_x = 300
        pipe_height = 200
        gap = 180
        
        result = check_collision(bird_rect, pipe_x, pipe_height, gap)
        
        self.assertTrue(result, "Ptáček ve spodní trubce by měl mít kolizi")
    
    def test_collision_out_of_bounds_top(self):
        """Test: Ptáček mimo obrazovku nahoře - MÁ být kolize"""
        bird_rect = pygame.Rect(150, -10, 50, 50)
        pipe_x = 300
        pipe_height = 200
        gap = 180
        
        result = check_collision(bird_rect, pipe_x, pipe_height, gap)
        
        self.assertTrue(result, "Ptáček mimo obrazovku nahoře by měl mít kolizi")
    
    def test_collision_out_of_bounds_bottom(self):
        """Test: Ptáček mimo obrazovku dole - MÁ být kolize"""
        bird_rect = pygame.Rect(150, 810, 50, 50)
        pipe_x = 300
        pipe_height = 200
        gap = 180
        
        result = check_collision(bird_rect, pipe_x, pipe_height, gap)
        
        self.assertTrue(result, "Ptáček mimo obrazovku dole by měl mít kolizi")

if __name__ == '__main__':
    # Spustí všechny testy a vypíše výsledky
    print("=" * 70)
    print("FLAPPY PALACH - TEST KOLIZNÍ DETEKCE")
    print("=" * 70)
    unittest.main(verbosity=2)
