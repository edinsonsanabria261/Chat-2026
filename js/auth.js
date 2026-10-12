let session = null;

async function request(path, payload) {
  const response = await fetch(path, {
    method: payload ? "POST" : "GET",
    credentials: "same-origin",
    headers: payload ? { "Content-Type": "application/json" } : undefined,
    body: payload ? JSON.stringify(payload) : undefined,
  });
  const data = await response.json().catch(() => ({}));
  if (!response.ok) return { ok: false, error: data.error || "No se pudo completar la acción." };
  return { ok: true, data };
}

export function currentSession() {
  return session;
}

export async function refreshSession() {
  const result = await request("/api/me");
  session = result.ok ? result.data : null;
  return session;
}

export async function registerUser({ username, nombre, password }) {
  return request("/api/register", { username, nombre, password });
}

export async function loginUser(username, password) {
  const result = await request("/api/login", { username, password });
  if (!result.ok) return result;
  session = result.data;
  return { ok: true };
}

export async function logoutUser() {
  await request("/api/logout", {});
  session = null;
}
