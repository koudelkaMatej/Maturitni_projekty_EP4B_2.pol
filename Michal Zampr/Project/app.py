# ==================== IMPORTS ====================
from flask import Flask, render_template_string, request, jsonify, session, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import os
from datetime import datetime
from functools import wraps

# ==================== FLASK APP INITIALIZATION ====================
# Create Flask application instance
app = Flask(__name__)

# Set secret key for session management (should be changed in production)
app.secret_key = 'your-secret-key-change-this'

# ==================== CONFIGURATION ====================
# Path to SQLite database (same one used by Pygame game)
DB_PATH = 'tetris.db'

# ==================== DATABASE FUNCTIONS ====================
def get_db_connection():
    """
    Create and return a database connection.
    Sets row_factory to return rows as dictionaries (accessible by column name).
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Allow dict-like access to rows
    return conn

def init_db():
    """
    Initialize the database by creating tables if they don't exist.
    This is called when the app starts.
    """
    if not os.path.exists(DB_PATH):
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        
        # Create users table
        c.execute('''CREATE TABLE IF NOT EXISTS users
                     (id INTEGER PRIMARY KEY, username TEXT UNIQUE, password TEXT)''')
        
        # Create scores table
        c.execute('''CREATE TABLE IF NOT EXISTS scores
                     (id INTEGER PRIMARY KEY, user_id INTEGER, score INTEGER, level INTEGER, 
                      timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                      FOREIGN KEY(user_id) REFERENCES users(id))''')
        
        conn.commit()
        conn.close()

# ==================== DECORATORS ====================
def login_required(f):
    """
    Decorator to require login for certain routes.
    Redirects to home page if user is not logged in.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:  # Check if user_id is in session
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

# ==================== ROUTES ====================

@app.route('/')
def index():
    """
    Home page route.
    Displays game description and features.
    """
    return render_template_string(INDEX_TEMPLATE, session=session)

@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    Login route.
    GET: Display login form
    POST: Process login credentials
    """
    if request.method == 'POST':
        # Get JSON data from request
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        # Validate input
        if not username or not password:
            return jsonify({'success': False, 'message': 'Username and password required'}), 400
        
        # Query database for user
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        conn.close()
        
        # Check if user exists and password is correct
        if user and check_password_hash(user['password'], password):
            # Login successful - set session variables
            session['user_id'] = user['id']
            session['username'] = user['username']
            return jsonify({'success': True, 'message': 'Login successful'})
        else:
            # Login failed
            return jsonify({'success': False, 'message': 'Invalid username or password'}), 401
    
    return render_template_string(LOGIN_TEMPLATE, session=session)

@app.route('/register', methods=['GET', 'POST'])
def register():
    """
    Registration route.
    GET: Display registration form
    POST: Create new user account
    """
    if request.method == 'POST':
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        # Validate input
        if not username or not password:
            return jsonify({'success': False, 'message': 'Username and password required'}), 400
        
        if len(password) < 4:
            return jsonify({'success': False, 'message': 'Password must be at least 4 characters'}), 400
        
        # Try to insert new user
        conn = get_db_connection()
        try:
            # Hash password before storing
            conn.execute('INSERT INTO users (username, password) VALUES (?, ?)',
                        (username, generate_password_hash(password)))
            conn.commit()
            conn.close()
            return jsonify({'success': True, 'message': 'Account created successfully! Please login.'})
        except sqlite3.IntegrityError:
            # Username already exists
            conn.close()
            return jsonify({'success': False, 'message': 'Username already exists'}), 400
    
    return render_template_string(REGISTER_TEMPLATE, session=session)

@app.route('/logout')
def logout():
    """
    Logout route.
    Clears session and redirects to home page.
    """
    session.clear()
    return redirect(url_for('index'))

@app.route('/leaderboard')
def leaderboard():
    """
    Leaderboard route.
    Displays global top 50 scores and user's personal scores.
    """
    conn = get_db_connection()
    
    # Get global top 50 scores
    global_scores = conn.execute('''
        SELECT users.username, scores.score, scores.level, scores.timestamp
        FROM scores
        JOIN users ON scores.user_id = users.id
        ORDER BY scores.score DESC
        LIMIT 50
    ''').fetchall()
    
    # Get current user's top 20 scores (if logged in)
    user_scores = None
    if 'user_id' in session:
        user_scores = conn.execute('''
            SELECT score, level, timestamp
            FROM scores
            WHERE user_id = ?
            ORDER BY score DESC
            LIMIT 20
        ''', (session['user_id'],)).fetchall()
    
    conn.close()
    
    return render_template_string(LEADERBOARD_TEMPLATE, session=session, global_scores=global_scores, user_scores=user_scores)

@app.route('/database-schema')
def database_schema():
    """
    Database schema route.
    Displays visual ER diagram and table schema information.
    """
    return render_template_string(DATABASE_SCHEMA_TEMPLATE, session=session)

@app.route('/profile')
@login_required  # Require login to access this page
def profile():
    """
    User profile route.
    Displays user statistics and recent game history.
    Only accessible when logged in.
    """
    conn = get_db_connection()
    
    # Get user statistics (aggregated from scores)
    stats = conn.execute('''
        SELECT 
            COUNT(*) as total_games,
            MAX(score) as best_score,
            AVG(score) as avg_score,
            MAX(level) as best_level
        FROM scores
        WHERE user_id = ?
    ''', (session['user_id'],)).fetchone()
    
    # Get user's 10 most recent games
    recent_scores = conn.execute('''
        SELECT score, level, timestamp
        FROM scores
        WHERE user_id = ?
        ORDER BY timestamp DESC
        LIMIT 10
    ''', (session['user_id'],)).fetchall()
    
    conn.close()
    
    return render_template_string(PROFILE_TEMPLATE, session=session, stats=stats, recent_scores=recent_scores)

# ==================== TEMPLATES ====================
# All HTML templates are embedded as strings below
# Templates use Jinja2 syntax for dynamic content

INDEX_TEMPLATE = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Tetris Game - Home</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Courier New', monospace;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            color: #fff;
            min-height: 100vh;
        }
        header {
            background: rgba(0, 0, 0, 0.5);
            padding: 20px;
            border-bottom: 3px solid #00d4ff;
        }
        nav {
            display: flex;
            justify-content: space-between;
            align-items: center;
            max-width: 1200px;
            margin: 0 auto;
        }
        .logo {
            font-size: 28px;
            font-weight: bold;
            color: #00d4ff;
            text-decoration: none;
        }
        nav ul {
            list-style: none;
            display: flex;
            gap: 30px;
        }
        nav a {
            color: #fff;
            text-decoration: none;
            transition: color 0.3s;
            font-size: 16px;
        }
        nav a:hover { color: #00d4ff; }
        .user-info {
            display: flex;
            gap: 20px;
            align-items: center;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 40px 20px;
        }
        .btn {
            padding: 12px 24px;
            background: #00d4ff;
            color: #000;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-weight: bold;
            transition: all 0.3s;
            font-family: 'Courier New', monospace;
            text-decoration: none;
            display: inline-block;
        }
        .btn:hover {
            background: #00a8cc;
            transform: scale(1.05);
        }
        .btn-secondary {
            background: #ff006e;
        }
        .btn-secondary:hover {
            background: #d60057;
        }
        h1, h2 {
            color: #00d4ff;
            margin-bottom: 20px;
        }
        footer {
            text-align: center;
            padding: 20px;
            background: rgba(0, 0, 0, 0.5);
            border-top: 2px solid #00d4ff;
            margin-top: 50px;
        }
        .hero {
            text-align: center;
            padding: 60px 0;
        }
        .hero h1 {
            font-size: 64px;
            margin-bottom: 20px;
            text-shadow: 0 0 20px #00d4ff;
        }
        .hero p {
            font-size: 18px;
            margin-bottom: 30px;
            color: #ccc;
        }
        .cta-buttons {
            display: flex;
            gap: 20px;
            justify-content: center;
            margin-bottom: 60px;
        }
        .features {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 30px;
            margin: 60px 0;
        }
        .feature-card {
            background: rgba(0, 212, 255, 0.1);
            border: 2px solid #00d4ff;
            border-radius: 10px;
            padding: 30px;
            transition: all 0.3s;
        }
        .feature-card:hover {
            transform: translateY(-10px);
            box-shadow: 0 0 20px rgba(0, 212, 255, 0.3);
        }
        .feature-card h3 {
            color: #00d4ff;
            margin-bottom: 15px;
        }
        .feature-card p {
            color: #ccc;
            line-height: 1.6;
        }
        .description {
            background: rgba(0, 0, 0, 0.3);
            border-left: 4px solid #ff006e;
            padding: 30px;
            margin: 40px 0;
            border-radius: 5px;
        }
        .game-rules {
            background: rgba(0, 0, 0, 0.3);
            padding: 30px;
            border-radius: 10px;
            margin: 40px 0;
        }
        .game-rules ol {
            margin-left: 20px;
            line-height: 2;
        }
        .controls {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 20px;
            margin: 30px 0;
        }
        .control-item {
            background: rgba(255, 0, 110, 0.1);
            padding: 15px;
            border-radius: 5px;
            border-left: 3px solid #ff006e;
        }
        .control-item strong {
            color: #00d4ff;
        }
    </style>
</head>
<body>
    <header>
        <nav>
            <a href="/" class="logo">🎮 TETRIS</a>
            <ul>
                <li><a href="/">Home</a></li>
                <li><a href="/leaderboard">Leaderboard</a></li>
                <li><a href="/database-schema">Database</a></li>
                {% if session.user_id %}
                    <li><a href="/profile">Profile</a></li>
                {% endif %}
            </ul>
            <div class="user-info">
                {% if session.user_id %}
                    <span>Welcome, <strong>{{ session.username }}</strong></span>
                    <a href="/logout" class="btn btn-secondary">Logout</a>
                {% else %}
                    <a href="/login" class="btn">Login</a>
                    <a href="/register" class="btn">Register</a>
                {% endif %}
            </div>
        </nav>
    </header>

    <div class="container">
        <div class="hero">
            <h1>TETRIS GAME</h1>
            <p>A classic puzzle game reimagined with web integration</p>
            <div class="cta-buttons">
                {% if session.user_id %}
                    <button class="btn" onclick="alert('Launch the Python app to play!')">▶ Play Game</button>
                    <a href="/profile" class="btn btn-secondary">📊 My Stats</a>
                {% else %}
                    <a href="/login" class="btn">🎮 Login to Play</a>
                    <a href="/register" class="btn btn-secondary">📝 Create Account</a>
                {% endif %}
            </div>
        </div>

        <div class="description">
            <h2>About the Game</h2>
            <p>
                Tetris is one of the most iconic puzzle video games of all time. In this modern implementation, 
                classic gameplay is combined with user authentication and persistent score tracking. 
                Built with Python (Pygame) for the game engine and Flask for web integration, 
                this version offers both desktop and web experiences.
            </p>
        </div>

        <div class="game-rules">
            <h2>How to Play</h2>
            <ol>
                <li><strong>Objective:</strong> Complete rows of blocks to clear them and earn points</li>
                <li><strong>Falling Pieces:</strong> Seven different Tetromino shapes fall from the top</li>
                <li><strong>Controls:</strong> Move, rotate, and drop pieces to fill the grid strategically</li>
                <li><strong>Scoring:</strong> Earn points for completing lines; difficulty increases with level</li>
                <li><strong>Game Over:</strong> The game ends when pieces reach the top of the board</li>
            </ol>

            <h3 style="margin-top: 30px; color: #00d4ff;">Controls</h3>
            <div class="controls">
                <div class="control-item"><strong>← →</strong> Move left/right</div>
                <div class="control-item"><strong>↑</strong> Rotate piece</div>
                <div class="control-item"><strong>↓</strong> Drop faster</div>
                <div class="control-item"><strong>SPACE</strong> Pause/Resume</div>
            </div>
        </div>

        <div class="features">
            <div class="feature-card">
                <h3>🎮 Classic Gameplay</h3>
                <p>Experience the timeless Tetris gameplay with smooth controls and responsive mechanics.</p>
            </div>
            <div class="feature-card">
                <h3>👤 User Accounts</h3>
                <p>Create an account and track your progress across multiple gaming sessions.</p>
            </div>
            <div class="feature-card">
                <h3>📊 Score Tracking</h3>
                <p>Your scores are automatically saved. View your best games and compete on the leaderboard.</p>
            </div>
            <div class="feature-card">
                <h3>🏆 Leaderboard</h3>
                <p>See the best players worldwide and their top scores. Compete for the top position!</p>
            </div>
            <div class="feature-card">
                <h3>📈 Level Progression</h3>
                <p>Difficulty increases as you progress. Each level brings faster-falling pieces.</p>
            </div>
            <div class="feature-card">
                <h3>💾 Database Integration</h3>
                <p>SQLite database ensures all your stats are securely stored and always available.</p>
            </div>
        </div>
    </div>

    <footer>
        <p>&copy; 2026 Tetris Game - Built with Flask & Pygame</p>
    </footer>
</body>
</html>'''

LOGIN_TEMPLATE = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Login - Tetris Game</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Courier New', monospace;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            color: #fff;
            min-height: 100vh;
        }
        header {
            background: rgba(0, 0, 0, 0.5);
            padding: 20px;
            border-bottom: 3px solid #00d4ff;
        }
        nav {
            display: flex;
            justify-content: space-between;
            align-items: center;
            max-width: 1200px;
            margin: 0 auto;
        }
        .logo {
            font-size: 28px;
            font-weight: bold;
            color: #00d4ff;
            text-decoration: none;
        }
        nav ul {
            list-style: none;
            display: flex;
            gap: 30px;
        }
        nav a {
            color: #fff;
            text-decoration: none;
            transition: color 0.3s;
        }
        nav a:hover { color: #00d4ff; }
        .user-info { display: flex; gap: 20px; }
        .btn {
            padding: 12px 24px;
            background: #00d4ff;
            color: #000;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-weight: bold;
            text-decoration: none;
            display: inline-block;
        }
        .btn:hover { background: #00a8cc; }
        footer {
            text-align: center;
            padding: 20px;
            background: rgba(0, 0, 0, 0.5);
            border-top: 2px solid #00d4ff;
            margin-top: 50px;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 40px 20px;
        }
        .auth-container {
            max-width: 400px;
            margin: 60px auto;
            background: rgba(0, 0, 0, 0.4);
            border: 2px solid #00d4ff;
            border-radius: 10px;
            padding: 40px;
        }
        .auth-container h2 {
            text-align: center;
            margin-bottom: 30px;
            color: #00d4ff;
        }
        .form-group {
            margin-bottom: 20px;
        }
        .form-group label {
            display: block;
            margin-bottom: 8px;
            color: #00d4ff;
            font-weight: bold;
        }
        .form-group input {
            width: 100%;
            padding: 12px;
            border: 2px solid #00d4ff;
            background: rgba(0, 212, 255, 0.1);
            color: #fff;
            border-radius: 5px;
            font-family: 'Courier New', monospace;
        }
        .form-group input:focus {
            outline: none;
            box-shadow: 0 0 10px rgba(0, 212, 255, 0.5);
        }
        .submit-btn {
            width: 100%;
            padding: 12px;
            background: #00d4ff;
            color: #000;
            border: none;
            border-radius: 5px;
            font-weight: bold;
            cursor: pointer;
            font-size: 16px;
        }
        .submit-btn:hover { background: #00a8cc; }
        .message {
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 20px;
            text-align: center;
        }
        .error {
            background: rgba(255, 0, 110, 0.2);
            border: 1px solid #ff006e;
            color: #ff006e;
        }
        .success {
            background: rgba(0, 212, 255, 0.2);
            border: 1px solid #00d4ff;
            color: #00d4ff;
        }
        .link {
            text-align: center;
            margin-top: 20px;
        }
        .link a {
            color: #00d4ff;
            text-decoration: none;
        }
        .link a:hover { text-decoration: underline; }
    </style>
</head>
<body>
    <header>
        <nav>
            <a href="/" class="logo">🎮 TETRIS</a>
            <ul>
                <li><a href="/">Home</a></li>
                <li><a href="/leaderboard">Leaderboard</a></li>
                <li><a href="/database-schema">Database</a></li>
            </ul>
            <div class="user-info">
                <a href="/register" class="btn">Register</a>
            </div>
        </nav>
    </header>

    <div class="container">
        <div class="auth-container">
            <h2>LOGIN</h2>
            <div id="message" class="message" style="display: none;"></div>
            
            <form id="loginForm">
                <div class="form-group">
                    <label for="username">Username</label>
                    <input type="text" id="username" name="username" required>
                </div>
                <div class="form-group">
                    <label for="password">Password</label>
                    <input type="password" id="password" name="password" required>
                </div>
                <button type="submit" class="submit-btn">Login</button>
            </form>

            <div class="link">
                Don't have an account? <a href="/register">Create one here</a>
            </div>
        </div>
    </div>

    <footer>
        <p>&copy; 2026 Tetris Game - Built with Flask & Pygame</p>
    </footer>

    <script>
        document.getElementById('loginForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const messageDiv = document.getElementById('message');
            
            const response = await fetch('/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    username: document.getElementById('username').value,
                    password: document.getElementById('password').value
                })
            });

            const data = await response.json();
            messageDiv.style.display = 'block';
            
            if (data.success) {
                messageDiv.className = 'message success';
                messageDiv.textContent = data.message;
                setTimeout(() => window.location.href = '/', 1500);
            } else {
                messageDiv.className = 'message error';
                messageDiv.textContent = data.message;
            }
        });
    </script>
</body>
</html>'''

REGISTER_TEMPLATE = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Register - Tetris Game</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Courier New', monospace;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            color: #fff;
            min-height: 100vh;
        }
        header {
            background: rgba(0, 0, 0, 0.5);
            padding: 20px;
            border-bottom: 3px solid #ff006e;
        }
        nav {
            display: flex;
            justify-content: space-between;
            align-items: center;
            max-width: 1200px;
            margin: 0 auto;
        }
        .logo {
            font-size: 28px;
            font-weight: bold;
            color: #ff006e;
            text-decoration: none;
        }
        nav ul {
            list-style: none;
            display: flex;
            gap: 30px;
        }
        nav a {
            color: #fff;
            text-decoration: none;
            transition: color 0.3s;
        }
        nav a:hover { color: #ff006e; }
        .user-info { display: flex; gap: 20px; }
        .btn {
            padding: 12px 24px;
            background: #ff006e;
            color: #fff;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-weight: bold;
            text-decoration: none;
            display: inline-block;
        }
        .btn:hover { background: #d60057; }
        footer {
            text-align: center;
            padding: 20px;
            background: rgba(0, 0, 0, 0.5);
            border-top: 2px solid #ff006e;
            margin-top: 50px;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 40px 20px;
        }
        .auth-container {
            max-width: 400px;
            margin: 60px auto;
            background: rgba(0, 0, 0, 0.4);
            border: 2px solid #ff006e;
            border-radius: 10px;
            padding: 40px;
        }
        .auth-container h2 {
            text-align: center;
            margin-bottom: 30px;
            color: #ff006e;
        }
        .form-group {
            margin-bottom: 20px;
        }
        .form-group label {
            display: block;
            margin-bottom: 8px;
            color: #ff006e;
            font-weight: bold;
        }
        .form-group input {
            width: 100%;
            padding: 12px;
            border: 2px solid #ff006e;
            background: rgba(255, 0, 110, 0.1);
            color: #fff;
            border-radius: 5px;
            font-family: 'Courier New', monospace;
        }
        .form-group input:focus {
            outline: none;
            box-shadow: 0 0 10px rgba(255, 0, 110, 0.5);
        }
        .submit-btn {
            width: 100%;
            padding: 12px;
            background: #ff006e;
            color: #fff;
            border: none;
            border-radius: 5px;
            font-weight: bold;
            cursor: pointer;
            font-size: 16px;
        }
        .submit-btn:hover { background: #d60057; }
        .message {
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 20px;
            text-align: center;
        }
        .error {
            background: rgba(255, 0, 110, 0.2);
            border: 1px solid #ff006e;
            color: #ff006e;
        }
        .success {
            background: rgba(0, 212, 255, 0.2);
            border: 1px solid #00d4ff;
            color: #00d4ff;
        }
        .link {
            text-align: center;
            margin-top: 20px;
        }
        .link a {
            color: #ff006e;
            text-decoration: none;
        }
        .link a:hover { text-decoration: underline; }
    </style>
</head>
<body>
    <header>
        <nav>
            <a href="/" class="logo">🎮 TETRIS</a>
            <ul>
                <li><a href="/">Home</a></li>
                <li><a href="/leaderboard">Leaderboard</a></li>
                <li><a href="/database-schema">Database</a></li>
            </ul>
            <div class="user-info">
                <a href="/login" class="btn">Login</a>
            </div>
        </nav>
    </header>

    <div class="container">
        <div class="auth-container">
            <h2>CREATE ACCOUNT</h2>
            <div id="message" class="message" style="display: none;"></div>
            
            <form id="registerForm">
                <div class="form-group">
                    <label for="username">Username</label>
                    <input type="text" id="username" name="username" required>
                </div>
                <div class="form-group">
                    <label for="password">Password (min. 4 characters)</label>
                    <input type="password" id="password" name="password" required>
                </div>
                <button type="submit" class="submit-btn">Create Account</button>
            </form>

            <div class="link">
                Already have an account? <a href="/login">Login here</a>
            </div>
        </div>
    </div>

    <footer>
        <p>&copy; 2026 Tetris Game - Built with Flask & Pygame</p>
    </footer>

    <script>
        document.getElementById('registerForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const messageDiv = document.getElementById('message');
            
            const response = await fetch('/register', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    username: document.getElementById('username').value,
                    password: document.getElementById('password').value
                })
            });

            const data = await response.json();
            messageDiv.style.display = 'block';
            
            if (data.success) {
                messageDiv.className = 'message success';
                messageDiv.textContent = data.message;
                setTimeout(() => window.location.href = '/login', 1500);
            } else {
                messageDiv.className = 'message error';
                messageDiv.textContent = data.message;
            }
        });
    </script>
</body>
</html>'''

LEADERBOARD_TEMPLATE = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Leaderboard - Tetris Game</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Courier New', monospace;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            color: #fff;
            min-height: 100vh;
        }
        header {
            background: rgba(0, 0, 0, 0.5);
            padding: 20px;
            border-bottom: 3px solid #00d4ff;
        }
        nav {
            display: flex;
            justify-content: space-between;
            align-items: center;
            max-width: 1200px;
            margin: 0 auto;
        }
        .logo {
            font-size: 28px;
            font-weight: bold;
            color: #00d4ff;
            text-decoration: none;
        }
        nav ul {
            list-style: none;
            display: flex;
            gap: 30px;
        }
        nav a {
            color: #fff;
            text-decoration: none;
            transition: color 0.3s;
        }
        nav a:hover { color: #00d4ff; }
        .user-info {
            display: flex;
            gap: 20px;
            align-items: center;
        }
        .btn {
            padding: 12px 24px;
            background: #00d4ff;
            color: #000;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-weight: bold;
            text-decoration: none;
            display: inline-block;
        }
        .btn:hover { background: #00a8cc; }
        .btn-secondary {
            background: #ff006e;
        }
        .btn-secondary:hover { background: #d60057; }
        footer {
            text-align: center;
            padding: 20px;
            background: rgba(0, 0, 0, 0.5);
            border-top: 2px solid #00d4ff;
            margin-top: 50px;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 40px 20px;
        }
        h1 {
            color: #00d4ff;
            margin-bottom: 20px;
        }
        .leaderboard-container {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 40px;
        }
        .leaderboard-section {
            background: rgba(0, 0, 0, 0.3);
            border: 2px solid #00d4ff;
            border-radius: 10px;
            padding: 30px;
        }
        .leaderboard-section h2 {
            border-bottom: 2px solid #00d4ff;
            padding-bottom: 15px;
            margin-bottom: 30px;
            color: #00d4ff;
        }
        .score-list {
            list-style: none;
        }
        .score-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 15px;
            border-bottom: 1px solid rgba(0, 212, 255, 0.2);
        }
        .score-item:hover { background: rgba(0, 212, 255, 0.1); }
        .score-rank {
            font-weight: bold;
            color: #ff006e;
            min-width: 40px;
        }
        .score-rank.top-3 {
            color: #ffd700;
            font-size: 18px;
        }
        .score-details {
            flex: 1;
            margin: 0 20px;
        }
        .score-username {
            color: #00d4ff;
            font-weight: bold;
        }
        .score-level {
            color: #aaa;
            font-size: 12px;
        }
        .score-value {
            color: #00d4ff;
            font-weight: bold;
            font-size: 18px;
        }
        .empty-message {
            text-align: center;
            padding: 40px;
            color: #aaa;
        }
        @media (max-width: 768px) {
            .leaderboard-container {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <header>
        <nav>
            <a href="/" class="logo">🎮 TETRIS</a>
            <ul>
                <li><a href="/">Home</a></li>
                <li><a href="/leaderboard">Leaderboard</a></li>
                <li><a href="/database-schema">Database</a></li>
                {% if session.user_id %}
                    <li><a href="/profile">Profile</a></li>
                {% endif %}
            </ul>
            <div class="user-info">
                {% if session.user_id %}
                    <span>Welcome, <strong>{{ session.username }}</strong></span>
                    <a href="/logout" class="btn btn-secondary">Logout</a>
                {% else %}
                    <a href="/login" class="btn">Login</a>
                    <a href="/register" class="btn">Register</a>
                {% endif %}
            </div>
        </nav>
    </header>

    <div class="container">
        <h1>🏆 LEADERBOARD</h1>

        <div class="leaderboard-container">
            <div class="leaderboard-section">
                <h2>Global Top Scores</h2>
                {% if global_scores %}
                    <ul class="score-list">
                        {% for score in global_scores %}
                            <li class="score-item">
                                <span class="score-rank {% if loop.index <= 3 %}top-3{% endif %}">
                                    #{{ loop.index }}
                                </span>
                                <div class="score-details">
                                    <div class="score-username">{{ score.username }}</div>
                                    <div class="score-level">Level {{ score.level }}</div>
                                </div>
                                <div class="score-value">{{ score.score }}</div>
                            </li>
                        {% endfor %}
                    </ul>
                {% else %}
                    <div class="empty-message">No scores yet. Be the first to play!</div>
                {% endif %}
            </div>

            {% if user_scores %}
                <div class="leaderboard-section">
                    <h2>Your Top Scores</h2>
                    <ul class="score-list">
                        {% for score in user_scores %}
                            <li class="score-item">
                                <span class="score-rank">#{{ loop.index }}</span>
                                <div class="score-details">
                                    <div class="score-level">Level {{ score.level }}</div>
                                </div>
                                <div class="score-value">{{ score.score }}</div>
                            </li>
                        {% endfor %}
                    </ul>
                </div>
            {% else %}
                <div class="leaderboard-section">
                    <div class="empty-message">Login and play to see your scores here!</div>
                </div>
            {% endif %}
        </div>
    </div>

    <footer>
        <p>&copy; 2026 Tetris Game - Built with Flask & Pygame</p>
    </footer>
</body>
</html>'''

PROFILE_TEMPLATE = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Profile - Tetris Game</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Courier New', monospace;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            color: #fff;
            min-height: 100vh;
        }
        header {
            background: rgba(0, 0, 0, 0.5);
            padding: 20px;
            border-bottom: 3px solid #00d4ff;
        }
        nav {
            display: flex;
            justify-content: space-between;
            align-items: center;
            max-width: 1200px;
            margin: 0 auto;
        }
        .logo {
            font-size: 28px;
            font-weight: bold;
            color: #00d4ff;
            text-decoration: none;
        }
        nav ul {
            list-style: none;
            display: flex;
            gap: 30px;
        }
        nav a {
            color: #fff;
            text-decoration: none;
            transition: color 0.3s;
        }
        nav a:hover { color: #00d4ff; }
        .user-info {
            display: flex;
            gap: 20px;
            align-items: center;
        }
        .btn {
            padding: 12px 24px;
            background: #ff006e;
            color: #fff;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-weight: bold;
            text-decoration: none;
            display: inline-block;
        }
        .btn:hover { background: #d60057; }
        footer {
            text-align: center;
            padding: 20px;
            background: rgba(0, 0, 0, 0.5);
            border-top: 2px solid #00d4ff;
            margin-top: 50px;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 40px 20px;
        }
        .profile-container {
            max-width: 900px;
            margin: 0 auto;
        }
        .profile-header {
            background: rgba(0, 212, 255, 0.1);
            border: 2px solid #00d4ff;
            border-radius: 10px;
            padding: 30px;
            margin-bottom: 40px;
        }
        .profile-username {
            font-size: 32px;
            color: #00d4ff;
            margin-bottom: 20px;
        }
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 20px;
        }
        .stat-box {
            background: rgba(0, 0, 0, 0.3);
            border-left: 4px solid #ff006e;
            padding: 20px;
            border-radius: 5px;
            text-align: center;
        }
        .stat-value {
            font-size: 28px;
            color: #00d4ff;
            font-weight: bold;
            margin-bottom: 10px;
        }
        .stat-label {
            color: #aaa;
            font-size: 12px;
            text-transform: uppercase;
        }
        .recent-scores {
            background: rgba(0, 0, 0, 0.3);
            border: 2px solid #ff006e;
            border-radius: 10px;
            padding: 30px;
        }
        .recent-scores h2 {
            border-bottom: 2px solid #ff006e;
            padding-bottom: 15px;
            margin-bottom: 30px;
            color: #ff006e;
        }
        .score-table {
            width: 100%;
            border-collapse: collapse;
        }
        .score-table th {
            text-align: left;
            padding: 12px;
            border-bottom: 2px solid #ff006e;
            color: #ff006e;
            font-weight: bold;
        }
        .score-table td {
            padding: 12px;
            border-bottom: 1px solid rgba(255, 0, 110, 0.2);
        }
        .score-table tr:hover { background: rgba(255, 0, 110, 0.1); }
        .empty-message {
            text-align: center;
            padding: 40px;
            color: #aaa;
        }
        @media (max-width: 768px) {
            .stats-grid {
                grid-template-columns: repeat(2, 1fr);
            }
        }
    </style>
</head>
<body>
    <header>
        <nav>
            <a href="/" class="logo">🎮 TETRIS</a>
            <ul>
                <li><a href="/">Home</a></li>
                <li><a href="/leaderboard">Leaderboard</a></li>
                <li><a href="/database-schema">Database</a></li>
                <li><a href="/profile">Profile</a></li>
            </ul>
            <div class="user-info">
                <span>Welcome, <strong>{{ session.username }}</strong></span>
                <a href="/logout" class="btn">Logout</a>
            </div>
        </nav>
    </header>

    <div class="container">
        <div class="profile-container">
            <div class="profile-header">
                <div class="profile-username">{{ session.username }}'s Profile</div>
                <div class="stats-grid">
                    <div class="stat-box">
                        <div class="stat-value">{{ stats.total_games or 0 }}</div>
                        <div class="stat-label">Games Played</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-value">{{ stats.best_score or 0 }}</div>
                        <div class="stat-label">Best Score</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-value">{{ "%.0f"|format(stats.avg_score or 0) }}</div>
                        <div class="stat-label">Avg Score</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-value">{{ stats.best_level or 0 }}</div>
                        <div class="stat-label">Best Level</div>
                    </div>
                </div>
            </div>

            <div class="recent-scores">
                <h2>Recent Games</h2>
                {% if recent_scores %}
                    <table class="score-table">
                        <thead>
                            <tr>
                                <th>Score</th>
                                <th>Level</th>
                                <th>Date</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for score in recent_scores %}
                                <tr>
                                    <td><strong>{{ score.score }}</strong></td>
                                    <td>{{ score.level }}</td>
                                    <td>{{ score.timestamp[:10] }}</td>
                                </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                {% else %}
                    <div class="empty-message">No games played yet. Launch the game and play to see your scores!</div>
                {% endif %}
            </div>
        </div>
    </div>

    <footer>
        <p>&copy; 2026 Tetris Game - Built with Flask & Pygame</p>
    </footer>
</body>
</html>'''

DATABASE_SCHEMA_TEMPLATE = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Database Schema - Tetris Game</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Courier New', monospace;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            color: #fff;
            min-height: 100vh;
        }
        header {
            background: rgba(0, 0, 0, 0.5);
            padding: 20px;
            border-bottom: 3px solid #00d4ff;
        }
        nav {
            display: flex;
            justify-content: space-between;
            align-items: center;
            max-width: 1200px;
            margin: 0 auto;
        }
        .logo {
            font-size: 28px;
            font-weight: bold;
            color: #00d4ff;
            text-decoration: none;
        }
        nav ul {
            list-style: none;
            display: flex;
            gap: 30px;
        }
        nav a {
            color: #fff;
            text-decoration: none;
            transition: color 0.3s;
        }
        nav a:hover { color: #00d4ff; }
        .user-info {
            display: flex;
            gap: 20px;
            align-items: center;
        }
        .btn {
            padding: 12px 24px;
            background: #00d4ff;
            color: #000;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-weight: bold;
            text-decoration: none;
            display: inline-block;
        }
        .btn:hover { background: #00a8cc; }
        .btn-secondary {
            background: #ff006e;
        }
        .btn-secondary:hover { background: #d60057; }
        footer {
            text-align: center;
            padding: 20px;
            background: rgba(0, 0, 0, 0.5);
            border-top: 2px solid #00d4ff;
            margin-top: 50px;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 40px 20px;
        }
        h1 {
            color: #00d4ff;
            margin-bottom: 20px;
        }
        h2 {
            color: #00d4ff;
            margin-bottom: 20px;
        }
        h3 {
            color: #ff006e;
            margin-top: 20px;
            margin-bottom: 15px;
        }
        .schema-container {
            max-width: 1000px;
            margin: 0 auto;
        }
        .er-diagram {
            background: rgba(0, 0, 0, 0.3);
            border: 2px solid #00d4ff;
            border-radius: 10px;
            padding: 40px;
            margin: 40px 0;
            text-align: center;
        }
        .relationship {
            margin: 40px 0;
            padding: 20px;
            background: rgba(255, 0, 110, 0.1);
            border-left: 4px solid #ff006e;
            border-radius: 5px;
        }
        .table-schema {
            background: rgba(0, 0, 0, 0.3);
            border: 2px solid #ff006e;
            border-radius: 10px;
            padding: 30px;
            margin: 30px 0;
        }
        .table-schema h3 {
            border-bottom: 2px solid #ff006e;
            padding-bottom: 15px;
            margin-bottom: 20px;
        }
        .schema-table {
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 20px;
        }
        .schema-table th {
            background: rgba(255, 0, 110, 0.2);
            text-align: left;
            padding: 12px;
            border-bottom: 2px solid #ff006e;
            color: #ff006e;
        }
        .schema-table td {
            padding: 12px;
            border-bottom: 1px solid rgba(255, 0, 110, 0.2);
        }
        .data-type {
            color: #00d4ff;
            font-weight: bold;
        }
        .primary-key {
            color: #ff006e;
            font-weight: bold;
        }
        .foreign-key {
            color: #ffd700;
            font-weight: bold;
        }
        ul {
            line-height: 2;
            margin-left: 20px;
        }
    </style>
</head>
<body>
    <header>
        <nav>
            <a href="/" class="logo">🎮 TETRIS</a>
            <ul>
                <li><a href="/">Home</a></li>
                <li><a href="/leaderboard">Leaderboard</a></li>
                <li><a href="/database-schema">Database</a></li>
                {% if session.user_id %}
                    <li><a href="/profile">Profile</a></li>
                {% endif %}
            </ul>
            <div class="user-info">
                {% if session.user_id %}
                    <span>Welcome, <strong>{{ session.username }}</strong></span>
                    <a href="/logout" class="btn btn-secondary">Logout</a>
                {% else %}
                    <a href="/login" class="btn">Login</a>
                    <a href="/register" class="btn">Register</a>
                {% endif %}
            </div>
        </nav>
    </header>

    <div class="container">
        <div class="schema-container">
            <h1>📊 Database Schema</h1>

            <div class="er-diagram">
                <h2>Entity Relationship Diagram</h2>
                <svg width="600" height="300" style="background: rgba(0,0,0,0.2); border-radius: 10px;">
                    <rect x="50" y="50" width="180" height="120" fill="rgba(0, 212, 255, 0.2)" stroke="#00d4ff" stroke-width="2" rx="5"/>
                    <rect x="50" y="50" width="180" height="35" fill="#00d4ff" rx="5"/>
                    <text x="140" y="75" text-anchor="middle" font-weight="bold" fill="#000" font-size="14">USERS</text>
                    <text x="60" y="100" fill="#fff" font-size="12">id (PK)</text>
                    <text x="60" y="118" fill="#fff" font-size="12">username</text>
                    <text x="60" y="136" fill="#fff" font-size="12">password</text>

                    <rect x="370" y="50" width="180" height="150" fill="rgba(255, 0, 110, 0.2)" stroke="#ff006e" stroke-width="2" rx="5"/>
                    <rect x="370" y="50" width="180" height="35" fill="#ff006e" rx="5"/>
                    <text x="460" y="75" text-anchor="middle" font-weight="bold" fill="#fff" font-size="14">SCORES</text>
                    <text x="380" y="100" fill="#fff" font-size="12">id (PK)</text>
                    <text x="380" y="118" fill="#fff" font-size="12">user_id (FK)</text>
                    <text x="380" y="136" fill="#fff" font-size="12">score</text>
                    <text x="380" y="154" fill="#fff" font-size="12">level</text>
                    <text x="380" y="172" fill="#fff" font-size="12">timestamp</text>

                    <line x1="230" y1="110" x2="370" y2="125" stroke="#ffd700" stroke-width="2" marker-end="url(#arrowhead)"/>
                    <text x="290" y="105" fill="#ffd700" font-size="12">1:N</text>

                    <defs>
                        <marker id="arrowhead" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto">
                            <polygon points="0 0, 10 3, 0 6" fill="#ffd700"/>
                        </marker>
                    </defs>
                </svg>
            </div>

            <div class="relationship">
                <h3>🔗 Relationship</h3>
                <p><strong>One-to-Many (1:N):</strong> One user can have multiple game scores. Each score record is linked to exactly one user via the user_id foreign key.</p>
            </div>

            <div class="table-schema">
                <h3>USERS Table</h3>
                <table class="schema-table">
                    <thead>
                        <tr>
                            <th>Column</th>
                            <th>Data Type</th>
                            <th>Constraints</th>
                            <th>Description</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td><span class="primary-key">id</span></td>
                            <td><span class="data-type">INTEGER</span></td>
                            <td>PRIMARY KEY, AUTOINCREMENT</td>
                            <td>Unique identifier for each user</td>
                        </tr>
                        <tr>
                            <td>username</td>
                            <td><span class="data-type">TEXT</span></td>
                            <td>UNIQUE, NOT NULL</td>
                            <td>User's login username</td>
                        </tr>
                        <tr>
                            <td>password</td>
                            <td><span class="data-type">TEXT</span></td>
                            <td>NOT NULL</td>
                            <td>Hashed password for security</td>
                        </tr>
                    </tbody>
                </table>
            </div>

            <div class="table-schema">
                <h3>SCORES Table</h3>
                <table class="schema-table">
                    <thead>
                        <tr>
                            <th>Column</th>
                            <th>Data Type</th>
                            <th>Constraints</th>
                            <th>Description</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td><span class="primary-key">id</span></td>
                            <td><span class="data-type">INTEGER</span></td>
                            <td>PRIMARY KEY, AUTOINCREMENT</td>
                            <td>Unique identifier for each score record</td>
                        </tr>
                        <tr>
                            <td><span class="foreign-key">user_id</span></td>
                            <td><span class="data-type">INTEGER</span></td>
                            <td>FOREIGN KEY, NOT NULL</td>
                            <td>Reference to users.id</td>
                        </tr>
                        <tr>
                            <td>score</td>
                            <td><span class="data-type">INTEGER</span></td>
                            <td>NOT NULL</td>
                            <td>The score achieved in the game</td>
                        </tr>
                        <tr>
                            <td>level</td>
                            <td><span class="data-type">INTEGER</span></td>
                            <td>NOT NULL</td>
                            <td>The level reached when game ended</td>
                        </tr>
                        <tr>
                            <td>timestamp</td>
                            <td><span class="data-type">DATETIME</span></td>
                            <td>DEFAULT CURRENT_TIMESTAMP</td>
                            <td>When the score was recorded</td>
                        </tr>
                    </tbody>
                </table>
            </div>

            <div class="relationship">
                <h3>📝 Key Features</h3>
                <ul>
                    <li><strong>Data Integrity:</strong> Foreign key constraint ensures scores can only reference existing users</li>
                    <li><strong>Security:</strong> Passwords are hashed before storage</li>
                    <li><strong>Uniqueness:</strong> Usernames are unique to prevent duplicate accounts</li>
                    <li><strong>Audit Trail:</strong> Timestamps automatically recorded for every score</li>
                    <li><strong>Scalability:</strong> Indexes on foreign keys for efficient queries</li>
                </ul>
            </div>
        </div>
    </div>

    <footer>
        <p>&copy; 2026 Tetris Game - Built with Flask & Pygame</p>
    </footer>
</body>
</html>'''

# ==================== APP INITIALIZATION ====================
if __name__ == '__main__':
    # Initialize database when app starts
    init_db()
    
    # Run Flask development server
    # debug=True enables auto-reload on code changes and shows detailed error pages
    app.run(debug=True)