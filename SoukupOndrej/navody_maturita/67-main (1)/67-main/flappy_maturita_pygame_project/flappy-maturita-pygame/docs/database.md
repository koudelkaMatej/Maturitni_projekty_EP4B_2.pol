# Návrh databáze (SQLite)

## Cíl
Ukládat žebříček skóre pro Flappy Bird podle obtížnosti.

## Tabulky
### `players`
- `id` (PK)
- `name`
- `created_at`

### `scores`
- `id` (PK)
- `player_id` (FK → players.id)
- `difficulty` (easy|normal|hard|insane)
- `score`
- `created_at`

## Vztah
- **Players (1) — (N) Scores**

## Integrita
- CHECK na `difficulty`
- CHECK na `score >= 0`
- FK s `ON DELETE CASCADE`

## Index
- `idx_scores_diff_score(difficulty, score DESC)` – rychlé dotazy na top skóre

Schéma je v `server/schema.sql`.
