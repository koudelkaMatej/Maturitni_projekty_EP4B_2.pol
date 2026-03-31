# Flappy Bird – maturitní projekt (Python hra + web + DB)

Tahle verze je **1:1 stejná myšlenka jako předtím**, jen samotná hra běží v **Pythonu (pygame)**.
Součástí projektu je pořád:
- **Python hra (pygame)** – Flappy Bird s menu, více obtížnostmi, hezkým UI
- **Web + REST API + DB** – Flask + SQLite pro ukládání a načítání žebříčku
- Dokumentace: datové toky, návrh DB, ER diagram

---

## Rychlé spuštění

### 0) Požadavky
- Python **3.10+**

### 1) Nainstaluj knihovny
V kořenové složce projektu:

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
# source .venv/bin/activate

pip install -r requirements.txt
```

### 2) Spusť server (web + DB)
```bash
python server/app.py
```

Otevři web (leaderboard):
- http://127.0.0.1:5000

### 3) Spusť hru (pygame)
V novém terminálu (se stejným venv):
```bash
python client/main.py
```

---

## Ovládání
- **Space / klik** = skok
- V menu: klikání, Enter = start
- Po Game Over: napiš jméno a Enter = uložit do DB

---

## Databáze
- SQLite se vytvoří automaticky při prvním spuštění serveru: `server/data/flappy.db`
- Schéma: `server/schema.sql`

---

## Dokumentace
- `docs/data_flow.md`
- `docs/database.md`
- `docs/ER_diagram.svg` (+ `docs/ER_diagram.mmd`)
