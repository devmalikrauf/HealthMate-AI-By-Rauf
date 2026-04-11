const API = "/api";

function authHeaders() {
  const token = localStorage.getItem("hm_token");
  return token ? { Authorization: `Bearer ${token}` } : {};
}

async function request(url, options = {}) {
  const res = await fetch(url, {
    ...options,
    headers: { ...authHeaders(), ...options.headers },
  });
  if (res.status === 401) {
    localStorage.removeItem("hm_token");
    localStorage.removeItem("hm_user");
    window.location.href = "/login";
    throw new Error("Session expired");
  }
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || `Error ${res.status}`);
  }
  return res.json();
}

export const auth = {
  register: (data) =>
    request(`${API}/auth/register`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    }),
  login: (data) =>
    request(`${API}/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    }),
  me: () => request(`${API}/auth/me`),
};

export const scan = {
  analyze: (file) => {
    const fd = new FormData();
    fd.append("file", file);
    return request(`${API}/analyze`, { method: "POST", body: fd });
  },
  history: () => request(`${API}/history`),
};

export const feedback = {
  submit: (data) =>
    request(`${API}/feedback`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    }),
};

export const admin = {
  dashboard: () => request(`${API}/admin/dashboard`),
  users: () => request(`${API}/admin/users`),
  scans: () => request(`${API}/admin/scans`),
};

export const medicines = {
  list: () => request(`${API}/medicines`),
};
