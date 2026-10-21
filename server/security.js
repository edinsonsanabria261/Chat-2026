import crypto from "node:crypto";

const SCRYPT = { N: 16384, r: 8, p: 1, maxmem: 64 * 1024 * 1024 };
const DUMMY_SALT = crypto.randomBytes(16).toString("base64url");
const DUMMY_HASH = crypto.scryptSync("dummy-password", DUMMY_SALT, 32, SCRYPT).toString("base64url");

const vaultKeys = new Map();
const hits = new Map();

export function rememberVaultKey(sessionId, key) {
  vaultKeys.set(sessionId, key);
}

export function vaultKeyFor(sessionId) {
  return vaultKeys.get(sessionId) || null;
}

export function forgetVaultKey(sessionId) {
  vaultKeys.delete(sessionId);
}

export async function deriveVaultKey(password, salt) {
  return scryptBuffer(password, salt);
}

function scryptBuffer(password, salt) {
  return new Promise((resolve, reject) => {
    crypto.scrypt(password, salt, 32, SCRYPT, (error, derived) => {
      if (error) reject(error);
      else resolve(derived);
    });
  });
}

export function sealVault(key, vault) {
  const iv = crypto.randomBytes(12);
  const cipher = crypto.createCipheriv("aes-256-gcm", key, iv);
  const data = Buffer.concat([cipher.update(JSON.stringify(vault), "utf8"), cipher.final()]);
  return {
    v: 1,
    iv: iv.toString("base64url"),
    tag: cipher.getAuthTag().toString("base64url"),
    data: data.toString("base64url"),
  };
}

export function openVault(key, blob) {
  const decipher = crypto.createDecipheriv("aes-256-gcm", key, Buffer.from(blob.iv, "base64url"));
  decipher.setAuthTag(Buffer.from(blob.tag, "base64url"));
  const text = Buffer.concat([
    decipher.update(Buffer.from(blob.data, "base64url")),
    decipher.final(),
  ]).toString("utf8");
  return JSON.parse(text);
}

export function hashToken(token) {
  return crypto.createHash("sha256").update(token).digest("hex");
}

export function sameSecret(left, right) {
  const a = Buffer.from(String(left));
  const b = Buffer.from(String(right));
  if (a.length !== b.length) return false;
  return crypto.timingSafeEqual(a, b);
}

function scrypt(password, salt) {
  return scryptBuffer(password, salt).then((derived) => derived.toString("base64url"));
}

function pbkdf2(password, salt) {
  return new Promise((resolve, reject) => {
    crypto.pbkdf2(password, salt, 120000, 32, "sha256", (error, derived) => {
      if (error) reject(error);
      else resolve(derived.toString("base64url"));
    });
  });
}

export async function hashPassword(password) {
  const salt = crypto.randomBytes(16).toString("base64url");
  return { algo: "scrypt", salt, hash: await scrypt(password, salt) };
}

export async function passwordMatches(password, user) {
  if (!user) {
    await scrypt(password, DUMMY_SALT);
    return sameSecret(DUMMY_HASH, DUMMY_HASH) && false;
  }
  const derived = user.algo === "pbkdf2"
    ? await pbkdf2(password, user.salt)
    : await scrypt(password, user.salt);
  return sameSecret(derived, user.hash);
}

export function clientIp(req) {
  const forwarded = String(req.headers["x-forwarded-for"] || "").split(",")[0].trim();
  return forwarded || req.ip || "local";
}

export function tooManyAttempts(key, limit, windowMs) {
  const now = Date.now();
  const entry = hits.get(key);
  if (!entry || entry.reset < now) {
    hits.set(key, { count: 1, reset: now + windowMs });
    return false;
  }
  entry.count += 1;
  return entry.count > limit;
}

export function passwordProblem(password) {
  if (typeof password !== "string" || password.length < 8) {
    return "La contraseña necesita al menos 8 caracteres.";
  }
  if (password.length > 128) return "La contraseña es demasiado larga.";
  return "";
}

export function usernameKey(value) {
  return String(value || "").trim().toLowerCase();
}

export function usernameProblem(username) {
  if (!/^[a-z0-9][a-z0-9._-]{2,31}$/.test(username)) {
    return "El usuario debe tener de 3 a 32 caracteres: letras, números, punto o guion, sin espacios.";
  }
  return "";
}

export function applyHeaders(res) {
  res.setHeader("X-Content-Type-Options", "nosniff");
  res.setHeader("X-Frame-Options", "DENY");
  res.setHeader("Referrer-Policy", "no-referrer");
  res.setHeader("Permissions-Policy", "camera=(), microphone=(), geolocation=()");
  res.setHeader(
    "Content-Security-Policy",
    "default-src 'self'; style-src 'self'; script-src 'self'; img-src 'self' data:; base-uri 'self'; form-action 'self'; frame-ancestors 'none'",
  );
}

export function readCookie(req, name) {
  const source = req.headers.cookie || "";
  for (const part of source.split(";")) {
    const [key, ...rest] = part.trim().split("=");
    if (key === name) return decodeURIComponent(rest.join("="));
  }
  return "";
}

export function writeSession(res, { token, csrf }) {
  const secure = process.env.NODE_ENV === "production" ? "; Secure" : "";
  const week = 7 * 24 * 60 * 60;
  res.setHeader("Set-Cookie", [
    `nexus_sid=${encodeURIComponent(token)}; HttpOnly; SameSite=Lax; Path=/; Max-Age=${week}${secure}`,
    `nexus_csrf=${encodeURIComponent(csrf)}; SameSite=Lax; Path=/; Max-Age=${week}${secure}`,
  ]);
}

export function clearSession(res) {
  const secure = process.env.NODE_ENV === "production" ? "; Secure" : "";
  res.setHeader("Set-Cookie", [
    `nexus_sid=; HttpOnly; SameSite=Lax; Path=/; Max-Age=0${secure}`,
    `nexus_csrf=; SameSite=Lax; Path=/; Max-Age=0${secure}`,
  ]);
}

export function sameOrigin(req) {
  const origin = req.get("origin");
  if (!origin) return true;
  try {
    return new URL(origin).host === req.get("host");
  } catch {
    return false;
  }
}

export function csrfOk(req, session) {
  const header = String(req.get("x-csrf-token") || "");
  const fromCookie = readCookie(req, "nexus_csrf");
  if (!session?.csrf || !header || !fromCookie) return false;
  return sameSecret(header, session.csrf) && sameSecret(fromCookie, session.csrf);
}
