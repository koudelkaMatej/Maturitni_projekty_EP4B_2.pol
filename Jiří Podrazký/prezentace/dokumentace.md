# Technická specifikace projektu Space Invaders

Tento dokument poskytuje detailní popis architektury, datových modelů a síťových protokolů použitých v projektu Space Invaders.

---

## 1. Systémová architektura
Systém je rozdělen na dvě hlavní části: klientskou aplikaci (Python/Pygame) a serverovou vrstvu (PHP/MySQL).

### 1.1 Klientský engine
Hra je implementována v jazyce Python s využitím knihovny Pygame. Jádro tvoří třída `Game`, která řídí herní smyčku s pevnou frekvencí 60 FPS. 
*   **Inicializace**: Před začátkem hry probíhá asynchronní ověření uživatele a načtení grafických assetů do operační paměti.
*   **Zpracování událostí**: Vstupy z klávesnice jsou transformovány na pohybové vektory entit.
*   **Vykreslování**: Využívá hardwarovou akceleraci pro blitování textur s alfa kanálem.

### 1.2 Serverová vrstva
Serverová část slouží k autorizaci a perzistenci dat. Pro komunikaci je využíváno bezestavové API postavené na protokolu HTTP POST.

---

## 2. Databázový model
Data jsou uložena v relační databázi MySQL/MariaDB s využitím tabulek `s18_users` a `s18_scoreboard`.

*   **Identita**: Tabulka `s18_users` ukládá unikátní uživatelská jména a hesla chráněná algoritmem BCRYPT.
*   **Relace**: Skóre je k uživateli vázáno pomocí cizího klíče (Foreign Key) s integritním omezením `ON DELETE CASCADE`.

---

## 3. Síťová komunikace a bezpečnost
Veškerá komunikace mezi klientem a serverem probíhá přes zabezpečené endpointy:

1.  **`check_login.php`**: Ověřuje integritu přihlašovacích údajů.
2.  **`save_score.php`**: Zajišťuje bezpečný zápis dosaženého výsledku.

Proti útokům typu SQL Injection jsou v PHP použity výhradně Prepared Statements (PDO).

---

## 4. Matematické modely a fyzika
*   **Kolize**: Detekce zásahů je realizována pomocí metody AABB (Axis-Aligned Bounding Box).
*   **VFX**: Částicový systém využívá lineární degradaci alfa kanálu a koeficienty kinetického tření pro simulaci explozí.
