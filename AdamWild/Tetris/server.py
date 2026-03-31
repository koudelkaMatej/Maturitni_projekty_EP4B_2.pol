#!/usr/bin/env python3
"""
server.py - Jednoduchý webový server pro Tetris projekt

Spuštění:
    python server.py

Pak otevři prohlížeč na:
    http://localhost:8000

Server dělá dvě věci:
  1. Slouží jako normální webový server (servíruje HTML, CSS, JS soubory)
  2. Poskytuje API pro registraci a přihlašování (zapisuje do prihlaseni.json)

API endpointy:
    POST /api/register   - registrace nového uživatele
    POST /api/login      - přihlášení uživatele
    GET  /api/uzivatele  - seznam uživatelů (jen jména, bez hesel)
"""

import http.server
import json
import os
import sys
from urllib.parse import urlparse

# ============================================================
# KONFIGURACE
# ============================================================

PORT          = 8000                          # Port na kterém server poslouchá
PRIHLASENI    = "prihlaseni.json"             # Soubor s uživateli (vedle server.py)
SCRIPT_DIR    = os.path.dirname(os.path.abspath(__file__))  # Složka tohoto skriptu


# ============================================================
# POMOCNÉ FUNKCE PRO PRÁCI S prihlaseni.json
# ============================================================

def nacti_uzivatele():
    """Načte seznam uživatelů ze souboru prihlaseni.json.
    Vrátí seznam slovníků [{"username": ..., "heslo": ...}, ...]"""
    soubor = os.path.join(SCRIPT_DIR, PRIHLASENI)
    if not os.path.exists(soubor):
        return []
    try:
        with open(soubor, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data.get("uzivatele", [])
    except Exception:
        return []


def uloz_uzivatele(uzivatele):
    """Uloží seznam uživatelů do souboru prihlaseni.json."""
    soubor = os.path.join(SCRIPT_DIR, PRIHLASENI)
    with open(soubor, "w", encoding="utf-8") as f:
        json.dump({"uzivatele": uzivatele}, f, ensure_ascii=False, indent=4)


# ============================================================
# HTTP HANDLER - zpracovává všechny požadavky
# ============================================================

class TetrisHandler(http.server.SimpleHTTPRequestHandler):
    """Rozšiřuje SimpleHTTPRequestHandler o API endpointy pro auth."""

    def log_message(self, format, *args):
        """Přepíše výchozí logování - zobrazí jen důležité info."""
        if "/api/" in args[0] if args else False:
            print(f"  API  {self.command} {self.path}")
        # Statické soubory nelogujeme (bylo by příliš mnoho výpisů)

    def send_json(self, status, data):
        """Odešle JSON odpověď s CORS hlavičkami."""
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        # CORS hlavičky - povolí požadavky z prohlížeče na localhost
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(body)

    def read_json_body(self):
        """Přečte a parsuje JSON tělo POST požadavku."""
        length = int(self.headers.get("Content-Length", 0))
        if length == 0:
            return {}
        raw = self.rfile.read(length)
        try:
            return json.loads(raw.decode("utf-8"))
        except Exception:
            return {}

    # ----------------------------------------------------------
    # OPTIONS - preflight CORS požadavky (prohlížeč se "ptá" před POST)
    # ----------------------------------------------------------
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    # ----------------------------------------------------------
    # GET - statické soubory + API endpointy
    # ----------------------------------------------------------
    def do_GET(self):
        parsed = urlparse(self.path)
        path   = parsed.path

        if path == "/api/uzivatele":
            # Vrátí seznam jmen registrovaných uživatelů (bez hesel!)
            uzivatele = nacti_uzivatele()
            jmena = [u["username"] for u in uzivatele]
            self.send_json(200, {"uzivatele": jmena, "pocet": len(jmena)})

        else:
            # Normální statický soubor (HTML, CSS, JS, JSON...)
            # SimpleHTTPRequestHandler se postará o servírování souboru
            super().do_GET()

    # ----------------------------------------------------------
    # POST - API endpointy pro registraci a přihlášení
    # ----------------------------------------------------------
    def do_POST(self):
        parsed = urlparse(self.path)
        path   = parsed.path
        body   = self.read_json_body()

        # ---- REGISTRACE ----
        if path == "/api/register":
            username = (body.get("username") or "").strip()
            heslo    = body.get("heslo") or ""

            # Validace
            if not username or len(username) < 3:
                self.send_json(400, {"success": False, "message": "Jméno musí mít alespoň 3 znaky."})
                return
            if len(username) > 16:
                self.send_json(400, {"success": False, "message": "Jméno může mít nejvýše 16 znaků."})
                return
            if not username.replace("_", "").isalnum():
                self.send_json(400, {"success": False, "message": "Jméno smí obsahovat pouze písmena, číslice a _."})
                return
            if not heslo or len(heslo) < 4:
                self.send_json(400, {"success": False, "message": "Heslo musí mít alespoň 4 znaky."})
                return

            uzivatele = nacti_uzivatele()

            # Kontrola duplicity
            existuje = any(u["username"].lower() == username.lower() for u in uzivatele)
            if existuje:
                self.send_json(409, {"success": False, "message": "Toto jméno je již zaregistrováno."})
                return

            # Přidáme uživatele a uložíme
            from datetime import datetime
            uzivatele.append({
                "username":    username,
                "heslo":       heslo,
                "registrovan": datetime.now().isoformat()
            })
            uloz_uzivatele(uzivatele)

            print(f"  ✅  Nový uživatel: {username}")
            self.send_json(200, {"success": True, "message": "Registrace úspěšná!"})

        # ---- PŘIHLÁŠENÍ ----
        elif path == "/api/login":
            username = (body.get("username") or "").strip()
            heslo    = body.get("heslo") or ""

            if not username or not heslo:
                self.send_json(400, {"success": False, "message": "Vyplň jméno i heslo."})
                return

            uzivatele = nacti_uzivatele()

            # Najdeme uživatele
            uzivatel = next(
                (u for u in uzivatele if u["username"].lower() == username.lower()),
                None
            )

            if not uzivatel:
                self.send_json(401, {"success": False, "message": "Uživatel nenalezen."})
                return

            if uzivatel["heslo"] != heslo:
                self.send_json(401, {"success": False, "message": "Špatné heslo."})
                return

            print(f"  🔑  Přihlášení: {uzivatel['username']}")
            self.send_json(200, {
                "success":  True,
                "message":  "Přihlášení úspěšné!",
                "username": uzivatel["username"]   # Vrátíme originální jméno (zachování velkých písmen)
            })

        else:
            self.send_json(404, {"success": False, "message": "Endpoint nenalezen."})


# ============================================================
# SPUŠTĚNÍ SERVERU
# ============================================================

if __name__ == "__main__":
    # Přepneme pracovní složku na složku tohoto skriptu
    # - SimpleHTTPRequestHandler servíruje soubory z aktuální složky
    os.chdir(SCRIPT_DIR)

    server = http.server.HTTPServer(("", PORT), TetrisHandler)

    print("=" * 50)
    print("  🎮  TETRIS SERVER")
    print("=" * 50)
    print(f"  Spuštěno na: http://localhost:{PORT}")
    print(f"  Složka:      {SCRIPT_DIR}")
    print(f"  Uživatelé:   {PRIHLASENI}")
    print()
    print("  Zastav serverem: Ctrl+C")
    print("=" * 50)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n  Server zastaven.")
        server.server_close()
