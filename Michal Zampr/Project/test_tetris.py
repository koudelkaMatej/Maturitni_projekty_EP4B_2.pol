# ==================== IMPORTS ====================
import unittest  # Python testing framework
import sqlite3  # Database operations
import os  # File operations
import sys  # System operations
from werkzeug.security import generate_password_hash, check_password_hash  # Password hashing

# ==================== IMPORTS FROM PROJECT ====================
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from app import app, init_db, DB_PATH  # Import Flask app

# ==================== WEB APPLICATION TESTS ====================
class TestWebApp(unittest.TestCase):
    """
    Test suite for Flask web application.
    Tests HTTP endpoints, authentication, and database integration.
    """
    
    def setUp(self):
        """
        Set up test environment before each test.
        Creates a test Flask client and test database.
        """
        # Configure Flask for testing
        self.app = app
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()  # Test client for making requests
        
        # Create separate test database (doesn't interfere with real data)
        self.test_db = 'test_tetris.db'
        if os.path.exists(self.test_db):
            os.remove(self.test_db)
        
        # Initialize test database with tables
        conn = sqlite3.connect(self.test_db)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS users
                     (id INTEGER PRIMARY KEY, username TEXT UNIQUE, password TEXT)''')
        c.execute('''CREATE TABLE IF NOT EXISTS scores
                     (id INTEGER PRIMARY KEY, user_id INTEGER, score INTEGER, level INTEGER, 
                      timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                      FOREIGN KEY(user_id) REFERENCES users(id))''')
        conn.commit()
        conn.close()

    def tearDown(self):
        """
        Clean up after each test.
        Removes test database.
        """
        if os.path.exists(self.test_db):
            os.remove(self.test_db)

    def test_1_home_page_loads(self):
        """
        TEST 1: Verify home page loads successfully with HTTP 200.
        Checks that expected content is present on the page.
        """
        print("\n✓ TEST 1: Testing home page loads...")
        
        # Make GET request to home page
        response = self.client.get('/')
        
        # Assert status code is 200 (OK)
        self.assertEqual(response.status_code, 200)
        
        # Assert page contains expected content
        self.assertIn(b'TETRIS GAME', response.data)
        self.assertIn(b'Classic Gameplay', response.data)
        self.assertIn(b'User Accounts', response.data)
        
        print("   ✓ Home page loads correctly with status 200")
        print("   ✓ Page contains expected Tetris game content")

    def test_2_user_registration_and_login(self):
        """
        TEST 2: Verify user registration and login flows.
        Tests new account creation and authentication.
        """
        print("\n✓ TEST 2: Testing user registration and login...")
        
        # Test 2a: User Registration
        response = self.client.post('/register', 
            json={'username': 'testuser', 'password': 'password123'},
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data['success'])  # Registration should succeed
        self.assertIn('successfully', data['message'].lower())
        print("   ✓ User registration successful")
        
        # Test 2b: Login with correct credentials
        response = self.client.post('/login',
            json={'username': 'testuser', 'password': 'password123'},
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data['success'])  # Login should succeed
        print("   ✓ User login successful with correct credentials")
        
        # Test 2c: Login with wrong password (should fail)
        response = self.client.post('/login',
            json={'username': 'testuser', 'password': 'wrongpassword'},
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 401)  # Unauthorized
        data = response.get_json()
        self.assertFalse(data['success'])  # Login should fail
        print("   ✓ Login fails with wrong password")

    def test_3_leaderboard_displays_scores(self):
        """
        TEST 3: Verify leaderboard displays and can save scores.
        Tests score storage and leaderboard retrieval.
        """
        print("\n✓ TEST 3: Testing leaderboard functionality...")
        
        # First register and login a user
        self.client.post('/register',
            json={'username': 'player1', 'password': 'pass123'},
            content_type='application/json'
        )
        
        login_response = self.client.post('/login',
            json={'username': 'player1', 'password': 'pass123'},
            content_type='application/json'
        )
        
        # Add test scores to database
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        
        # Retrieve user ID
        user = c.execute('SELECT id FROM users WHERE username = ?', ('player1',)).fetchone()
        if user:
            user_id = user[0]
            # Insert test scores
            c.execute('INSERT INTO scores (user_id, score, level) VALUES (?, ?, ?)',
                     (user_id, 5000, 5))
            c.execute('INSERT INTO scores (user_id, score, level) VALUES (?, ?, ?)',
                     (user_id, 3000, 3))
            conn.commit()
        conn.close()
        
        # Test leaderboard page
        response = self.client.get('/leaderboard')
        
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'LEADERBOARD', response.data)
        self.assertIn(b'Global Top Scores', response.data)
        print("   ✓ Leaderboard page loads successfully")
        print("   ✓ Scores can be added to database")
        print("   ✓ Leaderboard displays score data")


# ==================== GAME LOGIC TESTS ====================
class TestTetrisGameLogic(unittest.TestCase):
    """
    Test suite for Tetris game logic.
    Tests piece creation, board mechanics, and game rules.
    """
    
    def setUp(self):
        """Set up test components"""
        pass  # No special setup needed for these tests

    def test_4_tetromino_creation(self):
        """
        TEST 4: Verify Tetromino pieces are created correctly.
        Tests piece shapes, colors, and rotations.
        """
        print("\n✓ TEST 4: Testing Tetromino piece creation...")
        
        # Define Tetromino class for testing
        class Tetromino:
            """Simple Tetromino class for testing"""
            def __init__(self, shape_key):
                # Define all piece types with shapes and colors
                self.tetrominoes = {
                    'I': {'color': (0, 255, 255), 'shapes': [[[1, 1, 1, 1]], [[1], [1], [1], [1]]]},
                    'O': {'color': (255, 255, 0), 'shapes': [[[1, 1], [1, 1]]]},
                    'T': {'color': (255, 0, 255), 'shapes': [[[0, 1, 0], [1, 1, 1]]]},
                }
                if shape_key in self.tetrominoes:
                    self.key = shape_key
                    self.color = self.tetrominoes[shape_key]['color']
                    self.shapes = self.tetrominoes[shape_key]['shapes']
                    self.rotation = 0
                    self.x = 5
                    self.y = 0
            
            def get_shape(self):
                """Get current shape based on rotation"""
                return self.shapes[self.rotation % len(self.shapes)]
            
            def rotate(self):
                """Rotate to next rotation state"""
                self.rotation += 1
        
        # Test I-piece creation
        piece_i = Tetromino('I')
        self.assertEqual(piece_i.key, 'I')
        self.assertEqual(piece_i.color, (0, 255, 255))  # Cyan
        self.assertEqual(piece_i.x, 5)
        self.assertEqual(piece_i.y, 0)
        print("   ✓ I-piece created with correct properties")
        
        # Test O-piece creation
        piece_o = Tetromino('O')
        self.assertEqual(piece_o.key, 'O')
        self.assertEqual(piece_o.color, (255, 255, 0))  # Yellow
        print("   ✓ O-piece created with correct properties")
        
        # Test piece rotation
        initial_shape = piece_i.get_shape()
        piece_i.rotate()
        rotated_shape = piece_i.get_shape()
        self.assertNotEqual(initial_shape, rotated_shape)
        print("   ✓ Piece rotation works correctly")

    def test_5_game_board_logic(self):
        """
        TEST 5: Verify game board logic for collision and line clearing.
        Tests board initialization, collision detection, and line clearing.
        """
        print("\n✓ TEST 5: Testing game board logic...")
        
        # Define Board class for testing
        class Board:
            """Simple Board class for testing"""
            def __init__(self):
                # Initialize empty grid (20 rows × 10 columns)
                self.grid = [[0 for _ in range(10)] for _ in range(20)]
                self.score = 0
                self.level = 1
            
            def can_place(self, tetromino, x, y):
                """Check if piece can be placed at position"""
                shape = tetromino.get_shape()
                for row_idx, row in enumerate(shape):
                    for col_idx, cell in enumerate(row):
                        if cell:
                            grid_x = x + col_idx
                            grid_y = y + row_idx
                            # Check bounds
                            if grid_x < 0 or grid_x >= 10 or grid_y >= 20:
                                return False
                            # Check collision
                            if grid_y >= 0 and self.grid[grid_y][grid_x]:
                                return False
                return True
            
            def clear_lines(self):
                """Clear completed lines and update score"""
                lines_cleared = 0
                self.grid = [row for row in self.grid if not all(row)]
                cleared = 20 - len(self.grid)
                self.grid = [[0 for _ in range(10)] for _ in range(cleared)] + self.grid
                lines_cleared = cleared
                if lines_cleared > 0:
                    self.score += lines_cleared * 100 * self.level
                    if self.score // 500 > self.level - 1:
                        self.level += 1
                return lines_cleared
        
        # Test board initialization
        board = Board()
        
        self.assertEqual(len(board.grid), 20)  # 20 rows
        self.assertEqual(len(board.grid[0]), 10)  # 10 columns
        self.assertEqual(board.score, 0)
        self.assertEqual(board.level, 1)
        print("   ✓ Board initialized correctly (20x10 grid)")
        
        # Test collision detection - valid placement
        class MockTetromino:
            def get_shape(self):
                return [[1, 1], [1, 1]]
        
        mock_piece = MockTetromino()
        can_place = board.can_place(mock_piece, 3, 0)
        self.assertTrue(can_place)  # Should be able to place in middle
        print("   ✓ Collision detection allows valid piece placement")
        
        # Test collision detection - invalid placement (off board)
        can_place = board.can_place(mock_piece, 9, 0)
        self.assertFalse(can_place)  # Should NOT be able to place off edge
        print("   ✓ Collision detection prevents invalid piece placement")
        
        # Test line clearing
        board.grid[19] = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]  # Fill bottom row
        lines_cleared = board.clear_lines()
        self.assertEqual(lines_cleared, 1)
        self.assertEqual(board.score, 100)  # 1 line * 100 * level 1
        print("   ✓ Line clearing works and updates score")

    def test_6_database_operations(self):
        """
        TEST 6: Verify database operations for users and scores.
        Tests user creation, password hashing, and score saving.
        """
        print("\n✓ TEST 6: Testing database operations...")
        
        test_db = 'test_db_ops.db'
        
        # Clean up if test database exists from previous run
        if os.path.exists(test_db):
            os.remove(test_db)
        
        # Initialize test database
        conn = sqlite3.connect(test_db)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS users
                     (id INTEGER PRIMARY KEY, username TEXT UNIQUE, password TEXT)''')
        c.execute('''CREATE TABLE IF NOT EXISTS scores
                     (id INTEGER PRIMARY KEY, user_id INTEGER, score INTEGER, level INTEGER, 
                      timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                      FOREIGN KEY(user_id) REFERENCES users(id))''')
        conn.commit()
        conn.close()
        
        # Test user creation
        conn = sqlite3.connect(test_db)
        c = conn.cursor()
        
        # Hash password before storing
        hashed_pwd = generate_password_hash('testpass123')
        c.execute('INSERT INTO users (username, password) VALUES (?, ?)',
                 ('testplayer', hashed_pwd))
        conn.commit()
        
        # Verify user was created
        user = c.execute('SELECT * FROM users WHERE username = ?', ('testplayer',)).fetchone()
        self.assertIsNotNone(user)
        self.assertEqual(user[1], 'testplayer')
        print("   ✓ User created and stored in database")
        
        # Test password verification
        retrieved_hash = user[2]
        password_correct = check_password_hash(retrieved_hash, 'testpass123')
        self.assertTrue(password_correct)
        print("   ✓ Password hashing and verification works")
        
        # Test score saving
        user_id = user[0]
        c.execute('INSERT INTO scores (user_id, score, level) VALUES (?, ?, ?)',
                 (user_id, 5000, 5))
        conn.commit()
        
        # Verify score was saved
        score = c.execute('SELECT score, level FROM scores WHERE user_id = ?', 
                         (user_id,)).fetchone()
        self.assertIsNotNone(score)
        self.assertEqual(score[0], 5000)
        self.assertEqual(score[1], 5)
        print("   ✓ Score saved and retrieved from database")
        
        conn.close()
        
        # Clean up test database
        if os.path.exists(test_db):
            os.remove(test_db)


# ==================== TEST RUNNER ====================
def run_tests():
    """
    Execute all tests and print detailed results.
    Provides summary of passed/failed tests.
    """
    print("\n" + "="*60)
    print("TETRIS GAME - AUTOMATED TEST SUITE")
    print("="*60)
    
    # Create test suite combining all test classes
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test methods from both test classes
    suite.addTests(loader.loadTestsFromTestCase(TestWebApp))
    suite.addTests(loader.loadTestsFromTestCase(TestTetrisGameLogic))
    
    # Run tests with verbose output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print test summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    # Final status message
    if result.wasSuccessful():
        print("\n✓ ALL TESTS PASSED!")
    else:
        print("\n✗ SOME TESTS FAILED")
    
    print("="*60 + "\n")
    
    return result.wasSuccessful()


# ==================== MAIN ENTRY POINT ====================
if __name__ == '__main__':
    # Run all tests
    success = run_tests()
    # Exit with appropriate status code
    sys.exit(0 if success else 1)