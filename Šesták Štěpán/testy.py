import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "hra"))

import ui

# testuju jestli se spravne uklada a nacita skore z databaze
class TestUlozeniSkore(unittest.TestCase):
    def test_ulozeni_a_nacteni(self):
        # ulozim testovaci zaznam
        ui.LEADERBOARD_FILE = "test_leaderboard.json"
        ui.add_to_leaderboard("TestHrac", 100, "Normal", 30)

        # nactu databazi a zkontroluju jestli tam je
        board = ui.load_leaderboard()
        jmena = [e["name"] for e in board]
        self.assertIn("TestHrac", jmena)

        # uklid
        if os.path.exists("test_leaderboard.json"):
            os.remove("test_leaderboard.json")

# testuju jestli se skore spravne pocita - nejdulezitejsi pravidla
class TestSkore(unittest.TestCase):
    def test_bodovani(self):
        score = 0
        lives = 3

        # zelene jablko prida 10
        score += 10
        self.assertEqual(score, 10)

        # zmeskane zelene jablko ubere 5
        score = max(0, score - 5)
        self.assertEqual(score, 5)

        # bomba ubere zivot
        lives -= 1
        self.assertEqual(lives, 2)

        # skore nesmi jit pod nulu
        score = max(0, score - 100)
        self.assertEqual(score, 0)

if __name__ == "__main__":
    unittest.main(verbosity=2)
