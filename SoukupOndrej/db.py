import sqlite3
from settings import DB_PATH

DDL = """CREATE TABLE IF NOT EXISTS score (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    player_name TEXT NOT NULL,
    value INTEGER NOT NULL,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
"""

def _conn():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute(DDL)
    return conn

def save_score(player_name: str, value: int):
    with _conn() as c:
        c.execute("INSERT INTO score(player_name, value) VALUES (?, ?)", (player_name, value))

def get_top_scores(limit: int = 10):
    with _conn() as c:
        cur = c.execute("SELECT player_name, value, created_at FROM score ORDER BY value DESC, created_at ASC LIMIT ?", (limit,))
        return cur.fetchall()
