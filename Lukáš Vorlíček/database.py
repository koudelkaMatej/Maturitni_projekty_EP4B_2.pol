import sqlite3, datetime, os

# Dynamické zjištění absolutní cesty k DB (aby web fungoval na jakémkoliv PC)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "tetris.db")

def get_connection():
    # Pomocná funkce pro vytvoření spojení s databází
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    #Tabulka uživatelů a tabulka skóre s cizím klíčem (1:N)
    with get_connection() as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS users 
                        (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                         username TEXT UNIQUE NOT NULL, 
                         password TEXT NOT NULL, 
                         created_at TEXT)''')
        conn.execute('''CREATE TABLE IF NOT EXISTS high_scores 
                        (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                         user_id INTEGER, name TEXT, score INTEGER, 
                         level INTEGER, played_at TEXT,
                         FOREIGN KEY(user_id) REFERENCES users(id))''')
        conn.commit()

def register_user(u, p):
    try:
        with get_connection() as conn:
            reg_date = datetime.datetime.now().strftime("%d. %m. %Y")
            conn.execute("INSERT INTO users (username, password, created_at) VALUES (?, ?, ?)", (u, p, reg_date))
            conn.commit()
        return True
    except sqlite3.IntegrityError: return False

def login_user(u, p):
    # Ověření dvojice jméno/heslo v databázi
    with get_connection() as conn:
        res = conn.execute("SELECT id FROM users WHERE username=? AND password=?", (u, p)).fetchone()
        return res['id'] if res else None

def save_score(uid, name, s, l):
    # Uložení výsledku po skončení hry
    with get_connection() as conn:
        now = datetime.datetime.now().strftime("%d.%m.%Y %H:%M")
        conn.execute("INSERT INTO high_scores (user_id, name, score, level, played_at) VALUES (?,?,?,?,?)", (uid, name, s, l, now))
        conn.commit()