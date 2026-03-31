<?php
// save_score.php
require 'db.php';

$username = $_POST['username'] ?? '';
$new_score = intval($_POST['score'] ?? 0);

if (!empty($username)) {
    // Získáme stávající skóre
    $stmt = $pdo->prepare("SELECT high_score FROM users WHERE username = ?");
    $stmt->execute([$username]);
    $user = $stmt->fetch();

    if ($user && $new_score > $user['high_score']) {
        // Aktualizujeme pouze pokud je nové skóre vyšší
        $update = $pdo->prepare("UPDATE users SET high_score = ? WHERE username = ?");
        $update->execute([$new_score, $username]);
        echo json_encode(["status" => "success", "message" => "New high score!"]);
    } else {
        echo json_encode(["status" => "ignored", "message" => "Score not high enough."]);
    }
}
?>