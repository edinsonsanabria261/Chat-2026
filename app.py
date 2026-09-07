import streamlit as st
import time
import base64
import hashlib
import hmac

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

    /* Ocultar elementos predeterminados de Streamlit para un look corporativo limpio */
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

    /* Contenedor tipo Glassmorphism */
    .nexus-card {
        background: var(--glass-bg);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid var(--glass-border);
        border-radius: 20px;
        padding: 40px;
        box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.7),
                    0 0 30px var(--accent-glow);
        margin-top: 2rem;
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
        margin-bottom: 30px;
    }

    /* Personalización de inputs de Streamlit */
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

    /* Botón de acción principal */
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

# --- INICIALIZACIÓN DE ESTADO DE SESIÓN ---
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False
if "intentos_fallidos" not in st.session_state:
    st.session_state.intentos_fallidos = 0
if "bloqueo_hasta" not in st.session_state:
    st.session_state.bloqueo_hasta = 0

# --- LÓGICA DE CONTROL DE ACCESO ---
if st.session_state.autenticado:
    # --- PANEL PROTEGIDO (POST-LOGIN) ---
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
    # --- FORMULARIO DE ACCESO (LOGIN) ---
    st.markdown("""
        <div class="nexus-card">
            <div class="nexus-title">NEXUS<span>-SEC</span></div>
            <div class="nexus-subtitle">Sistema de Autenticación de Alta Seguridad</div>
    """, unsafe_allow_html=True)

    with st.form("login_form"):
        usuario = st.text_input("Identificador / Usuario", placeholder="usuario@nexus.sec")
        password = st.text_input("Clave de Acceso", type="password", placeholder="••••••••••••")
        
        submit = st.form_submit_button("Verificar e Ingresar")

        if submit:
            tiempo_actual = time.time()
            
            # Verificación de Bloqueo por Fuerza Bruta (Rate Limiting)
            if tiempo_actual < st.session_state.bloqueo_hasta:
                segundos_restantes = int(st.session_state.bloqueo_hasta - tiempo_actual)
                st.error(f"⚠️ Prevención anti-fuerza bruta activa. Intente de nuevo en {segundos_restantes} segundos.")
            else:
                # Sanitización básica y validación simulada
                usuario_limpio = usuario.strip()
                
                if not usuario_limpio or not password:
                    st.error("Por favor complete todas las credenciales de acceso.")
                else:
                    # Simulación de validación (Credenciales de ejemplo: admin / nexus2026)
                    # En producción puedes conectar esto a una base de datos segura o hashing de contraseñas (bcrypt)
                    if usuario_limpio == "admin" and password == "nexus2026":
                        st.session_state.autenticado = True
                        st.session_state.intentos_fallidos = 0
                        st.success("¡Autenticación concedida! Abriendo canal...")
                        time.sleep(0.8)
                        st.rerun()
                    else:
                        st.session_state.intentos_fallidos += 1
                        if st.session_state.intentos_fallidos >= 3:
                            st.session_state.bloqueo_hasta = time.time() + 15 # Bloqueo de 15 segundos
                            st.error("Demasiados intentos fallidos. Sistema bloqueado por seguridad (15s).")
                        else:
                            st.error(f"Credenciales inválidas. Intentos restantes: {3 - st.session_state.intentos_fallidos}")

    st.markdown("""
            <div class="security-footer">
                🔒 Canal Encriptado TLS 1.3 • Protección Activa Anti-BruteForce
            </div>
        </div>
    """, unsafe_allow_html=True)
