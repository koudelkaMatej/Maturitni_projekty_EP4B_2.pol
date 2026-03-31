# Automatizované testy – Flappy Palach

Projekt obsahuje 2 automatizované testy pro ověření klíčových funkcí:
1. Test herní logiky (Python)
2. Test databázových operací (PHP + MySQL)

---

## Přehled testů

| Číslo | Název | Co testuje | Technologie | Soubor |
|-------|-------|-----------|-------------|--------|
| 1 | Kolizní detekce | Herní logiku (kolize s trubkami) | Python unittest | test_game.py |
| 2 | Databázové operace | INSERT, best-score logiku, FK constraints | PHP + MySQL | test_database.php |

---

## TEST 1: Kolizní detekce (test_game.py)

### Popis funkce

Test ověřuje funkci `check_collision()` která detekuje kolize ptáčka:
- Náraz do horní trubky
- Náraz do spodní trubky
- Vyletění mimo obrazovku nahoře
- Spadnutí mimo obrazovku dole
- Bezpečný průlet mezi trubkami

### Testovací scénáře

Test obsahuje 5 konkrétních případů:

```python
def test_no_collision_between_pipes(self):
    # Ptáček uprostřed mezery - kolize NEMÁ nastat
    bird_rect = pygame.Rect(150, 400, 50, 50)
    result = check_collision(bird_rect, 300, 200, 180)
    self.assertFalse(result)

def test_collision_with_top_pipe(self):
    # Ptáček v horní trubce - kolize MÁ nastat
    bird_rect = pygame.Rect(320, 100, 50, 50)
    result = check_collision(bird_rect, 300, 200, 180)
    self.assertTrue(result)
```

### Jak test spustit

KROK 1: Otevři terminál (Command Prompt nebo PowerShell na Windows)

KROK 2: Přejdi do složky s projektem:
```bash
cd C:\Users\TvojeJmeno\Desktop\flappy_palach
```

KROK 3: Spusť test:
```bash
python test_game.py
```

### Očekávaný výstup

Pokud vše funguje správně, uvidíš:
```
======================================================================
FLAPPY PALACH - TEST KOLIZNÍ DETEKCE
======================================================================
test_collision_out_of_bounds_bottom ... ok
test_collision_out_of_bounds_top ... ok
test_collision_with_bottom_pipe ... ok
test_collision_with_top_pipe ... ok
test_no_collision_between_pipes ... ok

----------------------------------------------------------------------
Ran 5 tests in 0.003s

OK
```

Pokud některý test selže, uvidíš:
```
FAIL: test_collision_with_top_pipe
AssertionError: False is not true
```

### Co znamenají výsledky

| Výsledek | Význam |
|----------|--------|
| ok | Test prošel - funkce funguje správně |
| FAIL | Test selhal - je chyba v kódu |
| ERROR | Test nemohl proběhnout - chyba v samotném testu |

---

## TEST 2: Databázové operace (test_database.php)

### Popis funkce

Test se připojí ke skutečné MySQL databázi a ověří:
1. Vložení nového skóre (INSERT)
2. Best-score logiku (ukládání jen nejlepšího výsledku)
3. Více obtížností pro jednoho uživatele
4. Foreign key CASCADE DELETE (smazání uživatele smaže i jeho skóre)

### Příprava před spuštěním

DŮLEŽITÉ: Test pracuje se skutečnou databází. Před spuštěním musíš:

KROK 1: Zapnout XAMPP
- Spusť XAMPP Control Panel
- Klikni na "Start" u Apache
- Klikni na "Start" u MySQL
- Počkej až se obě služby rozběhnou (zelená)

KROK 2: Ověřit že databáze existuje
- Otevři prohlížeč
- Jdi na http://localhost/phpmyadmin
- V levém sloupci najdi databázi "flappy_palach"
- Měly by tam být tabulky "users" a "scores"

KROK 3: (Pokud databáze neexistuje)
- V phpMyAdmin klikni na "SQL" nahoře
- Zkopíruj obsah souboru database.sql
- Vlož ho do pole a klikni "Provést"

### Jak test spustit

KROK 1: Otevři terminál

KROK 2: Přejdi do složky s projektem:
```bash
cd C:\xampp\htdocs\flappy_palach
```

KROK 3: Spusť test:
```bash
php test_database.php
```

### Očekávaný výstup

Pokud vše funguje správně:
```
======================================================================
FLAPPY PALACH - TEST DATABÁZE
======================================================================

Připojování k databázi...
  ✓ PASS: Připojení k databázi úspěšné

Příprava testovacích dat...
  ✓ PASS: Testovací uživatel vytvořen (ID: 15)

TEST 1: Vložení prvního skóre
  ✓ PASS: První skóre (50 bodů) bylo úspěšně vloženo
  ✓ PASS: Ověření: Skóre v databázi je správně 50

TEST 2: Best-score logika
  ✓ PASS: Lepší skóre (100) úspěšně nahradilo horší (50)

TEST 3: Více obtížností
  ✓ PASS: Uživatel má správně 3 záznamy
  ✓ PASS: Všechna skóre jsou správně uložena

TEST 4: Foreign key constraint
  ✓ PASS: Po smazání uživatele byla smazána i jeho skóre

Úklid testovacích dat...
  ✓ PASS: Testovací data vyčištěna

======================================================================
VÝSLEDKY TESTŮ
======================================================================
Úspěšné: 16
Neúspěšné: 0
======================================================================
VŠECHNY TESTY PROŠLY!
======================================================================
```

### Možné chyby a řešení

**Chyba: "Connection refused"**
```
Řešení: MySQL v XAMPP neběží
Akce: Spusť XAMPP a klikni Start u MySQL
```

**Chyba: "Access denied for user 'root'"**
```
Řešení: Špatné přihlašovací údaje
Akce: Otevři test_database.php a zkontroluj řádky:
       define('DB_USER', 'root');
       define('DB_PASS', '');
```

**Chyba: "Unknown database 'flappy_palach'"**
```
Řešení: Databáze neexistuje
Akce: V phpMyAdmin vytvoř databázi "flappy_palach"
      a naimportuj database.sql
```

**Chyba: "Table 'users' doesn't exist"**
```
Řešení: Tabulky nejsou vytvořené
Akce: V phpMyAdmin otevři databázi "flappy_palach"
      a spusť SQL příkazy z database.sql
```

---

## Podrobný popis testů

### TEST 1 - Detaily

**Testovací metoda: unittest.TestCase**

Každý test má tři části:
1. `setUp()` - příprava (spustí se před každým testem)
2. `test_XXX()` - samotný test
3. Assertion - ověření výsledku

Příklad jednoho testu:
```python
def test_no_collision_between_pipes(self):
    # 1. Vytvoř ptáčka uprostřed mezery
    bird_rect = pygame.Rect(150, 400, 50, 50)
    
    # 2. Zavolej testovanou funkci
    result = check_collision(bird_rect, 300, 200, 180)
    
    # 3. Ověř že kolize NENASTALA
    self.assertFalse(result, "Ptáček mezi trubkami by neměl mít kolizi")
```

**Assertion metody:**
- `assertTrue(x)` - ověří že x je True
- `assertFalse(x)` - ověří že x je False
- `assertEqual(a, b)` - ověří že a je rovno b

### TEST 2 - Detaily

**Testovací logika:**

```
KROK 1: Připojení
- Otevře spojení s MySQL
- Nastaví UTF-8 kódování

KROK 2: Příprava (setUp)
- Smaže všechny TEST_ záznamy z předchozího běhu
- Vytvoří nového testovacího uživatele
- Uloží jeho ID pro další testy

KROK 3: Testy
- Test 1: Vloží první skóre, ověří že je v DB
- Test 2: Vloží lepší skóre, ověří že přepsalo horší
- Test 3: Vloží skóre na 3 obtížnosti, ověří že jsou všechny
- Test 4: Smaže uživatele, ověří že zmizela i jeho skóre

KROK 4: Úklid (tearDown)
- Smaže všechny TEST_ záznamy
- Vrátí databázi do původního stavu

KROK 5: Odpojení
- Zavře spojení s databází
```

**Best-score logika:**

```php
// Zjisti současné nejlepší skóre
$current = SELECT score FROM scores WHERE user_id = X AND difficulty = 'stredni';

// Pokud nové skóre > staré skóre
if ($new_score > $current['score']) {
    // Smaž starý záznam
    DELETE FROM scores WHERE user_id = X AND difficulty = 'stredni';
    
    // Vlož nový záznam
    INSERT INTO scores VALUES (X, 'username', $new_score, 'stredni', NOW());
}
```

---

## Jak prezentovat testy

### Možnost 1: Spustit testy naživo

1. Otevři terminál
2. Spusť `python test_game.py`
3. Ukaž že všech 5 testů prošlo (OK)
4. (Pokud běží XAMPP) Spusť `php test_database.php`
5. Ukaž že všech 16 testů prošlo

### Možnost 2: Vysvětlit jeden konkrétní test

Otevři test_game.py v editoru a vysvětli:

"Tento test ověřuje kolizní detekci. Mám tady funkci `check_collision()` 
která vrací True pokud ptáček narazil, nebo False pokud ne. 

Test vytvoří ptáčka na pozici (150, 400) což je uprostřed mezery mezi 
trubkami. Pak zavolá funkci a ověří že vrátila False, protože kolize 
nenastala. 

Pokud bych změnil pozici na (320, 100), ptáček by byl v horní trubce, 
takže test by ověřil že funkce vrátila True."

### Možnost 3: Ukázat jak test odhalí chybu

1. Otevři flappy_palach_commented.py
2. Najdi funkci `check_collision()`
3. Změň `return True` na `return False` (záměrná chyba)
4. Spusť `python test_game.py`
5. Ukaž že 4 testy selhaly - test odhalil chybu
6. Vrať změnu zpět
7. Spusť test znovu - vše projde

### Možnost 4: Ukázat databázový test

Spusť `php test_database.php` a vysvětli:

"Tento test se připojí ke skutečné MySQL databázi. Nejdřív vytvoří 
testovacího uživatele a vloží mu skóre 50 bodů. Pak simuluje že 
dosáhl lepšího skóre 100 bodů - test ověří že se starý záznam 
smazal a uložil se nový.

Také ověřuje že když uživatel hraje na různých obtížnostech, 
může mít více záznamů - jeden na lehkou, jeden na střední, jeden 
na těžkou.

Na konci test smaže uživatele a ověří že díky foreign key CASCADE 
se automaticky smazala i všechna jeho skóre. To je důležité pro 
integritu databáze."

---

## Co testy ověřují

### Test 1 (test_game.py)

| Funkce | Co test kontroluje |
|--------|-------------------|
| Kolize s horní trubkou | Funkce vrátí True když ptáček narazí shora |
| Kolize se spodní trubkou | Funkce vrátí True když ptáček narazí zdola |
| Bezpečný průlet | Funkce vrátí False když je ptáček mezi trubkami |
| Mimo obrazovku nahoře | Funkce vrátí True když bird_rect.top < 0 |
| Mimo obrazovku dole | Funkce vrátí True když bird_rect.bottom > HEIGHT |

### Test 2 (test_database.php)

| Funkce | Co test kontroluje |
|--------|-------------------|
| INSERT operace | Data se skutečně zapíší do databáze |
| Best-score DELETE+INSERT | Lepší skóre přepíše horší, horší se neuloží |
| Více obtížností | Jeden uživatel může mít 3 záznamy (lehka/stredni/tezka) |
| CASCADE DELETE | Smazání uživatele automaticky smaže jeho skóre |
| Prepared statements | SQL injection prevence funguje |
| Data integrity | Foreign key constraints jsou správně nastavené |

---

## Technické detaily

### Python unittest framework

Unittest je standardní testovací knihovna v Pythonu. Základní struktura:

```python
import unittest

class MojTest(unittest.TestCase):
    def setUp(self):
        # Příprava před každým testem
        pass
    
    def test_neco(self):
        # Samotný test
        vysledek = moje_funkce(vstup)
        self.assertEqual(vysledek, ocekavany_vysledek)
    
    def tearDown(self):
        # Úklid po každém testu
        pass

if __name__ == '__main__':
    unittest.main()
```

### PHP mysqli připojení

Test používá MySQLi extension pro připojení k databázi:

```php
$db = new mysqli('localhost', 'root', '', 'flappy_palach');

if ($db->connect_error) {
    die("Připojení selhalo");
}

// Prepared statement (prevence SQL injection)
$stmt = $db->prepare("SELECT * FROM users WHERE id = ?");
$stmt->bind_param("i", $user_id);
$stmt->execute();
$result = $stmt->get_result();
```

### Foreign key CASCADE

Constraint definovaný v database.sql:

```sql
ALTER TABLE scores
ADD CONSTRAINT fk_user
FOREIGN KEY (user_id) 
REFERENCES users(id)
ON DELETE CASCADE;
```

Znamená: Když smažeš záznam z tabulky `users`, automaticky se 
smažou i všechny záznamy z tabulky `scores` které na něj odkazují.

---

## Souhrn

Projekt obsahuje 2 funkční automatizované testy:

1. **test_game.py** - testuje kolizní detekci (Python unittest)
   - 5 testovacích případů
   - Spuštění: `python test_game.py`
   - Trvání: cca 0.003 sekundy

2. **test_database.php** - testuje databázové operace (PHP + MySQL)
   - 4 testy se 16 kontrolami
   - Spuštění: `php test_database.php`
   - Trvání: cca 0.5 sekundy
   - Vyžaduje: běžící XAMPP MySQL

Oba testy automaticky kontrolují že klíčové funkce projektu 
fungují správně. Pokud se v budoucnu něco rozbije, testy to okamžitě odhalí.

