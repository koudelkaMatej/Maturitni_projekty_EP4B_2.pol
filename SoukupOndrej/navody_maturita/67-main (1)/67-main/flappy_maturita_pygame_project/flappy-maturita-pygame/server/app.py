from flask import Flask, request, jsonify, send_from_directory  # Flask = web server, request = data od klienta, jsonify = odpověď v JSONu, send_from_directory = posílání souborů
from pathlib import Path  # práce s cestami k souborům
from werkzeug.security import generate_password_hash, check_password_hash  # bezpečné hashování hesel
from db import init_db, insert_score, top_scores, create_user, get_user_by_username  # funkce z databáze

BASE_DIR = Path(__file__).resolve().parent  # složka, kde je tento soubor
WEB_DIR = (BASE_DIR.parent / "web").resolve()  # složka "web" o úroveň výš (frontend)

app = Flask(__name__, static_folder=str(WEB_DIR), static_url_path="")  # vytvoří Flask server, nastaví statické soubory

@app.get("/")  # když někdo otevře hlavní URL
def index():
    return send_from_directory(str(WEB_DIR), "index.html")  # pošle index.html (hlavní stránku)

@app.get("/api/health")  # testovací endpoint
def health():
    return jsonify({"ok": True})  # vrátí jednoduchou odpověď, že server běží

@app.get("/api/scores")  # endpoint pro získání skóre
def get_scores():
    difficulty = request.args.get("difficulty", "normal").strip().lower()  # vezme obtížnost z URL (default normal)
    limit = int(request.args.get("limit", "10"))  # kolik výsledků vrátit (default 10)

    if difficulty not in {"easy", "normal", "hard", "insane"}:  # kontrola správné obtížnosti
        return jsonify({"error": "Invalid difficulty"}), 400  # chyba

    limit = max(1, min(limit, 50))  # omezí počet výsledků na 1–50
    return jsonify({"difficulty": difficulty, "items": top_scores(difficulty, limit)})  # vrátí data z databáze

@app.post("/api/register")  # endpoint pro registraci
def register():
    data = request.get_json(silent=True) or {}  # načte JSON data z požadavku
    username = str(data.get("username", "")).strip()  # vezme username
    password = str(data.get("password", "")).strip()  # vezme password

    if len(username) < 3 or len(username) > 20:  # kontrola délky jména
        return jsonify({"error": "Username must be 3-20 chars"}), 400

    if len(password) < 4 or len(password) > 50:  # kontrola délky hesla
        return jsonify({"error": "Password must be 4-50 chars"}), 400

    if get_user_by_username(username):  # když už uživatel existuje
        return jsonify({"error": "User already exists"}), 400

    password_hash = generate_password_hash(password)  # zahashuje heslo
    new_id = create_user(username, password_hash)  # uloží uživatele do DB

    return jsonify({"ok": True, "id": new_id, "username": username})  # vrátí úspěch

@app.post("/api/login")  # endpoint pro přihlášení
def login():
    data = request.get_json(silent=True) or {}  # načte JSON data
    username = str(data.get("username", "")).strip()  # username
    password = str(data.get("password", "")).strip()  # password

    user = get_user_by_username(username)  # najde uživatele v DB
    if not user:  # když neexistuje
        return jsonify({"error": "Invalid username or password"}), 401

    if not check_password_hash(user["password_hash"], password):  # kontrola hesla
        return jsonify({"error": "Invalid username or password"}), 401

    return jsonify({"ok": True, "username": user["username"]})  # přihlášení OK

@app.post("/api/scores")  # endpoint pro uložení skóre
def post_score():
    data = request.get_json(silent=True) or {}  # načte JSON
    username = str(data.get("username", "")).strip()  # jméno
    difficulty = str(data.get("difficulty", "normal")).strip().lower()  # obtížnost
    score = data.get("score", 0)  # skóre

    if not username or len(username) > 20:  # kontrola jména
        return jsonify({"error": "Username must be 1-20 chars"}), 400

    if difficulty not in {"easy", "normal", "hard", "insane"}:  # kontrola obtížnosti
        return jsonify({"error": "Invalid difficulty"}), 400

    try:
        score = int(score)  # převede skóre na číslo
    except Exception:
        return jsonify({"error": "Score must be integer"}), 400

    if score < 0 or score > 999999:  # kontrola rozsahu skóre
        return jsonify({"error": "Score out of range"}), 400

    new_id = insert_score(username, difficulty, score)  # uloží skóre do DB
    return jsonify({"ok": True, "id": new_id})  # vrátí OK

@app.get("/<path:path>")  # fallback pro statické soubory (CSS, JS…)
def static_proxy(path):
    return send_from_directory(str(WEB_DIR), path)  # pošle soubor ze složky web

if __name__ == "__main__":  # když se soubor spustí přímo
    init_db()  # vytvoří databázi (pokud neexistuje)
    app.run(host="127.0.0.1", port=5000, debug=True)  # spustí server na localhost:5000