import unittest
import pygame
from player import Player

class TestPlayerMechanics(unittest.TestCase):
    def setUp(self):
        pygame.init()
        pygame.display.set_mode((1, 1), pygame.HIDDEN)
        self.player = Player("ship1.png")

    def test_hit_loses_life(self):
        start_lives = self.player.lives
        self.player.hit()
        self.assertEqual(self.player.lives, start_lives - 1)
        self.assertTrue(self.player.invincible)

    def test_shield_protects(self):
        start_lives = self.player.lives
        self.player.apply_powerup('shield', 0)
        self.assertTrue(self.player.shield_active)
        self.player.hit()
        self.assertEqual(self.player.lives, start_lives)
        self.assertFalse(self.player.shield_active)

    def tearDown(self):
        pygame.quit()

if __name__ == "__main__":
    unittest.main()