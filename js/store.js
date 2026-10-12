const USERS = "nexus.users.v1";
const APPS = "nexus.apps.v1";
const SESSION = "nexus.session.v1";

const SAMPLE_APPS = {
  "App Auditoría Red": {
    url: "https://streamlit.io",
    descripcion: "Herramienta de análisis de nodos y puertos perimetrales.",
    categoria: "Ciberseguridad",
    permiso: "Libre",
    estado: "Activa",
    version: "v1.0.0",
  },
};

function read(storage, key, fallback) {
  try {
    const raw = storage.getItem(key);
    return raw ? JSON.parse(raw) : fallback;
  } catch {
    return fallback;
  }
}

function write(storage, key, value) {
  storage.setItem(key, JSON.stringify(value));
}

export function loadUsers() {
  return read(localStorage, USERS, {});
}

export function saveUsers(users) {
  write(localStorage, USERS, users);
}

export function loadApps() {
  const apps = read(localStorage, APPS, null);
  if (!apps) {
    write(localStorage, APPS, SAMPLE_APPS);
    return structuredClone(SAMPLE_APPS);
  }
  return apps;
}

export function saveApps(apps) {
  write(localStorage, APPS, apps);
}

export function loadSession() {
  return read(sessionStorage, SESSION, null);
}

export function saveSession(session) {
  write(sessionStorage, SESSION, session);
}

export function clearSession() {
  sessionStorage.removeItem(SESSION);
}
