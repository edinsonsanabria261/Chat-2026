import streamlit as st
import time

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="Nexus-Sec | Portal Ejecutivo de Autenticación",
    page_icon="🛡️",
    layout="centered"
)

# --- ESTILOS CSS AVANZADOS (DISEÑO SPLIT MODAL DOS COLUMNAS) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    :root {
        --bg-deep: #050b14;
        --modal-bg: #0b1329;
        --left-banner-bg: #dc2626; /* Tono rojo llamativo corporativo/gaming */
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

    /* Contenedor principal tipo Modal Ejecutivo */
    .nexus-modal-container {
        display: flex;
        flex-direction: row;
        background: var(--modal-bg);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        overflow: hidden;
        box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.8),
                    0 0 35px rgba(220, 38, 38, 0.15);
        margin-top: 2rem;
    }

    /* Ocultar elementos nativos de separadores en columnas */
    [data-testid="column"] {
        padding: 0px !important;
    }

    /* Estilo de los botones de OAuth (Google / Facebook) */
    .stButton button {
        width: 100%;
        border-radius: 8px !important;
        font-weight: 500 !important;
        font-size: 0.9rem !important;
        padding: 10px !important;
        transition: all 0.3s ease !important;
    }

    /* Estilización general de campos de texto */
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

    /* Pestañas internas */
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

# --- INICIALIZACIÓN DE ESTADO ---
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False
if "usuarios_bd" not in st.session_state:
    st.session_state.usuarios_bd = {
        "admin": {"password": "nexus2026", "tipo": "user"}
    }

# --- FLUJO PRINCIPAL ---
if st.session_state.autenticado:
    st.markdown("""
        <div style="background: #0b1329; border: 1px solid rgba(255,255,255,0.08); border-radius: 16px; padding: 40px; text-align: center; margin-top: 3rem;">
            <h2 style="color: #f8fafc; font-weight: 700;">NEXUS<span style="color: #ef4444;">-SEC</span> PANEL</h2>
            <p style="color: #94a3b8; font-size: 0.9rem;">Sesión Segura Activa - Nivel de Autorización: Operativo</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.success("✨ ¡Bienvenido al núcleo de operaciones seguro!")
    if st.button("Cerrar Sesión de Forma Segura"):
        st.session_state.autenticado = False
        st.rerun()

else:
    # Contenedor Split en 2 Columnas (Estilo Modal de Referencia)
    col_banner, col_form = st.columns([1, 1.2], gap="small")

    # --- COLUMNA IZQUIERDA: BANNER VISUAL E IMAGEN ---
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
                        Obtén análisis avanzados de seguridad, auditorías en tiempo real y protección de activos de alto rendimiento.
                    </p>
                </div>
                
                <div style="margin-top: 30px; text-align: center;">
                    <!-- Imagen ilustrativa integrada con enlace estable -->
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

        # Pestañas fluidas idénticas al modelo de referencia
        tab_login, tab_registro, tab_recuperar = st.tabs(["Iniciar Sesión", "Registro", "Recuperar"])

        # ================= PESTAÑA: INICIAR SESIÓN =================
        with tab_login:
            with st.form("login_modal_form"):
                usuario_in = st.text_input("Cédula o Correo Gmail", placeholder="ej: 12345678 o user@gmail.com")
                pass_in = st.text_input("Contraseña", type="password", placeholder="••••••••••••")
                
                submit_ingreso = st.form_submit_button("Iniciar Sesión")

                if submit_ingreso:
                    u_limpio = usuario_in.strip().lower()
                    if not u_limpio or not pass_in:
                        st.error("Complete todos los campos.")
                    else:
                        if u_limpio in st.session_state.usuarios_bd and st.session_state.usuarios_bd[u_limpio]["password"] == pass_in:
                            st.session_state.autenticado = True
                            st.success("¡Acceso concedido!")
                            time.sleep(0.5)
                            st.rerun()
                        else:
                            st.error("Credenciales incorrectas.")

            st.markdown("<p style='text-align: center; color: #94a3b8; font-size: 0.75rem; margin: 10px 0;'>O ingresa con una cuenta externa</p>", unsafe_allow_html=True)
            
            # Botones de inicio de sesión rápido (Gmail / Facebook)
            col_g, col_f = st.columns(2)
            with col_g:
                if st.button("🔵 Google / Gmail"):
                    st.info("Simulando autenticación segura mediante OAuth Google...")
            with col_f:
                if st.button("🔵 Facebook"):
                    st.info("Simulando autenticación segura mediante OAuth Facebook...")

        # ================= PESTAÑA: REGISTRO =================
        with tab_registro:
            with st.form("registro_modal_form"):
                reg_id = st.text_input("Cédula o Correo Gmail", placeholder="ej: V-12345678 o correo@gmail.com")
                reg_pass = st.text_input("Crear Contraseña", type="password", placeholder="••••••••••••")
                reg_pass2 = st.text_input("Confirmar Contraseña", type="password", placeholder="••••••••••••")
                
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
                    elif r_limpio in st.session_state.usuarios_bd:
                        st.warning("Este identificador ya se encuentra registrado.")
                    else:
                        st.session_state.usuarios_bd[r_limpio] = {"password": reg_pass, "tipo": "user"}
                        st.success("¡Registro completado con éxito! Ya puedes iniciar sesión.")
                        time.sleep(1)
                        st.rerun()

        # ================= PESTAÑA: RECUPERAR CONTRASEÑA =================
        with tab_recuperar:
            with st.form("recuperar_modal_form"):
                rec_id = st.text_input("Cédula o Gmail para recuperación", placeholder="ej: 12345678 o tu_correo@gmail.com")
                submit_recuperar = st.form_submit_button("Verificar e Instrucciones")

                if submit_recuperar:
                    rc_limpio = rec_id.strip().lower()
                    if not rc_limpio:
                        st.error("Ingrese su identificador registrado.")
                    elif rc_limpio in st.session_state.usuarios_bd:
                        st.success(f"Instrucciones de restablecimiento enviadas a `{rc_limpio}`.")
                    else:
                        st.error("No se encontró ningún registro asociado a este identificador.")

        st.markdown("""
                <div style="text-align: center; margin-top: 20px; font-size: 0.7rem; color: #94a3b8; border-top: 1px solid rgba(255,255,255,0.05); pt: 10px;">
                    🔒 Canal Encriptado TLS 1.3 • Soporte Técnico Nexus-Sec
                </div>
            </div>
        """, unsafe_allow_html=True)
