import { currentSession, loginUser, logoutUser, registerUser } from "./auth.js";
import {
  deleteSelectedApp,
  renderCrud,
  renderHub,
  saveAppFromForm,
  showAuthTab,
  showPanel,
} from "./portal.js";

const $ = (id) => document.getElementById(id);

function showError(id, error) {
  $(id).textContent = error?.message || error || "No se pudo completar la acción.";
}

function paintSession() {
  const logged = Boolean(currentSession());
  $("view-login").hidden = logged;
  $("view-app").hidden = !logged;
  if (!logged) return;
  const session = currentSession();
  $("session-line").textContent = `Sesión activa · ${session.nombre} · ${session.rol}`;
  showPanel("hub");
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

$("logout").addEventListener("click", () => {
  logoutUser();
  paintSession();
});

$("tab-hub").addEventListener("click", () => showPanel("hub"));
$("tab-crud").addEventListener("click", () => showPanel("crud"));
$("tab-telemetry").addEventListener("click", () => showPanel("telemetry"));
$("filter-category").addEventListener("change", renderHub);
$("edit-target").addEventListener("change", renderCrud);

$("form-app").addEventListener("submit", async (event) => {
  event.preventDefault();
  try {
    if (await saveAppFromForm()) {
      renderCrud();
      renderHub();
    }
  } catch (error) {
    showError("crud-error", error);
  }
});

$("delete-app").addEventListener("click", async () => {
  try {
    if (await deleteSelectedApp()) {
      renderCrud();
      renderHub();
    }
  } catch (error) {
    showError("crud-error", error);
  }
});

paintSession();
