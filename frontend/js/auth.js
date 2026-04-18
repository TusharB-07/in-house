function checkAuth() {
    const token = localStorage.getItem('token');
    const role = localStorage.getItem('role');
    const currentPage = window.location.pathname.split('/').pop();

    if (!token && currentPage !== 'index.html' && currentPage !== '') {
        window.location.href = 'index.html';
        return;
    }

    if (token) {
        // Simple role-based redirection
        if (currentPage === 'index.html' || currentPage === '') {
            if (role === 'admin' || role === 'staff') {
                window.location.href = 'dashboard.html';
            } else {
                window.location.href = 'student.html';
            }
        }
    }
}

function logout() {
    localStorage.clear();
    window.location.href = 'index.html';
}

function setupNavAuth() {
    const navAuth = document.getElementById('nav-auth');
    if (!navAuth) return;

    const name = localStorage.getItem('name');
    if (name) {
        navAuth.innerHTML = `
            <div style="display: flex; align-items: center; gap: 2rem;">
                <span style="font-size: 0.85rem; font-weight: 600; color: var(--text-secondary);">${name}</span>
                <button onclick="logout()" class="btn btn-outline" style="padding: 0.6rem 1.5rem; font-size: 0.75rem; border-radius: 100px;">Logout</button>
            </div>
        `;
    }
}

document.addEventListener('DOMContentLoaded', () => {
    checkAuth();
    setupNavAuth();
});
