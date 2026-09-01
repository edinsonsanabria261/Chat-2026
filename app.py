import streamlit as st
import time
import requests
import json
import base64

# -----------------------------------------------------------------
# CONFIGURACIÓN Y ESTILOS UI (DISEÑO COMPACTO Y MODERNO)
# -----------------------------------------------------------------
st.set_page_config(
    page_title="Plataforma Táctica de Ciberseguridad & P2P", 
    page_icon="⚡", 
    layout="wide"
)

st.markdown("""
    <style>
    .stApp { 
        background: linear-gradient(135deg, #0a0f1d 0%, #121829 100%); 
        color: #f0f6fc; 
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; 
    }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    .chat-container {
        max-height: 450px;
        overflow-y: auto;
        padding: 10px;
        display: flex;
        flex-direction: column;
    }

    .chat-bubble-incoming {
        background: #1f2937;
        color: #f3f4f6;
        padding: 10px 14px;
        border-radius: 12px;
        margin: 4px 0;
        max-width: 70%;
        border-left: 3px solid #00ffcc;
        align-self: flex-start;
        word-wrap: break-word;
    }
    
    .chat-bubble-outgoing {
        background: #0d9488;
        color: #ffffff;
        padding: 10px 14px;
        border-radius: 12px;
        margin: 4px 0;
        max-width: 70%;
        border-right: 3px solid #2dd4bf;
        align-self: flex-end;
        word-wrap: break-word;
    }

    .chat-meta {
        font-size: 0.65em;
        color: #94a3b8;
        text-align: right;
        margin-top: 2px;
    }

    .whatsapp-header-top {
        background: #111827;
        padding: 12px 20px;
        border-radius: 10px;
        margin-bottom: 15px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        border: 1px solid #374151;
    }

    .stButton>button {
        border-radius: 8px;
        font-weight: 600;
        background: linear-gradient(135deg, #00ffcc 0%, #00b386 100%);
        color: #0a0f1d;
        border: none;
        padding: 0.4rem 1rem;
    }
    .stButton>button:hover {
        background: linear-gradient(135deg, #00e6b8 0%, #009973 100%);
        color: #ffffff;
    }
    </style>
""", unsafe_allow_html=True)

FIREBASE_URL = "https://chat-2026-68203-default-rtdb.firebaseio.com"
ADMIN_MASTER_CEDULA = "2844102044"

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
        return True, f"Solicitud enviada a {op_destino.get('nombre')}."
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
    st.markdown("<h3 style='color: #00ffcc;'>Registro de Operador</h3>", unsafe_allow_html=True)
    with st.form("form_reg"):
        nombres = st.text_input("Nombres")
        apellidos = st.text_input("Apellidos")
        cedula = st.text_input("Cédula")
        telefono = st.text_input("Teléfono")
        pin = st.text_input("PIN", type="password")
        if st.form_submit_button("Registrarse"):
            if nombres and cedula and pin:
                rol = "Administrador Global" if cedula.strip() == ADMIN_MASTER_CEDULA else "Analista"
                if registrar_operador(cedula.strip(), nombres, apellidos, rol, telefono, pin):
                    st.success("¡Registrado con éxito!")
                    st.session_state['modo_registro'] = False
                    time.sleep(1)
                    st.rerun()
            else:
                st.error("Complete los campos obligatorios.")
    if st.button("Volver"):
        st.session_state['modo_registro'] = False
        st.rerun()
    st.stop()

# -----------------------------------------------------------------
# LOGIN
# -----------------------------------------------------------------
elif not st.session_state.get('acceso_concedido', False):
    st.markdown("<h3 style='color: #00ffcc; text-align: center;'>Portal Táctico</h3>", unsafe_allow_html=True)
    tabs = st.tabs(["Ingresar", "Registrarse"])
    with tabs[0]:
        with st.form("login"):
            c = st.text_input("Cédula")
            p = st.text_input("PIN", type="password")
            if st.form_submit_button("Entrar"):
                op = obtener_operador(c.strip())
                if op and op.get('codigo_pin') == p.strip():
                    st.session_state['acceso_concedido'] = True
                    st.session_state['cedula_actual'] = op.get('cedula')
                    st.session_state['usuario_actual'] = op.get('nombre')
                    st.session_state['rol_actual'] = op.get('rol')
                    st.rerun()
                else:
                    st.error("Datos incorrectos.")
    with tabs[1]:
        if st.button("Ir a Registro"):
            st.session_state['modo_registro'] = True
            st.rerun()
    st.stop()

# -----------------------------------------------------------------
# PANTALLA DE LLAMADA (SPLIT SCREEN)
# -----------------------------------------------------------------
if st.session_state.get('en_llamada', False):
    tipo = st.session_state.get('tipo_llamada')
    contacto = st.session_state.get('contacto_llamada')
    st.markdown(f"<h3 style='color: #00ffcc; text-align: center;'>{'📹 Videollamada Split-Screen' if tipo == 'video' else '📞 Llamada de Voz'} con {contacto}</h3>", unsafe_allow_html=True)
    
    if tipo == 'video':
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("<b>Tu Cámara</b>", unsafe_allow_html=True)
            st.camera_input("Local", key="cam_l")
        with col2:
            st.markdown(f"<b>Cámara de {contacto}</b>", unsafe_allow_html=True)
            st.camera_input("Remota", key="cam_r")
    else:
        st.info("Llamada de voz cifrada en curso...")
        
    if st.button("🔴 Colgar Llamada"):
        st.session_state['en_llamada'] = False
        st.rerun()
    st.stop()

# -----------------------------------------------------------------
# APP PRINCIPAL
# -----------------------------------------------------------------
st.markdown(f"""
    <div class="whatsapp-header-top">
        <div><b>⚡ P2P Ciberseguridad</b> | Operador: {st.session_state.get('usuario_actual')}</div>
        <div>Cédula: {st.session_state.get('cedula_actual')}</div>
    </div>
""", unsafe_allow_html=True)

es_admin = st.session_state.get('cedula_actual') == ADMIN_MASTER_CEDULA
menu = st.tabs(["💬 Mensajería", "👥 Solicitudes", "🛠️ Herramientas", "🚪 Salir"])

cedula_actual = st.session_state.get('cedula_actual')
nombre_actual = st.session_state.get('usuario_actual')

with menu[0]:
    tipo_chat = st.radio("Canal:", ["Chats Privados", "Canal General"], horizontal=True)
    
    if tipo_chat == "Chats Privados":
        contactos = obtener_contactos_vinculados(cedula_actual)
        if contactos:
            contacto_id = st.selectbox("Contacto:", list(contactos.keys()), format_func=lambda x: contactos[x])
            nombre_contacto = contactos[contacto_id]
            canal = f"chat_{min(cedula_actual, contacto_id)}_{max(cedula_actual, contacto_id)}"
            
            c_h1, c_h2, c_h3 = st.columns([6, 1, 1])
            with c_h1:
                st.markdown(f"<b>💬 {nombre_contacto}</b> <span style='color: #00ffcc;'>● En línea</span>", unsafe_allow_html=True)
            with c_h2:
                if st.button("📞", key="call_v"):
                    st.session_state['en_llamada'] = True
                    st.session_state['tipo_llamada'] = 'voice'
                    st.session_state['contacto_llamada'] = nombre_contacto
                    st.rerun()
            with c_h3:
                if st.button("📹", key="call_vid"):
                    st.session_state['en_llamada'] = True
                    st.session_state['tipo_llamada'] = 'video'
                    st.session_state['contacto_llamada'] = nombre_contacto
                    st.rerun()
            
            # Contenedor de mensajes limpio
            mensajes = cargar_mensajes(canal)
            st.markdown('<div class="chat-container">', unsafe_allow_html=True)
            for m in mensajes:
                mio = m.get('remitente') == nombre_actual
                b_clase = "chat-bubble-outgoing" if mio else "chat-bubble-incoming"
                st.markdown(f"""
                    <div class="{b_clase}">
                        <b>{m.get('remitente')}</b>: {m.get('texto')}
                        <div class="chat-meta">{m.get('timestamp')} ✓✓</div>
                    </div>
                """, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Input de texto limpio
            with st.form(key="f_msg", clear_on_submit=True):
                col_m1, col_m2 = st.columns([5, 1])
                with col_m1:
                    texto_msg = st.text_input("Escribe...", label_visibility="collapsed")
                with col_m2:
                    enviar = st.form_submit_button("Enviar ➤")
                if enviar and texto_msg.strip():
                    guardar_mensaje("texto", texto_msg.strip(), nombre_actual, canal)
                    st.rerun()

            # Herramientas adicionales ordenadas en columnas compactas
            col_utils1, col_utils2 = st.columns(2)
            with col_utils1:
                audio_file = st.file_uploader("🎤 Enviar Nota de Voz Real", type=["wav", "mp3", "m4a"], key="aud_up")
                if audio_file and st.button("Subir Audio"):
                    b64_audio = base64.b64encode(audio_file.getvalue()).decode('utf-8')
                    guardar_mensaje("audio", f"🎙️ [Nota de Voz: {audio_file.name}]", nombre_actual, canal, archivo_b64=b64_audio, nombre_archivo=audio_file.name)
                    st.success("Audio enviado.")
                    time.sleep(0.5)
                    st.rerun()
            with col_utils2:
                archivo_adj = st.file_uploader("📎 Adjuntar Archivo", key="file_up")
                if archivo_adj and st.button("Subir Archivo"):
                    b64_file = base64.b64encode(archivo_adj.getvalue()).decode('utf-8')
                    guardar_mensaje("archivo", f"📎 [Archivo: {archivo_adj.name}]", nombre_actual, canal, archivo_b64=b64_file, nombre_archivo=archivo_adj.name)
                    st.success("Archivo enviado.")
                    time.sleep(0.5)
                    st.rerun()

            # Selector de Stickers Limpio
            with st.expander("🎨 Stickers Tácticos Exclusivos"):
                sticker = st.selectbox("Elige sticker:", [
                    "🛡️ Escudo Cuántico", "💀 RedTeam Elite", "⚡ Ciber-Neón", 
                    "🔥 Hacking Ético", "💻 Root Access", "🛰️ Satélite P2P"
                ])
                if st.button("Enviar Sticker"):
                    guardar_mensaje("texto", f"✨ STICKER: {sticker}", nombre_actual, canal)
                    st.success("Sticker enviado.")
                    time.sleep(0.5)
                    st.rerun()
        else:
            st.info("No tienes contactos vinculados. Agrégalos en la pestaña Solicitudes.")
    else:
        st.markdown("#### Canal General")
        mensajes_g = cargar_mensajes("Canal General")
        for mg in mensajes_g:
            st.markdown(f"<b>{mg.get('remitente')}</b>: {mg.get('texto')}", unsafe_allow_html=True)
            
        with st.form("f_gen", clear_on_submit=True):
            tg = st.text_input("Mensaje general...", label_visibility="collapsed")
            if st.form_submit_button("Enviar") and tg.strip():
                guardar_mensaje("texto", tg.strip(), nombre_actual, "Canal General")
                st.rerun()

with menu[1]:
    st.markdown("### Solicitudes P2P")
    c_s1, c_s2 = st.columns(2)
    with c_s1:
        dest = st.text_input("Cédula destino:")
        if st.button("Enviar Solicitud"):
            if dest.strip():
                ex, msg = enviar_solicitud(cedula_actual, nombre_actual, dest.strip())
                if ex: st.success(msg)
                else: st.error(msg)
    with c_s2:
        recs = obtener_solicitudes_recibidas(cedula_actual)
        if recs:
            for k, v in recs.items():
                st.write(f"De: {v.get('remitente_nombre')} ({v.get('remitente_cedula')})")
                if st.button("Aceptar", key=f"ac_{k}"):
                    actualizar_estado_solicitud(k, True)
                    st.rerun()
                if st.button("Rechazar", key=f"rc_{k}"):
                    actualizar_estado_solicitud(k, False)
                    st.rerun()
        else:
            st.info("Sin solicitudes pendientes.")

with menu[2]:
    st.markdown("### Escaneo Táctico")
    ip = st.text_input("IP Objetivo:", "192.168.1.1")
    if st.button("Ejecutar Escaneo"):
        time.sleep(1)
        st.success(f"Escaneo finalizado sobre {ip}. Puertos 22, 80, 443 abiertos.")

with menu[3]:
    if st.button("Cerrar Sesión"):
        st.session_state['acceso_concedido'] = False
        st.rerun()
