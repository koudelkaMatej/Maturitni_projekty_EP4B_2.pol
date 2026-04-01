<?php
session_start();
require 'db_connect.php';

$error = "";
$success = "";

if ($_SERVER['REQUEST_METHOD'] == 'POST') {
    if (!$db_connected) {
        $error = "Databáze nejede, nelze se registrovat.";
    } else {
        $user = trim($_POST['username']);
        $pass = $_POST['password'];

        if (strlen($user) < 3) {
            $error = "Jméno musí mít aspoň 3 znaky.";
        } else {
            $hashed_pass = password_hash($pass, PASSWORD_DEFAULT);
            try {
                // TADY BYLA CHYBA - změněno na s18_users
                $stmt = $pdo->prepare("INSERT INTO s18_users (username, password) VALUES (?, ?)");
                $stmt->execute([$user, $hashed_pass]);
                $success = "Registrace hotova! Teď se můžeš přihlásit.";
            } catch (Exception $e) {
                $error = "Tohle jméno už někdo vyfoukl (nebo jiná DB chyba).";
            }
        }
    }
}
?>
<!DOCTYPE html>
<html lang="cs">
<head>
    <meta charset="UTF-8">
    <title>Registrace - Space Invaders</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <div class="auth-container">
        <h2>Nová posádka</h2>
        
        <?php if(!empty($error)) echo "<p style='color:red;'>⚠️ $error</p>"; ?>
        <?php if(!empty($success)) echo "<p style='color:green;'>✅ $success</p>"; ?>

        <form method="post">
            <input type="text" name="username" placeholder="Zvol si jméno" required>
            <input type="password" name="password" placeholder="Zvol si heslo" required>
            <button type="submit" class="btn">Zaregistrovat</button>
        </form>
        <p><a href="login.php">Už jsem členem</a> | <a href="index.php">Zpět</a></p>
    </div>
</body>
</html>