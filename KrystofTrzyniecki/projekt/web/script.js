document.addEventListener('DOMContentLoaded', () => {
    const loginModal = document.getElementById('loginModal');
    const registerModal = document.getElementById('registerModal');
    const openLoginBtn = document.getElementById('openLoginBtn');
    const openRegisterBtn = document.getElementById('openRegisterBtn');
    const closeLogin = document.getElementById('closeLogin');
    const closeRegister = document.getElementById('closeRegister');

    if (openLoginBtn) openLoginBtn.onclick = () => loginModal.classList.remove('hidden');
    if (openRegisterBtn) openRegisterBtn.onclick = () => registerModal.classList.remove('hidden');

    if (closeLogin) closeLogin.onclick = () => loginModal.classList.add('hidden');
    if (closeRegister) closeRegister.onclick = () => registerModal.classList.add('hidden');

    window.onclick = (e) => {
        if (e.target == loginModal) loginModal.classList.add('hidden');
        if (e.target == registerModal) registerModal.classList.add('hidden');
    };
});