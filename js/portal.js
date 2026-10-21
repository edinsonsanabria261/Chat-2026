import { api } from "./auth.js";

const $ = (id) => document.getElementById(id);
let appsCache = {};

function clear(node) {
  node.replaceChildren();
}

function cardMetaClass(estado) {
  if (estado === "Bloqueada") return "meta bad";
  if (estado === "Mantenimiento") return "meta warn";
  return "meta";
}

export async function renderHub() {
  appsCache = await api("/api/apps");
  const select = $("filter-category");
  const previous = select.value || "Todas";
  const categories = ["Todas", ...new Set(Object.values(appsCache).map((app) => app.categoria))];
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
  const visible = Object.entries(appsCache).filter(([, app]) => select.value === "Todas" || app.categoria === select.value);
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
    const version = document.createElement("span");
    version.className = "version";
    version.textContent = ` ${app.version}`;
    title.append(document.createTextNode(name), version);
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
  const app = appsCache[name];
  $("app-name").value = name && app ? name : "";
  $("app-url").value = app?.url || "";
  $("app-desc").value = app?.descripcion || "";
  $("app-cat").value = app?.categoria || "Ciberseguridad";
  $("app-permiso").value = app?.permiso || "Libre";
  $("app-estado").value = app?.estado || "Activa";
  $("app-version").value = app?.version || "v1.0.0";
}

export async function renderCrud() {
  appsCache = await api("/api/apps");
  $("crud-note").textContent = "Estas aplicaciones son solo tuyas. Otra cuenta no puede verlas ni cambiarlas.";
  const select = $("edit-target");
  const previous = select.value;
  clear(select);
  const fresh = document.createElement("option");
  fresh.value = "";
  fresh.textContent = "Nueva aplicación";
  select.append(fresh);
  Object.keys(appsCache).forEach((name) => {
    const option = document.createElement("option");
    option.value = name;
    option.textContent = name;
    select.append(option);
  });
  select.value = [...select.options].some((option) => option.value === previous) ? previous : "";
  fillForm(select.value);
}

export async function renderTelemetry() {
  const counts = await api("/api/telemetry");
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
  };
}

export async function saveAppFromForm() {
  $("crud-error").textContent = "";
  try {
    await api("/api/apps", { method: "POST", body: JSON.stringify(readAppForm()) });
    return true;
  } catch (error) {
    $("crud-error").textContent = error.message;
    return false;
  }
}

export async function deleteSelectedApp() {
  $("crud-error").textContent = "";
  const nombre = $("edit-target").value;
  if (!nombre) {
    $("crud-error").textContent = "Elige una aplicación para eliminarla.";
    return false;
  }
  try {
    await api("/api/apps", { method: "DELETE", body: JSON.stringify({ nombre }) });
    return true;
  } catch (error) {
    $("crud-error").textContent = error.message;
    return false;
  }
}

export async function showPanel(name) {
  ["hub", "crud", "telemetry"].forEach((id) => {
    $(`panel-${id}`).hidden = id !== name;
    $(`tab-${id}`).setAttribute("aria-selected", String(id === name));
  });
  if (name === "hub") await renderHub();
  if (name === "crud") await renderCrud();
  if (name === "telemetry") await renderTelemetry();
}

export function showAuthTab(which) {
  const login = which === "login";
  $("panel-login").hidden = !login;
  $("panel-register").hidden = login;
  $("tab-login").setAttribute("aria-selected", String(login));
  $("tab-register").setAttribute("aria-selected", String(!login));
}
