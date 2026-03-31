<?php
/**
 * Konfigurační soubor pro připojení k databázi
 * 
 * DŮLEŽITÉ: Upravte tyto údaje podle vašeho nastavení!
 */

// Nastavení databáze
define('DB_HOST', 'localhost');      // Adresa serveru (většinou localhost)
define('DB_USER', 'root');           // Uživatelské jméno (XAMPP defaultně 'root')
define('DB_PASS', '');               // Heslo (XAMPP defaultně prázdné)
define('DB_NAME', 'flappy_palach');  // Název databáze

// Timezone pro správné ukládání času
date_default_timezone_set('Europe/Prague');

/**
 * Funkce pro připojení k databázi
 * Vrací mysqli objekt nebo NULL při chybě
 */
function getDbConnection() {
    $conn = new mysqli(DB_HOST, DB_USER, DB_PASS, DB_NAME);
    
    // Kontrola připojení
    if ($conn->connect_error) {
        error_log("Database connection failed: " . $conn->connect_error);
        return null;
    }
    
    // Nastavení kódování na UTF-8
    $conn->set_charset("utf8mb4");
    
    return $conn;
}

/**
 * Funkce pro bezpečné ukončení připojení
 */
function closeDbConnection($conn) {
    if ($conn) {
        $conn->close();
    }
}
?>