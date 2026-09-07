import streamlit as st
import time
import re

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="Nexus-Sec | Portal de Acceso Seguro",
    page_icon="🛡️",
    layout="centered"
)

# --- ESTILOS AVANZADOS (GLASSMORPHISM & CSS) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    :root {
        --bg-deep: #050b14;
        --glass-bg: rgba(15, 23, 42, 0.75);
        --glass-border: rgba(56, 189, 248, 0.15);
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

    .nexus-card {
        background: var(--glass-bg);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid var(--glass-border);
        border-radius: 20px;
        padding: 35px;
        box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.7),
                    0 0 30px var(--accent-glow);
        margin-top: 1rem;
    }

    .nexus-title {
        text-align: center;
        font-size: 1.8rem;
        font-weight: 700;
        color: var(--text-main);
        margin-bottom: 5px;
    }

    .nexus-title span {
        color: var(--accent-cyan);
        text-shadow: 0 0 10px var(--accent-glow);
    }

    .nexus-subtitle {
        text-align: center;
        font-size: 0.85rem;
        color: var(--text-muted);
        margin-bottom: 25px;
    }

    .stTextInput input {
        background-color: rgba(30, 41, 59, 0.5) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        color: var(--text-main) !important;
        border-radius: 10px !important;
    }
    
    .stTextInput input:focus {
        border-color: var(--accent-cyan) !important;
        box-shadow: 0 0 0 3px var(--accent-glow) !important;
    }

    .stButton button {
        width: 100%;
        background: linear-gradient(135deg, #0891b2, #06b6d4) !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 12px !important;
        font-weight: 600 !important;
        box-shadow: 0 4px 12px rgba(6, 182, 212, 0.3) !important;
        transition: all 0.3s ease !important;
    }

    .stButton button:hover {
        transform: translateY(-1px);
        box-shadow: 0 6px 20px rgba(6, 182, 212, 0.5) !important;
        background: linear-gradient(135deg, #06b6d4, #22d3ee) !important;
    }

    .security-footer {
        text-align: center;
        font-size: 0.75rem;
        color: var(--text-muted);
        margin-top: 25px;
        border-top: 1px solid rgba(255, 255, 255, 0.05);
        padding-top: 15px;
    }
</style>
""", unsafe_allow_html=True)

# --- INICIALIZACIÓN DE ESTADO ---
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False
if "modo" not in st.session_state:
    st.session_state.modo = "login"  # login, registro, recuperar
if "usuarios_bd" not in st.session_state:
    # Base de datos simulada en memoria (Cédula/Gmail -> Password)
    st.session_state.usuarios_bd = {
        "admin": {"password": "nexus2026", "tipo": "user"}
    }

# --- FLUJO PRINCIPAL ---
if st.session_state.autenticado:
    st.markdown("""
        <div class="nexus-card">
            <h2 class="nexus-title">NEXUS<span>-SEC</span> PANEL</h2>
            <p class="nexus-subtitle">Sesión Segura Activa - Nivel de Autorización: Operativo</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.success("✨ ¡Bienvenido al núcleo de operaciones seguro!")
    if st.button("Cerrar Sesión de Forma Segura"):
        st.session_state.autenticado = False
        st.rerun()

else:
    st.markdown("""
        <div class="nexus-card">
            <div class="nexus-title">NEXUS<span>-SEC</span></div>
            <div class="nexus-subtitle">Portal de Gestión de Identidad y Acceso</div>
    """, unsafe_allow_html=True)

    # Selector visual de modo mediante columnas de botones limpios
    col_m1, col_m2, col_m3 = st.columns(3)
    with col_m1:
        if st.button("🔑 Iniciar"):
            st.session_state.modo = "login"
            st.rerun()
    with col_m2:
        if st.button("📝 Registro"):
            st.session_state.modo = "registro"
            st.rerun()
    with col_m3:
        if st.button("🔄 Recuperar"):
            st.session_state.modo = "recuperar"
            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    # ================= MODO: LOGIN =================
    if st.session_state.modo == "login":
        st.markdown("#### Acceso al Sistema")
        with st.form("login_form"):
            id_ingreso = st.text_input("Cédula o Correo Gmail", placeholder="ej: 12345678 o usuario@gmail.com")
            password = st.text_input("Clave de Acceso", type="password", placeholder="••••••••••••")
            submit_login = st.form_submit_button("Verificar e Ingresar")

            if submit_login:
                id_limpio = id_ingreso.strip().lower()
                if not id_limpio or not password:
                    st.error("Por favor complete todos los campos.")
                else:
                    if id_limpio in st.session_state.usuarios_bd and st.session_state.usuarios_bd[id_limpio]["password"] == password:
                        st.session_state.autenticado = True
                        st.success("¡Autenticación concedida!")
                        time.sleep(0.6)
                        st.rerun()
                    else:
                        st.error("Credenciales inválidas o usuario no registrado.")

    # ================= MODO: REGISTRO =================
    elif st.session_state.modo == "registro":
        st.markdown("#### Registro con Cédula o Gmail")
        with st.form("registro_form"):
            nuevo_id = st.text_input("Ingrese su Cédula o Correo Gmail", placeholder="ej: V-12345678 o correo@gmail.com")
            nuevo_pass = st.text_input("Crear Clave de Acceso", type="password", placeholder="••••••••••••")
            confirm_pass = st.text_input("Confirmar Clave de Acceso", type="password", placeholder="••••••••••••")
            
            submit_reg = st.form_submit_button("Registrarse en el Sistema")

            if submit_reg:
                id_limpio = nuevo_id.strip().lower()
                
                # Validación estricta para asegurar que sea Cédula (números/letras de documento) o formato Gmail válido
                es_gmail = id_limpio.endswith("@gmail.com")
                es_cedula = len(id_limpio) >= 6 and any(char.isdigit() for char in id_limpio)

                if not id_limpio or not nuevo_pass:
                    st.error("Debe rellenar todos los campos obligatorios.")
                elif not (es_gmail or es_cedula):
                    st.error("Por favor ingrese una **Cédula válida** o una cuenta de **Gmail** corporativa/personal.")
                elif nuevo_pass != confirm_pass:
                    st.error("Las claves de acceso no coinciden.")
                elif id_limpio in st.session_state.usuarios_bd:
                    st.warning("Este identificador (Cédula/Gmail) ya se encuentra registrado.")
                else:
                    st.session_state.usuarios_bd[id_limpio] = {"password": nuevo_pass, "tipo": "user"}
                    st.success("¡Registro exitoso! Ya puede iniciar sesión con sus credenciales.")
                    time.sleep(1)
                    st.session_state.modo = "login"
                    st.rerun()

    # ================= MODO: RECUPERAR ACCESO =================
    elif st.session_state.modo == "recuperar":
        st.markdown("#### Recuperación de Credenciales")
        with st.form("recuperar_form"):
            recuperar_id = st.text_input("Su Cédula o Correo Gmail registrado", placeholder="ej: 12345678 o correo@gmail.com")
            submit_rec = st.form_submit_button("Enviar Instrucciones de Recuperación")

            if submit_rec:
                rec_limpio = recuperar_id.strip().lower()
                if not rec_limpio:
                    st.error("Ingrese el identificador para buscar en la base de datos.")
                elif rec_limpio in st.session_state.usuarios_bd:
                    # Simulación de envío de enlace o restablecimiento seguro
                    st.success(f"Se han enviado los pasos de recuperación al registro asociado a: `{rec_limpio}`.")
                else:
                    st.error("El identificador proporcionado no registra actividad en el sistema.")

    st.markdown("""
            <div class="security-footer">
                🔒 Canal Encriptado TLS 1.3 • Identidad Verificada por Cédula o Gmail
            </div>
        </div>
    """, unsafe_allow_html=True)
