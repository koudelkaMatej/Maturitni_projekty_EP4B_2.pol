<?php
// --- ÚDAJE OD ŠKOLY ---
$host = 'dbs.spskladno.cz'; 
$db   = 'vyuka18';     
$user = 'student18';   
$pass = 'spsnet'; // <--- ZKONTROLUJ HLAVNĚ TOTO
$charset = 'utf8mb4';

$db_connected = false;
$db_error_msg = "";

try {
    $dsn = "mysql:host=$host;dbname=$db;charset=$charset";
    $pdo = new PDO($dsn, $user, $pass);
    
    // Nastavení, aby nám PDO házelo výjimky při každé chybě
    $pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);

    // --- TEST TVORBY TABULEK ---
    try {
        // Tabulka uživatelů
        $pdo->exec("CREATE TABLE IF NOT EXISTS s18_users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ) ENGINE=InnoDB;");

        // Tabulka skóre
        $pdo->exec("CREATE TABLE IF NOT EXISTS s18_scoreboard (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            score INT NOT NULL,
            played_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES s18_users(id) ON DELETE CASCADE
        ) ENGINE=InnoDB;");
        
        $db_connected = true;

    } catch (PDOException $e) {
        $db_error_msg = "Spojení OK, ale CHYBA PŘI TVORBĚ TABULEK: " . $e->getMessage();
    }

} catch (PDOException $e) {
    $db_error_msg = "CHYBA PŘIPOJENÍ K SERVERU: " . $e->getMessage();
}

// Pokud nejsme připojeni, vypíšeme to hned, abychom to viděli
if (!$db_connected) {
    echo "<div style='background: #ffcccc; color: #cc0000; padding: 15px; border: 2px solid red; margin: 20px;'>";
    echo "<strong>Debugger:</strong> " . $db_error_msg;
    echo "</div>";
}
?>