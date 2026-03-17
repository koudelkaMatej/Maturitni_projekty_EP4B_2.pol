/**
 * script.js – Flappy Palach front-end
 *
 * Zodpovědnosti:
 *   1. Auth modal  – přihlášení / registrace, session v paměti
 *   2. Nav bar     – zobrazení po přihlášení, odhlášení
 *   3. Leaderboard – nacti / filtruj / stránkuj (jako dříve)
 *   4. Profile panel – nejlepší skóre, všechny pokusy, změna jména
 */

// ============================================================
// KONFIGURACE
// ============================================================
const API = {
    login          : 'login.php',
    register       : 'register.php',
    getScores      : 'get_scores.php',
    submitScore    : 'submit_score.php',
    getUserScores  : 'get_user_scores.php',
    changeUsername  : 'change_username.php'
};

const PER_PAGE          = 50;   // žebříček
const ATTEMPTS_PER_PAGE = 30;   // pokusy na profilu

// ============================================================
// SESSION (in-memory – žádné localStorage)
// ============================================================
let session = { user_id: null, username: null };

// ============================================================
// LEADERBOARD STATE
// ============================================================
let allScores        = [];
let currentPage      = 1;
let currentDifficulty = 'all';
let searchQuery      = '';

// ============================================================
// PROFILE STATE
// ============================================================
let attemptsPage = 1;
let attemptsData = [];   // raw array from server

// ============================================================
// INIT
// ============================================================
document.addEventListener('DOMContentLoaded', () => {
    wireAuthModal();
    wireNavBar();
    wireLeaderboard();
    wireProfile();

    // na začátku zobrazíme auth modal (musí se přihlásit)
    showAuthModal();

    // nacti leaderboard na pozadí
    loadScores();
});

// ============================================================
// HELPERS
// ============================================================
function escapeHtml(t) {
    const d = document.createElement('div');
    d.textContent = t;
    return d.innerHTML;
}

function formatDate(str) {
    const d = new Date(str), now = new Date();
    const pad = n => String(n).padStart(2,'0');
    const time = `${pad(d.getHours())}:${pad(d.getMinutes())}`;

    if (d.toDateString() === now.toDateString()) return `Dnes ${time}`;

    const yest = new Date(now);
    yest.setDate(yest.getDate()-1);
    if (d.toDateString() === yest.toDateString()) return `Včera ${time}`;

    return `${pad(d.getDate())}.${pad(d.getMonth()+1)}.${d.getFullYear()} ${time}`;
}

const DIFF_LABEL = { lehka:'🟢 Lehká', stredni:'🟡 Střední', tezka:'🔴 Těžká' };

/** generic POST – vrácí parsed JSON */
async function postJson(url, body) {
    const params = new URLSearchParams(body);
    const res    = await fetch(url, {
        method  : 'POST',
        headers : { 'Content-Type': 'application/x-www-form-urlencoded' },
        body    : params.toString()
    });
    return res.json();
}

/** zobraz / skryj element */
function show(el) { el.classList.remove('hidden'); }
function hide(el) { el.classList.add('hidden'); }

// ============================================================
// 1. AUTH MODAL
// ============================================================
function wireAuthModal() {
    // tab přepínání
    document.querySelectorAll('.modal-tab').forEach(tab => {
        tab.addEventListener('click', () => {
            document.querySelectorAll('.modal-tab').forEach(t => t.classList.remove('active'));
            tab.classList.add('active');

            const isLogin = tab.dataset.tab === 'login';
            toggleEl('form-login',    isLogin);
            toggleEl('form-register', !isLogin);
            hideAuthMsg();
        });
    });

    // přihlášení
    document.getElementById('btn-login').addEventListener('click', async () => {
        const u = document.getElementById('login-username').value.trim();
        const p = document.getElementById('login-password').value;
        if (u.length < 3) return showAuthMsg('Jméno min 3 znaky', 'error');
        if (p.length < 4) return showAuthMsg('Heslo min 4 znaky', 'error');

        showAuthMsg('Přihlášování…', 'ok');
        try {
            const data = await postJson(API.login, { username: u, password: p });
            if (data.success) {
                session.user_id  = data.data.user_id;
                session.username = data.data.username;
                hideAuthModal();
                onLogin();
            } else {
                showAuthMsg(data.message, 'error');
            }
        } catch (e) {
            showAuthMsg('Chyba spojení se serverem', 'error');
        }
    });

    // registrace
    document.getElementById('btn-register').addEventListener('click', async () => {
        const u = document.getElementById('reg-username').value.trim();
        const p = document.getElementById('reg-password').value;
        if (u.length < 3) return showAuthMsg('Jméno min 3 znaky', 'error');
        if (p.length < 4) return showAuthMsg('Heslo min 4 znaky', 'error');

        showAuthMsg('Registrujeme…', 'ok');
        try {
            const data = await postJson(API.register, { username: u, password: p });
            if (data.success) {
                session.user_id  = data.data.user_id;
                session.username = data.data.username;
                hideAuthModal();
                onLogin();
            } else {
                showAuthMsg(data.message, 'error');
            }
        } catch (e) {
            showAuthMsg('Chyba spojení se serverem', 'error');
        }
    });

    // Enter na heslo = klik na příslušné tlačítko
    document.getElementById('login-password').addEventListener('keydown', e => {
        if (e.key === 'Enter') document.getElementById('btn-login').click();
    });
    document.getElementById('reg-password').addEventListener('keydown', e => {
        if (e.key === 'Enter') document.getElementById('btn-register').click();
    });
}

function showAuthModal() { show(document.getElementById('auth-modal')); }
function hideAuthModal() { hide(document.getElementById('auth-modal')); }

function showAuthMsg(text, type) {
    const el = document.getElementById('auth-msg');
    el.textContent = text;
    el.className   = 'modal-msg ' + type;
    show(el);
}

function hideAuthMsg() { hide(document.getElementById('auth-msg')); }

function toggleEl(id, visible) {
    visible ? show(document.getElementById(id)) : hide(document.getElementById(id));
}

// ============================================================
// 2. NAV BAR + ODHLÁŠENÍ
// ============================================================================
function wireNavBar() {
    document.getElementById('btn-logout').addEventListener('click', () => {
        session = { user_id: null, username: null };
        hide(document.getElementById('nav-bar'));
        hideProfilePanel();
        showAuthModal();
        // vyčisti fields
        document.getElementById('login-username').value  = '';
        document.getElementById('login-password').value  = '';
        document.getElementById('reg-username').value    = '';
        document.getElementById('reg-password').value    = '';
        hideAuthMsg();
    });

    document.getElementById('btn-profile').addEventListener('click', () => {
        openProfilePanel();
    });
}

/** po úspěšném přihlášení / registraci */
function onLogin() {
    document.getElementById('nav-username').textContent = session.username;
    show(document.getElementById('nav-bar'));
    // obnoví leaderboard (aby se zobrazil aktuální stav)
    loadScores();
}

// ============================================================
// 3. LEADERBOARD  (stejná logika jako dříve, refaktorováno)
// ============================================================
function wireLeaderboard() {
    // vyhledávání
    document.getElementById('search-input').addEventListener('input', e => {
        searchQuery = e.target.value.toLowerCase().trim();
        currentPage = 1;
        filterAndDisplay();
    });

    // filtry obtížnosti
    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            currentDifficulty = btn.dataset.difficulty;
            currentPage = 1;
            loadScores();
        });
    });

    // obnovit
    document.getElementById('refresh-btn').addEventListener('click', loadScores);
}

async function loadScores() {
    showLoadingRow('leaderboard-body', 5);

    let url = API.getScores + '?limit=500';
    if (currentDifficulty !== 'all') url += '&difficulty=' + currentDifficulty;

    try {
        const res  = await fetch(url);
        const data = await res.json();
        if (data.success) {
            allScores = data.data.scores;
            updateStats();
            filterAndDisplay();
        } else {
            showError('leaderboard-body', 5, data.message);
        }
    } catch (e) {
        showError('leaderboard-body', 5, 'Nepodařilo se nacti data.');
    }
}

function filterAndDisplay() {
    let list = allScores;
    if (searchQuery) list = list.filter(s => s.username.toLowerCase().includes(searchQuery));
    renderLeaderboard(list);
    renderPagination('pagination', list.length, currentPage, PER_PAGE, p => { currentPage = p; filterAndDisplay(); });
}

function renderLeaderboard(scores) {
    const start = (currentPage-1)*PER_PAGE;
    const page  = scores.slice(start, start+PER_PAGE);
    const tbody = document.getElementById('leaderboard-body');

    if (!page.length) {
        tbody.innerHTML = `<tr><td colspan="5" class="empty-state">
            <div class="empty-state-icon">🎮</div><p>Žádné záznamy</p></td></tr>`;
        return;
    }

    tbody.innerHTML = page.map((s,i) => {
        const rank = start+i+1;
        return `<tr>
            <td class="col-rank">${rank}</td>
            <td class="col-name">${escapeHtml(s.username)}</td>
            <td class="col-score"><span class="score-highlight">${s.score}</span></td>
            <td class="col-diff"><span class="difficulty-badge difficulty-${s.difficulty}">${DIFF_LABEL[s.difficulty]||s.difficulty}</span></td>
            <td class="col-date">${formatDate(s.date)}</td>
        </tr>`;
    }).join('');
}

function updateStats() {
    const players = new Set(allScores.map(s=>s.username)).size;
    const best    = allScores.length ? allScores[0].score : 0;
    document.getElementById('total-players').textContent  = players;
    document.getElementById('highest-score').textContent  = best;
    document.getElementById('total-games').textContent    = allScores.length;
}

// ============================================================
// 4. PROFILE PANEL
// ============================================================
function wireProfile() {
    document.getElementById('btn-profile-close').addEventListener('click', hideProfilePanel);
    document.getElementById('btn-rename').addEventListener('click', doRename);
}

async function openProfilePanel() {
    if (!session.user_id) return;

    show(document.getElementById('profile-panel'));

    // prefill rename
    document.getElementById('rename-input').value = session.username;
    hide(document.getElementById('rename-msg'));

    // nacti data uživatele
    try {
        const res  = await fetch(API.getUserScores + '?user_id=' + session.user_id + '&limit=500');
        const data = await res.json();
        if (data.success) {
            renderBestCards(data.data.bests);
            attemptsData = data.data.attempts;
            attemptsPage = 1;
            renderAttempts();
        }
    } catch (e) {
        console.error('Chyba nactu profilu', e);
    }
}

function hideProfilePanel() { hide(document.getElementById('profile-panel')); }

/* --- best cards --- */
function renderBestCards(bests) {
    const diffs = ['lehka','stredni','tezka'];
    document.getElementById('best-cards').innerHTML = diffs.map(d => {
        const b = bests[d];
        if (b) {
            return `<div class="best-card best-card--${d}">
                <div class="best-card__label">${DIFF_LABEL[d]}</div>
                <div class="best-card__score">${b.best_score}</div>
                <div class="best-card__attempts">${b.attempts} pokus${b.attempts===1?'':'ů'}</div>
            </div>`;
        }
        return `<div class="best-card best-card--empty best-card--${d}">
            <div class="best-card__label">${DIFF_LABEL[d]}</div>
            <div class="best-card__score">—</div>
            <div class="best-card__attempts">žádný pokus</div>
        </div>`;
    }).join('');
}

/* --- attempts table + paging --- */
function renderAttempts() {
    const start = (attemptsPage-1)*ATTEMPTS_PER_PAGE;
    const page  = attemptsData.slice(start, start+ATTEMPTS_PER_PAGE);
    const tbody = document.getElementById('attempts-body');

    if (!page.length) {
        tbody.innerHTML = '<tr><td colspan="4" style="text-align:center;color:#999;padding:24px;">Žádné pokusy</td></tr>';
    } else {
        tbody.innerHTML = page.map((a,i) => `<tr>
            <td>${start+i+1}.</td>
            <td><strong>${a.score}</strong></td>
            <td><span class="difficulty-badge difficulty-${a.difficulty}">${DIFF_LABEL[a.difficulty]||a.difficulty}</span></td>
            <td>${formatDate(a.date)}</td>
        </tr>`).join('');
    }

    renderPagination('attempts-pagination', attemptsData.length, attemptsPage, ATTEMPTS_PER_PAGE, p => {
        attemptsPage = p;
        renderAttempts();
    });
}

/* --- rename --- */
async function doRename() {
    const newName = document.getElementById('rename-input').value.trim();
    const msgEl   = document.getElementById('rename-msg');

    if (newName.length < 3) { showMsg(msgEl, 'Jméno min 3 znaky', 'error'); return; }
    if (newName.length > 30) { showMsg(msgEl, 'Jméno max 30 znaků', 'error'); return; }

    showMsg(msgEl, 'Měníme…', 'ok');

    try {
        const data = await postJson(API.changeUsername, { user_id: session.user_id, new_username: newName });
        if (data.success) {
            session.username = data.data.username;
            document.getElementById('nav-username').textContent = session.username;
            showMsg(msgEl, data.message, 'ok');
            // obnoví leaderboard + attempts (jména se změnily)
            loadScores();
            // obnoví attempts in-place
            attemptsData.forEach(a => a.username = session.username);
        } else {
            showMsg(msgEl, data.message, 'error');
        }
    } catch (e) {
        showMsg(msgEl, 'Chyba spojení', 'error');
    }
}

// ============================================================
// GENERIC PAGINATION RENDERER
// ============================================================
/**
 * @param {string}   containerId   – id elementu kde se zobrazí
 * @param {number}   total         – celkem položek
 * @param {number}   currentP      – aktuální stránka
 * @param {number}   perPage       – položky na stránku
 * @param {function} onChangeFn    – callback(newPage)
 */
function renderPagination(containerId, total, currentP, perPage, onChangeFn) {
    const container = document.getElementById(containerId);
    const pages     = Math.ceil(total / perPage);

    if (pages <= 1) { container.innerHTML = ''; return; }

    let html = `<button class="page-btn" ${currentP===1?'disabled':''} onclick="__pg('${containerId}',${currentP-1})">&larr; Předchozí</button>`;

    for (let i=1; i<=pages; i++) {
        if (i===1 || i===pages || (i>=currentP-2 && i<=currentP+2)) {
            html += `<button class="page-btn ${i===currentP?'active':''}" onclick="__pg('${containerId}',${i})">${i}</button>`;
        } else if (i===currentP-3 || i===currentP+3) {
            html += '<span style="padding:10px">…</span>';
        }
    }

    html += `<button class="page-btn" ${currentP===pages?'disabled':''} onclick="__pg('${containerId}',${currentP+1})">Další &rarr;</button>`;
    container.innerHTML = html;

    // uložíme callback do globálního mapy (aby onclick string fungoval)
    if (!window.__pgCallbacks) window.__pgCallbacks = {};
    window.__pgCallbacks[containerId] = onChangeFn;
}

/** globální helper volaný z onclick stringů */
window.__pg = function(containerId, page) {
    const cb = window.__pgCallbacks && window.__pgCallbacks[containerId];
    if (cb) cb(page);
};

// ============================================================
// SMALL UI HELPERS
// ============================================================
function showLoadingRow(tbodyId, cols) {
    document.getElementById(tbodyId).innerHTML =
        `<tr><td colspan="${cols}" class="loading-cell"><div class="pixel-loader"></div><p>NAČÍTÁNÍ...</p></td></tr>`;
}

function showError(tbodyId, cols, msg) {
    document.getElementById(tbodyId).innerHTML =
        `<tr><td colspan="${cols}" class="empty-state">
            <div class="empty-state-icon">⚠️</div>
            <p style="color:#e74c3c;font-weight:bold">Chyba</p>
            <p style="margin-top:8px">${escapeHtml(msg)}</p>
        </td></tr>`;
}

function showMsg(el, text, type) {
    el.textContent = text;
    el.className   = 'profile-msg ' + type;
    show(el);
}