/**
 * API Layer - Handles all communication with the Django REST backend.
 * Simple fetch-based HTTP client with JWT token management.
 */

// Auto-detect: use localhost for development, Render URL for production
const API_BASE = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
    ? 'http://127.0.0.1:8000/api/v1'
    : 'https://expmanage-sush.onrender.com/api/v1';

// ===== TOKEN MANAGEMENT =====

function getAccessToken() {
    return localStorage.getItem('access_token');
}

function getRefreshToken() {
    return localStorage.getItem('refresh_token');
}

function saveTokens(access, refresh) {
    localStorage.setItem('access_token', access);
    if (refresh) localStorage.setItem('refresh_token', refresh);
}

function clearTokens() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
}

// ===== HTTP HELPER =====

/**
 * Makes an authenticated API request.
 * Automatically attaches JWT token and handles 401 with token refresh.
 */
async function apiRequest(endpoint, options = {}) {
    const url = `${API_BASE}${endpoint}`;

    const headers = {
        'Content-Type': 'application/json',
        ...options.headers,
    };

    const token = getAccessToken();
    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }

    let response = await fetch(url, {
        ...options,
        headers,
    });

    // If 401, try to refresh the token
    if (response.status === 401 && getRefreshToken()) {
        const refreshed = await refreshAccessToken();
        if (refreshed) {
            headers['Authorization'] = `Bearer ${getAccessToken()}`;
            response = await fetch(url, { ...options, headers });
        } else {
            // Refresh failed, logout
            clearTokens();
            showPage('login-page');
            return null;
        }
    }

    return response;
}

/**
 * Refreshes the access token using the refresh token.
 */
async function refreshAccessToken() {
    try {
        const response = await fetch(`${API_BASE}/auth/login/refresh/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ refresh: getRefreshToken() }),
        });

        if (response.ok) {
            const data = await response.json();
            saveTokens(data.access, data.refresh || getRefreshToken());
            return true;
        }
        return false;
    } catch {
        return false;
    }
}

// ===== AUTH API =====

async function apiLogin(username, password) {
    const response = await fetch(`${API_BASE}/auth/login/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password }),
    });
    const data = await response.json();
    if (response.ok) {
        saveTokens(data.access, data.refresh);
    }
    return { ok: response.ok, data };
}

async function apiRegister(formData) {
    const response = await fetch(`${API_BASE}/auth/register/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData),
    });
    const data = await response.json();
    if (response.ok && data.data && data.data.tokens) {
        saveTokens(data.data.tokens.access, data.data.tokens.refresh);
    }
    return { ok: response.ok, data };
}

async function apiGetProfile() {
    const response = await apiRequest('/auth/profile/');
    if (!response) return null;
    const data = await response.json();
    return response.ok ? data.data : null;
}

async function apiLogout() {
    const refresh = getRefreshToken();
    if (refresh) {
        await apiRequest('/auth/logout/', {
            method: 'POST',
            body: JSON.stringify({ refresh }),
        });
    }
    clearTokens();
}

// ===== DASHBOARD API =====

async function apiGetDashboard(month, year) {
    const params = new URLSearchParams();
    if (month) params.append('month', month);
    if (year) params.append('year', year);
    const query = params.toString() ? `?${params.toString()}` : '';
    const response = await apiRequest(`/dashboard/${query}`);
    if (!response) return null;
    const data = await response.json();
    return response.ok ? data.data : null;
}

// ===== CATEGORIES API =====

async function apiGetCategories() {
    const response = await apiRequest('/categories/');
    if (!response) return [];
    const data = await response.json();
    return response.ok ? (data.data || []) : [];
}

// ===== INCOME API =====

async function apiGetIncomes() {
    const response = await apiRequest('/incomes/');
    if (!response) return [];
    const data = await response.json();
    return data.results || data.data || [];
}

async function apiCreateIncome(incomeData) {
    const response = await apiRequest('/incomes/', {
        method: 'POST',
        body: JSON.stringify(incomeData),
    });
    if (!response) return { ok: false };
    const data = await response.json();
    return { ok: response.ok, data };
}

async function apiDeleteIncome(id) {
    const response = await apiRequest(`/incomes/${id}/`, { method: 'DELETE' });
    return response && response.ok;
}

// ===== EXPENSES API =====

async function apiGetExpenses(params = {}) {
    const query = new URLSearchParams();
    if (params.category) query.append('category', params.category);
    if (params.month) {
        const [year, month] = params.month.split('-');
        query.append('month', month);
        query.append('year', year);
    }
    if (params.search) query.append('search', params.search);
    const queryStr = query.toString() ? `?${query.toString()}` : '';
    const response = await apiRequest(`/expenses/${queryStr}`);
    if (!response) return [];
    const data = await response.json();
    return data.results || data.data || [];
}

async function apiCreateExpense(expenseData) {
    const response = await apiRequest('/expenses/', {
        method: 'POST',
        body: JSON.stringify(expenseData),
    });
    if (!response) return { ok: false };
    const data = await response.json();
    return { ok: response.ok, data };
}

async function apiDeleteExpense(id) {
    const response = await apiRequest(`/expenses/${id}/`, { method: 'DELETE' });
    return response && response.ok;
}

// ===== SAVINGS API =====

async function apiGetSavings() {
    const response = await apiRequest('/savings/');
    if (!response) return [];
    const data = await response.json();
    return data.results || data.data || [];
}

async function apiGetSavingsSummary() {
    const response = await apiRequest('/savings/summary/');
    if (!response) return null;
    const data = await response.json();
    return response.ok ? data.data : null;
}

async function apiCreateSaving(savingData) {
    const response = await apiRequest('/savings/', {
        method: 'POST',
        body: JSON.stringify(savingData),
    });
    if (!response) return { ok: false };
    const data = await response.json();
    return { ok: response.ok, data };
}

async function apiDeleteSaving(id) {
    const response = await apiRequest(`/savings/${id}/`, { method: 'DELETE' });
    return response && response.ok;
}

// ===== BUDGETS API =====

async function apiGetBudgets(month, year) {
    const params = new URLSearchParams();
    if (month) params.append('month', month);
    if (year) params.append('year', year);
    const query = params.toString() ? `?${params.toString()}` : '';
    const response = await apiRequest(`/budgets/${query}`);
    if (!response) return [];
    const data = await response.json();
    return data.results || data.data || [];
}

async function apiCreateBudget(budgetData) {
    const response = await apiRequest('/budgets/', {
        method: 'POST',
        body: JSON.stringify(budgetData),
    });
    if (!response) return { ok: false };
    const data = await response.json();
    return { ok: response.ok, data };
}

async function apiDeleteBudget(id) {
    const response = await apiRequest(`/budgets/${id}/`, { method: 'DELETE' });
    return response && response.ok;
}


// ===== CONTACTS (KHATABOOK) API =====

async function apiGetContacts() {
    const response = await apiRequest('/contacts/');
    if (!response) return [];
    const data = await response.json();
    return data.results || data.data || [];
}

async function apiCreateContact(contactData) {
    const response = await apiRequest('/contacts/', {
        method: 'POST',
        body: JSON.stringify(contactData),
    });
    if (!response) return { ok: false };
    const data = await response.json();
    return { ok: response.ok, data };
}

async function apiDeleteContact(id) {
    const response = await apiRequest(`/contacts/${id}/`, { method: 'DELETE' });
    return response && response.ok;
}

// ===== LEDGER API =====

async function apiGetLedgerEntries(contactId) {
    const query = contactId ? `?contact_id=${contactId}` : '';
    const endpoint = contactId ? `/ledger/by-contact/${query}` : '/ledger/';
    const response = await apiRequest(endpoint);
    if (!response) return [];
    const data = await response.json();
    return data.results || data.data || [];
}

async function apiCreateLedgerEntry(entryData) {
    const response = await apiRequest('/ledger/', {
        method: 'POST',
        body: JSON.stringify(entryData),
    });
    if (!response) return { ok: false };
    const data = await response.json();
    return { ok: response.ok, data };
}

async function apiDeleteLedgerEntry(id) {
    const response = await apiRequest(`/ledger/${id}/`, { method: 'DELETE' });
    return response && response.ok;
}

async function apiSendReminder(contactId) {
    const response = await apiRequest('/ledger/send-reminder/', {
        method: 'POST',
        body: JSON.stringify({ contact_id: contactId }),
    });
    if (!response) return { ok: false };
    const data = await response.json();
    return { ok: response.ok, data };
}
