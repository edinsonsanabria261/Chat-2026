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
# 1. CONFIGURACIÓN TÁCTICA Y ESTILOS UI PREMIUM (MODO OSCURO)
# -----------------------------------------------------------------
st.set_page_config(
    page_title="Centro Táctico Pericial - Edinson Carlos Marin Sanabria", 
    page_icon="🛡️", 
    layout="wide"
)

st.markdown("""
    <style>
    .stApp {
        background-color: #05070b;
        color: #f3f4f6;
    }
    .chat-bubble-user {
        background: linear-gradient(135deg, #1e3a8a 0%, #1e1b4b 100%);
        color: #f8fafc;
        padding: 14px 18px;
        border-radius: 16px 16px 2px 16px;
        margin-bottom: 12px;
        box-shadow: 0 4px 12px rgba(30, 58, 138, 0.4);
        max-width: 85%;
        margin-left: auto;
        border: 1px solid #3b82f6;
    }
    .chat-bubble-other {
        background: linear-gradient(135deg, #0f172a 100%, #020617 0%);
        color: #f1f5f9;
        padding: 14px 18px;
        border-radius: 16px 16px 16px 2px;
        margin-bottom: 12px;
        border-left: 4px solid #ef4444;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.6);
        border: 1px solid #1e293b;
    }
    .tool-card {
        background-color: #0f172a;
        padding: 22px;
        border-radius: 14px;
        border: 1px solid #334155;
        margin-bottom: 18px;
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.7);
    }
    .login-container {
        background-color: #0f172a;
        padding: 35px;
        border-radius: 16px;
        border: 1px solid #475569;
        box-shadow: 0 15px 35px rgba(0, 0, 0, 0.9);
    }
    code {
        color: #38bdf8 !important;
        background-color: #020617 !important;
        padding: 3px 8px;
        border-radius: 6px;
        border: 1px solid #1e293b;
    }
    .author-badge {
        background: linear-gradient(90deg, #3b82f6, #ef4444);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: bold;
        font-size: 1.1em;
        text-align: center;
        margin-bottom: 10px;
    }
    </style>
""", unsafe_allow_html=True)

FIREBASE_URL = "https://chat-2026-68203-default-rtdb.firebaseio.com/"
CEDULA_ADMIN_MAESTRO = "12345678"
LLAVE_ACCESO_MAESTRA = "VIP-2026-SECURE"

# Inicialización segura de estados forenses
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
# 2. FUNCIONES DE TELEMETRÍA Y CONTramedidas PERICIALES AVANZADAS
# -----------------------------------------------------------------
def obtener_metadatos_red():
    meta = {
        'ip': '127.0.0.1', 
        'ciudad': 'Nodo Pericial Local', 
        'pais': 'Red Interna Segura', 
        'org': 'Control Táctico Directo', 
        'lat_lon': 'N/A', 
        'isp': 'N/A',
        'vector_ataque': 'Ninguno detectado'
    }
    try:
        response = requests.get('https://ipapi.co/json/', timeout=2)
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
        meta['vector_ataque'] = 'Posible intento de ocultación de ruta / Proxy anónimo'
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
        requests.post(f"{FIREBASE_URL}/auditoria_ip.json", data=json.dumps(payload), timeout=2)
    except Exception:
        pass

def guardar_operador(cedula, nombre, rol, foto_b64, meta, dispositivo):
    if cedula == CEDULA_ADMIN_MAESTRO:
        rol = "Perito Informático Titular / Administrador Global"
    
    # Generación de hash de integridad forense para la biometría facial
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
        requests.put(f"{FIREBASE_URL}/operadores/{cedula}.json", data=json.dumps(payload), timeout=2)
    except Exception:
        pass

def obtener_operador(cedula):
    try:
        res = requests.get(f"{FIREBASE_URL}/operadores/{cedula}.json", timeout=2)
        if res.status_code == 200:
            return res.json()
    except Exception:
        pass
    return None

def obtener_todos_operadores():
    try:
        res = requests.get(f"{FIREBASE_URL}/operadores.json", timeout=2)
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
        requests.post(f"{FIREBASE_URL}/mensajes.json", data=json.dumps(payload), timeout=2)
    except Exception:
        pass

def obtener_mensajes():
    try:
        res = requests.get(f"{FIREBASE_URL}.json", timeout=2)
        if res.status_code == 200 and res.json():
            data = res.json()
            return data.get('mensajes', {})
    except Exception:
        pass
    return {}

def obtener_auditorias():
    try:
        res = requests.get(f"{FIREBASE_URL}/auditoria_ip.json", timeout=2)
        if res.status_code == 200 and res.json():
            return res.json()
    except Exception:
        pass
    return {}

# -----------------------------------------------------------------
# 3. PASARELA DE ACCESO MAESTRO CON DEFENSA CONTRA FUERZA BRUTA
# -----------------------------------------------------------------
if not st.session_state['acceso_concedido']:
    st.markdown("<br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown(f"""
            <div class="login-container">
                <div class="author-badge">🛡️ SISTEMA PERICIAL • CREADO POR EDINSON CARLOS MARIN SANABRIA</div>
                <h2 style="text-align: center; color: #3b82f6; margin-top: 5px;">⚡ CENTRO FORENSE & RED TEAM</h2>
                <p style="text-align: center; color: #94a3b8;">Plataforma de Auditoría, Criptografía y Protección de Activos.</p>
            </div>
        """, unsafe_allow_html=True)
        
        if st.session_state['intentos_fallidos'] >= 3:
            st.error("🚨 ALTA ALERTA DE FUERZA BRUTA: Se han bloqueado los accesos temporalmente por múltiples intentos fallidos desde este segmento de red.")
            meta_fallo = obtener_metadatos_red()
            registrar_auditoria_forense("Intruso Desconocido", "Bloqueo por Fuerza Bruta en Pasarela Global", meta_fallo, "Vector Desconocido")
            time.sleep(3)
        else:
            with st.form(key="login_form"):
                llave_input = st.text_input("🔑 Llave de Acceso Global Pericial", type="password")
                btn_desbloquear = st.form_submit_button("Autorizar Enlace Cifrado", type="primary", use_container_width=True)
                
                if btn_desbloquear:
                    if hmac.compare_digest(llave_input, LLAVE_ACCESO_MAESTRA):
                        st.session_state['acceso_concedido'] = True
                        st.session_state['intentos_fallidos'] = 0
                        st.rerun()
                    else:
                        st.session_state['intentos_fallidos'] += 1
                        meta_intento = obtener_metadatos_red()
                        registrar_auditoria_forense("Anónimo", f"Intento fallido #{st.session_state['intentos_fallidos']} de acceso perimetral", meta_intento)
                        st.error(f"❌ Llave de acceso denegada. Intento registrado ({st.session_state['intentos_fallidos']}/3).")
    st.stop()

# -----------------------------------------------------------------
# 4. GESTIÓN DE SESIÓN Y AUTENTICACIÓN BIOMÉTRICA FORENSE
# -----------------------------------------------------------------
st.sidebar.title("⚡ Centro Pericial Central")
st.sidebar.markdown("👨‍💻 **Creador:** `Edinson Carlos Marin Sanabria`")
st.sidebar.markdown("---")

if not st.session_state['autenticado']:
    modo_auth = st.sidebar.radio("Protocolo de Ingreso", ["Validación Biométrica (Peritaje)", "Registrar Nuevo Operador"], key="modo_auth_radio")
    
    if modo_auth == "Validación Biométrica (Peritaje)":
        st.title("🔐 Validación Biométrica y Cadena de Custodia")
        st.markdown("Ingrese su cédula y ejecute el escáner facial para registrar la huella digital biométrica en el sistema.")
        
        cedula_ingreso = st.text_input("Cédula de Identidad Autorizada", key="cedula_ingreso_input")
        foto_camara = st.camera_input("Escáner Biométrico Facial en Vivo", key="camara_login_input")

        if foto_camara:
            if not cedula_ingreso:
                st.warning("⚠️ Ingrese la cédula para validar la correspondencia biométrica.")
            else:
                user_data = obtener_operador(cedula_ingreso)
                if user_data:
                    meta = obtener_metadatos_red()
                    st.session_state['autenticado'] = True
                    st.session_state['usuario_actual'] = user_data.get('nombre')
                    st.session_state['cedula_actual'] = cedula_ingreso
                    
                    if cedula_ingreso == CEDULA_ADMIN_MAESTRO:
                        st.session_state['rol_actual'] = "Perito Informático Titular / Administrador Global"
                    else:
                        st.session_state['rol_actual'] = "Operador Protegido (Empresa/Familia)"
                    
                    registrar_auditoria_forense(user_data.get('nombre'), "Validación biométrica y geolocalización exitosa", meta, "Terminal Móvil / Auditoría")
                    st.rerun()
                else:
                    st.error("❌ Cédula no registrada en los repositorios de custodia pericial.")

    elif modo_auth == "Registrar Nuevo Operador":
        st.title("📝 Registro Pericial y Encriptación Biométrica")
        reg_nombre = st.text_input("Nombre Completo / Alias del Operador", key="reg_nombre_input")
        reg_cedula = st.text_input("Cédula de Identidad", key="reg_cedula_input")
        reg_foto = st.camera_input("Captura Facial para Encriptación SHA-256", key="camara_registro_input")
        
        if reg_foto:
            if not reg_nombre or not reg_cedula:
                st.warning("⚠️ Complete todos los campos de identificación obligatorios.")
            else:
                meta = obtener_metadatos_red()
                foto_bytes_raw = reg_foto.getvalue()
                foto_b64 = base64.b64encode(foto_bytes_raw).decode('utf-8')
                
                rol_asignado = "Perito Informático Titular / Administrador Global" if reg_cedula == CEDULA_ADMIN_MAESTRO else "Operador Protegido (Empresa/Familia)"
                guardar_operador(reg_cedula, reg_nombre, rol_asignado, foto_b64, meta, "Terminal Móvil Segura")
                registrar_auditoria_forense(reg_nombre, "Registro pericial completado y biometría encriptada", meta, "Móvil", hashlib.sha256(foto_bytes_raw).hexdigest())
                st.success("✅ ¡Operador registrado con éxito! Integridad biométrica asegurada mediante hash SHA-256.")

else:
    # -----------------------------------------------------------------
    # 5. PANELES DE CONTROL TÁCTICO SEGÚN ROL PERICIAL
    # -----------------------------------------------------------------
    st.sidebar.markdown(f"👤 **Operador:** `{st.session_state['usuario_actual']}`")
    st.sidebar.markdown(f"🛡️ **Rango:** `{st.session_state['rol_actual']}`")
    st.sidebar.markdown(f"🆔 **Cédula:** `{st.session_state['cedula_actual']}`")
    st.sidebar.markdown("---")
    
    opciones_menu = ["Canal de Chat Cifrado & Evidencias"]
    
    # RESTRICCIÓN DE SEGURIDAD ESTRICTA: SOLO EDINSON (ADMIN MAESTRO) TIENE ACCESO TOTAL
    if st.session_state['cedula_actual'] == CEDULA_ADMIN_MAESTRO:
        opciones_menu.extend([
            "Panel de Control & Biometría Global", 
            "Inteligencia Forense, IPs y Análisis de Amenazas",
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

    # MÓDULO 1: CHAT DE EVIDENCIAS Y CADENA DE CUSTODIA
    elif seleccion == "Canal de Chat Cifrado & Evidencias":
        st.title("💬 Canal de Comunicaciones y Custodia de Evidencias")
        st.markdown("Transmisión cifrada con generación automática de hashes de integridad SHA-256 para cada evidencia multimedia.")
        st.markdown("---")
        
        chat_container = st.container()
        with chat_container:
            mensajes = obtener_mensajes()
            if mensajes:
                items = sorted(mensajes.items(), key=lambda x: x[0])
                for k, msg in items[-60:]:
                    es_mio = msg.get('remitente') == st.session_state['usuario_actual']
                    estilo = "chat-bubble-user" if es_mio else "chat-bubble-other"
                    
                    remitente_txt = msg.get('remitente', 'Desconocido')
                    timestamp_txt = msg.get('timestamp', '')
                    ip_txt = msg.get('ip', '')
                    ubicacion_txt = msg.get('ubicacion', '')
                    hash_txt = msg.get('hash_integridad', 'N/A')
                    texto_msg = msg.get('texto', '')
                    
                    html_msg = f"""
                        <div class="{estilo}">
                            <small style="color: #94a3b8;"><b>{remitente_txt}</b> • {timestamp_txt} • 🌐 IP: {ip_txt} • 📍 {ubicacion_txt}</small><br>
                            <span style="font-size: 1.15em; word-break: break-all;">{texto_msg}</span><br>
                            <small style="color: #38bdf8; font-family: monospace;">🔐 Hash SHA-256: {hash_txt[:24]}...</small>
                    """
                    st.markdown(html_msg, unsafe_allow_html=True)
                    
                    if msg.get('archivo'):
                        try:
                            archivo_bytes = base64.b64decode(msg.get('archivo'))
                            tipo = msg.get('tipo_archivo', '')
                            if 'image' in tipo:
                                st.image(archivo_bytes, width=320, caption="Evidencia Fotográfica Encriptada")
                            elif 'video' in tipo:
                                st.video(archivo_bytes)
                            elif 'audio' in tipo or 'mp3' in tipo or 'wav' in tipo or 'ogg' in tipo:
                                st.audio(archivo_bytes)
                            else:
                                st.download_button("📥 Descargar Archivo en Custodia", archivo_bytes, file_name="evidencia_pericial.bin", key=f"dl_{k}")
                        except Exception:
                            pass
                    st.markdown("</div>", unsafe_allow_html=True)
            else:
                st.info("Canal seguro sincronizado. Envíe reportes o evidencias para análisis pericial.")

        with st.form(key='whatsapp_form', clear_on_submit=True):
            texto_msg_input = st.text_area("Redactar reporte de seguridad...", height=70, label_visibility="collapsed")
            col_file, col_btn = st.columns([3, 1])
            with col_file:
                archivo_adjunto = st.file_uploader(
                    "Adjuntar Evidencia Digital (Imagen/Documento)", 
                    type=['png', 'jpg', 'jpeg', 'mp4', 'mov', 'mp3', 'wav', 'pdf', 'zip'], 
                    label_visibility="collapsed"
                )
            with col_btn:
                enviar = st.form_submit_button("Registrar Evidencia 🚀", use_container_width=True)
                
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
                        texto_msg_input if texto_msg_input else "[Evidencia Digital Encriptada]", 
                        b64_file, 
                        tipo_mime, 
                        meta
                    )
                    st.rerun()

    # MÓDULO EXCLUSIVO ADMIN (EDINSON): PANEL DE CONTROL & BIOMETRÍA GLOBAL
    elif seleccion == "Panel de Control & Biometría Global":
        st.title("🛡️ Base de Datos Centralizada de Operadores y Biometría")
        st.markdown("Control pericial exclusivo para auditar identidades, rostros encriptados y metadatos de hardware.")
        
        operadores = obtener_todos_operadores()
        st.subheader(f"👥 Operadores Registrados en la Red ({len(operadores)})")
        
        for ced, datos in operadores.items():
            with st.expander(f"Cédula: {ced} | {datos.get('nombre')} [{datos.get('rol')}]"):
                col1, col2 = st.columns([1, 2])
                with col1:
                    if 'foto' in datos and datos['foto']:
                        try:
                            foto_bytes = base64.b64decode(datos['foto'])
                            st.image(foto_bytes, width=160, caption="Biometría Verificada")
                        except Exception:
                            st.write("Sin imagen disponible")
                with col2:
                    st.markdown(f"**Nombre / Alias:** {datos.get('nombre')}")
                    st.markdown(f"**Cédula:** {dato
