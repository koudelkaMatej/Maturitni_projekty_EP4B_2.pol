import pygame
import random
import sqlite3
import hashlib
from typing import List, Tuple, Optional
from enum import Enum
from pathlib import Path

# Initialize Pygame - must be done before any pygame functions
pygame.init()

# ==================== CONFIGURATION ====================
# These constants define the game window and grid dimensions
GRID_SIZE = 30  # Size of each cell in pixels
GRID_WIDTH = 10  # Number of columns in the game grid
GRID_HEIGHT = 20  # Number of rows in the game grid
FPS = 60  # Target frames per second for smooth gameplay

# Calculate screen dimensions based on grid size
GAME_WIDTH = GRID_WIDTH * GRID_SIZE  # Width of game area
SIDEBAR_WIDTH = 150  # Width of right sidebar (shows score, level, next piece)
SCREEN_WIDTH = GAME_WIDTH + SIDEBAR_WIDTH  # Total window width
SCREEN_HEIGHT = GRID_HEIGHT * GRID_SIZE  # Total window height

# ==================== COLOR DEFINITIONS ====================
# Define all colors used in the game (RGB tuples)
BLACK = (0, 0, 0)  # Background color
WHITE = (255, 255, 255)  # Text color
GRAY = (128, 128, 128)  # Grid lines
DARK_GRAY = (50, 50, 50)  # Dark backgrounds
LIGHT_GRAY = (200, 200, 200)  # Light text
RED = (255, 0, 0)  # Z-piece color
GREEN = (0, 255, 0)  # S-piece color
BLUE = (0, 0, 255)  # J-piece color
CYAN = (0, 255, 255)  # I-piece color
MAGENTA = (255, 0, 255)  # T-piece color
YELLOW = (255, 255, 0)  # O-piece color
ORANGE = (255, 165, 0)  # L-piece color

# ==================== TETROMINO SHAPE DEFINITIONS ====================
# Dictionary defining all 7 tetromino pieces with their shapes, colors, and rotations
TETROMINOES = {
    'I': {  # I-piece (straight line)
        'color': CYAN,
        'shapes': [
            [[1, 1, 1, 1]],  # Horizontal
            [[1], [1], [1], [1]]  # Vertical
        ]
    },
    'O': {  # O-piece (square) - only one rotation
        'color': YELLOW,
        'shapes': [
            [[1, 1], [1, 1]]
        ]
    },
    'T': {  # T-piece (T-shaped)
        'color': MAGENTA,
        'shapes': [
            [[0, 1, 0], [1, 1, 1]],
            [[1, 0], [1, 1], [1, 0]],
            [[1, 1, 1], [0, 1, 0]],
            [[0, 1], [1, 1], [0, 1]]
        ]
    },
    'S': {  # S-piece (S-shaped)
        'color': GREEN,
        'shapes': [
            [[0, 1, 1], [1, 1, 0]],
            [[1, 0], [1, 1], [0, 1]]
        ]
    },
    'Z': {  # Z-piece (Z-shaped)
        'color': RED,
        'shapes': [
            [[1, 1, 0], [0, 1, 1]],
            [[0, 1], [1, 1], [1, 0]]
        ]
    },
    'J': {  # J-piece (J-shaped)
        'color': BLUE,
        'shapes': [
            [[1, 0, 0], [1, 1, 1]],
            [[1, 1], [1, 0], [1, 0]],
            [[1, 1, 1], [0, 0, 1]],
            [[0, 1], [0, 1], [1, 1]]
        ]
    },
    'L': {  # L-piece (L-shaped)
        'color': ORANGE,
        'shapes': [
            [[0, 0, 1], [1, 1, 1]],
            [[1, 0], [1, 0], [1, 1]],
            [[1, 1, 1], [1, 0, 0]],
            [[1, 1], [0, 1], [0, 1]]
        ]
    }
}

# ==================== GAME STATE ENUM ====================
# Enumeration for different game states/screens
class GameState(Enum):
    LOGIN = 0  # Login screen
    MENU = 1  # Main menu
    PLAYING = 2  # Active gameplay
    GAME_OVER = 3  # Game over screen
    PAUSED = 4  # Paused game
    REGISTER = 5  # Registration screen

# ==================== DATABASE CLASS ====================
# Handles all database operations for users and scores
class Database:
    """
    Manages SQLite database for user authentication and score storage.
    Handles user registration, login, and score saving.
    """
    
    def __init__(self, db_name: str = "tetris.db"):
        """Initialize database connection and create tables if needed"""
        self.db_path = Path(db_name)
        self.init_db()

    def init_db(self):
        """Create database tables if they don't exist"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Create users table for storing login credentials
        c.execute('''CREATE TABLE IF NOT EXISTS users
                     (id INTEGER PRIMARY KEY, username TEXT UNIQUE, password TEXT)''')
        
        # Create scores table for storing game scores with timestamp
        c.execute('''CREATE TABLE IF NOT EXISTS scores
                     (id INTEGER PRIMARY KEY, user_id INTEGER, score INTEGER, level INTEGER, 
                      timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                      FOREIGN KEY(user_id) REFERENCES users(id))''')
        
        conn.commit()
        conn.close()

    @staticmethod
    def hash_password(password: str) -> str:
        """
        Hash a password using SHA-256 for security.
        This ensures passwords are never stored in plain text.
        """
        return hashlib.sha256(password.encode()).hexdigest()

    def register_user(self, username: str, password: str) -> bool:
        """
        Register a new user in the database.
        Returns True if successful, False if username already exists.
        """
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            hashed_pw = self.hash_password(password)
            c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_pw))
            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            # Username already exists
            return False

    def login_user(self, username: str, password: str) -> Optional[int]:
        """
        Authenticate user login.
        Returns user ID if credentials are correct, None if incorrect.
        """
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        hashed_pw = self.hash_password(password)
        
        # Check if username and password match
        c.execute("SELECT id FROM users WHERE username = ? AND password = ?", (username, hashed_pw))
        result = c.fetchone()
        conn.close()
        return result[0] if result else None

    def save_score(self, user_id: int, score: int, level: int):
        """Save a game score to the database"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("INSERT INTO scores (user_id, score, level) VALUES (?, ?, ?)", (user_id, score, level))
        conn.commit()
        conn.close()

    def get_high_scores(self, user_id: int, limit: int = 50) -> List[Tuple[int, int]]:
        """
        Retrieve user's top scores from database.
        Returns list of (score, level) tuples sorted by score descending.
        """
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("SELECT score, level FROM scores WHERE user_id = ? ORDER BY score DESC LIMIT ?", 
                  (user_id, limit))
        results = c.fetchall()
        conn.close()
        return results

# ==================== TETROMINO CLASS ====================
# Represents a single falling tetromino piece
class Tetromino:
    """
    Represents a Tetromino piece in the game.
    Handles piece shape, rotation, position, and color.
    """
    
    def __init__(self, shape_key: str):
        """
        Initialize a new tetromino piece.
        
        Args:
            shape_key: Key in TETROMINOES dict ('I', 'O', 'T', etc.)
        """
        self.key = shape_key
        self.color = TETROMINOES[shape_key]['color']  # Piece color
        self.shapes = TETROMINOES[shape_key]['shapes']  # All rotation states
        self.rotation = 0  # Current rotation state (0-3)
        self.x = GRID_WIDTH // 2 - 1  # Starting x position (middle of grid)
        self.y = 0  # Starting y position (top of grid)

    def get_shape(self) -> List[List[int]]:
        """Get the current shape based on rotation state"""
        return self.shapes[self.rotation % len(self.shapes)]

    def rotate(self):
        """Rotate the piece to next rotation state"""
        self.rotation += 1

# ==================== BOARD CLASS ====================
# Manages the game board grid, collision detection, and line clearing
class Board:
    """
    Represents the game board.
    Handles grid state, collision detection, line clearing, and scoring.
    """
    
    def __init__(self):
        """Initialize empty game board"""
        # 2D grid representing the board (0 = empty, color value = filled)
        self.grid = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.score = 0  # Current game score
        self.level = 1  # Current difficulty level

    def can_place(self, tetromino: Tetromino, x: int, y: int) -> bool:
        """
        Check if a tetromino can be placed at position (x, y).
        Returns True if placement is valid, False if collision or out of bounds.
        
        This checks:
        - Piece doesn't go off the left/right edges
        - Piece doesn't go below the bottom
        - Piece doesn't overlap with existing blocks
        """
        shape = tetromino.get_shape()
        for row_idx, row in enumerate(shape):
            for col_idx, cell in enumerate(row):
                if cell:  # Only check filled cells of the shape
                    grid_x = x + col_idx
                    grid_y = y + row_idx
                    
                    # Check bounds
                    if grid_x < 0 or grid_x >= GRID_WIDTH or grid_y >= GRID_HEIGHT:
                        return False
                    
                    # Check collision with existing blocks
                    if grid_y >= 0 and self.grid[grid_y][grid_x]:
                        return False
        
        return True

    def place_tetromino(self, tetromino: Tetromino):
        """
        Place a tetromino permanently on the board.
        Fills the grid cells with the piece's color.
        """
        shape = tetromino.get_shape()
        for row_idx, row in enumerate(shape):
            for col_idx, cell in enumerate(row):
                if cell:  # Only place filled cells
                    self.grid[tetromino.y + row_idx][tetromino.x + col_idx] = tetromino.color

    def clear_lines(self) -> int:
        """
        Check for and clear complete lines.
        Updates score based on lines cleared and current level.
        Returns number of lines cleared.
        """
        # Filter out completed rows (rows where all cells are filled)
        self.grid = [row for row in self.grid if not all(row)]
        
        # Calculate how many lines were cleared
        cleared = GRID_HEIGHT - len(self.grid)
        
        # Add empty rows to top to maintain grid height
        self.grid = [[0 for _ in range(GRID_WIDTH)] for _ in range(cleared)] + self.grid
        
        # Update score: 100 points per line × current level
        if cleared > 0:
            self.score += cleared * 100 * self.level
            
            # Level up every 500 points
            if self.score // 500 > self.level - 1:
                self.level += 1
        
        return cleared

    def is_game_over(self) -> bool:
        """
        Check if game is over.
        Game ends when pieces reach the top of the board.
        """
        return any(self.grid[0])  # Check if any cells in top row are filled

# ==================== MAIN GAME CLASS ====================
# Controls overall game flow and rendering
class TetrisGame:
    """
    Main game class that orchestrates the entire Tetris game.
    Handles game states, user input, rendering, and game logic.
    """
    
    def __init__(self):
        """Initialize the game window and all game components"""
        # Initialize Pygame display
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Tetris")
        
        # Initialize game timing
        self.clock = pygame.time.Clock()
        
        # Initialize fonts for text rendering
        self.font_large = pygame.font.Font(None, 48)
        self.font_medium = pygame.font.Font(None, 28)
        self.font_small = pygame.font.Font(None, 20)
        
        # Game state
        self.running = True  # Main loop flag
        self.state = GameState.LOGIN  # Start at login screen
        self.db = Database()  # Initialize database
        
        # ===== Login/Register variables =====
        self.username_input = ""  # Current username being typed
        self.password_input = ""  # Current password being typed
        self.input_active = "username"  # Which input field is active
        self.login_error = ""  # Error message to display
        self.current_user_id = None  # ID of logged-in user
        self.current_username = ""  # Name of logged-in user
        
        # ===== Game variables =====
        self.board = Board()  # Game board
        self.current_tetromino = None  # Currently falling piece
        self.next_tetromino = None  # Next piece to spawn
        self.fall_timer = 0  # Counter for piece falling
        self.fall_speed = 30  # Frames between falls (lower = faster)
        
        # ===== Scoreboard variables =====
        self.high_scores = []  # List of user's high scores
        self.scoreboard_page = 0  # Current page in scoreboard

    def start_new_game(self):
        """Initialize a new game"""
        self.board = Board()  # Fresh board
        self.current_tetromino = self.spawn_tetromino()
        self.next_tetromino = self.spawn_tetromino()
        self.state = GameState.PLAYING
        self.fall_timer = 0

    def spawn_tetromino(self) -> Tetromino:
        """
        Create a new random tetromino piece.
        Randomly selects from the 7 tetromino types.
        """
        key = random.choice(list(TETROMINOES.keys()))
        return Tetromino(key)

    def load_high_scores(self):
        """Load user's high scores from database for scoreboard"""
        self.high_scores = self.db.get_high_scores(self.current_user_id, limit=50)

    def process_events(self):
        """
        Handle user input and window events.
        Different handling for each game state.
        """
        for event in pygame.event.get():
            # Handle window close button
            if event.type == pygame.QUIT:
                self.running = False

            # Handle keyboard input
            if event.type == pygame.KEYDOWN:
                if self.state == GameState.LOGIN:
                    self.handle_login_input(event)
                elif self.state == GameState.REGISTER:
                    self.handle_register_input(event)
                elif self.state == GameState.MENU:
                    if event.key == pygame.K_SPACE:
                        self.start_new_game()
                    elif event.key == pygame.K_s:
                        # Show scoreboard
                        self.load_high_scores()
                        # We removed the scoreboard state - now just show it in menu
                        # For now, we'll just show an alert
                        pass
                    elif event.key == pygame.K_ESCAPE:
                        self.logout()
                elif self.state == GameState.PLAYING:
                    self.handle_game_input(event)
                elif self.state == GameState.PAUSED:
                    if event.key == pygame.K_SPACE:
                        self.state = GameState.PLAYING
                    elif event.key == pygame.K_ESCAPE:
                        self.logout()
                elif self.state == GameState.GAME_OVER:
                    if event.key == pygame.K_SPACE:
                        self.start_new_game()
                    elif event.key == pygame.K_ESCAPE:
                        self.logout()

    def handle_login_input(self, event):
        """
        Handle typing on login screen.
        Now 'r' is treated as a regular character, not a register trigger.
        Register link is now only available in web UI.
        """
        if event.key == pygame.K_TAB:
            # Switch between username and password fields
            self.input_active = "password" if self.input_active == "username" else "username"
        elif event.key == pygame.K_BACKSPACE:
            # Delete last character
            if self.input_active == "username":
                self.username_input = self.username_input[:-1]
            else:
                self.password_input = self.password_input[:-1]
        elif event.key == pygame.K_RETURN:
            # Submit login
            self.attempt_login()
        elif event.unicode.isprintable():
            # Add character to active input field
            # Now 'r' is just a normal character, not a special key
            if self.input_active == "username":
                self.username_input += event.unicode
            else:
                self.password_input += event.unicode

    def handle_register_input(self, event):
        """Handle typing on registration screen"""
        if event.key == pygame.K_TAB:
            self.input_active = "password" if self.input_active == "username" else "username"
        elif event.key == pygame.K_BACKSPACE:
            if self.input_active == "username":
                self.username_input = self.username_input[:-1]
            else:
                self.password_input = self.password_input[:-1]
        elif event.key == pygame.K_RETURN:
            self.attempt_register()
        elif event.key == pygame.K_ESCAPE:
            # Go back to login
            self.state = GameState.LOGIN
            self.username_input = ""
            self.password_input = ""
            self.login_error = ""
        elif event.unicode.isprintable():
            if self.input_active == "username":
                self.username_input += event.unicode
            else:
                self.password_input += event.unicode

    def attempt_login(self):
        """Try to log in with provided credentials"""
        if not self.username_input or not self.password_input:
            self.login_error = "Please fill in both fields"
            return
        
        # Check credentials against database
        user_id = self.db.login_user(self.username_input, self.password_input)
        if user_id:
            # Login successful
            self.current_user_id = user_id
            self.current_username = self.username_input
            self.state = GameState.MENU
            self.username_input = ""
            self.password_input = ""
            self.login_error = ""
        else:
            # Login failed
            self.login_error = "Invalid username or password"

    def attempt_register(self):
        """Try to create a new account"""
        if not self.username_input or not self.password_input:
            self.login_error = "Please fill in both fields"
            return
        
        if len(self.password_input) < 4:
            self.login_error = "Password must be at least 4 characters"
            return
        
        # Try to register in database
        if self.db.register_user(self.username_input, self.password_input):
            self.login_error = "Account created! Now login."
            self.state = GameState.LOGIN
            self.username_input = ""
            self.password_input = ""
        else:
            self.login_error = "Username already exists"

    def logout(self):
        """Log out current user and save their score"""
        # Save the final score before logging out
        self.db.save_score(self.current_user_id, self.board.score, self.board.level)
        
        # Clear user session
        self.current_user_id = None
        self.current_username = ""
        self.state = GameState.LOGIN
        self.username_input = ""
        self.password_input = ""
        self.login_error = ""

    def handle_game_input(self, event):
        """Handle keyboard input during gameplay"""
        if event.key == pygame.K_LEFT:
            # Move left
            if self.board.can_place(self.current_tetromino, self.current_tetromino.x - 1, self.current_tetromino.y):
                self.current_tetromino.x -= 1
        elif event.key == pygame.K_RIGHT:
            # Move right
            if self.board.can_place(self.current_tetromino, self.current_tetromino.x + 1, self.current_tetromino.y):
                self.current_tetromino.x += 1
        elif event.key == pygame.K_DOWN:
            # Drop faster
            if self.board.can_place(self.current_tetromino, self.current_tetromino.x, self.current_tetromino.y + 1):
                self.current_tetromino.y += 1
        elif event.key == pygame.K_UP:
            # Rotate piece
            old_rotation = self.current_tetromino.rotation
            self.current_tetromino.rotate()
            # Revert rotation if collision detected
            if not self.board.can_place(self.current_tetromino, self.current_tetromino.x, self.current_tetromino.y):
                self.current_tetromino.rotation = old_rotation
        elif event.key == pygame.K_SPACE:
            # Pause game
            self.state = GameState.PAUSED

    def update(self):
        """
        Update game logic.
        Called once per frame.
        """
        if self.state == GameState.PLAYING:
            # Increment fall timer
            self.fall_timer += 1
            
            # Check if piece should fall
            # Faster fall speed at higher levels (subtract from fall_speed)
            if self.fall_timer >= self.fall_speed - (self.board.level - 1) * 2:
                if self.board.can_place(self.current_tetromino, self.current_tetromino.x, self.current_tetromino.y + 1):
                    # Move piece down
                    self.current_tetromino.y += 1
                    self.fall_timer = 0
                else:
                    # Piece can't fall further - place it on board
                    self.board.place_tetromino(self.current_tetromino)
                    
                    # Check for and clear complete lines
                    self.board.clear_lines()
                    
                    # Check if game is over (pieces reached top)
                    if self.board.is_game_over():
                        self.state = GameState.GAME_OVER
                    else:
                        # Spawn new piece
                        self.current_tetromino = self.next_tetromino
                        self.next_tetromino = self.spawn_tetromino()
                    
                    self.fall_timer = 0

    def draw(self):
        """
        Render everything to screen.
        Called once per frame.
        """
        # Clear screen
        self.screen.fill(BLACK)

        # Draw based on current game state
        if self.state == GameState.LOGIN:
            self.draw_login()
        elif self.state == GameState.REGISTER:
            self.draw_register()
        elif self.state == GameState.MENU:
            self.draw_menu()
        elif self.state == GameState.PLAYING:
            self.draw_game()
        elif self.state == GameState.PAUSED:
            self.draw_game()
            self.draw_paused()
        elif self.state == GameState.GAME_OVER:
            self.draw_game()
            self.draw_game_over()

        # Update display
        pygame.display.flip()

    def draw_login(self):
        """Render login screen"""
        title = self.font_large.render("TETRIS LOGIN", True, CYAN)
        username_label = self.font_small.render("Username:", True, WHITE)
        password_label = self.font_small.render("Password:", True, WHITE)
        register_hint = self.font_small.render("Go to web at localhost:5000 to register", True, GRAY)
        
        # Render input fields (highlight active field in yellow)
        username_text = self.font_medium.render(self.username_input, True, 
                                                YELLOW if self.input_active == "username" else WHITE)
        password_text = self.font_medium.render("*" * len(self.password_input), True,
                                                YELLOW if self.input_active == "password" else WHITE)
        
        # Render error message if any
        error_text = self.font_small.render(self.login_error, True, RED) if self.login_error else None
        
        # Draw all elements
        self.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 80))
        self.screen.blit(username_label, (100, 180))
        self.screen.blit(username_text, (100, 210))
        self.screen.blit(password_label, (100, 270))
        self.screen.blit(password_text, (100, 300))
        if error_text:
            self.screen.blit(error_text, (SCREEN_WIDTH // 2 - error_text.get_width() // 2, 360))
        self.screen.blit(register_hint, (SCREEN_WIDTH // 2 - register_hint.get_width() // 2, 420))

    def draw_register(self):
        """Render registration screen"""
        title = self.font_large.render("CREATE ACCOUNT", True, CYAN)
        username_label = self.font_small.render("Username:", True, WHITE)
        password_label = self.font_small.render("Password (4+ chars):", True, WHITE)
        esc_hint = self.font_small.render("Press ESC to go back", True, GRAY)
        
        username_text = self.font_medium.render(self.username_input, True,
                                                YELLOW if self.input_active == "username" else WHITE)
        password_text = self.font_medium.render("*" * len(self.password_input), True,
                                                YELLOW if self.input_active == "password" else WHITE)
        
        error_text = self.font_small.render(self.login_error, True, 
                                           GREEN if "created" in self.login_error else RED) if self.login_error else None
        
        self.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 80))
        self.screen.blit(username_label, (100, 180))
        self.screen.blit(username_text, (100, 210))
        self.screen.blit(password_label, (100, 270))
        self.screen.blit(password_text, (100, 300))
        if error_text:
            self.screen.blit(error_text, (SCREEN_WIDTH // 2 - error_text.get_width() // 2, 360))
        self.screen.blit(esc_hint, (SCREEN_WIDTH // 2 - esc_hint.get_width() // 2, 420))

    def draw_menu(self):
        """Render main menu screen"""
        title = self.font_large.render("TETRIS", True, CYAN)
        user_text = self.font_small.render(f"Logged in as: {self.current_username}", True, LIGHT_GRAY)
        start = self.font_medium.render("Press SPACE to Start", True, WHITE)
        logout_text = self.font_small.render("Press ESC to Logout", True, GRAY)
        web_hint = self.font_small.render("Visit localhost:5000 to see leaderboard & stats", True, GRAY)
        
        self.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 80))
        self.screen.blit(user_text, (SCREEN_WIDTH // 2 - user_text.get_width() // 2, 150))
        self.screen.blit(start, (SCREEN_WIDTH // 2 - start.get_width() // 2, 240))
        self.screen.blit(web_hint, (SCREEN_WIDTH // 2 - web_hint.get_width() // 2, 300))
        self.screen.blit(logout_text, (SCREEN_WIDTH // 2 - logout_text.get_width() // 2, 400))

    def draw_game(self):
        """Render main game screen during gameplay"""
        # Draw game board background
        pygame.draw.rect(self.screen, DARK_GRAY, (0, 0, GAME_WIDTH, SCREEN_HEIGHT))

        # Draw grid lines
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                rect = pygame.Rect(x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE, GRID_SIZE)
                pygame.draw.rect(self.screen, GRAY, rect, 1)

        # Draw placed blocks on the board
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                if self.board.grid[y][x]:
                    rect = pygame.Rect(x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE, GRID_SIZE)
                    pygame.draw.rect(self.screen, self.board.grid[y][x], rect)

        # Draw current falling tetromino
        if self.current_tetromino:
            shape = self.current_tetromino.get_shape()
            for row_idx, row in enumerate(shape):
                for col_idx, cell in enumerate(row):
                    if cell:
                        x = self.current_tetromino.x + col_idx
                        y = self.current_tetromino.y + row_idx
                        if y >= 0:  # Only draw if visible
                            rect = pygame.Rect(x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE, GRID_SIZE)
                            pygame.draw.rect(self.screen, self.current_tetromino.color, rect)

        # Draw sidebar with score, level, and next piece
        self.draw_sidebar()

    def draw_sidebar(self):
        """Render the right sidebar showing score, level, and next piece preview"""
        sidebar_x = GAME_WIDTH
        
        # Draw sidebar background
        pygame.draw.rect(self.screen, DARK_GRAY, (sidebar_x, 0, SIDEBAR_WIDTH, SCREEN_HEIGHT))

        # Draw score
        score_label = self.font_small.render("SCORE", True, LIGHT_GRAY)
        score_text = self.font_medium.render(str(self.board.score), True, WHITE)
        self.screen.blit(score_label, (sidebar_x + 10, 20))
        self.screen.blit(score_text, (sidebar_x + 10, 45))

        # Draw level
        level_label = self.font_small.render("LEVEL", True, LIGHT_GRAY)
        level_text = self.font_medium.render(str(self.board.level), True, WHITE)
        self.screen.blit(level_label, (sidebar_x + 10, 100))
        self.screen.blit(level_text, (sidebar_x + 10, 125))

        # Draw "NEXT" label
        next_label = self.font_small.render("NEXT", True, LIGHT_GRAY)
        self.screen.blit(next_label, (sidebar_x + 10, 180))

        # Draw next tetromino preview
        if self.next_tetromino:
            shape = self.next_tetromino.get_shape()
            preview_x = sidebar_x + 15
            preview_y = 215
            for row_idx, row in enumerate(shape):
                for col_idx, cell in enumerate(row):
                    if cell:
                        rect = pygame.Rect(
                            preview_x + col_idx * 20,
                            preview_y + row_idx * 20,
                            18, 18
                        )
                        pygame.draw.rect(self.screen, self.next_tetromino.color, rect)

    def draw_paused(self):
        """Render pause screen overlay"""
        # Create semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        paused = self.font_large.render("PAUSED", True, WHITE)
        resume = self.font_small.render("SPACE to Resume | ESC to Logout", True, GRAY)
        self.screen.blit(paused, (SCREEN_WIDTH // 2 - paused.get_width() // 2, SCREEN_HEIGHT // 2 - 40))
        self.screen.blit(resume, (SCREEN_WIDTH // 2 - resume.get_width() // 2, SCREEN_HEIGHT // 2 + 20))

    def draw_game_over(self):
        """Render game over screen with final score"""
        # Create semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(180)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        game_over = self.font_large.render("GAME OVER", True, RED)
        final_score = self.font_medium.render(f"Score: {self.board.score}", True, WHITE)
        restart = self.font_small.render("SPACE to Play Again | ESC to Logout", True, GRAY)
        self.screen.blit(game_over, (SCREEN_WIDTH // 2 - game_over.get_width() // 2, SCREEN_HEIGHT // 2 - 60))
        self.screen.blit(final_score, (SCREEN_WIDTH // 2 - final_score.get_width() // 2, SCREEN_HEIGHT // 2))
        self.screen.blit(restart, (SCREEN_WIDTH // 2 - restart.get_width() // 2, SCREEN_HEIGHT // 2 + 60))

    def run(self):
        """
        Main game loop.
        Runs until self.running is False.
        """
        while self.running:
            # Control frame rate
            self.clock.tick(FPS)
            
            # Handle input
            self.process_events()
            
            # Update game logic
            self.update()
            
            # Render everything
            self.draw()

        # Clean up when done
        pygame.quit()

# ==================== MAIN ENTRY POINT ====================
if __name__ == "__main__":
    # Create and run the game
    game = TetrisGame()
    game.run()