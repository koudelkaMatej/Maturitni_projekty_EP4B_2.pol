from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3, database

app = Flask(__name__)
app.secret_key = "full_project_2026" # Klíč pro šifrování dat v session (cookies)

# Univerzální funkce pro SQL dotazy
def db_query(q, args=(), one=False):
    with sqlite3.connect("tetris.db") as conn:
        conn.row_factory = sqlite3.Row
        res = conn.execute(q, args).fetchall()
        return (res[0] if res else None) if one else res

@app.route('/')
def index():
    # Úvodní stránka s dokumentací projektu
    return render_template('index.html')

@app.route('/leaderboard')
def leaderboard():
    q = """WITH Ranked AS (SELECT *, ROW_NUMBER() OVER(PARTITION BY user_id ORDER BY score DESC) as r FROM high_scores)
           SELECT * FROM Ranked WHERE r <= 2 ORDER BY score DESC LIMIT 20"""
    return render_template('leaderboard.html', scores=db_query(q))

@app.route('/login', methods=['GET', 'POST'])
def login():
    err = None
    if request.method == 'POST':
        uid = database.login_user(request.form['username'], request.form['password'])
        if uid:
            session['user_id'], session['username'] = uid, request.form['username']
            return redirect(url_for('profile'))
        err = "Chybné jméno nebo heslo!"
    return render_template('auth.html', mode='login', error=err)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        if database.register_user(request.form['username'], request.form['password']):
            return redirect(url_for('login'))
    return render_template('auth.html', mode='register')

@app.route('/profile')
def profile():
    if 'user_id' not in session: return redirect(url_for('login'))
    u = db_query("SELECT created_at FROM users WHERE id=?", [session['user_id']], one=True)
    s = db_query("SELECT * FROM high_scores WHERE user_id=? ORDER BY score DESC", [session['user_id']])
    return render_template('profile.html', scores=s, reg_date=u['created_at'] if u else "Neznámo")

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

if __name__ == '__main__':
    database.init_db() # Vytvoří DB tabulky při startu
    app.run(debug=True)