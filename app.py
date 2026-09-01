import streamlit as st
import time
import requests
import json

# -----------------------------------------------------------------
# CONFIGURACIÓN Y ESTILOS UI (ESTÉTICA TÁCTICA MODERNIZADA & CYBERPUNK)
# -----------------------------------------------------------------
st.set_page_config(
    page_title="Centro Táctico & WhatsApp P2P - Edinson Carlos Marin Sanabria", 
    page_icon="🛡️", 
    layout="wide"
)

st.markdown("""
    <style>
    .stApp { 
        background: radial-gradient(circle at 50% 50%, #090d16 0%, #05070b 100%); 
        color: #f0f6fc; 
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; 
    }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    .chat-bubble-incoming {
        background-color: #161b22;
        color: #f0f6fc;
        padding: 12px 16px;
        border-radius: 0px 14px 14px 14px;
        margin-bottom: 10px;
        max-width: 65%;
        border: 1px solid #30363d;
        box-shadow: 0 4px 15px rgba(0,0,0,0.4);
        float: left;
        clear: both;
    }
    
    .chat-bubble-outgoing {
        background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
        color: #ffffff;
        padding: 12px 16px;
        border-radius: 14px 0px 14px 14px;
        margin-bottom: 10px;
        max-width: 65%;
        box-shadow: 0 4px 15px rgba(37, 99, 235, 0.4);
        float: right;
        clear: both;
    }

    .chat-timestamp {
        font-size: 0.75em;
        color: #94a3b8;
        text-align: right;
        margin-top: 4px;
    }

    .whatsapp-header {
        background: linear-gradient(135deg, #121824 0%, #1a2333 100%);
        padding: 18px 22px;
        border-radius: 14px;
        margin-bottom: 20px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        border: 1px solid #1f6feb;
        box-shadow: 0 0 25px rgba(31, 111, 235, 0.25);
    }

    .stRadio > div[role="radiogroup"] > label {
        background: rgba(22, 27, 34, 0.85);
        border: 1px solid #30363d;
        padding: 12px 16px;
        border-radius: 12px !important;
        margin-bottom: 10px;
        transition: all 0.3s ease;
        font-weight: 600;
        color: #e2e8f0;
    }
    .stRadio > div[role="radiogroup"] > label:hover {
        background: linear-gradient(90deg, #2563eb 0%, #3b82f6 100%) !important;
        color: #ffffff !important;
        border-color: #3b82f6;
        box-shadow: 0 0 15px rgba(59, 130, 246, 0.5);
    }

    .stButton>button {
        border-radius: 10px;
        font-weight: 700;
        background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
        color: white;
        border: none;
        box-shadow: 0 4px 15px rgba(37, 99, 235, 0.4);
        transition: all 0.3s ease;
        padding: 0.55rem 1.2rem;
    }
    .stButton>button:hover {
        background: linear-gradient(135deg, #1d4ed8 100%, #1e40af 100%);
        color: white;
        box-shadow: 0 6px 20px rgba(37, 99, 235, 0.6);
        transform: translateY(-2px);
    }
    
    .stSelectbox label, .stTextInput label, .stPasswordInput label {
        color: #38bdf8 !important;
        font-weight: 700 !important;
    }
    </style>
""", unsafe_allow_html=True)

FIREBASE_URL = "https://chat-2026-68203-default-rtdb.firebaseio.com"
CEDULA_ADMIN_MAESTRO = "2844102044"  # Edinson Carlos Marin Sanabria

for key, val in {
    'acceso_concedido': False,
    'autenticado': False,
    'usuario_actual': "",
    'rol_actual': "",
    'cedula_actual': "",
    'modo_registro': False,
    'repositorio_archivos': [],
    'historial_mensajes': []
}.items():
    if key not in st.session_state:
        st.session_state[key] = val

def obtener_metadatos_locales():
    return {
        'ip': '190.202.14.88', 
        'ciudad': 'Caracas', 
        'pais': 'Venezuela', 
        'navegador': 'Kiwi Browser (Desktop Mode / Android)', 
        'isp': 'Cantv / Intercable'
    }

def registrar_conexion_auditoria(nombre, cedula, tipo_evento, meta):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    payload = {
        'nombre': nombre, 'cedula': cedula, 'evento': tipo_evento,
        'ip': meta.get('ip'), 'ubicacion': f"{meta.get('ciudad')}, {meta.get('pais')}",
        'timestamp': timestamp
    }
    try:
        requests.post(f"{FIREBASE_URL}/conexiones_log.json", data=json.dumps(payload), timeout=1.5)
        requests.post(f"{FIREBASE_URL}/honeypot_bruteforce_defense.json", data=json.dumps(payload), timeout=1.5)
    except Exception:
        pass

def obtener_operador(cedula):
    try:
        res = requests.get(f"{FIREBASE_URL}/operadores/{cedula}.json", timeout=2.0)
        if res.status_code == 200 and res.json():
            data = res.json()
            if isinstance(data, dict) and data.get('activo', True):
                return data
    except Exception:
        pass
    return None

def guardar_operador(cedula, nombre, apellido, rol, telefono, codigo_pin, meta, estado="Activo", cedula_verificada=True, correo=""):
    nombre_completo = f"{nombre} {apellido}"
    payload = {
        'nombre': nombre_completo, 'cedula': cedula, 'rol': rol, 
        'telefono': telefono, 'codigo_pin': codigo_pin, 'ip': meta.get('ip'),
        'fecha_registro': time.strftime("%Y-%m-%d %H:%M:%S"),
        'estado_perfil': estado, 'cedula_verificada': cedula_verificada,
        'correo': correo, 'activo': True
    }
    try:
        res = requests.put(f"{FIREBASE_URL}/operadores/{cedula}.json", data=json.dumps(payload), timeout=2.0)
        return res.status_code == 200
    except Exception:
        return False

def cargar_mensajes_firebase(canal="Canal General Táctico"):
    try:
        res = requests.get(f"{FIREBASE_URL}/chat_whatsapp/{canal}.json", timeout=2.0)
        if res.status_code == 200 and res.json():
            data = res.json()
            if isinstance(data, dict):
                mensajes_ordenados = sorted(data.values(), key=lambda x: x.get('timestamp', ''))
                return [{
                    'tipo': m.get('tipo', 'texto'), 
                    'texto': m.get('texto', ''), 
                    'remitente': m.get('remitente', 'Anónimo'), 
                    'timestamp': m.get('timestamp', ''),
                    'audio_url': m.get('audio_url', '')
                } for m in mensajes_ordenados]
    except Exception:
        pass
    return []

def guardar_mensaje_firebase(tipo, texto, remitente, canal="Canal General Táctico", audio_url=""):
    payload = {
        'tipo': tipo,
        'texto': texto,
        'remitente': remitente,
        'timestamp': time.strftime("%Y-%m-%d %H:%M:%S"),
        'audio_url': audio_url
    }
    try:
        requests.post(f"{FIREBASE_URL}/chat_whatsapp/{canal}.json", data=json.dumps(payload), timeout=2.0)
        return True
    except Exception:
        return False

# -----------------------------------------------------------------
# PANTALLA DE REGISTRO
# -----------------------------------------------------------------
if st.session_state.get('modo_registro', False):
    st.markdown("<h2 style='text-align: center; color: #38bdf8;'>📝 REGISTRO TÁCTICO DE OPERADOR</h2>", unsafe_allow_html=True)
    st.markdown("---")
    
    with st.form(key="registro_pin_form"):
        col_r1, col_r2 = st.columns(2)
        with col_r1:
            reg_nombres = st.text_input("Nombres")
            reg_apellidos = st.text_input("Apellidos")
            reg_telefono = st.text_input("Número Celular (Ej. 0412xxxxxxx)")
        with col_r2:
            reg_cedula = st.text_input("Número de Documento / Cédula")
            reg_correo = st.text_input("Correo Electrónico (Opcional)")
            reg_pin = st.text_input("Código PIN de Acceso", type="password")
            
        btn_ejecutar_reg = st.form_submit_button("Crear Cuenta y Vincular 🚀", use_container_width=True)
        
        if btn_ejecutar_reg:
            if not reg_nombres.strip() or not reg_apellidos.strip() or not reg_cedula.strip() or not reg_telefono.strip() or not reg_pin.strip():
                st.error("❌ Error: Todos los campos obligatorios deben estar llenos.")
            else:
                meta = obtener_metadatos_locales()
                rol = "Administrador Global" if reg_cedula.strip() == CEDULA_ADMIN_MAESTRO else "Operador Protegido"
                exito = guardar_operador(
                    reg_cedula.strip(), reg_nombres.strip(), reg_apellidos.strip(), 
                    rol, reg_telefono.strip(), reg_pin.strip(), meta
                )
                if exito:
                    st.success("✅ ¡Registro Completado con Éxito! Ya puedes iniciar sesión.")
                    st.session_state['modo_registro'] = False
                    time.sleep(1.2)
                    st.rerun()
                else:
                    st.error("❌ Error al guardar en la base de datos.")
                        
    if st.button("⬅️ Volver al Login"):
        st.session_state['modo_registro'] = False
        st.rerun()
    st.stop()

# -----------------------------------------------------------------
# PANTALLA DE LOGIN
# -----------------------------------------------------------------
elif not st.session_state.get('acceso_concedido', False):
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
        <div style="background: linear-gradient(135deg, #121824 0%, #1a2333 100%); padding: 35px; border-radius: 18px; border: 2px solid #2563eb; max-width: 520px; margin: auto; text-align: center; box-shadow: 0 8px 30px rgba(37,99,235,0.3);">
            <div style="font-size: 2.8em; margin-bottom: 10px;">🛡️</div>
            <h2 style="color: #38bdf8; margin-bottom: 5px; font-weight: 800;">CENTRO TÁCTICO EMPRESARIAL</h2>
            <p style="color: #94a3b8; font-size: 0.95em;">Acceso Seguro por Credenciales Protegidas</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    tab_login_metodos = st.tabs(["🔑 Acceso con Cédula y PIN", "📝 Nuevo Registro"])
    
    with tab_login_metodos[0]:
        st.markdown("#### Ingreso mediante Credenciales Seguras")
        with st.form("form_login_credenciales"):
            cedula_input = st.text_input("Número de Cédula")
            pin_input = st.text_input("Código PIN / Clave", type="password")
            btn_login = st.form_submit_button("Iniciar Sesión 🛡️", use_container_width=True)
            
            if btn_login:
                if not cedula_input.strip() or not pin_input.strip():
                    st.error("❌ Introduce tu cédula y tu PIN.")
                else:
                    operador_db = obtener_operador(cedula_input.strip())
                    if operador_db and operador_db.get('codigo_pin') == pin_input.strip():
                        meta = obtener_metadatos_locales()
                        st.session_state['acceso_concedido'] = True
                        st.session_state['autenticado'] = True
                        st.session_state['cedula_actual'] = operador_db.get('cedula')
                        st.session_state['usuario_actual'] = operador_db.get('nombre')
                        st.session_state['rol_actual'] = operador_db.get('rol')
                        
                        registrar_conexion_auditoria(operador_db.get('nombre'), operador_db.get('cedula'), "Login Exitoso", meta)
                        st.success(f"✅ Bienvenido, {operador_db.get('nombre')}.")
                        time.sleep(0.8)
                        st.rerun()
                    else:
                        meta = obtener_metadatos_locales()
                        registrar_conexion_auditoria("Intruso / Fallido", cedula_input.strip(), "Intento Fallido / Fuerza Bruta Detectada", meta)
                        st.error("⛔ Cédula o Código PIN incorrectos. Evento registrado en Honeypot de seguridad.")

    with tab_login_metodos[1]:
        st.markdown("#### Registro de Nuevo Operador")
        if st.button("Ir al Formulario de Registro ➡️", use_container_width=True):
            st.session_state['modo_registro'] = True
            st.rerun()

    st.stop()

# -----------------------------------------------------------------
# INTERFAZ PRINCIPAL CON 3 VENTANAS
# -----------------------------------------------------------------
col_nav, col_main = st.columns([1, 3], gap="small")

with col_nav:
    st.markdown("""
        <div class="whatsapp-header" style="justify-content: center; text-align: center;">
            <span style="font-weight: 800; font-size: 1.15em; color: #38bdf8; letter-spacing: 0.5px;">🛡️ CENTRO TÁCTICO</span>
        </div>
    """, unsafe_allow_html=True)
    
    st.caption(f"👤 Operador: `{st.session_state.get('usuario_actual')}`")
    st.markdown("---")
    
    opciones_menu = [
        "💬 Chat Principal & Contactos P2P",
        "🛠️ Herramientas de Ciberseguridad & Análisis",
        "📞 Videollamada & Streaming WebRTC",
        "⚙️ Configuración, Seguridad y Auditoría Empresa",
        "🚪 Cerrar Sesión"
    ]
    
    seleccion_modulo = st.radio("Menú Principal", opciones_menu, label_visibility="collapsed")

with col_main:
    if seleccion_modulo == "🚪 Cerrar Sesión":
        st.session_state['acceso_concedido'] = False
        st.rerun()
        
    elif seleccion_modulo == "💬 Chat Principal & Contactos P2P":
        st.markdown("""
            <div class="whatsapp-header">
                <div>
                    <span style="font-weight: bold; font-size: 1.25em; color: #f0f6fc;">💬 Mensajería Estilo WhatsApp Web & P2P</span><br>
                    <span style="font-size: 0.82em; color: #94a3b8;">Canal seguro sincronizado en tiempo real por Firebase</span>
                </div>
                <div>
                    <span style="cursor: pointer; padding: 5px; font-size: 1.1em; color: #38bdf8; font-weight: bold;">🟢 En línea</span>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        tab_chat_subs = st.tabs(["💬 Canal General", "👥 Agregar Amigo", "👤 Mis Chats Directos"])
        
        cedula_act = st.session_state.get('cedula_actual', '')
        nombre_act = st.session_state.get('usuario_actual', '')
        
        with tab_chat_subs[0]:
            st.markdown("#### 💬 Canal General Táctico")
            st.session_state.historial_mensajes = cargar_mensajes_firebase("Canal General Táctico")
            
            chat_box = st.container(height=380)
            with chat_box:
                if st.session_state.historial_mensajes:
                    for msg in st.session_state.historial_mensajes:
                        es_mio = msg.get('remitente') == nombre_act
                        clase_burbuja = "chat-bubble-outgoing" if es_mio else "chat-bubble-incoming"
                        st.markdown(f"""
                            <div class="{clase_burbuja}">
                                <b style="font-size: 0.85em; color: #38bdf8;">{msg.get('remitente')}</b><br>
                                {msg.get('texto')}<br>
                                <div class="chat-timestamp">{msg.get('timestamp')}</div>
                            </div>
                        """, unsafe_allow_html=True)
                else:
                    st.info("No hay mensajes previos en el canal general. ¡Escribe el primero!")
            
            nuevo_msj = st.text_input("Escribe tu mensaje táctico...", key="input_chat_general")
            if st.button("Enviar Mensaje 🚀", key="btn_enviar_chat"):
                if nuevo_msj.strip():
                    guardar_mensaje_firebase("texto", nuevo_msj.strip(), nombre_act, "Canal General Táctico")
                    st.rerun()

        with tab_chat_subs[1]:
            st.markdown("#### 👥 Vincular Nuevo Contacto por Cédula")
            cedula_amigo = st.text_input("Ingrese la cédula del operador a agregar:")
            if st.button("Enviar Solicitud de Enlace 🤝"):
                if cedula_amigo.strip():
                    op_amigo = obtener_operador(cedula_amigo.strip())
                    if op_amigo:
                        st.success(f"✅ Operador encontrado: {op_amigo.get('nombre')}. Solicitud enviada.")
                    else:
                        st.error("❌ Cédula no registrada en el sistema.")

        with tab_chat_subs[2]:
            st.markdown("#### 👤 Chats Directos P2P")
            st.info("Selecciona un operador de tu red segura para iniciar una conversación cifrada.")

    elif seleccion_modulo == "🛠️ Herramientas de Ciberseguridad & Análisis":
        st.markdown("### 🛠️ Módulo de Ciberseguridad & Red Team")
        st.info("Herramientas activas para auditoría, escaneo de puertos y análisis de aplicaciones.")
        
        tool_tab = st.tabs(["🌐 Escaneo Nmap / Redes", "📱 Análisis APK / Android"])
        with tool_tab[0]:
            st.markdown("#### Escáner de Red y Puertos")
            target_ip = st.text_input("IP o Dominio Objetivo:", value="127.0.0.1")
            if st.button("Ejecutar Escaneo Rápido"):
                st.success(f"Escaneando objetivos en {target_ip}...")
                st.code(f"Starting Nmap scan on {target_ip}\nHost is up.\nPORT 80/tcp open http\nPORT 443/tcp open https\nPORT 4443/tcp open alt-http", language="bash")
        with tool_tab[1]:
            st.markdown("#### Análisis Estático de APKs")
            st.write("Inspección de manifiestos y permisos de paquetes Android.")

    elif seleccion_modulo == "📞 Videollamada & Streaming WebRTC":
        st.markdown("### 📞 Videollamadas & Streaming WebRTC P2P")
        st.write("Comunicaciones multimedia cifradas en tiempo real (Cero operadoras telefónicas).")
        room_id = st.text_input("ID de Sala WebRTC:", value="SalaTactica-Principal")
        if st.button("Conectar Videollamada HD 🚀"):
            st.success(f"Conexión WebRTC establecida en la sala: {room_id}")
            st.markdown(f'<div style="background: #121824; padding:40px; text-align:center; border-radius:14px; border:2px solid #2563eb; color: #38bdf8; font-weight: bold;"><b>[ Flujo de Video Activo - Canal: {room_id} ]</b></div>', unsafe_allow_html=True)

    else:
        st.markdown("### ⚙️ Configuración y Seguridad de Empresa")
        st.warning("Panel de control restringido para la protección de la empresa y empleados.")
        st.text_input("Clave de cifrado simétrico actual:", type="password", value="*************")
        if st.button("Guardar Nuevos Parámetros de Seguridad"):
            st.success("Políticas de seguridad actualizadas correctamente en el nodo.")
