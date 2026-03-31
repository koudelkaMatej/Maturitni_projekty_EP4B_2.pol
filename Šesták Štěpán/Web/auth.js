// auth.js
// Sdilena logika prihlaseni - pouziva se na vsech strankach.
// Stara se o hash hesel, cteni/zapis uzivatelu a vykresleni user widgetu v headeru.

function hashPassword(password) {
    // Jednoduchy hash (djb2) - heslo se nikam neukada v cistém textu
    let hash = 5381;
    for (let i = 0; i < password.length; i++) {
        hash = ((hash << 5) + hash) + password.charCodeAt(i);
        hash = hash & hash;
    }
    return hash.toString();
}

function loadUsers() {
    try { return JSON.parse(localStorage.getItem('fc_users') || '{}'); }
    catch { return {}; }
}

function saveUsers(users) {
    localStorage.setItem('fc_users', JSON.stringify(users));
}

function getLoggedUser() {
    return localStorage.getItem('fc_logged_user') || null;
}

function logout() {
    localStorage.removeItem('fc_logged_user');
    window.location.href = 'Prihlaseni.html';
}

function renderUserWidget() {
    const slot = document.getElementById('header-user-slot');
    if (!slot) return;

    const user = getLoggedUser();

    if (!user) {
        slot.innerHTML = '<a href="Prihlaseni.html" class="btn-nav-login">Prihlasit se</a>';
        return;
    }

    slot.innerHTML = `
        <div class="user-widget" id="user-widget">
            <button class="user-btn" onclick="toggleDropdown()">
                <span class="status-dot"></span>
                <span>${escapeHtml(user)}</span>
                <span class="arrow">&#9660;</span>
            </button>
            <div class="user-dropdown">
                <div class="dropdown-header">
                    <div class="d-name">${escapeHtml(user)}</div>
                    <div class="d-sub">Prihlasen</div>
                </div>
                <a href="Zebricek.html" class="dropdown-item">Zebricek</a>
                <a href="Index.html"    class="dropdown-item">Domu</a>
                <div class="dropdown-divider"></div>
                <button class="dropdown-item danger" onclick="logout()">Odhlasit se</button>
            </div>
        </div>`;

    document.addEventListener('click', (e) => {
        const w = document.getElementById('user-widget');
        if (w && !w.contains(e.target)) w.classList.remove('open');
    });
}

function toggleDropdown() {
    document.getElementById('user-widget')?.classList.toggle('open');
}

function escapeHtml(str) {
    return String(str)
        .replace(/&/g, '&amp;').replace(/</g, '&lt;')
        .replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}

document.addEventListener('DOMContentLoaded', renderUserWidget);
