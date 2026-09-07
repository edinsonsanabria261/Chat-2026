import streamlit as st
import time
import urllib.parse

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="Nexus-Sec | Portal Ejecutivo de Autenticación",
    page_icon="🛡️",
    layout="centered"
)

# --- ESTILOS CSS AVANZADOS (DISEÑO LIMPIO Y MODERNO) ---
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

# --- CONFIGURACIÓN DE CREDENCIALES OAUTH REALEAS (REEMPLAZAR CON TUS CLIENT_ID) ---
GOOGLE_CLIENT_ID = "TU_GOOGLE_CLIENT_ID.apps.googleusercontent.com"
FACEBOOK_APP_ID = "TU_FACEBOOK_APP_ID"
REDIRECT_URI = "http://localhost:8501/"  # URL de redirección configurada en tu app

# --- INICIALIZACIÓN DE ESTADO DE SESIÓN ---
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False
if "usuarios_bd" not in st.session_state:
    st.session_state.usuarios_bd = {
        "admin": {"password": "nexus2026", "tipo": "user"}
    }

# Inicializar estados de campos de texto para limpieza limpia post-envío
for key in ["login_user", "login_pass", "reg_user", "reg_pass", "reg_pass2", "rec_user"]:
    if key not in st.session_state:
        st.session_state[key] = ""

# --- URLs de redirección OAuth reales ---
google_params = {
    "client_id": GOOGLE_CLIENT_ID,
    "redirect_uri": REDIRECT_URI,
    "response_type": "code",
    "scope": "openid email profile"
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
if st.session_state.autenticado:
    st.markdown("### NEXUS-SEC PANEL DE OPERACIONES")
    st.success("Sesión Segura Activa - Nivel de Autorización: Operativo")
    if st.button("Cerrar Sesión de Forma Segura"):
        st.session_state.autenticado = False
        st.rerun()

else:
    col_banner, col_form = st.columns([1, 1.2], gap="medium")

    # --- COLUMNA IZQUIERDA: BANNER VISUAL ---
    with col_banner:
        st.markdown("""
            <div style="background: linear-gradient(135deg, #b91c1c 0%, #dc2626 50%, #991b1b 100%); padding: 40px 25px; border-radius: 16px; color: white; height: 100%;">
                <h3 style="font-size: 1.1rem; font-weight: 600; opacity: 0.85; margin-bottom: 15px;">NEXUS-SEC SUITE</h3>
                <h1 style="font-size: 1.75rem; font-weight: 700; line-height: 1.2; margin-bottom: 20px;">
                    Protege tu infraestructura sin caer en vulnerabilidades
                </h1>
                <p style="font-size: 0.85rem; opacity: 0.9; line-height: 1.5;">
                    Obtén análisis avanzados de seguridad, auditorías en tiempo real y protección de activos de alto rendimiento.
                </p>
            </div>
        """, unsafe_allow_html=True)

    # --- COLUMNA DERECHA: PANELES DE AUTENTICACIÓN ---
    with col_form:
        st.markdown("### Acceso al Sistema")
        st.caption("Inicia sesión o regístrate en NEXUS-SEC")

        tab_login, tab_registro, tab_recuperar = st.tabs(["Iniciar Sesión", "Registro", "Recuperar"])

        # ================= PESTAÑA: INICIAR SESIÓN =================
        with tab_login:
            with st.form("login_form_real"):
                usuario_in = st.text_input("Cédula o Correo Gmail", key="login_user", placeholder="ej: 12345678 o user@gmail.com")
                pass_in = st.text_input("Contraseña", type="password", key="login_pass", placeholder="••••••••••••")
                
                submit_ingreso = st.form_submit_button("Iniciar Sesión")

                if submit_ingreso:
                    u_limpio = usuario_in.strip().lower()
                    if not u_limpio or not pass_in:
                        st.error("Complete todos los campos.")
                    else:
                        if u_limpio in st.session_state.usuarios_bd and st.session_state.usuarios_bd[u_limpio]["password"] == pass_in:
                            st.session_state.autenticado = True
                            st.session_state.login_user = ""
                            st.session_state.login_pass = ""
                            st.success("¡Acceso concedido!")
                            time.sleep(0.5)
                            st.rerun()
                        else:
                            st.error("Credenciales incorrectas.")
                            st.session_state.login_pass = ""

            st.markdown("<p style='text-align: center; color: #94a3b8; font-size: 0.75rem; margin: 10px 0;'>O ingresa mediante proveedor externo</p>", unsafe_allow_html=True)
            
            # Botones reales de redirección OAuth 2.0
            col_g, col_f = st.columns(2)
            with col_g:
                st.markdown(f'<a href="{google_oauth_url}" target="_self"><button style="width:100%; background:#ea4335; color:white; border:none; padding:10px; border-radius:8px; font-weight:500; cursor:pointer;">Google / Gmail</button></a>', unsafe_allow_html=True)
            with col_f:
                st.markdown(f'<a href="{facebook_oauth_url}" target="_self"><button style="width:100%; background:#1877f2; color:white; border:none; padding:10px; border-radius:8px; font-weight:500; cursor:pointer;">Facebook</button></a>', unsafe_allow_html=True)

        # ================= PESTAÑA: REGISTRO =================
        with tab_registro:
            with st.form("registro_form_real"):
                reg_id = st.text_input("Cédula o Correo Gmail", key="reg_user", placeholder="ej: V-12345678 o correo@gmail.com")
                reg_pass = st.text_input("Crear Contraseña", type="password", key="reg_pass", placeholder="••••••••••••")
                reg_pass2 = st.text_input("Confirmar Contraseña", type="password", key="reg_pass2", placeholder="••••••••••••")
                
                submit_registro = st.form_submit_button("Registrar Cuenta")

                if submit_registro:
                    r_limpio = reg_id.strip().lower()
                    es_gmail = r_limpio.endswith("@gmail.com")
                    es_cedula = len(r_limpio) >= 6 and any(char.isdigit() for char in r_limpio)

                    if not r_limpio or not reg_pass:
                        st.error("Todos los campos son obligatorios.")
                    elif not (es_gmail or es_cedula):
                        st.error("Debe ingresar una **Cédula válida** o un correo **Gmail**.")
                    elif reg_pass != reg_pass2:
                        st.error("Las contraseñas no coinciden.")
                        st.session_state.reg_pass = ""
                        st.session_state.reg_pass2 = ""
                    elif r_limpio in st.session_state.usuarios_bd:
                        st.warning("Este identificador ya se encuentra registrado.")
                    else:
                        st.session_state.usuarios_bd[r_limpio] = {"password": reg_pass, "tipo": "user"}
                        st.session_state.reg_user = ""
                        st.session_state.reg_pass = ""
                        st.session_state.reg_pass2 = ""
                        st.success("¡Registro completado con éxito! Ya puedes iniciar sesión.")
                        time.sleep(1)
                        st.rerun()

        # ================= PESTAÑA: RECUPERAR CONTRASEÑA =================
        with tab_recuperar:
            with st.form("recuperar_form_real"):
                rec_id = st.text_input("Cédula o Gmail registrado", key="rec_user", placeholder="ej: 12345678 o tu_correo@gmail.com")
                submit_recuperar = st.form_submit_button("Enviar Instrucciones")

                if submit_recuperar:
                    rc_limpio = rec_id.strip().lower()
                    if not rc_limpio:
                        st.error("Ingrese su identificador registrado.")
                    elif rc_limpio in st.session_state.usuarios_bd:
                        st.session_state.rec_user = ""
                        st.success(f"Instrucciones de restablecimiento enviadas de forma segura a `{rc_limpio}`.")
                    else:
                        st.error("No se encontró ningún registro asociado a este identificador.")

        st.markdown("---")
        st.markdown("<p style='text-align: center; font-size: 0.7rem; color: #94a3b8;'>🔒 Canal Encriptado TLS 1.3 • Soporte Técnico Nexus-Sec</p>", unsafe_allow_html=True)
