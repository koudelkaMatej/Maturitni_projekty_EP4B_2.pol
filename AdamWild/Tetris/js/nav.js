/**
 * nav.js - Sdílená navigace
 *
 * Vloží HTML navigace do každé stránky automaticky.
 * Díky tomu nemusíme kopírovat kód navigace do každého souboru zvlášť.
 */

/**
 * Vloží navigaci do elementu s id="navbar".
 * Označí aktivní stránku správnou CSS třídou.
 */
function renderNav() {
  const base = getBasePath();  // Cesta k root složce (pro správné relativní odkazy)

  // Zjistíme, na které stránce jsme (podle URL adresy)
  const path = window.location.pathname;
  const isHome     = path.endsWith('index.html') || path.endsWith('/');
  const isScores   = path.includes('leaderboard');
  const isDocs     = path.includes('docs');
  const isLogin    = path.includes('login');
  const isRegister = path.includes('register');
  const isProfile  = path.includes('profile');

  // Pomocná funkce - vrátí 'active' pokud je stránka aktivní
  const a = (check) => check ? 'active' : '';

  // Vložíme HTML navigace
  const navbar = document.getElementById('navbar');
  if (!navbar) return;

  navbar.innerHTML = `
    <a href="${base}index.html" class="nav-logo">
      <!-- Pixel logo - čtyři bloky jako Tetris kostička -->
      <span style="display:inline-flex;align-items:center;gap:8px;">
        <span style="display:grid;grid-template-columns:repeat(2,8px);gap:2px;">
          <span style="width:8px;height:8px;background:var(--accent-cyan);border-radius:1px;display:block;"></span>
          <span style="width:8px;height:8px;background:var(--accent-cyan);border-radius:1px;display:block;"></span>
          <span style="width:8px;height:8px;background:var(--accent-cyan);border-radius:1px;display:block;"></span>
          <span style="width:8px;height:8px;background:transparent;border-radius:1px;display:block;"></span>
        </span>
        TETRIS
      </span>
    </a>

    <ul class="nav-links">
      <li><a href="${base}index.html" class="${a(isHome)}">Home</a></li>
      <li><a href="${base}pages/leaderboard.html" class="${a(isScores)}">Žebříček</a></li>
      <li><a href="${base}pages/docs.html" class="${a(isDocs)}">Dokumentace</a></li>
      ${getCurrentUser() ? `<li><a href="${base}pages/profile.html" class="${a(isProfile)}">Profil</a></li>` : ''}
    </ul>

    <div class="nav-auth" id="nav-auth">
      <!-- Vyplní auth.js po načtení stránky -->
    </div>
  `;

  // Po vykreslení navigace aktualizujeme auth tlačítka
  updateNavUI();
}

// Spustíme renderNav jakmile je DOM připraven
document.addEventListener('DOMContentLoaded', renderNav);
