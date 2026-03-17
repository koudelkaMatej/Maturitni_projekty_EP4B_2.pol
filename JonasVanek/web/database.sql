-- ============================================================================
-- SQL SKRIPT PRO VYTVOŘENÍ DATABÁZE A TABULKY
-- Flappy Palach - Žebříček skóre
-- ============================================================================

-- Vytvoření databáze (pokud ještě neexistuje)
CREATE DATABASE IF NOT EXISTS flappy_palach
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

-- Použití databáze
USE flappy_palach;

-- Smazání tabulky (pokud existuje - pouze pro vývoj!)
-- POZOR: Toto smaže všechna data! Zakomentujte po prvním spuštění.
DROP TABLE IF EXISTS scores;

-- Vytvoření tabulky pro ukládání skóre
CREATE TABLE scores (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT 'Unikátní ID záznamu',
    player_name VARCHAR(30) NOT NULL COMMENT 'Jméno hráče (max 30 znaků)',
    score INT NOT NULL COMMENT 'Dosažené skóre',
    date_created DATETIME NOT NULL COMMENT 'Datum a čas dosažení skóre',
    
    -- Indexy pro rychlejší vyhledávání
    INDEX idx_score (score DESC) COMMENT 'Index pro řazení podle skóre',
    INDEX idx_date (date_created DESC) COMMENT 'Index pro řazení podle data',
    INDEX idx_player (player_name) COMMENT 'Index pro vyhledávání podle jména'
) ENGINE=InnoDB 
  DEFAULT CHARSET=utf8mb4 
  COLLATE=utf8mb4_unicode_ci
  COMMENT='Tabulka pro ukládání herního skóre';

-- ============================================================================
-- TESTOVACÍ DATA (volitelné - pro testování webu)
-- ============================================================================

-- Vložení testovacích záznamů
-- Toto je volitelné - můžete to zakomentovat nebo smazat

INSERT INTO scores (player_name, score, date_created) VALUES
('Jan Novák', 150, NOW() - INTERVAL 1 HOUR),
('Petra Svobodová', 200, NOW() - INTERVAL 2 HOUR),
('Tomáš Dvořák', 175, NOW() - INTERVAL 3 HOUR),
('Marie Nováková', 130, NOW() - INTERVAL 4 HOUR),
('Petr Černý', 220, NOW() - INTERVAL 5 HOUR),
('Eva Malá', 190, NOW() - INTERVAL 6 HOUR),
('Jakub Veselý', 160, NOW() - INTERVAL 1 DAY),
('Lenka Horáková', 145, NOW() - INTERVAL 1 DAY),
('Martin Kučera', 210, NOW() - INTERVAL 2 DAY),
('Lucie Procházková', 185, NOW() - INTERVAL 2 DAY),
('David Němec', 170, NOW() - INTERVAL 3 DAY),
('Tereza Marková', 155, NOW() - INTERVAL 3 DAY),
('Filip Pospíšil', 240, NOW() - INTERVAL 4 DAY),
('Karolína Fialová', 195, NOW() - INTERVAL 4 DAY),
('Ondřej Král', 180, NOW() - INTERVAL 5 DAY);

-- ============================================================================
-- UŽITEČNÉ SQL DOTAZY PRO SPRÁVU
-- ============================================================================

-- Zobrazení top 10 nejlepších skóre
-- SELECT * FROM scores ORDER BY score DESC LIMIT 10;

-- Zobrazení skóre konkrétního hráče
-- SELECT * FROM scores WHERE player_name = 'Jan Novák' ORDER BY score DESC;

-- Smazání všech záznamů (POZOR!)
-- DELETE FROM scores;

-- Smazání záznamů starších než 30 dní
-- DELETE FROM scores WHERE date_created < NOW() - INTERVAL 30 DAY;

-- Počet celkových her
-- SELECT COUNT(*) as total_games FROM scores;

-- Počet unikátních hráčů
-- SELECT COUNT(DISTINCT player_name) as unique_players FROM scores;

-- Nejvyšší skóre
-- SELECT MAX(score) as highest_score FROM scores;

-- Průměrné skóre
-- SELECT AVG(score) as average_score FROM scores;

-- Statistiky podle hráče
-- SELECT 
--     player_name,
--     COUNT(*) as games_played,
--     MAX(score) as best_score,
--     AVG(score) as average_score,
--     MIN(score) as worst_score
-- FROM scores
-- GROUP BY player_name
-- ORDER BY best_score DESC;

-- ============================================================================
-- KONEC SKRIPTU
-- ============================================================================

-- Výpis pro kontrolu
SELECT 'Databáze a tabulka byly úspěšně vytvořeny!' as Status;
SELECT COUNT(*) as 'Počet testovacích záznamů' FROM scores;
