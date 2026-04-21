const API_BASE = 'http://localhost:5001'; // Default for development

export const api = {
    // Auth (PRD 5.1)
    login: async (studentId, password) => {
        const res = await fetch(`${API_BASE}/api/auth/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ student_id: studentId, password })
        });
        const data = await res.json();
        if (!res.ok) throw data.error || 'Invalid student ID or password';
        return data;
    },

    signup: async (studentData) => {
        const res = await fetch(`${API_BASE}/api/auth/signup`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(studentData)
        });
        const data = await res.json();
        if (!res.ok) throw data.error || 'Failed to create account';
        return data;
    },

    registerStudent: async (studentData) => {
        const token = localStorage.getItem('token');
        const res = await fetch(`${API_BASE}/api/auth/register`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify(studentData)
        });
        const data = await res.json();
        if (res.status === 401) { 
             console.warn("401 Unauthorized - Redirection disabled in developer bypass mode.");
             // localStorage.clear(); window.location.href = 'index.html'; 
        }
        if (!res.ok) throw data.error || 'Failed to register student';
        return data;
    },

    // Bins (PRD 5.2)
    getAllBins: async () => {
        const token = localStorage.getItem('token');
        const res = await fetch(`${API_BASE}/api/bins/all`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        const data = await res.json();
        if (!res.ok) throw data.error || 'Failed to fetch bins';
        return data;
    },

    getBin: async (binId) => {
        const token = localStorage.getItem('token');
        const res = await fetch(`${API_BASE}/api/bins/${binId}`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        const data = await res.json();
        if (!res.ok) throw data.error || 'Failed to fetch bin details';
        return data;
    },

    registerBin: async (location) => {
        const token = localStorage.getItem('token');
        const res = await fetch(`${API_BASE}/api/bins/register`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({ location })
        });
        const data = await res.json();
        if (!res.ok) throw data.error || 'Failed to register bin';
        return data;
    },

    regenerateBinCode: async (binId) => {
        const token = localStorage.getItem('token');
        const res = await fetch(`${API_BASE}/api/bins/regenerate_code`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({ bin_id: binId })
        });
        const data = await res.json();
        if (!res.ok) throw data.error || 'Failed to regenerate code';
        return data;
    },

    // Sessions (PRD 5.3)
    startSession: async (binCode) => {
        const token = localStorage.getItem('token');
        const res = await fetch(`${API_BASE}/api/sessions/start`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({ bin_code: binCode })
        });
        const data = await res.json();
        if (res.status === 401) { 
             console.warn("401 Unauthorized - Redirection disabled in developer bypass mode.");
             // localStorage.clear(); window.location.href = 'index.html'; 
        }
        if (!res.ok) throw data.error || 'Failed to start session';
        return data;
    },

    getActiveSession: async (studentId) => {
        const token = localStorage.getItem('token');
        const res = await fetch(`${API_BASE}/api/sessions/active/${studentId}`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        const data = await res.json();
        if (res.status === 401) { 
             console.warn("401 Unauthorized - Redirection disabled in developer bypass mode.");
             // localStorage.clear(); window.location.href = 'index.html'; 
        }
        if (!res.ok) throw data.error || 'Failed to fetch active session';
        return data;
    },

    endSession: async (sessionId) => {
        const token = localStorage.getItem('token');
        const res = await fetch(`${API_BASE}/api/sessions/end`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({ session_id: sessionId })
        });
        const data = await res.json();
        if (!res.ok) throw data.error || 'Failed to end session';
        return data;
    },

    getAllSessions: async (params = {}) => {
        const token = localStorage.getItem('token');
        const query = new URLSearchParams(params).toString();
        const res = await fetch(`${API_BASE}/api/sessions/all?${query}`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        const data = await res.json();
        if (!res.ok) throw data.error || 'Failed to fetch sessions';
        return data;
    },

    forceEndSession: async (sessionId) => {
        const token = localStorage.getItem('token');
        const res = await fetch(`${API_BASE}/api/sessions/force-end`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({ session_id: sessionId })
        });
        const data = await res.json();
        if (!res.ok) throw data.error || 'Failed to terminate session';
        return data;
    },

    // Disposals (PRD 5.4)
    getDisposals: async (params = {}) => {
        const token = localStorage.getItem('token');
        const query = new URLSearchParams(params).toString();
        const res = await fetch(`${API_BASE}/api/disposals/all?${query}`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        const data = await res.json();
        if (!res.ok) throw data.error || 'Failed to fetch disposals';
        return data;
    },

    // Students (PRD 5.5)
    getLeaderboard: async () => {
        const token = localStorage.getItem('token');
        const res = await fetch(`${API_BASE}/api/students/leaderboard`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        const data = await res.json();
        if (!res.ok) throw data.error || 'Failed to fetch leaderboard';
        return data;
    },

    getStudentProfile: async (studentId) => {
        const token = localStorage.getItem('token');
        const res = await fetch(`${API_BASE}/api/students/${studentId}`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        const data = await res.json();
        if (!res.ok) throw data.error || 'Failed to fetch profile';
        return data;
    },

    getAllStudents: async (params = {}) => {
        const token = localStorage.getItem('token');
        const query = new URLSearchParams(params).toString();
        const res = await fetch(`${API_BASE}/api/students/all?${query}`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        const data = await res.json();
        if (!res.ok) throw data.error || 'Failed to fetch students';
        return data;
    },

    // Stats (PRD 5.6)
    getSummaryStats: async () => {
        const token = localStorage.getItem('token');
        const res = await fetch(`${API_BASE}/api/stats/summary`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        const data = await res.json();
        if (!res.ok) throw data.error || 'Failed to fetch summary stats';
        return data;
    }
};
