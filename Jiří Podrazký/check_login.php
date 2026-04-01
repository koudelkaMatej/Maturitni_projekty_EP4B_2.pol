<?php
require 'db_connect.php';

if (isset($_POST['username']) && isset($_POST['password'])) {
    $u = $_POST['username'];
    $p = $_POST['password'];

    if ($db_connected) {
        $stmt = $pdo->prepare("SELECT password FROM s18_users WHERE username = ?");
        $stmt->execute([$u]);
        $user = $stmt->fetch(PDO::FETCH_ASSOC);

        if ($user && password_verify($p, $user['password'])) {
            echo "OK";
        } else {
            echo "ERROR";
        }
    } else {
        echo "DB_OFFLINE";
    }
}
?>