function checkAuth() {
    const token = localStorage.getItem('token');
    const path = window.location.pathname.toLowerCase();
    const isLoginPage = path.endsWith('index.html') || path.endsWith('/') || path === '';
    const isProfilePage = path.endsWith('profile.html');

    // Handle redirects
    if (token && isLoginPage) {
        window.location.replace('student.html');
        return;
    }

    if (!token && isProfilePage) {
        window.location.replace('index.html');
    }
}

function requireLogin() {
    const token = localStorage.getItem('token');
    if (!token) {
        alert("Authentication required for this action.");
        window.location.href = 'index.html';
        return false;
    }
    return true;
}

function logout() {
    localStorage.clear();
    window.location.href = 'index.html';
}

function setupNavAuth() {
    const headerActions = document.querySelector('.header-actions');
    const token = localStorage.getItem('token');
    const name = localStorage.getItem('name');

    if (!headerActions) return;

    if (token && name) {
        const initials = name.split(' ').map(n => n[0]).join('');
        headerActions.innerHTML = `
            <a href="profile.html" class="header-btn">
                <div class="avatar-circle" id="header-avatar" style="width: 20px; height: 20px; font-size: 0.5rem; border: none; background: #a3b18a; color: #1a1a1a;">${initials}</div>
                Hello, <span id="header-user-name">${name.split(' ')[0]}</span>
            </a>
            <button onclick="logout()" class="header-btn" style="padding: 0.7rem; aspect-ratio: 1; justify-content: center;" title="Logout">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"></path><polyline points="16 17 21 12 16 7"></polyline><line x1="21" y1="12" x2="9" y2="12"></line></svg>
            </button>
        `;
    } else {
        headerActions.innerHTML = `
            <a href="index.html" class="header-btn">Login</a>
            <a href="signup.html" class="header-btn dark">Sign up</a>
        `;
    }
}

document.addEventListener('DOMContentLoaded', () => {
    checkAuth();
    setupNavAuth();
});
