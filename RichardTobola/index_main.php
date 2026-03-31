<?php
// 1. ZAPNUTÍ DIAGNOSTIKY
ini_set('display_errors', 1);
error_reporting(E_ALL);

session_start();

// --- KONFIGURACE DATABÁZE ---
$host = 'dbs.spskladno.cz';
$db   = 'vyuka10';
$user = 'student10'; 
$pass = 'spsnet';
$charset = 'utf8mb4';

try {
    $dsn = "mysql:host=$host;dbname=$db;charset=$charset";
    $pdo = new PDO($dsn, $user, $pass, [
        PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
        PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC
    ]);
} catch (\PDOException $e) {
    die("CHYBA PŘIPOJENÍ: " . $e->getMessage());
}

// =========================================================
// --- API PRO PYTHON HRU (Komunikace mezi hrou a webem) ---
// =========================================================
if (isset($_GET['api'])) {
    header('Content-Type: application/json');
    $input = json_decode(file_get_contents('php://input'), true);

    if ($_GET['api'] == 'login') {
        $u = $input['username'] ?? '';
        $p = $input['password'] ?? '';
        $stmt = $pdo->prepare("SELECT * FROM users WHERE username = ?");
        $stmt->execute([$u]);
        $user_data = $stmt->fetch();
        if ($user_data && password_verify($p, $user_data['password'])) {
            echo json_encode(['success' => true]);
        } else {
            echo json_encode(['success' => false]);
        }
        exit;
    }

    if ($_GET['api'] == 'savescore') {
        $u = $input['username'] ?? '';
        $p = $input['password'] ?? '';
        $score = (int)($input['score'] ?? 0);
        $diff = $input['difficulty'] ?? 'normal';

        $stmt = $pdo->prepare("SELECT * FROM users WHERE username = ?");
        $stmt->execute([$u]);
        $user_data = $stmt->fetch();

        if ($user_data && password_verify($p, $user_data['password'])) {
            if ($score > $user_data['score']) {
                $stmt = $pdo->prepare("UPDATE users SET score = ?, difficulty = ? WHERE id = ?");
                $stmt->execute([$score, $diff, $user_data['id']]);
            }
            echo json_encode(['success' => true]);
        } else {
            echo json_encode(['success' => false]);
        }
        exit;
    }
}
// =========================================================

$message = "";

// --- LOGIKA: REGISTRACE ---
if (isset($_POST['register'])) {
    $u = trim($_POST['new_user']);
    $p = password_hash($_POST['new_pass'], PASSWORD_DEFAULT);
    try {
        $stmt = $pdo->prepare("INSERT INTO users (username, password, score, difficulty) VALUES (?, ?, 0, '-')");
        $stmt->execute([$u, $p]);
        $message = "Registrace úspěšná! Nyní se přihlas.";
    } catch (Exception $e) { $message = "Chyba: Uživatel již existuje."; }
}

// --- LOGIKA: PŘIHLÁŠENÍ ---
if (isset($_POST['login'])) {
    $u = $_POST['user'];
    $p = $_POST['pass'];
    $stmt = $pdo->prepare("SELECT * FROM users WHERE username = ?");
    $stmt->execute([$u]);
    $user_data = $stmt->fetch();
    if ($user_data && password_verify($p, $user_data['password'])) {
        $_SESSION['user_id'] = $user_data['id'];
        $_SESSION['username'] = $user_data['username'];
        $message = "Vítej, " . htmlspecialchars($u) . "!";
    } else { $message = "Neplatné údaje."; }
}

if (isset($_GET['logout'])) { session_destroy(); header("Location: index_new_new.php"); exit; }

$leaderboard = $pdo->query("SELECT username, score, difficulty FROM users ORDER BY score DESC LIMIT 10")->fetchAll();
$theme = $_COOKIE['theme'] ?? 'dark';

// Zjistíme na jaké podstránce se uživatel nachází
$page = $_GET['page'] ?? 'main';
?>

<!DOCTYPE html>
<html lang="cs">
<head>
    <meta charset="UTF-8">
    <title>PONG ARCHIVE :: SYSTEM</title>
    <style>
        /* ÚPRAVA BAREV: --accent určuje barvu dříve tyrkysových nadpisů a zvýraznění */
        :root { --bg: #050505; --txt: #00ff41; --dim: #003b00; --in: #001100; --accent: #ffff00; } /* Změněno na žlutou */
        body.light-mode { --bg: #ffffff; --txt: #222222; --dim: #aaaaaa; --in: #f0f0f0; --accent: #cc0000; } /* Změněno na červenou */

        body { background: var(--bg); color: var(--txt); font-family: 'Courier New', monospace; display: flex; flex-direction: column; align-items: center; margin: 0; transition: 0.3s; padding-bottom: 50px;}
        .ascii-header { white-space: pre; padding: 20px; text-align: center; font-weight: bold; line-height: 1.2; color: var(--txt); }
        .ascii-header a { color: inherit; text-decoration: none; }
        
        nav { width: 100%; max-width: 900px; border-top: 1px solid var(--txt); border-bottom: 1px solid var(--txt); padding: 10px 0; display: flex; justify-content: center; flex-wrap: wrap; gap: 10px; margin-bottom: 20px; }
        
        .btn { background: transparent; color: var(--txt); border: 1px solid var(--txt); padding: 8px 16px; cursor: pointer; font-family: inherit; transition: 0.2s; text-decoration: none; display: inline-block; text-align: center;}
        .btn:hover { background: var(--txt); color: var(--bg); box-shadow: 0 0 10px var(--txt); }
        .btn.active { background: var(--txt); color: var(--bg); font-weight: bold; }

        .info-panel { width: 90%; max-width: 900px; border: 2px solid var(--txt); padding: 30px; position: relative; box-shadow: 5px 5px 0px var(--dim); margin-bottom: 30px; box-sizing: border-box; }
        .info-panel h2 { text-align: center; border-bottom: 1px double var(--txt); padding-bottom: 10px; margin-top: 0; color: var(--accent); }
        .terminal-prefix { color: var(--txt); font-weight: bold; margin-right: 10px; }

        /* KARTY PRO MANUÁL A PŘEHLEDY */
        .card-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-top: 20px; }
        .card { border: 1px solid var(--txt); background: rgba(0, 255, 65, 0.03); padding: 20px; position: relative; }
        .card h3 { margin-top: 0; border-bottom: 1px dashed var(--dim); padding-bottom: 10px; color: var(--accent); font-size: 1.1em; }
        .card ul { padding-left: 20px; margin-bottom: 0; }
        .card li { margin-bottom: 8px; }
        .card strong { color: var(--accent); }

        /* KÓDOVÉ BLOKY */
        pre { background: #111; border: 1px solid var(--dim); padding: 15px; overflow-x: auto; color: #ccc; font-family: 'Courier New', monospace; font-size: 0.85em; }
        body.light-mode pre { background: #eee; color: #333; }
        .code-comment { color: #888; font-style: italic; }
        .code-keyword { color: #f06; font-weight: bold; }
        .code-string { color: #0a0; }

        .score-table { width: 100%; border-collapse: collapse; margin-top: 20px; }
        .score-table th, .score-table td { border: 1px solid var(--txt); padding: 10px; text-align: left; }
        .score-table th { background: var(--dim); color: var(--bg); }

        .status-msg { color: yellow; margin: 10px; font-weight: bold; }

        .modal-overlay { display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.9); justify-content: center; align-items: center; z-index: 100; }
        .modal-box { background: var(--bg); border: 3px double var(--txt); padding: 25px; width: 320px; text-align: center; }
        .modal-box.wide { width: 600px; max-width: 90%; }
        .modal-tabs { display: flex; margin-bottom: 20px; gap: 5px; }
        .tab { flex: 1; padding: 5px; border: 1px solid var(--txt); cursor: pointer; font-size: 0.8em; }
        .tab.active { background: var(--txt); color: var(--bg); }
        input { width: 100%; background: var(--in); border: 1px solid var(--txt); color: var(--txt); padding: 8px; box-sizing: border-box; margin-top: 10px; font-family: inherit; }
    </style>
</head>
<body class="<?php echo ($theme === 'light') ? 'light-mode' : ''; ?>">

    <div class="ascii-header">
<a href="?page=main">
  _____   ___  _   _  ____ 
 |  __ \ / _ \| \ | |/ ___|
 | |__) | | | |  \| | |  _ 
 |  ___/| |_| | |\  | |_| |
 |_|     \___/|_| \_|\____|
    [ SYSTEM ARCHIVE v1.8 ]
</a>
    </div>

    <?php if($message): ?>
        <div class="status-msg">> <?php echo $message; ?></div>
    <?php endif; ?>

    <nav>
        <button class="btn" onclick="toggleTheme()">[ VZHLED ]</button>
        <button class="btn" onclick="openLeaderboard()">[ DATABÁZE ]</button>
        <a href="?page=investor" class="btn <?php echo $page=='investor'?'active':''; ?>">[ PREZENTACE PRO INVESTORA ]</a>
        <a href="?page=worker" class="btn <?php echo $page=='worker'?'active':''; ?>">[ PŘEHLED PRO PRACOVNÍKA ]</a>
        <?php if(isset($_SESSION['user_id'])): ?>
            <a href="?logout=1" class="btn">[ ODHLÁSIT: <?php echo htmlspecialchars($_SESSION['username']); ?> ]</a>
        <?php else: ?>
            <button class="btn" onclick="openAuth()">[ LOGIN / REGISTER ]</button>
        <?php endif; ?>
    </nav>

    <?php if ($page === 'main'): ?>
        
        <div class="info-panel">
            <h2>-- DATABÁZE: PROJEKT PONG --</h2>
            <p><span class="terminal-prefix">> IDENTIFIKACE:</span>Pong je považován za průkopníka videoherního průmyslu a první komerčně masově úspěšnou arkádovou hru. Pomohl etablovat společnost Atari jako giganta zábavního průmyslu a odstartoval takzvanou zlatou éru arkádových automatů. Přestože vycházel z dřívějšího konceptu elektronického stolního tenisu od Ralpha Baera, Pong jej dovedl k dokonalosti.</p>
            <p><span class="terminal-prefix">> ROK SPUŠTĚNÍ:</span>Listopad 1972 (Atari). Arkádová verze slavila okamžitý úspěch. Domácí verze (tzv. "Home Pong"), která se připojovala přímo k televizoru, následovala koncem roku 1975 a stala se absolutním hitem tehdejší vánoční sezóny.</p>
            <p><span class="terminal-prefix">> KONSTRUKTÉR:</span>Allan Alcorn. Zakladatel Atari, Nolan Bushnell, mu zadal vývoj Pongu pouze jako tréninkové cvičení. Alcorn neměl s videohrami žádné předchozí zkušenosti. Výsledek byl ale natolik zábavný a návykový, že se Bushnell rozhodl hru rovnou vydat a změnit tak herní historii.</p>
            <p><span class="terminal-prefix">> INCIDENT 01 (Případ plné pokladničky):</span>První testovací prototyp automatu byl umístěn do lokálního baru Andy Capp's Tavern v Sunnyvale v Kalifornii. Po pouhých dvou dnech volal majitel baru do Atari s tím, že automat přestal fungovat. Při inspekci Alcorn zjistil, že systém neselhal technicky – mechanismus na mince byl pouze doslova přeplněný čtvrťáky, což způsobilo zablokování celého stroje. Lidé do něj naházeli přes 40 dolarů za pár dní.</p>
            <p><span class="terminal-prefix">> DESIGN A HARDWARE:</span>Zajímavostí je, že původní Pong neobsahoval žádný kód, žádný mikroprocesor a žádnou systémovou paměť. Hra byla postavena čistě na úrovni hardwaru pomocí tzv. TTL obvodů (tranzistor-tranzistorová logika). Vizuálně postrádá jakékoli barvy a zvukové efekty – typické a ikonické "pípání" – nevznikly přes syntetizátor, ale generováním zvuků z frekvencí samotných synchronizačních obvodů monitoru.</p>
        </div>

        <div class="info-panel">
            <h2>-- HERNÍ MANUÁL --</h2>
            <p style="text-align:center; margin-bottom: 20px;">Technická specifikace ovládání a mechanik aktuálního buildu (v1.8).</p>
            
            <div class="card-grid">
                <div class="card">
                    <h3>> ZÁKLADNÍ OVLÁDÁNÍ</h3>
                    <ul>
                        <li><strong>Pohyb pálky:</strong> Použij klávesy <code>W / S</code> nebo <code>ŠIPKU NAHORU / DOLŮ</code> pro přesun po vertikální ose.</li>
                        <li><strong>Menu a Přihlášení:</strong> V rozhraní menu používej pro klikání myš. Během přihlašování se mezi poli přepínáš klávesou <code>TAB</code> a mažeš pomocí <code>BACKSPACE</code>.</li>
                        <li><strong>Ukončení (Nouzový únik):</strong> Klávesa <code>ESC</code>. Okamžitě ukončí probíhající hru, <strong>odešle aktuální skóre na server</strong> a vrátí tě do hlavního menu.</li>
                    </ul>
                </div>

                <div class="card">
                    <h3>> NASTAVENÍ (SETTINGS)</h3>
                    <ul>
                        <li><strong>Vizuální režim:</strong> Systém plně podporuje přepínání mezi Dark Mode a Light Mode pro optimalizaci zátěže očí.</li>
                        <li><strong>Obtížnost (Easy):</strong> Umělá inteligence je zpomalena na 50 % tvé rychlosti. Ideální pro nováčky.</li>
                        <li><strong>Obtížnost (Normal):</strong> Rychlost AI je nastavena na 85 %. Poskytuje vyrovnaný zážitek.</li>
                        <li><strong>Obtížnost (Hard):</strong> Umělá inteligence je o 20 % rychlejší než tvá loď. Vyžaduje absolutní soustředění.</li>
                    </ul>
                </div>

                <div class="card">
                    <h3>> HERNÍ MECHANIKY A CÍLE</h3>
                    <ul>
                        <li><strong>Zrychlování částic:</strong> S každým úspěšným odrazem se rychlost míčku plošně zvyšuje o 0.5 jednotek.</li>
                        <li><strong>Fyzika odrazu:</strong> Úhel odrazu se počítá dynamicky podle toho, jak daleko od středu tvé pálky byl míček zasažen. (Čím více ke kraji, tím ostřejší úhel).</li>
                        <li><strong>Cíl programu:</strong> Dostaň míček za záda AI oponenta. Hra končí v momentě, kdy jeden z hráčů dosáhne <strong>10 bodů</strong>. Systém následně automaticky zapíše výsledek do globální sítě (Databáze uživatelů).</li>
                    </ul>
                </div>
            </div>
        </div>

    <?php elseif ($page === 'investor'): ?>

        <div class="info-panel">
            <h2>-- PITCH DECK: PROJEKT PONG --</h2>
            <p style="text-align:center; font-style: italic;">Potenciál, monetizace a budoucnost retro gamingu s moderním backendem.</p>
            
            <div class="card-grid">
                <div class="card" style="grid-column: 1 / -1;">
                    <h3>> Vize Projektu</h3>
                    <p>Náš projekt "PONG ARCHIVE" neprodává jen hru, prodává <strong>nostalgii spojenou s moderní technologií</strong>. Podařilo se nám sjednotit estetiku úplně prvních herních automatů ze 70. let s robustní cloudovou infrastrukturou. Hra běží plynule v lokálním klientovi (Python/Pygame), ale veškerá data o uživatelích, zabezpečení a skóre se řeší na zabezpečeném webovém API.</p>
                </div>

                <div class="card">
                    <h3>> Konkurenční Výhody</h3>
                    <ul>
                        <li><strong>Hybridní ekosystém:</strong> Python herní klient + PHP/MySQL webový portál.</li>
                        <li><strong>Nativní AI adaptace:</strong> Oponent se přizpůsobuje chování hráče na základě 3 dynamických stupňů obtížnosti.</li>
                        <li><strong>Okamžitá distribuce:</strong> Nízké hardwarové nároky zaručují běh i na kancelářských zařízeních.</li>
                    </ul>
                </div>

                <div class="card">
                    <h3>> Očekávaný růst a KPI</h3>
                    <ul>
                        <li>Rozšíření o online P2P multiplayer.</li>
                        <li>Implementace in-game "skinů" pálek a částic za herní měnu (potenciální mikrotransakce).</li>
                        <li>Integrace mobilní aplikace připojené na stejnou databázi.</li>
                    </ul>
                </div>
            </div>
        </div>

    <?php elseif ($page === 'worker'): ?>

        <div class="info-panel">
            <h2>-- TECHNICKÁ DOKUMENTACE PRO VÝVOJÁŘE --</h2>
            <p style="text-align:center;">Struktura projektu a správa herní logiky (Zdrojový kód: <code>pong_main_new.py</code>)</p>

            <div class="card-grid">
                <div class="card" style="grid-column: 1 / -1; display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px;">
                    <div style="grid-column: 1 / -1;">
                        <h3>> 1. ARCHITEKTURA A STRUKTURA TŘÍD</h3>
                        <p>Kód je napsán objektově. Každý logický celek na obrazovce má svou vlastní třídu.</p>
                    </div>
                    <div>
                        <strong>Třída Game:</strong>
                        <p>Hlavní mozek ("Main Loop"). Udržuje herní stavy <code>MENU</code>, <code>PLAYING</code> a <code>GAME_OVER</code>. Řeší veškerou komunikaci přes knihovnu <code>requests</code> s webovým API.</p>
                    </div>
                    <div>
                        <strong>Třída Paddle:</strong>
                        <p>Kromě kreslení a kontroly mezí obrazovky obsahuje i funkci <code>ai_move()</code>, která řídí pohyb oponenta podle vybrané obtížnosti.</p>
                    </div>
                    <div>
                        <strong>Třídy Ball & Particle:</strong>
                        <p><code>Ball</code> řeší x/y vektory a reset do středu. <code>Particle</code> slouží jako jednoduchý vizuální emitor jisker po nárazu míčku do pálky.</p>
                    </div>
                </div>

                <div class="card" style="grid-column: 1 / -1;">
                    <h3>> 2. KLÍČOVÉ UKÁZKY KÓDU: Fyzika odrazu</h3>
                    <p>Aby hra nebyla monotónní, míček se odráží pod různým úhlem v závislosti na tom, zda trefil střed pálky, nebo její kraj. Úryvek metody <code>bounce_off_paddle()</code>:</p>
<pre>
<span class="code-keyword">def</span> bounce_off_paddle(self, paddle):
    <span class="code-comment"># Zjistíme rozdíl mezi středem pálky a středem míčku</span>
    intersect_y = paddle.rect.centery - self.ball.rect.centery
    normalized_intersect = intersect_y / (paddle.rect.height / 2)
    
    <span class="code-comment"># Výpočet úhlu (až 60 stupňů / pi/3 u kraje pálky)</span>
    bounce_angle = normalized_intersect * (math.pi / 3) 
    
    <span class="code-comment"># Zrychlení hry s každým odrazem</span>
    self.ball.speed += 0.5
    
    <span class="code-comment"># Aplikace nových vektorů</span>
    direction = 1 <span class="code-keyword">if</span> self.ball.dx < 0 <span class="code-keyword">else</span> -1
    self.ball.dx = math.cos(bounce_angle) * self.ball.speed * direction
    self.ball.dy = -math.sin(bounce_angle) * self.ball.speed
</pre>
                </div>

                <div class="card" style="grid-column: 1 / -1;">
                    <h3>> 3. KLÍČOVÉ UKÁZKY KÓDU: Komunikace se serverem</h3>
                    <p>Pro uložení skóre do PHP backendu volá herní klient asynchronně metodu <code>api_save_score()</code> přes HTTP POST.</p>
<pre>
<span class="code-keyword">def</span> api_save_score(self):
    <span class="code-keyword">if not</span> self.logged_in_user:
        <span class="code-keyword">return</span>
    
    <span class="code-keyword">try</span>:
        payload = {
            <span class="code-string">"username"</span>: self.logged_in_user,
            <span class="code-string">"password"</span>: self.logged_in_password,
            <span class="code-string">"score"</span>: self.player.score,
            <span class="code-string">"difficulty"</span>: self.difficulty
        }
        response = requests.post(<span class="code-string">f"{self.api_url}?api=savescore"</span>, json=payload)
        <span class="code-keyword">print</span>(<span class="code-string">"API: Skóre odesláno na server."</span>)
    <span class="code-keyword">except Exception as</span> e:
        <span class="code-keyword">print</span>(<span class="code-string">f"API Chyba při ukládání: {e}"</span>)
</pre>
                </div>

            </div>
        </div>

    <?php endif; ?>

    <div class="modal-overlay" id="leaderboardModal">
        <div class="modal-box wide">
            <button onclick="closeLeaderboard()" style="float:right; color:var(--txt); background:none; border:none; cursor:pointer; font-weight:bold;">[X]</button>
            <h2 style="margin-top: 0; border-bottom: 1px double var(--txt); padding-bottom: 10px; color: var(--accent);">-- DATABÁZE UŽIVATELŮ --</h2>
            <table class="score-table">
                <thead>
                    <tr><th>POŘADÍ</th><th>UŽIVATEL</th><th>SKÓRE</th><th>OBTÍŽNOST</th></tr>
                </thead>
                <tbody>
                    <?php
                    // Bezpečnostní kontrola pro prázdnou databázi
                    if (!empty($leaderboard)):
                        foreach($leaderboard as $i => $row): 
                    ?>
                    <tr>
                        <td>#<?php echo $i+1; ?></td>
                        <td><?php echo htmlspecialchars($row['username']); ?></td>
                        <td><?php echo $row['score']; ?></td>
                        <td><?php echo strtoupper(htmlspecialchars($row['difficulty'] ?? '-')); ?></td>
                    </tr>
                    <?php 
                        endforeach;
                    else:
                    ?>
                    <tr><td colspan="4" style="text-align: center;">Žádná data v databázi.</td></tr>
                    <?php endif; ?>
                </tbody>
            </table>
        </div>
    </div>

    <div class="modal-overlay" id="authModal">
        <div class="modal-box">
            <button onclick="closeAuth()" style="float:right; color:var(--txt); background:none; border:none; cursor:pointer; font-weight:bold;">[X]</button>
            <div style="clear:both; height:10px;"></div>
            <div class="modal-tabs">
                <div class="tab active" id="tab-l" onclick="switchTab('l')">LOGIN</div>
                <div class="tab" id="tab-r" onclick="switchTab('r')">REGISTER</div>
            </div>

            <form id="f-login" method="POST">
                <input type="text" name="user" placeholder="UŽIVATEL" required>
                <input type="password" name="pass" placeholder="HESLO" required>
                <button type="submit" name="login" class="btn" style="width:100%; margin-top:15px;">VSTOUPIT</button>
            </form>

            <form id="f-reg" method="POST" style="display:none">
                <input type="text" name="new_user" placeholder="NOVÉ JMÉNO" required>
                <input type="password" name="new_pass" placeholder="NOVÉ HESLO" required>
                <button type="submit" name="register" class="btn" style="width:100%; margin-top:15px;">VYTVOŘIT ÚČET</button>
            </form>
        </div>
    </div>

    <script>
        function toggleTheme() {
            const isLight = document.body.classList.toggle('light-mode');
            document.cookie = "theme=" + (isLight ? 'light' : 'dark') + "; path=/; max-age=31536000";
        }
        
        const authModal = document.getElementById('authModal');
        const lbModal = document.getElementById('leaderboardModal');
        
        function openAuth() { authModal.style.display = 'flex'; }
        function closeAuth() { authModal.style.display = 'none'; }
        
        function openLeaderboard() { lbModal.style.display = 'flex'; }
        function closeLeaderboard() { lbModal.style.display = 'none'; }

        function switchTab(t) {
            document.getElementById('f-login').style.display = t === 'l' ? 'block' : 'none';
            document.getElementById('f-reg').style.display = t === 'r' ? 'block' : 'none';
            document.getElementById('tab-l').classList.toggle('active', t === 'l');
            document.getElementById('tab-r').classList.toggle('active', t === 'r');
        }
        
        window.onclick = (e) => { 
            if(e.target == authModal) closeAuth(); 
            if(e.target == lbModal) closeLeaderboard(); 
        }
    </script>
</body>
</html>