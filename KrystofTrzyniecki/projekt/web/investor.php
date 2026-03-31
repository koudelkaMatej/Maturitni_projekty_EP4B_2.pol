<?php
session_start();
require_once 'db.php';
$isLoggedIn = isset($_SESSION['user']);
?>

<!DOCTYPE html>
<html lang="cs">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PREZENTACE PRO INVESTORA - SPACE SHOOTER</title>
    <link rel="stylesheet" href="style.css?v=<?php echo time(); ?>">
    <style>
        /* Speciální doplňky pro investorský vzhled */
        .slide-number {
            color: #00ffcc;
            font-size: 0.9em;
            text-transform: uppercase;
            letter-spacing: 2px;
            margin-bottom: 10px;
            display: block;
        }
        section {
            border-left: 3px solid #00ffcc;
            padding-left: 30px;
            margin-bottom: 60px;
        }
        .highlight-box {
            background: rgba(0, 255, 204, 0.05);
            border: 1px solid rgba(0, 255, 204, 0.2);
            padding: 20px;
            border-radius: 8px;
            margin-top: 15px;
        }
    </style>
</head>
<body>

<nav>
    <div class="nav-left">
        <a href="index.php">Home</a>
        <a href="manual.php">Manuál</a>
        <a href="investor.php" style="color: #00ffcc;">Prezentace pro investora</a>
        <a href="dev.php">Přehled pro nového spolupracovníka </a>
        <?php if ($isLoggedIn): ?>
            <a href="index.php#scoreboard">Scoreboard</a>
        <?php endif; ?>
    </div>
    <div class="nav-right">
        <?php if ($isLoggedIn): ?>
            <span style="color: #00ffcc; margin-right: 15px;">👤 <?php echo $_SESSION['user']; ?></span>
            <a href="index.php?logout=1" class="btn-logout">Odhlásit se</a>
        <?php else: ?>
            <a href="index.php" class="btn-nav-login">Přihlásit se</a>
        <?php endif; ?>
    </div>
</nav>

<header>
    <h1>PREZENTACE PRO INVESTORA</h1>
    <p>Představení strategického potenciálu projektu Space Shooter</p>
</header>

<main>

    <section id="vize">
        <h2>Vize projektu: Space Shooter</h2>
        <p><strong>Cíl:</strong> Transformace klasického arkádového žánru v moderní, daty řízenou herní platformu.</p>
        <div class="info-grid">
            <div class="info-box">
                <h3>Produkt</h3>
                <p>Responzivní vesmírná střílečka s plnou integrací na cloudové služby.</p>
            </div>
            <div class="info-box">
                <h3>Hlavní hodnota</h3>
                <p>Spojení okamžité hratelnosti (instant-play) s komplexním systémem hráčských účtů a progrese.</p>
            </div>
        </div>
    </section>

    <section id="design">
        <h2>Herní design a retence hráčů</h2>
        <div class="info-grid">
            <div class="info-box">
                <h3>Adaptivní obtížnost</h3>
                <p>Algoritmus v <code>settings.py</code> zajišťuje, že se hra přizpůsobuje dovednostem hráče v reálném čase. Tím eliminujeme nudu u zkušených hráčů a frustraci u nováčků.</p>
            </div>
            <div class="info-box">
                <h3>Motivační cyklus</h3>
                <p>Systém odměn (mince za aktivitu) a vylepšení (power-upy) vytváří silný dopaminový efekt a motivuje k opakovanému hraní.</p>
            </div>
            <div class="info-box">
                <h3>Customizace</h3>
                <p>Čtyři unikátní třídy lodí s odlišnými statistikami umožňují hráčům najít jejich vlastní herní styl.</p>
            </div>
        </div>
    </section>

    <section id="architektura">
        <h2>Technická architektura</h2>
        <div class="info-grid">
            <div class="info-box">
                <h3>Full-stack řešení</h3>
                <p>Na rozdíl od běžných indie her má náš projekt vlastní autentizační vrstvu (<code>auth.py</code>) komunikující se vzdáleným MySQL serverem přes PHP API.</p>
            </div>
            <div class="info-box">
                <h3>Bezpečnost a data</h3>
                <p>Šifrovaná komunikace a centralizované ukládání high-score umožňují pořádání globálních turnajů a budování komunity.</p>
            </div>
            <div class="info-box">
                <h3>Modulární architektura</h3>
                <p>Architektura je navržena tak, aby bylo možné grafické rozhraní (GUI) a herní logiku snadno aktualizovat bez nutnosti měnit jádro systému.</p>
            </div>
        </div>
    </section>

    <section id="ekonomika">
        <h2>Monetizační model a ekonomika</h2>
        <div class="info-grid">
            <div class="info-box">
                <h3>Progrese a výkon</h3>
                <p>Hráči jsou motivováni k nákupu prémiového obsahu (např. Prototyp X) prostřednictvím herní měny, jejíž zisk je přímo navázán na zvolenou loď.</p>
            </div>
            <div class="info-box">
                <h3>Škálovatelnost</h3>
                <p>Model je připraven na implementaci mikrotransakcí pro nákup herní měny nebo exkluzivních limitovaných skinů.</p>
            </div>
        </div>
        <div class="highlight-box">
            <p><strong>Nízké provozní náklady:</strong> Díky optimalizovanému kódu v Pythonu jsou nároky na klientský hardware minimální, což otevírá obrovský trh uživatelů.</p>
        </div>
    </section>

    <section id="roadmap">
        <h2>Roadmap: Další kroky</h2>
        <div class="info-grid">
            <div class="info-box">
                <h3>Fáze 1</h3>
                <p>Rozšíření webového portálu pro správu účtů a hloubkovou statistiku hráčů.</p>
            </div>
            <div class="info-box">
                <h3>Fáze 2</h3>
                <p>Implementace sezónních eventů a nových typů nepřátel s pokročilou AI.</p>
            </div>
            <div class="info-box">
                <h3>Fáze 3</h3>
                <p>Expanze na mobilní platformy a integrace sociálních funkcí.</p>
            </div>
        </div>
    </section>

</main>

<footer>
    <p>&copy; 2026 SPACE SHOOTER | Herní Studio</p>
</footer>

</body>
</html>