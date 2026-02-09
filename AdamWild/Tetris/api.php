<?php
// API pro přijímání skóre z Tetris hry
// TENTO SOUBOR NAHRAJ DO STEJNÉ SLOŽKY JAKO index.php

// Načtení připojení
require_once 'pripojeni.php';

// Nastavení headeru pro JSON
header('Content-Type: application/json');

// Bezpečnostní token (musí být stejný v Python hře)
define('API_TOKEN', 'tetris_secret_2024');

// Kontrola metody
if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    http_response_code(405);
    echo json_encode(['error' => 'Pouze POST požadavky']);
    exit;
}

// Načtení dat - zkus několik způsobů
$data = null;

// Způsob 1: JSON z php://input
$input = file_get_contents('php://input');
if ($input) {
    $data = json_decode($input, true);
}

// Způsob 2: Pokud JSON selhal, zkus $_POST
if (!$data && !empty($_POST)) {
    $data = $_POST;
}

// Pokud stále nic, vrať chybu
if (!$data) {
    http_response_code(400);
    echo json_encode(['error' => 'Žádná data nebyla přijata', 'debug' => 'Input: ' . substr($input, 0, 100)]);
    exit;
}

// Kontrola tokenu
if (!isset($data['token']) || $data['token'] !== API_TOKEN) {
    http_response_code(403);
    echo json_encode(['error' => 'Neplatný token']);
    exit;
}

// Kontrola dat
if (!isset($data['jmeno']) || !isset($data['skore'])) {
    http_response_code(400);
    echo json_encode(['error' => 'Chybí jméno nebo skóre', 'received' => array_keys($data)]);
    exit;
}

$jmeno = trim($data['jmeno']);
$skore = intval($data['skore']);

// Validace
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

// Připojení k databázi
$conn = get_db_connection();

// Vložení do databáze
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
    echo json_encode(['error' => 'Chyba při ukládání do databáze', 'db_error' => $stmt->error]);
}

$stmt->close();
$conn->close();
?>