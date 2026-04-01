from flask import Flask, request, jsonify, send_from_directory
import json
import os

app = Flask(__name__, static_folder='.')

LOGIN_FILE = 'prihlaseni.json'
HIGHSCORES_FILE = 'highscores.json'

# ── Helpers ──────────────────────────────────────────────────────────────────

def nacti_uzivatele():
    if not os.path.exists(LOGIN_FILE):
        with open(LOGIN_FILE, 'w', encoding='utf-8') as f:
            json.dump([], f)
    with open(LOGIN_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def uloz_uzivatele(uzivatele):
    with open(LOGIN_FILE, 'w', encoding='utf-8') as f:
        json.dump(uzivatele, f, indent=4, ensure_ascii=False)

def nacti_skore():
    if not os.path.exists(HIGHSCORES_FILE):
        with open(HIGHSCORES_FILE, 'w', encoding='utf-8') as f:
            json.dump([], f)
    with open(HIGHSCORES_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def uloz_skore_soubor(zaznamy):
    with open(HIGHSCORES_FILE, 'w', encoding='utf-8') as f:
        json.dump(zaznamy, f, indent=4, ensure_ascii=False)

# ── Static pages ─────────────────────────────────────────────────────────────

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/doc.html')
def doc():
    return send_from_directory('.', 'doc.html')

@app.route('/popis.html')
def popis():
    return send_from_directory('.', 'popis.html')

@app.route('/er.png')
def er_png():
    return send_from_directory('.', 'er.png')

# ── Auth API ──────────────────────────────────────────────────────────────────

@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()

    if not username or not password:
        return jsonify({'success': False, 'message': 'Vyplňte jméno i heslo.'})
    if len(password) < 3:
        return jsonify({'success': False, 'message': 'Heslo musí mít alespoň 3 znaky.'})

    uzivatele = nacti_uzivatele()

    if any(u['username'].lower() == username.lower() for u in uzivatele):
        return jsonify({'success': False, 'message': f'Uživatel "{username}" již existuje.'})

    uzivatele.append({'username': username, 'password': password})
    uloz_uzivatele(uzivatele)
    return jsonify({'success': True, 'message': f'Registrace "{username}" proběhla úspěšně!'})


@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()

    if not username or not password:
        return jsonify({'success': False, 'message': 'Vyplňte jméno i heslo.'})

    uzivatele = nacti_uzivatele()
    for u in uzivatele:
        if u['username'].lower() == username.lower():
            if u['password'] == password:
                return jsonify({'success': True, 'message': f'Vítej, {u["username"]}!', 'username': u['username']})
            else:
                return jsonify({'success': False, 'message': 'Špatné heslo.'})

    return jsonify({'success': False, 'message': 'Uživatel nenalezen.'})


@app.route('/api/check_user', methods=['POST'])
def check_user():
    """Ověří zda uživatel existuje (pro hru před uložením skóre)."""
    data = request.get_json()
    username = data.get('username', '').strip()
    uzivatele = nacti_uzivatele()
    exists = any(u['username'].lower() == username.lower() for u in uzivatele)
    return jsonify({'exists': exists})

# ── Scores API ────────────────────────────────────────────────────────────────

@app.route('/api/scores')
def scores():
    return jsonify(nacti_skore())


@app.route('/api/submit_score', methods=['POST'])
def submit_score():
    """
    Uloží skóre jen pokud je lepší než aktuální rekord hráče.
    Vyžaduje ověření heslem (aby nikdo cizí nepsal skóre za jiného hráče).
    """
    data = request.get_json()
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()
    skore    = data.get('score', 0)
    obtiznost = data.get('difficulty', 'normal')

    if not username or not password:
        return jsonify({'success': False, 'message': 'Chybí přihlašovací údaje.'})

    # Ověření hesla
    uzivatele = nacti_uzivatele()
    autorizovan = False
    for u in uzivatele:
        if u['username'].lower() == username.lower() and u['password'] == password:
            autorizovan = True
            username = u['username']   # správná velikost písmen
            break

    if not autorizovan:
        return jsonify({'success': False, 'message': 'Neplatné přihlašovací údaje.'})

    zaznamy = nacti_skore()
    nalezeno = False
    bylo_lepsi = False

    for z in zaznamy:
        if z['name'].lower() == username.lower():
            nalezeno = True
            if skore > z['score']:
                z['score'] = skore
                z['difficulty'] = obtiznost
                z['name'] = username
                bylo_lepsi = True
            break

    if not nalezeno:
        zaznamy.append({'name': username, 'score': skore, 'difficulty': obtiznost})
        bylo_lepsi = True

    zaznamy = sorted(zaznamy, key=lambda x: x['score'], reverse=True)[:10]
    uloz_skore_soubor(zaznamy)

    if bylo_lepsi:
        return jsonify({'success': True, 'message': f'Nový rekord: {skore} bodů! 🎉', 'new_record': True})
    else:
        return jsonify({'success': True, 'message': 'Skóre uloženo (není lepší než tvůj rekord).', 'new_record': False})

# ─────────────────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    app.run(debug=True, port=5000)
