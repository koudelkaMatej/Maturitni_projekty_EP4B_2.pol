<?php
session_start();
require 'db_connect.php';

$error = "";

if ($_SERVER['REQUEST_METHOD'] == 'POST') {
    if (!$db_connected) {
        $error = "Databáze není připojená! Chyba: " . $db_error_msg;
    } else {
        $user = trim($_POST['username']);
        $pass = $_POST['password'];

        // TADY BYLA CHYBA - změněno na s18_users
        $stmt = $pdo->prepare("SELECT id, username, password FROM s18_users WHERE username = ?");
        $stmt->execute([$user]);
        $db_user = $stmt->fetch(PDO::FETCH_ASSOC);

        if ($db_user && password_verify($pass, $db_user['password'])) {
            $_SESSION['user_id'] = $db_user['id'];
            $_SESSION['username'] = $db_user['username'];
            header("Location: index.php");
            exit;
        } else {
            $error = "Špatné jméno nebo heslo.";
        }
    }
}
?>
<!DOCTYPE html>
<html lang="cs">
<head>
    <meta charset="UTF-8">
    <title>Přihlášení - Space Invaders</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <div class="auth-container">
        <h2>Vstup do kokpitu</h2>
        
        <?php if(!empty($error)): ?>
            <p style="color: #ff4d4d; background: rgba(255,0,0,0.1); padding: 10px; border: 1px solid red;">
                ⚠️ <?php echo $error; ?>
            </p>
        <?php endif; ?>

        <form method="post">
            <input type="text" name="username" placeholder="Uživatelské jméno" required>
            <input type="password" name="password" placeholder="Heslo" required>
            <button type="submit" class="btn">Přihlásit se</button>
        </form>
        <p><a href="register.php">Ještě nemám účet</a> | <a href="index.php">Zpět</a></p>
    </div>
</body>
</html>