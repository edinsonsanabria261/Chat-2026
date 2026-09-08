import os
import json
import hashlib
import urllib.parse
import streamlit as st

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="Nexus-Sec | Portal Ejecutivo de Edinson Marin",
    page_icon="🛡️",
    layout="wide"
)

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

# Inicializar base de datos por defecto
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
if "username_key" not in st.session_state:
    st.session_state.username_key = ""

# --- FLUJO PRINCIPAL ---
if not st.session_state.autenticado:
    col_banner, col_login = st.columns([1, 1.2])
    
    with col_banner:
        st.markdown("""
            <div style="background: linear-gradient(135deg, #dc2626 0%, #991b1b 100%); border-radius: 12px; padding: 35px; color: white; box-shadow: 0 10px 25px rgba(220,38,38,0.3);">
                <p style="font-size: 0.8rem; font-weight: 700; letter-spacing: 1px; text-transform: uppercase; margin-bottom: 5px;">Nexus-Sec Suite</p>
                <h1 style="font-size: 1.8rem; font-weight: 800; line-height: 1.2; margin-bottom: 15px;">Protege tu infraestructura sin caer en vulnerabilidades</h1>
                <p style="font-size: 0.9rem; opacity: 0.9; line-height: 1.5;">Obtén análisis avanzados de seguridad, auditorías en tiempo real y protección de activos de alto rendimiento.</p>
            </div>
        """, unsafe_allow_html=True)
        
    with col_login:
        st.subheader("Acceso al Sistema")
        st.caption("Inicia sesión o regístrate en NEXUS-SEC")
        
        tab_login, tab_reg = st.tabs(["Iniciar Sesión", "Registro"])
        
        with tab_login:
            user_input = st.text_input("Usuario o Correo", key="login_user_input")
            pass_input = st.text_input("Contraseña", type="password", key="login_pass_input")
            if st.button("Iniciar Sesión", use_container_width=True):
                db_users = cargar_base_datos(DB_FILE)
                if user_input in db_users and db_users[user_input]["password"] == hashear_password(pass_input):
                    st.session_state.autenticado = True
                    st.session_state.usuario_activo = db_users[user_input]["nombre"]
                    st.session_state.rol_activo = db_users[user_input]["rol"]
                    st.session_state.username_key = user_input
                    st.rerun()
                else:
                    st.error("Credenciales inválidas.")

        with tab_reg:
            nuevo_u = st.text_input("Nuevo Usuario", key="reg_u")
            nuevo_n = st.text_input("Nombre Completo", key="reg_n")
            nuevo_p = st.text_input("Contraseña", type="password", key="reg_p")
            if st.button("Registrarse", use_container_width=True):
                db_users = cargar_base_datos(DB_FILE)
                if nuevo_u in db_users:
                    st.error("El usuario ya existe.")
                elif nuevo_u and nuevo_p:
                    db_users[nuevo_u] = {
                        "password": hashear_password(nuevo_p),
                        "rol": "Operador",
                        "nombre": nuevo_n if nuevo_n else nuevo_u
                    }
                    guardar_base_datos(DB_FILE, db_users)
                    st.success("¡Registrado con éxito! Ya puedes iniciar sesión.")
                else:
                    st.warning("Completa los campos obligatorios.")

        st.markdown("<p style='text-align: center; font-size: 0.8rem; color: #94a3b8; margin-top: 15px;'>O ingresa mediante proveedor externo</p>", unsafe_allow_html=True)
        
        col_g, _ = st.columns(2)
        with col_g:
            google_params = {
                "client_id": GOOGLE_CLIENT_ID,
                "redirect_id": REDIRECT_URI,
                "response_type": "code",
                "scope": "openid email profile"
            }
            google_oauth_url = f"https://accounts.google.com/o/oauth2/v2/auth?{urllib.parse.urlencode(google_params)}"
            st.markdown(f'<a href="{google_oauth_url}" target="_self"><button style="background-color:#ea4335;color:white;padding:8px 16px;border:none;border-radius:6px;cursor:pointer;font-weight:600;width:100%;">Google</button></a>', unsafe_allow_html=True)

        st.markdown("<br><p style='text-align: center; font-size: 0.75rem; color: #64748b;'>🔒 Canal Encriptado TLS 1.3 - Soporte Técnico Nexus-Sec</p>", unsafe_allow_html=True)

else:
    # --- PANEL INTERNO DE EDINSON MARIN ---
    st.markdown(f"""
        <div style="background: #0f172a; border: 1px solid rgba(255,255,255,0.08); border-radius: 10px; padding: 20px; margin-bottom: 20px;">
            <h3 style="color: #f8fafc; margin:0;">Centro de Comando de Edinson Marin</h3>
            <p style="color: #94a3b8; margin:0; font-size: 0.85rem;">Sesión Activa - Usuario: <b>{st.session_state.usuario_activo}</b> | Rol: <b>{st.session_state.rol_activo}</b></p>
        </div>
    """, unsafe_allow_html=True)

    if st.button("Cerrar Sesión"):
        st.session_state.autenticado = False
        st.session_state.usuario_activo = ""
        st.session_state.rol_activo = ""
        st.session_state.username_key = ""
        st.rerun()

    st.markdown("---")

    tab_hub, tab_admin, tab_telemetria = st.tabs(["🚀 App Hub & Enlaces", "⚙️ Gestión CRUD", "📊 Telemetría"])
    apps_db = cargar_base_datos(APPS_DB_FILE)

    with tab_hub:
        st.subheader("Directorio Central de Aplicaciones")
        categorias = ["Todas"] + list(set([app["categoria"] for app in apps_db.values()]))
        cat_seleccionada = st.selectbox("Filtrar por Categoría", categorias)

        cols = st.columns(2)
        idx = 0
        for nombre_app, datos in apps_db.items():
            if cat_seleccionada != "Todas" and datos["categoria"] != cat_seleccionada:
                continue
            with cols[idx % 2]:
                st.markdown(f"""
                    <div style="background: #0f172a; border: 1px solid rgba(255,255,255,0.08); border-radius: 8px; padding: 15px; margin-bottom: 15px;">
                        <h4 style="color: #f8fafc; margin-bottom: 5px;">{nombre_app} <span style="font-size:0.7rem; color:#38bdf8;">({datos['version']})</span></h4>
                        <p style="color: #94a3b8; font-size: 0.85rem;">{datos['descripcion']}</p>
                        <p style="font-size: 0.75rem; color: #4ade80;">Estado: {datos['estado']} | Permiso: {datos['permiso']}</p>
                    </div>
                """, unsafe_allow_html=True)
                st.link_button(f"Abrir {nombre_app}", datos["url"])
            idx += 1

    with tab_admin:
        st.subheader("Administración de Herramientas (CRUD)")
        st.info("🔒 Sección protegida con contraseña para autorizar cambios.")
        
        with st.form("form_app"):
            app_nombre = st.text_input("Nombre de la Aplicación")
            app_url = st.text_input("URL de Despliegue")
            app_desc = st.text_area("Descripción")
            app_cat = st.selectbox("Categoría", ["Ciberseguridad", "Forense", "Utilidades", "Automatización"])
            app_permiso = st.selectbox("Permiso", ["Libre", "Limitado", "Restringido"])
            app_estado = st.selectbox("Estado", ["Activa", "Mantenimiento", "Bloqueada"])
            app_version = st.text_input("Versión", value="v1.0.0")
            
            # --- CAMPO DE CONTRASEÑA AGREGADO PARA PROTEGER EL CRUD ---
            crud_pass_confirm = st.text_input("Confirma tu contraseña para guardar cambios", type="password")
            
            if st.form_submit_button("Guardar Aplicación"):
                db_users = cargar_base_datos(DB_FILE)
                user_key = st.session_state.username_key
                
                # Validar que la contraseña introducida coincida con la del usuario logueado
                if user_key in db_users and db_users[user_key]["password"] == hashear_password(crud_pass_confirm):
                    if app_nombre:
                        apps_db[app_nombre] = {
                            "url": app_url, "descripcion": app_desc, "categoria": app_cat,
                            "permiso": app_permiso, "estado": app_estado, "version": app_version
                        }
                        guardar_base_datos(APPS_DB_FILE, apps_db)
                        st.success("Guardado correctamente.")
                        st.rerun()
                    else:
                        st.warning("El nombre de la aplicación es obligatorio.")
                else:
                    st.error("Contraseña incorrecta. No se pudieron aplicar los cambios.")

    with tab_telemetria:
        st.subheader("Telemetría del Sistema")
        st.metric("Total de Aplicaciones", len(apps_db))
        st.metric("Estado del Nodo", "Estable / Seguro")
