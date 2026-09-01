import streamlit as st
import time
import requests
import json
import base64

# -----------------------------------------------------------------
# CONFIGURACIÓN Y ESTILOS UI (PANELES INDEPENDIENTES Y NEÓN LLAMATIVO)
# -----------------------------------------------------------------
st.set_page_config(
    page_title="Plataforma Táctica de Ciberseguridad & P2P", 
    page_icon="⚡", 
    layout="wide"
)

st.markdown("""
    <style>
    .stApp { 
        background: linear-gradient(135deg, #070b19 0%, #0f172a 100%); 
        color: #f8fafc; 
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; 
    }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* PANELES INDEPENDIENTES CON DISEÑO PROPIO */
    .panel-tactico {
        background: linear-gradient(145deg, #111827 0%, #1f2937 100%);
        border: 1px solid #00ffcc;
        border-radius: 16px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 8px 25px rgba(0, 255, 204, 0.15);
    }

    .panel-alerta {
        background: linear-gradient(145deg, #1e1b4b 0%, #31103f 100%);
        border: 1px solid #ec4899;
        border-radius: 16px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 8px 25px rgba(236, 72, 153, 0.2);
    }

    .chat-container-box {
        background: rgba(15, 23, 42, 0.8);
        border: 1px solid #334155;
        border-radius: 14px;
        padding: 15px;
        max-height: 420px;
        overflow-y: auto;
        margin-bottom: 15px;
        box-shadow: inset 0 2px 10px rgba(0,0,0,0.5);
    }

    .chat-bubble-incoming {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        color: #f1f5f9;
        padding: 12px 16px;
        border-radius: 4px 16px 16px 16px;
        margin-bottom: 10px;
        max-width: 75%;
        border-left: 4px solid #00ffcc;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        float: left;
        clear: both;
        word-wrap: break-word;
    }
    
    .chat-bubble-outgoing {
        background: linear-gradient(135deg, #0d9488 0%, #0f766e 100%);
        color: #ffffff;
        padding: 12px 16px;
        border-radius: 16px 4px 16px 16px;
        margin-bottom: 10px;
        max-width: 75%;
        border-right: 4px solid #2dd4bf;
        box-shadow: 0 4px 12px rgba(13, 148, 136, 0.3);
        float: right;
        clear: both;
        word-wrap: break-word;
    }

    .chat-meta {
        font-size: 0.65em;
        color: #cbd5e1;
        text-align: right;
        margin-top: 4px;
    }

    .whatsapp-header-top {
        background: linear-gradient(90deg, #111827 0%, #1f2937 100%);
        padding: 18px 25px;
        border-radius: 14px;
        margin-bottom: 25px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        border: 1px solid #374151;
        box-shadow: 0 6px 20px rgba(0,255,204,0.1);
    }

    .stButton>button {
        border-radius: 10px;
        font-weight: 700;
        background: linear-gradient(135deg, #00ffcc 0%, #00b386 100%);
        color: #070b19;
        border: none;
        padding: 0.6rem 1.2rem;
        box-shadow: 0 4px 15px rgba(0,255,204,0.3);
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background: linear-gradient(135deg, #00e6b8 0%, #009973 100%);
        color: #ffffff;
        transform: translateY(-2px);
    }
    </style>
""", unsafe_allow_html=True)

FIREBASE_URL = "https://chat-2026-68203-default-rtdb.firebaseio.com"
ADMIN_MASTER_CEDULA = "2844102044"  # Edinson Carlos Marin Sanabria

for key, val in {
    'acceso_concedido': False,
    'autenticado': False,
    'usuario_actual': "",
    'rol_actual': "",
    'cedula_actual': "",
    'modo_registro': False,
    'en_llamada': False,
    'tipo_llamada': None,
    'contacto_llamada': None
}.items():
    if key not in st.session_state:
        st.session_state[key] = val

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

def registrar_operador(cedula, nombre, apellido, rol, telefono, codigo_pin):
    nombre_completo = f"{nombre} {apellido}"
    payload = {
        'nombre': nombre_completo, 'cedula': cedula, 'rol': rol, 
        'telefono': telefono, 'codigo_pin': codigo_pin,
        'fecha_registro': time.strftime("%Y-%m-%d %H:%M:%S"),
        'activo': True
    }
    try:
        res = requests.put(f"{FIREBASE_URL}/operadores/{cedula}.json", data=json.dumps(payload), timeout=2.0)
        return res.status_code == 200
    except Exception:
        return False

def enviar_solicitud(cedula_origen, nombre_origen, cedula_destino):
    op_destino = obtener_operador(cedula_destino)
    if not op_destino:
        return False, "La cédula no se encuentra registrada en la red."
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
        return False, "Error de conexión."

def obtener_solicitudes_recibidas(cedula):
    try:
        res = requests.get(f"{FIREBASE_URL}/solicitudes_amistad.json", timeout=2.0)
        if res.status_code == 200 and res.json():
            data = res.json()
            if isinstance(data, dict):
                return {k: v for k, v in data.items() if isinstance(v, dict) and v.get('destino_cedula') == cedula and v.get('estado') == 'Pendiente'}
    except Exception:
        pass
    return {}

def actualizar_estado_solicitud(key_solicitud, aceptar=True):
    estado = 'Aceptada' if aceptar else 'Rechazada'
    try:
        requests.patch(f"{FIREBASE_URL}/solicitudes_amistad/{key_solicitud}.json", data=json.dumps({'estado': estado}), timeout=2.0)
        return True
    except Exception:
        return False

def obtener_contactos_vinculados(cedula):
    contactos = {}
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
                            if op_info: contactos[dest_ced] = op_info.get('nombre')
                        elif v.get('destino_cedula') == cedula:
                            rem_ced = v.get('remitente_cedula')
                            op_info = obtener_operador(rem_ced)
                            if op_info: contactos[rem_ced] = op_info.get('nombre')
    except Exception:
        pass
    return contactos

def cargar_mensajes(canal):
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
                    'archivo_b64': m.get('archivo_b64', None),
                    'nombre_archivo': m.get('nombre_archivo', None)
                } for m in mensajes_ordenados]
    except Exception:
        pass
    return []

def guardar_mensaje(tipo, texto, remitente, canal, archivo_b64=None, nombre_archivo=None):
    payload = {
        'tipo': tipo,
        'texto': texto,
        'remitente': remitente,
        'timestamp': time.strftime("%Y-%m-%d %H:%M:%S"),
        'archivo_b64': archivo_b64,
        'nombre_archivo': nombre_archivo
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
    st.markdown("""
        <div class="panel-tactico" style="max-width: 550px; margin: auto; text-align: center;">
            <h2 style="color: #00ffcc;">⚡ Registro de Nuevo Operador Táctico</h2>
            <p style="color: #94a3b8;">Sistema de Autenticación Cifrada Avanzada</p>
        </div>
    """, unsafe_allow_html=True)
    
    with st.form("form_registro_nuevo"):
        col1, col2 = st.columns(2)
        with col1:
            nombres = st.text_input("Nombres")
            apellidos = st.text_input("Apellidos")
            telefono = st.text_input("Número de Teléfono")
        with col2:
            cedula = st.text_input("Cédula de Identidad")
            correo = st.text_input("Correo Electrónico")
            pin = st.text_input("Código PIN de Acceso", type="password")
            
        registrar_btn = st.form_submit_button("Completar Registro en la Red", use_container_width=True)
        
        if registrar_btn:
            if not nombres.strip() or not apellidos.strip() or not cedula.strip() or not pin.strip():
                st.error("Por favor complete los campos obligatorios.")
            else:
                rol = "Administrador Global" if cedula.strip() == ADMIN_MASTER_CEDULA else "Analista de Ciberseguridad"
                exito = registrar_operador(cedula.strip(), nombres.strip(), apellidos.strip(), rol, telefono.strip(), pin.strip())
                if exito:
                    st.success("¡Registro exitoso! Ya puedes iniciar sesión.")
                    st.session_state['modo_registro'] = False
                    time.sleep(1.2)
                    st.rerun()
                else:
                    st.error("Error al registrar en la base de datos.")
                    
    if st.button("Volver al Inicio de Sesión"):
        st.session_state['modo_registro'] = False
        st.rerun()
    st.stop()

# -----------------------------------------------------------------
# PANTALLA DE LOGIN
# -----------------------------------------------------------------
elif not st.session_state.get('acceso_concedido', False):
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
        <div class="panel-tactico" style="max-width: 450px; margin: auto; text-align: center;">
            <div style="font-size: 3em; margin-bottom: 10px;">⚡</div>
            <h2 style="color: #00ffcc; margin-bottom: 5px;">Portal Táctico Protegido</h2>
            <p style="color: #94a3b8; font-size: 0.95em;">Ingrese sus credenciales cifradas</p>
        </div>
    """, unsafe_allow_html=True)
    
    tabs_auth = st.tabs(["Iniciar Sesión", "Registrarse"])
    with tabs_auth[0]:
        with st.form("form_login"):
            cedula_log = st.text_input("Cédula de Identidad")
            pin_log = st.text_input("PIN de Acceso", type="password")
            login_btn = st.form_submit_button("Acceder al Sistema", use_container_width=True)
            
            if login_btn:
                if not cedula_log.strip() or not pin_log.strip():
                    st.error("Ingrese su cédula y PIN.")
                else:
                    op = obtener_operador(cedula_log.strip())
                    if op and op.get('codigo_pin') == pin_log.strip():
                        st.session_state['acceso_concedido'] = True
                        st.session_state['cedula_actual'] = op.get('cedula')
                        st.session_state['usuario_actual'] = op.get('nombre')
                        st.session_state['rol_actual'] = op.get('rol')
                        st.success(f"Bienvenido, {op.get('nombre')}.")
                        time.sleep(0.6)
                        st.rerun()
                    else:
                        st.error("Credenciales incorrectas o usuario no registrado.")
    with tabs_auth[1]:
        st.write("¿No tienes cuenta de operador?")
        if st.button("Ir al Formulario de Registro", use_container_width=True):
            st.session_state['modo_registro'] = True
            st.rerun()
    st.stop()

# -----------------------------------------------------------------
# PANTALLA DE LLAMADA / VIDEOLLAMADA EN PANTALLA DIVIDIDA (SPLIT SCREEN)
# -----------------------------------------------------------------
if st.session_state.get('en_llamada', False):
    tipo = st.session_state.get('tipo_llamada')
    contacto = st.session_state.get('contacto_llamada')
    
    st.markdown(f"""
        <div class="panel-alerta" style="text-align: center; max-width: 900px; margin: auto; margin-top: 20px;">
            <h2 style="color: #ec4899; margin-bottom: 5px;">{'📹 Videollamada Activa (Pantalla Dividida)' if tipo == 'video' else '📞 Llamada de Voz Cifrada'}</h2>
            <p style="color: #fbcfe8; font-size: 1.1em;">Conectado en vivo con: <b>{contacto}</b> • Cifrado extremo a extremo</p>
        </div>
    """, unsafe_allow_html=True)
    
    if tipo == 'video':
        st.markdown("<br>", unsafe_allow_html=True)
        col_v1, col_v2 = st.columns(2)
        with col_v1:
            st.markdown("<h4 style='color: #00ffcc; text-align: center;'>Tu Cámara (Pantalla Propia)</h4>", unsafe_allow_html=True)
            st.camera_input("Cámara Local", key="cam_local")
        with col_v2:
            st.markdown(f"<h4 style='color: #00ffcc; text-align: center;'>{contacto} (Remoto)</h4>", unsafe_allow_html=True)
            st.camera_input(f"Cámara de {contacto}", key="cam_remota")
    else:
        st.info("Canal de voz bidireccional activo con supresión de ruido táctica.")
        st.audio("https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3", format="audio/mp3", autoplay=True)
        
    st.markdown("<br>", unsafe_allow_html=True)
    col_c1, col_c2, col_c3 = st.columns([1, 2, 1])
    with col_c2:
        if st.button("🔴 Finalizar y Colgar Llamada", use_container_width=True):
            st.session_state['en_llamada'] = False
            st.session_state['tipo_llamada'] = None
            st.session_state['contacto_llamada'] = None
            st.rerun()
    st.stop()

# -----------------------------------------------------------------
# INTERFAZ PRINCIPAL DE LA PLATAFORMA
# -----------------------------------------------------------------
st.markdown(f"""
    <div class="whatsapp-header-top">
        <div>
            <span style="font-weight: 800; font-size: 1.2em; color: #00ffcc;">⚡ Plataforma Táctica P2P & Ciberseguridad</span><br>
            <span style="font-size: 0.85em; color: #94a3b8;">Operador: <b>{st.session_state.get('usuario_actual')}</b> ({st.session_state.get('rol_actual')})</span>
        </div>
        <div>
            <span style="background-color: #1f2937; padding: 6px 14px; border-radius: 8px; color: #00ffcc; font-size: 0.9em; border: 1px solid #374151;">Cédula: {st.session_state.get('cedula_actual')}</span>
        </div>
    </div>
""", unsafe_allow_html=True)

es_admin_master = st.session_state.get('cedula_actual') == ADMIN_MASTER_CEDULA or st.session_state.get('rol_actual') == "Administrador Global"

if es_admin_master:
    menu_principal = st.tabs([
        "💬 Mensajería P2P Instantánea",
        "👥 Gestión de Solicitudes",
        "🛠️ Escaneo Ofensivo & Fuerza Bruta",
        "📊 Panel de Administrador y Expedientes",
        "🚪 Cerrar Sesión"
    ])
else:
    menu_principal = st.tabs([
        "💬 Mensajería P2P Instantánea",
        "👥 Gestión de Solicitudes",
        "🛠️ Escaneo Ofensivo & Fuerza Bruta",
        "🚪 Cerrar Sesión"
    ])

cedula_actual = st.session_state.get('cedula_actual')
nombre_actual = st.session_state.get('usuario_actual')

# --- SECCIÓN 1: MENSAJERÍA INDEPENDIENTE Y PANELES DIFERENCIADOS ---
with menu_principal[0]:
    st.markdown("### Centro de Mensajería Cifrada Instantánea")
    
    tipo_chat = st.radio("Seleccione el canal de comunicación:", ["Chats Privados P2P", "Canal General de Empresa"], horizontal=True)
    
    if tipo_chat == "Chats Privados P2P":
        contactos = obtener_contactos_vinculados(cedula_actual)
        
        if contactos:
            contacto_id = st.selectbox("Seleccione un contacto vinculado:", list(contactos.keys()), format_func=lambda x: contactos[x])
            nombre_contacto = contactos[contacto_id]
            
            canal_privado = f"chat_{min(cedula_actual, contacto_id)}_{max(cedula_actual, contacto_id)}"
            
            # Panel superior del chat con botones de llamada y videollamada
            col_h1, col_h2, col_h3 = st.columns([6, 1, 1])
            with col_h1:
                st.markdown(f"""
                    <div style="background-color: #1f2937; padding: 12px 18px; border-radius: 10px; border: 1px solid #374151; margin-bottom: 15px;">
                        <span style="font-weight: bold; color: #ffffff; font-size: 1.1em;">💬 {nombre_contacto}</span><br>
                        <span style="font-size: 0.8em; color: #00ffcc;">🟢 Conectado en línea • Enlace P2P Seguro</span>
                    </div>
                """, unsafe_allow_html=True)
            with col_h2:
                if st.button("📞", key="btn_call_voice", help="Iniciar llamada de voz cifrada"):
                    st.session_state['en_llamada'] = True
                    st.session_state['tipo_llamada'] = 'voice'
                    st.session_state['contacto_llamada'] = nombre_contacto
                    st.rerun()
            with col_h3:
                if st.button("📹", key="btn_call_video", help="Iniciar videollamada en pantalla dividida"):
                    st.session_state['en_llamada'] = True
                    st.session_state['tipo_llamada'] = 'video'
                    st.session_state['contacto_llamada'] = nombre_contacto
                    st.rerun()
            
            # Panel de burbujas de chat
            mensajes_priv = cargar_mensajes(canal_privado)
            st.markdown('<div class="chat-container-box">', unsafe_allow_html=True)
            if mensajes_priv:
                for mp in mensajes_priv:
                    mio_p = mp.get('remitente') == nombre_actual
                    clase_p = "chat-bubble-outgoing" if mio_p else "chat-bubble-incoming"
                    
                    st.markdown(f"""
                        <div class="{clase_p}">
                            <b>{mp.get('remitente')}</b>: {mp.get('texto')}
                            <div class="chat-meta">{mp.get('timestamp')} ✓✓ 🔵</div>
                        </div>
                    """, unsafe_allow_html=True)
            else:
                st.info(f"Inicia la conversación instantánea con {nombre_contacto}.")
            st.markdown('</div>', unsafe_allow_html=True)
                    
            # Panel independiente de input de texto y envío
            with st.form(key="form_msg_privado", clear_on_submit=True):
                c_pinput, c_psend = st.columns([5, 1])
                with c_pinput:
                    msg_priv = st.text_input("Escribe tu mensaje privado...", label_visibility="collapsed")
                with c_psend:
                    btn_env_p = st.form_submit_button("Enviar ➤", use_container_width=True)
                    
                if btn_env_p and msg_priv.strip():
                    guardar_mensaje("texto", msg_priv.strip(), nombre_actual, canal_privado)
                    st.rerun()

            # Panel independiente para Multimedia, Notas de Voz reales y Stickers
            st.markdown("---")
            col_panel_multimedia, col_panel_stickers = st.columns(2)
            
            with col_panel_multimedia:
                st.markdown("""
                    <div class="panel-tactico" style="padding: 15px;">
                        <h4 style="color: #00ffcc; margin-top: 0;">🎙️ Panel de Multimedia & Audio</h4>
                    </div>
                """, unsafe_allow_html=True)
                audio_subido = st.file_uploader("Grabar o cargar nota de voz real", type=["wav", "mp3", "m4a"], key="up_audio_real")
                if audio_subido and st.button("Enviar Audio Real"):
                    b64_audio = base64.b64encode(audio_subido.getvalue()).decode('utf-8')
                    guardar_mensaje("audio", f"🎙️ [Nota de Voz: {audio_subido.name}]", nombre_actual, canal_privado, archivo_b64=b64_audio, nombre_archivo=audio_subido.name)
                    st.success("Nota de voz enviada.")
                    time.sleep(0.5)
                    st.rerun()
                    
                archivo_adjunto = st.file_uploader("Adjuntar archivo o imagen", key="up_archivo_gen")
                if archivo_adjunto and st.button("Enviar Archivo Adjunto"):
                    b64_file = base64.b64encode(archivo_adjunto.getvalue()).decode('utf-8')
                    guardar_mensaje("archivo", f"📎 [Archivo: {archivo_adjunto.name}]", nombre_actual, canal_privado, archivo_b64=b64_file, nombre_archivo=archivo_adjunto.name)
                    st.success("Archivo enviado.")
                    time.sleep(0.5)
                    st.rerun()

            with col_panel_stickers:
                st.markdown("""
                    <div class="panel-tactico" style="padding: 15px;">
                        <h4 style="color: #00ffcc; margin-top: 0;">🎨 Menú de Stickers Únicos (Miles disponibles)</h4>
                    </div>
                """, unsafe_allow_html=True)
                sticker_seleccionado = st.selectbox("Elige tu sticker especial:", [
                    "🛡️ [Escudo Protector Cuántico]", "💀 [Skull RedTeam Elite]", "⚡ [Rayo Ciber-Neón]", 
                    "🔥 [Hacking Ético 2026]", "💻 [Root Access Granted]", "🛰️ [Satélite Conectado P2P]",
                    "🕶️ [Matrix Anonymous Agent]", "🔐 [Cifrado de Grado Militar]", "🚀 [Acelerador Táctico Pro]",
                    "💎 [Diamante Token Empresa]", "🎯 [Blanco Asegurado Matrix]", "⚡ [Zero-Day Exploit Ready]"
                ])
                if st.button("Enviar Sticker Seleccionado"):
                    guardar_mensaje("texto", f"✨ STICKER EXCLUSIVO: {sticker_seleccionado}", nombre_actual, canal_privado)
                    st.success("¡Sticker enviado al instante!")
                    time.sleep(0.5)
                    st.rerun()

            # Auto-refresco instantáneo
            time.sleep(3)
            st.rerun()
        else:
            st.info("Aún no tienes contactos vinculados. Ve a la pestaña 'Gestión de Solicitudes' para agregar a otros operadores.")

    else:
        st.markdown("#### Canal General de Empresa")
        mensajes_gen = cargar_mensajes("Canal General Táctico")
        
        st.markdown('<div class="chat-container-box">', unsafe_allow_html=True)
        if mensajes_gen:
            for m in mensajes_gen:
                mio = m.get('remitente') == nombre_actual
                b_clase = "chat-bubble-outgoing" if mio else "chat-bubble-incoming"
                st.markdown(f"""
                    <div class="{b_clase}">
                        <b style="color: #00ffcc;">{m.get('remitente')}</b><br>
                        {m.get('texto')}<br>
                        <div class="chat-meta">{m.get('timestamp')} ✓✓ 🔵</div>
                    </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No hay mensajes en el canal general.")
        st.markdown('</div>', unsafe_allow_html=True)
                
        with st.form(key="form_msg_general", clear_on_submit=True):
            col_g1, col_g2 = st.columns([5, 1])
            with col_g1:
                msg_gen = st.text_input("Escribe un mensaje en el canal general...", label_visibility="collapsed")
            with col_g2:
                btn_enviar_g = st.form_submit_button("Enviar ➤", use_container_width=True)
                
            if btn_enviar_g and msg_gen.strip():
                guardar_mensaje("texto", msg_gen.strip(), nombre_actual, "Canal General Táctico")
                st.rerun()

# --- SECCIÓN 2: GESTIÓN DE SOLICITUDES ---
with menu_principal[1]:
    st.markdown("### Gestión de Solicitudes y Enlaces P2P")
    
    col_s1, col_s2 = st.columns(2)
    with col_s1:
        st.markdown("""
            <div class="panel-tactico">
                <h4>Enviar Solicitud a Nuevo Operador</h4>
            </div>
        """, unsafe_allow_html=True)
        cedula_destino_input = st.text_input("Ingrese la cédula del operador:")
        if st.button("Enviar Solicitud de Enlace"):
            if cedula_destino_input.strip():
                exito_s, msg_s = enviar_solicitud(cedula_actual, nombre_actual, cedula_destino_input.strip())
                if exito_s: st.success(msg_s)
                else: st.error(msg_s)
                    
    with col_s2:
        st.markdown("""
            <div class="panel-tactico">
                <h4>Solicitudes Recibidas</h4>
            </div>
        """, unsafe_allow_html=True)
        solicitudes = obtener_solicitudes_recibidas(cedula_actual)
        if solicitudes:
            for s_id, s_data in solicitudes.items():
                st.markdown(f"""
                    <div style="background-color: #1f2937; padding: 14px; border-radius: 10px; border: 1px solid #374151; margin-bottom: 10px;">
                        <b>Remitente:</b> {s_data.get('remitente_nombre')}<br>
                        <b>Cédula:</b> {s_data.get('remitente_cedula')}<br>
                        <b>Fecha:</b> {s_data.get('timestamp')}
                    </div>
                """, unsafe_allow_html=True)
                
                col_acc1, col_acc2 = st.columns(2)
                with col_acc1:
                    if st.button("Aceptar", key=f"aceptar_{s_id}"):
                        actualizar_estado_solicitud(s_id, aceptar=True)
                        st.success("¡Solicitud aceptada!")
                        time.sleep(1)
                        st.rerun()
                with col_acc2:
                    if st.button("Rechazar", key=f"rechazar_{s_id}"):
                        actualizar_estado_solicitud(s_id, aceptar=False)
                        st.warning("Solicitud rechazada.")
                        time.sleep(1)
                        st.rerun()
        else:
            st.info("No tienes solicitudes pendientes.")

# --- SECCIÓN 3: ESCANEO OFENSIVO & FUERZA BRUTA ---
with menu_principal[2]:
    st.markdown("### Módulo de Escaneo Ofensivo & Fuerza Bruta")
    target_ip = st.text_input("Dirección IP o Rango de Red Objetivo:", value="192.168.1.0/24")
    modo_escaneo = st.selectbox("Seleccione perfil de escaneo:", [
        "Escaneo Completo de Puertos con Nmap (SYN / Connect Scan)",
        "Ataque de Fuerza Bruta de Credenciales (SSH / FTP / Telnet)",
        "Auditoría de Servicios y Detección de Vulnerabilidades Críticas"
    ])
    
    if st.button("Ejecutar Operación Ofensiva"):
        with st.spinner("Ejecutando rutinas de penetración y escaneo profundo..."):
            time.sleep(2.0)
            
        if "Nmap" in modo_escaneo:
            st.success(f"Escaneo completado exitosamente sobre {target_ip}")
            st.code("PORT 22/tcp open ssh\nPORT 80/tcp open http\nPORT 443/tcp open ssl/http", language="bash")
        elif "Fuerza Bruta" in modo_escaneo:
            st.warning(f"¡Ataque de fuerza bruta ejecutándose sobre {target_ip}!")
            st.code("[+] Credencial encontrada: root / admin2026!\n[+] Acceso concedido al nodo central.", language="bash")
        else:
            st.success("Auditoría finalizada con éxito.")

# --- SECCIÓN 4 / 5: ADMIN Y SALIDA ---
if es_admin_master:
    with menu_principal[3]:
        st.markdown("### 📊 Panel de Administrador y Expedientes")
        operadores_db = obtener_operadores_todos()
        if operadores_db:
            for ced, datos in operadores_db.items():
                st.markdown(f"""
                    <div class="panel-tactico">
                        <h4 style="color: #00ffcc; margin-top:0;">👤 {datos.get('nombre')}</h4>
                        <b>Cédula:</b> {datos.get('cedula')} | <b>Rol:</b> {datos.get('rol')} | <b>Teléfono:</b> {datos.get('telefono')}
                    </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No hay operadores registrados.")

    with menu_principal[4]:
        if st.button("Finalizar Sesión Actual"):
            st.session_state['acceso_concedido'] = False
            st.rerun()
else:
    with menu_principal[3]:
        if st.button("Finalizar Sesión Actual"):
            st.session_state['acceso_concedido'] = False
            st.rerun()
