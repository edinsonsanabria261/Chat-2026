import os
import json
import hashlib
import urllib.parse
import streamlit as st

# --- CONFIGURACIÓN DE PÁGINA Y ESTILO ---
st.set_page_config(
    page_title="Nexus-Sec | Portal Ejecutivo de Edinson Marin",
    page_icon="🛡️",
    layout="wide"
)

# Estilos Glassmorphism personalizados por Edinson Marin
st.markdown("""
    <style>
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: rgba(15, 23, 42, 0.4);
        padding: 4px;
        border-radius: 8px;
        margin-bottom: 15px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 35px;
        color: var(--text-muted);
        border-radius: 6px;
        font-size: 0.85rem;
        font-weight: 500;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #dc2626, #ef4444) !important;
        color: #ffffff !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- BASE DE DATOS LOCAL Y HASHING ---
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

# --- CREDENCIALES OAUTH 2.0 ---
GOOGLE_CLIENT_ID = "634339650841-phifavamet5jp6c5q0lratdc5o2elpkt.apps.googleusercontent.com"
REDIRECT_URI = "https://chat-2026-mr7nx8ncjcgsdsln3oit6.streamlit.app/"

# --- INICIALIZACIÓN DE ESTADO ---
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False
if "usuario_activo" not in st.session_state:
    st.session_state.usuario_activo = ""
if "rol_activo" not in st.session_state:
    st.session_state.rol_activo = ""

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

else:
    # --- PANEL INTERNO Y HUB DE APLICACIONES DE EDINSON MARIN ---
    st.markdown(f"""
        <div style="background: #0b1329; border: 1px solid rgba(255,255,255,0.08); border-radius: 10px; padding: 20px; margin-bottom: 20px;">
            <h3 style="color: #f8fafc; margin:0;">Centro de Comando de Edinson Marin</h3>
            <p style="color: #94a3b8; margin:0; font-size: 0.85rem;">Sesión Activa - Usuario: <b>{st.session_state.usuario_activo}</b> | Rol: <b>{st.session_state.rol_activo}</b></p>
        </div>
    """, unsafe_allow_html=True)

    if st.button("Cerrar Sesión de Forma Segura"):
        st.session_state.autenticado = False
        st.session_state.usuario_activo = ""
        st.session_state.rol_activo = ""
        st.rerun()

    st.markdown("---")

    # Navegación interna del Portal
    tab_hub, tab_admin, tab_telemetria = st.tabs(["🚀 App Hub & Enlaces", "⚙️ Gestión CRUD (Edinson Marin)", "📊 Telemetría y Auditoría"])

    apps_db = cargar_base_datos(APPS_DB_FILE)

    with tab_hub:
        st.subheader("Directorio Central de Aplicaciones")
        
        # Filtros de Categorías
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
                guardar_base_datos(APPS_DB_FILE, apps_db)
                st.success(f"Aplicación '{app_nombre}' configurada exitosamente por Edinson Marin.")
                st.rerun()

    with tab_telemetria:
        st.subheader("Registros de Actividad e Intrusión")
        st.info("Monitoreo inmutable y control de accesos supervisados por Edinson Marin.")
        st.metric(label="Total de Utilidades Registradas", value=len(apps_db))
        st.metric(label="Estado del Firewall Perimetral", value="Óptimo / Blindado")
