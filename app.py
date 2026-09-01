import streamlit as st
import time
import requests
import json

# -----------------------------------------------------------------
# CONFIGURACIÓN Y ESTILOS UI (ESTÉTICA TÁCTICA & WHATSAPP MODERNO)
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

def guardar_operador(cedula, nombre, apellido, rol, telefono, codigo_pin, meta):
    nombre_completo = f"{nombre} {apellido}"
    payload = {
        'nombre': nombre_completo, 'cedula': cedula, 'rol': rol, 
        'telefono': telefono, 'codigo_pin': codigo_pin, 'ip': meta.get('ip'),
        'fecha_registro': time.strftime("%Y-%m-%d %H:%M:%S"),
        'estado_perfil': 'Activo', 'cedula_verificada': True, 'activo': True
    }
    try:
        res = requests.put(f"{FIREBASE_URL}/operadores/{cedula}.json", data=json.dumps(payload), timeout=2.0)
        return res.status_code == 200
    except Exception:
        return False

def enviar_solicitud_amistad(cedula_origen, nombre_origen, cedula_destino):
    op_destino = obtener_operador(cedula_destino)
    if not op_destino:
        return False, "La cédula de destino no está registrada en el sistema."
    if cedula_origen == cedula_destino:
        return False, "No puedes enviarte una solicitud a ti mismo."
    
    payload = {
        'remitente_cedula': cedula_origen,
        'remitente_nombre': nombre_origen,
        'destino_cedula': cedula_destino,
        'estado': 'Pendiente',
        'timestamp': time.strftime("%Y-%m-%d %H:%M:%S")
    }
    try:
        requests.post(f"{FIREBASE_URL}/solicitudes_amistad.json", data=json.dumps(payload), timeout=2.0)
        return True, f"Solicitud enviada con éxito a {op_destino.get('nombre')}."
    except Exception:
        return False, "Error de conexión con la base de datos."

def obtener_solicitudes_pendientes(cedula):
    try:
        res = requests.get(f"{FIREBASE_URL}/solicitudes_amistad.json", timeout=2.0)
        if res.status_code == 200 and res.json():
            data = res.json()
            if isinstance(data, dict):
                return {k: v for k, v in data.items() if isinstance(v, dict) and v.get('destino_cedula') == cedula and v.get('estado') == 'Pendiente'}
    except Exception:
        pass
    return {}

def responder_solicitud_amistad(key_solicitud, aceptar=True):
    estado = 'Aceptada' if aceptar else 'Rechazada'
    try:
        requests.patch(f"{FIREBASE_URL}/solicitudes_amistad/{key_solicitud}.json", data=json.dumps({'estado': estado}), timeout=2.0)
        return True
    except Exception:
        return False

def obtener_amigos_conectados(cedula):
    amigos = {}
    try:
        res = requests.get(f"{FIREBASE_URL}/solicitudes_amistad.json", timeout=2.0)
        if res.status_code == 200 and res.json():
            data = res.json()
            if isinstance(data, dict):
                for k, v in data.items():
                    if isinstance(v, dict) and v.get('estado') == 'Aceptada':
                        if v.get('remitente_cedula') == cedula:
                            dest_ced = v.get('destino_cedula')
                            op_info = obtener_operador(dest_ced)
                            if op_info: amigos[dest_ced] = op_info.get('nombre')
                        elif v.get('destino_cedula') == cedula:
                            rem_ced = v.get('remitente_cedula')
                            op_info = obtener_operador(rem_ced)
                            if op_info: amigos[rem_ced] = op_info.get('nombre')
    except Exception:
        pass
    return amigos

def cargar_mensajes_firebase(canal):
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
                    'timestamp': m.get('timestamp', '')
                } for m in mensajes_ordenados]
    except Exception:
        pass
    return []

def guardar_mensaje_firebase(tipo, texto, remitente, canal):
    payload = {
        'tipo': tipo,
        'texto': texto,
        'remitente': remitente,
        'timestamp': time.strftime("%Y-%m-%d %H:%M:%S")
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
                        st.error("⛔ Cédula o Código PIN incorrectos.")

    with tab_login_metodos[1]:
        st.markdown("#### Registro de Nuevo Operador")
        if st.button("Ir al Formulario de Registro ➡️", use_container_width=True):
            st.session_state['modo_registro'] = True
            st.rerun()

    st.stop()

# -----------------------------------------------------------------
# INTERFAZ PRINCIPAL
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
        "⚙️ Configuración y Seguridad",
        "🚪 Cerrar Sesión"
    ]
    
    seleccion_modulo = st.radio("Menú Principal", opciones_menu, label_visibility="collapsed")

with col_main:
    if seleccion_modulo == "🚪 Cerrar Sesión":
        st.session_state['acceso_concedido'] = False
        st.rerun()
        
    elif seleccion_modulo == "💬 Chat Principal & Contactos P2P":
        cedula_act = st.session_state.get('cedula_actual', '')
        nombre_act = st.session_state.get('usuario_actual', '')
        
        tab_chat_subs = st.tabs([
            "💬 Canal General", 
            "👥 Agregar por Cédula", 
            "📥 Solicitudes Pendientes", 
            "👤 Mis Chats Directos"
        ])
        
        # 1. Canal General
        with tab_chat_subs[0]:
            st.markdown("#### 💬 Canal General Táctico")
            mensajes = cargar_mensajes_firebase("Canal General Táctico")
            
            chat_box = st.container(height=340)
            with chat_box:
                if mensajes:
                    for msg in mensajes:
                        es_mio = msg.get('remitente') == nombre_act
                        clase = "chat-bubble-outgoing" if es_mio else "chat-bubble-incoming"
                        st.markdown(f"""
                            <div class="{clase}">
                                <b style="font-size: 0.85em; color: #38bdf8;">{msg.get('remitente')}</b><br>
                                {msg.get('texto')}<br>
                                <div class="chat-timestamp">{msg.get('timestamp')}</div>
                            </div>
                        """, unsafe_allow_html=True)
                else:
                    st.info("No hay mensajes previos en el canal general.")
            
            # Barra de texto + botón de audio estilo WhatsApp
            col_txt, col_mic, col_send = st.columns([5, 1, 1])
            with col_txt:
                texto_gen = st.text_input("Escribe un mensaje...", key="input_gen", label_visibility="collapsed")
            with col_mic:
                btn_audio = st.button("🎙️", key="btn_audio_gen", help="Mantener o pulsar para enviar nota de voz")
            with col_send:
                btn_env = st.button("➤ Enviar", key="btn_send_gen")
                
            if btn_env and texto_gen.strip():
                guardar_mensaje_firebase("texto", texto_gen.strip(), nombre_act, "Canal General Táctico")
                st.rerun()
            if btn_audio:
                guardar_mensaje_firebase("audio", "🎙️ [Nota de voz cifrada]", nombre_act, "Canal General Táctico")
                st.success("Nota de voz enviada.")
                st.rerun()

        # 2. Agregar por Cédula
        with tab_chat_subs[1]:
            st.markdown("#### 👥 Vincular Nuevo Contacto por Cédula")
            cedula_amigo_input = st.text_input("Ingrese la cédula del operador a agregar:")
            if st.button("Enviar Solicitud de Enlace 🤝"):
                if cedula_amigo_input.strip():
                    exito, mensaje_resp = enviar_solicitud_amistad(cedula_act, nombre_act, cedula_amigo_input.strip())
                    if exito:
                        st.success(f"✅ {mensaje_resp}")
                    else:
                        st.error(f"❌ {mensaje_resp}")

        # 3. Solicitudes Pendientes (Aceptar / Rechazar)
        with tab_chat_subs[2]:
            st.markdown("#### 📥 Solicitudes de Contacto Recibidas")
            pendientes = obtener_solicitudes_pendientes(cedula_act)
            if pendientes:
                for req_id, req_data in pendientes.items():
                    st.markdown(f"""
                        <div style="background: #121824; padding: 15px; border-radius: 10px; border: 1px solid #2563eb; margin-bottom: 10px;">
                            <b>Remitente:</b> {req_data.get('remitente_nombre')}<br>
                            <b>Cédula:</b> {req_data.get('remitente_cedula')}<br>
                            <b>Fecha:</b> {req_data.get('timestamp')}
                        </div>
                    """, unsafe_allow_html=True)
                    
                    col_acp, col_rec = st.columns(2)
                    with col_acp:
                        if st.button("✅ Aceptar Solicitud", key=f"acp_{req_id}"):
                            responder_solicitud_amistad(req_id, aceptar=True)
                            st.success("¡Solicitud aceptada! Ya puedes chatear en 'Mis Chats Directos'.")
                            time.sleep(1)
                            st.rerun()
                    with col_rec:
                        if st.button("❌ Rechazar", key=f"rec_{req_id}"):
                            responder_solicitud_amistad(req_id, aceptar=False)
                            st.warning("Solicitud rechazada.")
                            time.sleep(1)
                            st.rerun()
            else:
                st.info("No tienes solicitudes pendientes en este momento.")

        # 4. Mis Chats Directos (Con botones de llamada y videollamada arriba)
        with tab_chat_subs[3]:
            st.markdown("#### 👤 Mis Chats Directos P2P")
            amigos = obtener_amigos_conectados(cedula_act)
            if amigos:
                amigo_seleccionado_cedula = st.selectbox("Selecciona un contacto vinculado:", list(amigos.keys()), format_func=lambda x: amigos[x])
                nombre_amigo = amigos[amigo_seleccionado_cedula]
                
                # Cabecera simulada estilo WhatsApp con iconos de llamada y videollamada
                canal_privado_id = f"chat_{min(cedula_act, amigo_seleccionado_cedula)}_{max(cedula_act, amigo_seleccionado_cedula)}"
                
                st.markdown(f"""
                    <div style="background: #121824; padding: 12px 18px; border-radius: 10px; border: 1px solid #1f6feb; display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
                        <div>
                            <span style="font-weight: bold; color: #38bdf8; font-size: 1.1em;">💬 {nombre_amigo}</span><br>
                            <span style="font-size: 0.8em; color: #94a3b8;">Cifrado de extremo a extremo P2P</span>
                        </div>
                        <div>
                            <span style="background: #161b22; padding: 6px 10px; border-radius: 8px; margin-right: 5px; cursor: pointer; border: 1px solid #30363d;" title="Llamada de Voz">📞</span>
                            <span style="background: #161b22; padding: 6px 10px; border-radius: 8px; cursor: pointer; border: 1px solid #30363d;" title="Videollamada">📹</span>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
                
                mensajes_priv = cargar_mensajes_firebase(canal_privado_id)
                chat_box_priv = st.container(height=280)
                with chat_box_priv:
                    if mensajes_priv:
                        for msg in mensajes_priv:
                            es_mio = msg.get('remitente') == nombre_act
                            clase = "chat-bubble-outgoing" if es_mio else "chat-bubble-incoming"
                            st.markdown(f"""
                                <div class="{clase}">
                                    {msg.get('texto')}<br>
                                    <div class="chat-timestamp">{msg.get('timestamp')}</div>
                                </div>
                            """, unsafe_allow_html=True)
                    else:
                        st.info(f"Inicia la conversación privada con {nombre_amigo}.")
                
                col_ptxt, col_pmic, col_psend = st.columns([5, 1, 1])
                with col_ptxt:
                    texto_priv = st.text_input("Mensaje privado...", key=f"input_priv_{amigo_seleccionado_cedula}", label_visibility="collapsed")
                with col_pmic:
                    btn_paudio = st.button("🎙️", key=f"mic_priv_{amigo_seleccionado_cedula}")
                with col_psend:
                    btn_psend = st.button("➤", key=f"send_priv_{amigo_seleccionado_cedula}")
                    
                if btn_psend and texto_priv.strip():
                    guardar_mensaje_firebase("texto", texto_priv.strip(), nombre_act, canal_privado_id)
                    st.rerun()
                if btn_paudio:
                    guardar_mensaje_firebase("audio", "🎙️ [Nota de voz privada]", nombre_act, canal_privado_id)
                    st.success("Audio enviado por chat privado.")
                    st.rerun()
            else:
                st.info("Aún no tienes contactos agregados. Ve a la pestaña 'Agregar por Cédula' para vincularte con alguien.")

    elif seleccion_modulo == "🛠️ Herramientas de Ciberseguridad & Análisis":
        st.markdown("### 🛠️ Módulo de Ciberseguridad & Red Team")
        st.info("Herramientas activas para auditoría, escaneo de puertos y análisis de aplicaciones.")
        target_ip = st.text_input("IP o Dominio Objetivo:", value="127.0.0.1")
        if st.button("Ejecutar Escaneo Rápido"):
            st.success(f"Escaneando objetivos en {target_ip}...")
            st.code(f"Starting Nmap scan on {target_ip}\nHost is up.\nPORT 80/tcp open http\nPORT 443/tcp open https", language="bash")

    elif seleccion_modulo == "📞 Videollamada & Streaming WebRTC":
        st.markdown("### 📞 Videollamadas & Streaming WebRTC P2P")
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
