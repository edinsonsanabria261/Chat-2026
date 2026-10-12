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

async function paintSession() {
  const session = await refreshSession();
  $("view-login").hidden = Boolean(session);
  $("view-app").hidden = !session;
  if (!session) return;
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
    paintSession();
  } catch (error) {
    showError("login-error", error);
  }
});

$("panel-register").addEventListener("submit", async (event) => {
  event.preventDefault();
  $("register-error").textContent = "";
  $("register-ok").textContent = "";
  try {
    const result = await registerUser({
      username: $("reg-user").value,
      nombre: $("reg-name").value,
      password: $("reg-pass").value,
    });
    if (!result.ok) {
      $("register-error").textContent = result.error;
      return;
    }
    $("reg-pass").value = "";
    $("register-ok").textContent = "Registro listo. Ya puedes iniciar sesión.";
    showAuthTab("login");
    $("login-user").value = $("reg-user").value.trim();
  } catch (error) {
    showError("register-error", error);
  }
});

$("logout").addEventListener("click", async () => {
  await logoutUser();
  await paintSession();
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

paintSession();
