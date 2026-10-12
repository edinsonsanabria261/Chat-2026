import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";

const dir = process.env.DATA_DIR || path.join(process.cwd(), "data");
const file = path.join(dir, "db.json");

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

function emptyDb() {
  return { users: {}, apps: structuredClone(SAMPLE_APPS), sessions: {} };
}

function readDb() {
  try {
    return JSON.parse(fs.readFileSync(file, "utf8"));
  } catch {
    return emptyDb();
  }
}

function writeDb(db) {
  fs.mkdirSync(dir, { recursive: true });
  const tmp = `${file}.tmp`;
  fs.writeFileSync(tmp, JSON.stringify(db, null, 2));
  fs.renameSync(tmp, file);
}

let chain = Promise.resolve();

export function updateDb(change) {
  const run = chain.then(async () => {
    const db = readDb();
    db.sessions = db.sessions || {};
    const now = Date.now();
    for (const [key, session] of Object.entries(db.sessions)) {
      if (!session || session.expires < now) delete db.sessions[key];
    }
    const result = await change(db);
    writeDb(db);
    return result;
  });
  chain = run.then(
    () => undefined,
    () => undefined,
  );
  return run;
}

export function hashToken(token) {
  return crypto.createHash("sha256").update(token).digest("hex");
}

export async function hashPassword(password, salt = crypto.randomBytes(16).toString("base64url")) {
  const hash = await new Promise((resolve, reject) => {
    crypto.pbkdf2(password, salt, 120000, 32, "sha256", (error, derived) => {
      if (error) reject(error);
      else resolve(derived.toString("base64url"));
    });
  });
  return { salt, hash };
}

export function sameSecret(left, right) {
  const a = Buffer.from(left);
  const b = Buffer.from(right);
  if (a.length !== b.length) return false;
  return crypto.timingSafeEqual(a, b);
}
