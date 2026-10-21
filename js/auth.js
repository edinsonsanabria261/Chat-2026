let session = null;

function csrfToken() {
  const part = document.cookie.split("; ").find((row) => row.startsWith("nexus_csrf="));
  return part ? decodeURIComponent(part.slice("nexus_csrf=".length)) : "";
}

export async function api(path, options = {}) {
  const headers = { ...(options.headers || {}) };
  if (options.body) {
    headers["Content-Type"] = "application/json";
    headers["X-CSRF-Token"] = csrfToken();
  }
  const response = await fetch(path, {
    credentials: "same-origin",
    ...options,
    headers,
  });
  const data = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(data.error || "No se pudo completar la acción.");
  return data;
}

async function request(path, payload) {
  try {
    const data = await api(path, payload ? { method: "POST", body: JSON.stringify(payload) } : {});
    return { ok: true, data };
  } catch (error) {
    return { ok: false, error: error.message };
  }
}

export function currentSession() {
  return session;
}

export async function refreshSession() {
  try {
    session = await api("/api/me");
  } catch {
    session = null;
  }
  return session;
}

export async function registerUser(payload) {
  const result = await request("/api/register", payload);
  if (result.ok) session = result.data;
  return result;
}

export async function loginUser(username, password) {
  const result = await request("/api/login", { username, password });
  if (result.ok) session = result.data;
  return result;
}

export async function logoutUser() {
  await request("/api/logout", {});
  session = null;
}
