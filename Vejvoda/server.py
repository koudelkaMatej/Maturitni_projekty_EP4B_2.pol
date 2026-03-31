from flask import Flask, request, jsonify, send_from_directory
import json
import os

app = Flask(__name__, static_folder='.')

LOGIN_FILE = 'prihlaseni.json'
HIGHSCORES_FILE = 'highscores.json'

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
        return []
    with open(HIGHSCORES_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

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

@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()

    if not username or not password:
        return jsonify({'success': False, 'message': 'Vyplňte jméno i heslo.'})

    uzivatele = nacti_uzivatele()
    
    # KONTROLA DUPLICITY JMÉNA
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

    uzivatele = nacti_uzivatele()
    for u in uzivatele:
        if u['username'].lower() == username.lower():
            if u['password'] == password:
                return jsonify({'success': True, 'message': f'Vítej, {u["username"]}!'})
            else:
                return jsonify({'success': False, 'message': 'Špatné heslo.'})

    return jsonify({'success': False, 'message': 'Uživatel nenalezen.'})

@app.route('/api/scores')
def scores():
    return jsonify(nacti_skore())

if __name__ == '__main__':
    app.run(debug=True, port=5000)