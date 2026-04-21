(function() {
    // SEPARATE MOCK LOGIN UTILITY
    // Set to 'false' to disable mock login
    const MOCK_ENABLED = true;

    if (MOCK_ENABLED && !localStorage.getItem('token')) {
        localStorage.setItem('token', 'mock-auth-token-2026');
        localStorage.setItem('role', 'student');
        localStorage.setItem('name', 'Priya Sharma');
        localStorage.setItem('student_id', 'RA2211003010');
        console.log("🚀 ECOIN: Mock Session Initialized");
    }
})();
