import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const dir = process.env.DATA_DIR || path.join(root, "data");
const file = path.join(dir, "db.json");

export const SAMPLE_APPS = {
  "App Auditoría Red": {
    url: "https://streamlit.io",
    descripcion: "Herramienta de análisis de nodos y puertos perimetrales.",
    categoria: "Ciberseguridad",
    permiso: "Libre",
    estado: "Activa",
    version: "v1.0.0",
    prioridad: "Media",
    responsable: "Admin",
    tags: ["red", "seguridad"],
    favorita: true,
    updatedAt: Date.now(),
  },
};

function emptyDb() {
  return { users: {}, vaults: {}, sessions: {} };
}

export function freshVault() {
  return { apps: structuredClone(SAMPLE_APPS) };
}

function normalize(db) {
  if (!db || typeof db !== "object") db = emptyDb();
  db.users ||= {};
  db.vaults ||= {};
  db.sessions ||= {};

  for (const [name, user] of Object.entries(db.users)) {
    if (!user.algo) user.algo = "pbkdf2";
    user.failed ||= 0;
    user.lockedUntil ||= 0;
    const role = String(user.rol || "").trim();
    if (role === "Usuario" || role === "Editor" || !role) user.rol = "Editor";
    else if (role === "Administrador Principal") user.rol = role;
    else if (role === "Administrador") user.rol = role;
    if (!db.vaults[name]) db.vaults[name] = { apps: {} };
  }

  if (db.apps) {
    const admin = Object.keys(db.users).find((name) => db.users[name].rol === "Administrador Principal");
    if (admin && Object.keys(db.vaults[admin]?.apps || {}).length === 0) db.vaults[admin].apps = db.apps;
    delete db.apps;
  }
  return db;
}

function readDb() {
  try {
    return normalize(JSON.parse(fs.readFileSync(file, "utf8")));
  } catch (error) {
    if (error.code !== "ENOENT") console.error("No se pudo leer la base de datos:", error.message);
    return emptyDb();
  }
}

function writeDb(db) {
  fs.mkdirSync(dir, { recursive: true });
  const tmp = `${file}.tmp`;
  fs.writeFileSync(tmp, JSON.stringify(db, null, 2), { mode: 0o600 });
  fs.renameSync(tmp, file);
}

let chain = Promise.resolve();

export function updateDb(change) {
  const run = chain.then(async () => {
    const db = readDb();
    const now = Date.now();
    for (const [key, session] of Object.entries(db.sessions)) {
      if (!session || session.expires < now) delete db.sessions[key];
    }
    const result = await change(db);
    writeDb(db);
    return result;
  });
  chain = run.then(() => undefined, () => undefined);
  return run;
}
