const BASE_URL = import.meta.env.VITE_API_BASE_URL || (
  typeof window !== "undefined" && (window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1")
    ? "http://localhost:8080/api/v1"
    : "/api/v1"
);

// ── Auth token storage ────────────────────────────────────────────────
// Ported over from the guardian-v2 frontend: every request now carries a
// bearer token (read fresh from localStorage each call, same pattern as an
// axios request interceptor), and a 401 clears the stored session.
const TOKEN_KEY = "abg_access_token";

export function getToken() {
  return localStorage.getItem(TOKEN_KEY);
}

export function setToken(token) {
  if (token) localStorage.setItem(TOKEN_KEY, token);
}

export function clearToken() {
  localStorage.removeItem(TOKEN_KEY);
}

async function request(path, { method = "GET", body } = {}) {
  const token = getToken();
  const headers = {};
  if (body) headers["Content-Type"] = "application/json";
  if (token) headers["Authorization"] = `Bearer ${token}`;

  const res = await fetch(`${BASE_URL}${path}`, {
    method,
    headers,
    body: body ? JSON.stringify(body) : undefined,
  });
  if (res.status === 401) {
    clearToken();
  }
  if (!res.ok) {
    let detail = "";
    try { detail = (await res.json()).detail || ""; } catch { /* ignore */ }
    throw new Error(`${path} -> HTTP ${res.status}${detail ? `: ${detail}` : ""}`);
  }
  return res.json();
}

export const api = {
  // auth
  register: (payload) => request("/auth/register", { method: "POST", body: payload }),
  login: (payload) => request("/auth/login", { method: "POST", body: payload }),

  // per-user behavioral data
  getTrust: (userId) => request(`/trust/${userId}`),
  getRisk: (userId) => request(`/risk/${userId}`),
  getAlerts: (userId) => request(`/alerts/${userId}`),
  getHistory: (userId) => request(`/history/${userId}`),
  getSession: (userId) => request(`/session/${userId}`),

  // users / roster
  getUsers: (organization) =>
    request(`/users${organization ? `?organization=${encodeURIComponent(organization)}` : ""}`),
  getUser: (userId) => request(`/users/${userId}`),
  updateUser: (userId, payload) => request(`/users/${userId}`, { method: "PATCH", body: payload }),

  // settings
  getSettings: (userId) => request(`/settings/${userId}`),
  updateSettings: (userId, payload) => request(`/settings/${userId}`, { method: "PUT", body: payload }),

  // device pairing — exchanges the current session token for a long-lived
  // (30 day) token the desktop agent can use, so the person never types
  // their password into a terminal.
  connectDevice: () => request("/auth/device-token", { method: "POST" }),

  // analytics
  getAnalytics: (userId, { organization, days = 7 } = {}) => {
    const qs = new URLSearchParams({ days: String(days) });
    if (organization) qs.set("organization", organization);
    return request(`/analytics/${userId}?${qs.toString()}`);
  },
};

// Real backend response shapes (see behavioral_guardian/backend/schemas/models.py):
//   TrustResponse:   { user_id, identity_trust, status_level }
//   RiskResponse:    { user_id, activity_risk }
//   AlertResponse[]: { id, severity, title, message, is_read, created_at }
//   HistoryResponse: { user_id, trust_history: [{created_at,score,label}], risk_history: [...] }
//   status_level / severity values are one of:
//     NORMAL, ELEVATED, SUSPICIOUS, HIGH_RISK, CRITICAL
