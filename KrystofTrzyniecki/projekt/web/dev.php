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
    <title>Přehled pro nového spolupracovníka</title>
    <link rel="stylesheet" href="style.css?v=<?php echo time(); ?>">
    <style>
        /* Styl pro ukázky kódu */
        pre {
            background: #000;
            border: 1px solid #333;
            padding: 15px;
            overflow-x: auto;
            border-radius: 5px;
            margin: 10px 0;
            color: #ffff; /* Hlavní barva kódu */
            font-family: 'Courier New', Courier, monospace;
            font-size: 0.85em;
            line-height: 1.4;
        }
        code {
            color: #00ffcc;
            background: rgba(0, 255, 204, 0.1);
            padding: 2px 4px;
            border-radius: 3px;
        }
        .file-tag {
            color: #ffaa00;
            font-weight: bold;
            font-size: 0.9em;
            display: block;
            margin-bottom: 5px;
        }
    </style>
</head>
<body>

<nav>
    <div class="nav-left">
        <a href="index.php">Domů</a>
        <a href="manual.php">Manuál</a>
        <a href="investor.php">Prezentace pro investora</a>
        <a href="dev.php" style="color: #00ffcc;">Přehled pro nového spolupracovníka</a>
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
    <h1>Přehled pro nového spolupracovníka</h1>
    <p>Technická dokumentace, struktura projektu a správa herní logiky</p>
</header>

<main>
    <section>
        <p>Tato dokumentace podrobně rozebírá strukturu projektu, odpovědnosti jednotlivých souborů a poskytuje připravené ukázky kódu pro nejčastější úkoly.</p>
    </section>

    <section>
        <h2>1. Architektura a struktura souborů</h2>
        <p>Projekt je rozdělen tak, aby se nekřížila logika zobrazení (Menu) s logikou hry (Hráč/Nepřátelé).</p>
        
        <div class="info-grid">
            <div class="info-box">
                <h3>Jádro hry</h3>
                <ul>
                    <li><strong>main.py:</strong> Hlavní mozek. Obsahuje třídu <code>GameController</code>. Zde se řeší kolize, správa skóre a přepínání stavů.</li>
                    <li><strong>settings.py:</strong> Centrální mozek dat. Obsahuje veškeré konstanty (barvy, rychlosti, ceny). <strong>Jediné místo pro "natvrdo" napsaná čísla.</strong></li>
                </ul>
            </div>
            <div class="info-box">
                <h3>Herní entity (Objekty)</h3>
                <ul>
                    <li><strong>player.py:</strong> Loď hráče, pohyby, střelba a efekty power-upů.</li>
                    <li><strong>enemy.py:</strong> Pohyb nepřátel (cik-cak) a intervaly střelby.</li>
                    <li><strong>asteroid.py:</strong> Třída pro padající kameny, náhodná rotace.</li>
                    <li><strong>powerup.py:</strong> Správa bonusů (repair, shield, rapid, triple).</li>
                </ul>
            </div>
            <div class="info-box">
                <h3>Rozhraní a data</h3>
                <ul>
                    <li><strong>menu.py:</strong> Vykreslování textů, tlačítek a interakce v obchodě.</li>
                    <li><strong>auth.py:</strong> Komunikační modul. Odesílání skóre a ověřování uživatelů.</li>
                </ul>
            </div>
        </div>
    </section>

    <section>
        <h2>2. Klíčové ukázky kódu pro rychlý start</h2>

        <div class="info-box" style="width: 100%; margin-bottom: 20px;">
            <span class="file-tag"># settings.py</span>
            <h3>Jak funguje systém lodí a statistik</h3>
            <p>Místo složitého kódování nových lodí stačí přidat řádek do tohoto slovníku. O vykreslení v obchodu a nastavení statistik v bitvě se postará zbytek programu automaticky.</p>
            <pre># Formát: "Jméno": ["obrázek.png", cena, životy, rychlost_palby, rychlost_pohybu, násobič_mincí]
SKIN_DATA = {
    "Základní loď": ["ship1.png", 0, 3, 500, 5, 1.0],
    "Rychlý letec": ["ship2.png", 500, 2, 300, 8, 1.2],
    "Těžký křižník": ["ship3.png", 1000, 5, 700, 3, 1.5]
}</pre>
        </div>

        <div class="info-box" style="width: 100%; margin-bottom: 20px;">
            <span class="file-tag"># player.py</span>
            <h3>Jak se počítá "Nesmrtelnost" po zásahu</h3>
            <p>Aby hráč neumřel hned při kontaktu s více objekty najednou, používáme po zásahu krátký časovač.</p>
            <pre>def hit(self):
    if not self.invincible:
        if self.shield_active:
            self.shield_active = False # Štít tě zachrání
        else:
            self.lives -= 1
        # Aktivace nesmrtelnosti na 2 sekundy (2000 ms)
        self.invincible = True
        self.inv_timer = pygame.time.get_ticks() + 2000</pre>
        </div>

        <div class="info-box" style="width: 100%; margin-bottom: 20px;">
            <span class="file-tag"># main.py</span>
            <h3>Detekce kolizí "na pixel přesně"</h3>
            <p>Vesmírné lodi mají složité tvary. Proto nepoužíváme jen obdélníky, ale tzv. masky.</p>
            <pre># Uvnitř smyčky kontrolující kolize
offset = (asteroid.rect.x - self.player.rect.x, asteroid.rect.y - self.player.rect.y)
if self.player.mask.overlap(asteroid.mask, offset):
    self.player.hit() # Došlo ke skutečnému dotyku pixelů
    asteroid.explode()</pre>
        </div>

        <div class="info-box" style="width: 100%;">
            <span class="file-tag"># auth.py</span>
            <h3>Odesílání High Score na server</h3>
            <pre>def update_high_score(username, score):
    url = f"{URL_BASE}/save_score.php"
    try:
        # verify=False je tu kvůli ignorování problémů s SSL certifikáty na školním serveru
        requests.post(url, data={'username': username, 'score': int(score)}, timeout=5, verify=False)
    except:
        print("Chyba: Skóre se nepodařilo odeslat na server.")</pre>
        </div>
    </section>

    <section>
        <div class="info-box" style="border: 1px dashed #00ffcc; text-align: center;">
            <h3>Příprava vývojového prostředí</h3>
            <p>Hra vyžaduje nainstalované knihovny <strong>pygame</strong> a <strong>requests</strong>.</p>
            <code>pip install pygame requests</code>
        </div>
    </section>
</main>

<footer>
    <p>&copy; 2026 SPACE SHOOTER | Herní Studio</p>
</footer>

</body>
</html>