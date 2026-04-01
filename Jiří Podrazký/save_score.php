<?php
require 'db_connect.php';

if (isset($_POST['username']) && isset($_POST['score'])) {
    $username = $_POST['username'];
    $score = (int)$_POST['score'];

    if ($db_connected) {
        $stmt = $pdo->prepare("SELECT id FROM s18_users WHERE username = ?");
        $stmt->execute([$username]);
        $user = $stmt->fetch(PDO::FETCH_ASSOC);

        if ($user) {
            $stmt = $pdo->prepare("INSERT INTO s18_scoreboard (user_id, score) VALUES (?, ?)");
            $stmt->execute([$user['id'], $score]);
            echo "OK";
        } else {
            echo "Uživatel nenalezen";
        }
    }
}
?>