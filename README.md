# Chat-2026

Portal Nexus-Sec. El diseño sigue en `css/styles.css`. Cada cuenta entra al crearse y solo ve sus propias aplicaciones.

```
index.html          pantalla
css/styles.css      diseño
js/                 interfaz
server/index.js     acceso, directorio y telemetría
server/security.js  contraseña, sesión y cifrado
server/db.js        archivo de datos
```

La contraseña no se guarda. Los datos de cada usuario van cifrados y no los ve otra cuenta.

## Render

En el formulario de Web Service deja estos valores:

| Campo | Valor |
|---|---|
| Name | Chat-2026 |
| Language | Node |
| Branch | main |
| Region | Oregon |
| Root Directory | vacío |
| Build Command | yarn |
| Start Command | yarn start |

No hace falta una clave en este paso. Después de crearlo, en Disks añade un disco montado en `/data` y en Environment crea `DATA_DIR` = `/data`. Sin ese disco el portal arranca, pero olvida las cuentas en cada despliegue.

## Local

```bash
npm install
npm start
```

Abre `http://127.0.0.1:8080`.
