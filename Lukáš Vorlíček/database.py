import sqlite3, datetime

def init_db():
    with sqlite3.connect("../../Maturitka/tetris.db") as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS users 
                        (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                         username TEXT UNIQUE, password TEXT, created_at TEXT)''')
        conn.execute('''CREATE TABLE IF NOT EXISTS high_scores 
                        (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                         user_id INTEGER, name TEXT, score INTEGER, 
                         level INTEGER, played_at TEXT,
                         FOREIGN KEY(user_id) REFERENCES users(id))''')

def register_user(u, p):
    try:
        with sqlite3.connect("../../Maturitka/tetris.db") as conn:
            d = datetime.datetime.now().strftime("%d. %m. %Y")
            conn.execute("INSERT INTO users (username, password, created_at) VALUES (?, ?, ?)", (u, p, d))
        return True
    except: return False

def login_user(u, p):
    with sqlite3.connect("../../Maturitka/tetris.db") as conn:
        res = conn.execute("SELECT id FROM users WHERE username=? AND password=?", (u, p)).fetchone()
        return res[0] if res else None

def save_score(uid, name, s, l):
    with sqlite3.connect("../../Maturitka/tetris.db") as conn:
        now = datetime.datetime.now().strftime("%d.%m.%Y %H:%M")
        conn.execute("INSERT INTO high_scores (user_id, name, score, level, played_at) VALUES (?,?,?,?,?)", (uid, name, s, l, now))