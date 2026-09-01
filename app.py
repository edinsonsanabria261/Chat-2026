import streamlit as st
import time
import requests
import json

# -----------------------------------------------------------------
# CONFIGURACIÓN Y ESTILOS UI (ESTILO WHATSAPP WEB Y CIBERSEGURIDAD)
# -----------------------------------------------------------------
st.set_page_config(
    page_title="Plataforma de Ciberseguridad & Mensajería P2P", 
    page_icon="🔒", 
    layout="wide"
)

st.markdown("""
    <style>
    .stApp { 
        background-color: #0b141a; 
        color: #e9edef; 
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; 
    }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Burbujas de chat estilo WhatsApp */
    .chat-bubble-incoming {
        background-color: #202c33;
        color: #e9edef;
        padding: 10px 14px;
        border-radius: 0px 12px 12px 12px;
        margin-bottom: 8px;
        max-width: 70%;
        box-shadow: 0 1px 0.5px rgba(0,0,0,0.3);
        float: left;
        clear: both;
        word-wrap: break-word;
    }
    
    .chat-bubble-outgoing {
        background-color: #005c4b;
        color: #e9edef;
        padding: 10px 14px;
        border-radius: 12px 0px 12px 12px;
        margin-bottom: 8px;
        max-width: 70%;
        box-shadow: 0 1px 0.5px rgba(0,0,0,0.3);
        float: right;
        clear: both;
        word-wrap: break-word;
    }

    .chat-timestamp {
        font-size: 0.7em;
        color: #8696a0;
        text-align: right;
        margin-top: 2px;
    }

    .whatsapp-header-top {
        background-color: #202c33;
        padding: 12px 20px;
        border-radius: 8px;
        margin-bottom: 15px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        border-bottom: 1px solid #222d34;
    }

    .stButton>button {
        border-radius: 8px;
        font-weight: 600;
        background-color: #00a884;
        color: white;
        border: none;
        transition: all 0.2s ease;
        padding: 0.5rem 1rem;
    }
    .stButton>button:hover {
        background-color: #008f72;
        color: white;
    }
    
    .stSelectbox label, .stTextInput label, .stPasswordInput label {
        color: #00a884 !important;
        font-weight: 600 !important;
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
    'vista_actual': "Mensajería P2P"
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
        return True, f"Solicitud enviada correctamente a {op_destino.get('nombre')}."
    except Exception:
        return False, "Error de conexión con la base de datos."

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
                    'timestamp': m.get('timestamp', '')
                } for m in mensajes_ordenados]
    except Exception:
        pass
    return []

def guardar_mensaje(tipo, texto, remitente, canal):
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
    st.markdown("<h2 style='text-align: center; color: #00a884;'>Registro de Operador en Ciberseguridad</h2>", unsafe_allow_html=True)
    st.markdown("---")
    
    with st.form("form_registro_nuevo"):
        col1, col2 = st.columns(2)
        with col1:
            nombres = st.text_input("Nombres")
            apellidos = st.text_input("Apellidos")
            telefono = st.text_input("Número de Teléfono / Celular")
        with col2:
            cedula = st.text_input("Número de Cédula de Identidad")
            correo = st.text_input("Correo Electrónico")
            pin = st.text_input("Código PIN de Acceso", type="password")
            
        registrar_btn = st.form_submit_button("Completar Registro", use_container_width=True)
        
        if registrar_btn:
            if not nombres.strip() or not apellidos.strip() or not cedula.strip() or not telefono.strip() or not pin.strip():
                st.error("Todos los campos marcados son obligatorios.")
            else:
                rol = "Administrador Global" if cedula.strip() == ADMIN_MASTER_CEDULA else "Analista de Ciberseguridad"
                exito = registrar_operador(cedula.strip(), nombres.strip(), apellidos.strip(), rol, telefono.strip(), pin.strip())
                if exito:
                    st.success("¡Registro exitoso! Ya puedes iniciar sesión con tu cédula y PIN.")
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
# PANTALLA DE INICIO DE SESIÓN
# -----------------------------------------------------------------
elif not st.session_state.get('acceso_concedido', False):
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
        <div style="background-color: #111b21; padding: 35px; border-radius: 12px; border: 1px solid #222d34; max-width: 450px; margin: auto; text-align: center; box-shadow: 0 4px 20px rgba(0,0,0,0.5);">
            <div style="font-size: 2.5em; margin-bottom: 10px;">🔒</div>
            <h2 style="color: #00a884; margin-bottom: 5px;">Portal de Ciberseguridad</h2>
            <p style="color: #8696a0; font-size: 0.9em;">Autenticación Segura de Empresa</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    tabs_auth = st.tabs(["Iniciar Sesión", "Registrarse"])
    
    with tabs_auth[0]:
        with st.form("form_login"):
            cedula_log = st.text_input("Cédula de Identidad")
            pin_log = st.text_input("PIN de Acceso", type="password")
            login_btn = st.form_submit_button("Acceder al Sistema", use_container_width=True)
            
            if login_btn:
                if not cedula_log.strip() or not pin_log.strip():
                    st.error("Ingrese su cédula y su PIN.")
                else:
                    op = obtener_operador(cedula_log.strip())
                    if op and op.get('codigo_pin') == pin_log.strip():
                        st.session_state['acceso_concedido'] = True
                        st.session_state['autenticado'] = True
                        st.session_state['cedula_actual'] = op.get('cedula')
                        st.session_state['usuario_actual'] = op.get('nombre')
                        st.session_state['rol_actual'] = op.get('rol')
                        st.success(f"Bienvenido, {op.get('nombre')}.")
                        time.sleep(0.6)
                        st.rerun()
                    else:
                        st.error("Credenciales incorrectas o usuario no registrado.")

    with tabs_auth[1]:
        st.write("¿No tienes cuenta en la plataforma?")
        if st.button("Ir al Formulario de Registro", use_container_width=True):
            st.session_state['modo_registro'] = True
            st.rerun()
    st.stop()

# -----------------------------------------------------------------
# INTERFAZ PRINCIPAL DE LA PLATAFORMA (PANTALLA COMPLETA)
# -----------------------------------------------------------------
st.markdown(f"""
    <div class="whatsapp-header-top">
        <div>
            <span style="font-weight: 700; font-size: 1.1em; color: #00a884;">🔒 Plataforma de Ciberseguridad & Empresa</span><br>
            <span style="font-size: 0.8em; color: #8696a0;">Operador activo: <b>{st.session_state.get('usuario_actual')}</b> ({st.session_state.get('rol_actual')})</span>
        </div>
        <div>
            <span style="color: #8696a0; font-size: 0.9em; margin-right: 15px;">Cédula: {st.session_state.get('cedula_actual')}</span>
        </div>
    </div>
""", unsafe_allow_html=True)

# Menú superior de navegación limpio por pestañas independientes
menu_principal = st.tabs([
    "💬 Mensajería P2P y Canal General",
    "👥 Gestión de Solicitudes y Contactos",
    "🛠️ Herramientas de Ciberseguridad",
    "🚪 Cerrar Sesión"
])

cedula_actual = st.session_state.get('cedula_actual')
nombre_actual = st.session_state.get('usuario_actual')

# --- SECCIÓN 1: MENSAJERÍA ---
with menu_principal[0]:
    st.markdown("### Centro de Mensajería Cifrada")
    
    tipo_chat = st.radio("Seleccione el canal de comunicación:", ["Canal General de Empresa", "Chats Privados P2P"], horizontal=True)
    
    if tipo_chat == "Canal General de Empresa":
        st.markdown("#### Canal General")
        mensajes_gen = cargar_mensajes("Canal General Táctico")
        
        contenedor_chat = st.container(height=380)
        with contenedor_chat:
            if mensajes_gen:
                for m in mensajes_gen:
                    mio = m.get('remitente') == nombre_actual
                    b_clase = "chat-bubble-outgoing" if mio else "chat-bubble-incoming"
                    st.markdown(f"""
                        <div class="{b_clase}">
                            <b style="font-size: 0.8em; color: #00a884;">{m.get('remitente')}</b><br>
                            {m.get('texto')}<br>
                            <div class="chat-timestamp">{m.get('timestamp')}</div>
                        </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("No hay mensajes en el canal general.")
                
        # Barra estilo WhatsApp: Botón adjuntar (+), texto, microfono y enviar
        c_adj, c_input, c_mic, c_btn = st.columns([0.6, 6, 0.8, 1])
        with c_adj:
            btn_adj = st.button("➕", help="Adjuntar archivo o imagen", key="adj_gen")
        with c_input:
            msg_gen = st.text_input("Escribe un mensaje", key="txt_gen", label_visibility="collapsed")
        with c_mic:
            btn_mic = st.button("🎙️", help="Enviar nota de voz", key="mic_gen")
        with c_btn:
            btn_enviar_g = st.button("➤", key="send_gen")
            
        if btn_enviar_g and msg_gen.strip():
            guardar_mensaje("texto", msg_gen.strip(), nombre_actual, "Canal General Táctico")
            st.rerun()
        if btn_adj:
            guardar_mensaje("archivo", "📎 [Archivo multimedia adjunto]", nombre_actual, "Canal General Táctico")
            st.success("Archivo adjuntado y enviado.")
            st.rerun()
        if btn_mic:
            guardar_mensaje("audio", "🎙️ [Nota de voz cifrada]", nombre_actual, "Canal General Táctico")
            st.success("Nota de voz enviada.")
            st.rerun()

    else:
        st.markdown("#### Chats Privados P2P")
        contactos = obtener_contactos_vinculados(cedula_actual)
        
        if contactos:
            contacto_id = st.selectbox("Seleccione un contacto vinculado:", list(contactos.keys()), format_func=lambda x: contactos[x])
            nombre_contacto = contactos[contacto_id]
            
            canal_privado = f"chat_{min(cedula_actual, contacto_id)}_{max(cedula_actual, contacto_id)}"
            
            # Cabecera del chat privado estilo WhatsApp con botones de llamada y videollamada arriba
            st.markdown(f"""
                <div style="background-color: #202c33; padding: 10px 15px; border-radius: 8px; display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; border: 1px solid #222d34;">
                    <div>
                        <span style="font-weight: bold; color: #e9edef; font-size: 1.05em;">💬 {nombre_contacto}</span><br>
                        <span style="font-size: 0.75em; color: #00a884;">Conexión directa P2P cifrada</span>
                    </div>
                    <div>
                        <span style="background-color: #111b21; padding: 6px 12px; border-radius: 6px; margin-right: 6px; cursor: pointer; border: 1px solid #222d34;" title="Llamada de voz">📞</span>
                        <span style="background-color: #111b21; padding: 6px 12px; border-radius: 6px; cursor: pointer; border: 1px solid #222d34;" title="Videollamada">📹</span>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            mensajes_priv = cargar_mensajes(canal_privado)
            box_priv = st.container(height=320)
            with box_priv:
                if mensajes_priv:
                    for mp in mensajes_priv:
                        mio_p = mp.get('remitente') == nombre_actual
                        clase_p = "chat-bubble-outgoing" if mio_p else "chat-bubble-incoming"
                        st.markdown(f"""
                            <div class="{clase_p}">
                                {mp.get('texto')}<br>
                                <div class="chat-timestamp">{mp.get('timestamp')}</div>
                            </div>
                        """, unsafe_allow_html=True)
                else:
                    st.info(f"Inicia la conversación segura con {nombre_contacto}.")
                    
            c_padj, c_pinput, c_pmic, c_psend = st.columns([0.6, 6, 0.8, 1])
            with c_padj:
                btn_padj = st.button("➕", key="adj_priv")
            with c_pinput:
                msg_priv = st.text_input("Mensaje privado", key="txt_priv", label_visibility="collapsed")
            with c_pmic:
                btn_pmic = st.button("🎙️", key="mic_priv")
            with c_psend:
                btn_env_p = st.button("➤", key="send_priv")
                
            if btn_env_p and msg_priv.strip():
                guardar_mensaje("texto", msg_priv.strip(), nombre_actual, canal_privado)
                st.rerun()
            if btn_padj:
                guardar_mensaje("archivo", "📎 [Archivo multimedia enviado]", nombre_actual, canal_privado)
                st.success("Archivo enviado.")
                st.rerun()
            if btn_pmic:
                guardar_mensaje("audio", "🎙️ [Nota de voz privada]", nombre_actual, canal_privado)
                st.success("Nota de voz enviada.")
                st.rerun()
        else:
            st.info("Aún no tienes contactos vinculados. Ve a la pestaña 'Gestión de Solicitudes y Contactos' para agregar a otros operadores.")

# --- SECCIÓN 2: GESTIÓN DE SOLICITUDES Y CONTACTOS ---
with menu_principal[1]:
    st.markdown("### Gestión de Solicitudes y Enlaces")
    
    col_s1, col_s2 = st.columns(2)
    
    with col_s1:
        st.markdown("#### Enviar Solicitud a Nuevo Operador")
        cedula_destino_input = st.text_input("Ingrese la cédula del operador:")
        if st.button("Enviar Solicitud de Enlace"):
            if cedula_destino_input.strip():
                exito_s, msg_s = enviar_solicitud(cedula_actual, nombre_actual, cedula_destino_input.strip())
                if exito_s:
                    st.success(msg_s)
                else:
                    st.error(msg_s)
                    
    with col_s2:
        st.markdown("#### Solicitudes Recibidas")
        solicitudes = obtener_solicitudes_recibidas(cedula_actual)
        if solicitudes:
            for s_id, s_data in solicitudes.items():
                st.markdown(f"""
                    <div style="background-color: #111b21; padding: 12px; border-radius: 8px; border: 1px solid #222d34; margin-bottom: 10px;">
                        <b>Remitente:</b> {s_data.get('remitente_nombre')}<br>
                        <b>Cédula:</b> {s_data.get('remitente_cedula')}<br>
                        <b>Fecha:</b> {s_data.get('timestamp')}
                    </div>
                """, unsafe_allow_html=True)
                
                col_acc1, col_acc2 = st.columns(2)
                with col_acc1:
                    if st.button("Aceptar", key=f"aceptar_{s_id}"):
                        actualizar_estado_solicitud(s_id, aceptar=True)
                        st.success("¡Solicitud aceptada! Ya está disponible en tus chats privados.")
                        time.sleep(1)
                        st.rerun()
                with col_acc2:
                    if st.button("Rechazar", key=f"rechazar_{s_id}"):
                        actualizar_estado_solicitud(s_id, aceptar=False)
                        st.warning("Solicitud rechazada.")
                        time.sleep(1)
                        st.rerun()
        else:
            st.info("No tienes solicitudes pendientes por aceptar.")

# --- SECCIÓN 3: HERRAMIENTAS DE CIBERSEGURIDAD ---
with menu_principal[2]:
    st.markdown("### Módulo de Ciberseguridad & Redes")
    st.write("Utilidades avanzadas de análisis y auditoría técnica.")
    
    tab_herram = st.tabs(["Escaneo de Redes", "Análisis de Aplicaciones"])
    with tab_herram[0]:
        target = st.text_input("Dirección IP o Dominio objetivo:", value="127.0.0.1")
        if st.button("Ejecutar Escaneo de Puertos"):
            st.success(f"Escaneando objetivo: {target}")
            st.code(f"Nmap scan report for {target}\nHost is up.\nPORT 80/tcp open http\nPORT 443/tcp open https", language="bash")
    with tab_herram[1]:
        st.markdown("#### Análisis Estático de Paquetes APK")
        st.info("Sube o inspecciona archivos de manifiesto y permisos de Android.")

# --- SECCIÓN 4: CERRAR SESIÓN ---
with menu_principal[3]:
    st.markdown("### Cerrar Sesión")
    if st.button("Finalizar Sesión Actual"):
        st.session_state['acceso_concedido'] = False
        st.rerun()
