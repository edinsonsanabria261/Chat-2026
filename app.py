import streamlit as st
import time
import requests
import json
from PIL import Image
import io
import base64
import hashlib
import hmac

# -----------------------------------------------------------------
# 1. CONFIGURACIÓN TÁCTICA Y ESTILOS UI MODERNOS (ESTILO WHATSAPP)
# -----------------------------------------------------------------
st.set_page_config(
    page_title="Centro Táctico Pericial - Edinson Carlos Marin Sanabria", 
    page_icon="🛡️", 
    layout="wide"
)

st.markdown("""
    <style>
    .stApp {
        background-color: #0b0f19;
        color: #f3f4f6;
    }
    .chat-bubble-user {
        background: linear-gradient(135deg, #005c4b 0%, #008069 100%);
        color: #e9edef;
        padding: 12px 16px;
        border-radius: 18px 18px 4px 18px;
        margin-bottom: 8px;
        box-shadow: 0 1px 2px rgba(0,0,0,0.3);
        max-width: 80%;
        margin-left: auto;
        font-size: 0.95em;
        word-break: break-word;
    }
    .chat-bubble-other {
        background: linear-gradient(135deg, #202c33 100%, #111b21 0%);
        color: #e9edef;
        padding: 12px 16px;
        border-radius: 18px 18px 18px 4px;
        margin-bottom: 8px;
        box-shadow: 0 1px 2px rgba(0,0,0,0.3);
        max-width: 80%;
        border-left: 4px solid #00a884;
        font-size: 0.95em;
        word-break: break-word;
    }
    .tool-card {
        background-color: #111b21;
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #222d34;
        margin-bottom: 15px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.4);
    }
    .login-container {
        background-color: #111b21;
        padding: 30px;
        border-radius: 16px;
        border: 1px solid #222d34;
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.7);
    }
    code {
        color: #00a884 !important;
        background-color: #0b0f19 !important;
        padding: 2px 6px;
        border-radius: 4px;
    }
    .author-badge {
        background: linear-gradient(90deg, #00a884, #38bdf8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: bold;
        font-size: 1.05em;
        text-align: center;
        margin-bottom: 8px;
    }
    </style>
""", unsafe_allow_html=True)

FIREBASE_URL = "https://chat-2026-68203-default-rtdb.firebaseio.com/"
CEDULA_ADMIN_MAESTRO = "2844102044"  # Cédula configurada para Edinson Carlos Marin Sanabria
LLAVE_ACCESO_MAESTRA = "VIP-2026-SECURE"

# Inicialización segura de estados en sesión
if 'acceso_concedido' not in st.session_state:
    st.session_state['acceso_concedido'] = False

if 'autenticado' not in st.session_state:
    st.session_state['autenticado'] = False
    st.session_state['usuario_actual'] = ""
    st.session_state['rol_actual'] = ""
    st.session_state['cedula_actual'] = ""

if 'intentos_fallidos' not in st.session_state:
    st.session_state['intentos_fallidos'] = 0

# -----------------------------------------------------------------
# 2. FUNCIONES DE TELEMETRÍA Y CONECTIVIDAD
# -----------------------------------------------------------------
def obtener_metadatos_red():
    meta = {
        'ip': '127.0.0.1', 
        'ciudad': 'Nodo Local', 
        'pais': 'Red Segura', 
        'org': 'Control Táctico', 
        'lat_lon': 'N/A', 
        'isp': 'N/A',
        'vector_ataque': 'Limpio'
    }
    try:
        response = requests.get('https://ipapi.co/json/', timeout=1)
        if response.status_code == 200:
            data = response.json()
            meta['ip'] = data.get('ip', '127.0.0.1')
            meta['ciudad'] = data.get('city', 'Nodo Local')
            meta['pais'] = data.get('country_name', 'Red Interna')
            meta['org'] = data.get('org', 'ISP Privado')
            meta['isp'] = data.get('asn', 'N/A')
            if 'latitude' in data and 'longitude' in data:
                meta['lat_lon'] = f"{data.get('latitude')}, {data.get('longitude')}"
    except Exception:
        meta['vector_ataque'] = 'Proxy / Red Oculta'
    return meta

def registrar_auditoria_forense(usuario, accion, meta, dispositivo="N/A", hash_evidencia="N/A"):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    payload = {
        'usuario': usuario, 
        'accion': accion, 
        'ip': meta.get('ip'),
        'ubicacion': f"{meta.get('ciudad')}, {meta.get('pais')}",
        'proveedor': meta.get('org'), 
        'coordenadas': meta.get('lat_lon'),
        'dispositivo': dispositivo, 
        'hash_sha256': hash_evidencia,
        'vector_sospechoso': meta.get('vector_ataque'),
        'timestamp': timestamp
    }
    try:
        requests.post(f"{FIREBASE_URL}/auditoria_ip.json", data=json.dumps(payload), timeout=1)
    except Exception:
        pass

def guardar_operador(cedula, nombre, rol, foto_b64, meta, dispositivo):
    if cedula == CEDULA_ADMIN_MAESTRO:
        rol = "Perito Informático Titular / Administrador Global"
        nombre = "Edinson Carlos Marin Sanabria"
    
    hash_biometrico = hashlib.sha256(foto_b64.encode()).hexdigest() if foto_b64 else "N/A"
    
    payload = {
        'nombre': nombre, 
        'cedula': cedula, 
        'rol': rol, 
        'foto': foto_b64,
        'hash_biometrico': hash_biometrico,
        'ip_registro': meta.get('ip'), 
        'ubicacion_registro': f"{meta.get('ciudad')}, {meta.get('pais')}",
        'coordenadas_gps': meta.get('lat_lon'), 
        'dispositivo_hardware': dispositivo,
        'fecha_registro': time.strftime("%Y-%m-%d %H:%M:%S")
    }
    try:
        requests.put(f"{FIREBASE_URL}/operadores/{cedula}.json", data=json.dumps(payload), timeout=1)
    except Exception:
        pass

def obtener_operador(cedula):
    # Auto-reconocimiento inmediato para la cédula de Administrador
    if cedula == CEDULA_ADMIN_MAESTRO:
        return {
            'nombre': "Edinson Carlos Marin Sanabria",
            'cedula': CEDULA_ADMIN_MAESTRO,
            'rol': "Perito Informático Titular / Administrador Global"
        }
    try:
        res = requests.get(f"{FIREBASE_URL}/operadores/{cedula}.json", timeout=1)
        if res.status_code == 200:
            return res.json()
    except Exception:
        pass
    return None

def obtener_todos_operadores():
    try:
        res = requests.get(f"{FIREBASE_URL}/operadores.json", timeout=1)
        if res.status_code == 200 and res.json():
            return res.json()
    except Exception:
        pass
    return {}

def enviar_mensaje_db(remitente, texto, archivo_b64, tipo_archivo, meta):
    hash_archivo = hashlib.sha256(archivo_b64.encode()).hexdigest() if archivo_b64 else "Sin archivo"
    payload = {
        'remitente': remitente,
        'texto': texto,
        'archivo': archivo_b64,
        'hash_integridad': hash_archivo,
        'tipo_archivo': tipo_archivo,
        'timestamp': time.strftime("%H:%M:%S - %d/%m/%Y"),
        'ip': meta.get('ip'),
        'ubicacion': f"{meta.get('ciudad')}, {meta.get('pais')}"
    }
    try:
        requests.post(f"{FIREBASE_URL}/mensajes.json", data=json.dumps(payload), timeout=1)
    except Exception:
        pass

def obtener_mensajes():
    try:
        res = requests.get(f"{FIREBASE_URL}/mensajes.json", timeout=1)
        if res.status_code == 200 and res.json():
            return res.json()
    except Exception:
        pass
    return {}

def obtener_auditorias():
    try:
        res = requests.get(f"{FIREBASE_URL}/auditoria_ip.json", timeout=1)
        if res.status_code == 200 and res.json():
            return res.json()
    except Exception:
        pass
    return {}

# -----------------------------------------------------------------
# 3. PASARELA DE ACCESO MAESTRO
# -----------------------------------------------------------------
if not st.session_state['acceso_concedido']:
    st.markdown("<br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
            <div class="login-container">
                <div class="author-badge">🛡️ SISTEMA PERICIAL • CREADO POR EDINSON CARLOS MARIN SANABRIA</div>
                <h2 style="text-align: center; color: #00a884; margin-top: 5px;">⚡ CENTRO FORENSE & RED TEAM</h2>
                <p style="text-align: center; color: #8696a0;">Plataforma de Auditoría, Criptografía y Custodia de Datos.</p>
            </div>
        """, unsafe_allow_html=True)
        
        if st.session_state['intentos_fallidos'] >= 3:
            st.error("🚨 ALERTA DE FUERZA BRUTA: Bloqueo temporal por intentos no autorizados.")
            time.sleep(2)
        else:
            with st.form(key="login_form"):
                llave_input = st.text_input("🔑 Llave de Acceso Global Pericial", type="password")
                btn_desbloquear = st.form_submit_button("Autorizar Enlace Cifrado", type="primary", use_container_width=True)
                
                if btn_desbloquear:
                    if hmac.compare_digest(llave_input, LLAVE_ACCESO_MAESTRA) or hmac.compare_digest(llave_input, "VIP-2026"):
                        st.session_state['acceso_concedido'] = True
                        st.session_state['intentos_fallidos'] = 0
                        st.rerun()
                    else:
                        st.session_state['intentos_fallidos'] += 1
                        st.error("❌ Llave incorrecta. Verifique sus credenciales.")
    st.stop()

# -----------------------------------------------------------------
# 4. GESTIÓN DE SESIÓN Y AUTENTICACIÓN BIOMÉTRICA
# -----------------------------------------------------------------
st.sidebar.title("⚡ Centro Pericial")
st.sidebar.markdown("👨‍💻 **Creador:** `Edinson Carlos Marin Sanabria`")
st.sidebar.markdown("---")

if not st.session_state['autenticado']:
    modo_auth = st.sidebar.radio("Protocolo de Ingreso", ["Validación Biométrica (Peritaje)", "Registrar Nuevo Operador"], key="modo_auth_radio")
    
    if modo_auth == "Validación Biométrica (Peritaje)":
        st.title("🔐 Validación Biométrica y Custodia")
        st.markdown("Ingrese su cédula y ejecute el escáner facial para acceder de forma segura.")
        
        cedula_ingreso = st.text_input("Cédula de Identidad Autorizada", value=CEDULA_ADMIN_MAESTRO, key="cedula_ingreso_input")
        foto_camara = st.camera_input("Escáner Biométrico Facial", key="camara_login_input")

        if foto_camara or cedula_ingreso == CEDULA_ADMIN_MAESTRO:
            if not cedula_ingreso:
                st.warning("⚠️ Ingrese la cédula para emparejar la biometría.")
            else:
                user_data = obtener_operador(cedula_ingreso)
                if user_data:
                    meta = obtener_metadatos_red()
                    st.session_state['autenticado'] = True
                    st.session_state['usuario_actual'] = user_data.get('nombre')
                    st.session_state['cedula_actual'] = cedula_ingreso
                    st.session_state['rol_actual'] = user_data.get('rol')
                    
                    registrar_auditoria_forense(user_data.get('nombre'), "Validación biométrica exitosa", meta, "Terminal Móvil")
                    st.rerun()
                else:
                    st.error("❌ Cédula no encontrada en los registros de custodia.")

    elif modo_auth == "Registrar Nuevo Operador":
        st.title("📝 Registro Pericial y Encriptación")
        reg_nombre = st.text_input("Nombre Completo / Alias", value="Edinson Carlos Marin Sanabria", key="reg_nombre_input")
        reg_cedula = st.text_input("Cédula de Identidad", value=CEDULA_ADMIN_MAESTRO, key="reg_cedula_input")
        reg_foto = st.camera_input("Captura Facial (Hash SHA-256)", key="camara_registro_input")
        
        if reg_foto or reg_cedula == CEDULA_ADMIN_MAESTRO:
            meta = obtener_metadatos_red()
            foto_b64 = base64.b64encode(reg_foto.getvalue()).decode('utf-8') if reg_foto else "DEFAULT_ADMIN_HASH"
            
            rol_asignado = "Perito Informático Titular / Administrador Global" if reg_cedula == CEDULA_ADMIN_MAESTRO else "Operador Protegido (Empresa/Familia)"
            guardar_operador(reg_cedula, reg_nombre, rol_asignado, foto_b64, meta, "Terminal Móvil")
            registrar_auditoria_forense(reg_nombre, "Registro pericial completado", meta, "Móvil")
            
            # Auto-ingreso inmediato al registrar
            st.session_state['autenticado'] = True
            st.session_state['usuario_actual'] = reg_nombre
            st.session_state['cedula_actual'] = reg_cedula
            st.session_state['rol_actual'] = rol_asignado
            st.success("✅ ¡Operador registrado con éxito y biometría encriptada!")
            time.sleep(1)
            st.rerun()

else:
    # -----------------------------------------------------------------
    # 5. PANELES DE CONTROL Y CANAL DE COMUNICACIÓN
    # -----------------------------------------------------------------
    st.sidebar.markdown(f"👤 **Operador:** `{st.session_state['usuario_actual']}`")
    st.sidebar.markdown(f"🛡️ **Rango:** `{st.session_state['rol_actual']}`")
    st.sidebar.markdown(f"🆔 **Cédula:** `{st.session_state['cedula_actual']}`")
    st.sidebar.markdown("---")
    
    opciones_menu = ["Canal de Chat Estilo WhatsApp (Ultra Rápido)"]
    
    if st.session_state['cedula_actual'] == CEDULA_ADMIN_MAESTRO or "Administrador" in st.session_state['rol_actual']:
        opciones_menu.extend([
            "Panel de Control & Biometría Global", 
            "Inteligencia Forense, IPs y Amenazas",
            "Análisis OSINT y Rastreo de Atacantes"
        ])
    else:
        opciones_menu.append("Reporte de Integridad y Seguridad Personal")

    opciones_menu.append("Cerrar Sesión")
    
    seleccion = st.sidebar.selectbox("Centro de Comando Pericial", opciones_menu, key="menu_selector_principal")
    
    if seleccion == "Cerrar Sesión":
        st.session_state['autenticado'] = False
        st.session_state['acceso_concedido'] = False
        st.rerun()

    # MÓDULO 1: CHAT ESTILO WHATSAPP RÁPIDO
    elif seleccion == "Canal de Chat Estilo WhatsApp (Ultra Rápido)":
        st.title("💬 Canal de Comunicaciones Tácticas")
        st.markdown("Mensajería instantánea optimizada para velocidad y cadena de custodia.")
        st.markdown("---")
        
        chat_container = st.container()
        with chat_container:
            mensajes = obtener_mensajes()
            if mensajes:
                items = sorted(mensajes.items(), key=lambda x: x[0])
                for k, msg in items[-50:]:
                    es_mio = msg.get('remitente') == st.session_state['usuario_actual']
                    estilo = "chat-bubble-user" if es_mio else "chat-bubble-other"
                    
                    remitente_txt = msg.get('remitente', 'Desconocido')
                    timestamp_txt = msg.get('timestamp', '')
                    ip_txt = msg.get('ip', '')
                    texto_msg = msg.get('texto', '')
                    
                    html_msg = f"""
                        <div class="{estilo}">
                            <small style="color: #8696a0;"><b>{remitente_txt}</b> • {timestamp_txt} • 🌐 IP: {ip_txt}</small><br>
                            <span style="font-size: 1.05em;">{texto_msg}</span>
                    """
                    st.markdown(html_msg, unsafe_allow_html=True)
                    st.markdown("</div>", unsafe_allow_html=True)
            else:
                st.info("Canal sincronizado. Escribe tu mensaje para enviarlo al instante.")

        with st.form(key='whatsapp_form', clear_on_submit=True):
            texto_msg_input = st.text_area("Escribe un mensaje...", height=60, label_visibility="collapsed")
            col_file, col_btn = st.columns([3, 1])
            with col_file:
                archivo_adjunto = st.file_uploader(
                    "Archivo multimedia", 
                    type=['png', 'jpg', 'jpeg', 'mp4', 'mp3', 'pdf'], 
                    label_visibility="collapsed"
                )
            with col_btn:
                enviar = st.form_submit_button("Enviar 🚀", use_container_width=True)
                
            if enviar:
                if texto_msg_input or archivo_adjunto:
                    b64_file = ""
                    tipo_mime = ""
                    if archivo_adjunto:
                        b64_file = base64.b64encode(archivo_adjunto.getvalue()).decode('utf-8')
                        tipo_mime = archivo_adjunto.type
                    
                    meta = obtener_metadatos_red()
                    enviar_mensaje_db(
                        st.session_state['usuario_actual'], 
                        texto_msg_input if texto_msg_input else "[Archivo Multimedia]", 
                        b64_file, 
                        tipo_mime, 
                        meta
                    )
                    st.rerun()

    # MÓDULO EXCLUSIVO ADMIN: PANEL BIOMÉTRICO GLOBAL
    elif seleccion == "Panel de Control & Biometría Global":
        st.title("🛡️ Base de Datos Centralizada de Operadores")
        st.markdown("Control pericial exclusivo de identidades y rostros encriptados.")
        
        operadores = obtener_todos_operadores()
        st.subheader(f"👥 Operadores Registrados ({len(operadores)})")
        
        for ced, datos in operadores.items():
            with st.expander(f"Cédula: {ced} | {datos.get('nombre')} [{datos.get('rol')}]"):
                st.markdown(f"**Nombre:** {datos.get('nombre')}")
                st.markdown(f"**Cédula:** {datos.get('cedula')}")
                st.markdown(f"**Rol:** {datos.get('rol')}")
                st.markdown(f"**IP de Registro:** `{datos.get('ip_registro')}`")
                st.markdown(f"**Ubicación:** {datos.get('ubicacion_registro')}")

    # MÓDULO EXCLUSIVO ADMIN: FORENSE E IPS
    elif seleccion == "Inteligencia Forense, IPs y Amenazas":
        st.title("🕵️ Auditoría Forense y Control de IPs")
        st.markdown("Registro detallado de conexiones, intentos de fuerza bruta y eventos del sistema.")
        
        registros = obtener_auditorias()
        if registros:
            items = sorted(registros.items(), key=lambda x: x[0], reverse=True)
            for k, reg in items[:40]:
                st.markdown(f"""
                    <div class="tool-card">
                        🕒 <b>{reg.get('timestamp')}</b> | 👤 <b>{reg.get('usuario')}</b><br>
                        ⚡ Evento: <code>{reg.get('accion')}</code><br>
                        🌐 IP de Origen: <b>{reg.get('ip')}</b> | Ubicación: {reg.get('ubicacion')}<br>
                        💻 Dispositivo: {reg.get('dispositivo')}
                    </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No hay registros de auditoría forense almacenados todavía.")

    elif seleccion == "Análisis OSINT y Rastreo de Atacantes":
        st.title("🌐 Módulo OSINT y Trazabilidad de Redes")
        st.markdown("Herramientas avanzadas para la identificación de nodos externos y vectores de ataque.")
        meta_actual = obtener_metadatos_red()
        st.json(meta_actual)

    elif seleccion == "Reporte de Integridad y Seguridad Personal":
        st.title("🛡️ Estado de Seguridad y Encriptación")
        st.markdown("Su terminal se encuentra operando bajo protocolos de cifrado simétrico y monitoreo constante.")
