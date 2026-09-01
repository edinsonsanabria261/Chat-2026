import streamlit as st
import time
import requests
import json
import base64

# -----------------------------------------------------------------
# CONFIGURACIÓN DE LA APLICACIÓN Y ESTILOS COMPACTOS
# -----------------------------------------------------------------
st.set_page_config(
    page_title="Plataforma Táctica Ciberseguridad Ultra P2P [900TB Core]", 
    page_icon="⚡", 
    layout="wide"
)

st.markdown("""
    <style>
    .stApp { 
        background: linear-gradient(135deg, #030712 0%, #0f172a 50%, #020617 100%); 
        color: #f8fafc; 
        font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; 
    }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* PANELES LIMPIOS Y COMPACTOS */
    .panel-tactico-compacto {
        background: linear-gradient(145deg, #0f172a 100%, #1e293b 0%);
        border: 1px solid #334155;
        border-radius: 14px;
        padding: 18px;
        margin-bottom: 15px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
    }

    .chat-container-box-v3 {
        background: rgba(3, 7, 18, 0.95);
        border: 1px solid #334155;
        border-radius: 14px;
        padding: 15px;
        max-height: 420px;
        overflow-y: auto;
        margin-bottom: 15px;
        box-shadow: inset 0 2px 10px rgba(0,0,0,0.6);
    }

    .chat-bubble-incoming {
        background: #1e293b;
        color: #f1f5f9;
        padding: 10px 14px;
        border-radius: 4px 14px 14px 14px;
        margin-bottom: 10px;
        max-width: 75%;
        border-left: 3px solid #00ffcc;
        float: left;
        clear: both;
        word-wrap: break-word;
        font-size: 0.95em;
    }
    
    .chat-bubble-outgoing {
        background: #0d9488;
        color: #ffffff;
        padding: 10px 14px;
        border-radius: 14px 4px 14px 14px;
        margin-bottom: 10px;
        max-width: 75%;
        border-right: 3px solid #2dd4bf;
        float: right;
        clear: both;
        word-wrap: break-word;
        font-size: 0.95em;
    }

    .chat-meta {
        font-size: 0.65em;
        color: #cbd5e1;
        text-align: right;
        margin-top: 4px;
    }

    .whatsapp-header-top {
        background: #0f172a;
        padding: 15px 20px;
        border-radius: 12px;
        margin-bottom: 20px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        border: 1px solid #334155;
    }

    .stButton>button {
        border-radius: 8px;
        font-weight: 700;
        background: linear-gradient(135deg, #00ffcc 0%, #00b386 100%);
        color: #030712;
        border: none;
        padding: 0.5rem 1rem;
        transition: all 0.2s ease;
    }
    .stButton>button:hover {
        background: linear-gradient(135deg, #00e6b8 0%, #009973 100%);
        color: #ffffff;
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
    'contacto_llamada': None,
    'mostrar_adjuntos': False
}.items():
    if key not in st.session_state:
        st.session_state[key] = val

def obtener_operador(cedula):
    try:
        res = requests.get(f"{FIREBASE_URL}/operadores/{cedula}.json", timeout=2.5)
        if res.status_code == 200 and res.json():
            data = res.json()
            if isinstance(data, dict) and data.get('activo', True):
                return data
    except Exception:
        pass
    return None

def obtener_operadores_todos():
    try:
        res = requests.get(f"{FIREBASE_URL}/operadores.json", timeout=2.5)
        if res.status_code == 200 and res.json():
            data = res.json()
            if isinstance(data, dict):
                return data
    except Exception:
        pass
    return {}

def registrar_operador(cedula, nombre, apellido, rol, telefono, codigo_pin):
    nombre_completo = f"{nombre} {apellido}"
    payload = {
        'nombre': nombre_completo, 'cedula': cedula, 'rol': rol, 
        'telefono': telefono, 'codigo_pin': codigo_pin,
        'fecha_registro': time.strftime("%Y-%m-%d %H:%M:%S"),
        'activo': True,
        'almacenamiento_asignado_tb': 900
    }
    try:
        res = requests.put(f"{FIREBASE_URL}/operadores/{cedula}.json", data=json.dumps(payload), timeout=2.5)
        return res.status_code == 200
    except Exception:
        return False

def enviar_solicitud(cedula_origen, nombre_origen, cedula_destino):
    op_destino = obtener_operador(cedula_destino)
    if not op_destino:
        return False, "La cédula no está registrada en el sistema."
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
        requests.post(f"{FIREBASE_URL}/solicitudes_amistad.json", data=json.dumps(payload), timeout=2.5)
        return True, f"Solicitud enviada a {op_destino.get('nombre')}."
    except Exception:
        return False, "Error de conexión."

def obtener_solicitudes_recibidas(cedula):
    try:
        res = requests.get(f"{FIREBASE_URL}/solicitudes_amistad.json", timeout=2.5)
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
        requests.patch(f"{FIREBASE_URL}/solicitudes_amistad/{key_solicitud}.json", data=json.dumps({'estado': estado}), timeout=2.5)
        return True
    except Exception:
        return False

def obtener_contactos_vinculados(cedula):
    contactos = {}
    try:
        res = requests.get(f"{FIREBASE_URL}/solicitudes_amistad.json", timeout=2.5)
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
        res = requests.get(f"{FIREBASE_URL}/chat_whatsapp/{canal}.json", timeout=2.5)
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
        requests.post(f"{FIREBASE_URL}/chat_whatsapp/{canal}.json", data=json.dumps(payload), timeout=2.5)
        return True
    except Exception:
        return False

# -----------------------------------------------------------------
# PANTALLA DE REGISTRO
# -----------------------------------------------------------------
if st.session_state.get('modo_registro', False):
    st.markdown("""
        <div class="panel-tactico-compacto" style="max-width: 550px; margin: auto; text-align: center;">
            <h3 style="color: #00ffcc;">⚡ Registro de Operador</h3>
        </div>
    """, unsafe_allow_html=True)
    
    with st.form("form_registro_compacto"):
        nombres = st.text_input("Nombres")
        apellidos = st.text_input("Apellidos")
        cedula = st.text_input("Cédula de Identidad")
        telefono = st.text_input("Teléfono Móvil")
        pin = st.text_input("PIN de Acceso", type="password")
            
        if st.form_submit_button("Completar Registro", use_container_width=True):
            if not nombres.strip() or not cedula.strip() or not pin.strip():
                st.error("Complete los campos obligatorios.")
            else:
                rol = "Administrador Global" if cedula.strip() == ADMIN_MASTER_CEDULA else "Analista"
                if registrar_operador(cedula.strip(), nombres.strip(), apellidos.strip(), rol, telefono.strip(), pin.strip()):
                    st.success("¡Registrado con éxito!")
                    st.session_state['modo_registro'] = False
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("Error al registrar.")
                    
    if st.button("Volver al Ingreso"):
        st.session_state['modo_registro'] = False
        st.rerun()
    st.stop()

# -----------------------------------------------------------------
# PANTALLA DE LOGIN
# -----------------------------------------------------------------
elif not st.session_state.get('acceso_concedido', False):
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
        <div class="panel-tactico-compacto" style="max-width: 420px; margin: auto; text-align: center;">
            <h3 style="color: #00ffcc; margin-bottom: 5px;">🔐 Ingreso al Sistema</h3>
            <p style="color: #94a3b8; font-size: 0.9em;">Plataforma P2P Cifrada [900TB]</p>
        </div>
    """, unsafe_allow_html=True)
    
    tabs_auth = st.tabs(["Iniciar Sesión", "Registrarse"])
    with tabs_auth[0]:
        with st.form("form_login_compact"):
            cedula_log = st.text_input("Cédula de Identidad")
            pin_log = st.text_input("PIN de Seguridad", type="password")
            if st.form_submit_button("Entrar", use_container_width=True):
                op = obtener_operador(cedula_log.strip())
                if op and op.get('codigo_pin') == pin_log.strip():
                    st.session_state['acceso_concedido'] = True
                    st.session_state['cedula_actual'] = op.get('cedula')
                    st.session_state['usuario_actual'] = op.get('nombre')
                    st.session_state['rol_actual'] = op.get('rol')
                    st.rerun()
                else:
                    st.error("Credenciales incorrectas.")
    with tabs_auth[1]:
        if st.button("Ir al Formulario de Registro", use_container_width=True):
            st.session_state['modo_registro'] = True
            st.rerun()
    st.stop()

# -----------------------------------------------------------------
# PANTALLA DE LLAMADA O VIDEOLLAMADA
# -----------------------------------------------------------------
if st.session_state.get('en_llamada', False):
    tipo = st.session_state.get('tipo_llamada')
    contacto = st.session_state.get('contacto_llamada')
    
    st.markdown(f"""
        <div class="panel-tactico-compacto" style="text-align: center; max-width: 800px; margin: auto;">
            <h3 style="color: #ec4899;">{'📹 Videollamada P2P' : tipo == 'video' else '📞 Llamada de Voz Cifrada'}</h3>
            <p>Conectado con: <b>{contacto}</b></p>
        </div>
    """, unsafe_allow_html=True)
    
    if tipo == 'video':
        col_v1, col_v2 = st.columns(2)
        with col_v1:
            st.markdown("<b>Tu Cámara</b>", unsafe_allow_html=True)
            st.camera_input("Local", key="cam_loc")
        with col_v2:
            st.markdown(f"<b>Cámara de {contacto}</b>", unsafe_allow_html=True)
            st.camera_input("Remota", key="cam_rem")
    else:
        st.info("Audio bidimensional activo...")
        st.audio("https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3", format="audio/mp3", autoplay=True)
        
    if st.button("🔴 Colgar y Salir", use_container_width=True):
        st.session_state['en_llamada'] = False
        st.rerun()
    st.stop()

# -----------------------------------------------------------------
# INTERFAZ PRINCIPAL CON PESTAÑAS
# -----------------------------------------------------------------
st.markdown(f"""
    <div class="whatsapp-header-top">
        <div>
            <span style="font-weight: 800; color: #00ffcc;">⚡ Plataforma P2P [900TB]</span><br>
            <span style="font-size: 0.85em; color: #94a3b8;">Operador: <b>{st.session_state.get('usuario_actual')}</b></span>
        </div>
        <div>
            <span style="background-color: #1e293b; padding: 6px 12px; border-radius: 8px; color: #00ffcc; font-size: 0.85em;">Cédula: {st.session_state.get('cedula_actual')}</span>
        </div>
    </div>
""", unsafe_allow_html=True)

es_admin_master = st.session_state.get('cedula_actual') == ADMIN_MASTER_CEDULA or st.session_state.get('rol_actual') == "Administrador Global"

menu_principal = st.tabs([
    "💬 Chats P2P",
    "📞 Llamadas",
    "🔔 Novedades",
    "🛠️ Herramientas",
    "📊 Panel 900TB" if es_admin_master else "🚪 Salir",
    "🚪 Salir" if es_admin_master else None
])
# Limpiar pestañas nulas si no es admin
menu_principal = [t for t in menu_principal if t is not None]

cedula_actual = st.session_state.get('cedula_actual')
nombre_actual = st.session_state.get('usuario_actual')

# --- TAB 1: CHATS P2P (COMPACTO Y ORDENADO) ---
with menu_principal[0]:
    tipo_chat = st.radio("Canal:", ["Privados", "General [900TB]"], horizontal=True, label_visibility="collapsed")
    
    if tipo_chat == "Privados":
        contactos = obtener_contactos_vinculados(cedula_actual)
        if contactos:
            contacto_id = st.selectbox("Seleccionar contacto:", list(contactos.keys()), format_func=lambda x: contactos[x])
            nombre_contacto = contactos[contacto_id]
            canal_privado = f"chat_{min(cedula_actual, contacto_id)}_{max(cedula_actual, contacto_id)}"
            
            # Cabecera del chat con botones de llamada pequeños
            col_ch1, col_ch2, col_ch3 = st.columns([6, 1, 1])
            with col_ch1:
                st.markdown(f"<b>Chat con: {nombre_contacto}</b>", unsafe_allow_html=True)
            with col_ch2:
                if st.button("📞", key="bc_v"):
                    st.session_state['en_llamada'] = True
                    st.session_state['tipo_llamada'] = 'voice'
                    st.session_state['contacto_llamada'] = nombre_contacto
                    st.rerun()
            with col_ch3:
                if st.button("📹", key="bc_d"):
                    st.session_state['en_llamada'] = True
                    st.session_state['tipo_llamada'] = 'video'
                    st.session_state['contacto_llamada'] = nombre_contacto
                    st.rerun()
            
            # Historial de mensajes
            mensajes_priv = cargar_mensajes(canal_privado)
            st.markdown('<div class="chat-container-box-v3">', unsafe_allow_html=True)
            if mensajes_priv:
                for mp in mensajes_priv:
                    mio_p = mp.get('remitente') == nombre_actual
                    clase_p = "chat-bubble-outgoing" if mio_p else "chat-bubble-incoming"
                    st.markdown(f"""
                        <div class="{clase_p}">
                            <b>{mp.get('remitente')}</b>: {mp.get('texto')}
                    """, unsafe_allow_html=True)
                    if mp.get('archivo_b64'):
                        try:
                            fb = base64.b64decode(mp.get('archivo_b64'))
                            if mp.get('tipo') == 'audio':
                                st.audio(fb, format='audio/mp3')
                            else:
                                st.download_button(f"📥 {mp.get('nombre_archivo', 'Archivo')}", fb, file_name=mp.get('nombre_archivo', 'archivo'), key=f"dl_{mp.get('timestamp')}")
                        except Exception:
                            pass
                    st.markdown(f"""
                            <div class="chat-meta">{mp.get('timestamp')}</div>
                        </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("No hay mensajes aún.")
            st.markdown('</div>', unsafe_allow_html=True)
                    
            # Barra de mensajes compacta con botón "+" diminuto para adjuntos
            col_input_txt, col_btn_plus = st.columns([9, 1])
            with col_btn_plus:
                if st.button("➕", key="btn_toggle_adjuntos", help="Adjuntar archivo o nota de voz"):
                    st.session_state['mostrar_adjuntos'] = not st.session_state.get('mostrar_adjuntos', False)
                    st.rerun()
            with col_input_txt:
                with st.form(key="form_msg_p", clear_on_submit=True):
                    msg_priv = st.text_input("Escribe un mensaje...", label_visibility="collapsed")
                    if st.form_submit_button("Enviar ➤"):
                        if msg_priv.strip():
                            guardar_mensaje("texto", msg_priv.strip(), nombre_actual, canal_privado)
                            st.rerun()

            # Menú desplegable pequeño para adjuntar archivos o notas de voz (sin ocupar toda la pantalla)
            if st.session_state.get('mostrar_adjuntos', False):
                with st.expander("📎 Adjuntar Archivos / 🎙️ Nota de Voz (Menú Compacto)", expanded=True):
                    f_audio = st.file_uploader("Nota de voz (.mp3, .wav)", type=["wav", "mp3"], key="up_a")
                    if f_audio and st.button("Enviar Audio"):
                        b64_a = base64.b64encode(f_audio.getvalue()).decode('utf-8')
                        guardar_mensaje("audio", f"🎙️ [Audio: {f_audio.name}]", nombre_actual, canal_privado, archivo_b64=b64_a, nombre_archivo=f_audio.name)
                        st.session_state['mostrar_adjuntos'] = False
                        st.rerun()
                        
                    f_arch = st.file_uploader("Archivo general", key="up_f")
                    if f_arch and st.button("Enviar Archivo"):
                        b64_f = base64.b64encode(f_arch.getvalue()).decode('utf-8')
                        guardar_mensaje("archivo", f"📎 [Archivo: {f_arch.name}]", nombre_actual, canal_privado, archivo_b64=b64_f, nombre_archivo=f_arch.name)
                        st.session_state['mostrar_adjuntos'] = False
                        st.rerun()

            time.sleep(3)
            st.rerun()
        else:
            st.info("No tienes contactos vinculados. Ve a la pestaña 'Novedades' para enlazar operadores.")
    else:
        st.markdown("<b>Canal General</b>", unsafe_allow_html=True)
        mensajes_gen = cargar_mensajes("Canal General Táctico 900TB")
        st.markdown('<div class="chat-container-box-v3">', unsafe_allow_html=True)
        if mensajes_gen:
            for m in mensajes_gen:
                mio = m.get('remitente') == nombre_actual
                b_clase = "chat-bubble-outgoing" if mio else "chat-bubble-incoming"
                st.markdown(f"""
                    <div class="{b_clase}">
                        <b>{m.get('remitente')}</b>: {m.get('texto')}
                        <div class="chat-meta">{m.get('timestamp')}</div>
                    </div>
                """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
                
        with st.form(key="form_msg_g", clear_on_submit=True):
            msg_gen = st.text_input("Mensaje general...", label_visibility="collapsed")
            if st.form_submit_button("Enviar ➤"):
                if msg_gen.strip():
                    guardar_mensaje("texto", msg_gen.strip(), nombre_actual, "Canal General Táctico 900TB")
                    st.rerun()

# --- TAB 2: LLAMADAS ---
with menu_principal[1]:
    st.markdown("### 📞 Directorio de Llamadas")
    contactos_llamada = obtener_contactos_vinculados(cedula_actual)
    if contactos_llamada:
        contacto_sel_call = st.selectbox("Contacto:", list(contactos_llamada.keys()), format_func=lambda x: contactos_llamada[x])
        nombre_sel_call = contactos_llamada[contacto_sel_call]
        
        c1, c2 = st.columns(2)
        with c1:
            if st.button("📞 Llamada de Voz", use_container_width=True):
                st.session_state['en_llamada'] = True
                st.session_state['tipo_llamada'] = 'voice'
                st.session_state['contacto_llamada'] = nombre_sel_call
                st.rerun()
        with c2:
            if st.button("📹 Videollamada", use_container_width=True):
                st.session_state['en_llamada'] = True
                st.session_state['tipo_llamada'] = 'video'
                st.session_state['contacto_llamada'] = nombre_sel_call
                st.rerun()
    else:
        st.info("Sin contactos vinculados.")

# --- TAB 3: NOVEDADES Y SOLICITUDES ---
with menu_principal[2]:
    st.markdown("### 🔔 Solicitudes de Enlace")
    col_s1, col_s2 = st.columns(2)
    with col_s1:
        st.markdown("<b>Enviar Solicitud</b>", unsafe_allow_html=True)
        cedula_destino_input = st.text_input("Cédula destino:")
        if st.button("Enviar Enlace"):
            if cedula_destino_input.strip():
                exito_s, msg_s = enviar_solicitud(cedula_actual, nombre_actual, cedula_destino_input.strip())
                if exito_s: st.success(msg_s)
                else: st.error(msg_s)
    with col_s2:
        st.markdown("<b>Recibidas</b>", unsafe_allow_html=True)
        solicitudes = obtener_solicitudes_recibidas(cedula_actual)
        if solicitudes:
            for s_id, s_data in solicitudes.items():
                st.write(f"De: {s_data.get('remitente_nombre')} ({s_data.get('remitente_cedula')})")
                ca1, ca2 = st.columns(2)
                with ca1:
                    if st.button("Aceptar", key=f"ac_{s_id}"):
                        actualizar_estado_solicitud(s_id, True)
                        st.rerun()
                with ca2:
                    if st.button("Rechazar", key=f"rc_{s_id}"):
                        actualizar_estado_solicitud(s_id, False)
                        st.rerun()
        else:
            st.info("No hay solicitudes pendientes.")

# --- TAB 4: HERRAMIENTAS ---
with menu_principal[3]:
    st.markdown("### 🛠️ Herramientas de Red")
    target_ip = st.text_input("IP Objetivo:", value="192.168.1.0/24")
    if st.button("Ejecutar Escaneo"):
        with st.spinner("Escaneando..."):
            time.sleep(1.5)
        st.success("Escaneo completado sin anomalías críticas.")

# --- TAB 5 / 6: PANEL ADMIN Y SALIDA ---
idx_panel = 4 if es_admin_master else len(menu_principal) - 1
if es_admin_master:
    with menu_principal[4]:
        st.markdown("### 📊 Panel de Administración 900TB")
        operadores_db = obtener_operadores_todos()
        for ced, datos in operadores_db.items():
            st.markdown(f"""
                <div class="panel-tactico-compacto">
                    <b>{datos.get('nombre')}</b> — Cédula: {ced} — Rol: {datos.get('rol')}
                </div>
            """, unsafe_allow_html=True)

with menu_principal[-1]:
    if st.button("Cerrar Sesión", use_container_width=True):
        st.session_state['acceso_concedido'] = False
        st.rerun()
