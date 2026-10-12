import { clearSession, loadSession, loadUsers, saveSession, saveUsers } from "./store.js";

function bytesToB64(bytes) {
  let text = "";
  bytes.forEach((byte) => {
    text += String.fromCharCode(byte);
  });
  return btoa(text);
}

function b64ToBytes(value) {
  const text = atob(value);
  const bytes = new Uint8Array(text.length);
  for (let i = 0; i < text.length; i += 1) bytes[i] = text.charCodeAt(i);
  return bytes;
}

function sameText(left, right) {
  if (left.length !== right.length) return false;
  let diff = 0;
  for (let i = 0; i < left.length; i += 1) diff |= left.charCodeAt(i) ^ right.charCodeAt(i);
  return diff === 0;
}

export async function hashPassword(password, saltB64) {
  if (!crypto.subtle) {
    throw new Error("Abre el portal en HTTPS o con un servidor local. Un archivo suelto no puede proteger la contraseña.");
  }
  const salt = saltB64 ? b64ToBytes(saltB64) : crypto.getRandomValues(new Uint8Array(16));
  const key = await crypto.subtle.importKey("raw", new TextEncoder().encode(password), "PBKDF2", false, ["deriveBits"]);
  const bits = await crypto.subtle.deriveBits(
    { name: "PBKDF2", salt, iterations: 120000, hash: "SHA-256" },
    key,
    256,
  );
  return { salt: bytesToB64(salt), hash: bytesToB64(new Uint8Array(bits)) };
}

export function currentSession() {
  return loadSession();
}

export async function registerUser({ username, nombre, password }) {
  const user = username.trim();
  if (!/^[a-zA-Z0-9._-]{3,32}$/.test(user)) {
    return { ok: false, error: "El usuario debe tener 3 a 32 caracteres, sin espacios." };
  }
  if (password.length < 8) return { ok: false, error: "La contraseña necesita al menos 8 caracteres." };
  const users = loadUsers();
  if (users[user]) return { ok: false, error: "El usuario ya existe." };
  const secret = await hashPassword(password);
  users[user] = {
    nombre: nombre.trim() || user,
    rol: Object.keys(users).length === 0 ? "Administrador Principal" : "Operador",
    salt: secret.salt,
    hash: secret.hash,
  };
  saveUsers(users);
  return { ok: true };
}

export async function loginUser(username, password) {
  const users = loadUsers();
  const record = users[username.trim()];
  if (!record) return { ok: false, error: "Credenciales inválidas." };
  const secret = await hashPassword(password, record.salt);
  if (!sameText(secret.hash, record.hash)) return { ok: false, error: "Credenciales inválidas." };
  saveSession({
    username: username.trim(),
    nombre: record.nombre,
    rol: record.rol,
  });
  return { ok: true };
}

export async function confirmPassword(password) {
  const session = currentSession();
  if (!session) return false;
  const record = loadUsers()[session.username];
  if (!record) return false;
  const secret = await hashPassword(password, record.salt);
  return sameText(secret.hash, record.hash);
}

export function logoutUser() {
  clearSession();
}
