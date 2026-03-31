PRAGMA foreign_keys = ON;
-- zapne kontrolu cizích klíčů (relací mezi tabulkami)
-- bez toho by SQLite ignoroval FOREIGN KEY

CREATE TABLE IF NOT EXISTS users (
-- vytvoří tabulku "users", pokud ještě neexistuje

    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    -- unikátní ID uživatele (automaticky se zvyšuje)

    username        TEXT NOT NULL UNIQUE,
    -- uživatelské jméno (musí být vyplněné a nesmí se opakovat)

    password_hash   TEXT NOT NULL,
    -- uložené heslo ve formě hashe (nikdy ne čisté heslo)

    created_at      TEXT NOT NULL DEFAULT (datetime('now'))
    -- datum vytvoření uživatele (automaticky aktuální čas)
);

CREATE TABLE IF NOT EXISTS scores (
-- vytvoří tabulku "scores" (skóre hráčů)

    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    -- unikátní ID záznamu

    user_id     INTEGER NOT NULL,
    -- ID uživatele (odkaz na tabulku users)

    difficulty  TEXT NOT NULL CHECK (difficulty IN ('easy','normal','hard','insane')),
    -- obtížnost (povoleny jen tyto hodnoty)

    score       INTEGER NOT NULL CHECK (score >= 0),
    -- skóre (musí být číslo ≥ 0)

    created_at  TEXT NOT NULL DEFAULT (datetime('now')),
    -- čas vytvoření záznamu

    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    -- propojení s tabulkou users
    -- když smažeš uživatele → smažou se i jeho skóre

    UNIQUE(user_id, difficulty)
    -- jeden uživatel může mít jen jedno skóre pro každou obtížnost
);

CREATE INDEX IF NOT EXISTS idx_scores_diff_score ON scores(difficulty, score DESC);
-- vytvoří index (urychlení databáze)
-- pomáhá rychle najít top skóre podle obtížnosti a seřazení