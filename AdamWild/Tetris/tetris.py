# ============================================================
# IMPORT KNIHOVEN
# ============================================================

import sys           # Načte systémový modul - potřebujeme sys.exit(), sys.argv (argumenty příkazové řádky)
import json          # Načte modul pro práci s JSON soubory - slouží k ukládání a načítání highscores
import os            # Načte modul pro práci se soubory a cestami - použijeme os.path.exists(), os.path.join() atd.
import random        # Načte modul pro náhodnost - použijeme random.choice() pro náhodný výběr kostičky/barvy

# Pygame načítáme pouze pokud NEspouštíme testy - testy pygame vůbec nepotřebují
# "python tetris.py test" = sys.argv[1] == "test" → pygame se přeskočí
if not (len(sys.argv) > 1 and sys.argv[1] == "test"):
    import pygame    # Načte knihovnu pygame - bez ní nelze kreslit okno, přijímat klávesy ani řídit čas
    pygame.init()    # Spustíme pygame - MUSÍ být voláno jako úplně první, jinak žádná pygame funkce nefunguje

# ============================================================
# HERNÍ KONSTANTY
# Konstanty jsou proměnné psané VELKÝMI PÍSMENY - jejich hodnota se nikdy nemění
# ============================================================

ROWS = 20          # Herní plocha má 20 řádků (výška) - standardní Tetris rozměr
COLS = 10          # Herní plocha má 10 sloupců (šířka) - standardní Tetris rozměr
FPS = 60           # Hra běží na 60 snímků za sekundu - plynulý pohyb bez trhání

# Seznam čtveřic (šířka, výška) - každá položka je jedno dostupné rozlišení okna
RESOLUTIONS = [(480, 800), (560, 1000), (700, 1240), (1920, 1080)]

# ============================================================
# BARVY
# Každá barva je trojice čísel (R, G, B) - červená, zelená, modrá, každá 0-255
# ============================================================

BLACK  = (0, 0, 0)           # Černá - použita pro prázdná políčka mřížky
GRAY   = (50, 50, 50)        # Tmavě šedá - okraje mřížky (pouze funkce draw_grid, jinak se nepoužívá)
WHITE  = (255, 255, 255)     # Bílá - texty, nadpisy, hodnoty v panelu
MENU_BG       = (30, 30, 30)      # Velmi tmavě šedá - pozadí menu a obrazovky zadání jména
BUTTON_COLOR  = (70, 70, 70)      # Středně šedá - normální barva tlačítka
BUTTON_HOVER  = (100, 100, 100)   # Světlejší šedá - barva tlačítka když na něj najede myš (hover efekt)

# Seznam barev kostiček - každá nová kostička dostane jednu náhodně vybranou barvu z tohoto seznamu
COLORS = [
    (0, 255, 255),    # Azurová  - kostička I (dlouhá tyč)
    (0, 0, 255),      # Modrá    - kostička J
    (255, 165, 0),    # Oranžová - kostička L
    (255, 255, 0),    # Žlutá    - kostička O (čtverec)
    (0, 255, 0),      # Zelená   - kostička S
    (128, 0, 128),    # Fialová  - kostička T
    (255, 0, 0),      # Červená  - kostička Z
]

# Tvary všech 7 kostiček - každý tvar je mřížka z 1 (vyplněný blok) a 0 (prázdné místo)
# Toto je ZÁKLADNÍ poloha - rotace se generují automaticky v new_piece()
SHAPES = [
    [[1, 1, 1, 1]],           # I - jeden řádek čtyř bloků za sebou
    [[1, 0, 0],               # J - blok vlevo nahoře + tři bloky v dolním řádku
     [1, 1, 1]],
    [[0, 0, 1],               # L - blok vpravo nahoře + tři bloky v dolním řádku
     [1, 1, 1]],
    [[1, 1],                  # O - čtverec 2x2, tato kostička nemá žádnou rotaci
     [1, 1]],
    [[0, 1, 1],               # S - dva bloky vpravo nahoře, dva bloky vlevo dole
     [1, 1, 0]],
    [[0, 1, 0],               # T - jeden blok uprostřed nahoře + tři bloky dole
     [1, 1, 1]],
    [[1, 1, 0],               # Z - dva bloky vlevo nahoře, dva bloky vpravo dole
     [0, 1, 1]]
]

# Sestaví absolutní cestu k souboru highscores.json ve stejné složce jako spustitelný soubor
# sys.argv[0] = cesta ke spouštěnému souboru, os.path.dirname() = složka tohoto souboru
# os.path.join() správně spojí složku a název souboru (funguje na Windows i Linux)
HIGHSCORE_FILE = os.path.join(os.path.dirname(sys.argv[0]), "highscores.json")

# Speciální klíč pro uložení posledního skóre do JSON slovníku
# Začíná __ aby bylo jasné, že nejde o jméno hráče, a dá se snadno odfiltrovat
LAST_SCORE_KEY = "__last_score__"


# ============================================================
# FUNKCE PRO PRÁCI S HIGHSCORES
# ============================================================

def load_highscores():
    """Načte highscores ze souboru JSON a vrátí je jako slovník {jmeno: skore}."""
    if not os.path.exists(HIGHSCORE_FILE):  # Zkontroluje, zda soubor vůbec existuje na disku
        return {}                            # Pokud neexistuje, vrátí prázdný slovník (první spuštění)
    try:                                     # try/except zachytí chyby čtení (poškozený soubor apod.)
        with open(HIGHSCORE_FILE, "r") as f:     # Otevře soubor pro čtení ("r" = read), f = file handle
            return json.load(f)                  # Přečte JSON ze souboru a vrátí ho jako Python slovník
    except:                                  # Pokud cokoliv selže (poškozený JSON, práva apod.)
        return {}                            # Vrátí prázdný slovník - hra nespadne kvůli vadnému souboru


def save_highscores(scores):
    """Uloží slovník se skóre do souboru JSON."""
    with open(HIGHSCORE_FILE, "w") as f:    # Otevře soubor pro zápis ("w" = write, přepíše starý obsah)
        json.dump(scores, f, indent=4)      # Zapíše Python slovník jako JSON, indent=4 = čitelné odsazení


def get_max_score(scores):
    """Vrátí nejvyšší skóre ze všech hráčů. Ignoruje speciální klíče začínající __."""
    # Slovníkové porozumění (dict comprehension) - vytvoří nový slovník jen s položkami hráčů
    # k = klíč (jméno hráče), v = hodnota (skóre)
    # Podmínka: klíč nesmí začínat __ (odfiltruje LAST_SCORE_KEY a podobné interní klíče)
    player_scores = {k: v for k, v in scores.items() if not k.startswith("__")}
    # Pokud slovník není prázdný, vrátí maximum hodnot; jinak vrátí 0
    return max(player_scores.values()) if player_scores else 0


def get_last_score(scores):
    """Vrátí poslední nahrané skóre, nebo 0 pokud žádné nebylo uloženo."""
    # dict.get(klíč, výchozí) - vrátí hodnotu pro klíč, nebo výchozí hodnotu pokud klíč neexistuje
    return scores.get(LAST_SCORE_KEY, 0)


# ============================================================
# ZADÁNÍ JMÉNA HRÁČE - zobrazí se po skončení hry
# ============================================================

def nacti_registrovane_uzivatele():
    """Načte seznam registrovaných uživatelů ze souboru prihlaseni.json.
    Vrátí množinu jmen (malými písmeny) pro rychlé vyhledávání.
    Pokud soubor neexistuje, vrátí prázdnou množinu (registrace není povinná)."""
    prihlaseni_soubor = os.path.join(os.path.dirname(sys.argv[0]), "prihlaseni.json")
    if not os.path.exists(prihlaseni_soubor):
        return set()  # Soubor neexistuje = kontrola je vypnuta
    try:
        with open(prihlaseni_soubor, "r", encoding="utf-8") as f:
            data = json.load(f)
        uzivatele = data.get("uzivatele", [])
        # Vrátíme množinu jmen malými písmeny pro porovnání bez ohledu na velikost
        return {u["username"].lower() for u in uzivatele if "username" in u}
    except Exception:
        return set()  # Při jakékoli chybě vrátíme prázdnou množinu


def ask_name(screen, width, height):
    """Zobrazí obrazovku pro zadání jména hráče.
    Ověří jméno oproti prihlaseni.json - pokud uživatel neexistuje, zobrazí chybu.
    Vrátí zadané jméno jako řetězec, nebo None pokud hráč zvolil Zpět do menu."""
    font_size  = max(20, min(36, width // 12))
    font       = pygame.font.SysFont("arial", font_size)
    small_font = pygame.font.SysFont("arial", max(14, font_size // 2))
    name       = ""
    chyba      = ""          # Chybová zpráva - prázdná = žádná chyba
    input_active = True
    go_to_menu = False       # Příznak - True = hráč chce zpět do menu
    clock = pygame.time.Clock()

    # Načteme registrované uživatele jednou před smyčkou
    registrovani = nacti_registrovane_uzivatele()
    # Zkontrolujeme zda soubor prihlaseni.json vůbec existuje
    prihlaseni_soubor = os.path.join(os.path.dirname(sys.argv[0]), "prihlaseni.json")
    soubor_existuje = os.path.exists(prihlaseni_soubor)
    # Kontrola je vždy aktivní pokud soubor existuje (i když je prázdný)
    # Pokud soubor neexistuje vůbec, kontrolu vypneme (volný režim)
    kontrola_aktivni = soubor_existuje

    # Rozměry a pozice tlačítka "Zpět do menu"
    btn_w, btn_h = 220, 50
    btn_x = width // 2 - btn_w // 2
    btn_y = min(height // 2 + 130, height - 80)  # Nikdy nepřekročí spodní okraj okna

    while input_active:
        screen.fill(MENU_BG)

        # Hlavní prompt
        prompt_text = "Zadej sve jmeno: " + name
        text_surface = font.render(prompt_text, True, WHITE)
        rect = text_surface.get_rect(center=(width // 2, height // 2 - 20))
        screen.blit(text_surface, rect)

        # Nápověda pod polem
        hint_color = (150, 150, 150)
        hint = small_font.render("Enter = potvrdit   Backspace = smazat", True, hint_color)
        hint_rect = hint.get_rect(center=(width // 2, height // 2 + 30))
        screen.blit(hint, hint_rect)

        # Chybová zpráva (červená) - zobrazí se pokud jméno nebylo nalezeno
        if chyba:
            chyba_barva = (255, 80, 80)
            chyba_surf = small_font.render(chyba, True, chyba_barva)
            chyba_rect = chyba_surf.get_rect(center=(width // 2, height // 2 + 65))
            screen.blit(chyba_surf, chyba_rect)

        # Info řádek dole (pokud je kontrola aktivní)
        if kontrola_aktivni:
            info = small_font.render("Pouzij jmeno z webu (prihlaseni.json)", True, (100, 100, 100))
            info_rect = info.get_rect(center=(width // 2, height // 2 + 95))
            screen.blit(info_surf := info, info_rect)

        # Tlačítko "Zpět do menu" - zvýrazněné zelenou barvou, vždy viditelné
        mouse_pos = pygame.mouse.get_pos()
        btn_hovered = btn_x <= mouse_pos[0] <= btn_x + btn_w and btn_y <= mouse_pos[1] <= btn_y + btn_h
        btn_color = (60, 160, 60) if btn_hovered else (40, 120, 40)
        pygame.draw.rect(screen, btn_color, (btn_x, btn_y, btn_w, btn_h), border_radius=8)
        pygame.draw.rect(screen, (80, 200, 80), (btn_x, btn_y, btn_w, btn_h), 2, border_radius=8)
        btn_label = small_font.render("< Zpet do menu", True, WHITE)
        btn_label_rect = btn_label.get_rect(center=(btn_x + btn_w // 2, btn_y + btn_h // 2))
        screen.blit(btn_label, btn_label_rect)

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    # Escape = rychlý návrat do menu
                    go_to_menu = True
                    input_active = False
                elif event.key == pygame.K_RETURN and name.strip():
                    # Ověření jména oproti databázi registrovaných uživatelů
                    if kontrola_aktivni and len(registrovani) == 0:
                        # Soubor existuje ale je prázdný - nikdo není registrován
                        chyba = "Zadny uzivatel neni registrovan!"
                        name  = ""
                    elif kontrola_aktivni and name.lower() not in registrovani:
                        # Uživatel nenalezen - zobrazíme chybu, NEUKONČÍME smyčku
                        chyba = f"Uzivatel '{name}' neni registrovan!"
                        name  = ""   # Vymažeme pole pro nové zadání
                    else:
                        # Jméno je v pořádku (buď existuje v databázi, nebo kontrola je vypnutá)
                        input_active = False
                elif event.key == pygame.K_BACKSPACE:
                    name  = name[:-1]
                    chyba = ""       # Smazat znak = vyčistit chybovou zprávu
                elif len(name) < 16 and (event.unicode.isalnum() or event.unicode == "_"):
                    name  += event.unicode
                    chyba = ""       # Psaní = vyčistit chybovou zprávu
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if btn_x <= event.pos[0] <= btn_x + btn_w and btn_y <= event.pos[1] <= btn_y + btn_h:
                    # Klik na tlačítko "Zpět do menu"
                    go_to_menu = True
                    input_active = False

        clock.tick(60)

    if go_to_menu:
        return None  # None = hráč se vrátil do menu bez uložení
    return name  # Vrátí ověřené jméno volající funkci (game_over_save)


# ============================================================
# TŘÍDA KOSTIČKY (Piece)
# Třída = šablona pro vytváření objektů. Každá kostička je jeden objekt třídy Piece.
# ============================================================

class Piece:
    def __init__(self, x, y, shape):
        """Konstruktor - zavolá se automaticky při vytvoření nové kostičky (Piece(...))."""
        self.x = x              # Uloží X pozici (sloupec) kostičky na hrací ploše
        self.y = y              # Uloží Y pozici (řádek) kostičky na hrací ploše
        self.shape = shape      # Uloží seznam všech rotací kostičky (vytvořený v new_piece)
        self.color = random.choice(COLORS)  # Náhodně vybere jednu barvu ze seznamu COLORS
        self.rotation = 0       # Začíná v základní rotaci (index 0 v seznamu shape)

    def image(self):
        """Vrátí aktuální tvar kostičky (2D seznam 0 a 1) podle její aktuální rotace."""
        # Modulo (%) zajistí cyklické opakování - pokud by rotation přetekla délku, vrátí se na začátek
        return self.shape[self.rotation % len(self.shape)]

    def rotate(self):
        """Posune rotaci o jednu dopředu = otočení o 90° doprava."""
        # Modulo zajistí, že po poslední rotaci se vrátíme zpět na 0 (cyklická rotace)
        self.rotation = (self.rotation + 1) % len(self.shape)


def new_piece():
    """Vytvoří novou náhodnou kostičku a předpočítá všechny její rotace."""
    shape = random.choice(SHAPES)   # Náhodně vybere jeden ze 7 základních tvarů
    rotations = [shape]             # Začne seznam rotací se základní polohou (0°)

    for _ in range(3):              # Opakuje 3x - přidá rotace 90°, 180°, 270°
        # zip(*shape[::-1]) je matematický trik pro otočení 2D matice o 90° doprava:
        # shape[::-1] = obrácení pořadí řádků matice
        # zip(*...) = transpozice (záměna řádků a sloupců)
        shape = list(zip(*shape[::-1]))
        # Každou rotaci uloží jako seznam seznamů (zip vrací tuple, musíme převést)
        rotations.append([list(row) for row in shape])

    # Vrátí nový objekt Piece: startovní sloupec 3 (střed plochy), řádek 0 (nahoře), se všemi rotacemi
    return Piece(3, 0, rotations)


# ============================================================
# HERNÍ LOGIKA - pohyb, kolize, mazání řádků
# ============================================================

def valid_space(piece, grid):
    """Zkontroluje zda kostička na své aktuální pozici nekoliduje s hranou nebo jiným blokem.
    Vrátí True = pozice je volná, False = kolize."""
    shape = piece.image()                   # Získá aktuální tvar kostičky (2D seznam)

    for i, row in enumerate(shape):         # i = index řádku v tvaru kostičky (0, 1, ...)
        for j, cell in enumerate(row):      # j = index sloupce v řádku tvaru (0, 1, 2, ...)
            if cell:                        # Pokud je cell == 1 (vyplněný blok, ne prázdné místo)
                new_x = piece.x + j        # Absolutní X pozice tohoto bloku na hrací ploše
                new_y = piece.y + i        # Absolutní Y pozice tohoto bloku na hrací ploše

                # Zkontroluje, zda blok není mimo levý/pravý okraj nebo pod spodním okrajem
                if new_x < 0 or new_x >= COLS or new_y >= ROWS:
                    return False            # Mimo hranice = neplatná pozice

                # Zkontroluje, zda políčko v mřížce není obsazeno jinou kostičkou
                # new_y >= 0 chrání před indexováním záporných řádků (kostička ještě nad plochou)
                if new_y >= 0 and grid[new_y][new_x] != BLACK:
                    return False            # Políčko obsazeno = kolize = neplatná pozice

    return True  # Všechny bloky kostičky jsou na volných místech = platná pozice


def place_piece(piece, grid):
    """Natrvalo zapíše kostičku do mřížky - používá se když kostička dosedne."""
    shape = piece.image()                       # Získá aktuální tvar kostičky

    for i, row in enumerate(shape):             # Prochází každý řádek tvaru
        for j, cell in enumerate(row):          # Prochází každé pole v řádku
            if cell:                            # Pouze vyplněné bloky (1), ne prázdná místa (0)
                # Zapíše barvu kostičky do odpovídajícího políčka mřížky
                grid[piece.y + i][piece.x + j] = piece.color


def clear_rows(grid):
    """Najde plné řádky, smaže je a přidá prázdné na vrch. Vrátí počet smazaných řádků."""
    # List comprehension - vytvoří seznam indexů plných řádků
    # Řádek je plný pokud každé políčko (cell) je jiné než BLACK (= obsazené)
    full_rows = [i for i, row in enumerate(grid) if all(cell != BLACK for cell in row)]

    for i in full_rows:             # Projde každý plný řádek
        del grid[i]                 # Smaže ho ze seznamu - ostatní řádky se posunou dolů
        # Vloží nový prázdný řádek na index 0 (úplně nahoře) - simuluje pád bloků dolů
        grid.insert(0, [BLACK for _ in range(COLS)])

    return len(full_rows)           # Vrátí počet smazaných řádků - použije se pro výpočet skóre


# ============================================================
# KRESLENÍ - funkce pro vykreslování na obrazovku
# ============================================================

def draw_grid(screen, grid, block_size, offset_x, offset_y):
    """Vykreslí hrací plochu - každé políčko dostane svou barvu a šedý rámeček."""
    for i in range(ROWS):       # Prochází všechny řádky (0 až 19)
        for j in range(COLS):   # Prochází všechny sloupce (0 až 9)
            # Spočítá pixelové souřadnice políčka: offset + pozice*velikost bloku
            rect = (offset_x + j * block_size, offset_y + i * block_size, block_size, block_size)
            pygame.draw.rect(screen, grid[i][j], rect)   # Vyplní políčko barvou z mřížky
            pygame.draw.rect(screen, GRAY, rect, 1)      # Nakreslí šedý rámeček tloušťky 1px (mřížka)


def draw_text(screen, text, size, color, x, y, center=True):
    """Nakreslí text na obrazovku. center=True = vycentrovat kolem (x,y), False = levý horní roh na (x,y)."""
    font = pygame.font.SysFont("arial", size, bold=True)    # Vytvoří tučné arial písmo dané velikosti
    label = font.render(text, True, color)                  # Vykreslí text do Surface (True = antialiasing)
    # get_rect vrátí obdélník textu, center/topleft nastaví jeho zarovnání
    rect = label.get_rect(center=(x, y)) if center else label.get_rect(topleft=(x, y))
    screen.blit(label, rect)    # Nakopíruje text surface na hlavní obrazovku na správnou pozici
    return rect                 # Vrátí obdélník - volající ho může použít pro detekci kliknutí


def button(screen, text, x, y, w, h, action=None):
    """Nakreslí tlačítko a při kliknutí zavolá funkci action."""
    mouse = pygame.mouse.get_pos()         # Zjistí aktuální pozici kurzoru myši jako (x, y)
    click = pygame.mouse.get_pressed()[0]  # [0] = levé tlačítko myši; True pokud je stisknuto
    # Pokud je myš uvnitř tlačítka, použije světlejší barvu (hover efekt), jinak normální
    color = BUTTON_HOVER if (x < mouse[0] < x + w and y < mouse[1] < y + h) else BUTTON_COLOR
    pygame.draw.rect(screen, color, (x, y, w, h), border_radius=10)  # Nakreslí obdélník se zakulacenými rohy
    draw_text(screen, text, 24, WHITE, x + w // 2, y + h // 2)       # Nakreslí text přesně do středu tlačítka
    # Pokud je myš nad tlačítkem A levé tlačítko je stisknuto
    if click and (x < mouse[0] < x + w and y < mouse[1] < y + h):
        if action:                       # Pokud byla předána funkce k zavolání
            pygame.time.wait(150)        # Pauza 150ms - zabrání víceprůchodovému kliknutí (debounce)
            action()                     # Zavolá přiřazenou funkci (např. start_game, go_back...)


# ============================================================
# KRESLENÍ PRAVÉHO PANELU
# Jedna centrální funkce - zabrání opakování stejného kódu ve 3 různých místech
# ============================================================

def draw_panel(screen, BORDER_COLOR, PANEL_COLOR, panel_x, panel_width, offset_y,
               block_size, hard_mode, score, lines, level,
               next_piece, display_max_score, display_last_score):
    """Vykreslí celý pravý informační panel: mód, skóre, řádky, level, max, minule, další kostička."""

    # Nakreslí vyplněný obdélník = pozadí panelu
    pygame.draw.rect(screen, PANEL_COLOR,
                     (panel_x - 5, offset_y - 3, panel_width + 5, block_size * ROWS + 6),
                     border_radius=8)  # border_radius=8 = zakulacené rohy
    # Nakreslí obrys panelu (tloušťka 2px) přes pozadí
    pygame.draw.rect(screen, BORDER_COLOR,
                     (panel_x - 5, offset_y - 3, panel_width + 5, block_size * ROWS + 6),
                     2, border_radius=8)

    cx = panel_x + panel_width // 2 - 5  # Vypočítá X souřadnici středu panelu pro centrování textů

    # Zobrazí aktuální herní mód - červená pro HARD, zelená pro NORMAL
    mode_color = (255, 80, 80) if hard_mode else (80, 200, 80)
    draw_text(screen, "HARD" if hard_mode else "NORMAL", 14, mode_color, cx, offset_y + 16)

    # Popisek "SKÓRE" malým písmem v modravé barvě (sekundární barva)
    draw_text(screen, "SKÓRE", 13, (150, 150, 200), cx, offset_y + 38)
    # Samotná hodnota skóre - větší písmo, bílá barva; str() převede číslo na řetězec
    draw_text(screen, str(score), 20, WHITE, cx, offset_y + 57)

    # Popisek "ŘÁDKY" - počet celkově smazaných řádků
    draw_text(screen, "ŘÁDKY", 13, (150, 150, 200), cx, offset_y + 82)
    draw_text(screen, str(lines), 20, WHITE, cx, offset_y + 101)

    # Popisek "LEVEL" - level se zvyšuje každých 1000 bodů
    draw_text(screen, "LEVEL", 13, (150, 150, 200), cx, offset_y + 126)
    draw_text(screen, str(level), 20, WHITE, cx, offset_y + 145)

    # Vodorovná oddělující čára mezi levelem a max skóre
    pygame.draw.line(screen, BORDER_COLOR,
                     (panel_x - 5, offset_y + 165),   # Počáteční bod čáry (x1, y1)
                     (panel_x + panel_width, offset_y + 165),  # Koncový bod čáry (x2, y2)
                     1)  # Tloušťka čáry v pixelech

    # MAX skóre - zlatá barva (255, 215, 0) = barva zlata
    draw_text(screen, "MAX", 13, (150, 150, 200), cx, offset_y + 182)
    draw_text(screen, str(display_max_score), 18, (255, 215, 0), cx, offset_y + 200)

    # POSLEDNÍ skóre - světle modrá barva
    draw_text(screen, "MINULE", 13, (150, 150, 200), cx, offset_y + 222)
    draw_text(screen, str(display_last_score), 18, (130, 200, 255), cx, offset_y + 240)

    # Druhá oddělující čára mezi posledním skóre a náhledem příští kostičky
    pygame.draw.line(screen, BORDER_COLOR,
                     (panel_x - 5, offset_y + 258),
                     (panel_x + panel_width, offset_y + 258),
                     1)

    # Popisek a vykreslení náhledu příští kostičky
    draw_text(screen, "DALŠÍ", 13, (150, 150, 200), cx, offset_y + 274)
    draw_next_piece(screen, next_piece, panel_x, offset_y + 290, block_size - 4)  # blok o 4px menší = vizuálně menší


# ============================================================
# ANIMACE
# ============================================================

def animated_hard_drop(screen, piece, grid, block_size, offset_x, offset_y,
                        BG_COLOR, BORDER_COLOR, PANEL_COLOR, panel_x, panel_width,
                        score, lines, hard_mode, next_piece, level,
                        display_max_score, display_last_score):
    """Animace hard dropu - kostička viditelně proletí celou plochou dolů se stopou za sebou."""
    import copy  # Import zde (ne nahoře) - copy je potřeba pouze v této funkci, lokální import šetří paměť

    anim_piece = copy.copy(piece)       # Vytvoří mělkou kopii objektu kostičky (nový objekt, stejná data)
    anim_piece.shape = piece.shape      # Zkopíruje odkaz na seznam rotací (sdílený, neměníme ho)
    anim_piece.color = piece.color      # Zkopíruje barvu kostičky
    anim_piece.rotation = piece.rotation  # Zkopíruje aktuální index rotace

    clock = pygame.time.Clock()         # Lokální hodiny pro řízení rychlosti animace

    # Najde nejnižší volnou pozici: posouvá kopii dolů dokud je pozice platná
    while valid_space(anim_piece, grid):
        anim_piece.y += 1               # Posune kopii o jeden řádek dolů
    anim_piece.y -= 1                   # Jeden krok zpět - poslední platná (neklidující) pozice

    start_y = piece.y   # Uloží odkud kostička začíná padat (aktuální Y pozice originálu)
    end_y = anim_piece.y  # Uloží kam kostička dopadne (cílová Y pozice)

    for y in range(start_y, end_y + 1):  # Prochází každou Y pozici od startu do cíle
        screen.fill(BG_COLOR)            # Smaže obrazovku tmavým pozadím (připraví nový snímek)

        board_width = block_size * COLS  # Celková šířka hrací plochy v pixelech
        # Nakreslí rámeček kolem hrací plochy (3px přesah na každou stranu, 3px tloušťka)
        pygame.draw.rect(screen, BORDER_COLOR,
                         (offset_x - 3, offset_y - 3, board_width + 6, block_size * ROWS + 6),
                         3, border_radius=4)

        # Nakreslí všechna pevně umístěná políčka mřížky
        for i in range(ROWS):           # Prochází řádky
            for j in range(COLS):       # Prochází sloupce
                rect = (offset_x + j * block_size, offset_y + i * block_size, block_size, block_size)
                color = grid[i][j]      # Načte barvu políčka z herní mřížky
                pygame.draw.rect(screen, color, rect)  # Vyplní políčko barvou
                if color != BLACK:      # Obsazené políčko dostane světlejší okraj = 3D efekt
                    light = (min(color[0] + 60, 255), min(color[1] + 60, 255), min(color[2] + 60, 255))
                    # min(..., 255) zabrání přetečení - RGB hodnota nesmí překročit 255
                    pygame.draw.rect(screen, light, rect, 2, border_radius=2)
                else:                   # Prázdné políčko dostane jemnou tmavou mřížku
                    pygame.draw.rect(screen, (30, 30, 50), rect, 1)

        shape = piece.image()  # Načte tvar originální kostičky (ne kopie) pro kreslení stopy a těla

        # Nakreslí vizuální stopu (trail) - bloky zanechané za padající kostičkou
        for trail in range(min(4, y - start_y)):   # Max 4 stopové bloky; min() zabrání záporným hodnotám na začátku
            trail_y = y - trail - 1                 # Y pozice stopy: čím větší trail, tím výše (starší stopa)
            alpha_val = max(30, 120 - trail * 30)   # Čím starší stopa (větší trail), tím tmavší; min 30
            for i, row in enumerate(shape):
                for j, cell in enumerate(row):
                    if cell:                        # Pouze vyplněné bloky tvaru
                        ty = trail_y + i            # Absolutní Y pozice stopového bloku
                        tx = piece.x + j            # Absolutní X pozice stopového bloku
                        if 0 <= ty < ROWS:          # Kreslí jen pokud je stopa v hrací ploše (ne nad ní)
                            trail_rect = (offset_x + tx * block_size + 2,   # +2 = malý vnitřní odskok
                                          offset_y + ty * block_size + 2,
                                          block_size - 4, block_size - 4)    # -4 = menší než plný blok
                            # Barva stopy = ztmavená verze barvy kostičky (mixování s alpha_val)
                            trail_color = (min(255, piece.color[0] * alpha_val // 255 + 10),
                                           min(255, piece.color[1] * alpha_val // 255 + 10),
                                           min(255, piece.color[2] * alpha_val // 255 + 10))
                            pygame.draw.rect(screen, trail_color, trail_rect, border_radius=2)

        # Nakreslí samotnou kostičku na aktuální Y pozici animace
        for i, row in enumerate(shape):
            for j, cell in enumerate(row):
                if cell:                            # Pouze vyplněné bloky
                    cy = y + i                      # Absolutní Y pozice bloku
                    cx_pos = piece.x + j            # Absolutní X pozice bloku
                    if 0 <= cy < ROWS:              # Kreslí jen pokud je blok v hrací ploše
                        rect = (offset_x + cx_pos * block_size, offset_y + cy * block_size,
                                block_size, block_size)
                        pygame.draw.rect(screen, piece.color, rect, border_radius=2)  # Vyplní barvou
                        # Přidá světlejší okraj pro 3D efekt (ještě světlejší než u pevných bloků - +80 vs +60)
                        light = (min(255, piece.color[0] + 80), min(255, piece.color[1] + 80),
                                 min(255, piece.color[2] + 80))
                        pygame.draw.rect(screen, light, rect, 2, border_radius=2)

        # Nakreslí pravý informační panel (skóre, level, max, minule, další...)
        draw_panel(screen, BORDER_COLOR, PANEL_COLOR, panel_x, panel_width, offset_y,
                   block_size, hard_mode, score, lines, level,
                   next_piece, display_max_score, display_last_score)

        pygame.display.update()  # Zobrazí nakreslený snímek na obrazovce
        clock.tick(120)          # Animace běží na 120 FPS - dvakrát rychlejší než hra = plynulá

    return end_y  # Vrátí Y pozici kde kostička přistane - play_game ji použije pro umístění originálu


def line_clear_animation(screen, full_rows, grid, block_size, offset_x, offset_y,
                          bg_color, border_color, panel_color, panel_x, panel_width,
                          score, lines, hard_mode, next_piece, level,
                          display_max_score, display_last_score):
    """Animace mazání řádků - plné řádky nejprve poblikají (přechod k bílé) a pak zmizí."""
    for step in range(6):           # 6 kroků animace = 6 snímků záblesku (každý 40ms = celkem 240ms)
        screen.fill(bg_color)       # Smaže obrazovku pro nový snímek animace

        board_width = block_size * COLS  # Šířka hrací plochy v pixelech
        # Nakreslí rámeček hrací plochy
        pygame.draw.rect(screen, border_color,
                         (offset_x - 3, offset_y - 3, board_width + 6, block_size * ROWS + 6),
                         3, border_radius=4)

        for i in range(ROWS):       # Prochází všechny řádky
            for j in range(COLS):   # Prochází všechny sloupce
                rect = (offset_x + j * block_size, offset_y + i * block_size, block_size, block_size)
                color = grid[i][j]  # Načte barvu políčka

                if i in full_rows:      # Tento řádek se maže - přehraje záblesk
                    t = step / 5.0      # t jde od 0.0 (step=0) do 1.0 (step=5) - průběh animace
                    # Interpolace barvy od původní k bílé:
                    # (1-t) = 1 na začátku (plná barva), 0 na konci (plná bílá)
                    flash_col = (
                        min(255, int(color[0] + (255 - color[0]) * (1 - t))),  # Červená složka
                        min(255, int(color[1] + (255 - color[1]) * (1 - t))),  # Zelená složka
                        min(255, int(color[2] + (255 - color[2]) * (1 - t)))   # Modrá složka
                    )
                    pygame.draw.rect(screen, flash_col, rect, border_radius=2)  # Nakreslí zábleskový blok
                else:                           # Normální řádek - nakreslí standardně
                    pygame.draw.rect(screen, color, rect)
                    if color != BLACK:          # Obsazené políčko - přidá 3D okraj
                        light = (min(color[0] + 60, 255), min(color[1] + 60, 255), min(color[2] + 60, 255))
                        pygame.draw.rect(screen, light, rect, 2, border_radius=2)
                    else:                       # Prázdné políčko - jemná mřížka
                        pygame.draw.rect(screen, (30, 30, 50), rect, 1)

        # Nakreslí pravý panel se všemi informacemi (stejný jako v hlavní smyčce)
        draw_panel(screen, border_color, panel_color, panel_x, panel_width, offset_y,
                   block_size, hard_mode, score, lines, level,
                   next_piece, display_max_score, display_last_score)

        pygame.display.update()     # Zobrazí snímek animace
        pygame.time.wait(40)        # Počká 40 milisekund - záblesk je tak viditelný lidskému oku


# ============================================================
# NÁHLED DALŠÍ KOSTIČKY v pravém panelu
# ============================================================

def draw_next_piece(screen, piece, panel_x, panel_y, block_size):
    """Vykreslí malý náhled příští kostičky v pravém panelu, vycentrovaný v oblasti 5x5."""
    shape = piece.image()                       # Načte aktuální tvar kostičky (2D seznam)

    # Vypočítá odsazení aby byla kostička vycentrovaná uvnitř imaginární oblasti 5x5 bloků
    offset_x = (5 - len(shape[0])) // 2        # Horizontální odsazení = (5 - šířka tvaru) / 2
    offset_y = (5 - len(shape)) // 2           # Vertikální odsazení = (5 - výška tvaru) / 2

    for i, row in enumerate(shape):            # Prochází řádky tvaru
        for j, cell in enumerate(row):         # Prochází sloupce v řádku
            if cell:                           # Pouze vyplněné bloky
                # Absolutní X pozice v pixelech: začátek panelu + (odsazení+sloupec) * velikost bloku
                x = panel_x + (offset_x + j) * block_size
                # Absolutní Y pozice v pixelech: začátek oblasti náhledu + (odsazení+řádek) * velikost bloku
                y = panel_y + (offset_y + i) * block_size
                rect = (x, y, block_size - 1, block_size - 1)  # -1 = malá mezera mezi bloky
                pygame.draw.rect(screen, piece.color, rect, border_radius=3)  # Vyplní blokem barvy kostičky
                # Přidá světlejší okraj pro 3D efekt
                light = (min(piece.color[0] + 60, 255), min(piece.color[1] + 60, 255),
                         min(piece.color[2] + 60, 255))
                pygame.draw.rect(screen, light, rect, 2, border_radius=3)


# ============================================================
# HLAVNÍ HERNÍ SMYČKA
# ============================================================

def play_game(screen, width, height, fullscreen=False, hard_mode=False):
    """Spustí a řídí celou hru od prvního snímku až po konec (prohra nebo návrat do menu)."""

    panel_width = 110   # Šířka pravého panelu s informacemi v pixelech (fixní)
    margin = 20         # Okraj kolem herní plochy v pixelech (vlevo, vpravo, nahoře, dole)

    # Dostupná šířka pro hrací plochu = celá šířka okna minus panel, minus okraje (3x margin: vlevo, střed, vpravo)
    available_width = width - panel_width - margin * 3
    # Dostupná výška pro hrací plochu = celá výška okna minus okraje nahoře a dole
    available_height = height - margin * 2

    # Velikost jednoho bloku = minimum z max možné šířky a max možné výšky
    # Zajistí, že plocha se vejde jak do šířky tak do výšky okna
    block_size = min(available_width // COLS, available_height // ROWS)

    board_width  = block_size * COLS    # Celková šířka hrací plochy v pixelech
    board_height = block_size * ROWS    # Celková výška hrací plochy v pixelech

    total_width = board_width + margin + panel_width  # Celková šířka layoutu (plocha + mezera + panel)
    offset_x = (width - total_width) // 2            # X pozice levého okraje hrací plochy (horizontální centrování)
    offset_y = (height - board_height) // 2          # Y pozice horního okraje hrací plochy (vertikální centrování)
    panel_x = offset_x + board_width + margin         # X pozice levého okraje panelu (hned za hrací plochou)

    BG_COLOR    = (18, 18, 30)    # Velmi tmavě modré pozadí hry (barva vesmíru)
    PANEL_COLOR = (30, 30, 50)    # O trochu světlejší modrá pro panel (viditelný rozdíl)
    BORDER_COLOR = (60, 60, 100)  # Ještě světlejší modrá pro okraje a čáry

    # Načteme highscores ze souboru PŘED začátkem hry - zobrazíme je v panelu celou hru
    _hs = load_highscores()                   # _hs = underscore na začátku = pomocná/dočasná proměnná
    display_max_score  = get_max_score(_hs)   # Nejvyšší skóre všech hráčů (zobrazeno zlatě)
    display_last_score = get_last_score(_hs)  # Poslední nahrané skóre (zobrazeno světle modře)

    # Vytvoří prázdnou herní mřížku: seznam 20 řádků, každý řádek = seznam 10 černých políček
    grid = [[BLACK for _ in range(COLS)] for _ in range(ROWS)]
    current_piece = new_piece()     # Vygeneruje první padající kostičku (náhodný tvar a barva)
    next_piece    = new_piece()     # Vygeneruje kostičku která přijde jako další (zobrazena v panelu)

    clock      = pygame.time.Clock()  # Hodiny pro řízení FPS a měření delta time
    fall_time  = 0                    # Čítač ms od posledního automatického pádu kostičky
    # Základní rychlost pádu: hard mode = 0.45s/krok (rychleji), normal = 0.6s/krok
    fall_speed = 0.45 if hard_mode else 0.6
    score      = 0      # Aktuální skóre hráče (začíná na 0)
    lines      = 0      # Celkový počet smazaných řádků v této hře
    level      = 1      # Aktuální level (zvyšuje se každých 1000 bodů)
    move_cooldown = 0   # Čítač ms pro prodlevu pohybu vlevo/vpravo (zabraňuje příliš rychlému pohybu)
    paused     = False  # Příznak pauzy: True = hra je pozastavena, False = hra běží

    def game_over_save():
        """Vnitřní funkce volaná při prohře: zobrazí zadání jména a uloží skóre.
        Pokud hráč klikne 'Zpět do menu', vrátí False. Jinak uloží skóre a vrátí True."""
        name = ask_name(screen, width, height)  # Zobrazí obrazovku pro zadání jména, vrátí jméno nebo None

        if name is None:
            return False  # Hráč zvolil Zpět do menu - nic neukládáme

        highscores = load_highscores()          # Znovu načte aktuální highscores ze souboru

        # Uloží poslední skóre pod speciálním klíčem - přepíše předchozí hodnotu
        highscores[LAST_SCORE_KEY] = score

        if name in highscores:                  # Hráč s tímto jménem už existuje v tabulce
            if score > highscores[name]:        # Uloží jen pokud je nové skóre lepší než stávající
                highscores[name] = score
        else:                                   # Nový hráč - přidá ho do tabulky
            highscores[name] = score

        save_highscores(highscores)             # Zapíše aktualizovaný slovník do souboru JSON
        return True

    # -----------------------------------------------
    # HLAVNÍ HERNÍ SMYČKA - opakuje se každý snímek
    # -----------------------------------------------
    running = True
    while running:
        # clock.tick(FPS) počká tak dlouho aby FPS nepřekročilo 60, vrátí ms od minulého volání
        dt = clock.tick(FPS)  # dt = delta time = čas od posledního snímku v milisekundách

        # --- ZPRACOVÁNÍ UDÁLOSTÍ ---
        for event in pygame.event.get():        # Projde všechny události ve frontě od minulého snímku
            if event.type == pygame.QUIT:       # Uživatel klikl na křížek okna
                pygame.quit()                   # Ukončí pygame
                sys.exit()                      # Ukončí Python proces

            elif event.type == pygame.KEYDOWN:  # Byla stisknuta klávesa (detekuje pouze okamžik stisku)
                if event.key == pygame.K_ESCAPE:    # ESC = přepnout pauzu
                    paused = not paused             # Přepne True->False nebo False->True
                    if paused:                      # Pokud jsme právě zapnuli pauzu
                        draw_pause_screen(screen, width, height)  # Zobrazí overlay s "PAUZA"

                elif paused and event.key == pygame.K_m:  # M stisknuto během pauzy
                    return                          # Ukončí play_game = vrátí se do hlavního menu

                elif not paused:                    # Tyto klávesy fungují jen pokud hra NEje pozastavena
                    if event.key == pygame.K_r:     # R = otočit kostičku
                        current_piece.rotate()      # Zvýší index rotace o 1
                        if not valid_space(current_piece, grid):    # Otočená poloha není volná (kolize)
                            current_piece.rotation -= 1             # Vrátí rotaci zpět (undo)

                    elif event.key == pygame.K_SPACE:               # Mezerník = hard drop
                        level = score // 1000 + 1                   # Aktualizuje level pro animaci
                        # Spustí animaci pádu a vrátí Y pozici kde kostička dopadla
                        final_y = animated_hard_drop(
                            screen, current_piece, grid, block_size, offset_x, offset_y,
                            BG_COLOR, BORDER_COLOR, PANEL_COLOR, panel_x, panel_width,
                            score, lines, hard_mode, next_piece, level,
                            display_max_score, display_last_score)
                        current_piece.y = final_y                   # Přesune originál na cílovou pozici
                        place_piece(current_piece, grid)            # Zapíše kostičku natrvalo do mřížky

                        # Zjistí indexy plných řádků pro animaci mazání
                        full_rows = [i for i, row in enumerate(grid) if all(cell != BLACK for cell in row)]
                        if full_rows:                               # Pokud jsou nějaké plné řádky
                            line_clear_animation(                   # Přehraje animaci záblesku a zmizení
                                screen, full_rows, grid, block_size, offset_x, offset_y,
                                BG_COLOR, BORDER_COLOR, PANEL_COLOR, panel_x, panel_width,
                                score, lines, hard_mode, next_piece, level,
                                display_max_score, display_last_score)

                        cleared = clear_rows(grid)      # Smaže plné řádky, vrátí jejich počet
                        score  += cleared * 100         # 100 bodů za každý smazaný řádek
                        lines  += cleared               # Přičte k celkovému počtu smazaných řádků
                        current_piece = next_piece      # Příští kostička se stane aktuální
                        next_piece    = new_piece()     # Vygeneruje novou příští kostičku

                        if not valid_space(current_piece, grid):    # Nová kostička nemá místo = konec hry
                            game_over_save()            # Uloží skóre
                            return                      # Ukončí play_game = návrat do menu

                    elif event.key == pygame.K_DOWN and hard_mode:  # Šipka dolů v HARD modu = hard drop
                        level = score // 1000 + 1       # Aktualizuje level
                        final_y = animated_hard_drop(   # Spustí animaci pádu
                            screen, current_piece, grid, block_size, offset_x, offset_y,
                            BG_COLOR, BORDER_COLOR, PANEL_COLOR, panel_x, panel_width,
                            score, lines, hard_mode, next_piece, level,
                            display_max_score, display_last_score)
                        current_piece.y = final_y       # Umístí na cílovou pozici
                        place_piece(current_piece, grid)  # Zapíše do mřížky

                        full_rows = [i for i, row in enumerate(grid) if all(cell != BLACK for cell in row)]
                        if full_rows:
                            line_clear_animation(       # Přehraje animaci mazání řádků
                                screen, full_rows, grid, block_size, offset_x, offset_y,
                                BG_COLOR, BORDER_COLOR, PANEL_COLOR, panel_x, panel_width,
                                score, lines, hard_mode, next_piece, level,
                                display_max_score, display_last_score)

                        cleared = clear_rows(grid)      # Smaže plné řádky
                        score  += cleared * 100         # Přičte body
                        lines  += cleared               # Přičte řádky
                        current_piece = next_piece      # Posune kostičky
                        next_piece    = new_piece()     # Vygeneruje novou

                        if not valid_space(current_piece, grid):    # Konec hry
                            game_over_save()
                            return

        if paused:      # Pokud je hra pozastavená, přeskočí veškerou herní logiku a kreslení
            continue    # Skočí na začátek while smyčky - pygame.event.get() stále zpracovává události

        # --- POHYB A GRAVITACE ---
        fall_time     += dt  # Přičte uplynulý čas k čítači pádu (v ms)
        move_cooldown += dt  # Přičte uplynulý čas k čítači prodlevy pohybu (v ms)

        keys = pygame.key.get_pressed()  # Vrátí aktuální stav VŠECH kláves jako pole True/False
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:     # Levá šipka NEBO klávesa A
            if move_cooldown > 120:                     # Pohyb jen pokud uplynulo více než 120ms (8x/s)
                current_piece.x -= 1                    # Posune kostičku o jeden sloupec doleva
                if not valid_space(current_piece, grid):  # Pokud nová pozice je kolize
                    current_piece.x += 1                # Vrátí zpět na původní pozici
                move_cooldown = 0                       # Resetuje čítač - čeká dalších 120ms
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:  # Pravá šipka NEBO klávesa D
            if move_cooldown > 120:
                current_piece.x += 1                    # Posune o jeden sloupec doprava
                if not valid_space(current_piece, grid):
                    current_piece.x -= 1                # Vrátí zpět
                move_cooldown = 0

        # Výpočet faktoru rychlosti pádu:
        # hard_mode: žádný soft drop (šipka dolů = hard drop, řešeno výše v events) = vždy 1.0
        # normal mode: šipka dolů nebo S = soft drop (10x rychlejší pád) = 0.1; jinak normální = 1.0
        speed_factor = 1.0 if hard_mode else (0.1 if keys[pygame.K_DOWN] or keys[pygame.K_s] else 1.0)

        # Automatický pád dolů (gravitace): pokud uplynul dostatečný čas
        # fall_time/1000 převede ms na sekundy; porovnává s fall_speed upravenou speed_factorem
        if fall_time / 1000 >= fall_speed * speed_factor:
            fall_time = 0               # Resetuje čítač pádu
            current_piece.y += 1       # Posune kostičku o jeden řádek dolů

            if not valid_space(current_piece, grid):    # Pokud po pádu nastala kolize
                current_piece.y -= 1                    # Vrátí jeden řádek nahoru (poslední platná pozice)
                place_piece(current_piece, grid)        # Zapíše kostičku natrvalo do mřížky

                full_rows = [i for i, row in enumerate(grid) if all(cell != BLACK for cell in row)]
                if full_rows:                           # Jsou-li plné řádky
                    line_clear_animation(               # Přehraje animaci záblesku
                        screen, full_rows, grid, block_size, offset_x, offset_y,
                        BG_COLOR, BORDER_COLOR, PANEL_COLOR, panel_x, panel_width,
                        score, lines, hard_mode, next_piece, level,
                        display_max_score, display_last_score)

                cleared = clear_rows(grid)  # Smaže plné řádky a vrátí jejich počet
                score  += cleared * 100     # Přičte body
                lines  += cleared           # Přičte smazané řádky
                current_piece = next_piece  # Posune kostičky
                next_piece    = new_piece() # Vygeneruje novou příští

                if not valid_space(current_piece, grid):  # Nová kostička nemá místo = konec hry
                    game_over_save()
                    return

        # Aktualizuje rychlost pádu s rostoucím skóre - každých 1000 bodů o 0.05s rychleji
        # max(0.1, ...) zabrání tomu aby se hra stala nehratelnou (minimální rychlost 0.1s/krok)
        fall_speed = max(0.1, (0.45 if hard_mode else 0.6) - (score // 1000) * 0.05)
        level = score // 1000 + 1  # Level = celé číslo (skóre/1000) + 1; začíná na 1, roste každých 1000 bodů

        # --- KRESLENÍ SNÍMKU ---
        screen.fill(BG_COLOR)   # Smaže celou obrazovku tmavým pozadím (přepíše předchozí snímek)

        # Nakreslí rámeček kolem hrací plochy
        border_rect = (offset_x - 3, offset_y - 3, board_width + 6, block_size * ROWS + 6)
        pygame.draw.rect(screen, BORDER_COLOR, border_rect, 3, border_radius=4)

        # Vytvoří dočasnou kopii mřížky pro kreslení (nechceme aktuální kostičku zapsat permanentně)
        temp_grid = [row[:] for row in grid]    # row[:] = mělká kopie každého řádku = nový seznam
        shape = current_piece.image()           # Načte tvar aktuální kostičky
        for i, row in enumerate(shape):
            for j, cell in enumerate(row):
                if cell:                        # Vyplněný blok kostičky
                    x = current_piece.x + j    # Absolutní X pozice
                    y = current_piece.y + i    # Absolutní Y pozice
                    if y >= 0:                  # Nekreslí bloky nad hrací plochou (nad y=0)
                        temp_grid[y][x] = current_piece.color  # Zapíše barvu do KOPIE mřížky

        # Nakreslí celou hrací plochu včetně aktuální kostičky (z dočasné kopie)
        for i in range(ROWS):
            for j in range(COLS):
                rect = (offset_x + j * block_size, offset_y + i * block_size, block_size, block_size)
                color = temp_grid[i][j]                 # Barva z kopie mřížky (obsahuje i aktuální kostičku)
                pygame.draw.rect(screen, color, rect)   # Vyplní políčko barvou
                if color != BLACK:                      # Obsazené políčko - přidá 3D okraj
                    light = (min(color[0] + 60, 255), min(color[1] + 60, 255), min(color[2] + 60, 255))
                    pygame.draw.rect(screen, light, rect, 2, border_radius=2)
                else:                                   # Prázdné políčko - jemná mřížka
                    pygame.draw.rect(screen, (30, 30, 50), rect, 1)

        # Nakreslí pravý informační panel se všemi statistikami a náhledem příští kostičky
        draw_panel(screen, BORDER_COLOR, PANEL_COLOR, panel_x, panel_width, offset_y,
                   block_size, hard_mode, score, lines, level,
                   next_piece, display_max_score, display_last_score)

        pygame.display.update()  # Zobrazí hotový snímek na obrazovce (flip = swap bufferů)


# ============================================================
# OBRAZOVKA PAUZY
# ============================================================

def draw_pause_screen(screen, width, height):
    """Nakreslí poloprůhledný tmavý overlay přes herní obrazovku s textem PAUZA."""
    # Vytvoří nový Surface stejné velikosti jako okno s podporou průhlednosti (SRCALPHA)
    overlay = pygame.Surface((width, height), pygame.SRCALPHA)
    # Vyplní overlay poloprůhlednou černou: (R, G, B, Alpha) - Alpha 160 = ~63% neprůhlednost
    overlay.fill((0, 0, 0, 160))
    screen.blit(overlay, (0, 0))    # Nakopíruje overlay přes celou herní obrazovku (ztmaví ji)

    draw_text(screen, "PAUZA", 54, WHITE, width // 2, height // 2 - 80)                    # Velký nadpis PAUZA uprostřed
    draw_text(screen, "ESC - pokračovat", 24, (180, 180, 180), width // 2, height // 2)    # Instrukce pod ním
    draw_text(screen, "M - zpět do menu", 24, (180, 180, 180), width // 2, height // 2 + 40)  # Další instrukce

    pygame.display.update()  # Zobrazí overlay na obrazovce


# ============================================================
# HLAVNÍ MENU
# ============================================================

def main_menu():
    """Zobrazí a řídí hlavní menu - navigaci mezi obrazovkami (menu, hra, žebříček, nastavení)."""
    current_res = 0         # Index aktuálně vybraného rozlišení v seznamu RESOLUTIONS (začíná na 0 = 480x800)
    fullscreen  = False     # Příznak celé obrazovky: False = okno, True = fullscreen
    width, height = RESOLUTIONS[current_res]    # Rozbalí tuple rozlišení do dvou proměnných

    screen = pygame.display.set_mode((width, height))   # Vytvoří pygame okno daného rozlišení
    pygame.display.set_caption("Tetris")                # Nastaví text v záhlaví okna
    clock = pygame.time.Clock()                         # Hodiny pro omezení FPS menu na 60
    state     = "menu"      # Aktuální stav: "menu" | "mode_select" | "leaderboard" | "settings" | "play"
    hard_mode = False       # Výchozí herní mód = normal

    cached_highscores  = {}     # Lokální cache žebříčku - data se nenačítají každý snímek
    leaderboard_loaded = False  # Příznak: False = data je třeba znovu načíst, True = data jsou v cache

    # Vnitřní funkce pro přepínání stavů - předávají se tlačítkům jako akce (callbacks)
    def start_game():
        nonlocal state          # nonlocal = chce měnit proměnnou z nadřazené funkce main_menu
        state = "mode_select"   # Přejde na obrazovku výběru módu

    def open_settings():
        nonlocal state
        state = "settings"      # Přejde do nastavení

    def open_leaderboard():
        nonlocal state, leaderboard_loaded
        state = "leaderboard"
        leaderboard_loaded = False  # Vynutí opětovné načtení dat ze souboru

    def go_back():
        nonlocal state
        state = "menu"          # Vrátí zpět do hlavního menu

    def quit_game():
        nonlocal running
        running = False         # Ukončí hlavní smyčku čistě - pygame.quit() se zavolá až na konci

    # --- HLAVNÍ SMYČKA MENU ---
    running = True
    while running:
        screen.fill(MENU_BG)    # Smaže obrazovku tmavou barvou pro nový snímek
        clock.tick(60)          # Omezí FPS na 60

        for event in pygame.event.get():    # Zpracuje všechny události
            if event.type == pygame.QUIT:   # Křížek okna = ukončit
                running = False             # Vyskočí z while smyčky, program se ukončí

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Klik levým tlačítkem
                mouse_pos = event.pos       # Pozice kliknutí jako (x, y)

                if state == "settings":     # Klik v nastavení - zpracovává se jinak (vlastní logika)
                    for i, res in enumerate(RESOLUTIONS):      # Prochází seznam rozlišení
                        rect_y = 270 + i * 40                  # Y pozice textu tohoto rozlišení
                        font  = pygame.font.SysFont("arial", 26, bold=True)
                        label = font.render(f"{res[0]}x{res[1]}", True, WHITE)
                        rect  = label.get_rect(center=(width // 2, rect_y))
                        if rect.collidepoint(mouse_pos):        # Hráč klikl na toto rozlišení
                            current_res = i                     # Uloží nový index rozlišení
                            width, height = RESOLUTIONS[current_res]  # Aktualizuje rozměry
                            flags  = pygame.FULLSCREEN if fullscreen else 0  # Zachová fullscreen stav
                            screen = pygame.display.set_mode((width, height), flags)  # Přizpůsobí okno
                            break                               # Přestane hledat další rozlišení

                    # Zpracuje klik na fullscreen přepínač
                    font  = pygame.font.SysFont("arial", 26, bold=True)
                    label = font.render("ZAP" if fullscreen else "VYP", True, WHITE)
                    rect  = label.get_rect(center=(width // 2, 460))
                    if rect.collidepoint(mouse_pos):            # Kliknutí na ZAP/VYP text
                        fullscreen = not fullscreen             # Přepne fullscreen stav
                        flags  = pygame.FULLSCREEN if fullscreen else 0
                        screen = pygame.display.set_mode((width, height), flags)

        # --- KRESLENÍ PODLE AKTUÁLNÍHO STAVU ---

        if state == "menu":     # Hlavní menu
            draw_text(screen, "TETRIS", 54, WHITE, width // 2, 150)                              # Nadpis
            button(screen, "HRÁT",      width // 2 - 90, 280, 180, 60, start_game)              # Tlačítko Hrát
            button(screen, "ŽEBŘÍČEK", width // 2 - 90, 360, 180, 60, open_leaderboard)         # Žebříček
            button(screen, "NASTAVENÍ", width // 2 - 90, 440, 180, 60, open_settings)           # Nastavení
            button(screen, "KONEC",     width // 2 - 90, 520, 180, 60, quit_game)             # Konec

        elif state == "mode_select":    # Výběr herního módu
            draw_text(screen, "VYBER MÓD", 42, WHITE, width // 2, 150)  # Nadpis

            # Tlačítko NORMAL - zelené pozadí (50, 150, 50)
            pygame.draw.rect(screen, (50, 150, 50), (width // 2 - 110, 260, 220, 80), border_radius=12)
            draw_text(screen, "NORMAL", 28, WHITE, width // 2, 290)                             # Název módu
            draw_text(screen, "Klasická hra, soft drop", 16, (180, 255, 180), width // 2, 318)  # Popis

            # Tlačítko HARD - červené pozadí (180, 50, 50)
            pygame.draw.rect(screen, (180, 50, 50), (width // 2 - 110, 380, 220, 80), border_radius=12)
            draw_text(screen, "HARD", 28, WHITE, width // 2, 410)                               # Název módu
            draw_text(screen, "Rychlejší, hard drop mezerník", 16, (255, 180, 180), width // 2, 438)  # Popis

            button(screen, "ZPĚT", width // 2 - 80, 500, 160, 50, go_back)  # Tlačítko zpět do menu

            mouse = pygame.mouse.get_pos()      # Aktuální pozice myši
            if pygame.mouse.get_pressed()[0]:   # Levé tlačítko myši je stisknuto
                # Zkontroluje klik na oblast tlačítka NORMAL (Y: 260-340)
                if (width // 2 - 110 < mouse[0] < width // 2 + 110) and (260 < mouse[1] < 340):
                    hard_mode = False           # Nastaví normal mód
                    pygame.time.wait(150)       # Krátká pauza - zabrání dvojitému kliknutí
                    state = "play"              # Přejde do hry
                # Zkontroluje klik na oblast tlačítka HARD (Y: 380-460)
                elif (width // 2 - 110 < mouse[0] < width // 2 + 110) and (380 < mouse[1] < 460):
                    hard_mode = True            # Nastaví hard mód
                    pygame.time.wait(150)
                    state = "play"              # Přejde do hry

        elif state == "leaderboard":    # Žebříček
            if not leaderboard_loaded:              # Načte data pouze jednou (ne každý snímek)
                cached_highscores  = load_highscores()  # Načte slovník ze souboru
                leaderboard_loaded = True           # Označí jako načteno

            draw_text(screen, "ŽEBŘÍČEK", 42, WHITE, width // 2, 80)  # Nadpis

            # Odfiltruje speciální klíče začínající __ (jako __last_score__) - zobrazí jen hráče
            player_scores = {k: v for k, v in cached_highscores.items() if not k.startswith("__")}

            if player_scores:   # Jsou-li nějaká data k zobrazení
                # Seřadí hráče sestupně podle skóre (nejvyšší první)
                # key=lambda x: x[1] = řadí podle hodnoty (skóre), ne klíče (jména)
                sorted_scores = sorted(player_scores.items(), key=lambda x: x[1], reverse=True)

                start_y     = 180   # Y pozice prvního řádku tabulky
                row_height  = 50    # Výška jednoho řádku tabulky v pixelech
                max_visible = min(10, len(sorted_scores))   # Zobrazí max 10 hráčů (nebo méně pokud jich není dost)

                # Nadpisy sloupců - světle šedá barva
                draw_text(screen, "Pořadí", 24, (200, 200, 200), width // 2 - 120, start_y - 40)
                draw_text(screen, "Jméno",  24, (200, 200, 200), width // 2,        start_y - 40)
                draw_text(screen, "Skóre",  24, (200, 200, 200), width // 2 + 120,  start_y - 40)

                for i, (name, sc) in enumerate(sorted_scores[:max_visible]):  # Prochází max 10 hráčů
                    y_pos = start_y + i * row_height    # Y pozice tohoto řádku
                    if i % 2 == 0:                      # Sudé řádky (0, 2, 4...) dostanou tmavší pozadí
                        pygame.draw.rect(screen, (40, 40, 40),
                                         (width // 2 - 200, y_pos - 18, 400, row_height - 5),
                                         border_radius=5)
                    draw_text(screen, f"#{i + 1}", 26, WHITE, width // 2 - 120, y_pos)  # Pořadí (#1, #2...)
                    draw_text(screen, name,        26, WHITE, width // 2,        y_pos)  # Jméno hráče
                    draw_text(screen, str(sc),     26, WHITE, width // 2 + 120,  y_pos)  # Skóre

                if len(sorted_scores) > max_visible:    # Pokud je více hráčů než zobrazujeme
                    draw_text(screen, f"... a dalších {len(sorted_scores) - max_visible} hráčů",
                              18, (150, 150, 150), width // 2,
                              start_y + max_visible * row_height + 20)  # Informace pod tabulkou
            else:
                # Žádná data - zobrazí motivační zprávu
                draw_text(screen, "Zatím žádné skóre!", 28, (150, 150, 150), width // 2, height // 2 - 50)
                draw_text(screen, "Zahraj si hru a staň se prvním!", 20, (100, 100, 100), width // 2, height // 2)

            button(screen, "ZPĚT", width // 2 - 80, height - 100, 160, 50, go_back)  # Tlačítko zpět

        elif state == "settings":       # Nastavení
            draw_text(screen, "NASTAVENÍ", 42, WHITE, width // 2, 120)     # Nadpis
            draw_text(screen, "Rozlišení:", 28, WHITE, width // 2, 220)    # Popisek sekce

            for i, res in enumerate(RESOLUTIONS):   # Prochází dostupná rozlišení
                # Aktivní rozlišení je bílé, ostatní šedá
                color = WHITE if i == current_res else (180, 180, 180)
                draw_text(screen, f"{res[0]}x{res[1]}", 26, color, width // 2, 270 + i * 40)

            draw_text(screen, "Fullscreen:", 28, WHITE, width // 2, 420)   # Popisek
            fs_color = (0, 255, 0) if fullscreen else (200, 80, 80)        # Zelená = ZAP, červená = VYP
            draw_text(screen, "ZAP" if fullscreen else "VYP", 26, fs_color, width // 2, 460)

            button(screen, "ZPĚT", width // 2 - 80, 550, 160, 50, go_back)  # Tlačítko zpět

        pygame.display.update()     # Zobrazí nakreslený snímek (flip)

        if state == "play":         # Pokud byl vybrán herní stav
            play_game(screen, width, height, fullscreen, hard_mode)  # Spustí celou hru (blokující volání)
            state = "menu"          # Po návratu z hry se automaticky vrátí do menu
            # Vyčistíme event frontu a počkáme na uvolnění myši -
            # zabrání tomu aby klik z "Zpět do menu" okamžitě spustil tlačítko v hlavním menu
            pygame.event.clear()
            while pygame.mouse.get_pressed()[0]:
                pygame.event.pump()
                pygame.time.wait(10)

    pygame.quit()   # Ukončí pygame - uvolní paměť, zavře okno, ukončí audio


# ============================================================
# TESTY - spustí se příkazem: python tetris.py test
# Testují herní logiku bez spuštění pygame okna
# ============================================================

def test_clear_rows():
    """Test funkce clear_rows - ověří že plné řádky se smažou a mřížka zůstane správně velká."""

    # Vytvoříme prázdnou mřížku (stejně jako na začátku hry)
    grid = [[BLACK for _ in range(COLS)] for _ in range(ROWS)]

    # Poslední dva řádky vyplníme nějakou barvou (simulujeme plné řádky)
    NECO = (255, 0, 0)  # Červená - cokoliv jiného než BLACK
    grid[18] = [NECO for _ in range(COLS)]  # Předposlední řádek - plný
    grid[19] = [NECO for _ in range(COLS)]  # Poslední řádek - plný

    pocet = clear_rows(grid)  # Zavoláme testovanou funkci

    # Ověříme že funkce vrátila správný počet smazaných řádků
    assert pocet == 2, f"CHYBA: Očekávány 2 smazané řádky, dostali jsme {pocet}"
    # Ověříme že řádky jsou nyní prázdné (černé)
    assert grid[18] == [BLACK] * COLS, "CHYBA: Řádek 18 není prázdný po smazání"
    assert grid[19] == [BLACK] * COLS, "CHYBA: Řádek 19 není prázdný po smazání"
    # Ověříme že mřížka má stále správný počet řádků (insert přidal nové nahoře)
    assert len(grid) == ROWS, f"CHYBA: Mřížka má {len(grid)} řádků místo {ROWS}"

    print("✓ TEST 1 PROBĚHL V POŘÁDKU - clear_rows správně smaže 2 plné řádky")


def test_get_max_score():
    """Test funkce get_max_score - ověří správné maximum a ignorování speciálních klíčů."""

    # Simulujeme slovník highscores jako v souboru JSON
    scores = {
        "Honza": 500,
        "Pepa": 1200,
        "Marek": 800,
        "__last_score__": 9999,  # Tento klíč se NESMÍ počítat jako hráčovo skóre
    }

    maximum = get_max_score(scores)

    # Ověříme že maximum je 1200 (Pepa) a ne 9999 (__last_score__)
    assert maximum == 1200, f"CHYBA: Očekáváno maximum 1200, dostali jsme {maximum}"
    assert maximum != 9999, "CHYBA: get_max_score zahrnul speciální klíč __last_score__"

    # Test s prázdným slovníkem - nesmí spadnout, musí vrátit 0
    prazdny = get_max_score({})
    assert prazdny == 0, f"CHYBA: Pro prázdný slovník očekáváno 0, dostali jsme {prazdny}"

    print("✓ TEST 2 PROBĚHL V POŘÁDKU - get_max_score vrátí správné maximum a ignoruje __last_score__")


def spust_testy():
    """Spustí všechny testy a vypíše výsledky do terminálu."""
    print("=" * 55)
    print("   SPOUŠTÍM TESTY...")
    print("=" * 55)

    chyba = False  # Příznak - True pokud nějaký test selhal

    try:
        test_clear_rows()
    except AssertionError as e:  # AssertionError = assert podmínka nebyla splněna
        print(f"✗ TEST 1 SELHAL: {e}")
        chyba = True

    try:
        test_get_max_score()
    except AssertionError as e:
        print(f"✗ TEST 2 SELHAL: {e}")
        chyba = True

    print("=" * 55)
    if not chyba:
        print("   VŠECHNY TESTY PROŠLY!")
    else:
        print("   NĚKTERÉ TESTY SELHALY!")
    print("=" * 55)


# ============================================================
# VSTUPNÍ BOD PROGRAMU
# ============================================================

# Tato podmínka je True pouze pokud spouštíme tento soubor přímo (python tetris.py)
# Při importu jako modul (import tetris) se main_menu() NESPUSTÍ
if __name__ == "__main__":
    # Pokud byl jako argument předán "test", spustí testy místo hry
    # sys.argv je seznam argumentů příkazové řádky: sys.argv[0] = název souboru, sys.argv[1] = první argument
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        spust_testy()   # Spustí testy - nevyžaduje pygame okno
    else:
        main_menu()     # Spustí hlavní menu - zde začíná celý program
