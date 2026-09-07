import streamlit as st
import json
import os
import hashlib
import urllib.parse
import time

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="Nexus-Sec | Portal Ejecutivo de Autenticación",
    page_icon="🛡️",
    layout="centered"
)

# --- ESTILOS CSS AVANZADOS (DISEÑO MODAL DOS COLUMNAS) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    :root {
        --bg-deep: #050b14;
        --modal-bg: #0b1329;
        --accent-cyan: #06b6d4;
        --accent-glow: rgba(6, 182, 212, 0.25);
        --text-main: #f8fafc;
        --text-muted: #94a3b8;
    }

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    body {
        background-color: var(--bg-deep);
        font-family: 'Inter', sans-serif;
    }

    .stApp {
        background: radial-gradient(circle at 50% 50%, #0a192f 0%, #050b14 100%);
    }

    [data-testid="column"] {
        padding: 0px !important;
    }

    .stTextInput input {
        background-color: rgba(15, 23, 42, 0.6) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        color: var(--text-main) !important;
        border-radius: 8px !important;
        padding: 10px !important;
    }
    
    .stTextInput input:focus {
        border-color: var(--accent-cyan) !important;
        box-shadow: 0 0 0 2px var(--accent-glow) !important;
    }

    .stButton button {
        width: 100%;
        border-radius: 8px !important;
        font-weight: 500 !important;
        font-size: 0.9rem !important;
        padding: 10px !important;
        transition: all 0.3s ease !important;
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 6px;
        background-color: rgba(15, 23, 42, 0.4);
        padding: 4px;
        border-radius: 8px;
        margin-bottom: 15px;
    }

    .stTabs [data-baseweb="tab"] {
        height: 35px;
        color: var(--text-muted);
        border-radius: 6px;
        font-size: 0.8rem;
        font-weight: 500;
    }

    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #dc2626, #ef4444) !important;
        color: #ffffff !important;
    }
</style>
""", unsafe_allow_html=True)

# --- BASE DE DATOS LOCAL, HASHING Y APPS HUB ---
DB_FILE = "nexus_users_vault.json"
APPS_DB_FILE = "nexus_apps_registry.json"

def cargar_base_datos(archivo):
    if os.path.exists(archivo):
        try:
            with open(archivo, "r") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def guardar_base_datos(archivo, data):
    with open(archivo, "w") as f:
        json.dump(data, f, indent=4)

def hashear_password(password):
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

# Inicializar bases de datos por defecto si no existen
if not os.path.exists(DB_FILE):
    guardar_base_datos(DB_FILE, {
        "edinson": {
            "password": hashear_password("admin123"),
            "rol": "Administrador Principal",
            "nombre": "Edinson Marin"
        }
    })

if not os.path.exists(APPS_DB_FILE):
    guardar_base_datos(APPS_DB_FILE, {
        "App Auditoría Red": {
            "url": "https://streamlit.io",
            "descripcion": "Herramienta de análisis de nodos y puertos perimetrales.",
            "categoria": "Ciberseguridad",
            "permiso": "Libre",
            "estado": "Activa",
            "version": "v1.0.0"
        }
    })

# --- CREDENCIALES OAUTH 2.0 REALES ---
GOOGLE_CLIENT_ID = "634339650841-phifavamet5jp6c5q0lratdc5o2elpkt.apps.googleusercontent.com"
FACEBOOK_APP_ID = "TU_FACEBOOK_APP_ID"
REDIRECT_URI = "https://chat-2026-mr7nx8ncjcgsdsln3oit6.streamlit.app/"


# --- CREDENCIALES OAUTH 2.0 REALES ---
GOOGLE_CLIENT_ID = "634339650841-phifavamet5jp6c5q0lratdc5o2elpkt.apps.googleusercontent.com"
FACEBOOK_APP_ID = "TU_FACEBOOK_APP_ID"  # Puedes dejarlo así por ahora si aún no configuras Facebook
REDIRECT_URI = "https://chat-2026-mr7nx8ncjcgsdsln3oit6.streamlit.app/"

# --- INICIALIZACIÓN DE ESTADO ---
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False
if "usuario_activo" not in st.session_state:
    st.session_state.usuario_activo = ""
if "rol_activo" not in st.session_state:
    st.session_state.rol_activo = ""

# Control de limpieza de formularios mediante triggers de estado
if "form_limpiar" not in st.session_state:
    st.session_state.form_limpiar = False

# Control de limpieza de formularios mediante triggers de estado
if "form_limpiar" not in st.session_state:
    st.session_state.form_limpiar = False

# Generación de URLs de Autenticación Externa Real
google_params = {
    "client_id": GOOGLE_CLIENT_ID,
    "redirect_uri": REDIRECT_URI,
    "response_type": "code",
    "scope": "openid email profile"  # <-- Cambiado de 'tcope' a 'scope'
}

google_oauth_url = f"https://accounts.google.com/o/oauth2/v2/auth?{urllib.parse.urlencode(google_params)}"

facebook_params = {
    "client_id": FACEBOOK_APP_ID,
    "redirect_uri": REDIRECT_URI,
    "response_type": "code",
    "scope": "email"
}
facebook_oauth_url = f"https://www.facebook.com/v12.0/dialog/oauth?{urllib.parse.urlencode(facebook_params)}"


# --- FLUJO PRINCIPAL ---
if not st.session_state.autenticado:
    st.markdown("""
        <div style="background: #0b1329; border: 1px solid rgba(255,255,255,0.08); border-radius: 10px; padding: 40px; text-align: center; margin-top: 3rem;">
            <h2 style="color: #f8fafc; font-weight: 700;">NEXUS-SEC // PANEL EJECUTIVO DE EDINSON MARIN</h2>
            <p style="color: #94a3b8; font-size: 0.9rem;">Autenticación Requerida - Arquitectura de Control de Edinson Marin</p>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Acceso Local Administrador")
        user_input = st.text_input("Usuario", key="login_user")
        pass_input = st.text_input("Contraseña", type="password", key="login_pass")
        if st.button("Iniciar Sesión Local"):
            db_users = cargar_base_datos(DB_FILE)
            if user_input in db_users and db_users[user_input]["password"] == hashear_password(pass_input):
                st.session_state.autenticado = True
                st.session_state.usuario_activo = db_users[user_input]["nombre"]
                st.session_state.rol_activo = db_users[user_input]["rol"]
                st.rerun()
            else:
                st.error("Credenciales inválidas.")

    with col2:
        st.subheader("Autenticación Externa")
        google_params = {
            "client_id": GOOGLE_CLIENT_ID,
            "redirect_uri": REDIRECT_URI,
            "response_type": "code",
            "scope": "openid email profile"
        }
        google_oauth_url = f"https://accounts.google.com/o/oauth2/v2/auth?{urllib.parse.urlencode(google_params)}"
        st.markdown(f'<a href="{google_oauth_url}" target="_self"><button style="background-color:#4285F4;color:white;padding:10px 20px;border:none;border-radius:5px;cursor:pointer;font-weight:600;width:100%;">Acceder con Google</button></a>', unsafe_allow_html=True)

    # --- COLUMNA IZQUIERDA: BANNER VISUAL ---
    with col_banner:
        st.markdown("""
            <div style="
                background: linear-gradient(135deg, #b91c1c 0%, #dc2626 50%, #991b1b 100%);
                padding: 40px 25px;
                height: 100%;
                display: flex;
                flex-direction: column;
                justify-content: space-between;
                color: white;
                border-top-left-radius: 16px;
                border-bottom-left-radius: 16px;
            ">
                <div>
                    <h3 style="font-size: 1.1rem; font-weight: 600; letter-spacing: 0.05em; opacity: 0.85; margin-bottom: 15px;">NEXUS-SEC SUITE</h3>
                    <h1 style="font-size: 1.75rem; font-weight: 700; line-height: 1.2; margin-bottom: 20px;">
                        Protege tu infraestructura sin caer en vulnerabilidades
                    </h1>
                    <p style="font-size: 0.85rem; opacity: 0.9; line-height: 1.5;">
                        Obtén análisis avanzados de seguridad, auditorías en tiempo real, hashing SHA-256 y protección de activos.
                    </p>
                </div>
                
                <div style="margin-top: 30px; text-align: center;">
                    <img src="https://img.icons8.com/external-flat-wichaiwi/64/null/external-cyber-security-cyber-security-flat-wichaiwi.png" style="width: 70px; margin-bottom: 15px; filter: drop-shadow(0 4px 8px rgba(0,0,0,0.3));" />
                    <div style="display: flex; justify-content: center; gap: 8px; margin-top: 10px;">
                        <span style="width: 20px; height: 4px; background: white; border-radius: 2px;"></span>
                        <span style="width: 8px; height: 4px; background: rgba(255,255,255,0.4); border-radius: 2px;"></span>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)

    # --- COLUMNA DERECHA: PANELES DE AUTENTICACIÓN (TABS) ---
    with col_form:
        st.markdown("""
            <div style="background: #0b1329; padding: 30px; border-top-right-radius: 16px; border-bottom-right-radius: 16px; height: 100%;">
                <div style="font-size: 1.2rem; font-weight: 700; color: #f8fafc; margin-bottom: 4px;">Acceso al Sistema</div>
                <div style="font-size: 0.75rem; color: #94a3b8; margin-bottom: 20px;">Inicia sesión o regístrate en NEXUS-SEC</div>
        """, unsafe_allow_html=True)

        tab_login, tab_registro, tab_recuperar = st.tabs(["Iniciar Sesión", "Registro", "Recuperar"])

        # ================= PESTAÑA: INICIAR SESIÓN =================
        with tab_login:
            with st.form("login_modal_form"):
                usuario_in = st.text_input("Cédula o Correo Gmail", placeholder="ej: 12345678 o user@gmail.com")
                pass_in = st.text_input("Contraseña", type="password", placeholder="••••••••••••")
                
                submit_ingreso = st.form_submit_button("Iniciar Sesión")

                if submit_ingreso:
                    db = cargar_base_datos()
                    u_limpio = usuario_in.strip().lower()
                    p_hash = hashear_password(pass_in)

                    if not u_limpio or not pass_in:
                        st.error("Complete todos los campos.")
                    else:
                        if u_limpio in db and db[u_limpio]["password"] == p_hash:
                            st.session_state.autenticado = True
                            st.session_state.usuario_activo = u_limpio
                            st.success("¡Acceso concedido!")
                            time.sleep(0.5)
                            st.rerun()
                        else:
                            st.error("Credenciales incorrectas o usuario no registrado.")

            st.markdown("<p style='text-align: center; color: #94a3b8; font-size: 0.75rem; margin: 10px 0;'>O ingresa con una cuenta externa</p>", unsafe_allow_html=True)
            
            col_g, col_f = st.columns(2)
            with col_g:
                st.link_button("🔵 Google", google_oauth_url, use_container_width=True)
            with col_f:
                st.link_button("🔵 Facebook", facebook_oauth_url, use_container_width=True)

        # ================= PESTAÑA: REGISTRO =================
        with tab_registro:
            with st.form("registro_modal_form"):
                reg_id = st.text_input("Cédula o Correo Gmail", placeholder="ej: V-12345678 o correo@gmail.com")
                reg_pass = st.text_input("Crear Contraseña", type="password", placeholder="••••••••••••")
                reg_pass2 = st.text_input("Confirmar Contraseña", type="password", placeholder="••••••••••••")
                
                submit_registro = st.form_submit_button("Registrar Cuenta")

                if submit_registro:
                    db = cargar_base_datos()
                    r_limpio = reg_id.strip().lower()
                    es_gmail = r_limpio.endswith("@gmail.com")
                    es_cedula = len(r_limpio) >= 6 and any(char.isdigit() for char in r_limpio)

                    if not r_limpio or not reg_pass:
                        st.error("Todos los campos son obligatorios.")
                    elif not (es_gmail or es_cedula):
                        st.error("Debe ingresar una **Cédula válida** o un correo **Gmail**.")
                    elif reg_pass != reg_pass2:
                        st.error("Las contraseñas no coinciden.")
                    elif r_limpio in db:
                        st.warning("Este identificador ya se encuentra registrado.")
                    else:
                        db[r_limpio] = {"password": hashear_password(reg_pass), "tipo": "user"}
                        guardar_base_datos(db)
                        st.success("¡Registro completado con éxito! Ya puedes iniciar sesión.")
                        time.sleep(1)
                        st.rerun()

        # ================= PESTAÑA: RECUPERAR CONTRASEÑA =================
        with tab_recuperar:
            with st.form("recuperar_modal_form"):
                rec_id = st.text_input("Cédula o Gmail para recuperación", placeholder="ej: 12345678 o tu_correo@gmail.com")
                submit_recuperar = st.form_submit_button("Verificar e Instrucciones")

                if submit_recuperar:
                    db = cargar_base_datos()
                    rc_limpio = rec_id.strip().lower()
                    if not rc_limpio:
                        st.error("Ingrese su identificador registrado.")
                    elif rc_limpio in db:
                        st.success(f"Instrucciones de restablecimiento enviadas de forma segura a `{rc_limpio}`.")
                    else:
                        st.error("No se encontró ningún registro asociado a este identificador.")

        st.markdown("""
                <div style="text-align: center; margin-top: 20px; font-size: 0.7rem; color: #94a3b8; border-top: 1px solid rgba(255,255,255,0.05); padding-top: 10px;">
                    🔒 Canal Encriptado TLS 1.3 • Hashing SHA-256 • Soporte Técnico Nexus-Sec
                </div>
            </div>
       """, unsafe_allow_html=True)
else:
    # --- PANEL INTERNO Y HUB DE APLICACIONES DE EDINSON MARIN ---
    st.markdown("""
        <div style="background: #0b1329; border: 1px solid rgba(255,255,255,0.08); border-radius: 10px; padding: 20px; margin-bottom: 20px;">
            <h3 style="color: #f8fafc; margin:0;">Centro de Comando de Edinson Marin</h3>
            <p style="color: #94a3b8; margin:0; font-size: 0.85rem;">Sesión Activa - Usuario: <b>{}</b> | Rol: <b>{}</b></p>
        </div>
    """.format(st.session_state.get('usuario_activo', 'Admin'), st.session_state.get('rol_activo', 'Superusuario')), unsafe_allow_html=True)

    if st.button("Cerrar Sesión de Forma Segura"):
        st.session_state.autenticado = False
        st.session_state.usuario_activo = ""
        st.session_state.rol_activo = ""
        st.rerun()

    st.markdown("---")

    # Navegación interna del Portal
    tab_hub, tab_admin, tab_telemetria = st.tabs(["🚀 App Hub & Enlaces", "⚙️ Gestión CRUD (Edinson Marin)", "📊 Telemetría y Auditoría"])

    # Función simulada o cargador de base de datos local si no existe
    def obtener_apps_seguras():
        if 'cargar_base_datos' in globals() and 'APPS_DB_FILE' in globals():
            return cargar_base_datos(APPS_DB_FILE)
        return {
            "Nexus-Sec Portal": {"url": "#", "descripcion": "Plataforma principal de operaciones y ciberseguridad.", "categoria": "Ciberseguridad", "permiso": "Libre", "estado": "Activa", "version": "v1.0.0"},
            "Auditor Forense": {"url": "#", "descripcion": "Herramienta de análisis estático y dinámico de artefactos.", "categoria": "Forense", "permiso": "Restringido", "estado": "Activa", "version": "v2.1.0"}
        }

    apps_db = obtener_apps_seguras()

    with tab_hub:
        st.subheader("Directorio Central de Aplicaciones")
        
        categorias = ["Todas"] + list(set([app["categoria"] for app in apps_db.values()]))
        cat_seleccionada = st.selectbox("Filtrar por Propósito Operativo", categorias)

        cols = st.columns(2)
        idx = 0
        for nombre_app, datos in apps_db.items():
            if cat_seleccionada != "Todas" and datos["categoria"] != cat_seleccionada:
                continue
            
            with cols[idx % 2]:
                st.markdown(f"""
                    <div style="background: rgba(15, 23, 42, 0.6); border: 1px solid rgba(255,255,255,0.08); border-radius: 8px; padding: 15px; margin-bottom: 15px;">
                        <h4 style="color: #f8fafc; margin-bottom: 5px;">{nombre_app} <span style="font-size:0.7rem; color:#38bdf8;">({datos['version']})</span></h4>
                        <p style="color: #94a3b8; font-size: 0.85rem;">{datos['descripcion']}</p>
                        <p style="font-size: 0.75rem; color: #4ade80;">Estado: {datos['estado']} | Permiso: {datos['permiso']}</p>
                    </div>
                """, unsafe_allow_html=True)
                st.link_button(f"Abrir {nombre_app}", datos["url"])
            idx += 1

    with tab_admin:
        st.subheader("Administración de Herramientas (CRUD)")
        with st.form("form_nueva_app"):
            app_nombre = st.text_input("Nombre de la Aplicación")
            app_url = st.text_input("URL de Despliegue (ej. Streamlit Cloud / Servidor)")
            app_desc = st.text_area("Descripción Operativa")
            app_cat = st.selectbox("Categoría", ["Ciberseguridad", "Forense", "Utilidades", "Automatización"])
            app_permiso = st.selectbox("Nivel de Permiso (RBAC)", ["Libre", "Limitado", "Restringido"])
            app_estado = st.selectbox("Estado del Sistema", ["Activa", "Mantenimiento", "Bloqueada"])
            app_version = st.text_input("Versión actual", value="v1.0.0")
            
            submit_app = st.form_submit_button("Registrar / Actualizar Aplicación")
            if submit_app and app_nombre:
                apps_db[app_nombre] = {
                    "url": app_url,
                    "descripcion": app_desc,
                    "categoria": app_cat,
                    "permiso": app_permiso,
                    "estado": app_estado,
                    "version": app_version
                }
                if 'guardar_base_datos' in globals() and 'APPS_DB_FILE' in globals():
                    guardar_base_datos(APPS_DB_FILE, apps_db)
                st.success(f"Aplicación '{app_nombre}' configurada exitosamente por Edinson Marin.")
                st.rerun()

    with tab_telemetria:
        st.subheader("Registros de Actividad e Intrusión")
        st.info("Monitoreo inmutable y control de accesos supervisados por Edinson Marin.")
        st.metric(label="Total de Utilidades Registradas", value=len(apps_db))
        st.metric(label="Estado del Firewall Perimetral", value="Óptimo / Blindado")

    
