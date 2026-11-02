const CSRF_COOKIE = "nexus_csrf";
const appState = {
  user: null,
  apps: [],
};

const elements = {
  viewLogin: document.getElementById("view-login"),
  viewApp: document.getElementById("view-app"),
  sessionLine: document.getElementById("session-line"),
  loginError: document.getElementById("login-error"),
  registerError: document.getElementById("register-error"),
  registerOk: document.getElementById("register-ok"),
  appGrid: document.getElementById("app-grid"),
  filterCategory: document.getElementById("filter-category"),
  filterState: document.getElementById("filter-state"),
  hubSort: document.getElementById("hub-sort"),
  appSearch: document.getElementById("app-search"),
  editTarget: document.getElementById("edit-target"),
  appForm: document.getElementById("form-app"),
  crudError: document.getElementById("crud-error"),
  deleteApp: document.getElementById("delete-app"),
  metrics: document.getElementById("metrics"),
  accountMenu: document.getElementById("account-menu"),
  accountButton: document.getElementById("account-button"),
  closeAccountMenu: document.getElementById("close-account-menu"),
  logoutButton: document.getElementById("logout"),
  accountPasswordForm: document.getElementById("account-password-form"),
  profileStatus: document.getElementById("profile-status"),
  passwordStatus: document.getElementById("password-status"),
};

function readCookie(name) {
  const source = document.cookie || "";
  for (const part of source.split(";")) {
    const [key, ...rest] = part.trim().split("=");
    if (key === name) return decodeURIComponent(rest.join("="));
  }
  return "";
}

function setFormMessage(node, text, isError = false) {
  if (!node) return;
  node.textContent = text || "";
  node.style.color = isError ? "#fca5a5" : "#a7f3d0";
}

function showLoginView() {
  elements.viewLogin.hidden = false;
  elements.viewApp.hidden = true;
  elements.loginError.textContent = "";
}

function showAppView() {
  elements.viewLogin.hidden = true;
  elements.viewApp.hidden = false;
  elements.sessionLine.textContent = appState.user
    ? `${appState.user.nombre || appState.user.username} · ${appState.user.rol || "Usuario"}`
    : "No autenticado";
}

function csrfHeaders() {
  const token = readCookie(CSRF_COOKIE);
  return token ? { "x-csrf-token": token } : {};
}

async function api(path, options = {}) {
  const headers = new Headers(options.headers || {});
  if (!(options.body instanceof FormData) && options.body && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }

  const response = await fetch(path, {
    credentials: "same-origin",
    ...options,
    headers,
  });

  const text = await response.text();
  const payload = text ? JSON.parse(text) : null;

  if (!response.ok) {
    throw new Error(payload?.error || "Error de petición");
  }

  return payload;
}

async function refreshUser() {
  try {
    const user = await api("/api/me");
    appState.user = user;
    showAppView();
    await refreshApps();
    await refreshTelemetry();
  } catch {
    appState.user = null;
    showLoginView();
  }
}

function normalizeAppItem(name, item) {
  return {
    name,
    url: item.url || "",
    descripcion: item.descripcion || "",
    categoria: item.categoria || "",
    permiso: item.permiso || "",
    estado: item.estado || "",
    version: item.version || "v1.0.0",
    prioridad: item.prioridad || "Media",
    responsable: item.responsable || "",
    tags: Array.isArray(item.tags) ? item.tags : [],
    favorita: Boolean(item.favorita),
    updatedAt: Number(item.updatedAt) || Date.now(),
  };
}

function getFilteredApps() {
  const search = (elements.appSearch.value || "").trim().toLowerCase();
  const category = elements.filterCategory.value || "Todos";
  const statusFilter = elements.filterState.value || "Todos";
  const sort = elements.hubSort.value || "name";

  let list = appState.apps.filter((app) => {
    const matchesCategory = category === "Todos" || app.categoria === category;
    const matchesStatus = statusFilter === "Todos" || app.estado === statusFilter;
    const haystack = [app.name, app.url, app.descripcion, app.categoria, app.estado, ...(app.tags || [])]
      .join(" ")
      .toLowerCase();
    const matchesSearch = !search || haystack.includes(search);
    return matchesCategory && matchesStatus && matchesSearch;
  });

  list.sort((a, b) => {
    if (sort === "status") return a.estado.localeCompare(b.estado) || a.name.localeCompare(b.name);
    if (sort === "updated") return (b.updatedAt || 0) - (a.updatedAt || 0);
    return a.name.localeCompare(b.name);
  });

  return list;
}

function renderCategories() {
  const categories = ["Todos", ...new Set(appState.apps.map((app) => app.categoria).filter(Boolean))];
  const current = elements.filterCategory.value || "Todos";
  elements.filterCategory.innerHTML = categories
    .map((category) => `<option value="${category}">${category === "Todos" ? "Todas" : category}</option>`)
    .join("");
  elements.filterCategory.value = categories.includes(current) ? current : "Todos";
}

function renderAppGrid() {
  const apps = getFilteredApps();
  if (!apps.length) {
    elements.appGrid.innerHTML = `
      <div class="empty-state">
        <h4>No hay resultados</h4>
        <p>Cambia los filtros o crea una nueva aplicación.</p>
      </div>
    `;
    return;
  }

  elements.appGrid.innerHTML = apps
    .map((app) => `
      <article class="app-card" data-name="${app.name}">
        <div class="app-card-head">
          <div>
            <h4>${app.name}</h4>
            <span class="badge ${app.estado === "Activa" ? "ok" : app.estado === "Mantenimiento" ? "warn" : "danger"}">${app.estado}</span>
          </div>
          ${app.favorita ? '<span class="star">★</span>' : ""}
        </div>
        <p>${app.descripcion}</p>
        <div class="meta-row">
          <span>${app.categoria}</span>
          <span>${app.permiso}</span>
        </div>
        <div class="meta-row">
          <span>${app.version}</span>
          <span>${app.prioridad}</span>
        </div>
        <div class="tag-list">
          ${(app.tags || []).slice(0, 4).map((tag) => `<span class="tag">${tag}</span>`).join("") || '<span class="tag">Sin etiquetas</span>'}
        </div>
        <a href="${app.url}" target="_blank" rel="noreferrer noopener">Abrir</a>
      </article>
    `)
    .join("");
}

async function refreshApps() {
  try {
    const payload = await api("/api/apps");
    appState.apps = Object.entries(payload || {}).map(([name, item]) => normalizeAppItem(name, item));
    renderCategories();
    renderAppGrid();
    populateEditTarget();
  } catch (error) {
    appState.apps = [];
    renderCategories();
    renderAppGrid();
    console.error(error);
  }
}

async function refreshTelemetry() {
  try {
    const payload = await api("/api/telemetry");
    const entries = Object.entries(payload || {});
    elements.metrics.innerHTML = entries
      .map(([label, value]) => `
        <div class="metric-card">
          <span>${label}</span>
          <strong>${value}</strong>
        </div>
      `)
      .join("");
  } catch (error) {
    elements.metrics.innerHTML = "<p class=\"muted\">No se pudo cargar la telemetría.</p>";
    console.error(error);
  }
}

function populateEditTarget() {
  const names = appState.apps.map((app) => app.name).sort((a, b) => a.localeCompare(b));
  const previous = elements.editTarget.value || names[0] || "";
  elements.editTarget.innerHTML = names
    .map((name) => `<option value="${name}">${name}</option>`)
    .join("");
  if (names.includes(previous)) {
    elements.editTarget.value = previous;
  }
  if (names.length) {
    const selected = appState.apps.find((app) => app.name === elements.editTarget.value) || appState.apps[0];
    fillForm(selected);
  } else {
    elements.appForm.reset();
    document.getElementById("app-name").value = "";
    document.getElementById("app-url").value = "";
    document.getElementById("app-desc").value = "";
    document.getElementById("app-version").value = "v1.0.0";
    document.getElementById("app-prioridad").value = "Media";
  }
}

function fillForm(app) {
  if (!app) return;
  document.getElementById("app-name").value = app.name;
  document.getElementById("app-url").value = app.url;
  document.getElementById("app-desc").value = app.descripcion;
  document.getElementById("app-cat").value = app.categoria;
  document.getElementById("app-permiso").value = app.permiso;
  document.getElementById("app-estado").value = app.estado;
  document.getElementById("app-version").value = app.version;
  document.getElementById("app-prioridad").value = app.prioridad;
  document.getElementById("app-responsable").value = app.responsable || "";
  document.getElementById("app-tags").value = (app.tags || []).join(", ");
  document.getElementById("app-favorita").checked = Boolean(app.favorita);
}

function buildAppPayload(formData, originalName) {
  const nombre = String(formData.get("nombre") || "").trim();
  const payload = {
    original: originalName || "",
    nombre,
    url: String(formData.get("url") || "").trim(),
    descripcion: String(formData.get("descripcion") || "").trim(),
    categoria: String(formData.get("categoria") || "").trim(),
    permiso: String(formData.get("permiso") || "").trim(),
    estado: String(formData.get("estado") || "").trim(),
    version: String(formData.get("version") || "").trim(),
    prioridad: String(formData.get("prioridad") || "Media").trim(),
    responsable: String(formData.get("responsable") || "").trim(),
    tags: String(formData.get("tags") || "").split(",").map((tag) => tag.trim()).filter(Boolean),
    favorita: Boolean(formData.get("favorita") === "on" || formData.get("favorita") === true),
    updatedAt: Date.now(),
  };
  return payload;
}

function setCrudError(message) {
  setFormMessage(elements.crudError, message, true);
}

async function saveApp(event) {
  event.preventDefault();
  const form = event.currentTarget;
  const formData = new FormData(form);
  const originalName = elements.editTarget.value || "";
  const payload = buildAppPayload(formData, originalName);

  try {
    await api("/api/apps", {
      method: "POST",
      headers: csrfHeaders(),
      body: JSON.stringify(payload),
    });
    setFormMessage(elements.crudError, "Aplicación guardada correctamente.", false);
    await refreshUser();
  } catch (error) {
    setCrudError(error.message);
  }
}

async function deleteApp(event) {
  event.preventDefault();
  const name = elements.editTarget.value;
  if (!name) {
    setCrudError("No hay ninguna aplicación seleccionada.");
    return;
  }

  try {
    await api("/api/apps", {
      method: "DELETE",
      headers: csrfHeaders(),
      body: JSON.stringify({ nombre: name }),
    });
    setFormMessage(elements.crudError, "Aplicación eliminada.", false);
    await refreshUser();
    elements.appForm.reset();
  } catch (error) {
    setCrudError(error.message);
  }
}

async function submitLogin(event) {
  event.preventDefault();
  const formData = new FormData(event.currentTarget);
  const username = String(formData.get("username") || "").trim();
  const password = String(formData.get("password") || "");

  try {
    const user = await api("/api/login", {
      method: "POST",
      body: JSON.stringify({ username, password }),
    });
    appState.user = user;
    showAppView();
    await refreshApps();
    await refreshTelemetry();
    event.currentTarget.reset();
    setFormMessage(elements.loginError, "", false);
  } catch (error) {
    setFormMessage(elements.loginError, error.message, true);
  }
}

async function submitRegister(event) {
  event.preventDefault();
  const formData = new FormData(event.currentTarget);
  const payload = {
    username: String(formData.get("username") || "").trim(),
    nombre: String(formData.get("nombre") || "").trim(),
    password: String(formData.get("password") || ""),
    confirm: String(formData.get("confirm") || ""),
  };

  try {
    const user = await api("/api/register", {
      method: "POST",
      body: JSON.stringify(payload),
    });
    appState.user = user;
    showAppView();
    await refreshApps();
    await refreshTelemetry();
    event.currentTarget.reset();
    setFormMessage(elements.registerError, "", false);
    setFormMessage(elements.registerOk, "Cuenta creada correctamente.", false);
  } catch (error) {
    setFormMessage(elements.registerError, error.message, true);
    setFormMessage(elements.registerOk, "", false);
  }
}

async function handleLogout() {
  try {
    await api("/api/logout", { method: "POST", headers: csrfHeaders() });
  } catch (error) {
    console.error(error);
  } finally {
    appState.user = null;
    appState.apps = [];
    showLoginView();
    elements.appGrid.innerHTML = "";
    elements.metrics.innerHTML = "";
  }
}

function bindTabs() {
  const loginTab = document.getElementById("tab-login");
  const registerTab = document.getElementById("tab-register");
  const loginPanel = document.getElementById("panel-login");
  const registerPanel = document.getElementById("panel-register");

  loginTab.addEventListener("click", () => {
    loginTab.setAttribute("aria-selected", "true");
    registerTab.setAttribute("aria-selected", "false");
    loginPanel.hidden = false;
    registerPanel.hidden = true;
  });

  registerTab.addEventListener("click", () => {
    loginTab.setAttribute("aria-selected", "false");
    registerTab.setAttribute("aria-selected", "true");
    loginPanel.hidden = true;
    registerPanel.hidden = false;
  });

  document.querySelectorAll("[data-account-tab]").forEach((button) => {
    button.addEventListener("click", () => {
      const panel = button.dataset.accountTab === "password" ? "account-password-panel" : "account-profile-panel";
      document.querySelectorAll(".account-tab").forEach((tab) => tab.classList.toggle("active", tab === button));
      document.querySelectorAll(".account-panel-body").forEach((node) => node.classList.toggle("active", node.id === panel));
    });
  });
}

function bindAccountMenu() {
  elements.accountButton.addEventListener("click", () => {
    elements.accountMenu.hidden = false;
    elements.accountMenu.setAttribute("aria-hidden", "false");
  });

  elements.closeAccountMenu.addEventListener("click", () => {
    elements.accountMenu.hidden = true;
    elements.accountMenu.setAttribute("aria-hidden", "true");
  });

  elements.accountPasswordForm.addEventListener("submit", (event) => {
    event.preventDefault();
    const formData = new FormData(event.currentTarget);
    const currentPassword = String(formData.get("currentPassword") || "");
    const newPassword = String(formData.get("newPassword") || "");
    const confirmPassword = String(formData.get("confirmPassword") || "");

    if (!currentPassword || !newPassword || !confirmPassword) {
      setFormMessage(elements.passwordStatus, "Completa todos los campos.", true);
      return;
    }

    if (newPassword !== confirmPassword) {
      setFormMessage(elements.passwordStatus, "Las nuevas contraseñas no coinciden.", true);
      return;
    }

    setFormMessage(elements.passwordStatus, "Cambio de contraseña pendiente: el backend no expone aún este endpoint.", false);
    event.currentTarget.reset();
  });

  document.getElementById("account-profile-form").addEventListener("submit", (event) => {
    event.preventDefault();
    setFormMessage(elements.profileStatus, "Perfil actualizado localmente en la vista actual. El backend aún no expone este cambio.", false);
    event.currentTarget.reset();
  });
}

function bindFilterEvents() {
  elements.appSearch.addEventListener("input", renderAppGrid);
  elements.filterCategory.addEventListener("change", renderAppGrid);
  elements.filterState.addEventListener("change", renderAppGrid);
  elements.hubSort.addEventListener("change", renderAppGrid);
}

async function init() {
  bindTabs();
  bindAccountMenu();
  bindFilterEvents();

  document.getElementById("panel-login").addEventListener("submit", submitLogin);
  document.getElementById("panel-register").addEventListener("submit", submitRegister);
  elements.logoutButton.addEventListener("click", handleLogout);
  elements.appForm.addEventListener("submit", saveApp);
  elements.deleteApp.addEventListener("click", deleteApp);
  elements.editTarget.addEventListener("change", () => {
    const selected = appState.apps.find((app) => app.name === elements.editTarget.value);
    fillForm(selected || null);
  });

  await refreshUser();
}

init();
