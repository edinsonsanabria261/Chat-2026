<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Nexus-Sec | Portal</title>
  <link rel="stylesheet" href="css/styles.css" />
</head>
<body>
  <main id="view-login" class="login-layout" hidden>
    <section class="hero" aria-label="Nexus-Sec Suite">
      <p class="eyebrow">Nexus-Sec Suite</p>
      <h1>Protege tu infraestructura sin caer en vulnerabilidades</h1>
      <p class="hero-copy">Análisis de seguridad, directorio de herramientas y control de accesos en un solo portal.</p>
    </section>

    <section class="auth-card" aria-label="Acceso al sistema">
      <h2>Acceso al Sistema</h2>
      <p class="muted">Inicia sesión o regístrate en NEXUS-SEC</p>

      <div class="tabs" role="tablist" aria-label="Acceso">
        <button type="button" id="tab-login" role="tab" aria-selected="true" aria-controls="panel-login">Iniciar Sesión</button>
        <button type="button" id="tab-register" role="tab" aria-selected="false" aria-controls="panel-register">Registro</button>
      </div>

      <form id="panel-login" class="panel" role="tabpanel">
        <label for="login-user">Usuario</label>
        <input id="login-user" name="username" type="email" autocomplete="username" required />
        <label for="login-pass">Contraseña</label>
        <input id="login-pass" name="password" type="password" autocomplete="current-password" required />
        <p id="login-error" class="form-error" role="alert"></p>
        <button class="btn-primary" type="submit">Iniciar Sesión</button>
      </form>

      <form id="panel-register" class="panel" role="tabpanel" hidden>
        <label for="reg-user">Nuevo usuario</label>
        <input id="reg-user" name="username" type="email" autocomplete="username" required />
        <p class="hint">Introduce un correo electrónico válido, por ejemplo: usuario@ejemplo.com</p>
        <label for="reg-name">Nombre completo</label>
        <input id="reg-name" name="nombre" autocomplete="name" />
        <label for="reg-pass">Contraseña</label>
        <input id="reg-pass" name="password" type="password" autocomplete="new-password" required />
        <p class="hint">Mínimo 8 caracteres. Se distinguen mayúsculas y minúsculas.</p>
        <label for="reg-pass2">Repite la contraseña</label>
        <input id="reg-pass2" name="confirm" type="password" autocomplete="new-password" required />
        <p id="register-error" class="form-error" role="alert"></p>
        <p id="register-ok" class="form-ok" role="status"></p>
        <button class="btn-primary" type="submit">Crear cuenta</button>
      </form>

      <p class="fine-print">Al crear la cuenta entras directo. Tus datos quedan separados de los demás.</p>
    </section>
  </main>

  <main id="view-app" class="app-shell" hidden>
    <header class="command">
      <div>
        <h2>Bienvenido a MarinDrawset</h2>
        <p id="session-line"></p>
      </div>
      <div class="header-actions">
        <button id="account-button" class="btn-ghost" type="button">Cuenta</button>
        <button id="logout" class="btn-ghost" type="button">Cerrar Sesión</button>
      </div>
    </header>

    <div id="account-menu" class="account-menu" aria-hidden="true">
      <div class="account-panel" role="dialog" aria-modal="true" aria-labelledby="account-menu-title">
        <div class="account-panel-header">
          <div>
            <p class="eyebrow small">Configuración</p>
            <h3 id="account-menu-title">Cuenta y Seguridad</h3>
          </div>
          <button id="close-account-menu" class="close-menu" type="button" aria-label="Cerrar configuración">×</button>
        </div>

        <div class="account-tabs">
          <button type="button" class="account-tab active" data-account-tab="password">Cambiar Contraseña</button>
          <button type="button" class="account-tab" data-account-tab="profile">Administrar Cuenta</button>
        </div>

        <div id="account-password-panel" class="account-panel-body active">
          <form id="account-password-form" class="account-form">
            <label for="current-password">Contraseña actual</label>
            <input id="current-password" name="currentPassword" type="password" placeholder="••••••••" required />

            <label for="new-password">Nueva contraseña</label>
            <input id="new-password" name="newPassword" type="password" placeholder="Mínimo 8 caracteres" required />

            <label for="confirm-password">Confirmar nueva contraseña</label>
            <input id="confirm-password" name="confirmPassword" type="password" placeholder="Repite la nueva contraseña" required />

            <p id="password-status" class="field-status" aria-live="polite"></p>
            <button type="submit" class="btn-primary compact">Actualizar contraseña</button>
          </form>
        </div>

        <div id="account-profile-panel" class="account-panel-body">
          <form id="account-profile-form" class="account-form">
            <label for="profile-name">Nombre</label>
            <input id="profile-name" name="name" type="text" placeholder="Tu nombre" />

            <label for="profile-email">Usuario / Correo</label>
            <input id="profile-email" name="email" type="email" placeholder="usuario@ejemplo.com" />

            <p id="profile-status" class="field-status" aria-live="polite"></p>
            <button type="submit" class="btn-primary compact">Guardar perfil</button>
          </form>
        </div>
      </div>
    </div>

    <div class="tabs" role="tablist" aria-label="Portal">
      <button type="button" id="tab-hub" role="tab" aria-selected="true">App Hub</button>
      <button type="button" id="tab-crud" role="tab" aria-selected="false">Gestión</button>
      <button type="button" id="tab-telemetry" role="tab" aria-selected="false">Telemetría</button>
    </div>

    <section id="panel-hub" class="panel-block">
      <div class="panel-head">
        <h3>Directorio de aplicaciones</h3>
      </div>

      <div class="hub-toolbar">
        <label class="filter-field">
          Buscar
          <input id="app-search" type="search" placeholder="Nombre, URL, descripción..." />
        </label>

        <label class="filter-field">
          Estado
          <select id="filter-state" class="dark-select">
            <option value="Todos">Todos</option>
            <option value="Activa">Activas</option>
            <option value="Mantenimiento">Mantenimiento</option>
            <option value="Bloqueada">Bloqueadas</option>
          </select>
        </label>

        <label class="filter-field">
          Categoría
          <select id="filter-category" class="dark-select"></select>
        </label>

        <label class="filter-field">
          Orden
          <select id="hub-sort" class="dark-select">
            <option value="name">Nombre</option>
            <option value="status">Estado</option>
            <option value="updated">Actualizadas</option>
          </select>
        </label>
      </div>

      <div id="app-grid" class="app-grid"></div>
    </section>

    <section id="panel-crud" class="panel-block" hidden>
      <h3>Administración de herramientas</h3>
      <p id="crud-note" class="muted"></p>
      <form id="form-app" class="crud-form">
        <label for="edit-target">Aplicación</label>
        <select id="edit-target" class="dark-select"></select>

        <label for="app-name">Nombre</label>
        <input id="app-name" required />

        <label for="app-url">URL de despliegue</label>
        <input id="app-url" type="url" placeholder="https://" required />

        <label for="app-desc">Descripción</label>
        <textarea id="app-desc" rows="3" required></textarea>

        <div class="form-row">
          <label>Categoría
            <select id="app-cat" class="dark-select">
              <option>OSINT / Reconocimiento</option>
              <option>Auditoría Web</option>
              <option>Análisis de Redes</option>
              <option>Herramientas de IA</option>
            </select>
          </label>
          <label>Permiso
            <select id="app-permiso" class="dark-select">
              <option>Libre</option>
              <option>Limitado</option>
              <option>Restringido</option>
            </select>
          </label>
        </div>

        <div class="form-row">
          <label>Estado
            <select id="app-estado" class="dark-select">
              <option>Activa</option>
              <option>Mantenimiento</option>
              <option>Bloqueada</option>
            </select>
          </label>
          <label>Versión
            <input id="app-version" value="v1.0.0" required />
          </label>
        </div>

        <div class="form-row">
          <label>Prioridad
            <select id="app-prioridad" class="dark-select">
              <option value="Baja">Baja</option>
              <option value="Media" selected>Media</option>
              <option value="Alta">Alta</option>
              <option value="Crítica">Crítica</option>
            </select>
          </label>
          <label>Responsable
            <input id="app-responsable" placeholder="Tu nombre" />
          </label>
        </div>

        <div class="form-row">
          <label>Etiquetas
            <input id="app-tags" placeholder="seguridad, red, ia" />
          </label>
          <label class="checkbox-field">
            <span>Favorita</span>
            <input id="app-favorita" type="checkbox" />
          </label>
        </div>

        <p id="crud-error" class="form-error" role="alert"></p>
        <div class="crud-actions">
          <button class="btn-primary compact" type="submit">Guardar aplicación</button>
          <button id="delete-app" class="btn-danger" type="button">Eliminar</button>
        </div>
      </form>
    </section>

    <section id="panel-telemetry" class="panel-block" hidden>
      <h3>Telemetría del sistema</h3>
      <div id="metrics" class="metrics"></div>
    </section>
  </main>

  <script type="module" src="js/main.js"></script>
</body>
</html>
