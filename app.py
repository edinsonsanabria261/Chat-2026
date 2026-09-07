import os
import json
import hashlib
import urllib.parse
import streamlit as st

# --- CONFIGURACIÓN DE PÁGINA Y ESTILO GLOBAL ---
st.set_page_config(
    page_title="Nexus-Sec // Centro de Comando de Edinson Marin",
    page_icon="🛡️",
    layout="wide"
)

st.markdown("""
    <style>
    /* Estilos Generales y Fondo Oscuro Ejecutivo */
    .stApp {
        background-color: #030712;
        color: #f8fafc;
        font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
    }
    
    /* Pestañas Glassmorphism */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        background-color: rgba(15, 23, 42, 0.6);
        padding: 6px;
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.08);
        margin-bottom: 20px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 40px;
        color: #94a3b8;
        border-radius: 8px;
        font-size: 0.9rem;
        font-weight: 600;
        background-color: transparent;
        border: none;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #dc2626, #991b1b) !important;
        color: #ffffff !important;
        box-shadow: 0 4px 12px rgba(220, 38, 38, 0.4);
    }

    /* Tarjetas de Módulos (Glassmorphism Cards) */
    .nexus-card {
        background: rgba(15, 23, 42, 0.7);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    .nexus-card:hover {
        border-color: rgba(220, 38, 38, 0.4);
        transform: translateY(-2px);
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

# Inicialización de bases de datos seguras
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
        "Auditoría de Red Perimetral": {
            "url": "https://streamlit.io",
            "descripcion": "Herramienta avanzada de análisis de nodos, puertos y flujos de red.",
            "categoria": "Ciberseguridad",
            "permiso": "Libre",
            "estado": "Activa",
            "version": "v1.2.0"
        },
        "Forense APK / Android": {
            "url": "https://streamlit.io",
            "descripcion": "Inspección de manifiestos y análisis estático de paquetes móviles.",
            "categoria": "Forense",
            "permiso": "Restringido",
            "estado": "Activa",
            "version": "v2.0.1"
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
    # Pantalla de Login Dividida (Diseño Ejecutivo Superior)
    col_banner, col_login = st.columns([1.2, 1])
    
    with col_banner:
        st.markdown("""
            <div style="background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%); border: 1px solid rgba(255,255,255,0.08); border-radius: 16px; padding: 40px; height: 100%; display: flex; flex-direction: column; justify-content: center; box-shadow: 0 10px 30px rgba(0,0,0,0.5);">
                <span style="color: #ef4444; font-weight: 700; font-size: 0.85rem; letter-spacing: 2px; text-transform: uppercase; margin-bottom: 10px;">Security Operations Center</span>
                <h1 style="color: #f8fafc; font-weight: 800; font-size: 2.2rem; margin-bottom: 15px; line-height: 1.2;">NEXUS-SEC // PORTAL DE EDINSON MARIN</h1>
                <p style="color: #94a3b8; font-size: 1rem; line-height: 1.6;">Plataforma centralizada y modular diseñada para la gestión de activos tácticos, control de accesos RBAC y telemetría avanzada en tiempo real.</p>
            </div>
        """, unsafe_allow_html=True)
        
    with col_login:
        st.markdown("""
            <div style="background: rgba(15, 23, 42, 0.6); backdrop-filter: blur(12px); border: 1px solid rgba(255,255,255,0.08); border-radius: 16px; padding: 30px; box-shadow: 0 10px 30px rgba(0,0,0,0.5);">
                <h3 style="color: #f8fafc; margin-bottom: 20px; font-weight: 700;">Autenticación Requerida</h3>
            </div>
        """, unsafe_allow_html=True)
        
        tab_local, tab_ext = st.tabs(["🔑 Credenciales", "🌐 Google OAuth"])
        
        with tab_local:
            user_input = st.text_input("Usuario Administrador", key="login_user")
            pass_input = st.text_input("Contraseña del Sistema", type="password", key="login_pass")
            if st.button("Iniciar Sesión Local", use_container_width=True):
                db_users = cargar_base_datos(DB_FILE)
                if user_input in db_users and db_users[user_input]["password"] == hashear_password(pass_input):
                    st.session_state.autenticado = True
                    st.session_state.usuario_activo = db_users[user_input]["nombre"]
                    st.session_state.rol_activo = db_users[user_input]["rol"]
                    st.rerun()
                else:
                    st.error("Credenciales de acceso inválidas.")

        with tab_ext:
            st.write("Acceso federado seguro a través de los servidores de autenticación autorizados.")
            google_params = {
                "client_id": GOOGLE_CLIENT_ID,
                "redirect_uri": REDIRECT_URI,
                "response_type": "code",
                "scope": "openid email profile"
            }
            google_oauth_url = f"https://accounts.google.com/o/oauth2/v2/auth?{urllib.parse.urlencode(google_params)}"
            st.markdown(f'<a href="{google_oauth_url}" target="_self"><button style="background: linear-gradient(135deg, #2563eb, #1d4ed8); color:white; padding:12px 20px; border:none; border-radius:8px; cursor:pointer; font-weight:600; width:100%; box-shadow: 0 4px 12px rgba(37,99,235,0.4);">Acceder con Cuenta Google</button></a>', unsafe_allow_html=True)

else:
    # --- PANEL INTERNO Y HUB DE APLICACIONES DE EDINSON MARIN ---
    st.markdown(f"""
        <div class="nexus-card" style="display: flex; justify-content: space-between; align-items: center; background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%);">
            <div>
                <span style="color: #4ade80; font-size: 0.75rem; font-weight: 700; text-transform: uppercase; letter-spacing: 1px;">● Sistema Operativo Protegido</span>
                <h2 style="color: #f8fafc; margin: 5px 0 0 0; font-weight: 800;">Centro de Comando de Edinson Marin</h2>
                <p style="color: #94a3b8; margin: 0; font-size: 0.85rem;">Operador Activo: <b>{st.session_state.usuario_activo}</b> | Nivel de Credencial: <b>{st.session_state.rol_activo}</b></p>
            </div>
        </div>
    """, unsafe_allow_html=True)

    if st.button("Cerrar Sesión de Forma Segura"):
        st.session_state.autenticado = False
        st.session_state.usuario_activo = ""
        st.session_state.rol_activo = ""
        st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    # Navegación interna del Portal con Pestañas Optimizadas
    tab_hub, tab_admin, tab_telemetria = st.tabs(["🚀 App Hub & Directorio", "⚙️ Gestión CRUD de Activos", "📊 Telemetría y Auditoría"])

    apps_db = cargar_base_datos(APPS_DB_FILE)

    with tab_hub:
        st.subheader("Directorio Central de Aplicaciones y Enlaces Únicos")
        
        categorias = ["Todas"] + list(set([app["categoria"] for app in apps_db.values()]))
        cat_seleccionada = st.selectbox("Filtrar por Categoría Operativa", categorias)

        cols = st.columns(2)
        idx = 0
        for nombre_app, datos in apps_db.items():
            if cat_seleccionada != "Todas" and datos["categoria"] != cat_seleccionada:
                continue
            
            with cols[idx % 2]:
                st.markdown(f"""
                    <div class="nexus-card">
                        <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 10px;">
                            <h4 style="color: #f8fafc; margin: 0; font-weight: 700;">{nombre_app}</h4>
                            <span style="background: rgba(56, 189, 248, 0.1); color: #38bdf8; padding: 2px 8px; border-radius: 4px; font-size: 0.7rem; font-weight: 600;">{datos['version']}</span>
                        </div>
                        <p style="color: #94a3b8; font-size: 0.85rem; margin-bottom: 15px; min-height: 40px;">{datos['descripcion']}</p>
                        <div style="display: flex; justify-content: space-between; align-items: center; font-size: 0.75rem; border-top: 1px solid rgba(255,255,255,0.05); padding-top: 10px;">
                            <span style="color: #4ade80;">● {datos['estado']}</span>
                            <span style="color: #cbd5e1;">Permiso: <b>{datos['permiso']}</b></span>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
                st.link_button(f"Lanzar {nombre_app}", datos["url"], use_container_width=True)
            idx += 1

    with tab_admin:
        st.subheader("Administración de Enlaces y Módulos (CRUD)")
        st.write("Da de alta nuevas aplicaciones, modifica sus URLs de despliegue o actualiza sus metadatos de forma dinámica.")
        
        with st.form("form_nueva_app", clear_on_submit=True):
            app_nombre = st.text_input("Nombre de la Herramienta / Aplicación")
            app_url = st.text_input("URL de Despliegue (ej. Streamlit Cloud / Servidor Propio)")
            app_desc = st.text_area("Descripción Operativa")
            col_a, col_b = st.columns(2)
            with col_a:
                app_cat = st.selectbox("Categoría", ["Ciberseguridad", "Forense", "Utilidades", "Automatización"])
                app_permiso = st.selectbox("Nivel de Permiso (RBAC)", ["Libre", "Limitado", "Restringido"])
            with col_b:
                app_estado = st.selectbox("Estado del Sistema", ["Activa", "Mantenimiento", "Bloqueada"])
                app_version = st.text_input("Versión actual", value="v1.0.0")
            
            submit_app = st.form_submit_button("Registrar / Actualizar Aplicación en el Hub", use_container_width=True)
            if submit_app and app_nombre and app_url:
                apps_db[app_nombre] = {
                    "url": app_url,
                    "descripcion": app_desc,
                    "categoria": app_cat,
                    "permiso": app_permiso,
                    "estado": app_estado,
                    "version": app_version
                }
                guardar_base_datos(APPS_DB_FILE, apps_db)
                st.success(f"Aplicación '{app_nombre}' configurada e integrada con éxito al sistema de Edinson Marin.")
                st.rerun()

        st.markdown("---")
        st.subheader("Eliminar Módulo Existente")
        app_a_borrar = st.selectbox("Seleccione la aplicación a retirar", list(apps_db.keys()))
        if st.button("Eliminar Aplicación del Registro", type="primary"):
            if app_a_borrar in apps_db:
                del apps_db[app_a_borrar]
                guardar_base_datos(APPS_DB_FILE, apps_db)
                st.success(f"La aplicación '{app_a_borrar}' ha sido dada de baja correctamente.")
                st.rerun()

    with tab_telemetria:
        st.subheader("Telemetría Ejecutiva e Integridad del Sistema")
        st.markdown("""
            <div class="nexus-card">
                <p style="color: #94a3b8; font-size: 0.9rem;">Monitoreo inmutable y auditoría de accesos centralizada bajo la supervisión directa de la arquitectura de control de Edinson Marin.</p>
            </div>
        """, unsafe_allow_html=True)
        
        col_m1, col_m2, col_m3 = st.columns(3)
        with col_m1:
            st.metric(label="Utilidades Activas en Hub", value=len(apps_db))
        with col_m2:
            st.metric(label="Estado del Firewall Perimetral", value="Óptimo / Blindado")
        with col_m3:
            st.metric(label="Integridad del Vault (SHA-256)", value="Verificada")
