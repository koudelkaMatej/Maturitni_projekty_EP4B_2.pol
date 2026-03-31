import sqlite3  # knihovna pro práci s SQLite databází
from pathlib import Path  # práce s cestami k souborům

DB_PATH = Path(__file__).parent / "data" / "flappy.db"  # cesta k databázovému souboru
SCHEMA_PATH = Path(__file__).parent / "schema.sql"  # cesta k SQL souboru, který vytvoří tabulky


def get_conn():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    # vytvoří složku "data", pokud ještě neexistuje

    conn = sqlite3.connect(DB_PATH)
    # připojí se k databázi (nebo ji vytvoří, když neexistuje)

    conn.row_factory = sqlite3.Row
    # umožní přístup k datům jako slovník (row["id"] místo row[0])

    conn.execute("PRAGMA foreign_keys = ON;")
    # zapne kontrolu cizích klíčů (relace mezi tabulkami)

    return conn
    # vrátí připojení k databázi


def init_db():
    with get_conn() as conn:
        # otevře připojení k databázi

        conn.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))
        # načte SQL skript ze souboru schema.sql a spustí ho
        # tím vytvoří tabulky (users, scores atd.)


def create_user(username: str, password_hash: str) -> int:
    with get_conn() as conn:
        # otevře připojení

        cur = conn.execute(
            "INSERT INTO users(username, password_hash) VALUES(?, ?)",
            # SQL příkaz pro vložení uživatele
            (username, password_hash),
            # hodnoty (chráněné proti SQL injection)
        )

        conn.commit()
        # uloží změny do databáze

        return int(cur.lastrowid)
        # vrátí ID nově vytvořeného uživatele


def get_user_by_username(username: str):
    with get_conn() as conn:
        # otevře připojení

        cur = conn.execute(
            "SELECT id, username, password_hash, created_at FROM users WHERE username = ?",
            # SQL dotaz na nalezení uživatele podle jména
            (username,),
        )

        row = cur.fetchone()
        # vezme jeden výsledek

        return dict(row) if row else None
        # vrátí data jako slovník nebo None, když neexistuje


def insert_score(username: str, difficulty: str, score: int) -> int:
    with get_conn() as conn:
        # otevře připojení

        cur = conn.execute("SELECT id FROM users WHERE username = ?", (username,))
        # najde ID uživatele podle jména

        user = cur.fetchone()
        # vezme výsledek

        if not user:
            raise ValueError("User not found")
            # když uživatel neexistuje → chyba

        user_id = int(user["id"])
        # uloží ID uživatele

        # zjistí, jestli už uživatel má score na téhle obtížnosti
        cur = conn.execute(
            "SELECT id, score FROM scores WHERE user_id = ? AND difficulty = ?",
            # hledá existující skóre pro daného uživatele a obtížnost
            (user_id, difficulty),
        )

        row = cur.fetchone()
        # vezme výsledek

        if row:
            # když už existuje záznam

            old_id = int(row["id"])
            # ID existujícího záznamu

            old_score = int(row["score"])
            # staré skóre

            # přepiš jen když je nové skóre lepší
            if score > old_score:
                conn.execute(
                    """
                    UPDATE scores
                    SET score = ?, created_at = datetime('now')
                    WHERE id = ?
                    """,
                    (score, old_id),
                )
                # aktualizuje skóre a nastaví nový čas

                conn.commit()
                # uloží změnu

            return old_id
            # vrátí ID (nemění ID, jen update)

        # když ještě žádný záznam nemá, vlož nový
        cur = conn.execute(
            "INSERT INTO scores(user_id, difficulty, score) VALUES(?,?,?)",
            # vloží nové skóre
            (user_id, difficulty, score),
        )

        conn.commit()
        # uloží změnu

        return int(cur.lastrowid)
        # vrátí ID nového záznamu


def top_scores(difficulty: str, limit: int = 10):
        with get_conn() as conn:
            # otevře připojení

            cur = conn.execute(
                """
                SELECT s.id, u.username AS name, s.difficulty, s.score, s.created_at
                FROM scores s
                JOIN users u ON u.id = s.user_id
                WHERE s.difficulty = ?
                ORDER BY s.score DESC, s.created_at ASC
                LIMIT ?
                """,
                (difficulty, limit),
            )
            # SQL dotaz:
            # spojí tabulku scores a users
            # vezme jen danou obtížnost
            # seřadí od nejvyššího skóre
            # když stejné skóre → starší dřív
            # omezí počet výsledků

            return [dict(r) for r in cur.fetchall()]
            # vrátí seznam výsledků jako slovníky