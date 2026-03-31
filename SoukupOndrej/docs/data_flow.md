# Návrh rozložení projektu (data a jejich toky) – Python hra + web + DB

## Komponenty
1) **Python hra (pygame)**: `client/main.py`
- Menu, výběr obtížnosti, herní smyčka, kolize, skóre
- Po Game Over: odešle skóre na server přes HTTP (REST)

2) **Backend (Flask)**: `server/app.py`
- REST API:
  - `GET /api/scores?difficulty=...&limit=...`
  - `POST /api/scores`
- Servíruje jednoduchý web `web/index.html` s leaderboardem

3) **Databáze (SQLite)**: `server/data/flappy.db`
- Tabulky `players`, `scores`

---

## Stavový automat hry (pygame)
- **MENU** → výběr obtížnosti, Start
- **READY** → čeká na první skok
- **PLAYING** → běží fyzika, trubky, skóre
- **GAMEOVER** → zobrazení výsledku + text input pro jméno + uložení do DB

---

## Datové toky (co–kde–kam–odkud)

### A) Herní smyčka (lokálně v Pythonu)
- `while running:` → `dt` → `update(dt)` → `render()`

**Data v RAM:**
- `bird`: pozice, rychlost, rotace
- `pipes[]`: pozice, mezera, passed
- `score`, `difficulty` → parametry (gap/speed/gravity/flap)

### B) Uložení skóre do DB (hra → server)
- **Odkud:** `client/main.py` po GameOver
- **Kam:** `POST http://127.0.0.1:5000/api/scores`
- **Co:** JSON `{name, difficulty, score}`
- **Výsledek:** `server/db.py` zapíše do SQLite

### C) Načtení žebříčku (web → server → DB)
- **Odkud:** `web/index.html`
- **Kam:** `GET /api/scores?difficulty=...`
- **Co:** top skóre z DB
- **Kam dál:** vykreslení tabulky v HTML
