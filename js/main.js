import { loginUser, logoutUser, refreshSession, registerUser } from "./auth.js";
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

function applyProtectedView(sessionActive) {
  $("view-login").hidden = sessionActive;
  $("view-app").hidden = !sessionActive;
}

async function paintSession() {
  const session = await refreshSession();
  applyProtectedView(Boolean(session));
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
    $("login-pass").value = "";
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
    $("reg-pass").value = "";
    $("reg-pass2").value = "";
    await paintSession();
  } catch (error) {
    showError("register-error", error);
  }
});

$("logout").addEventListener("click", async () => {
  try {
    await logoutUser();
  } finally {
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
