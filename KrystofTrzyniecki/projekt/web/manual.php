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
    <title>MANUÁL - SPACE SHOOTER</title>
    <link rel="stylesheet" href="style.css?v=<?php echo time(); ?>">
</head>
<body>

<nav>
    <div class="nav-left">
        <a href="index.php">Home</a>
        <a href="manual.php" style="color: #00ffcc;">Manuál</a>
        <a href="investor.php">Prezentace pro investora</a>
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
    <h1>HERNÍ MANUÁL</h1>
</header>

<main>
    <section>
        <h2>Základní ovládání</h2>
        <div class="info-grid">
            <div class="info-box">
                <h3>Pohyb a Střelba</h3>
                <ul>
                    <li><strong>Pohyb lodi:</strong> K pohybu po obrazovce použij šipky na klávesnici (nahoru, dolů, doleva, doprava).</li>
                    <li><strong>Střelba:</strong> Pro střelbu stiskni a drž mezerník (SPACE).</li>
                    <li><strong>Pauza:</strong> Probíhající hru můžeš kdykoliv pozastavit stisknutím klávesy ESC.</li>
                </ul>
            </div>
            <div class="info-box">
                <h3>Menu a Přihlášení</h3>
                <p>Pokud ještě nemáš herní účet, musíš si ho nejprve založit na webových stránkách hry. Při zadávání jména a hesla v úvodní obrazovce přepínáš mezi políčky klávesou <strong>TAB</strong>. Přihlášení potvrdíš klávesou <strong>ENTER</strong>. V menu a obchodu se pohybuješ klikáním myší, v obchodu lze navíc scrollovat kolečkem.</p>
            </div>
        </div>
    </section>

    <section>
        <h2>Nastavení (Settings)</h2>
        <p style="margin-bottom: 15px;">V sekci SETTINGS můžeš upravit technické parametry hry tak, aby ti co nejlépe vyhovovaly.</p>
        <div class="info-grid">
            <div class="info-box">
                <h3>Rozlišení</h3>
                <p>Můžeš přepínat mezi různými velikostmi okna (např. 800x600, 1024x768 nebo 1280x720). Hra automaticky přepočítá velikost lodi i nepřátel tak, aby zůstal zachován herní zážitek.</p>
            </div>
            <div class="info-box">
                <h3>Obtížnost</h3>
                <ul>
                    <li><strong>EASY:</strong> Pomalejší nepřátelé a méně asteroidů.</li>
                    <li><strong>MEDIUM:</strong> Standardní vyvážený zážitek.</li>
                    <li><strong>HARD:</strong> Rychlí nepřátelé a hustý déšť asteroidů.</li>
                </ul>
                <p><em>Změna obtížnosti: Vyšší obtížnost zvyšuje rychlost, s jakou se hra v průběhu času stává těžší.</em></p>
            </div>
        </div>
    </section>

    <section>
        <h2>Herní mechaniky a Cíle</h2>
        <p style="margin-bottom: 15px;">Cílem hry je přežít co nejdéle, zničit co nejvíce překážek a nahrát tak nejvyšší skóre. S přibývajícím časem přežití se postupně zvyšuje obtížnost hry (rychlost a počet nepřátel).</p>
        <div class="info-grid">
            <div class="info-box">
                <h3>Asteroidy</h3>
                <p>Padají shora dolů. Za jejich zničení získáš <strong>100 bodů</strong> a základní odměnu <strong>10 mincí</strong>.</p>
            </div>
            <div class="info-box">
                <h3>Nepřátelé</h3>
                <p>Létají ze strany na stranu, odrážejí se od okrajů obrazovky a střílejí po tobě lasery. Zničení nepřátelské lodi tě odmění <strong>500 body</strong> a základní odměnou <strong>50 mincí</strong>.</p>
            </div>
            <div class="info-box">
                <h3>Zásah</h3>
                <p>Pokud do tebe narazí asteroid, nepřítel, nebo tě trefí nepřátelský laser, ztrácíš jeden život (nebo aktivní štít) a na malou chvíli se staneš nesmrtelným, abys měl šanci uniknout.</p>
            </div>
        </div>
    </section>

    <section>
        <h2>Vylepšení a Bonusy (Power-upy)</h2>
        <p style="margin-bottom: 15px;">Kdykoliv zničíš asteroid nebo nepřítele, je tu 20% šance, že z něj vypadne bonusový předmět. Chytíš ho tak, že přes něj přelétneš lodí.</p>
        <div class="info-grid">
            <div class="info-box">
                <h3>Oprava</h3>
                <p>Doplní tvé lodi jeden ztracený život (maximálně do plné kapacity tvé lodi).</p>
            </div>
            <div class="info-box">
                <h3>Štít</h3>
                <p>Vytvoří kolem tvé lodi modrou ochrannou elipsu, která absorbuje přesně jeden jakýkoliv zásah.</p>
            </div>
            <div class="info-box">
                <h3>Rychlá palba</h3>
                <p>Zkrátí prodlevu mezi tvými výstřely na polovinu po dobu <strong>8 sekund</strong>.</p>
            </div>
            <div class="info-box">
                <h3>Trojitá střela</h3>
                <p>Tvá loď bude po dobu <strong>10 sekund</strong> střílet tři lasery najednou ve třech různých směrech.</p>
            </div>
        </div>
    </section>

    <section>
        <h2>SHOP</h2>
        <p style="margin-bottom: 15px;">V menu pod položkou SHOP si můžeš za nasbírané mince kupovat a vybírat nové lodě. Každá loď má jiné herní statistiky.</p>
        <div class="info-grid">
            <div class="info-box">
                <h3>Základní loď</h3>
                <p>Tvůj výchozí stroj se 3 životy, středně rychlou střelbou a normálním ziskem mincí.</p>
            </div>
            <div class="info-box">
                <h3>Rychlý letec</h3>
                <p>Rychlejší loď, která střílí rychleji a dává o 20 % více mincí, ale má pouze 2 životy.</p>
            </div>
            <div class="info-box">
                <h3>Těžký křižník</h3>
                <p>Nejpomalejší loď s nejpomalejší střelbou, nabízí ale vynikající ochranu v podobě 5 životů a dává o 50 % více mincí.</p>
            </div>
            <div class="info-box">
                <h3>Prototyp X</h3>
                <p>Nejdražší elitní loď se 4 životy, extrémně rychlou palbou a rovnou dvojnásobným ziskem mincí oproti základu.</p>
            </div>
        </div>
    </section>
</main>

<footer>
    <p>&copy; 2026 SPACE SHOOTER | Herní Studio</p>
</footer>

</body>
</html>