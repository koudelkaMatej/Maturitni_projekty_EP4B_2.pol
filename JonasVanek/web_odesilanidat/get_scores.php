<?php
/**
 * get_scores.php
 * 
 * Vrací seznam nejlepších skóre s podporou filtrování podle obtížnosti.
 * Pro každého uživatele zobrazuje pouze jeho nejlepší skóre na dané obtížnosti.
 * 
 * GET parametry:
 * - limit: Počet výsledků (default: 100, max: 500)
 * - offset: Od kterého záznamu začít (default: 0)
 * - difficulty: Filtr obtížnosti ("all", "lehka", "stredni", "tezka", default: "all")
 */

require_once 'config.php';

header('Content-Type: application/json; charset=utf-8');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: GET');

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

// Získání parametrů
$limit = isset($_GET['limit']) ? intval($_GET['limit']) : 100;
$offset = isset($_GET['offset']) ? intval($_GET['offset']) : 0;
$difficulty_filter = isset($_GET['difficulty']) ? trim($_GET['difficulty']) : 'all';

// Validace parametrů
if ($limit < 1) $limit = 100;
if ($limit > 500) $limit = 500;
if ($offset < 0) $offset = 0;

// Validace obtížnosti
$valid_difficulties = ['all', 'lehka', 'stredni', 'tezka'];
if (!in_array($difficulty_filter, $valid_difficulties)) {
    $difficulty_filter = 'all';
}

// Připojení k databázi
$conn = getDbConnection();
if (!$conn) {
    sendResponse(false, 'Chyba připojení k databázi');
}

// Sestavíme SQL dotaz
// Pro každého uživatele na každé obtížnosti vezmeme jen nejlepší skóre
$sql = "
    SELECT 
        s.id,
        s.user_id,
        s.username,
        s.score,
        s.difficulty,
        s.date_created
    FROM scores s
    INNER JOIN (
        SELECT 
            user_id, 
            difficulty, 
            MAX(score) as max_score
        FROM scores
";

// Přidáme filtr obtížnosti, pokud není "all"
if ($difficulty_filter !== 'all') {
    $sql .= " WHERE difficulty = ? ";
}

$sql .= "
        GROUP BY user_id, difficulty
    ) best 
    ON s.user_id = best.user_id 
    AND s.difficulty = best.difficulty 
    AND s.score = best.max_score
";

// Seřazení podle skóre
$sql .= " ORDER BY s.score DESC, s.date_created ASC LIMIT ? OFFSET ?";

// Příprava dotazu
$stmt = $conn->prepare($sql);
if (!$stmt) {
    closeDbConnection($conn);
    sendResponse(false, 'Chyba při přípravě dotazu: ' . $conn->error);
}

// Navázání parametrů
if ($difficulty_filter !== 'all') {
    $stmt->bind_param("sii", $difficulty_filter, $limit, $offset);
} else {
    $stmt->bind_param("ii", $limit, $offset);
}

// Provedení dotazu
if (!$stmt->execute()) {
    $error = $stmt->error;
    $stmt->close();
    closeDbConnection($conn);
    sendResponse(false, 'Chyba při získávání dat: ' . $error);
}

// Získání výsledků
$result = $stmt->get_result();
$scores = [];
$rank = $offset + 1;

while ($row = $result->fetch_assoc()) {
    $scores[] = [
        'rank' => $rank++,
        'id' => $row['id'],
        'user_id' => $row['user_id'],
        'username' => $row['username'],
        'score' => intval($row['score']),
        'difficulty' => $row['difficulty'],
        'date' => $row['date_created']
    ];
}

$stmt->close();

// Získání celkového počtu záznamů
$count_sql = "
    SELECT COUNT(*) as total
    FROM (
        SELECT user_id, difficulty, MAX(score) as max_score
        FROM scores
";

if ($difficulty_filter !== 'all') {
    $count_sql .= " WHERE difficulty = ? ";
}

$count_sql .= "
        GROUP BY user_id, difficulty
    ) as unique_scores
";

$count_stmt = $conn->prepare($count_sql);
if ($count_stmt) {
    if ($difficulty_filter !== 'all') {
        $count_stmt->bind_param("s", $difficulty_filter);
    }
    $count_stmt->execute();
    $count_result = $count_stmt->get_result();
    $count_row = $count_result->fetch_assoc();
    $total_count = intval($count_row['total']);
    $count_stmt->close();
} else {
    $total_count = 0;
}

closeDbConnection($conn);

// Odeslání odpovědi
sendResponse(true, 'Skóre úspěšně načteno', [
    'scores' => $scores,
    'total_count' => $total_count,
    'limit' => $limit,
    'offset' => $offset,
    'difficulty_filter' => $difficulty_filter
]);
?>