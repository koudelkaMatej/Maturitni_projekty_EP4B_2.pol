# Vývojářská příručka Space Invaders

Tato příručka slouží jako referenční manuál pro budoucí rozvoj a údržbu projektu Space Invaders. Obsahuje konkrétní implementační postupy pro přidávání herních mechanik a modifikaci stávajících entit.

---

## 1. Vývojové prostředí
Hra je vyvíjena v jazyce **Python 3.10+**. Pro izolaci závislostí využíváme virtuální prostředí (`venv`).
*   **Závislosti**: `pygame`, `requests`.
*   **Spuštění**: `python menu.py`.

---

## 2. Implementační příklady (Herní mechaniky)

### 2.1 Přidání zvukových efektů
Pro přidání zvukové stopy k herní události:
1.  Uložte soubor ve formátu `.wav` do složky `hra/data/`.
2.  V metodě `load_assets()` inicializujte objekt zvuku:
    `self.sound_shoot = pygame.mixer.Sound("data/shoot.wav")`
3.  V místě spuštění (např. metoda `shoot()`) volejte: `self.sound_shoot.play()`.

### 2.2 Úprava grafiky Bosse
Chcete-li změnit vizuální reprezentaci nepřítele typu Boss:
1.  Nahraďte soubor `boss.png` v `hra/data/` novým obrázkem (zachovejte průhlednost PNG).
2.  Pokud měníte rozlišení, upravte konstanty rozměrů v metodě `load_assets()`.

### 2.3 Přidání speciálních zbraní (Trojitá střela)
1.  V třídě `Player` definujte stavový příznak `self.triple_shot`.
2.  V metodě `shoot()` přidejte logiku pro vícenásobnou instanci třídy `Bullet`:
    ```python
    if self.player.triple_shot:
        for angle in [-2, 0, 2]:
            self.bullets.append(Bullet(self.player.x, self.player.y, vx=angle, vy=-10))
    ```

---

## 3. Integrace s webovou vrstvou
Ukládání skóre probíhá ve třídě `Game` prostřednictvím metody `send_score()`.

### 3.1 Úprava scoreboardu
Zobrazení výsledků na webu je realizováno v `index.php`. Pro přidání nového pole do tabulky:
1.  Upravte SQL dotaz tak, aby zahrnoval požadované sloupce z tabulky `s18_users` nebo `s18_scoreboard`.
2.  V PHP cyklu `while` přidejte novou buňku `<td>`.

---

## 4. Testování a diagnostika
Projekt obsahuje základní sadu Unit testů umístěných přímo v `main.py`. Testy lze spustit příkazem:
`python main.py --test`

---

*Tato dokumentace je určena pro interní účely vývoje.*
