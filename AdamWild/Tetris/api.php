<?php
// API pro přijímání skóre z Tetris hry přes GET
// Tento soubor nahraj na školní server do stejné složky jako index.php

// Načtení připojení k databázi
require_once 'pripojeni.php';

// Nastavení headeru pro JSON
header('Content-Type: application/json');

// Bezpečnostní token (musí být stejný v Python hře)
define('API_TOKEN', 'tetris_secret_2024');

// --- NAČTENÍ DAT Z GET ---
$jmeno = isset($_GET['jmeno']) ? trim($_GET['jmeno']) : '';
$skore = isset($_GET['skore']) ? intval($_GET['skore']) : 0;
$token = isset($_GET['token']) ? $_GET['token'] : '';

// --- KONTROLA TOKENU ---
if ($token !== API_TOKEN) {
    http_response_code(403);
    echo json_encode(['error' => 'Neplatný token']);
    exit;
}

// --- VALIDACE DAT ---
if (empty($jmeno) || strlen($jmeno) > 50) {
    http_response_code(400);
    echo json_encode(['error' => 'Jméno musí mít 1-50 znaků']);
    exit;
}

if ($skore < 0 || $skore > 999999) {
    http_response_code(400);
    echo json_encode(['error' => 'Neplatné skóre']);
    exit;
}

// --- PŘIPOJENÍ K DATABÁZI ---
$conn = get_db_connection();

// --- VLOŽENÍ SKÓRE DO DATABÁZE ---
$stmt = $conn->prepare("INSERT INTO tetris_highscores (jmeno, skore) VALUES (?, ?)");
$stmt->bind_param("si", $jmeno, $skore);

if ($stmt->execute()) {
    http_response_code(200);
    echo json_encode([
        'success' => true,
        'message' => 'Skóre uloženo',
        'jmeno' => $jmeno,
        'skore' => $skore
    ]);
} else {
    http_response_code(500);
    echo json_encode([
        'error' => 'Chyba při ukládání do databáze',
        'db_error' => $stmt->error
    ]);
}

$stmt->close();
$conn->close();
?>
