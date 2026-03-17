<?php
/**
 * login.php
 * 
 * Přihlášení uživatele
 * 
 * Očekávané POST parametry:
 * - username: Uživatelské jméno
 * - password: Heslo
 */

require_once 'config.php';

header('Content-Type: application/json; charset=utf-8');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: POST');
header('Access-Control-Allow-Headers: Content-Type');

function sendResponse($success, $message = '', $data = null) {
    $response = [
        'success' => $success,
        'message' => $message
    ];
    
    if ($data !== null) {
        $response['data'] = $data;
    }
    
    echo json_encode($response, JSON_UNESCAPED_UNICODE);
    exit;
}

// Kontrola metody
if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    sendResponse(false, 'Pouze POST requesty jsou povoleny');
}

// Získání dat
$username = isset($_POST['username']) ? trim($_POST['username']) : '';
$password = isset($_POST['password']) ? $_POST['password'] : '';

// Validace
if (empty($username)) {
    sendResponse(false, 'Uživatelské jméno nesmí být prázdné');
}

if (empty($password)) {
    sendResponse(false, 'Heslo nesmí být prázdné');
}

// Připojení k databázi
$conn = getDbConnection();
if (!$conn) {
    sendResponse(false, 'Chyba připojení k databázi');
}

// Najdeme uživatele
$stmt = $conn->prepare("SELECT id, username, password_hash FROM users WHERE username = ?");
if (!$stmt) {
    closeDbConnection($conn);
    sendResponse(false, 'Chyba při přípravě dotazu');
}

$stmt->bind_param("s", $username);
$stmt->execute();
$result = $stmt->get_result();

if ($result->num_rows === 0) {
    $stmt->close();
    closeDbConnection($conn);
    sendResponse(false, 'Nesprávné uživatelské jméno nebo heslo');
}

$user = $result->fetch_assoc();
$stmt->close();

// Ověření hesla
if (!password_verify($password, $user['password_hash'])) {
    closeDbConnection($conn);
    sendResponse(false, 'Nesprávné uživatelské jméno nebo heslo');
}

// Aktualizace last_login
$update_stmt = $conn->prepare("UPDATE users SET last_login = NOW() WHERE id = ?");
if ($update_stmt) {
    $update_stmt->bind_param("i", $user['id']);
    $update_stmt->execute();
    $update_stmt->close();
}

closeDbConnection($conn);

// Úspěšné přihlášení
sendResponse(true, 'Přihlášení úspěšné', [
    'user_id' => $user['id'],
    'username' => $user['username']
]);
?>
