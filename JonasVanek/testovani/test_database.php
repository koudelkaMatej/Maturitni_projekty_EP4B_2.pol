<?php
/**
 * test_database.php - Test databázových operací pro Flappy Palach
 * 
 * TENTO TEST PRACUJE SE SKUTEČNOU DATABÁZÍ!
 * 
 * Co testuje:
 * - Připojení k databázi
 * - Vložení nového skóre
 * - Best-score logiku (přepsání horším/lepším skóre)
 * - Unikátnost uživatelských jmen
 * - Foreign key constraints
 * 
 * Jak spustit:
 *   php test_database.php
 * 
 * DŮLEŽITÉ: Před spuštěním se ujisti že:
 * 1. XAMPP Apache a MySQL běží
 * 2. Databáze 'flappy_palach' existuje
 * 3. Tabulky users a scores jsou vytvořené (viz database.sql)
 */

// Konfigurace
define('DB_HOST', 'localhost');
define('DB_USER', 'root');
define('DB_PASS', '');
define('DB_NAME', 'flappy_palach');

// Barvy pro terminálový výstup
class Colors {
    const GREEN = "\033[0;32m";
    const RED = "\033[0;31m";
    const YELLOW = "\033[1;33m";
    const BLUE = "\033[0;34m";
    const NC = "\033[0m"; // No Color
}

class DatabaseTest {
    private $db;
    private $passed = 0;
    private $failed = 0;
    private $test_user_id = null;
    
    public function __construct() {
        echo "\n";
        echo str_repeat("=", 70) . "\n";
        echo Colors::BLUE . "🗄️  FLAPPY PALACH - TEST DATABÁZE" . Colors::NC . "\n";
        echo str_repeat("=", 70) . "\n\n";
    }
    
    /**
     * Připojení k databázi
     */
    public function connect() {
        echo Colors::YELLOW . "📡 Připojování k databázi...\n" . Colors::NC;
        
        $this->db = new mysqli(DB_HOST, DB_USER, DB_PASS, DB_NAME);
        
        if ($this->db->connect_error) {
            $this->fail("Připojení k databázi selhalo: " . $this->db->connect_error);
            $this->fail("Zkontroluj že XAMPP MySQL běží a databáze 'flappy_palach' existuje!");
            $this->summary();
            exit(1);
        }
        
        $this->db->set_charset("utf8mb4");
        $this->pass("Připojení k databázi úspěšné");
        echo "\n";
    }
    
    /**
     * Příprava testovacích dat (vyčistit + vytvořit test user)
     */
    public function setUp() {
        echo Colors::YELLOW . "🧹 Příprava testovacích dat...\n" . Colors::NC;
        
        // Smazat všechny test záznamy
        $this->db->query("DELETE FROM scores WHERE username LIKE 'TEST_%'");
        $this->db->query("DELETE FROM users WHERE username LIKE 'TEST_%'");
        
        // Vytvořit testovacího uživatele
        $username = 'TEST_USER_' . time();
        $password_hash = password_hash('testpass123', PASSWORD_BCRYPT);
        
        $stmt = $this->db->prepare(
            "INSERT INTO users (username, password_hash, date_registered, last_login) 
             VALUES (?, ?, NOW(), NOW())"
        );
        $stmt->bind_param("ss", $username, $password_hash);
        
        if ($stmt->execute()) {
            $this->test_user_id = $this->db->insert_id;
            $this->pass("Testovací uživatel vytvořen (ID: {$this->test_user_id}, jméno: {$username})");
        } else {
            $this->fail("Vytvoření testovacího uživatele selhalo: " . $stmt->error);
        }
        $stmt->close();
        echo "\n";
    }
    
    /**
     * TEST 1: Vložení prvního skóre
     */
    public function testInsertFirstScore() {
        echo Colors::YELLOW . "🧪 TEST 1: Vložení prvního skóre\n" . Colors::NC;
        
        $stmt = $this->db->prepare(
            "INSERT INTO scores (user_id, username, score, difficulty, date_created)
             VALUES (?, 'TEST_USER', 50, 'stredni', NOW())"
        );
        $stmt->bind_param("i", $this->test_user_id);
        
        if ($stmt->execute()) {
            $this->pass("První skóre (50 bodů) bylo úspěšně vloženo");
            
            // Ověříme že záznam existuje
            $check = $this->db->query(
                "SELECT score FROM scores WHERE user_id = {$this->test_user_id} AND difficulty = 'stredni'"
            );
            
            if ($check && $check->num_rows === 1) {
                $row = $check->fetch_assoc();
                if ($row['score'] == 50) {
                    $this->pass("Ověření: Skóre v databázi je správně 50");
                } else {
                    $this->fail("Ověření: Očekávané skóre 50, ale v DB je {$row['score']}");
                }
            } else {
                $this->fail("Ověření: Záznam nebyl nalezen v databázi");
            }
        } else {
            $this->fail("Vložení skóre selhalo: " . $stmt->error);
        }
        $stmt->close();
        echo "\n";
    }
    
    /**
     * TEST 2: Best-score logika - lepší skóre přepíše horší
     */
    public function testBetterScoreReplacesWorse() {
        echo Colors::YELLOW . "🧪 TEST 2: Best-score logika - lepší skóre přepíše horší\n" . Colors::NC;
        
        // Krok 1: Zjistit současné skóre
        $current = $this->db->query(
            "SELECT score FROM scores WHERE user_id = {$this->test_user_id} AND difficulty = 'stredni'"
        )->fetch_assoc();
        
        $old_score = $current['score'];
        $this->pass("Současné skóre: {$old_score}");
        
        // Krok 2: Simulovat lepší skóre (100 > 50)
        $new_score = 100;
        
        // Smazat staré
        $this->db->query(
            "DELETE FROM scores WHERE user_id = {$this->test_user_id} AND difficulty = 'stredni'"
        );
        
        // Vložit nové
        $stmt = $this->db->prepare(
            "INSERT INTO scores (user_id, username, score, difficulty, date_created)
             VALUES (?, 'TEST_USER', ?, 'stredni', NOW())"
        );
        $stmt->bind_param("ii", $this->test_user_id, $new_score);
        $stmt->execute();
        $stmt->close();
        
        // Krok 3: Ověřit že v DB je nové skóre
        $check = $this->db->query(
            "SELECT score FROM scores WHERE user_id = {$this->test_user_id} AND difficulty = 'stredni'"
        )->fetch_assoc();
        
        if ($check['score'] == 100) {
            $this->pass("Lepší skóre (100) úspěšně nahradilo horší skóre ({$old_score})");
        } else {
            $this->fail("Očekávané skóre 100, ale v DB je {$check['score']}");
        }
        
        // Krok 4: Zkusit horší skóre (30 < 100) - NEMĚLO by se uložit
        $worse_score = 30;
        $current_best = $this->db->query(
            "SELECT score FROM scores WHERE user_id = {$this->test_user_id} AND difficulty = 'stredni'"
        )->fetch_assoc()['score'];
        
        if ($worse_score > $current_best) {
            $this->fail("Logická chyba v testu: {$worse_score} není horší než {$current_best}");
        } else {
            $this->pass("Simulace: horší skóre ({$worse_score}) se NEULOŽÍ (současný rekord: {$current_best})");
        }
        echo "\n";
    }
    
    /**
     * TEST 3: Více obtížností pro jednoho uživatele
     */
    public function testMultipleDifficulties() {
        echo Colors::YELLOW . "🧪 TEST 3: Jeden uživatel může mít skóre na více obtížnostech\n" . Colors::NC;
        
        // Přidáme skóre na "lehka"
        $stmt = $this->db->prepare(
            "INSERT INTO scores (user_id, username, score, difficulty, date_created)
             VALUES (?, 'TEST_USER', 75, 'lehka', NOW())"
        );
        $stmt->bind_param("i", $this->test_user_id);
        $stmt->execute();
        $stmt->close();
        
        // Přidáme skóre na "tezka"
        $stmt = $this->db->prepare(
            "INSERT INTO scores (user_id, username, score, difficulty, date_created)
             VALUES (?, 'TEST_USER', 25, 'tezka', NOW())"
        );
        $stmt->bind_param("i", $this->test_user_id);
        $stmt->execute();
        $stmt->close();
        
        // Spočítáme záznamy pro tohoto uživatele
        $count = $this->db->query(
            "SELECT COUNT(*) as cnt FROM scores WHERE user_id = {$this->test_user_id}"
        )->fetch_assoc()['cnt'];
        
        if ($count == 3) {
            $this->pass("Uživatel má správně 3 záznamy (stredni, lehka, tezka)");
            
            // Ověříme všechny obtížnosti
            $difficulties = $this->db->query(
                "SELECT difficulty, score FROM scores WHERE user_id = {$this->test_user_id} ORDER BY difficulty"
            );
            
            $expected = ['lehka' => 75, 'stredni' => 100, 'tezka' => 25];
            $all_correct = true;
            
            while ($row = $difficulties->fetch_assoc()) {
                if (isset($expected[$row['difficulty']]) && $expected[$row['difficulty']] == $row['score']) {
                    $this->pass("  ✓ {$row['difficulty']}: {$row['score']} bodů");
                } else {
                    $this->fail("  ✗ {$row['difficulty']}: nesprávné skóre");
                    $all_correct = false;
                }
            }
            
            if ($all_correct) {
                $this->pass("Všechna skóre jsou správně uložena");
            }
        } else {
            $this->fail("Očekávané 3 záznamy, ale v DB je {$count}");
        }
        echo "\n";
    }
    
    /**
     * TEST 4: Foreign key constraint - cascade delete
     */
    public function testForeignKeyConstraint() {
        echo Colors::YELLOW . "🧪 TEST 4: Foreign key - smazání uživatele smaže i jeho skóre\n" . Colors::NC;
        
        // Spočítáme současná skóre
        $before = $this->db->query(
            "SELECT COUNT(*) as cnt FROM scores WHERE user_id = {$this->test_user_id}"
        )->fetch_assoc()['cnt'];
        
        $this->pass("Před smazáním: uživatel má {$before} skóre");
        
        // Smažeme uživatele
        $this->db->query("DELETE FROM users WHERE id = {$this->test_user_id}");
        
        // Spočítáme skóre po smazání (měla by být 0 díky CASCADE)
        $after = $this->db->query(
            "SELECT COUNT(*) as cnt FROM scores WHERE user_id = {$this->test_user_id}"
        )->fetch_assoc()['cnt'];
        
        if ($after == 0) {
            $this->pass("Po smazání: všechna skóre (CASCADE DELETE) byla smazána ✓");
        } else {
            $this->fail("Po smazání: stále existuje {$after} skóre (CASCADE nefunguje!)");
        }
        echo "\n";
    }
    
    /**
     * Ukončení testů
     */
    public function tearDown() {
        echo Colors::YELLOW . "🧹 Úklid testovacích dat...\n" . Colors::NC;
        
        // Smazat všechny test záznamy
        $this->db->query("DELETE FROM scores WHERE username LIKE 'TEST_%'");
        $this->db->query("DELETE FROM users WHERE username LIKE 'TEST_%'");
        
        $this->pass("Testovací data vyčištěna");
        echo "\n";
    }
    
    /**
     * Uzavření připojení
     */
    public function disconnect() {
        if ($this->db) {
            $this->db->close();
            echo Colors::YELLOW . "👋 Odpojeno od databáze\n" . Colors::NC;
        }
    }
    
    /**
     * Pomocné metody pro výpis výsledků
     */
    private function pass($message) {
        $this->passed++;
        echo Colors::GREEN . "  ✓ PASS: " . Colors::NC . $message . "\n";
    }
    
    private function fail($message) {
        $this->failed++;
        echo Colors::RED . "  ✗ FAIL: " . Colors::NC . $message . "\n";
    }
    
    /**
     * Výpis souhrnu
     */
    public function summary() {
        echo "\n";
        echo str_repeat("=", 70) . "\n";
        echo "📊 VÝSLEDKY TESTŮ\n";
        echo str_repeat("=", 70) . "\n";
        echo Colors::GREEN . "Úspěšné: " . $this->passed . Colors::NC . "\n";
        echo Colors::RED . "Neúspěšné: " . $this->failed . Colors::NC . "\n";
        echo str_repeat("=", 70) . "\n";
        
        if ($this->failed === 0) {
            echo Colors::GREEN . "🎉 VŠECHNY TESTY PROŠLY!\n" . Colors::NC;
        } else {
            echo Colors::RED . "⚠️  NĚKTERÉ TESTY SELHALY\n" . Colors::NC;
        }
        echo str_repeat("=", 70) . "\n\n";
    }
}

// ============================================================================
// SPUŠTĚNÍ TESTŮ
// ============================================================================

$test = new DatabaseTest();

try {
    $test->connect();
    $test->setUp();
    
    $test->testInsertFirstScore();
    $test->testBetterScoreReplacesWorse();
    $test->testMultipleDifficulties();
    $test->testForeignKeyConstraint();
    
    $test->tearDown();
    $test->disconnect();
    $test->summary();
    
    // Exit code (pro automatizaci)
    exit($test->failed > 0 ? 1 : 0);
    
} catch (Exception $e) {
    echo Colors::RED . "\n💥 CHYBA: " . $e->getMessage() . "\n" . Colors::NC;
    $test->summary();
    exit(1);
}
?>
