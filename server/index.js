import path from "node:path";
import crypto from "node:crypto";
import { fileURLToPath } from "node:url";
import express from "express";
import { freshVault, updateDb } from "./db.js";
import {
  applyHeaders,
  clearSession,
  clientIp,
  csrfOk,
  deriveVaultKey,
  forgetVaultKey,
  hashPassword,
  hashToken,
  openVault,
  passwordMatches,
  passwordProblem,
  readCookie,
  rememberVaultKey,
  sameOrigin,
  sealVault,
  tooManyAttempts,
  usernameKey,
  usernameProblem,
  vaultKeyFor,
  writeSession,
} from "./security.js";

const app = express();
const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const WEEK = 7 * 24 * 60 * 60 * 1000;
const LOCK = 15 * 60 * 1000;

app.disable("x-powered-by");
app.set("trust proxy", 1);
app.use(express.json({ limit: "32kb" }));
app.use((_req, res, next) => {
  applyHeaders(res);
  next();
});

function publicUser(username, user) {
  return { username, nombre: user.nombre, rol: user.rol };
}

function findUser(db, username) {
  if (db.users[username]) return { key: username, user: db.users[username] };
  const found = Object.keys(db.users).find((name) => name.toLowerCase() === username);
  return found ? { key: found, user: db.users[found] } : { key: username, user: null };
}

function sessionOf(db, req) {
  const token = readCookie(req, "nexus_sid");
  if (!token) return null;
  const id = hashToken(token);
  const session = db.sessions[id];
  if (!session || session.expires < Date.now()) return null;
  if (!db.users[session.username]) return null;
  if (!vaultKeyFor(id)) return null;
  return { ...session, id };
}

function openSession(db, username) {
  const token = crypto.randomBytes(32).toString("base64url");
  const csrf = crypto.randomBytes(32).toString("base64url");
  db.sessions[hashToken(token)] = { username, csrf, expires: Date.now() + WEEK };
  return { token, csrf };
}

function requireUser(req, db) {
  if (!sameOrigin(req)) return { error: "Solicitud rechazada.", status: 403 };
  const session = sessionOf(db, req);
  if (!session) return { error: "Sin sesión.", status: 401 };
  if (!csrfOk(req, session)) return { error: "La protección de la sesión caducó. Vuelve a entrar.", status: 403 };
  return { session, user: publicUser(session.username, db.users[session.username]) };
}

app.get("/api/me", (req, res) => {
  updateDb((db) => {
    const session = sessionOf(db, req);
    if (!session) return null;
    if (!session.csrf) session.csrf = crypto.randomBytes(32).toString("base64url");
    return { session, user: publicUser(session.username, db.users[session.username]) };
  }).then((result) => {
    if (!result) return res.status(401).json({ error: "Sin sesión." });
    writeSession(res, { token: readCookie(req, "nexus_sid"), csrf: result.session.csrf });
    res.json(result.user);
  }).catch(() => res.status(500).json({ error: "No se pudo leer la sesión." }));
});

app.post("/api/register", (req, res) => {
  if (!sameOrigin(req)) return res.status(403).json({ error: "Solicitud rechazada." });
  if (tooManyAttempts(`reg:${clientIp(req)}`, 8, 10 * 60 * 1000)) {
    return res.status(429).json({ error: "Demasiados intentos. Espera unos minutos." });
  }
  const username = usernameKey(req.body?.username);
  const nombre = String(req.body?.nombre || "").trim().slice(0, 80);
  const password = String(req.body?.password || "");
  const confirm = String(req.body?.confirm || "");
  const userError = usernameProblem(username);
  if (userError) return res.status(400).json({ error: userError });
  const passError = passwordProblem(password);
  if (passError) return res.status(400).json({ error: passError });
  if (password !== confirm) return res.status(400).json({ error: "Las contraseñas no coinciden." });

  hashPassword(password).then(async (secret) => {
    const vaultSalt = crypto.randomBytes(16).toString("base64url");
    const vaultKey = await deriveVaultKey(password, vaultSalt);
    return updateDb((db) => {
      if (findUser(db, username).user) return { error: "Ese usuario ya existe.", status: 409 };
      db.users[username] = {
        nombre: nombre || username,
        rol: Object.keys(db.users).length === 0 ? "Administrador Principal" : "Usuario",
        algo: secret.algo,
        salt: secret.salt,
        hash: secret.hash,
        vaultSalt,
        failed: 0,
        lockedUntil: 0,
      };
      const opened = openSession(db, username);
      db.vaults[username] = sealVault(vaultKey, freshVault());
      rememberVaultKey(hashToken(opened.token), vaultKey);
      return { session: opened, user: publicUser(username, db.users[username]) };
    });
  }).then((result) => {
    if (result.error) return res.status(result.status || 400).json({ error: result.error });
    writeSession(res, result.session);
    res.status(201).json(result.user);
  }).catch(() => res.status(500).json({ error: "No se pudo crear la cuenta." }));
});

app.post("/api/login", (req, res) => {
  if (!sameOrigin(req)) return res.status(403).json({ error: "Solicitud rechazada." });
  const ip = clientIp(req);
  if (tooManyAttempts(`login:${ip}`, 10, 10 * 60 * 1000)) {
    return res.status(429).json({ error: "Demasiados intentos. Espera unos minutos." });
  }
  const username = usernameKey(req.body?.username);
  const password = String(req.body?.password || "");
  updateDb(async (db) => {
    const found = findUser(db, username);
    if (found.user?.lockedUntil > Date.now()) {
      return { error: "Demasiados intentos. Espera unos minutos.", status: 429 };
    }
    const matches = await passwordMatches(password, found.user);
    if (!found.user || !matches) {
      if (found.user) {
        found.user.failed = (found.user.failed || 0) + 1;
        if (found.user.failed >= 5) {
          found.user.lockedUntil = Date.now() + LOCK;
          found.user.failed = 0;
        }
      }
      return { error: "Usuario o contraseña incorrectos.", status: 401 };
    }
    found.user.failed = 0;
    found.user.lockedUntil = 0;
    if (!found.user.vaultSalt) found.user.vaultSalt = crypto.randomBytes(16).toString("base64url");
    const vaultKey = await deriveVaultKey(password, found.user.vaultSalt);
    const blob = db.vaults[found.key];
    if (!blob?.v) db.vaults[found.key] = sealVault(vaultKey, blob?.apps ? blob : freshVault());
    for (const [key, session] of Object.entries(db.sessions)) {
      if (session.username === found.key) {
        forgetVaultKey(key);
        delete db.sessions[key];
      }
    }
    const opened = openSession(db, found.key);
    rememberVaultKey(hashToken(opened.token), vaultKey);
    return { session: opened, user: publicUser(found.key, found.user) };
  }).then((result) => {
    if (result.error) return res.status(result.status || 401).json({ error: result.error });
    writeSession(res, result.session);
    res.json(result.user);
  }).catch(() => res.status(500).json({ error: "No se pudo entrar." }));
});

app.post("/api/logout", (req, res) => {
  updateDb((db) => {
    const session = sessionOf(db, req);
    if (session && csrfOk(req, session)) {
      forgetVaultKey(session.id);
      delete db.sessions[session.id];
    }
  }).then(() => {
    clearSession(res);
    res.json({ ok: true });
  }).catch(() => res.status(500).json({ error: "No se pudo cerrar la sesión." }));
});

function readVault(db, session) {
  const key = vaultKeyFor(session.id);
  const blob = db.vaults[session.username];
  if (!blob?.v) return freshVault();
  return openVault(key, blob);
}

function saveVault(db, session, vault) {
  db.vaults[session.username] = sealVault(vaultKeyFor(session.id), vault);
}

app.get("/api/apps", (req, res) => {
  updateDb((db) => {
    const session = sessionOf(db, req);
    if (!session) return { error: "Sin sesión.", status: 401 };
    return { apps: readVault(db, session).apps };
  }).then((result) => {
    if (result.error) return res.status(result.status).json({ error: result.error });
    res.json(result.apps);
  }).catch(() => res.status(500).json({ error: "No se pudo leer el directorio." }));
});

function cleanApp(body) {
  const nombre = String(body?.nombre || "").trim();
  let url = "";
  try {
    const parsed = new URL(String(body?.url || "").trim());
    if (parsed.protocol === "https:" || parsed.protocol === "http:") url = parsed.href;
  } catch {
    url = "";
  }
  const descripcion = String(body?.descripcion || "").trim();
  const categorias = ["Ciberseguridad", "Forense", "Utilidades", "Automatización"];
  const permisos = ["Libre", "Limitado", "Restringido"];
  const estados = ["Activa", "Mantenimiento", "Bloqueada"];
  const categoria = categorias.includes(body?.categoria) ? body.categoria : "";
  const permiso = permisos.includes(body?.permiso) ? body.permiso : "";
  const estado = estados.includes(body?.estado) ? body.estado : "";
  const version = String(body?.version || "v1.0.0").trim().slice(0, 20);
  if (!nombre || nombre.length > 80) return { error: "El nombre de la aplicación es obligatorio." };
  if (!url) return { error: "La URL debe empezar por http o https." };
  if (!descripcion || descripcion.length > 500) return { error: "La descripción es obligatoria." };
  if (!categoria || !permiso || !estado || !version) return { error: "Revisa categoría, permiso, estado y versión." };
  return { nombre, app: { url, descripcion, categoria, permiso, estado, version } };
}

app.post("/api/apps", (req, res) => {
  const cleaned = cleanApp(req.body);
  if (cleaned.error) return res.status(400).json({ error: cleaned.error });
  updateDb((db) => {
    const auth = requireUser(req, db);
    if (auth.error) return auth;
    let vault;
    try {
      vault = readVault(db, auth.session);
    } catch {
      return { error: "No se pudieron abrir tus datos. Vuelve a entrar.", status: 401 };
    }
    const apps = vault.apps;
    const original = String(req.body?.original || "");
    if (original && original !== cleaned.nombre) delete apps[original];
    apps[cleaned.nombre] = cleaned.app;
    saveVault(db, auth.session, vault);
    return { ok: true };
  }).then((result) => {
    if (result.error) return res.status(result.status || 400).json({ error: result.error });
    res.json({ ok: true });
  }).catch(() => res.status(500).json({ error: "No se pudo guardar." }));
});

app.delete("/api/apps", (req, res) => {
  const nombre = String(req.body?.nombre || "").trim();
  if (!nombre) return res.status(400).json({ error: "Elige una aplicación para eliminarla." });
  updateDb((db) => {
    const auth = requireUser(req, db);
    if (auth.error) return auth;
    let vault;
    try {
      vault = readVault(db, auth.session);
    } catch {
      return { error: "No se pudieron abrir tus datos. Vuelve a entrar.", status: 401 };
    }
    const apps = vault.apps;
    if (!apps[nombre]) return { error: "Esa aplicación ya no está.", status: 404 };
    delete apps[nombre];
    saveVault(db, auth.session, vault);
    return { ok: true };
  }).then((result) => {
    if (result.error) return res.status(result.status || 400).json({ error: result.error });
    res.json({ ok: true });
  }).catch(() => res.status(500).json({ error: "No se pudo eliminar." }));
});

app.get("/api/telemetry", (req, res) => {
  updateDb((db) => {
    const session = sessionOf(db, req);
    if (!session) return { error: "Sin sesión.", status: 401 };
    const apps = Object.values(readVault(db, session).apps);
    return {
      counts: {
        Total: apps.length,
        Activas: apps.filter((item) => item.estado === "Activa").length,
        Mantenimiento: apps.filter((item) => item.estado === "Mantenimiento").length,
        Bloqueadas: apps.filter((item) => item.estado === "Bloqueada").length,
      },
    };
  }).then((result) => {
    if (result.error) return res.status(result.status).json({ error: result.error });
    res.json(result.counts);
  }).catch(() => res.status(500).json({ error: "No se pudo leer la telemetría." }));
});

app.use("/css", express.static(path.join(root, "css")));
app.use("/js", express.static(path.join(root, "js")));
app.get("/", (_req, res) => res.sendFile(path.join(root, "index.html")));

const port = Number(process.env.PORT) || 8080;
app.listen(port, "0.0.0.0", () => {
  console.log(`Chat-2026 escuchando en ${port}`);
});
