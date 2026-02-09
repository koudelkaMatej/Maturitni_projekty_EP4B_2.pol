<?php
// API pro načtení žebříčku do Tetris hry
// Vrací JSON se skóre z databáze

// Načtení připojení
require_once 'pripojeni.php';

// Nastavení headeru pro JSON
header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');

// Připojení k databázi
$conn = get_db_connection();

// Počet záznamů (default 20, max 100)
$limit = isset($_GET['limit']) ? min(intval($_GET['limit']), 100) : 20;

// Načtení highscores z databáze
$sql = "SELECT jmeno, skore, datum FROM tetris_highscores ORDER BY skore DESC LIMIT ?";
$stmt = $conn->prepare($sql);
$stmt->bind_param("i", $limit);
$stmt->execute();
$result = $stmt->get_result();

$highscores = [];
if ($result && $result->num_rows > 0) {
    while($row = $result->fetch_assoc()) {
        $highscores[] = [
            'jmeno' => $row['jmeno'],
            'skore' => intval($row['skore']),
            'datum' => $row['datum']
        ];
    }
}

$stmt->close();
$conn->close();

// Vrácení dat
echo json_encode([
    'success' => true,
    'count' => count($highscores),
    'data' => $highscores
], JSON_UNESCAPED_UNICODE);
?>