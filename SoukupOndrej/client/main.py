import math                         # Importuje matematické funkce, například sinus, který se hodí pro pohyby a animace.
import os                           # Umožňuje pracovat se soubory a cestami k nim.
import sys                          # Umožňuje komunikaci se systémem, například ukončení programu.
import time                         # Slouží k měření času mezi snímky hry.
import random                       # Umožňuje generovat náhodná čísla.
from dataclasses import dataclass   # Umožní jednoduše vytvářet třídy, které jen drží data.
from typing import List             # Říká, že některé proměnné budou seznamy určitého typu.

import pygame                       # Hlavní knihovna pro tvorbu hry, grafiku, zvuk, vstupy z klávesnice atd.
import requests                     # Knihovna pro komunikaci se serverem přes internet / HTTP.

WIDTH, HEIGHT = 420, 640            # Nastaví šířku a výšku herního okna.
GROUND_H = 70                       # Výška země ve spodní části obrazovky.
FPS = 60                            # Počet snímků za sekundu, o který se hra snaží.
API_BASE = "http://127.0.0.1:5000"  # Adresa lokálního serveru, kam se posílá login a skóre.
BOOST_DURATION = 5.0                # Jak dlouho trvá aktivní boost po sebrání.
DIFF = {                            # Slovník s nastavením obtížností.
    "easy":   {"label": "Easy",   "gap": 230, "speed": 2.35, "spacing": 300, "gravity": 0.36, "flap": -6.7},   # Lehká obtížnost: velká mezera, nižší rychlost.
    "normal": {"label": "Normal", "gap": 180, "speed": 2.70, "spacing": 270, "gravity": 0.40, "flap": -7.2},   # Normální obtížnost.
    "hard":   {"label": "Hard",   "gap": 142, "speed": 3.10, "spacing": 212, "gravity": 0.44, "flap": -7.6},   # Těžší obtížnost: menší mezery a rychlejší hra.
    "insane": {"label": "Insane", "gap": 124, "speed": 3.55, "spacing": 212, "gravity": 0.48, "flap": -7.9},   # Extrémní obtížnost.
}                                   # gap = mezera mezi trubkami, speed = rychlost, spacing = vzdálenost trubek, gravity = gravitace, flap = síla skoku.


def clamp(v, a, b):                 # Funkce omezí hodnotu v do intervalu od a do b.
    return max(a, min(b, v))        # Když je v moc malé, vrátí a. Když moc velké, vrátí b. Jinak vrátí v.


def lerp(a, b, t):                  # Funkce pro plynulý přechod mezi dvěma hodnotami.
    return a + (b - a) * t          # Vrací číslo mezi a a b podle poměru t.


def circle_rect_collide(cx, cy, cr, rx, ry, rw, rh) -> bool:   # Zjistí, jestli se kruh (pták) dotýká obdélníku (trubka).
    closest_x = clamp(cx, rx, rx + rw)                         # Najde nejbližší X bod obdélníku ke středu kruhu.
    closest_y = clamp(cy, ry, ry + rh)                         # Najde nejbližší Y bod obdélníku ke středu kruhu.
    dx = cx - closest_x                                        # Vzdálenost středu kruhu od nejbližšího bodu v ose X.
    dy = cy - closest_y                                        # Vzdálenost středu kruhu od nejbližšího bodu v ose Y.
    return (dx * dx + dy * dy) < (cr * cr)                     # Pokud je vzdálenost menší než poloměr kruhu, došlo ke kolizi.


def try_get_json(url, timeout=0.6):                            # Pokusí se stáhnout JSON data ze serveru.
    try:                                                       # Začne blok, který zkouší provést kód a zachytit případnou chybu.
        r = requests.get(url, timeout=timeout)                 # Odešle GET požadavek na server.
        if r.ok:                                               # Pokud server odpověděl úspěšně (například kódem 200).
            return r.json()                                    # Vrátí odpověď převedenou na JSON.
    except Exception:                                          # Když nastane jakákoli chyba (server neběží, timeout...).
        return None                                            # Vrátí None místo pádu programu.
    return None                                                # Když server nevrátil správnou odpověď, vrátí None.


def post_json(url, payload, timeout=1.2):                      # Odešle data na server metodou POST.
    r = requests.post(url, json=payload, timeout=timeout)      # Pošle JSON data na danou adresu.
    r.raise_for_status()                                       # Pokud server vrátí chybu, vyhodí výjimku.
    return r.json()                                            # Vrátí odpověď serveru jako JSON.


def try_login(username, password):                             # Funkce pro pokus o přihlášení uživatele.
    try:                                                       # Zkusí provést přihlášení bez pádu programu při chybě.
        return post_json(                                      # Zavolá pomocnou funkci pro odeslání dat na server.
            f"{API_BASE}/api/login",                           # URL adresa endpointu pro login.
            {"username": username, "password": password},      # Do serveru se pošle jméno a heslo.
            timeout=1.2,                                       # Maximální čekání na odpověď 1.2 sekundy.
        )
    except Exception:                                          # Pokud se něco pokazí.
        return None                                            # Vrátí None.


def try_register(username, password):                          # Funkce pro registraci nového účtu.
    try:                                                       # Zkusí registraci.
        return post_json(                                      # Pošle data na server.
            f"{API_BASE}/api/register",                        # URL adresa endpointu pro registraci.
            {"username": username, "password": password},      # Odeslané registrační údaje.
            timeout=1.2,                                       # Limit čekání na server.
        )
    except Exception:                                          # Když dojde k chybě.
        return None                                            # Vrátí None místo pádu.


@dataclass                                                    # Označí, že následující třída je datová třída.
class Pipe:                                                   # Třída reprezentuje jednu trubku.
    x: float                                                  # Vodorovná pozice trubky.
    gap_y: float                                              # Svislá pozice středu mezery mezi horní a spodní trubkou.
    passed: bool = False                                      # Informace, jestli už pták trubku proletěl a dostal za ni bod.


@dataclass                                                    # Datová třída.
class Particle:                                               # Třída pro jednu částici efektu.
    x: float                                                  # X souřadnice částice.
    y: float                                                  # Y souřadnice částice.
    vx: float                                                 # Rychlost částice v ose X.
    vy: float                                                 # Rychlost částice v ose Y.
    life: float                                               # Jak dlouho částice ještě existuje.


@dataclass                                                    # Datová třída.
class Cloud:                                                  # Třída pro oblak na pozadí.
    x: float                                                  # X pozice oblaku.
    y: float                                                  # Y pozice oblaku.
    s: float                                                  # Velikost oblaku (scale).
    v: float                                                  # Rychlost pohybu oblaku.

@dataclass                                                   # Datová třída.
class Boost:                                                 # Třída reprezentuje jeden boost.
    x: float          # X pozice boostu                      # Vodorovná pozice boostu.
    y: float          # Y pozice boostu                      # Svislá pozice boostu.
    active: bool = True  # jestli je boost ještě na mapě    # Určuje, zda je boost stále aktivní a může sebrat.

class Button:                                                 # Třída pro tlačítko v menu.
    def __init__(self, rect: pygame.Rect, text: str):         # Konstruktor tlačítka, zavolá se při vytvoření objektu.
        self.rect = rect                                      # Uloží obdélník určující polohu a velikost tlačítka.
        self.text = text                                      # Uloží text, který bude na tlačítku.

    def hit(self, pos):                                       # Funkce zjistí, jestli bylo kliknuto do tlačítka.
        return self.rect.collidepoint(pos)                    # Vrací True, pokud bod myši leží uvnitř obdélníku tlačítka.

    def draw(self, surf, font, active=False):                 # Funkce vykreslí tlačítko na plochu.
        bg = (0, 0, 0, 70) if not active else (0, 180, 160, 90)      # Barva pozadí podle toho, zda je tlačítko aktivní.
        border = (255, 255, 255, 35) if not active else (0, 255, 213, 90)  # Barva rámečku podle aktivního stavu.
        pygame.draw.rect(surf, bg, self.rect, border_radius=14)      # Nakreslí tělo tlačítka jako zaoblený obdélník.
        pygame.draw.rect(surf, border, self.rect, width=2, border_radius=14) # Nakreslí obrys tlačítka.
        t = font.render(self.text, True, (233, 240, 255))            # Vyrenderuje text tlačítka jako obrázek.
        surf.blit(t, t.get_rect(center=self.rect.center))            # Nakreslí text doprostřed tlačítka.


def main():                                                   # Hlavní funkce celé hry.
    pygame.init()                                             # Spustí a inicializuje knihovnu pygame.
    pygame.display.set_caption("Flappy Bird – Python (pygame) + DB")  # Nastaví název okna hry.
    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.DOUBLEBUF)  # Vytvoří okno hry se zadanou velikostí.
    clock = pygame.time.Clock()                               # Objekt pro řízení rychlosti hry (FPS).

    font_big = pygame.font.SysFont("Segoe UI", 22, bold=True) # Vytvoří větší tučné písmo.
    font = pygame.font.SysFont("Segoe UI", 16, bold=True)     # Vytvoří střední tučné písmo.
    font_small = pygame.font.SysFont("Segoe UI", 13)          # Vytvoří malé písmo.

    best_path = os.path.join(os.path.dirname(__file__), "best.txt")  # Sestaví cestu k souboru s nejlepším skóre.
    best = 0                                                  # Výchozí nejlepší skóre je 0.
    try:                                                      # Pokusí se načíst uložené nejlepší skóre ze souboru.
        if os.path.exists(best_path):                         # Pokud soubor opravdu existuje.
            best = int(open(best_path, "r", encoding="utf-8").read().strip() or "0")  # Přečte číslo ze souboru a převede ho na int.
    except Exception:                                         # Pokud se čtení nepovede.
        best = 0                                              # Nastaví nejlepší skóre na 0.

    state = "login"  # login | register | menu | ready | playing | paused | gameover | leaderboard
    difficulty = "normal"                                     # Výchozí obtížnost je nastavena na normal.
    server_ok = False                                         # Na začátku nevíme, jestli běží server.

    logged_in_user = ""                                       # Uloží jméno přihlášeného uživatele.
    login_username = ""                                       # Text napsaný do pole uživatelského jména.
    login_password = ""                                       # Text napsaný do pole hesla.
    login_message = ""                                        # Informační zpráva v login panelu.
    login_field = "username"                                  # Určuje, které pole je právě aktivní.

    world_time = 0.0                                          # Celkový čas běhu hry.
    scroll = 0.0                                              # Posun světa pro pohyb pozadí.
    score = 0                                                 # Aktuální skóre hráče.
    speed_mul = 1.0                                           # Násobitel rychlosti hry.
    shake = 0.0                                               # Síla otřesu obrazovky.

    bird_x = 140.0                                            # X pozice ptáka.
    bird_y = 240.0                                            # Y pozice ptáka.
    bird_vy = 0.0                                             # Vertikální rychlost ptáka.
    bird_r = 16                                               # Poloměr ptáka pro výpočet kolizí.
    bird_rot = 0.0                                            # Natočení ptáka.
    flap_cd = 0.0                                             # Cooldown mezi skoky, aby nešlo klikat moc rychle.

    pipes: List[Pipe] = []  # seznam trubek                   # Seznam všech trubek ve hře.
    particles: List[Particle] = []  # částice (efekty)        # Seznam částic pro vizuální efekty.
    clouds: List[Cloud] = []  # mraky na pozadí               # Seznam mraků v pozadí.
    boosts: List[Boost] = []  # seznam boostů ve hře          # Seznam boost předmětů.

    boost_timer = 0.0  # čas do dalšího spawnu boostu         # Odpočítávání do vytvoření dalšího boostu.
    boost_active_time = 0.0  # kolik sekund ještě trvá aktivní boost  # Čas, po který ještě boost působí.

    btn_start = Button(pygame.Rect(24, 470, 180, 46), "▶ Start")      # Tlačítko pro spuštění hry.
    btn_lb = Button(pygame.Rect(216, 470, 180, 46), "🏆 Žebříček")     # Tlačítko pro zobrazení žebříčku.
    btn_logout = Button(pygame.Rect(24, 524, 372, 42), "Odhlásit")     # Tlačítko pro odhlášení.
    btn_continue = Button(pygame.Rect(120, 300, 180, 44), "Continue")  # Tlačítko pro pokračování z pauzy.
    btn_menu_pause = Button(pygame.Rect(120, 354, 180, 44), "Menu")    # Tlačítko pro návrat do menu z pauzy.
    diff_rects = {                                            # Slovník oblastí pro výběr obtížnosti.
        "easy": pygame.Rect(24, 290, 372, 36),                # Klikací oblast obtížnosti easy.
        "normal": pygame.Rect(24, 332, 372, 36),              # Klikací oblast obtížnosti normal.
        "hard": pygame.Rect(24, 374, 372, 36),                # Klikací oblast obtížnosti hard.
        "insane": pygame.Rect(24, 416, 372, 36),              # Klikací oblast obtížnosti insane.
    }

    lb_items = []                                             # Seznam položek žebříčku.
    lb_note = ""                                              # Poznámka u žebříčku (například Načítám...).

    def save_best():                                          # Pomocná funkce uloží nejlepší skóre do souboru.
        try:                                                  # Zkusí zapisovat do souboru.
            with open(best_path, "w", encoding="utf-8") as f: # Otevře soubor pro zápis.
                f.write(str(best))                            # Zapíše nejlepší skóre jako text.
        except Exception:                                     # Pokud se nepodaří zapisovat.
            pass                                              # Neudělá nic, hra nespadne.

    def make_clouds():                                        # Vytvoří seznam mraků do pozadí.
        arr = []                                              # Připraví prázdný seznam.
        for _ in range(8):                                    # Vytvoří 8 mraků.
            arr.append(                                       # Přidá nový mrak do seznamu.
                Cloud(                                        # Vytvoří objekt Cloud.
                    x=random.random() * WIDTH,                # Náhodná X pozice po šířce obrazovky.
                    y=40 + random.random() * 220,             # Náhodná Y pozice v horní části obrazovky.
                    s=0.6 + random.random() * 1.2,            # Náhodná velikost oblaku.
                    v=0.25 + random.random() * 0.45,          # Náhodná rychlost pohybu oblaku.
                )
            )
        return arr                                            # Vrátí hotový seznam mraků.

    def spawn_pipe(x):                                        # Funkce vytvoří novou trubku na dané X pozici.
        cfg = DIFF[difficulty]                                # Načte parametry aktuální obtížnosti.
        margin = 90                                           # Okraj, aby mezera nebyla moc nahoře ani moc dole.
        gap_y = margin + random.random() * (HEIGHT - GROUND_H - margin * 2)  # Náhodně určí výšku středu mezery.
        pipes.append(Pipe(x=x, gap_y=gap_y))                  # Přidá vytvořenou trubku do seznamu trubek.

    def spawn_boost(x, gap_y):                                # Funkce vytvoří boost uvnitř mezery mezi trubkami.
        offset = random.uniform(-24, 24)  # malý náhodný posun uvnitř mezery
        y = gap_y + offset  # boost bude bezpečně mezi trubkami

        boosts.append(Boost(x=x, y=y))  # vytvoří boost

    def reset_game():                                         # Funkce vrátí hru do výchozího stavu.
        nonlocal world_time, scroll, score, speed_mul, shake  # Říká, že budeme měnit proměnné z nadřazené funkce main.
        nonlocal bird_x, bird_y, bird_vy, bird_rot, flap_cd   # Totéž pro proměnné ptáka.
        nonlocal pipes, particles, clouds, boosts             # Totéž pro seznamy objektů.
        nonlocal boost_timer, boost_active_time               # Totéž pro boost proměnné.

        world_time = 0.0                                      # Vynuluje čas hry.
        scroll = 0.0                                          # Vynuluje posun pozadí.
        score = 0                                             # Vynuluje skóre.
        speed_mul = 1.0                                       # Nastaví rychlost na normální hodnotu.
        shake = 0.0                                           # Vypne otřes obrazovky.

        bird_x = 140.0                                        # Vrátí ptáka na startovní X pozici.
        bird_y = 240.0                                        # Vrátí ptáka na startovní Y pozici.
        bird_vy = 0.0                                         # Zastaví jeho vertikální pohyb.
        bird_rot = 0.0                                        # Narovná natočení ptáka.
        flap_cd = 0.0                                         # Vynuluje cooldown skoku.

        pipes = []  # smaže všechny trubky                    # Odstraní všechny staré trubky.
        particles = []  # smaže částice                       # Odstraní všechny částice.
        clouds = make_clouds()  # vytvoří nové mraky          # Vygeneruje nové mraky do pozadí.
        boosts = []  # smaže všechny boosty                   # Smaže všechny boosty.

        boost_timer = 0.0  # reset timeru boostu              # Resetuje časovač pro další boost.
        boost_active_time = 0.0  # vypne aktivní boost        # Vypne efekt boostu.

        cfg = DIFF[difficulty]                                # Načte aktuální nastavení obtížnosti.
        spawn_pipe(WIDTH + 120)                               # Vytvoří první trubku mimo pravý okraj.
        spawn_pipe(WIDTH + 120 + cfg["spacing"])              # Vytvoří druhou trubku.
        spawn_pipe(WIDTH + 120 + cfg["spacing"] * 2)          # Vytvoří třetí trubku.

    def flap():                                               # Funkce skoku ptáka.
        nonlocal bird_vy, flap_cd                             # Budeme měnit rychlost ptáka a cooldown.
        if state not in ("playing", "ready"):                 # Pokud hra není ve stavu hraní nebo připraveno.
            return                                            # Tak se skok neprovede.
        if flap_cd > 0:                                       # Pokud ještě běží cooldown mezi skoky.
            return                                            # Tak také neudělá další skok.
        cfg = DIFF[difficulty]                                # Načte parametry aktuální obtížnosti.
        bird_vy = cfg["flap"]                                 # Nastaví ptákovi zápornou rychlost, takže letí nahoru.
        flap_cd = 0.08                                        # Nastaví krátkou prodlevu do dalšího skoku.

        for _ in range(10):                                   # Vytvoří 10 částic efektu za ptákem.
            particles.append(                                 # Přidá novou částici do seznamu.
                Particle(                                     # Vytvoří objekt částice.
                    x=bird_x - 10,                            # Začne trochu za ptákem.
                    y=bird_y + (random.random() * 10 - 5),    # Náhodná výška kolem ptáka.
                    vx=-(1.2 + random.random() * 1.6),        # Částice letí doleva.
                    vy=(random.random() * 1.8 - 0.9),         # Může trochu nahoru nebo dolů.
                    life=0.45 + random.random() * 0.25,       # Nastaví, jak dlouho částice vydrží.
                )
            )

    def start_game():                                         # Funkce přepne hru do aktivního hraní.
        nonlocal state                                        # Budeme měnit proměnnou state.
        state = "playing"                                     # Změní stav na hraní.
        flap()                                                # Hned při startu udělá pták první skok.

    def do_game_over():                                       # Funkce, co se provede při prohře.
        nonlocal state, shake, best                           # Budeme měnit stav hry, otřes a nejlepší skóre.
        state = "gameover"                                    # Přepne hru do stavu game over.
        shake = 10.0                                          # Spustí otřes obrazovky.

        if score > best:                                      # Pokud je aktuální skóre větší než dosavadní rekord.
            best = score                                      # Uloží nové nejlepší skóre.
            save_best()                                       # Zapíše nové nejlepší skóre do souboru.

        for _ in range(40):                                   # Vytvoří 40 částic výbuchu.
            particles.append(                                 # Přidá částici do seznamu.
                Particle(                                     # Vytvoří novou částici.
                    x=bird_x,                                 # Začne na pozici ptáka.
                    y=bird_y,                                 # Začne na pozici ptáka.
                    vx=(random.random() * 3 - 1.5),           # Náhodný pohyb doleva nebo doprava.
                    vy=(random.random() * 3 - 1.5),           # Náhodný pohyb nahoru nebo dolů.
                    life=0.6 + random.random() * 0.4,         # Délka života částice.
                )
            )

    def collide() -> bool:                                    # Funkce zkontroluje kolizi a vrátí True/False.
        cfg = DIFF[difficulty]                                # Načte obtížnost.
        pipe_w = 70                                           # Šířka jedné trubky.
        ground_y = HEIGHT - GROUND_H                          # Y souřadnice horní hrany země.

        if bird_y + bird_r > ground_y or bird_y - bird_r < 0: # Když pták narazí do země nebo do horního okraje obrazovky.
            return True                                       # Vrátí True = kolize.

        for p in pipes:                                       # Projde všechny trubky.
            top_h = p.gap_y - cfg["gap"] / 2                  # Spočítá výšku horní trubky.
            bottom_y = p.gap_y + cfg["gap"] / 2               # Spočítá začátek spodní trubky.

            if circle_rect_collide(bird_x, bird_y, bird_r, p.x, 0, pipe_w, top_h):  # Kontrola kolize s horní trubkou.
                return True                                   # Pokud ano, vrátí True.
            if circle_rect_collide(                           # Kontrola kolize se spodní trubkou.
                bird_x, bird_y, bird_r, p.x, bottom_y, pipe_w, ground_y - bottom_y
            ):
                return True                                   # Pokud ano, vrátí True.
        return False                                          # Pokud nic nenarazilo, vrátí False.

    def collect_boosts():                                     # Funkce zkontroluje, jestli pták sebral nějaký boost.
        nonlocal boost_active_time                            # Budeme měnit čas aktivního boostu.

        for b in boosts:                                      # Projde všechny boosty.
            if not b.active:                                  # Pokud už boost není aktivní.
                continue                                      # Přeskočí ho.

            dx = bird_x - b.x                                 # Rozdíl X mezi ptákem a boostem.
            dy = bird_y - b.y                                 # Rozdíl Y mezi ptákem a boostem.
            rr = bird_r + 11                                  # Poloměr kolize = velikost ptáka + velikost boostu.

            if (dx * dx + dy * dy) < (rr * rr):               # Pokud je vzdálenost dost malá, pták boost sebral.
                b.active = False                              # Boost zmizí z mapy.
                boost_active_time = BOOST_DURATION            # Aktivuje boost na plnou délku.

                for _ in range(18):                           # Vytvoří efektní částice při sebrání boostu.
                    particles.append(
                        Particle(
                            x=b.x,                            # Částice začíná na pozici boostu.
                            y=b.y,                            # Částice začíná na pozici boostu.
                            vx=(random.random() * 3.0 - 1.5),# Náhodná vodorovná rychlost.
                            vy=(random.random() * 3.0 - 1.5),# Náhodná svislá rychlost.
                            life=0.45 + random.random() * 0.35,  # Náhodná délka života částice.
                        )
                    )

    def refresh_leaderboard(diff):                            # Funkce načte žebříček ze serveru.
        nonlocal lb_items, lb_note                            # Budeme měnit seznam položek a poznámku.
        lb_items = []                                         # Smaže starý seznam žebříčku.
        lb_note = "Načítám…"                                  # Nastaví dočasnou zprávu.
        j = try_get_json(f"{API_BASE}/api/scores?difficulty={diff}&limit=10", timeout=0.8)  # Pokusí se načíst top 10.
        if not j:                                             # Pokud server neodpověděl nebo nastala chyba.
            lb_note = "Server/DB nedostupné. Spusť nejdřív: python server/app.py"  # Zobrazí informaci o chybě.
            return                                            # Ukončí funkci.
        items = j.get("items", []) or []                      # Vytáhne pole položek z JSON odpovědi.
        lb_items = items                                      # Uloží položky do seznamu.
        lb_note = f"{DIFF[diff]['label']} — top {len(items)}" if items else "Zatím žádné záznamy."  # Nastaví horní text.

    def submit_login(mode):                                   # Funkce zpracuje login nebo registraci.
        nonlocal logged_in_user, login_message, state         # Budeme měnit uživatele, zprávu a stav hry.

        username = login_username.strip()                     # Odstraní mezery z obou stran uživatelského jména.
        password = login_password.strip()                     # Odstraní mezery z obou stran hesla.

        if len(username) < 3:                                 # Pokud je jméno kratší než 3 znaky.
            login_message = "Chyba: jméno je moc krátké"      # Ukáže chybovou zprávu.
            return                                            # Ukončí funkci.
        if len(password) < 4:                                 # Pokud je heslo kratší než 4 znaky.
            login_message = "Chyba: heslo je moc krátké"      # Ukáže chybovou zprávu.
            return                                            # Ukončí funkci.

        if mode == "login":                                   # Pokud se jedná o přihlášení.
            result = try_login(username, password)            # Zkusí se přihlásit přes server.
            if result and result.get("ok"):                   # Pokud server odpověděl úspěšně.
                logged_in_user = result["username"]           # Uloží přihlášeného uživatele.
                login_message = "Přihlášení úspěšné"          # Zobrazí úspěšnou zprávu.
                state = "menu"                                # Přepne do hlavního menu.
            else:                                             # Pokud přihlášení nevyšlo.
                login_message = "Chyba: přihlášení se nepovedlo"  # Zobrazí chybu.
        else:                                                 # Jinak se jedná o registraci.
            result = try_register(username, password)         # Zkusí registraci na serveru.
            if result and result.get("ok"):                   # Pokud registrace proběhla úspěšně.
                logged_in_user = result["username"]           # Uloží jméno nově registrovaného uživatele.
                login_message = "Registrace úspěšná"          # Zobrazí úspěšnou zprávu.
                state = "menu"                                # Přepne do menu.
            else:                                             # Pokud registrace nevyšla.
                login_message = "Chyba: registrace se nepovedla"  # Zobrazí chybovou hlášku.

    reset_game()                                              # Na začátku připraví novou čistou hru.
    jh = try_get_json(f"{API_BASE}/api/health", timeout=0.6)  # Zkusí zjistit, jestli server běží.
    server_ok = bool(jh and jh.get("ok"))                     # server_ok bude True jen když server odpověděl správně.

    def draw_background(surf):                                # Funkce vykreslí pozadí hry.
        for y in range(HEIGHT):                               # Pro každý vodorovný řádek obrazovky.
            t = y / HEIGHT                                    # Vypočte poměr výšky od 0 do 1.
            r = int(7 + (6 * (1 - t)))                        # Spočítá červenou složku barvy.
            g = int(26 + (25 * t))                            # Spočítá zelenou složku barvy.
            b = int(43 + (40 * t))                            # Spočítá modrou složku barvy.
            pygame.draw.line(surf, (r, g, b), (0, y), (WIDTH, y))  # Nakreslí vodorovnou čáru dané barvy, čímž vzniká gradient.

        for i in range(60):                                   # Nakreslí 60 hvězdiček / světelných bodů.
            x = int((i * 97 + int(scroll * 0.2)) % WIDTH)     # Určí jejich X pozici a lehký posun podle pohybu světa.
            y = int((i * 53) % int(HEIGHT * 0.6))             # Určí Y pozici v horní části obrazovky.
            surf.set_at((x, y), (255, 255, 255))              # Nastaví jeden bílý pixel.

        for c in clouds:                                      # Pro každý mrak v seznamu.
            x = (c.x - scroll * c.v * 0.35) % (WIDTH + 180) - 90  # Vypočítá jeho posunutou pozici, aby se mraky plynule opakovaly.
            y = c.y                                           # Výška mraku zůstává stejná.
            draw_cloud(surf, x, y, c.s)                       # Zavolá funkci, která mrak nakreslí.

        hill = pygame.Surface((WIDTH, 160), pygame.SRCALPHA)  # Vytvoří průhlednou plochu pro kopec na pozadí.
        pts = [(0, 90)]                                       # Začne seznam bodů polygonu.
        for x in range(0, WIDTH + 1, 40):                     # Postupuje po 40 pixelech po šířce obrazovky.
            yy = 90 + math.sin((x + scroll * 0.5) * 0.02) * 14  # Výšku kopce určuje sinus, takže je zvlněný.
            pts.append((x, yy))                               # Přidá vypočtený bod do polygonu.
        pts += [(WIDTH, 160), (0, 160)]                       # Uzavře polygon dole.
        pygame.draw.polygon(hill, (0, 255, 213, 55), pts)     # Nakreslí průhledný polygon kopce.
        surf.blit(hill, (0, HEIGHT - 160))                    # Vloží kopec do spodní části obrazovky.

        ground_y = HEIGHT - GROUND_H                          # Spočítá Y pozici země.
        pygame.draw.rect(surf, (255, 204, 0, 30), (0, ground_y, WIDTH, GROUND_H))  # Nakreslí základní plochu země.
        stripe = pygame.Surface((WIDTH, GROUND_H), pygame.SRCALPHA)  # Vytvoří průhlednou vrstvu pro proužky na zemi.
        for i in range(12):                                   # Nakreslí 12 světlých proužků.
            xx = int(i * 70 - (scroll * 1.6) % 70)            # Posune proužky podle pohybu, aby země působila živě.
            pygame.draw.rect(stripe, (255, 255, 255, 55), (xx, 18, 40, 6), border_radius=6)  # Nakreslí jeden proužek.
        surf.blit(stripe, (0, ground_y))                      # Překryje proužky na zem.

    def draw_cloud(surf, x, y, s):                            # Funkce nakreslí jeden mrak.
        cloud = pygame.Surface((200, 80), pygame.SRCALPHA)    # Vytvoří průhlednou plochu pro mrak.
        col = (255, 255, 255, 36)                             # Nastaví průsvitnou bílou barvu mraku.
        pygame.draw.ellipse(cloud, col, (60, 22, 84, 32))     # Nakreslí střední ovál mraku.
        pygame.draw.ellipse(cloud, col, (30, 30, 58, 30))     # Nakreslí levou část mraku.
        pygame.draw.ellipse(cloud, col, (118, 30, 62, 30))    # Nakreslí pravou část mraku.
        cloud = pygame.transform.smoothscale(cloud, (int(200 * s), int(80 * s)))  # Změní velikost mraku podle měřítka s.
        surf.blit(cloud, (int(x), int(y)))                    # Umístí mrak na výslednou plochu.

    def draw_pipes(surf):                                     # Funkce vykreslí všechny trubky.
        cfg = DIFF[difficulty]                                # Načte aktuální obtížnost.
        pipe_w = 70                                           # Šířka trubky.
        ground_y = HEIGHT - GROUND_H                          # Výška, kde začíná země.
        for p in pipes:                                       # Projde všechny trubky v seznamu.
            x = int(p.x)                                      # Převede X pozici trubky na celé číslo.
            top_h = int(p.gap_y - cfg["gap"] / 2)             # Spočítá výšku horní trubky.
            bottom_y = int(p.gap_y + cfg["gap"] / 2)          # Spočítá začátek spodní trubky.
            h2 = ground_y - bottom_y                          # Spočítá výšku spodní trubky.

            pygame.draw.rect(surf, (0, 0, 0, 60), (x, 0, pipe_w, top_h), border_radius=12)             # Stín horní trubky.
            pygame.draw.rect(surf, (0, 255, 213, 55), (x, 0, pipe_w, top_h), border_radius=12)         # Hlavní tyrkysová vrstva horní trubky.
            pygame.draw.rect(surf, (30, 108, 255, 45), (x, 0, pipe_w, top_h), border_radius=12)        # Modrý lesk / další barevná vrstva.
            pygame.draw.rect(surf, (255, 255, 255, 40), (x, 0, pipe_w, top_h), width=1, border_radius=12)  # Tenký obrys trubky.
            pygame.draw.rect(surf, (255, 255, 255, 28), (x - 6, top_h - 22, pipe_w + 12, 22), border_radius=12)  # Okraj horního „hrdla“ trubky.

            pygame.draw.rect(surf, (0, 0, 0, 60), (x, bottom_y, pipe_w, h2), border_radius=12)         # Stín spodní trubky.
            pygame.draw.rect(surf, (0, 255, 213, 55), (x, bottom_y, pipe_w, h2), border_radius=12)     # Hlavní barva spodní trubky.
            pygame.draw.rect(surf, (30, 108, 255, 45), (x, bottom_y, pipe_w, h2), border_radius=12)    # Druhá barevná vrstva.
            pygame.draw.rect(surf, (255, 255, 255, 40), (x, bottom_y, pipe_w, h2), width=1, border_radius=12)  # Obrys spodní trubky.
            pygame.draw.rect(surf, (255, 255, 255, 28), (x - 6, bottom_y, pipe_w + 12, 22), border_radius=12)  # Hrdlo spodní trubky.

    def draw_boosts(surf):                                    # Funkce vykreslí všechny boosty.
        pulse = 1.0 + math.sin(world_time * 6.0) * 0.08       # Spočítá jemné pulzování boostu podle času.

        for b in boosts:                                      # Projde všechny boosty.
            if not b.active:                                  # Pokud boost už není aktivní.
                continue                                      # Přeskočí ho.

            size = int(26 * pulse)                            # Vypočítá velikost podle pulzování (v kódu není dále použitá, ale ukazuje zamýšlený efekt).

            glow = pygame.Surface((70, 70), pygame.SRCALPHA)  # Vytvoří průhlednou plochu pro světelný efekt.
            pygame.draw.circle(glow, (0, 255, 213, 26), (35, 35), 24)  # Nakreslí kolem boostu průsvitnou záři.
            surf.blit(glow, glow.get_rect(center=(int(b.x), int(b.y)))) # Umístí záři na pozici boostu.

            pygame.draw.circle(surf, (0, 255, 213), (int(b.x), int(b.y)), 10)  # Nakreslí hlavní kruh boostu.
            pygame.draw.circle(surf, (255, 255, 255), (int(b.x), int(b.y)), 4)  # Přidá světlý lesk doprostřed.

    def draw_bird(surf):                                      # Funkce vykreslí ptáka.
        size = 64                                             # Velikost pomocné plochy, na kterou se pták nejdřív kreslí.
        b = pygame.Surface((size, size), pygame.SRCALPHA)     # Vytvoří průhlednou plochu pro ptáka.
        pygame.draw.ellipse(b, (0, 0, 0, 45), (20, 40, 28, 18))         # Stín pod ptákem.
        pygame.draw.ellipse(b, (255, 212, 106, 255), (16, 14, 32, 28))  # Hlavní tělo ptáka.
        pygame.draw.ellipse(b, (255, 156, 58, 200), (16, 14, 32, 28))   # Překryvná oranžová vrstva těla.
        pygame.draw.ellipse(b, (255, 255, 255, 55), (18, 22, 26, 18))   # Lesk na těle ptáka.

        if state == "playing":                                # Pokud se právě hraje.
            flap_speed = 18                                   # Křídla budou mávat rychle.
            flap_amp = 0.75                                   # Pohyb křídel bude větší.
        elif state == "ready":                                # Pokud hra čeká na start.
            flap_speed = 10                                   # Křídla budou mávat středně rychle.
            flap_amp = 0.45                                   # Rozsah pohybu bude menší.
        else:                                                 # V jiných stavech (menu, game over...).
            flap_speed = 7                                    # Křídla se pohybují pomaleji.
            flap_amp = 0.25                                   # Pohyb je jemnější.

        flap_phase = math.sin(world_time * flap_speed)        # Pomocí sinusovky spočítá aktuální fázi mávnutí křídla.

        wing = pygame.Surface((34, 24), pygame.SRCALPHA)      # Vytvoří průhlednou plochu pro křídlo.
        pygame.draw.ellipse(wing, (255, 255, 255, 65), (0, 2, 34, 20))  # Nakreslí tvar křídla.
        pygame.draw.ellipse(wing, (255, 255, 255, 35), (4, 6, 24, 12))  # Přidá lesk na křídle.
        wing_angle = (-0.35 + flap_phase * flap_amp) * 57.3   # Spočítá úhel otočení křídla ve stupních.
        wing = pygame.transform.rotozoom(wing, wing_angle, 1.0)  # Otočí křídlo.

        wing_x = 6                                            # X pozice křídla vůči tělu.
        wing_y = 18 + int(flap_phase * 2)                     # Y pozice křídla se lehce mění podle mávnutí.
        b.blit(wing, (wing_x, wing_y))                        # Přikreslí křídlo na tělo ptáka.

        pygame.draw.circle(b, (255, 255, 255), (42, 22), 6)   # Bílé oko.
        pygame.draw.circle(b, (11, 18, 32), (44, 22), 3)      # Tmavá zornička.
        pygame.draw.circle(b, (255, 255, 255, 220), (45, 20), 1)  # Malý odlesk v oku.

        pygame.draw.polygon(b, (255, 61, 142), [(48, 28), (60, 32), (48, 35)])  # Zobák.
        pygame.draw.polygon(b, (255, 255, 255, 60), [(48, 28), (57, 32), (48, 32)])  # Lesk na zobáku.
        pygame.draw.ellipse(b, (0, 0, 0, 45), (16, 14, 32, 28), width=2)  # Jemný obrys těla.

        rot_deg = -bird_rot * 57.3                            # Převede rotaci ptáka z radiánů na stupně.
        br = pygame.transform.rotozoom(b, rot_deg, 1.0)       # Otočí celý obrázek ptáka.
        surf.blit(br, br.get_rect(center=(int(bird_x), int(bird_y))))  # Nakreslí ptáka na jeho pozici.

    def draw_particles(surf):                                 # Funkce vykreslí částice.
        for p in particles:                                   # Projde všechny částice.
            pygame.draw.rect(surf, (255, 255, 255, 70), (int(p.x), int(p.y), 2, 2))  # Každou částici nakreslí jako malý bílý čtvereček.

    def draw_hud(surf):                                       # Funkce kreslí HUD = informační panel během hry.
        badge = pygame.Surface((160, 46), pygame.SRCALPHA)    # Vytvoří malou průhlednou plochu pro skóre.
        pygame.draw.rect(badge, (0, 0, 0, 80), (0, 0, 160, 46), border_radius=12)  # Pozadí panelu.
        pygame.draw.rect(badge, (255, 255, 255, 40), (0, 0, 160, 46), width=1, border_radius=12)  # Obrys panelu.
        t = font.render(f"Score: {score}", True, (233, 240, 255))  # Vyrenderuje text se skóre.
        badge.blit(t, (12, 14))                               # Nakreslí text do panelu.
        surf.blit(badge, (14, 14))                            # Umístí panel do levého horního rohu.

        info = font_small.render(                             # Vytvoří text s obtížností a rychlostí.
            f"{DIFF[difficulty]['label']}  |  speed {speed_mul:.2f}×",
            True,
            (233, 240, 255, 200),
        )
        surf.blit(info, (14, 62))                             # Nakreslí informační řádek pod skóre.

        status = "DB: připojeno" if server_ok else "DB: nedostupné"  # Připraví text podle dostupnosti databáze/serveru.
        st = font_small.render(status, True, (233, 240, 255, 150))  # Vyrenderuje tento status.
        surf.blit(st, (WIDTH - st.get_width() - 14, 18))      # Zobrazí ho vpravo nahoře.

        if boost_active_time > 0:                             # Pokud je boost právě aktivní.
            ratio = boost_active_time / BOOST_DURATION        # Spočítá podíl zbývajícího času boostu.
            ratio = clamp(ratio, 0.0, 1.0)                    # Omezí tuto hodnotu mezi 0 a 1.

            timer_box = pygame.Surface((190, 44), pygame.SRCALPHA)  # Vytvoří průhledný box pro boost timer.
            pygame.draw.rect(timer_box, (0, 0, 0, 90), (0, 0, 190, 44), border_radius=12)  # Pozadí boxu.
            pygame.draw.rect(timer_box, (255, 255, 255, 35), (0, 0, 190, 44), width=1, border_radius=12)  # Obrys boxu.

            boost_font = pygame.font.SysFont("Segoe UI", 16, bold=True)  # Vytvoří výraznější font pro text boostu.

            text_str = f"BOOST +1  {boost_active_time:.1f}s"  # Připraví text se zbývajícím časem boostu.

            shadow = boost_font.render(text_str, True, (0, 0, 0))  # Vytvoří černý stín textu pro lepší čitelnost.
            timer_box.blit(shadow, (11, 7))                   # Nakreslí stín lehce posunutý.

            color = (255, 80, 80) if boost_active_time < 2 else (0, 255, 213)  # Když zbývá málo času, text zčervená.
            boost_label = boost_font.render(text_str, True, color)  # Vytvoří hlavní text boostu.
            timer_box.blit(boost_label, (10, 6))              # Nakreslí text boostu.

            pygame.draw.rect(timer_box, (255, 255, 255, 28), (10, 26, 170, 10),
                             border_radius=8)                 # Nakreslí podklad progress baru.

            fill_w = int(170 * ratio)                         # Spočítá šířku vyplněné části baru.
            if fill_w > 0:                                    # Pokud má bar ještě něco vyplněného.
                pygame.draw.rect(timer_box, (0, 255, 213, 180), (10, 26, fill_w, 10),
                                 border_radius=8)             # Nakreslí vyplněnou tyrkysovou část.
                pygame.draw.rect(timer_box, (30, 108, 255, 90), (10, 26, fill_w, 10), width=2,
                                 border_radius=8)             # Přidá lesk / obrys vyplněné části.

            surf.blit(timer_box, (14, 84))                    # Zobrazí timer pod informačním řádkem.

    def draw_overlay_box(surf, title, lines):                 # Obecná funkce pro zobrazení informačního okna uprostřed.
        box = pygame.Surface((360, 220), pygame.SRCALPHA)     # Vytvoří průhledný panel.
        pygame.draw.rect(box, (0, 0, 0, 140), (0, 0, 360, 220), border_radius=16)  # Pozadí panelu.
        pygame.draw.rect(box, (255, 255, 255, 45), (0, 0, 360, 220), width=1, border_radius=16)  # Obrys panelu.
        tt = font_big.render(title, True, (233, 240, 255))    # Vyrenderuje nadpis.
        box.blit(tt, (18, 16))                                # Nakreslí nadpis do panelu.
        y = 58                                                # Nastaví počáteční výšku prvního řádku textu.
        for ln in lines:                                      # Projde všechny textové řádky.
            tln = font_small.render(ln, True, (233, 240, 255, 200))  # Vyrenderuje jeden řádek.
            box.blit(tln, (18, y))                            # Nakreslí ho.
            y += 20                                           # Posune Y pozici pro další řádek.
        surf.blit(box, box.get_rect(center=(WIDTH // 2, HEIGHT // 2)))  # Umístí panel doprostřed obrazovky.

    def draw_menu(surf):                                      # Funkce vykreslí hlavní menu.
        title = font_big.render("Flappy Bird", True, (233, 240, 255))  # Nadpis hry.
        surf.blit(title, (24, 26))                            # Zobrazí nadpis.
        sub = font_small.render("GOOD LUCK", True, (233, 240, 255, 160))  # Podnadpis.
        surf.blit(sub, (24, 54))                              # Zobrazí podnadpis.

        btxt = font.render(f"Best score: {best}", True, (233, 240, 255))  # Text s nejlepším skóre.
        surf.blit(btxt, (24, 86))                             # Zobrazí ho.

        lab = font.render("Vyber obtížnost:", True, (233, 240, 255, 210))  # Popisek pro volbu obtížnosti.
        surf.blit(lab, (24, 258))                             # Zobrazí popisek.
        for key, r in diff_rects.items():                     # Projde všechny možnosti obtížnosti.
            active = (key == difficulty)                      # Zjistí, jestli je tahle obtížnost právě vybraná.
            bg = (0, 0, 0, 80) if not active else (0, 255, 213, 60)  # Barva pozadí tlačítka podle výběru.
            pygame.draw.rect(surf, bg, r, border_radius=14)   # Nakreslí tlačítko obtížnosti.
            pygame.draw.rect(                                 # Nakreslí jeho obrys.
                surf,
                (255, 255, 255, 35) if not active else (0, 255, 213, 110),
                r,
                width=2,
                border_radius=14,
            )
            t = font.render(DIFF[key]["label"], True, (233, 240, 255))  # Vytvoří text názvu obtížnosti.
            surf.blit(t, (r.x + 12, r.y + 9))                 # Zobrazí text v tlačítku.

        btn_start.draw(surf, font, active=True)               # Nakreslí tlačítko Start jako aktivní.
        btn_lb.draw(surf, font, active=False)                 # Nakreslí tlačítko Žebříček.
        btn_logout.draw(surf, font, active=False)             # Nakreslí tlačítko Odhlásit.

        if logged_in_user:                                    # Pokud je někdo přihlášen.
            txt = font_small.render(f"Přihlášen: {logged_in_user}", True, (0, 255, 213))  # Zobrazí jméno přihlášeného.
        else:                                                 # Pokud nikdo přihlášen není.
            txt = font_small.render("Nepřihlášen", True, (233, 240, 255, 140))  # Zobrazí text Nepřihlášen.
        surf.blit(txt, (24, 230))                             # Nakreslí tento text.

        hint = font_small.render("Space/klik = skok | Enter = start | Esc = zpět", True, (233, 240, 255, 140))  # Krátká nápověda.
        surf.blit(hint, (24, HEIGHT - 26))                    # Zobrazí nápovědu dole.

    def draw_leaderboard(surf):                               # Funkce vykreslí žebříček výsledků.
        title = font_big.render("Žebříček", True, (233, 240, 255))  # Nadpis žebříčku.
        surf.blit(title, (24, 26))                            # Zobrazí nadpis.
        sub = font_small.render(                              # Podnadpis s obtížností a nápovědou.
            f"Obtížnost: {DIFF[difficulty]['label']}  (R = refresh)",
            True,
            (233, 240, 255, 160),
        )
        surf.blit(sub, (24, 54))                              # Zobrazí podnadpis.
        note = font_small.render(lb_note, True, (233, 240, 255, 160))  # Vyrenderuje stavovou poznámku.
        surf.blit(note, (24, 86))                             # Zobrazí ji.

        y = 118                                               # Počáteční Y pozice tabulky.
        headers = ["#", "Jméno", "Skóre", "Datum"]            # Názvy sloupců tabulky.
        colx = [24, 64, 210, 290]                             # X pozice jednotlivých sloupců.
        for i, h in enumerate(headers):                       # Projde všechny hlavičky.
            surf.blit(font_small.render(h, True, (233, 240, 255, 140)), (colx[i], y))  # Zobrazí název sloupce.
        y += 18                                               # Posune se níž.
        pygame.draw.line(surf, (255, 255, 255, 30), (24, y), (WIDTH - 24, y), 1)  # Nakreslí oddělovací čáru.
        y += 10                                               # Posune Y pod čáru.

        for idx, it in enumerate(lb_items[:10], start=1):     # Projde maximálně 10 záznamů.
            surf.blit(font_small.render(str(idx), True, (233, 240, 255, 140)), (24, y))  # Pořadí hráče.
            surf.blit(font.render(it.get("name", "")[:20], True, (233, 240, 255)), (64, y - 2))  # Jméno hráče.
            surf.blit(font.render(str(it.get("score", 0)), True, (233, 240, 255)), (210, y - 2))  # Skóre hráče.
            surf.blit(font_small.render(it.get("created_at", "")[:16], True, (233, 240, 255, 140)), (290, y))  # Datum záznamu.
            y += 28                                           # Posun na další řádek tabulky.
            if y > HEIGHT - 60:                               # Pokud už je tabulka moc dole.
                break                                         # Přestane kreslit další položky.

        hint = font_small.render("Esc = zpět do menu", True, (233, 240, 255, 140))  # Nápověda pro návrat.
        surf.blit(hint, (24, HEIGHT - 26))                    # Zobrazí nápovědu dole.

    def draw_gameover_panel(surf):                            # Funkce vykreslí panel po prohře.
        panel = pygame.Surface((360, 250), pygame.SRCALPHA)   # Vytvoří průhledný panel.
        pygame.draw.rect(panel, (0, 0, 0, 165), (0, 0, 360, 250), border_radius=18)  # Pozadí panelu.
        pygame.draw.rect(panel, (255, 255, 255, 45), (0, 0, 360, 250), width=1, border_radius=18)  # Obrys panelu.

        title = font_big.render("Game Over", True, (233, 240, 255))  # Vytvoří nadpis Game Over.
        panel.blit(title, (24, 18))                           # Zobrazí ho.

        score_txt = font.render(f"Score: {score}", True, (233, 240, 255))  # Aktuální skóre.
        best_txt = font.render(f"Best score: {best}", True, (233, 240, 255))  # Nejlepší skóre.
        panel.blit(score_txt, (24, 70))                       # Zobrazí aktuální skóre.
        panel.blit(best_txt, (24, 100))                       # Zobrazí nejlepší skóre.

        label = font_small.render("Uložit jako:", True, (233, 240, 255, 200))  # Popisek jména.
        panel.blit(label, (24, 140))                          # Nakreslí popisek.

        input_rect = pygame.Rect(24, 160, 312, 40)            # Obdélník zobrazující jméno hráče.
        pygame.draw.rect(panel, (10, 20, 40, 220), input_rect, border_radius=12)  # Pozadí pole.
        pygame.draw.rect(panel, (0, 255, 213, 110), input_rect, width=2, border_radius=12)  # Obrys pole.

        display_name = logged_in_user if logged_in_user else "Nepřihlášen"  # Zobrazované jméno hráče.
        name_txt = font.render(display_name, True, (233, 240, 255))  # Vytvoří text jména.
        panel.blit(name_txt, (input_rect.x + 12, input_rect.y + 10)) # Zobrazí text jména v poli.

        save_rect = pygame.Rect(90, 210, 180, 34)             # Oblast tlačítka Uložit skóre.
        pygame.draw.rect(panel, (0, 180, 160, 110), save_rect, border_radius=12)  # Pozadí tlačítka.
        pygame.draw.rect(panel, (0, 255, 213, 140), save_rect, width=2, border_radius=12)  # Obrys tlačítka.

        save_txt = font.render("Uložit skóre", True, (233, 240, 255))  # Text tlačítka.
        panel.blit(save_txt, save_txt.get_rect(center=save_rect.center))  # Vycentruje text do středu tlačítka.

        surf.blit(panel, panel.get_rect(center=(WIDTH // 2, HEIGHT // 2)))  # Umístí panel doprostřed obrazovky.

    def draw_pause_panel(surf):                               # Funkce vykreslí pauza menu.
        panel = pygame.Surface((320, 170), pygame.SRCALPHA)   # Vytvoří panel pro pauzu.
        pygame.draw.rect(panel, (0, 0, 0, 170), (0, 0, 320, 170), border_radius=18)  # Tmavé pozadí panelu.
        pygame.draw.rect(panel, (255, 255, 255, 45), (0, 0, 320, 170), width=1, border_radius=18)  # Obrys panelu.

        title = font_big.render("Pause", True, (233, 240, 255))  # Vytvoří nadpis Pause.
        panel.blit(title, title.get_rect(center=(160, 28)))  # Vycentruje nadpis.

        surf.blit(panel, panel.get_rect(center=(WIDTH // 2, HEIGHT // 2)))  # Zobrazí panel uprostřed.

        btn_continue.draw(surf, font, active=True)            # Nakreslí tlačítko Continue.
        btn_menu_pause.draw(surf, font, active=False)         # Nakreslí tlačítko Menu.

    def draw_login_panel(surf, mode="login"):                 # Funkce vykreslí panel přihlášení nebo registrace.
        panel = pygame.Surface((360, 340), pygame.SRCALPHA)   # Vytvoří průhledný panel.
        pygame.draw.rect(panel, (0, 0, 0, 170), (0, 0, 360, 340), border_radius=20)  # Pozadí panelu.
        pygame.draw.rect(panel, (0, 255, 213, 70), (0, 0, 360, 340), width=2, border_radius=20)  # Obrys panelu.

        title_text = "Přihlášení" if mode == "login" else "Registrace"  # Zvolí nadpis podle režimu.
        title = font_big.render(title_text, True, (233, 240, 255))      # Vytvoří nadpis.
        panel.blit(title, (24, 20))                           # Zobrazí nadpis.

        subtitle = font_small.render("Flappy Bird účet", True, (233, 240, 255, 170))  # Podnadpis panelu.
        panel.blit(subtitle, (24, 50))                        # Zobrazí podnadpis.

        user_label = font_small.render("Uživatelské jméno", True, (233, 240, 255))  # Popisek pole pro jméno.
        panel.blit(user_label, (24, 92))                      # Zobrazí popisek.

        user_rect = pygame.Rect(24, 112, 312, 42)             # Oblast inputu pro uživatelské jméno.
        pygame.draw.rect(panel, (10, 20, 40, 220), user_rect, border_radius=12)  # Pozadí pole.
        pygame.draw.rect(                                     # Obrys pole.
            panel,
            (0, 255, 213, 130) if login_field == "username" else (255, 255, 255, 40),
            user_rect,
            width=2,
            border_radius=12,
        )
        user_txt = font.render(login_username, True, (233, 240, 255))  # Vyrenderuje zadané uživatelské jméno.
        panel.blit(user_txt, (user_rect.x + 12, user_rect.y + 11))      # Zobrazí text v poli.

        pass_label = font_small.render("Heslo", True, (233, 240, 255))  # Popisek pole pro heslo.
        panel.blit(pass_label, (24, 166))                      # Zobrazí popisek.

        pass_rect = pygame.Rect(24, 186, 312, 42)             # Oblast inputu pro heslo.
        pygame.draw.rect(panel, (10, 20, 40, 220), pass_rect, border_radius=12)  # Pozadí pole hesla.
        pygame.draw.rect(                                     # Obrys pole hesla.
            panel,
            (0, 255, 213, 130) if login_field == "password" else (255, 255, 255, 40),
            pass_rect,
            width=2,
            border_radius=12,
        )
        hidden_password = "*" * len(login_password)            # Místo skutečného hesla zobrazí hvězdičky.
        pass_txt = font.render(hidden_password, True, (233, 240, 255))  # Vytvoří text hvězdiček.
        panel.blit(pass_txt, (pass_rect.x + 12, pass_rect.y + 11))       # Zobrazí hvězdičky v poli.

        login_btn_rect = pygame.Rect(24, 248, 145, 52)        # Oblast tlačítka Přihlásit.
        register_btn_rect = pygame.Rect(191, 248, 145, 52)    # Oblast tlačítka Registrovat.

        login_active = mode == "login"                         # Zjistí, jestli je aktivní přihlašovací režim.
        register_active = mode == "register"                   # Zjistí, jestli je aktivní registrační režim.

        pygame.draw.rect(panel, (0, 180, 160, 110) if login_active else (0, 0, 0, 90), login_btn_rect, border_radius=12)  # Pozadí tlačítka login.
        pygame.draw.rect(panel, (0, 255, 213, 140), login_btn_rect, width=2, border_radius=12)  # Obrys tlačítka login.

        pygame.draw.rect(panel, (0, 180, 160, 110) if register_active else (0, 0, 0, 90), register_btn_rect, border_radius=12)  # Pozadí tlačítka registrace.
        pygame.draw.rect(panel, (0, 255, 213, 140), register_btn_rect, width=2, border_radius=12)  # Obrys tlačítka registrace.

        login_label = font.render("Přihlásit", True, (233, 240, 255))    # Text tlačítka Přihlásit.
        register_label = font.render("Registrovat", True, (233, 240, 255))  # Text tlačítka Registrovat.
        panel.blit(login_label, login_label.get_rect(center=login_btn_rect.center))  # Vycentruje text Přihlásit.
        panel.blit(register_label, register_label.get_rect(center=register_btn_rect.center))  # Vycentruje text Registrovat.

        msg_color = (255, 160, 160) if "Chyba" in login_message else (180, 255, 180)  # Zvolí barvu zprávy: červená = chyba, zelená = úspěch.
        msg = font_small.render(login_message[:42], True, msg_color)    # Vytvoří zprávu pro uživatele.
        panel.blit(msg, (24, 312))                            # Zobrazí zprávu v dolní části panelu.

        surf.blit(panel, panel.get_rect(center=(WIDTH // 2, HEIGHT // 2)))  # Umístí celý panel doprostřed obrazovky.

    last = time.perf_counter()                                # Uloží čas posledního snímku.
    server_check_timer = 0.0                                  # Časovač pro pravidelnou kontrolu serveru.
    running = True                                            # Proměnná říká, že hlavní smyčka má běžet.

    while running:                                            # Hlavní herní smyčka, běží pořád dokud hru neukončíme.
        now = time.perf_counter()                             # Aktuální čas.
        dt = min(0.05, now - last)                            # Spočítá čas od minulého snímku, ale omezí ho na max 0.05 s.
        last = now                                            # Nastaví aktuální čas jako poslední čas.
        world_time += dt                                      # Přičte uplynulý čas do herního času.

        server_check_timer -= dt                              # Odečítá čas do další kontroly serveru.
        if server_check_timer <= 0:                           # Pokud je čas zkontrolovat server.
            server_check_timer = 3.0                          # Další kontrola proběhne zase za 3 sekundy.
            if state in ("menu", "leaderboard", "gameover", "login", "register"):  # Kontroluje jen mimo aktivní hraní.
                jh = try_get_json(f"{API_BASE}/api/health", timeout=0.2)  # Zavolá serverový health endpoint.
                server_ok = bool(jh and jh.get("ok"))         # Uloží, zda server odpověděl správně.

        for event in pygame.event.get():                      # Projde všechny události od uživatele.
            if event.type == pygame.QUIT:                     # Pokud uživatel zavře okno.
                running = False                               # Ukončí hlavní smyčku.

            if event.type == pygame.KEYDOWN:                  # Pokud uživatel stiskl klávesu.
                if event.key == pygame.K_ESCAPE:              # Když stiskl Escape.
                    if state == "playing":                    # Pokud se právě hraje.
                        state = "paused"                      # Přepne hru do pauzy.

                    elif state == "paused":                   # Pokud je hra pozastavená.
                        state = "playing"                     # Zase se vrátí do hraní.

                    elif state in ("ready", "gameover", "leaderboard"):  # Pokud je hra v jednom z těchto stavů.
                        state = "menu"                        # Escape vrátí hráče do menu.

                    elif state in ("login", "register"):      # Pokud je na login nebo registraci.
                        login_message = ""                    # Smaže text zprávy.
                        login_username = ""                   # Smaže zadané jméno.
                        login_password = ""                   # Smaže zadané heslo.
                        state = "menu" if logged_in_user else "login"  # Pokud je už přihlášen, jde do menu, jinak zůstane na loginu.

                    else:                                     # V ostatních stavech.
                        running = False                       # Ukončí program.

                elif state in ("login", "register"):          # Pokud je hráč v loginu nebo registraci.
                    if event.key == pygame.K_TAB:             # Po stisku klávesy Tab.
                        login_field = "password" if login_field == "username" else "username"  # Přepne aktivní pole.

                    elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):  # Po stisku Enter.
                        submit_login(state)                   # Odešle login nebo registraci.

                    elif event.key == pygame.K_BACKSPACE:     # Po stisku Backspace.
                        if login_field == "username":         # Pokud je aktivní pole jména.
                            login_username = login_username[:-1]  # Smaže poslední znak jména.
                        else:                                 # Jinak je aktivní pole hesla.
                            login_password = login_password[:-1]  # Smaže poslední znak hesla.

                    else:                                     # Jakákoli jiná klávesa.
                        ch = event.unicode                    # Získá napsaný znak.
                        if ch and ch.isprintable():           # Pokud je znak tisknutelný.
                            if login_field == "username" and len(login_username) < 20:  # Do jména maximálně 20 znaků.
                                login_username += ch          # Přidá znak do jména.
                            elif login_field == "password" and len(login_password) < 30:  # Do hesla maximálně 30 znaků.
                                login_password += ch          # Přidá znak do hesla.

                elif state == "menu":                         # Pokud je hráč v menu.
                    if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):  # Po Enteru.
                        state = "ready"                       # Přepne hru do stavu připraveno.
                        reset_game()                          # Resetuje hru.
                    elif event.key == pygame.K_r:             # Pokud stiskne R.
                        best = 0                              # Vynuluje nejlepší skóre.
                        save_best()                           # Uloží nulové skóre do souboru.

                elif state == "leaderboard":                  # Pokud je v žebříčku.
                    if event.key == pygame.K_r:               # Po stisku R.
                        refresh_leaderboard(difficulty)       # Obnoví načtení žebříčku.

                elif state == "ready":                        # Pokud je hra připravená ke startu.
                    if event.key == pygame.K_SPACE:           # Po stisku mezerníku.
                        start_game()                          # Spustí hru.

                elif state == "playing":                      # Pokud se aktivně hraje.
                    if event.key == pygame.K_SPACE:           # Po stisku mezerníku.
                        flap()                                # Pták skočí.

                elif state == "gameover":                     # Pokud je po prohře.
                    if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):  # Když hráč stiskne Enter.
                        if logged_in_user and server_ok:      # Jen když je přihlášen a funguje server.
                            try:                              # Zkusí uložit skóre.
                                post_json(                    # Pošle POST požadavek na server.
                                    f"{API_BASE}/api/scores",
                                    {
                                        "username": logged_in_user,  # Uživatelské jméno.
                                        "difficulty": difficulty,    # Zvolená obtížnost.
                                        "score": score,              # Dosažené skóre.
                                    },
                                )
                            except Exception:                 # Když se uložení nepovede.
                                pass                          # Program nespadne.
                        state = "leaderboard"                 # Přepne se na žebříček.
                        refresh_leaderboard(difficulty)       # Načte nové výsledky.

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Když hráč klikne levým tlačítkem myši.
                mx, my = event.pos                            # Uloží pozici kliknutí.

                if state == "menu":                           # Pokud jsme v menu.
                    for k, r in diff_rects.items():           # Projde všechny oblasti obtížností.
                        if r.collidepoint((mx, my)):          # Když kliknutí padlo do některé oblasti.
                            difficulty = k                    # Nastaví tuto obtížnost.

                    if btn_start.hit((mx, my)):               # Pokud bylo kliknuto na Start.
                        state = "ready"                       # Přepne hru do režimu připraveno.
                        reset_game()                          # Resetuje hru.

                    elif btn_lb.hit((mx, my)):                # Pokud bylo kliknuto na žebříček.
                        state = "leaderboard"                 # Přepne na žebříček.
                        refresh_leaderboard(difficulty)       # Načte žebříček pro zvolenou obtížnost.

                    elif btn_logout.hit((mx, my)):            # Pokud bylo kliknuto na odhlášení.
                        logged_in_user = ""                   # Odhlásí hráče.
                        login_username = ""                   # Smaže login jméno.
                        login_password = ""                   # Smaže login heslo.
                        login_message = ""                    # Smaže informační zprávu.
                        login_field = "username"              # Aktivní bude znovu pole jména.
                        state = "login"                       # Vrátí hráče na login obrazovku.

                elif state in ("login", "register"):          # Pokud je na loginu nebo registraci.
                    panel_x = WIDTH // 2 - 180                # Levý okraj login panelu.
                    panel_y = HEIGHT // 2 - 170               # Horní okraj login panelu.

                    user_rect = pygame.Rect(panel_x + 24, panel_y + 112, 312, 42)       # Absolutní pozice pole jména.
                    pass_rect = pygame.Rect(panel_x + 24, panel_y + 186, 312, 42)       # Absolutní pozice pole hesla.
                    login_btn_rect = pygame.Rect(panel_x + 24, panel_y + 248, 145, 52)  # Absolutní pozice tlačítka Přihlásit.
                    register_btn_rect = pygame.Rect(panel_x + 191, panel_y + 248, 145, 52)  # Absolutní pozice tlačítka Registrovat.

                    if user_rect.collidepoint((mx, my)):      # Pokud klikl do pole jména.
                        login_field = "username"              # Aktivní bude pole jméno.

                    elif pass_rect.collidepoint((mx, my)):    # Pokud klikl do pole hesla.
                        login_field = "password"              # Aktivní bude pole heslo.

                    elif login_btn_rect.collidepoint((mx, my)):  # Pokud klikl na Přihlásit.
                        state = "login"                       # Nastaví login režim.
                        submit_login("login")                 # Odešle přihlášení.

                    elif register_btn_rect.collidepoint((mx, my)):  # Pokud klikl na Registrovat.
                        state = "register"                    # Nastaví registrační režim.
                        submit_login("register")              # Odešle registraci.

                elif state == "gameover":                     # Pokud je konec hry.
                    panel_x = WIDTH // 2 - 180                # Levý okraj game over panelu.
                    panel_y = HEIGHT // 2 - 125               # Horní okraj game over panelu.
                    save_rect = pygame.Rect(panel_x + 90, panel_y + 210, 180, 34)  # Pozice tlačítka Uložit skóre.

                    if save_rect.collidepoint((mx, my)):      # Pokud klikl na tlačítko Uložit skóre.
                        if logged_in_user and server_ok:      # Jen pokud je přihlášen a funguje server.
                            try:                              # Zkusí odeslat skóre.
                                post_json(                    # Odešle data na server.
                                    f"{API_BASE}/api/scores",
                                    {
                                        "username": logged_in_user,  # Jméno hráče.
                                        "difficulty": difficulty,    # Obtížnost.
                                        "score": score,              # Skóre.
                                    },
                                )
                            except Exception:                 # Pokud se něco nepovede.
                                pass                          # Program dál pokračuje.

                        state = "leaderboard"                 # Po uložení přepne do žebříčku.
                        refresh_leaderboard(difficulty)       # Načte žebříček.

                elif state == "paused":                       # Pokud je hra v pauze.
                    if btn_continue.hit((mx, my)):            # Kliknutí na Continue.
                        state = "playing"                     # Pokračuje ve hře.

                    elif btn_menu_pause.hit((mx, my)):        # Kliknutí na Menu.
                        state = "menu"                        # Vrátí do hlavního menu.

                elif state == "ready":                        # Pokud je hra připravená.
                    start_game()                              # Kliknutím se rovnou spustí hra.

                elif state == "playing":                      # Pokud se právě hraje.
                    flap()                                    # Kliknutím pták skočí.

        cfg = DIFF[difficulty]                                # Načte aktuální parametry obtížnosti.

        if state == "ready":                                  # Pokud hra čeká na start.
            bird_y = 240 + math.sin(world_time * 6) * 8       # Pták se lehce pohupuje nahoru a dolů.
            bird_rot = math.sin(world_time * 4) * 0.05        # Pták se lehce naklání.

        if state == "playing":                                # Pokud se aktivně hraje.
            speed_mul = 1.0 + min(0.35, score * 0.01)         # Se skóre se hra trochu zrychluje, ale jen do určitého limitu.
            speed = cfg["speed"] * speed_mul                  # Výsledná rychlost podle obtížnosti a skóre.
            boost_active_time = max(0.0, boost_active_time - dt)  # Zkracuje zbývající dobu boostu.
            boost_timer -= dt                                 # Odpočítává čas do dalšího spawnutí boostu.
            flap_cd = max(0.0, flap_cd - dt)                  # Snižuje cooldown mezi skoky.

            bird_vy += cfg["gravity"] * (dt * 60)             # Přidává gravitaci do svislé rychlosti ptáka.
            bird_y += bird_vy * (dt * 60)                     # Posune ptáka podle svislé rychlosti.

            target_rot = clamp(bird_vy * 0.06, -0.55, 1.0)    # Spočítá cílové natočení podle rychlosti pádu nebo stoupání.
            bird_rot = lerp(bird_rot, target_rot, 0.18)       # Plynule přibližuje aktuální rotaci k cílové.

            for p in pipes:                                   # Projde všechny trubky.
                p.x -= speed * (dt * 60)                      # Posune trubku doleva.
                if not p.passed and p.x + 70 < bird_x:        # Pokud už pták trubku proletěl a ještě za ni nedostal bod.
                    p.passed = True                           # Označí trubku jako započítanou.
                    score += 2 if boost_active_time > 0 else 1  # Když je aktivní boost, dá 2 body, jinak 1.

            if pipes and pipes[0].x < -120:                   # Pokud první trubka odjela mimo obrazovku.
                pipes.pop(0)                                  # Odstraní ji ze seznamu.
                last_x = pipes[-1].x if pipes else WIDTH      # Zjistí X pozici poslední trubky.
                new_x = last_x + cfg["spacing"]               # Spočítá X pozici nové trubky.
                spawn_pipe(new_x)                             # Vytvoří novou trubku.

                new_pipe = pipes[-1]                          # Vezme právě vytvořenou novou trubku.

                if boost_timer <= 0 and random.random() < 0.22:  # Pokud je čas na boost a vyjde náhodná šance.
                    spawn_boost(new_x + 35, new_pipe.gap_y)   # Vytvoří boost uvnitř mezery nové trubky.
                    boost_timer = random.uniform(7.0, 12.0)   # Nastaví další možný spawn až za několik sekund.

            for b in boosts:                                  # Projde všechny boosty.
                if b.active:                                  # Jen aktivní boosty.
                    b.x -= speed * (dt * 60)                  # Posune boost doleva stejně jako trubky.

            for prt in particles:                             # Projde všechny částice.
                prt.x += prt.vx * (dt * 60)                   # Posune částici v ose X.
                prt.y += prt.vy * (dt * 60)                   # Posune částici v ose Y.
                prt.life -= dt                                # Zkrátí dobu života částice.
            particles[:] = [p for p in particles if p.life > 0]  # Odstraní částice, které už „umřely“.
            boosts[:] = [b for b in boosts if b.x > -40 and b.active]  # Smaže boosty mimo obraz nebo neaktivní.
            collect_boosts()                                  # Zkontroluje, jestli pták nějaký boost sebral.

            scroll += speed * (dt * 60)                       # Posune pozadí světa.

            if collide():                                     # Pokud došlo ke kolizi.
                do_game_over()                                # Spustí konec hry.

        if shake > 0:                                         # Pokud ještě běží otřes obrazovky.
            shake *= 0.88                                     # Postupně se zeslabuje.

        frame = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)  # Vytvoří pomocnou plochu pro celý aktuální snímek.
        draw_background(frame)                                # Nakreslí pozadí.
        draw_pipes(frame)                                     # Nakreslí trubky.
        draw_boosts(frame)                                    # Nakreslí boosty.
        draw_particles(frame)                                 # Nakreslí částice.
        draw_bird(frame)                                      # Nakreslí ptáka.

        if state not in ("menu", "leaderboard", "login", "register"):  # Pokud se má zobrazovat herní HUD.
            draw_hud(frame)                                   # Nakreslí informační panel.

        if state == "login":                                  # Pokud je stav login.
            draw_login_panel(frame, "login")                  # Nakreslí login panel.
        elif state == "register":                             # Pokud je stav registrace.
            draw_login_panel(frame, "register")               # Nakreslí registrační panel.
        elif state == "menu":                                 # Pokud je stav menu.
            draw_menu(frame)                                  # Nakreslí menu.
        elif state == "leaderboard":                          # Pokud je stav žebříček.
            draw_leaderboard(frame)                           # Nakreslí žebříček.
        elif state == "ready":                                # Pokud hra čeká na start.
            draw_overlay_box(                                 # Nakreslí informační okno.
                frame,
                "Připrav se!",
                [
                    "Stiskni Space nebo klikni pro start.",   # Nápověda k ovládání startu.
                    f"Obtížnost: {DIFF[difficulty]['label']}",# Zobrazení aktuální obtížnosti.
                ],
            )
        elif state == "paused":                               # Pokud je hra pozastavená.
            draw_pause_panel(frame)                           # Nakreslí pause menu.
        elif state == "gameover":                             # Pokud je konec hry.
            draw_gameover_panel(frame)                        # Nakreslí panel Game Over.

        if shake > 0.2:                                       # Pokud je otřes ještě dost velký.
            ox = int((math.sin(world_time * 40) * 0.5) * shake)  # Vypočítá vodorovný posun otřesu.
            oy = int((math.cos(world_time * 44) * 0.5) * shake)  # Vypočítá svislý posun otřesu.
        else:                                                 # Pokud už je otřes malý.
            ox, oy = 0, 0                                     # Žádný posun.

        screen.fill((0, 0, 0))                                # Vyčistí celé okno na černo.
        screen.blit(frame, (ox, oy))                          # Přenese hotový snímek na obrazovku s případným otřesem.
        pygame.display.flip()                                 # Zobrazí nový snímek hráči.
        clock.tick(FPS)                                       # Omezí běh smyčky na 60 FPS.

    pygame.quit()                                             # Korektně ukončí pygame.
    sys.exit(0)                                               # Ukončí celý program.


if __name__ == "__main__":                                   # Pokud je tento soubor spuštěn přímo.
    main()                                                    # Zavolá hlavní funkci hry.