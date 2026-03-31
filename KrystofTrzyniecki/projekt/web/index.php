<?php
session_start();
require_once 'db.php';

// 1. Načtení reálných dat z databáze
$scores = [];
try {
    // Vytáhneme jméno a nejvyšší skóre, seřazené od největšího
    $stmt = $pdo->query("SELECT username as name, high_score as score FROM users WHERE high_score > 0 ORDER BY high_score DESC LIMIT 10");
    $scores = $stmt->fetchAll();
} catch (Exception $e) {
    // Pokud nastane chyba (např. tabulka neexistuje), necháme pole prázdné
    $scores = [];
}

$message = "";

// Logika REGISTRACE
if (isset($_POST['register_user'])) {
    $user = htmlspecialchars(trim($_POST['username']));
    $pass = $_POST['password'];

    $stmt = $pdo->prepare("SELECT * FROM users WHERE username = ?");
    $stmt->execute([$user]);
    
    if ($stmt->fetch()) {
        $message = "Tento účet už v databázi existuje!";
    } else {
        $hashedPass = password_hash($pass, PASSWORD_DEFAULT);
        $stmt = $pdo->prepare("INSERT INTO users (username, password) VALUES (?, ?)");
        
        if ($stmt->execute([$user, $hashedPass])) {
            $_SESSION['user'] = $user;
            header("Location: index.php");
            exit;
        } else {
            $message = "Chyba při registraci do databáze.";
        }
    }
}

// Logika PŘIHLÁŠENÍ
if (isset($_POST['login_user'])) {
    $user = htmlspecialchars(trim($_POST['username']));
    $pass = $_POST['password'];

    $stmt = $pdo->prepare("SELECT * FROM users WHERE username = ?");
    $stmt->execute([$user]);
    $dbUser = $stmt->fetch();

    if ($dbUser && password_verify($pass, $dbUser['password'])) {
        $_SESSION['user'] = $dbUser['username'];
        header("Location: index.php");
        exit;
    } else {
        $message = "Špatné jméno nebo heslo!";
    }
}

// Logika ODHLÁŠENÍ
if (isset($_GET['logout'])) {
    session_destroy();
    header("Location: index.php");
    exit;
}

$isLoggedIn = isset($_SESSION['user']);


?>

<!DOCTYPE html>
<html lang="cs">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SPACE SHOOTER</title>
    <link rel="stylesheet" href="style.css?v=<?php echo time(); ?>">
</head>
<body>

<nav>
    <div class="nav-left">
        <a href="index.php" style="color: #00ffcc;">Home</a>
        <a href="manual.php">Manuál</a>
        <a href="investor.php">Prezentace pro investora</a>
        <a href="dev.php">Přehled pro nového spolupracovníka</a>
        <?php if ($isLoggedIn): ?>
            <a href="index.php#scoreboard">Scoreboard</a>
        <?php endif; ?>
        <a href="diagram.jpg" target="_blank">Er-diagram</a>
    </div>
    <div class="nav-right">
        <?php if ($isLoggedIn): ?>
            <span style="color: #00ffcc; margin-right: 15px;">👤 <?php echo $_SESSION['user']; ?></span>
            <a href="index.php?logout=1" class="btn-logout">Odhlásit se</a>
        <?php else: ?>
            <button id="openLoginBtn" class="btn-nav-login">Přihlásit se</button>
            <button id="openRegisterBtn" class="btn-nav-reg">Vytvořit účet</button>
        <?php endif; ?>
    </div>
</nav>

<?php if ($message): ?>
    <div style="background: #ff4444; color: white; text-align: center; padding: 10px; font-weight: bold;"><?php echo $message; ?></div>
<?php endif; ?>

<div id="loginModal" class="modal-overlay hidden">
    <div class="modal-content">
        <span class="close-btn" id="closeLogin">&times;</span>
        <h2>Přihlásit se</h2>
        <form method="POST">
            <input type="text" name="username" placeholder="Uživatelské jméno" required>
            <input type="password" name="password" placeholder="Heslo" required>
            <button type="submit" name="login_user" class="btn-primary">Vstoupit</button>
        </form>
    </div>
</div>

<div id="registerModal" class="modal-overlay hidden">
    <div class="modal-content">
        <span class="close-btn" id="closeRegister">&times;</span>
        <h2>Vytvořit účet</h2>
        <form method="POST">
            <input type="text" name="username" placeholder="Nové jméno" required>
            <input type="password" name="password" placeholder="Heslo" required>
            <button type="submit" name="register_user" class="btn-primary">Zaregistrovat se</button>
        </form>
    </div>
</div>

<header>
    <h1>SPACE SHOOTER</h1>
</header>

<main>
    <section id="o-hre">
        <h2>O hře</h2>
        <p>Space Shooter je dynamická arkádová střílečka vytvořená v jazyce Python pomocí knihovny Pygame. Převezměte kontrolu nad svou vesmírnou lodí, 
            vyhýbejte se nebezpečným asteroidům a zlikvidujte vlny nepřátelských útočníků v nekonečném boji o nejvyšší skóre.</p>
        <div class="info-grid">
            <div class="info-box">
                <h3>Ovládání</h3>
                <ul>
                    <li><strong>Šipky:</strong> Pohyb lodi</li>
                    <li><strong>Mezerník:</strong> Střelba laserem</li>
                    <li><strong>ESC:</strong> Pauza</li>
                </ul>
            </div>
            <div class="info-box">
                <h3>Ekonomika</h3>
                <ul>
                    <li><strong>Zabití:</strong> Mince za nepřátele (50) a asteroidy (10).</li>
                    <li><strong>Skiny:</strong> Vydělané kredity můžete utratit v obchodě za nové, vizuálně unikátní skiny lodí.</li>
                </ul>
            </div>
        </div>
    </section>

    <?php if ($isLoggedIn): ?>
    <section id="scoreboard">
        <h2><strong>SCOREBOARD</strong></h2>
        <div class="table-wrapper">
            <table>
                <thead>
                    <tr><th>Pořadí</th><th>Hráč</th><th>Skóre</th></tr>
                </thead>
                <tbody>
                    <?php 
                    // Pro jistotu ještě jednou seřadíme, i když SQL to už udělalo
                    usort($scores, fn($a, $b) => $b['score'] <=> $a['score']);
                    
                    if (empty($scores)): ?>
                        <tr><td colspan="3" style="text-align:center;">Zatím nebyla nahrána žádná skóre.</td></tr>
                    <?php else:
                        foreach ($scores as $index => $player): 
                        ?>
                        <tr>
                            <td><?php echo $index + 1; ?>.</td>
                            <td><?php echo htmlspecialchars($player['name']); ?></td>
                            <td><?php echo number_format($player['score']); ?></td>
                        </tr>
                        <?php endforeach; 
                    endif; ?>
                </tbody>
            </table>
        </div>
    </section>
    <?php else: ?>
    <section class="locked">
        <p>Pro přístup k žebříčku se musíš přihlásit.</p>
    </section>
    <?php endif; ?>
</main>

<footer>
    <p>&copy; 2026 SPACE SHOOTER | Herní Studio</p>
</footer>

<script src="script.js?v=<?php echo time(); ?>"></script>
</body>
</html>