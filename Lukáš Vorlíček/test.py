import unittest
import os
import database
import settings
from game_elements import Piece


class TetrisProjectTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        database.DB_PATH = "test_tetris.db"
        if os.path.exists("test_tetris.db"):
            try:
                os.remove("test_tetris.db")
            except:
                pass

    def setUp(self):
        database.init_db()
        with database.get_connection() as conn:
            conn.execute("DELETE FROM high_scores")
            conn.execute("DELETE FROM users")
            conn.commit()

        self.grid = [[0 for _ in range(settings.COLUMNS)] for _ in range(settings.ROWS)]

    def tearDown(self):
        pass

    def test_movement_and_walls(self):
        p = Piece(self.grid, 0)
        p.x = 0
        self.assertFalse(p.valid(dx=-1))
        p.x = settings.COLUMNS - len(p.shape[0])
        self.assertFalse(p.valid(dx=1))

    def test_block_collision(self):
        self.grid[5][5] = (255, 255, 255)
        p = Piece(self.grid, 0)
        p.x, p.y = 5, 4
        self.assertFalse(p.valid(dy=1))

    def test_registration_and_login(self):
        u, p = "lukas_test", "heslo123"
        self.assertTrue(database.register_user(u, p))
        self.assertFalse(database.register_user(u, p))
        uid = database.login_user(u, p)
        self.assertIsNotNone(uid)

    def test_scoring_logic(self):
        def calc(rows, lvl):
            return {1: 100, 2: 300, 3: 700, 4: 1500}.get(rows, 0) * lvl

        self.assertEqual(calc(1, 1), 100)
        self.assertEqual(calc(4, 2), 3000)


if __name__ == '__main__':
    unittest.main()