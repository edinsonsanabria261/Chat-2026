# Chat-2026

Portal Nexus-Sec: acceso, directorio de aplicaciones, gestión y telemetría.

El diseño sigue el portal original. La interfaz está en CSS y la lógica en módulos JavaScript.

```
index.html          pantalla
css/styles.css      diseño
js/main.js          eventos
js/auth.js          registro, sesión y contraseña
js/portal.js        hub, gestión y telemetría
js/store.js         datos del navegador
```

## Cómo abrirlo

Hace falta HTTPS o un servidor local. Abrir el archivo directo no puede proteger la contraseña.

```bash
python3 -m http.server 8080
```

Entra en `http://127.0.0.1:8080`.

La primera cuenta que se registre queda como administrador. Las siguientes entran como operador y pueden ver el directorio, no editarlo.

Los datos se guardan en este navegador. No hay servidor ni cuentas compartidas entre equipos.
