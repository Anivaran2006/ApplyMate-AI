/**
 * ApplyMate AI – Shared API Client
 * Wraps fetch with auth headers, auto-refresh, and error handling.
 */

const API_BASE = window.API_BASE_URL || 'http://localhost:8000/api/v1';

// ── Token Management ─────────────────────────────────────────
const Auth = {
  getAccessToken()  { return localStorage.getItem('am_access_token'); },
  getRefreshToken() { return localStorage.getItem('am_refresh_token'); },
  getUserData()     { return JSON.parse(localStorage.getItem('am_user') || 'null'); },

  setTokens(data) {
    localStorage.setItem('am_access_token', data.access_token);
    localStorage.setItem('am_refresh_token', data.refresh_token);
    localStorage.setItem('am_user', JSON.stringify({
      id: data.user_id,
      full_name: data.full_name,
      email: data.email,
    }));
  },

  clear() {
    localStorage.removeItem('am_access_token');
    localStorage.removeItem('am_refresh_token');
    localStorage.removeItem('am_user');
  },

  isLoggedIn() { return !!this.getAccessToken(); },

  redirectToLogin() {
    this.clear();
    window.location.href = '/login.html';
  }
};

// ── Refresh Access Token ─────────────────────────────────────
let _refreshing = null;

async function refreshAccessToken() {
  if (_refreshing) return _refreshing;

  _refreshing = (async () => {
    const refresh = Auth.getRefreshToken();
    if (!refresh) { Auth.redirectToLogin(); return false; }

    try {
      const resp = await fetch(`${API_BASE}/auth/refresh`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ refresh_token: refresh }),
      });
      if (!resp.ok) { Auth.redirectToLogin(); return false; }
      const data = await resp.json();
      Auth.setTokens(data);
      return true;
    } catch {
      Auth.redirectToLogin();
      return false;
    } finally {
      _refreshing = null;
    }
  })();

  return _refreshing;
}

// ── Core Fetch Wrapper ───────────────────────────────────────
async function apiFetch(endpoint, options = {}, retry = true) {
  const token = Auth.getAccessToken();
  const headers = {
    'Content-Type': 'application/json',
    ...(token ? { 'Authorization': `Bearer ${token}` } : {}),
    ...(options.headers || {}),
  };

  let resp;
  try {
    resp = await fetch(`${API_BASE}${endpoint}`, {
      ...options,
      headers,
    });
  } catch (err) {
    throw new Error('Network error. Please check your connection.');
  }

  // Auto-refresh on 401
  if (resp.status === 401 && retry) {
    const refreshed = await refreshAccessToken();
    if (refreshed) return apiFetch(endpoint, options, false);
    return;
  }

  if (!resp.ok) {
    const err = await resp.json().catch(() => ({ detail: 'Unknown error' }));
    throw new Error(err.detail || `Request failed (${resp.status})`);
  }

  // No content
  if (resp.status === 204) return null;

  return resp.json();
}

// ── API Endpoints ────────────────────────────────────────────
const API = {
  // Auth
  auth: {
    signup: (data) => apiFetch('/auth/signup', { method: 'POST', body: JSON.stringify(data) }),
    login:  (data) => apiFetch('/auth/login',  { method: 'POST', body: JSON.stringify(data) }),
    logout: ()     => { Auth.clear(); window.location.href = '/login.html'; },
    forgotPassword: (email) => apiFetch('/auth/forgot-password', { method: 'POST', body: JSON.stringify({ email }) }),
    resetPassword:  (token, password) => apiFetch('/auth/reset-password', { method: 'POST', body: JSON.stringify({ token, new_password: password }) }),
  },

  // User
  user: {
    me:                  ()     => apiFetch('/users/me'),
    update:              (data) => apiFetch('/users/me',              { method: 'PUT', body: JSON.stringify(data) }),
    changePassword:      (data) => apiFetch('/users/me/password',     { method: 'PUT', body: JSON.stringify(data) }),
    updateNotifications: (data) => apiFetch('/users/me/notifications', { method: 'PUT', body: JSON.stringify(data) }),
    connectTelegram:     (chatId) => apiFetch('/users/me/telegram/connect', { method: 'POST', body: JSON.stringify({ chat_id: chatId }) }),
    disconnectTelegram:  ()     => apiFetch('/users/me/telegram',     { method: 'DELETE' }),
  },

  // Subscriptions
  subscriptions: {
    list:        ()         => apiFetch('/subscriptions'),
    add:         (category) => apiFetch('/subscriptions',             { method: 'POST', body: JSON.stringify({ category }) }),
    remove:      (category) => apiFetch(`/subscriptions/${category}`, { method: 'DELETE' }),
    bulkUpdate:  (cats)     => apiFetch('/subscriptions/bulk',        { method: 'PUT',  body: JSON.stringify({ categories: cats }) }),
  },

  // Notices
  notices: {
    list:      (params = {}) => {
      const q = new URLSearchParams(params).toString();
      return apiFetch(`/notices${q ? '?' + q : ''}`);
    },
    getById:   (id)          => apiFetch(`/notices/${id}`),
    aiAction:  (id, action)  => apiFetch(`/notices/${id}/ai-action`, { method: 'POST', body: JSON.stringify({ action }) }),
  },

  // Bookmarks
  bookmarks: {
    list:   ()   => apiFetch('/bookmarks'),
    add:    (id) => apiFetch(`/bookmarks/${id}`, { method: 'POST' }),
    remove: (id) => apiFetch(`/bookmarks/${id}`, { method: 'DELETE' }),
  },

  // Notifications
  notifications: {
    history: (page = 1) => apiFetch(`/notifications/history?page=${page}`),
  },

  // Admin
  admin: {
    login:      (data)   => apiFetch('/admin/login',              { method: 'POST', body: JSON.stringify(data) }),
    stats:      ()       => apiFetch('/admin/stats'),
    users:      (params) => { const q = new URLSearchParams(params).toString(); return apiFetch(`/admin/users${q ? '?' + q : ''}`); },
    deleteUser: (id)     => apiFetch(`/admin/users/${id}`,        { method: 'DELETE' }),
    notices:    (params) => { const q = new URLSearchParams(params).toString(); return apiFetch(`/admin/notices${q ? '?' + q : ''}`); },
    scrapeNow:  ()       => apiFetch('/admin/notices/scrape-now', { method: 'POST' }),
    logs:       (page)   => apiFetch(`/admin/logs?page=${page}`),
    exportCSV:  ()       => `${API_BASE}/admin/export/users`,
  },
};

// ── Toast Utility ────────────────────────────────────────────
function showToast(message, type = 'info', duration = 4000) {
  let container = document.getElementById('toastContainer');
  if (!container) {
    container = document.createElement('div');
    container.id = 'toastContainer';
    container.className = 'toast-container';
    document.body.appendChild(container);
  }

  const toast = document.createElement('div');
  toast.className = `toast ${type}`;
  const icons = { success: '✅', error: '❌', info: 'ℹ️', warning: '⚠️' };
  toast.innerHTML = `<span>${icons[type] || 'ℹ️'}</span><span>${message}</span>`;
  container.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateX(60px)';
    toast.style.transition = '0.3s ease';
    setTimeout(() => toast.remove(), 300);
  }, duration);
}

// ── Route Guard ──────────────────────────────────────────────
function requireAuth() {
  if (!Auth.isLoggedIn()) {
    window.location.href = '/login.html';
    return false;
  }
  return true;
}

function requireGuest() {
  if (Auth.isLoggedIn()) {
    window.location.href = '/dashboard.html';
    return false;
  }
  return true;
}

// ── Category Config ──────────────────────────────────────────
const CATEGORIES = [
  { id: 'NEET',         emoji: '🩺', label: 'NEET',         color: '#ef4444' },
  { id: 'JEE',          emoji: '⚡', label: 'JEE',          color: '#3b82f6' },
  { id: 'CUET',         emoji: '🎓', label: 'CUET',         color: '#8b5cf6' },
  { id: 'GATE',         emoji: '🔬', label: 'GATE',         color: '#10b981' },
  { id: 'CAT',          emoji: '📊', label: 'CAT',          color: '#f59e0b' },
  { id: 'UPSC',         emoji: '🏛️', label: 'UPSC',         color: '#6366f1' },
  { id: 'SSC',          emoji: '📋', label: 'SSC',          color: '#14b8a6' },
  { id: 'BANKING',      emoji: '🏦', label: 'Banking',      color: '#f97316' },
  { id: 'SCHOLARSHIPS', emoji: '🌟', label: 'Scholarships', color: '#ec4899' },
];
