<?php
/**
 * submit_score.php
 * 
 * Ukládání skóre s autentizací a podporou obtížnosti.
 * Pokud už uživatel má lepší skóre na dané obtížnosti, nové se neuloží.
 * Pokud je nové skóre lepší, staré se smaže a uloží se nové.
 * 
 * Očekávané POST parametry:
 * - user_id: ID uživatele
 * - username: Jméno uživatele
 * - score: Skóre (celé číslo)
 * - difficulty: Obtížnost ("lehka", "stredni", "tezka")
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
$user_id = isset($_POST['user_id']) ? intval($_POST['user_id']) : 0;
$username = isset($_POST['username']) ? trim($_POST['username']) : '';
$score = isset($_POST['score']) ? intval($_POST['score']) : 0;
$difficulty = isset($_POST['difficulty']) ? trim($_POST['difficulty']) : 'stredni';

// Validace
if ($user_id <= 0) {
    sendResponse(false, 'Neplatné ID uživatele');
}

if (empty($username)) {
    sendResponse(false, 'Uživatelské jméno nesmí být prázdné');
}

if ($score < 0) {
    sendResponse(false, 'Skóre nemůže být záporné');
}

if ($score > 999999) {
    sendResponse(false, 'Skóre je příliš vysoké');
}

// Validace obtížnosti
$valid_difficulties = ['lehka', 'stredni', 'tezka'];
if (!in_array($difficulty, $valid_difficulties)) {
    $difficulty = 'stredni'; // Výchozí hodnota
}

// Připojení k databázi
$conn = getDbConnection();
if (!$conn) {
    sendResponse(false, 'Chyba připojení k databázi');
}

// Ověření, že uživatel existuje
$check_user = $conn->prepare("SELECT id FROM users WHERE id = ?");
if (!$check_user) {
    closeDbConnection($conn);
    sendResponse(false, 'Chyba při přípravě dotazu');
}

$check_user->bind_param("i", $user_id);
$check_user->execute();
$user_result = $check_user->get_result();

if ($user_result->num_rows === 0) {
    $check_user->close();
    closeDbConnection($conn);
    sendResponse(false, 'Uživatel neexistuje');
}
$check_user->close();

// Najdeme nejlepší skóre uživatele na této obtížnosti
$best_score_stmt = $conn->prepare("
    SELECT id, score 
    FROM scores 
    WHERE user_id = ? AND difficulty = ? 
    ORDER BY score DESC 
    LIMIT 1
");

if (!$best_score_stmt) {
    closeDbConnection($conn);
    sendResponse(false, 'Chyba při přípravě dotazu');
}

$best_score_stmt->bind_param("is", $user_id, $difficulty);
$best_score_stmt->execute();
$best_result = $best_score_stmt->get_result();

$action = 'new'; // 'new', 'better', or 'worse'
$old_score_id = null;
$old_score = 0;

if ($best_result->num_rows > 0) {
    $best_row = $best_result->fetch_assoc();
    $old_score_id = $best_row['id'];
    $old_score = $best_row['score'];
    
    if ($score > $old_score) {
        $action = 'better'; // Nové skóre je lepší
    } else {
        $action = 'worse'; // Nové skóre je horší nebo stejné
    }
}

$best_score_stmt->close();

// Pokud je nové skóre horší než existující, neuložíme ho
if ($action === 'worse') {
    closeDbConnection($conn);
    sendResponse(true, 'Skóre nebylo uloženo (máte lepší skóre: ' . $old_score . ')', [
        'saved' => false,
        'new_score' => $score,
        'best_score' => $old_score,
        'difficulty' => $difficulty
    ]);
}

// Pokud je nové skóre lepší, smažeme staré
if ($action === 'better' && $old_score_id !== null) {
    $delete_stmt = $conn->prepare("DELETE FROM scores WHERE id = ?");
    if ($delete_stmt) {
        $delete_stmt->bind_param("i", $old_score_id);
        $delete_stmt->execute();
        $delete_stmt->close();
    }
}

// Uložíme nové skóre
$insert_stmt = $conn->prepare("
    INSERT INTO scores (user_id, username, score, difficulty, date_created) 
    VALUES (?, ?, ?, ?, NOW())
");

if (!$insert_stmt) {
    closeDbConnection($conn);
    sendResponse(false, 'Chyba při přípravě dotazu: ' . $conn->error);
}

$insert_stmt->bind_param("isis", $user_id, $username, $score, $difficulty);

if ($insert_stmt->execute()) {
    $insert_id = $insert_stmt->insert_id;
    $insert_stmt->close();
    closeDbConnection($conn);
    
    $message = ($action === 'better') 
        ? 'Gratulace! Nové osobní rekord! (Předchozí: ' . $old_score . ')'
        : 'Skóre úspěšně uloženo';
    
    sendResponse(true, $message, [
        'saved' => true,
        'id' => $insert_id,
        'user_id' => $user_id,
        'username' => $username,
        'score' => $score,
        'difficulty' => $difficulty,
        'is_new_record' => ($action === 'better' || $action === 'new'),
        'old_score' => ($action === 'better') ? $old_score : null
    ]);
} else {
    $error = $insert_stmt->error;
    $insert_stmt->close();
    closeDbConnection($conn);
    sendResponse(false, 'Chyba při ukládání skóre: ' . $error);
}
?>