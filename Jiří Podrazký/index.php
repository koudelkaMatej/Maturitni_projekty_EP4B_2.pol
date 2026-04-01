<?php 
session_start(); 
require 'db_connect.php'; 
?>
<!DOCTYPE html>
<html lang="cs">
<head>
    <meta charset="UTF-8">
    <title>Space Invaders - Scoreboard</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <header>
        <h1>🚀 SPACE INVADERS</h1>
        <nav>
            <?php if (isset($_SESSION['username'])): ?>
                <span>Vítej, pilot <strong><?php echo htmlspecialchars($_SESSION['username']); ?></strong>!</span>
                <a href="logout.php" class="btn-small">Odhlásit se</a>
            <?php else: ?>
                <a href="login.php" class="btn">Přihlášení</a>
                <a href="register.php" class="btn">Registrace</a>
            <?php endif; ?>
        </nav>
    </header>

    <main>
        <!-- DOWNLOAD sekce pro všechny -->
        <section class="download-section" style="margin-bottom: 40px;">
            <div style="background: rgba(233, 69, 96, 0.1); border: 1px solid #e94560; padding: 30px; border-radius: 15px; display: inline-block; width: 100%; box-sizing: border-box;">
                <h2 style="margin-top: 0; color: #fff;">PŘIPRAVTE SE K BOJI, PILOTE!</h2>
                <a href="SpaceInvaders_Enterprise.zip" class="download-btn">🎮 STÁHNOUT ENGINE HRY (.zip)</a>
                <p style="margin-top: 15px; color: #00ffcc;">
                    Rozbalte archiv a spusťte <strong><code>start_hry.bat</code></strong> pro zahájení mise.
                </p>
            </div>
        </section>

        <?php if (isset($_SESSION['user_id'])): ?>
            <section class="personal-stats">
                <?php
                // Získání osobního rekordu
                $stmtPb = $pdo->prepare("SELECT MAX(score) as pb FROM s18_scoreboard WHERE user_id = ?");
                $stmtPb->execute([$_SESSION['user_id']]);
                $pb = $stmtPb->fetch(PDO::FETCH_ASSOC)['pb'] ?? 0;
                ?>
                <div class="pb-badge">
                    <h3>Tvůj osobní rekord: <span><?php echo $pb; ?></span> bodů</h3>
                </div>


                <?php
                $stmtMy = $pdo->prepare("SELECT score, played_at FROM s18_scoreboard WHERE user_id = ? ORDER BY played_at DESC LIMIT 5");
                $stmtMy->execute([$_SESSION['user_id']]);
                $userScoresFound = false;
                while ($row = $stmtMy->fetch(PDO::FETCH_ASSOC)) {
                    if (!$userScoresFound) {
                        echo "<table><tr><th>Skóre</th><th>Datum</th></tr>";
                        $userScoresFound = true;
                    }
                    echo "<tr><td>{$row['score']}</td><td>{$row['played_at']}</td></tr>";
                }
                if (!$userScoresFound) {
                    echo "<p style='color: #888;'>Zatím jsi neuskutečnil žádnou misi. Stáhni si hru níže a začni bojovat!</p>";
                } else {
                    echo "</table>";
                }
                ?>
            </section>
            <hr>
        <?php endif; ?>

        <h2>GLOBÁLNÍ TOP 10 PILOTŮ</h2>
        <table>
            <tr>
                <th>Pořadí</th>
                <th>Hráč</th>
                <th>Skóre</th>
                <th>Datum</th>
            </tr>
            <?php
            if ($db_connected) {
                $stmt = $pdo->query("SELECT u.username, s.score, s.played_at 
                                     FROM s18_scoreboard s
                                     JOIN s18_users u ON s.user_id = u.id 
                                     ORDER BY s.score DESC LIMIT 10");
                $rank = 1;
                while ($row = $stmt->fetch(PDO::FETCH_ASSOC)) {
                    $highlight = (isset($_SESSION['username']) && $_SESSION['username'] == $row['username']) ? "style='color: #00ffcc; font-weight: bold;'" : "";
                    echo "<tr $highlight><td>{$rank}.</td><td>" . htmlspecialchars($row['username']) . "</td><td>{$row['score']}</td><td>{$row['played_at']}</td></tr>";
                    $rank++;
                }
            } else {
                echo "<tr><td colspan='4'>Databáze není připojená.</td></tr>";
            }
            ?>
        </table>

        <!-- 🚀 SPACE INVADERS: OPERAČNÍ MANUÁL -->
        <section class="manual-section">
            <h2>📜 OPERAČNÍ MANUÁL</h2>

            <div class="manual-card">
                <h3>🔐 1. Přístup do systému (Login)</h3>
                <p>Před zahájením mise je nutná autorizace operátora proti centrální databázi.</p>
                <ul>
                    <li><strong>Vstupní pole:</strong> Přepínejte mezi jménem a heslem pomocí klávesy <code>TAB</code>.</li>
                    <li><strong>Autorizace:</strong> Stiskněte <code>ENTER</code> pro odeslání požadavku na server.</li>
                    <li><strong>Offline režim:</strong> Pokud server neodpovídá, systém vás upozorní na chybu spojení.</li>
                </ul>
            </div>

            <div class="manual-card">
                <h3>🌌 2. Hlavní terminál a Hangár</h3>
                <p>Po úspěšném přihlášení získáte přístup k následujícím modulům:</p>
                <ul>
                    <li><strong>HRÁT:</strong> Spustí ostrou bojovou simulaci s aktuálně nakonfigurovaným plavidlem.</li>
                    <li><strong>HANGÁR:</strong> Vstup do výběru lodí. Klikněte myší na libovolný model v mřížce. Vybraná loď je indikována zlatým rámečkem. Pro potvrzení a návrat stiskněte <code>ZPĚT</code>.</li>
                    <li><strong>KONEC:</strong> Bezpečné ukončení všech procesů a odhlášení.</li>
                </ul>
            </div>

            <div class="manual-card">
                <h3>🎮 3. Ovládání plavidla</h3>
                <p>Bojový modul využívá pokročilou vektorovou kinematiku.</p>
                <ul>
                    <li><strong>Pohyb vlevo:</strong> Klávesa <code>Šipka DOLEVA</code></li>
                    <li><strong>Pohyb vpravo:</strong> Klávesa <code>Šipka DOPRAVA</code></li>
                    <li><strong>Palba:</strong> Klávesa <code>MEZERNÍK</code></li>
                </ul>
                <blockquote>
                    <strong>Taktický tip:</strong> Loď využívá efekt <strong>Banking</strong> (kinetické naklánění). Při rychlém manévrování se loď nakloní do směru letu, což zlepšuje vizuální přehled o trajektorii.
                </blockquote>
            </div>

            <div class="manual-card">
                <h3>👾 4. Taktická analýza nepřátel</h3>
                <p>Nepřátelské entity vstupují do sektoru skrze <strong>Hyperprostor (Warp-in)</strong>. Během modrého světelného záblesku a protahování textury jsou entity v meziprostoru a jsou <strong>imunní vůči palbě</strong>.</p>
                
                <table class="enemy-table">
                    <thead>
                        <tr>
                            <th>Typ entity</th>
                            <th>Vlastnosti</th>
                            <th>Integrita (HP)</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td class="enemy-type yellow-normal">Yellow Normal</td>
                            <td>Standardní rychlost, základní hrozba.</td>
                            <td>1 zásah</td>
                        </tr>
                        <tr>
                            <td class="enemy-type green-tank">Green Tank</td>
                            <td>Pomalý, robustní pancéřování. Má viditelný Healthbar.</td>
                            <td>3 zásahy</td>
                        </tr>
                        <tr>
                            <td class="enemy-type black-assassin">Black Assassin</td>
                            <td>Extrémní rychlost, zanechává Phantom Trail (stíny).</td>
                            <td>1 zásah</td>
                        </tr>
                    </tbody>
                </table>
            </div>

            <div class="manual-card">
                <h3>🛠️ 5. Evoluční moduly (Upgrady)</h3>
                <p>Během boje se v operační zóně zhmotňují <strong>zlaté levitující bedny (Lootboxy)</strong>. Jejich sebráním vyvoláte menu evoluce (klávesy <code>1</code>, <code>2</code> nebo <code>3</code>):</p>
                
                <div class="upgrade-grid">
                    <div class="upgrade-item"><strong>VOLLEY</strong>Přidá další střelu</div>
                    <div class="upgrade-item"><strong>PLASMA</strong>Zvýší úsťovou rychlost</div>
                    <div class="upgrade-item"><strong>WIDE BEAM</strong>Zvětší kalibr střel</div>
                    <div class="upgrade-item"><strong>DRONE SQUAD</strong>Autonomní drony</div>
                    <div class="upgrade-item"><strong>TURBO ENGINES</strong>Zvýší rychlost lodě</div>
                    <div class="upgrade-item"><strong>SHIELD REPAIR</strong>Oprava 1 HP</div>
                </div>
            </div>

            <div class="manual-card">
                <h3>⚠️ 6. Obranný perimetr a Bossové</h3>
                <ul>
                    <li><strong>Kritická linie:</strong> Spodní rudý laserový perimetr. Pokud nepřítel proletí pod tuto linii, dojde k <strong>Shield Overload</strong>, ztratíte 1 život a sektor je vyčištěn.</li>
                    <li><strong>Critical Entity (Boss):</strong> Při dosažení milníku skóre obdržíte varování. Masivní loď s vysokým HP. Její zničení posune hru do další fáze (Stage).</li>
                </ul>
            </div>

            <div class="manual-card">
                <h3>📊 7. HUD - Telemetrie</h3>
                <p>V horní liště neustále sledujte:</p>
                <ul>
                    <li><strong>SCORE:</strong> Vaše bojová efektivita.</li>
                    <li><strong>STAGE:</strong> Úroveň postupu vesmírem.</li>
                    <li><strong>INTEGRITY:</strong> Zbývající počet životů.</li>
                    <li><strong>OP:</strong> Vaše operační jméno v systému.</li>
                </ul>
            </div>
        </section>

        <!-- DOKUMENTACE A TECHNICKÉ PODKLADY -->
        <section id="resources" class="manual-section">
            <h2>📁 Dokumentace a technické podklady</h2>
            <p>Kompletní technická dokumentace a materiály pro další rozvoj projektu.</p>
            
            <div class="manual-grid">
                <!-- Technická Specifikace -->
                <div class="manual-card">
                    <div class="card-icon">📄</div>
                    <h3>Technická specifikace</h3>
                    <p>Podrobný popis architektury, datového schématu a API komunikace.</p>
                    <div style="display: flex; gap: 10px; margin-top: 20px;">
                        <a href="prezentace/dokumentace.html" class="btn" style="flex: 1; text-align: center; font-size: 0.9rem;">ZOBRAZIT</a>
                        <a href="prezentace/dokumentace.md" download class="btn" style="flex: 1; text-align: center; font-size: 0.9rem; background: rgba(255,255,255,0.1);">STÁHNOUT (.md)</a>
                    </div>
                </div>

                <!-- Vývojářská příručka -->
                <div class="manual-card">
                    <div class="card-icon">🤝</div>
                    <h3>Vývojářská příručka</h3>
                    <p>Technický manuál pro vývojáře a spolupracovníky – postupy a příklady.</p>
                    <div style="display: flex; gap: 10px; margin-top: 20px;">
                        <a href="prezentace/spolupracovnik.html" class="btn" style="flex: 1; text-align: center; font-size: 0.9rem;">ZOBRAZIT</a>
                        <a href="prezentace/spolupracovnik.md" download class="btn" style="flex: 1; text-align: center; font-size: 0.9rem; background: rgba(255,255,255,0.1);">STÁHNOUT (.md)</a>
                    </div>
                </div>

                <!-- Prezentace pro investory -->
                <div class="manual-card">
                    <div class="card-icon">📈</div>
                    <h3>Prezentace pro investory</h3>
                    <p>Obchodní analýza, tržní potenciál a dlouhodobá vize projektu.</p>
                    <div style="display: flex; gap: 10px; margin-top: 20px;">
                        <a href="prezentace/investor.html" class="btn" style="flex: 1; text-align: center; font-size: 0.9rem;">PITCH DECK</a>
                        <a href="prezentace/investor.html" download class="btn" style="flex: 1; text-align: center; font-size: 0.9rem; background: rgba(255,255,255,0.1);">STÁHNOUT (.html)</a>
                    </div>
                </div>
            </div>
        </section>
        
        <footer style="text-align: center; margin-top: 50px; opacity: 0.5;">
            <p>Space Invaders Enterprise © 2026 - Defensive Solutions Ltd.</p>
        </footer>
    </main>
</body>
</html>