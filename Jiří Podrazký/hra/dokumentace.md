# 🚀 Space Invaders: Enterprise Edition - Operační manuál

Vítejte v operačním rozhraní pokročilého obranného systému **Space Invaders**. Tato dokumentace slouží k rychlé orientaci v ovládání plavidla, taktických systémech a identifikaci nepřátelských hrozeb.

---

## 🔐 1. Přístup do systému (Login)
Před zahájením mise je nutná autorizace operátora proti centrální databázi.
* **Vstupní pole:** Přepínejte mezi jménem a heslem pomocí klávesy **`TAB`**.
* **Autorizace:** Stiskněte **`ENTER`** pro odeslání požadavku na server.
* **Offline režim:** Pokud server neodpovídá, systém vás upozorní na chybu spojení.

---

## 🌌 2. Hlavní terminál a Hangár
Po úspěšném přihlášení získáte přístup k následujícím modulům:

* **HRÁT:** Spustí ostrou bojovou simulaci s aktuálně nakonfigurovaným plavidlem.
* **HANGÁR:** Vstup do výběru lodí. Klikněte myší na libovolný model v mřížce. Vybraná loď je indikována **zlatým rámečkem**. Pro potvrzení a návrat stiskněte **`ZPĚT`**.
* **KONEC:** Bezpečné ukončení všech procesů a odhlášení.

---

## 🎮 3. Ovládání plavidla
Bojový modul využívá pokročilou vektorovou kinematiku.
* **Pohyb vlevo:** Klávesa **`Šipka DOLEVA`**
* **Pohyb vpravo:** Klávesa **`Šipka DOPRAVA`**
* **Palba:** Klávesa **`MEZERNÍK`**

> **Taktický tip:** Loď využívá efekt **Banking** (kinetické naklánění). Při rychlém manévrování se loď nakloní do směru letu, což zlepšuje vizuální přehled o trajektorii.

---

## 👾 4. Taktická analýza nepřátel
Nepřátelské entity vstupují do sektoru skrze **Hyperprostor (Warp-in)**. Během modrého světelného záblesku a protahování textury jsou entity v meziprostoru a jsou **imunní vůči palbě**.

| Typ entity | Vlastnosti | Integrita (HP) |
| :--- | :--- | :--- |
| **Yellow Normal** | Standardní rychlost, základní hrozba. | 1 zásah |
| **Green Tank** | Pomalý, robustní pancéřování. Má viditelný Healthbar. | 3 zásahy |
| **Black Assassin** | Extrémní rychlost, zanechává Phantom Trail (stíny). | 1 zásah |

---

## 🛠️ 5. Evoluční moduly (Upgrady)
Během boje se v operační zóně zhmotňují **zlaté levitující bedny (Lootboxy)**. Jejich sebráním (přeletem lodě) vyvoláte menu evoluce:
* Navigujte v menu pomocí kláves **`1`**, **`2`** nebo **`3`**.
* **VOLLEY:** Přidá další střelu do zásobníku (víc projektilů naráz).
* **PLASMA:** Zvýší úsťovou rychlost vašich střel.
* **WIDE BEAM:** Zvětší kalibr (velikost) vašich střel.
* **DRONE SQUAD:** Aktivuje autonomní drony, které krouží kolem vás a pálí na cíle.
* **TURBO ENGINES:** Zvýší maximální rychlost pohybu vaší lodě.
* **SHIELD REPAIR:** Okamžitá oprava 1 bodu integrity.

---

## ⚠️ 6. Obranný perimetr a Bossové
* **Kritická linie:** Spodní rudý laserový perimetr. Pokud nepřítel proletí pod tuto linii, dojde k **Shield Overload** (přetížení štítů), ztratíte 1 život a sektor je vyčištěn výbojem.
* **Critical Entity (Boss):** Při dosažení milníku skóre obdržíte varování. Na scénu přiletí masivní loď s vysokým HP. Její zničení posune hru do další fáze (Stage) s jiným prostředím.

---

## 📊 7. HUD - Telemetrie
V horní liště neustále sledujte:
* **SCORE:** Vaše bojová efektivita.
* **STAGE:** Úroveň postupu vesmírem.
* **INTEGRITY:** Zbývající počet životů.
* **OP:** Vaše operační jméno v systému.

