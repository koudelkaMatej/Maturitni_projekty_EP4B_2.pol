# Flappy Palach - Webový žebříček

Tento projekt obsahuje kompletní webové rozhraní pro zobrazení žebříčku nejlepších hráčů Flappy Palach.

## 📁 Struktura souborů

```
flappy_palach_web/
│
├── config.php              # Konfigurace databáze
├── submit_score.php        # API endpoint pro odesílání skóre z hry
├── get_scores.php          # API endpoint pro získání žebříčku
├── index.html              # Hlavní HTML stránka
├── style.css               # CSS styly
├── script.js               # JavaScript pro načítání dat
├── database.sql            # SQL skript pro vytvoření databáze
└── README.md               # Tento soubor
```

## 🚀 Instalace a nastavení

### Krok 1: Nainstalujte XAMPP (nebo jiný web server)

1. Stáhněte XAMPP z [https://www.apachefriends.org](https://www.apachefriends.org)
2. Nainstalujte ho (defaultní nastavení je OK)
3. Spusťte XAMPP Control Panel
4. Zapněte **Apache** a **MySQL**

### Krok 2: Umístěte soubory

1. Najděte složku `htdocs` ve vašem XAMPP (obvykle `C:\xampp\htdocs\`)
2. Vytvořte novou složku: `C:\xampp\htdocs\flappy_palach\`
3. Zkopírujte všechny soubory (.php, .html, .css, .js) do této složky

### Krok 3: Vytvořte databázi

#### Možnost A: Přes phpMyAdmin (doporučeno pro začátečníky)

1. Otevřete prohlížeč a jděte na: `http://localhost/phpmyadmin`
2. Klikněte na záložku **SQL** nahoře
3. Otevřete soubor `database.sql` v textovém editoru
4. Zkopírujte celý obsah a vložte ho do SQL pole v phpMyAdmin
5. Klikněte na **Provést** (Go)
6. Databáze a tabulka jsou vytvořeny! ✅

#### Možnost B: Přes příkazovou řádku (pro pokročilé)

```bash
cd C:\xampp\mysql\bin
mysql -u root -p
```

Po zadání hesla (defaultně prázdné - jen Enter):

```sql
source C:/xampp/htdocs/flappy_palach/database.sql
```

### Krok 4: Ověřte konfiguraci

Otevřte soubor `config.php` a zkontrolujte nastavení:

```php
define('DB_HOST', 'localhost');      // OK
define('DB_USER', 'root');           // OK pro XAMPP
define('DB_PASS', '');               // Prázdné pro XAMPP
define('DB_NAME', 'flappy_palach');  // OK
```

### Krok 5: Otestujte web

1. Otevřete prohlížeč
2. Jděte na: `http://localhost/flappy_palach/`
3. Měli byste vidět žebříček s testovacími daty! 🎉

### Krok 6: Propojte s Python hrou

V souboru `flappy_palach_commented.py` změňte na začátku:

```python
SCORE_SERVER_URL = "http://localhost/flappy_palach/submit_score.php"
SCORE_API_KEY = None
SCORE_USERNAME = None
SCORE_PASSWORD = None
```

## 🎮 Použití

### Odesílání skóre z hry

Když hráč zemře v Pythonové hře, skóre se automaticky odešle na server pomocí `submit_score.php`.

### Zobrazení žebříčku

Otevřete `http://localhost/flappy_palach/` v prohlížeči pro zobrazení žebříčku.

Funkce:
- 🔍 **Vyhledávání** - Hledejte konkrétního hráče
- 📅 **Filtry** - Zobrazit všechny / dnes / tento týden
- 📄 **Stránkování** - Procházení více záznamů
- 🔄 **Obnovit** - Aktualizace dat
- 📊 **Statistiky** - Celkem hráčů, nejvyšší skóre, počet her

## 🔧 Řešení problémů

### Chyba: "Cannot connect to database"

1. Zkontrolujte, že MySQL běží v XAMPP Control Panel
2. Ověřte nastavení v `config.php`
3. Zkontrolujte, že databáze `flappy_palach` existuje v phpMyAdmin

### Chyba: "404 Not Found"

1. Ujistěte se, že soubory jsou v `C:\xampp\htdocs\flappy_palach\`
2. Zkontrolujte, že Apache běží v XAMPP Control Panel
3. Zkuste restart Apache

### Skóre se neukládá z Pythonové hry

1. Ověřte URL v Python kódu: `http://localhost/flappy_palach/submit_score.php`
2. Zkontrolujte, že Apache běží
3. Podívejte se do konzole Pythonu na chybové hlášky

### Prázdný žebříček

1. Zkontrolujte, že máte testovací data (spusťte `database.sql`)
2. Otevřete `http://localhost/flappy_palach/get_scores.php` - měli byste vidět JSON s daty
3. Zkontrolujte konzoli prohlížeče (F12) pro JavaScript chyby

## 🎨 Přizpůsobení

### Změna barev

Upravte soubor `style.css`:

```css
/* Hlavní gradient */
background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);

/* Můžete změnit na jiné barvy, např: */
background: linear-gradient(135deg, #FF6B6B 0%, #4ECDC4 100%);
```

### Změna počtu záznamů na stránku

V souboru `script.js` změňte:

```javascript
const CONFIG = {
    scoresPerPage: 50,  // Změňte na požadovaný počet
    // ...
};
```

### Automatické obnovování

V souboru `script.js` zapněte:

```javascript
const CONFIG = {
    autoRefresh: true,          // Změňte na true
    refreshInterval: 30000,     // 30 sekund
    // ...
};
```

## 📊 SQL dotazy pro správu

### Smazání všech záznamů
```sql
DELETE FROM scores;
```

### Smazání starých záznamů (starších než 30 dní)
```sql
DELETE FROM scores WHERE date_created < NOW() - INTERVAL 30 DAY;
```

### Export dat
V phpMyAdmin:
1. Vyberte databázi `flappy_palach`
2. Klikněte na **Export**
3. Vyberte formát (SQL doporučeno)
4. Klikněte **Provést**

## 🔒 Zabezpečení (pro produkci)

Pokud chcete web zpřístupnit veřejně:

1. **Změňte heslo do databáze** v `config.php`
2. **Použijte HTTPS** místo HTTP
3. **Přidejte API klíč** pro odesílání skóre
4. **Omezte počet requestů** (rate limiting)

## 📝 Licence

Tento projekt je vytvořen pro školní účely.

## 💡 Tipy

- Pravidelně zálohujte databázi
- Sledujte velikost databáze (po čase může narůst)
- Můžete přidat další funkce (reset skóre, ban hráčů, atd.)

## 🆘 Podpora

Pokud máte problémy:
1. Zkontrolujte, že Apache a MySQL běží
2. Podívejte se do error logu (v XAMPP)
3. Zkontrolujte konzoli prohlížeče (F12)

---

**Vytvořeno pro Flappy Palach © 2025**
