import { confirmPassword, currentSession } from "./auth.js";
import { loadApps, saveApps } from "./store.js";

const $ = (id) => document.getElementById(id);

function clear(node) {
  node.replaceChildren();
}

function cardMetaClass(estado) {
  if (estado === "Bloqueada") return "meta bad";
  if (estado === "Mantenimiento") return "meta warn";
  return "meta";
}

export function renderHub() {
  const apps = loadApps();
  const select = $("filter-category");
  const previous = select.value || "Todas";
  const categories = ["Todas", ...new Set(Object.values(apps).map((app) => app.categoria))];
  clear(select);
  categories.forEach((category) => {
    const option = document.createElement("option");
    option.value = category;
    option.textContent = category;
    select.append(option);
  });
  select.value = categories.includes(previous) ? previous : "Todas";

  const grid = $("app-grid");
  clear(grid);
  const visible = Object.entries(apps).filter(([, app]) => select.value === "Todas" || app.categoria === select.value);
  if (visible.length === 0) {
    const empty = document.createElement("p");
    empty.className = "empty";
    empty.textContent = "No hay aplicaciones en esta categoría.";
    grid.append(empty);
    return;
  }
  visible.forEach(([name, app]) => {
    const card = document.createElement("article");
    card.className = "app-card";
    const title = document.createElement("h4");
    title.textContent = name;
    const version = document.createElement("span");
    version.className = "version";
    version.textContent = ` ${app.version}`;
    title.append(version);
    const desc = document.createElement("p");
    desc.textContent = app.descripcion;
    const meta = document.createElement("p");
    meta.className = cardMetaClass(app.estado);
    meta.textContent = `Estado: ${app.estado} | Permiso: ${app.permiso}`;
    const link = document.createElement("a");
    link.className = "open-link";
    link.href = app.url;
    link.target = "_blank";
    link.rel = "noopener noreferrer";
    link.textContent = `Abrir ${name}`;
    card.append(title, desc, meta, link);
    grid.append(card);
  });
}

function fillForm(name) {
  const apps = loadApps();
  const app = apps[name];
  $("app-name").value = name && app ? name : "";
  $("app-url").value = app?.url || "";
  $("app-desc").value = app?.descripcion || "";
  $("app-cat").value = app?.categoria || "Ciberseguridad";
  $("app-permiso").value = app?.permiso || "Libre";
  $("app-estado").value = app?.estado || "Activa";
  $("app-version").value = app?.version || "v1.0.0";
}

export function renderCrud() {
  const session = currentSession();
  const admin = session?.rol === "Administrador Principal";
  $("crud-note").textContent = admin
    ? "Confirma con tu contraseña antes de guardar o eliminar."
    : "Solo el administrador principal puede cambiar el directorio.";
  const form = $("form-app");
  [...form.elements].forEach((field) => {
    field.disabled = !admin;
  });

  const select = $("edit-target");
  const previous = select.value;
  clear(select);
  const fresh = document.createElement("option");
  fresh.value = "";
  fresh.textContent = "Nueva aplicación";
  select.append(fresh);
  Object.keys(loadApps()).forEach((name) => {
    const option = document.createElement("option");
    option.value = name;
    option.textContent = name;
    select.append(option);
  });
  select.value = [...select.options].some((option) => option.value === previous) ? previous : "";
  if (!admin) return;
  fillForm(select.value);
}

export function renderTelemetry() {
  const apps = Object.values(loadApps());
  const counts = {
    Total: apps.length,
    Activas: apps.filter((app) => app.estado === "Activa").length,
    Mantenimiento: apps.filter((app) => app.estado === "Mantenimiento").length,
    Bloqueadas: apps.filter((app) => app.estado === "Bloqueada").length,
  };
  const box = $("metrics");
  clear(box);
  Object.entries(counts).forEach(([label, value]) => {
    const item = document.createElement("article");
    item.className = "metric";
    const name = document.createElement("span");
    name.textContent = label;
    const strong = document.createElement("strong");
    strong.textContent = String(value);
    item.append(name, strong);
    box.append(item);
  });
  const note = document.createElement("article");
  note.className = "metric";
  const name = document.createElement("span");
  name.textContent = "Dónde viven los datos";
  const strong = document.createElement("strong");
  strong.textContent = "Este navegador";
  note.append(name, strong);
  box.append(note);
}

export function readAppForm() {
  return {
    nombre: $("app-name").value.trim(),
    url: $("app-url").value.trim(),
    descripcion: $("app-desc").value.trim(),
    categoria: $("app-cat").value,
    permiso: $("app-permiso").value,
    estado: $("app-estado").value,
    version: $("app-version").value.trim() || "v1.0.0",
    original: $("edit-target").value,
    password: $("crud-pass").value,
  };
}

export async function saveAppFromForm() {
  const data = readAppForm();
  $("crud-error").textContent = "";
  if (!data.nombre || !data.url || !data.descripcion) {
    $("crud-error").textContent = "Nombre, URL y descripción son obligatorios.";
    return false;
  }
  let parsed;
  try {
    parsed = new URL(data.url);
  } catch {
    $("crud-error").textContent = "La URL no es válida.";
    return false;
  }
  if (parsed.protocol !== "https:" && parsed.protocol !== "http:") {
    $("crud-error").textContent = "La URL debe empezar por http o https.";
    return false;
  }
  if (!(await confirmPassword(data.password))) {
    $("crud-error").textContent = "Contraseña incorrecta. No se aplicaron cambios.";
    return false;
  }
  const apps = loadApps();
  if (data.original && data.original !== data.nombre) delete apps[data.original];
  apps[data.nombre] = {
    url: data.url,
    descripcion: data.descripcion,
    categoria: data.categoria,
    permiso: data.permiso,
    estado: data.estado,
    version: data.version,
  };
  saveApps(apps);
  $("crud-pass").value = "";
  return true;
}

export async function deleteSelectedApp() {
  const original = $("edit-target").value;
  $("crud-error").textContent = "";
  if (!original) {
    $("crud-error").textContent = "Elige una aplicación para eliminarla.";
    return false;
  }
  if (!(await confirmPassword($("crud-pass").value))) {
    $("crud-error").textContent = "Contraseña incorrecta. No se aplicaron cambios.";
    return false;
  }
  const apps = loadApps();
  delete apps[original];
  saveApps(apps);
  $("crud-pass").value = "";
  return true;
}

export function showPanel(name) {
  ["hub", "crud", "telemetry"].forEach((id) => {
    $(`panel-${id}`).hidden = id !== name;
    $(`tab-${id}`).setAttribute("aria-selected", String(id === name));
  });
  if (name === "hub") renderHub();
  if (name === "crud") renderCrud();
  if (name === "telemetry") renderTelemetry();
}

export function showAuthTab(which) {
  const login = which === "login";
  $("panel-login").hidden = !login;
  $("panel-register").hidden = login;
  $("tab-login").setAttribute("aria-selected", String(login));
  $("tab-register").setAttribute("aria-selected", String(!login));
}
