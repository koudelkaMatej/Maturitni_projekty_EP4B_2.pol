<?php
/**
 * change_username.php
 *
 * Změna uživatelového jména.  Ověřuje:
 *   – uživatel existuje
 *   – nové jméno splňuje pravidla (3-30 znaků)
 *   – nové jméno není dosud použité
 * Při úspěchu aktualizuje OBĚ tabulky (users i scores).
 *
 * POST:
 *   user_id       (int)
 *   new_username  (string)
 */

require_once 'config.php';

header('Content-Type: application/json; charset=utf-8');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: POST');
header('Access-Control-Allow-Headers: Content-Type');

function respond($ok, $msg = '', $data = null) {
    $r = ['success' => $ok, 'message' => $msg];
    if ($data !== null) $r['data'] = $data;
    echo json_encode($r, JSON_UNESCAPED_UNICODE);
    exit;
}

if ($_SERVER['REQUEST_METHOD'] !== 'POST') respond(false, 'Pouze POST');

$user_id      = intval($_POST['user_id']      ?? 0);
$new_username = trim($_POST['new_username'] ?? '');

// ---------- validace ----------
if ($user_id <= 0)                          respond(false, 'Neplatné user_id');
if (strlen($new_username) < 3)              respond(false, 'Jméno musí mít alespoň 3 znaky');
if (strlen($new_username) > 30)             respond(false, 'Jméno může mít maximálně 30 znaků');
if (!preg_match('/^[\p{L}\p{N}_\- ]+$/u', $new_username))
                                            respond(false, 'Jméno obsahuje nedovolené znaky');

// ---------- DB ----------
$conn = getDbConnection();
if (!$conn) respond(false, 'Chyba připojení k databázi');

// --- ověření uživatele ---
$s = $conn->prepare("SELECT id, username FROM users WHERE id = ?");
$s->bind_param("i", $user_id);
$s->execute();
$current = $s->get_result()->fetch_assoc();
$s->close();
if (!$current) { closeDbConnection($conn); respond(false, 'Uživatel neexistuje'); }

// --- pokud je nové jméno stejné jako stávající, nic neděláme ---
if ($current['username'] === $new_username) {
    closeDbConnection($conn);
    respond(true, 'Jméno se nezměnilo – je to tvé aktuální jméno', ['username' => $new_username]);
}

// --- kontrola unikátnosti nového jména ---
$s = $conn->prepare("SELECT id FROM users WHERE username = ? AND id != ?");
$s->bind_param("si", $new_username, $user_id);
$s->execute();
if ($s->get_result()->num_rows > 0) {
    $s->close();
    closeDbConnection($conn);
    respond(false, 'Jméno „' . $new_username . '" je již obsazené');
}
$s->close();

// ---------- aktualizace ----------
// users
$s = $conn->prepare("UPDATE users SET username = ? WHERE id = ?");
$s->bind_param("si", $new_username, $user_id);
if (!$s->execute()) {
    $err = $s->error; $s->close(); closeDbConnection($conn);
    respond(false, 'Chyba při aktualizaci users: ' . $err);
}
$s->close();

// scores (uchová konzistenci – username je denormalizovaný sloupec)
$s = $conn->prepare("UPDATE scores SET username = ? WHERE user_id = ?");
$s->bind_param("si", $new_username, $user_id);
if (!$s->execute()) {
    $err = $s->error; $s->close(); closeDbConnection($conn);
    respond(false, 'Chyba při aktualizaci scores: ' . $err);
}
$s->close();

closeDbConnection($conn);
respond(true, 'Jméno úspěšně změněno na „' . $new_username . '"', ['username' => $new_username]);
?>
