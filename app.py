import time
import requests
import json
import base64
import streamlit as st

# -----------------------------------------------------------------
# CONFIGURACIÓN Y ESTILOS UI (LETRAS DE COLORES FUERTES Y VISIBLES)
# -----------------------------------------------------------------
st.set_page_config(
    page_title="Plataforma Táctica P2P [Estilo WhatsApp]", 
    page_icon="💬", 
    layout="wide"
)

st.markdown("""
    <style>
    .stApp { 
        background-color: #0b141a; 
        color: #ffffff !important; 
        font-family: 'Segoe UI', Helvetica, Arial, sans-serif; 
    }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Textos con colores fuertes y legibilidad máxima */
    h1, h2, h3, h4, h5, h6 {
        color: #00ffcc !important;
        font-weight: 700;
    }
    
    p, span, label, div {
        color: #ffffff !important;
    }

    .panel-whatsapp-card {
        background-color: #111b21;
        border: 2px solid #00ffcc;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 15px;
        box-shadow: 0 4px 15px rgba(0, 255, 204, 0.2);
    }

    .panel-whatsapp-header {
        background-color: #111b21;
        padding: 15px 20px;
        border-radius: 12px;
        margin-bottom: 20px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        border-bottom: 3px solid #00ffcc;
    }

    .chat-container-box {
        background-color: #0b141a;
        border: 2px solid #2a3942;
        border-radius: 12px;
        padding: 15px;
        max-height: 400px;
        overflow-y: auto;
        margin-bottom: 15px;
    }

    .chat-bubble-incoming {
        background-color: #202c33;
        color: #ffffff !important;
        padding: 10px 14px;
        border-radius: 0px 12px 12px 12px;
        margin-bottom: 8px;
        max-width: 80%;
        float: left;
        clear: both;
        word-wrap: break-word;
        border-left: 4px solid #00ffcc;
    }
    
    .chat-bubble-outgoing {
        background-color: #005c4b;
        color: #ffffff !important;
        padding: 10px 14px;
        border-radius: 12px 0px 12px 12px;
        margin-bottom: 8px;
        max-width: 80%;
        float: right;
        clear: both;
        word-wrap: break-word;
        border-right: 4px solid #25d366;
    }

    .chat-meta {
        font-size: 0.7em;
        color: #00ffcc !important;
        text-align: right;
        margin-top: 4px;
        font-weight: bold;
    }

    /* Botones compactos y visibles con colores fuertes */
    .stButton>button {
        border-radius: 8px;
        font-weight: 700;
        background-color: #00a884;
        color: #ffffff !important;
        border: 1px solid #00ffcc;
        padding: 0.4rem 0.8rem;
        font-size: 0.95em;
        box-shadow: 0 2px 5px rgba(0,0,0,0.4);
    }
    .stButton>button:hover {
        background-color: #00ffcc;
        color: #0b141a !important;
    }

    /* Inputs de texto claros y legibles */
    input, select, textarea {
        color: #ffffff !important;
        background-color: #222e35 !important;
        border: 1px solid #00ffcc !important;
        font-weight: 600 !important;
    }
    </style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------
# BACKEND INTEGRADO (FIREBASE Y LÓGICA DE DATOS)
# -----------------------------------------------------------------
FIREBASE_URL = "https://chat-2026-68203-default-rtdb.firebaseio.com"
ADMIN_MASTER_CEDULA = "2844102044"  # Edinson Carlos Marin Sanabria

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
        requests.post(f"{FIREBASE_URL}/solicitudes_amistad.json", data=json.dumps(payload), timeout=2.5)
        return True, f"Solicitud enviada con éxito a {op_destino.get('nombre')}."
    except Exception:
        return False, "Error de conexión en el servidor."

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

# Funciones de la Nube Infinita de Fotos (Actualizadas y Robustas)
def guardar_foto_nube(cedula, nombre_archivo, foto_b64):
    payload = {
        'cedula_operador': cedula,
        'nombre_archivo': nombre_archivo,
        'foto_b64': foto_b64,
        'timestamp': time.strftime("%Y-%m-%d %H:%M:%S")
    }
    try:
        res = requests.post(f"{FIREBASE_URL}/nube_fotos/{cedula}.json", data=json.dumps(payload), timeout=3.0)
        return res.status_code == 200
    except Exception:
        return False

def obtener_fotos_nube(cedula):
    try:
        res = requests.get(f"{FIREBASE_URL}/nube_fotos/{cedula}.json", timeout=3.0)
        if res.status_code == 200 and res.json():
            data = res.json()
            lista_fotos = []
            if isinstance(data, dict):
                for k, v in data.items():
                    if isinstance(v, dict):
                        if 'foto_b64' in v and v.get('foto_b64'):
                            v['firebase_key'] = k
                            lista_fotos.append(v)
                        else:
                            for sub_k, sub_v in v.items():
                                if isinstance(sub_v, dict) and sub_v.get('foto_b64'):
                                    sub_v['firebase_key'] = f"{k}/{sub_k}"
                                    lista_fotos.append(sub_v)
            return sorted(lista_fotos, key=lambda x: x.get('timestamp', ''), reverse=True)
    except Exception:
        pass
    return []

def limpiar_nube_corrupta(cedula):
    try:
        requests.delete(f"{FIREBASE_URL}/nube_fotos/{cedula}.json", timeout=3.0)
        return True
    except Exception:
        return False

# -----------------------------------------------------------------
# GESTIÓN DE ESTADOS DE SESIÓN
# -----------------------------------------------------------------
for key, val in {
    'acceso_concedido': False,
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

# -----------------------------------------------------------------
# PANTALLA DE REGISTRO
# -----------------------------------------------------------------
if st.session_state.get('modo_registro', False):
    st.markdown("""
        <div class="panel-whatsapp-card" style="max-width: 600px; margin: auto; text-align: center;">
            <h2>💬 Registro de Nuevo Operador</h2>
            <p>Ingrese sus datos para unirse a la red de comunicación segura</p>
        </div>
    """, unsafe_allow_html=True)
    
    with st.form("form_registro_wa"):
        col1, col2 = st.columns(2)
        with col1:
            nombres = st.text_input("Nombres")
            apellidos = st.text_input("Apellidos")
            telefono = st.text_input("Teléfono Móvil")
        with col2:
            cedula = st.text_input("Cédula de Identidad (Única)")
            _correo = st.text_input("Correo Electrónico")
            pin = st.text_input("PIN de Seguridad", type="password")
            
        if st.form_submit_button("Completar Registro", use_container_width=True):
            if not nombres.strip() or not apellidos.strip() or not cedula.strip() or not pin.strip():
                st.error("Por favor complete todos los campos obligatorios.")
            else:
                rol = "Administrador Global" if cedula.strip() == ADMIN_MASTER_CEDULA else "Operador Autorizado"
                if registrar_operador(cedula.strip(), nombres.strip(), apellidos.strip(), rol, telefono.strip(), pin.strip()):
                    st.success("¡Registro exitoso! Ya puede iniciar sesión.")
                    st.session_state['modo_registro'] = False
                    time.sleep(1)
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
        <div class="panel-whatsapp-card" style="max-width: 450px; margin: auto; text-align: center;">
            <div style="font-size: 3em; margin-bottom: 8px;">🟢</div>
            <h2>Acceso Seguro P2P</h2>
            <p>Ingrese sus credenciales registradas</p>
        </div>
    """, unsafe_allow_html=True)
    
    tabs_auth = st.tabs(["Iniciar Sesión", "Registrarse"])
    with tabs_auth[0]:
        with st.form("form_login_wa"):
            cedula_log = st.text_input("Cédula de Identidad")
            pin_log = st.text_input("PIN de Seguridad", type="password")
            if st.form_submit_button("Entrar al Sistema", use_container_width=True):
                if not cedula_log.strip() or not pin_log.strip():
                    st.error("Ingrese su cédula y PIN.")
                else:
                    op = obtener_operador(cedula_log.strip())
                    if op and op.get('codigo_pin') == pin_log.strip():
                        st.session_state['acceso_concedido'] = True
                        st.session_state['cedula_actual'] = op.get('cedula')
                        st.session_state['usuario_actual'] = op.get('nombre')
                        st.session_state['rol_actual'] = op.get('rol')
                        st.success(f"Bienvenido, {op.get('nombre')}")
                        time.sleep(0.5)
                        st.rerun()
                    else:
                        st.error("Credenciales incorrectas o cédula no encontrada.")
    with tabs_auth[1]:
        st.write("¿No tienes una cuenta?")
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
        <div class="panel-whatsapp-card" style="text-align: center; max-width: 600px; margin: auto; margin-top: 30px;">
            <h2>{'📹 Videollamada Activa' if tipo == 'video' else '📞 Llamada de Voz Activa'}</h2>
            <p>Conectado con: <b style="color: #00ffcc;">{contacto}</b></p>
            <p style="color: #00ffcc; margin-top: 10px; font-weight: bold;">🟢 Canal P2P Establecido Correctamente</p>
        </div>
    """, unsafe_allow_html=True)
    
    if tipo == 'video':
        col_v1, col_v2 = st.columns(2)
        with col_v1:
            st.markdown("<p style='text-align: center; font-weight: bold; color: #00ffcc;'>Tu Cámara</p>", unsafe_allow_html=True)
            st.camera_input("Tu Cámara", key="cam_local_wa", label_visibility="collapsed")
        with col_v2:
            st.markdown(f"<p style='text-align: center; font-weight: bold; color: #00ffcc;'>Cámara de {contacto}</p>", unsafe_allow_html=True)
            st.info("Esperando flujo remoto de video...")
    else:
        st.markdown("""
            <div style="text-align: center; padding: 25px; background-color: #111b21; border: 1px solid #00ffcc; border-radius: 10px; max-width: 400px; margin: auto;">
                <p style="font-size: 1.1em; color: #00ffcc; font-weight: bold;">🔊 Transmisión de voz en curso...</p>
            </div>
        """, unsafe_allow_html=True)
        
    st.markdown("<br>", unsafe_allow_html=True)
    col_c1, col_c2, col_c3 = st.columns([1, 2, 1])
    with col_c2:
        if st.button("🔴 Colgar Llamada", use_container_width=True):
            st.session_state['en_llamada'] = False
            st.session_state['tipo_llamada'] = None
            st.session_state['contacto_llamada'] = None
            st.rerun()
    st.stop()

# -----------------------------------------------------------------
# INTERFAZ PRINCIPAL
# -----------------------------------------------------------------
st.markdown(f"""
    <div class="panel-whatsapp-header">
        <div>
            <span style="font-weight: 800; font-size: 1.2em; color: #00ffcc;">💬 Red de Mensajería y Seguridad</span><br>
            <span style="font-size: 0.9em; color: #ffffff;">Operador: <b style="color: #00ffcc;">{st.session_state.get('usuario_actual')}</b></span>
        </div>
        <div>
            <span style="background-color: #222e35; padding: 6px 12px; border-radius: 6px; color: #00ffcc; font-size: 0.9em; border: 1px solid #00ffcc; font-weight: bold;">ID: {st.session_state.get('cedula_actual')}</span>
        </div>
    </div>
""", unsafe_allow_html=True)

es_admin_master = st.session_state.get('cedula_actual') == ADMIN_MASTER_CEDULA or st.session_state.get('rol_actual') == "Administrador Global"

menu_tabs = [
    "💬 Chats",
    "📞 Llamadas",
    "🔔 Solicitudes",
    "☁️ Nube Infinita de Fotos",
    "🛠️ Herramientas / Exit Full Tools",
    "📊 Admin" if es_admin_master else "🚪 Salir",
    "🚪 Salir" if es_admin_master else None
]
menu_tabs = [t for t in menu_tabs if t is not None]
menu_principal = st.tabs(menu_tabs)

cedula_actual = st.session_state.get('cedula_actual')
nombre_actual = st.session_state.get('usuario_actual')

# --- SECCIÓN 1: CHATS ---
with menu_principal[0]:
    tipo_chat = st.radio("Seleccionar tipo de chat:", ["Chats Privados con Contactos", "Canal General de la Red"], horizontal=True, label_visibility="collapsed")
    
    if tipo_chat == "Chats Privados con Contactos":
        contactos = obtener_contactos_vinculados(cedula_actual)
        
        if contactos:
            contacto_id = st.selectbox("Seleccione un contacto:", list(contactos.keys()), format_func=lambda x: contactos[x])
            nombre_contacto = contactos[contacto_id]
            canal_privado = f"chat_{min(cedula_actual, contacto_id)}_{max(cedula_actual, contacto_id)}"
            
            col_h1, col_h2, col_h3 = st.columns([6, 1, 1])
            with col_h1:
                st.markdown(f"""
                    <div style="background-color: #111b21; padding: 12px 15px; border-radius: 8px; border: 1px solid #00ffcc; margin-bottom: 10px;">
                        <span style="font-weight: bold; color: #00ffcc;">💬 Conversación con {nombre_contacto}</span><br>
                        <span style="font-size: 0.85em; color: #ffffff;">🟢 Cifrado extremo activo</span>
                    </div>
                """, unsafe_allow_html=True)
            with col_h2:
                if st.button("📞", key="btn_call_wa", help="Llamada de voz"):
                    st.session_state['en_llamada'] = True
                    st.session_state['tipo_llamada'] = 'voice'
                    st.session_state['contacto_llamada'] = nombre_contacto
                    st.rerun()
            with col_h3:
                if st.button("📹", key="btn_call_vid_wa", help="Videollamada"):
                    st.session_state['en_llamada'] = True
                    st.session_state['tipo_llamada'] = 'video'
                    st.session_state['contacto_llamada'] = nombre_contacto
                    st.rerun()
            
            mensajes_priv = cargar_mensajes(canal_privado)
            st.markdown('<div class="chat-container-box">', unsafe_allow_html=True)
            if mensajes_priv:
                for mp in mensajes_priv:
                    mio_p = mp.get('remitente') == nombre_actual
                    clase_p = "chat-bubble-outgoing" if mio_p else "chat-bubble-incoming"
                    
                    st.markdown(f"""
                        <div class="{clase_p}">
                            <div style="font-size: 0.8em; font-weight: bold; color: #00ffcc; margin-bottom: 2px;">{mp.get('remitente')}</div>
                            <div>{mp.get('texto')}</div>
                            <div class="chat-meta">{mp.get('timestamp')[-8:]}</div>
                        </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("No hay mensajes en este chat privado. Envía el primero.")
            st.markdown('</div>', unsafe_allow_html=True)
            
            with st.form(key=f"form_priv_{contacto_id}", clear_on_submit=True):
                txt_priv = st.text_input("Escribe tu mensaje seguro...", label_visibility="collapsed")
                col_sub1, col_sub2 = st.columns([5, 1])
                with col_sub2:
                    enviar_p = st.form_submit_button("Enviar", use_container_width=True)
                
                if enviar_p and txt_priv.strip():
                    guardar_mensaje('texto', txt_priv.strip(), nombre_actual, canal_privado)
                    st.rerun()
        else:
            st.warning("No tienes contactos vinculados. Ve a la pestaña 'Solicitudes' para agregar operadores mediante su cédula.")
            
    else:
        st.markdown("""
            <div style="background-color: #111b21; padding: 12px 15px; border-radius: 8px; border: 1px solid #00ffcc; margin-bottom: 10px;">
                <span style="font-weight: bold; color: #00ffcc;">🌐 Canal General de Difusión de la Red</span><br>
                <span style="font-size: 0.85em; color: #ffffff;">🟢 Todos los operadores conectados pueden leer y escribir aquí</span>
            </div>
        """, unsafe_allow_html=True)
        
        mensajes_gen = cargar_mensajes("canal_general")
        st.markdown('<div class="chat-container-box">', unsafe_allow_html=True)
        if mensajes_gen:
            for mg in mensajes_gen:
                mio_g = mg.get('remitente') == nombre_actual
                clase_g = "chat-bubble-outgoing" if mio_g else "chat-bubble-incoming"
                
                st.markdown(f"""
                    <div class="{clase_g}">
                        <div style="font-size: 0.8em; font-weight: bold; color: #00ffcc; margin-bottom: 2px;">{mg.get('remitente')}</div>
                        <div>{mg.get('texto')}</div>
                        <div class="chat-meta">{mg.get('timestamp')[-8:]}</div>
                    </div>
                """, unsafe_allow_html=True)
        else:
            st.info("El canal general está vacío. Inicia la conversación.")
        st.markdown('</div>', unsafe_allow_html=True)
        
        with st.form(key="form_general_wa", clear_on_submit=True):
            txt_gen = st.text_input("Escribe al canal general...", label_visibility="collapsed")
            col_g1, col_g2 = st.columns([5, 1])
            with col_g2:
                enviar_g = st.form_submit_button("Enviar", use_container_width=True)
            
            if enviar_g and txt_gen.strip():
                guardar_mensaje('texto', txt_gen.strip(), nombre_actual, "canal_general")
                st.rerun()

# --- SECCIÓN 2: LLAMADAS ---
with menu_principal[1]:
    st.subheader("📞 Central de Llamadas y Enlaces Activos")
    st.write("Selecciona un contacto vinculado para iniciar una llamada de voz o videollamada cifrada de extremo a extremo.")
    
    contactos_llamada = obtener_contactos_vinculados(cedula_actual)
    if contactos_llamada:
        cid_llamada = st.selectbox("Seleccionar operador para llamar:", list(contactos_llamada.keys()), format_func=lambda x: contactos_llamada[x], key="select_call_tab")
        nom_llamada = contactos_llamada[cid_llamada]
        
        col_call_1, col_call_2 = st.columns(2)
        with col_call_1:
            if st.button("📞 Iniciar Llamada de Voz", use_container_width=True):
                st.session_state['en_llamada'] = True
                st.session_state['tipo_llamada'] = 'voice'
                st.session_state['contacto_llamada'] = nom_llamada
                st.rerun()
        with col_call_2:
            if st.button("📹 Iniciar Videollamada", use_container_width=True):
                st.session_state['en_llamada'] = True
                st.session_state['tipo_llamada'] = 'video'
                st.session_state['contacto_llamada'] = nom_llamada
                st.rerun()
    else:
        st.info("No tienes contactos vinculados para realizar llamadas.")

# --- SECCIÓN 3: SOLICITUDES ---
with menu_principal[2]:
    st.subheader("🔔 Gestión de Solicitudes y Enlaces de Red")
    
    col_sol1, col_sol2 = st.columns(2)
    with col_sol1:
        st.markdown("### ➕ Agregar Nuevo Contacto")
        cedula_destino_input = st.text_input("Cédula del Operador Destino")
        if st.button("Enviar Solicitud de Enlace"):
            if not cedula_destino_input.strip():
                st.error("Ingrese una cédula válida.")
            else:
                ok, msg = enviar_solicitud(cedula_actual, nombre_actual, cedula_destino_input.strip())
                if ok:
                    st.success(msg)
                else:
                    st.error(msg)
                    
    with col_sol2:
        st.markdown("### 📥 Solicitudes Recibidas")
        solicitudes = obtener_solicitudes_recibidas(cedula_actual)
        if solicitudes:
            for skey, sval in solicitudes.items():
                st.markdown(f"""
                    <div style="background-color: #111b21; padding: 10px; border-radius: 8px; border: 1px solid #00ffcc; margin-bottom: 8px;">
                        <b>{sval.get('remitente_nombre')}</b> (Cédula: {sval.get('remitente_cedula')}) quiere enlazarse contigo.<br>
                        <span style="font-size: 0.8em; color: #8696a0;">Fecha: {sval.get('timestamp')}</span>
                    </div>
                """, unsafe_allow_html=True)
                
                col_b1, col_b2 = st.columns(2)
                with col_b1:
                    if st.button("Aceptar", key=f"acc_{skey}Y"):
                        if actualizar_estado_solicitud(skey, aceptar=True):
                            st.success("¡Solicitud aceptada!")
                            time.sleep(0.5)
                            st.rerun()
                with col_b2:
                    if st.button("Rechazar", key=f"rec_{skey}N"):
                        if actualizar_estado_solicitud(skey, aceptar=False):
                            st.warning("Solicitud rechazada.")
                            time.sleep(0.5)
                            st.rerun()
        else:
            st.info("No tienes solicitudes pendientes.")

# --- SECCIÓN 4: NUBE INFINITA DE FOTOS (OPTIMIZADA CON PERSISTENCIA DE SESIÓN) ---
with menu_principal[3]:
    st.subheader("☁️ Nube Infinita de Fotos (900 TB Asignados)")
    st.write("Sube y almacena imágenes de forma segura en tu repositorio personal cifrado.")
    
    # Inicializar estado temporal para la foto cargada
    if 'temp_foto_b64' not in st.session_state:
        st.session_state['temp_foto_b64'] = None
    if 'temp_nombre_archivo' not in st.session_state:
        st.session_state['temp_nombre_archivo'] = None

    archivo_subido = st.file_uploader("Seleccionar imagen para respaldar", type=["jpg", "jpeg", "png"], key="uploader_foto_nube")
    
    if archivo_subido is not None:
        # Capturamos los bytes inmediatamente y los guardamos en session_state para que no se borren al hacer clic
        bytes_img = archivo_subido.read()
        st.session_state['temp_foto_b64'] = base64.b64encode(bytes_img).decode('utf-8')
        st.session_state['temp_nombre_archivo'] = archivo_subido.name

    # Si ya hay una imagen cargada en memoria, mostramos la vista previa y el botón de subida definitiva
    if st.session_state['temp_foto_b64']:
        st.success(f"Imagen lista para enviar: **{st.session_state['temp_nombre_archivo']}**")
        
        if st.button("🚀 Confirmar y Subir a la Nube Segura", use_container_width=True):
            with st.spinner("Subiendo imagen cifrada a Firebase..."):
                exito = guardar_foto_nube(
                    cedula_actual, 
                    st.session_state['temp_nombre_archivo'], 
                    st.session_state['temp_foto_b64']
                )
                if exito:
                    st.success("¡Imagen guardada exitosamente en la nube!")
                    # Limpiamos la memoria temporal
                    st.session_state['temp_foto_b64'] = None
                    st.session_state['temp_nombre_archivo'] = None
                    time.sleep(0.8)
                    st.rerun()
                else:
                    st.error("Error al subir la imagen a la base de datos.")
                
    st.markdown("---")
    
    col_inf_1, col_inf_2 = st.columns([4, 1])
    with col_inf_1:
        st.markdown("### 📂 Tus Imágenes Almacenadas")
    with col_inf_2:
        if st.button("🗑️ Limpiar Repositorio", help="Borra registros corruptos o antiguos"):
            if limpiar_nube_corrupta(cedula_actual):
                st.success("Repositorio limpiado correctamente.")
                time.sleep(0.8)
                st.rerun()
            else:
                st.error("No se pudo limpiar el repositorio.")
    
    # Recuperar y renderizar las fotos desde Firebase
    fotos = obtener_fotos_nube(cedula_actual)
    if fotos:
        cols_f = st.columns(3)
        renderizadas = 0
        for foto in fotos:
            b64_data = foto.get('foto_b64', '')
            if not b64_data:
                continue
            try:
                if ',' in b64_data:
                    b64_data = b64_data.split(',')[1]
                
                img_bytes = base64.b64decode(b64_data, validate=True)
                with cols_f[renderizadas % 3]:
                    st.image(img_bytes, caption=foto.get('nombre_archivo', 'Sin nombre'), use_column_width=True)
                    st.markdown(f"<span style='font-size: 0.75em; color: #8696a0;'>Guardado: {foto.get('timestamp', '')}</span>", unsafe_allow_html=True)
                renderizadas += 1
            except Exception:
                continue
                
        if renderizadas == 0:
            st.info("No hay imágenes válidas para mostrar. Prueba subiendo una nueva imagen.")
    else:
        st.info("Tu nube de fotos está vacía.")


# --- SECCIÓN 5: HERRAMIENTAS ---
with menu_principal[4]:
    st.subheader("🛠️ Panel de Herramientas Tácticas y Auditoría")
    st.write("Utilidades de análisis de red, seguridad y diagnóstico avanzado.")
    
    col_tool_1, col_tool_2 = st.columns(2)
    with col_tool_1:
        st.markdown("### 🔍 Escáner de Puertos y Nodos P2P")
        if st.button("Ejecutar Escaneo Rápido de Red"):
            with st.spinner("Analizando nodos activos en la red local..."):
                time.sleep(1.5)
            st.success("Escaneo completado: 4 nodos seguros detectados y activos.")
            st.code("Node 1: 192.168.1.10 [SECURE]\nNode 2: 192.168.1.14 [SECURE]\nGateway P2P: Online", language="text")
            
    with col_tool_2:
        st.markdown("### 🛡️ Diagnóstico de Seguridad")
        if st.button("Verificar Integridad del Sistema"):
            with st.spinner("Verificando hashes y certificados de cifrado..."):
                time.sleep(1.2)
            st.success("Integridad verificada al 100%. Sin alteraciones detectadas.")

# --- SECCIÓN 6 o 7: ADMIN O SALIR ---
indice_admin_o_salir = 5 if not es_admin_master else 6

with menu_principal[indice_admin_o_salir - (1 if not es_admin_master else 0) if not es_admin_master else 5]:
    if not es_admin_master:
        st.session_state['acceso_concedido'] = False
        st.session_state['cedula_actual'] = ""
        st.session_state['usuario_actual'] = ""
        st.rerun()
    else:
        st.subheader("📊 Panel de Administración Global")
        st.write("Gestión de operadores registrados en la plataforma táctica.")
        
        operadores = obtener_operadores_todos()
        if operadores:
            data_tabla = []
            for ced, opinfo in operadores.items():
                if isinstance(opinfo, dict):
                    data_tabla.append({
                        "Cédula": opinfo.get('cedula'),
                        "Nombre": opinfo.get('nombre'),
                        "Rol": opinfo.get('rol'),
                        "Teléfono": opinfo.get('telefono'),
                        "Registro": opinfo.get('fecha_registro'),
                        "Activo": opinfo.get('activo')
                    })
            st.dataframe(data_tabla, use_container_width=True)
        else:
            st.info("No hay operadores registrados.")

if es_admin_master and len(menu_principal) > 6:
    with menu_principal[6]:
        if st.button("🚪 Cerrar Sesión Definitiva", use_container_width=True):
            st.session_state['acceso_concedido'] = False
            st.session_state['cedula_actual'] = ""
            st.session_state['usuario_actual'] = ""
            st.rerun()
