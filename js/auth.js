import { currentSession, loginUser, logoutUser, refreshSession, registerUser } from "./auth.js";
import {
  deleteSelectedApp,
  saveAppFromForm,
  showAuthTab,
  showPanel,
} from "./portal.js";

const $ = (id) => document.getElementById(id);

function showError(id, error) {
  $(id).textContent = error?.message || error || "No se pudo completar la acción.";
}

function clearFormFields(form) {
  form.querySelectorAll("input, textarea, select").forEach((element) => {
    if (element.type === "checkbox" || element.type === "radio") {
      element.checked = false;
      return;
    }
    if (element.tagName === "SELECT") {
      element.selectedIndex = 0;
    }
    element.value = "";
  });
}

function applyProtectedView(sessionActive) {
  const loginView = $("view-login");
  const appView = $("view-app");

  loginView.hidden = sessionActive;
  appView.hidden = !sessionActive;

  if (sessionActive) {
    loginView.style.display = "none";
    appView.style.display = "block";
  } else {
    loginView.style.display = "grid";
    appView.style.display = "none";
  }
}

function applyRoleUI() {
  const user = currentSession();
  const role = user?.rol || "";
  const canManage = ["Administrador Principal", "Administrador", "Editor"].includes(role);
  const crudTab = $("tab-crud");
  crudTab.disabled = !canManage;
  crudTab.title = canManage ? "Gestión" : "Solo lectura";
  crudTab.style.opacity = canManage ? "1" : "0.55";

  if (!canManage && $("panel-crud").getAttribute("aria-selected") === "true") {
    $("tab-hub").click();
  }
}

async function paintSession() {
  const session = await refreshSession();
  applyProtectedView(Boolean(session));
  applyRoleUI();

  if (!session) {
    showAuthTab("login");
    $("login-error").textContent = "";
    $("register-error").textContent = "";
    $("register-ok").textContent = "";
    return;
  }

  $("session-line").textContent = `Sesión activa · ${session.nombre} · ${session.rol}`;
  await showPanel("hub");
}

async function openPanel(name) {
  try {
    const user = currentSession();
    const role = user?.rol || "";
    const canManage = ["Administrador Principal", "Administrador", "Editor"].includes(role);
    if (name === "crud" && !canManage) {
      $("crud-error").textContent = "No tienes permisos para administrar aplicaciones.";
      return;
    }
    await showPanel(name);
  } catch (error) {
    showError("crud-error", error);
  }
}

$("tab-login").addEventListener("click", () => showAuthTab("login"));
$("tab-register").addEventListener("click", () => showAuthTab("register"));

$("panel-login").addEventListener("submit", async (event) => {
  event.preventDefault();
  $("login-error").textContent = "";
  try {
    const result = await loginUser($("login-user").value, $("login-pass").value);
    if (!result.ok) {
      $("login-error").textContent = result.error;
      return;
    }

    clearFormFields($("panel-login"));
    $("login-pass").value = "";
    $("login-user").value = "";
    applyProtectedView(true);
    await paintSession();
  } catch (error) {
    showError("login-error", error);
  }
});

$("panel-register").addEventListener("submit", async (event) => {
  event.preventDefault();
  $("register-error").textContent = "";
  $("register-ok").textContent = "";
  try {
    const password = $("reg-pass").value;
    const confirm = $("reg-pass2").value;
    if (password !== confirm) {
      $("register-error").textContent = "Las contraseñas no coinciden.";
      return;
    }
    const result = await registerUser({
      username: $("reg-user").value,
      nombre: $("reg-name").value,
      password,
      confirm,
    });
    if (!result.ok) {
      $("register-error").textContent = result.error;
      return;
    }

    clearFormFields($("panel-register"));
    $("reg-pass").value = "";
    $("reg-pass2").value = "";
    $("reg-user").value = "";
    $("reg-name").value = "";
    applyProtectedView(true);
    await paintSession();
  } catch (error) {
    showError("register-error", error);
  }
});

$("logout").addEventListener("click", async () => {
  try {
    await logoutUser();
  } finally {
    clearFormFields($("panel-login"));
    clearFormFields($("panel-register"));
    $("login-error").textContent = "";
    $("register-error").textContent = "";
    $("register-ok").textContent = "";
    applyProtectedView(false);
    showAuthTab("login");
    await paintSession();
  }
});

$("tab-hub").addEventListener("click", () => openPanel("hub"));
$("tab-crud").addEventListener("click", () => openPanel("crud"));
$("tab-telemetry").addEventListener("click", () => openPanel("telemetry"));
$("filter-category").addEventListener("change", () => openPanel("hub"));
$("edit-target").addEventListener("change", () => openPanel("crud"));

$("form-app").addEventListener("submit", async (event) => {
  event.preventDefault();
  try {
    if (await saveAppFromForm()) await openPanel("crud");
  } catch (error) {
    showError("crud-error", error);
  }
});

$("delete-app").addEventListener("click", async () => {
  try {
    if (await deleteSelectedApp()) await openPanel("crud");
  } catch (error) {
    showError("crud-error", error);
  }
});

applyProtectedView(false);
showAuthTab("login");
paintSession();







































































































































































































































































































































