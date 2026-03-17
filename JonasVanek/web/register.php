<?php
/**
 * register.php
 * 
 * Registrace nového uživatele
 * 
 * Očekávané POST parametry:
 * - username: Uživatelské jméno (3-30 znaků)
 * - password: Heslo (minimálně 4 znaky)
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

// Validace uživatelského jména
if (empty($username)) {
    sendResponse(false, 'Uživatelské jméno nesmí být prázdné');
}

if (strlen($username) < 3) {
    sendResponse(false, 'Uživatelské jméno musí mít alespoň 3 znaky');
}

if (strlen($username) > 30) {
    sendResponse(false, 'Uživatelské jméno může mít maximálně 30 znaků');
}

// Validace hesla
if (empty($password)) {
    sendResponse(false, 'Heslo nesmí být prázdné');
}

if (strlen($password) < 4) {
    sendResponse(false, 'Heslo musí mít alespoň 4 znaky');
}

// Připojení k databázi
$conn = getDbConnection();
if (!$conn) {
    sendResponse(false, 'Chyba připojení k databázi');
}

// Kontrola, zda uživatel už neexistuje
$check_stmt = $conn->prepare("SELECT id FROM users WHERE username = ?");
if (!$check_stmt) {
    closeDbConnection($conn);
    sendResponse(false, 'Chyba při přípravě dotazu');
}

$check_stmt->bind_param("s", $username);
$check_stmt->execute();
$check_result = $check_stmt->get_result();

if ($check_result->num_rows > 0) {
    $check_stmt->close();
    closeDbConnection($conn);
    sendResponse(false, 'Uživatelské jméno je již obsazené');
}
$check_stmt->close();

// Hashování hesla
$password_hash = password_hash($password, PASSWORD_DEFAULT);

// Vložení nového uživatele
$stmt = $conn->prepare("INSERT INTO users (username, password_hash, date_registered) VALUES (?, ?, NOW())");
if (!$stmt) {
    closeDbConnection($conn);
    sendResponse(false, 'Chyba při přípravě dotazu: ' . $conn->error);
}

$stmt->bind_param("ss", $username, $password_hash);

if ($stmt->execute()) {
    $user_id = $stmt->insert_id;
    $stmt->close();
    closeDbConnection($conn);
    
    sendResponse(true, 'Registrace úspěšná', [
        'user_id' => $user_id,
        'username' => $username
    ]);
} else {
    $error = $stmt->error;
    $stmt->close();
    closeDbConnection($conn);
    sendResponse(false, 'Chyba při registraci: ' . $error);
}
?>
