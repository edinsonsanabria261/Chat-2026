import path from "node:path";
import crypto from "node:crypto";
import express from "express";
import { hashPassword, hashToken, sameSecret, updateDb } from "./db.js";

const app = express();
const root = process.cwd();
const WEEK = 7 * 24 * 60 * 60;

app.disable("x-powered-by");
app.use(express.json({ limit: "100kb" }));

function cookie(req, name) {
  const source = req.headers.cookie || "";
  for (const part of source.split(";")) {
    const [key, ...rest] = part.trim().split("=");
    if (key === name) return decodeURIComponent(rest.join("="));
  }
  return "";
}

function sendCookie(res, token) {
  const secure = process.env.NODE_ENV === "production" ? "; Secure" : "";
  res.setHeader(
    "Set-Cookie",
    `nexus_sid=${encodeURIComponent(token)}; HttpOnly; SameSite=Lax; Path=/; Max-Age=${WEEK}${secure}`,
  );
}

function clearCookie(res) {
  const secure = process.env.NODE_ENV === "production" ? "; Secure" : "";
  res.setHeader("Set-Cookie", `nexus_sid=; HttpOnly; SameSite=Lax; Path=/; Max-Age=0${secure}`);
}

function publicUser(username, user) {
  return { username, nombre: user.nombre, rol: user.rol };
}

function currentUser(db, req) {
  const token = cookie(req, "nexus_sid");
  if (!token) return null;
  const session = db.sessions[hashToken(token)];
  if (!session || session.expires < Date.now()) return null;
  const user = db.users[session.username];
  if (!user) return null;
  return publicUser(session.username, user);
}

function validUsername(value) {
  return /^[a-zA-Z0-9._-]{3,32}$/.test(value);
}

function validUrl(value) {
  try {
    const parsed = new URL(value);
    return parsed.protocol === "https:" || parsed.protocol === "http:" ? parsed.href : "";
  } catch {
    return "";
  }
}

app.get("/api/me", (req, res) => {
  updateDb((db) => currentUser(db, req)).then((user) => {
    if (!user) return res.status(401).json({ error: "Sin sesión." });
    res.json(user);
  }).catch(() => res.status(500).json({ error: "No se pudo leer la sesión." }));
});

app.post("/api/register", (req, res) => {
  const username = String(req.body?.username || "").trim();
  const nombre = String(req.body?.nombre || "").trim();
  const password = String(req.body?.password || "");
  if (!validUsername(username)) {
    return res.status(400).json({ error: "El usuario debe tener 3 a 32 caracteres, sin espacios." });
  }
  if (password.length < 8) {
    return res.status(400).json({ error: "La contraseña necesita al menos 8 caracteres." });
  }
  hashPassword(password).then((secret) => updateDb((db) => {
    if (db.users[username]) return { error: "El usuario ya existe.", status: 409 };
    db.users[username] = {
      nombre: nombre || username,
      rol: Object.keys(db.users).length === 0 ? "Administrador Principal" : "Operador",
      salt: secret.salt,
      hash: secret.hash,
    };
    return { ok: true };
  })).then((result) => {
    if (result.error) return res.status(result.status || 400).json({ error: result.error });
    res.status(201).json({ ok: true });
  }).catch(() => res.status(500).json({ error: "No se pudo registrar." }));
});

app.post("/api/login", (req, res) => {
  const username = String(req.body?.username || "").trim();
  const password = String(req.body?.password || "");
  updateDb(async (db) => {
    const user = db.users[username];
    const fake = { salt: "missing", hash: "missing" };
    const secret = await hashPassword(password, user?.salt || fake.salt);
    const matches = user ? sameSecret(secret.hash, user.hash) : false;
    if (!user || !matches) return { error: "Credenciales inválidas." };
    const token = crypto.randomBytes(32).toString("base64url");
    db.sessions[hashToken(token)] = { username, expires: Date.now() + WEEK * 1000 };
    return { token, user: publicUser(username, user) };
  }).then((result) => {
    if (result.error) return res.status(401).json({ error: result.error });
    sendCookie(res, result.token);
    res.json(result.user);
  }).catch(() => res.status(500).json({ error: "No se pudo entrar." }));
});

app.post("/api/logout", (req, res) => {
  const token = cookie(req, "nexus_sid");
  updateDb((db) => {
    if (token) delete db.sessions[hashToken(token)];
  }).then(() => {
    clearCookie(res);
    res.json({ ok: true });
  }).catch(() => res.status(500).json({ error: "No se pudo cerrar la sesión." }));
});

app.get("/api/apps", (req, res) => {
  updateDb((db) => {
    const user = currentUser(db, req);
    if (!user) return { error: "Sin sesión.", status: 401 };
    return { apps: db.apps };
  }).then((result) => {
    if (result.error) return res.status(result.status).json({ error: result.error });
    res.json(result.apps);
  }).catch(() => res.status(500).json({ error: "No se pudo leer el directorio." }));
});

function cleanApp(body) {
  const nombre = String(body?.nombre || "").trim();
  const url = validUrl(String(body?.url || "").trim());
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

async function authorizedAdmin(db, req, password) {
  const user = currentUser(db, req);
  if (!user) return { error: "Sin sesión.", status: 401 };
  if (user.rol !== "Administrador Principal") return { error: "Solo el administrador puede cambiar el directorio.", status: 403 };
  const record = db.users[user.username];
  const secret = await hashPassword(String(password || ""), record.salt);
  if (!sameSecret(secret.hash, record.hash)) return { error: "Contraseña incorrecta. No se aplicaron cambios.", status: 403 };
  return { user };
}

app.post("/api/apps", (req, res) => {
  const cleaned = cleanApp(req.body);
  if (cleaned.error) return res.status(400).json({ error: cleaned.error });
  updateDb(async (db) => {
    const auth = await authorizedAdmin(db, req, req.body?.password);
    if (auth.error) return auth;
    const original = String(req.body?.original || "");
    if (original && original !== cleaned.nombre) delete db.apps[original];
    db.apps[cleaned.nombre] = cleaned.app;
    return { ok: true };
  }).then((result) => {
    if (result.error) return res.status(result.status || 400).json({ error: result.error });
    res.json({ ok: true });
  }).catch(() => res.status(500).json({ error: "No se pudo guardar." }));
});

app.delete("/api/apps", (req, res) => {
  const nombre = String(req.body?.nombre || "").trim();
  if (!nombre) return res.status(400).json({ error: "Elige una aplicación para eliminarla." });
  updateDb(async (db) => {
    const auth = await authorizedAdmin(db, req, req.body?.password);
    if (auth.error) return auth;
    if (!db.apps[nombre]) return { error: "Esa aplicación ya no está.", status: 404 };
    delete db.apps[nombre];
    return { ok: true };
  }).then((result) => {
    if (result.error) return res.status(result.status || 400).json({ error: result.error });
    res.json({ ok: true });
  }).catch(() => res.status(500).json({ error: "No se pudo eliminar." }));
});

app.get("/api/telemetry", (req, res) => {
  updateDb((db) => {
    if (!currentUser(db, req)) return { error: "Sin sesión.", status: 401 };
    const apps = Object.values(db.apps);
    return {
      counts: {
        Total: apps.length,
        Activas: apps.filter((item) => item.estado === "Activa").length,
        Mantenimiento: apps.filter((item) => item.estado === "Mantenimiento").length,
        Bloqueadas: apps.filter((item) => item.estado === "Bloqueada").length,
        Cuentas: Object.keys(db.users).length,
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
