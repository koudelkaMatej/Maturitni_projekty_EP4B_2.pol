/**
 * auth.js - Systém přihlašování a registrace
 *
 * Komunikuje se serverem (server.py) přes HTTP API.
 * Spusť server příkazem: python server.py
 * Pak otevři: http://localhost:8000
 */

async function apiCall(endpoint, data) {
    try {
        const res = await fetch(endpoint, {
            method:  "POST",
            headers: { "Content-Type": "application/json" },
            body:    JSON.stringify(data)
        });
        return await res.json();
    } catch (err) {
        return { success: false, message: "❌ Server není dostupný. Spusť: python server.py" };
    }
}

async function register(username, heslo) {
    return await apiCall("/api/register", { username, heslo });
}

async function login(username, heslo) {
    const result = await apiCall("/api/login", { username, heslo });
    if (result.success) {
        setCurrentUser(result.username || username);
    }
    return result;
}

function getCurrentUser() {
    return localStorage.getItem('tetris_session');
}

function setCurrentUser(username) {
    localStorage.setItem('tetris_session', username);
}

function logout() {
    localStorage.removeItem('tetris_session');
    updateNavUI();
    window.location.href = getBasePath() + 'index.html';
}

function getUsers() {
    return [];
}

function updateNavUI() {
    const user    = getCurrentUser();
    const navAuth = document.getElementById('nav-auth');
    if (!navAuth) return;

    if (user) {
        navAuth.innerHTML = `
            <span class="nav-user">▶ ${user}</span>
            <button class="btn btn-danger" onclick="logout()" style="font-size:11px;padding:0.3rem 0.7rem;">
                Odhlásit
            </button>
        `;
    } else {
        const base = getBasePath();
        navAuth.innerHTML = `
            <a href="${base}pages/login.html"    class="btn btn-ghost"   style="font-size:11px;padding:0.3rem 0.8rem;">Přihlásit</a>
            <a href="${base}pages/register.html" class="btn btn-primary" style="font-size:11px;padding:0.3rem 0.8rem;">Registrovat</a>
        `;
    }
}

function getBasePath() {
    return window.location.pathname.includes('/pages/') ? '../' : '';
}

document.addEventListener('DOMContentLoaded', function () {
    updateNavUI();
});