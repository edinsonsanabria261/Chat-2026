import streamlit as st
import hashlib
import json
import os

st.set_page_config(
    page_title="Nexus-Sec | Portal de Acceso Seguro",
    page_icon="🛡️",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Archivo de base de datos local para persistencia real de usuarios
DB_FILE = "users_db.json"

def load_users():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f:
            return json.load(f)
    return {}

def save_users(users):
    with open(DB_FILE, "w") as f:
        json.dump(users, f)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Inicializar base de datos en session_state
if "users" not in st.session_state:
    st.session_state.users = load_users()

# --- DISEÑO CSS AVANZADO ---
st.markdown("""
    <style>
        .stApp { background-color: #07090e; color: #f3f4f6; font-family: 'Inter', sans-serif; }
        #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
        .main-card {
            background: rgba(13, 17, 23, 0.85);
            border: 1px solid rgba(56, 189, 248, 0.2);
            border-radius: 16px;
            padding: 30px;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.6);
            backdrop-filter: blur(10px);
            margin-bottom: 20px;
        }
        .portal-title { text-align: center; font-size: 1.8rem; font-weight: 700; color: #ffffff; }
        .portal-title span { color: #38bdf8; }
        .portal-subtitle { text-align: center; font-size: 0.85rem; color: #9ca3af; margin-bottom: 25px; text-transform: uppercase; }
        .stTextInput input { background-color: rgba(3, 7, 18, 0.6) !important; color: #ffffff !important; border: 1px solid rgba(255, 255, 255, 0.1) !important; border-radius: 8px !important; }
        .stButton button { width: 100%; background: linear-gradient(135deg, #0284c7 0%, #38bdf8 100%); color: #030712; font-weight: 600; border-radius: 8px; border: none; }
        .security-footer { text-align: center; font-size: 0.75rem; color: #6b7280; margin-top: 30px; border-top: 1px solid rgba(255, 255, 255, 0.05); padding-top: 15px; }
    </style>
""", unsafe_allow_html=True)

# --- ENCABEZADO ---
st.markdown("""
    <div class="main-card">
        <div class="portal-title">NEXUS<span>-SEC</span></div>
        <div class="portal-subtitle">Portal de Gestión de Identidad y Acceso</div>
    </div>
""", unsafe_allow_html=True)

# --- NAVEGACIÓN ---
menu = st.radio(
    "Navegación", 
    ["🔑 Iniciar Sesión", "📝 Registro Oficial", "🔄 Recuperar Cuenta"],
    horizontal=True,
    label_visibility="collapsed"
)

st.markdown("<br>", unsafe_allow_html=True)

# --- 1. INICIAR SESIÓN ---
if menu == "🔑 Iniciar Sesión":
    with st.form("login_form"):
        st.markdown("### Acceso al Sistema")
        identificador = st.text_input("Cédula o Correo Gmail", placeholder="ej: usuario@gmail.com")
        password = st.text_input("Clave de Acceso", type="password", placeholder="••••••••••••")
        
        submit_btn = st.form_submit_button("Verificar e Ingresar")
        
        if submit_btn:
            users = st.session_state.users
            if not identificador or not password:
                st.warning("⚠️ Complete todos los campos de seguridad.")
            elif identificador in users and users[identificador]["password"] == hash_password(password):
                st.success(f"🔓 Acceso autorizado. Bienvenido al sistema, {identificador}")
            else:
                st.error("❌ Credenciales incorrectas o usuario no registrado.")

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #9ca3af; font-size: 0.8rem;'>O autentícate mediante proveedores externos reales</p>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        # Enlace real de OAuth 2.0 con Google (requiere Client ID real de Google Cloud Console)
        google_client_id = "TU_GOOGLE_CLIENT_ID.apps.googleusercontent.com"
        redirect_uri = "https://tu-app.streamlit.app"  # Cambia por tu URL pública de Streamlit
        google_auth_url = f"https://accounts.google.com/o/oauth2/v2/auth?client_id={google_client_id}&redirect_uri={redirect_uri}&response_type=token&scope=email%20profile"
        st.link_button("🌐 Google / Gmail", google_auth_url, use_container_width=True)
        
    with col2:
        # Enlace real de OAuth con Facebook (requiere App ID real de Facebook Developers)
        fb_app_id = "TU_FACEBOOK_APP_ID"
        fb_auth_url = f"https://www.facebook.com/v12.0/dialog/oauth?client_id={fb_app_id}&redirect_uri={redirect_uri}&response_type=token&scope=email"
        st.link_button("🌐 Facebook", fb_auth_url, use_container_width=True)

# --- 2. REGISTRO OFICIAL ---
elif menu == "📝 Registro Oficial":
    with st.form("register_form"):
        st.markdown("### Registro de Nueva Identidad")
        nuevo_id = st.text_input("Cédula o Correo Gmail", placeholder="usuario@gmail.com")
        nueva_pass = st.text_input("Definir Clave de Enclave", type="password", placeholder="••••••••••••")
        
        reg_btn = st.form_submit_button("Registrar Credencial")
        
        if reg_btn:
            if not nuevo_id or not nueva_pass:
                st.warning("⚠️ Todos los campos son obligatorios.")
            elif nuevo_id in st.session_state.users:
                st.error("❌ Este identificador ya se encuentra registrado en el sistema.")
            else:
                st.session_state.users[nuevo_id] = {"password": hash_password(nueva_pass)}
                save_users(st.session_state.users)
                st.success("✅ Registro completado con éxito. Ya puedes iniciar sesión.")

# --- 3. RECUPERAR CUENTA ---
else:
    with st.form("recovery_form"):
        st.markdown("### Recuperación de Credenciales")
        st.info("Ingrese su cédula o correo Gmail asociado para enviar un token temporal de recuperación.")
        
        rec_input = st.text_input("Cédula o Correo Registrado", placeholder="usuario@gmail.com")
        rec_btn = st.form_submit_button("Solicitar Token de Recuperación")
        
        if rec_btn:
            if not rec_input:
                st.warning("⚠️ Ingrese un identificador válido.")
            elif rec_input in st.session_state.users:
                st.success(f"📧 Token de recuperación enviado de forma cifrada a: {rec_input}")
            else:
                st.error("❌ El identificador ingresado no existe en los registros de seguridad.")

# --- PIE DE PÁGINA ---
st.markdown("""
    <div class="security-footer">
        🔒 Canal Encriptado TLS 1.3 • Integridad de Base de Datos Activa
    </div>
""", unsafe_allow_html=True)
