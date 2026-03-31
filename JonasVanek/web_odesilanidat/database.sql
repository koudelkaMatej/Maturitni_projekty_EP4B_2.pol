-- ============================================================================
-- SQL SKRIPT PRO VYTVOŘENÍ DATABÁZE A TABULEK
-- Flappy Palach - Žebříček skóre s login systémem
-- ============================================================================

-- Vytvoření databáze (pokud ještě neexistuje)
CREATE DATABASE IF NOT EXISTS flappy_palach
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

-- Použití databáze
USE flappy_palach;

-- Smazání tabulek (pokud existují - pouze pro vývoj!)
-- POZOR: Toto smaže všechna data! Zakomentujte po prvním spuštění.
DROP TABLE IF EXISTS scores;
DROP TABLE IF EXISTS users;

-- ============================================================================
-- TABULKA UŽIVATELŮ
-- ============================================================================
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT 'Unikátní ID uživatele',
    username VARCHAR(30) NOT NULL UNIQUE COMMENT 'Uživatelské jméno (unikátní)',
    password_hash VARCHAR(255) NOT NULL COMMENT 'Hashované heslo',
    date_registered DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Datum registrace',
    last_login DATETIME NULL COMMENT 'Poslední přihlášení',
    
    -- Indexy
    INDEX idx_username (username) COMMENT 'Index pro rychlé vyhledávání podle jména'
) ENGINE=InnoDB 
  DEFAULT CHARSET=utf8mb4 
  COLLATE=utf8mb4_unicode_ci
  COMMENT='Tabulka uživatelů';

-- ============================================================================
-- TABULKA SKÓRE
-- ============================================================================
CREATE TABLE scores (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT 'Unikátní ID záznamu',
    user_id INT NOT NULL COMMENT 'ID uživatele (foreign key)',
    username VARCHAR(30) NOT NULL COMMENT 'Jméno hráče (pro snadnější dotazy)',
    score INT NOT NULL COMMENT 'Dosažené skóre',
    difficulty ENUM('lehka', 'stredni', 'tezka') NOT NULL DEFAULT 'stredni' COMMENT 'Obtížnost hry',
    date_created DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Datum a čas dosažení skóre',
    
    -- Foreign key constraint
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    
    -- Indexy pro rychlejší vyhledávání
    INDEX idx_user_difficulty (user_id, difficulty) COMMENT 'Index pro hledání podle uživatele a obtížnosti',
    INDEX idx_score_difficulty (score DESC, difficulty) COMMENT 'Index pro řazení podle skóre a obtížnosti',
    INDEX idx_username (username) COMMENT 'Index pro vyhledávání podle jména',
    INDEX idx_difficulty (difficulty) COMMENT 'Index pro filtrování podle obtížnosti'
) ENGINE=InnoDB 
  DEFAULT CHARSET=utf8mb4 
  COLLATE=utf8mb4_unicode_ci
  COMMENT='Tabulka pro ukládání herního skóre';

-- ============================================================================
-- UŽITEČNÉ SQL DOTAZY PRO SPRÁVU
-- ============================================================================

-- Zobrazení top 10 nejlepších skóre (všechny obtížnosti)
-- SELECT u.username, s.score, s.difficulty, s.date_created 
-- FROM scores s 
-- JOIN users u ON s.user_id = u.id 
-- ORDER BY s.score DESC 
-- LIMIT 10;

-- Nejlepší skóre pro každého hráče na každé obtížnosti
-- SELECT u.username, s.difficulty, MAX(s.score) as best_score
-- FROM scores s
-- JOIN users u ON s.user_id = u.id
-- GROUP BY u.username, s.difficulty
-- ORDER BY s.difficulty, best_score DESC;

-- Počet registrovaných uživatelů
-- SELECT COUNT(*) as total_users FROM users;

-- Počet celkových her
-- SELECT COUNT(*) as total_games FROM scores;

-- Statistiky podle obtížnosti
-- SELECT 
--     difficulty,
--     COUNT(*) as games_played,
--     MAX(score) as highest_score,
--     AVG(score) as average_score
-- FROM scores
-- GROUP BY difficulty;

-- Smazání všech skóre (ne uživatelů!)
-- DELETE FROM scores;

-- Smazání všech uživatelů (smaže i jejich skóre kvůli CASCADE)
-- DELETE FROM users;

-- Smazání starých záznamů (starších než 30 dní)
-- DELETE FROM scores WHERE date_created < NOW() - INTERVAL 30 DAY;

-- ============================================================================
-- KONEC SKRIPTU
-- ============================================================================

SELECT 'Databáze a tabulky byly úspěšně vytvořeny!' as Status;
SELECT 'Nyní můžete registrovat uživatele a ukládat skóre.' as Info;