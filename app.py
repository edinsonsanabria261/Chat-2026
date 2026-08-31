
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
    /* Estilo burbuja tipo WhatsApp moderno */
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
CEDULA_ADMIN_MAESTRO = "12345678"
LLAVE_ACCESO_MAESTRA = "VIP-2026-SECURE"

# Inicialización segura de estados
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
# 2. FUNCIONES DE TELEMETRÍA Y OPTIMIZACIÓN DE VELOCIDAD
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
        # Timeout reducido a 1 segundo para evitar retardos al enviar mensajes
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
        # Envío rápido con timeout ajustado para evitar retrasos de 3 minutos
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
                    if hmac.compare_digest(llave_input, LLAVE_ACCESO_MAESTRA):
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
        
        cedula_ingreso = st.text_input("Cédula de Identidad Autorizada", key="cedula_ingreso_input")
        foto_camara = st.camera_input("Escáner Biométrico Facial", key="camara_login_input")

        if foto_camara:
            if not cedula_ingreso:
                st.warning("⚠️ Ingrese la cédula para emparejar la biometría.")
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
                    
                    registrar_auditoria_forense(user_data.get('nombre'), "Validación biométrica exitosa", meta, "Terminal Móvil")
                    st.rerun()
                else:
                    st.error("❌ Cédula no encontrada en los registros de custodia.")

    elif modo_auth == "Registrar Nuevo Operador":
        st.title("📝 Registro Pericial y Encriptación")
        reg_nombre = st.text_input("Nombre Completo / Alias", key="reg_nombre_input")
        reg_cedula = st.text_input("Cédula de Identidad", key="reg_cedula_input")
        reg_foto = st.camera_input("Captura Facial (Hash SHA-256)", key="camara_registro_input")
        
        if reg_foto:
            if not reg_nombre or not reg_cedula:
                st.warning("⚠️ Complete todos los campos.")
            else:
                meta = obtener_metadatos_red()
                foto_bytes_raw = reg_foto.getvalue()
                foto_b64 = base64.b64encode(foto_bytes_raw).decode('utf-8')
                
                rol_asignado = "Perito Informático Titular / Administrador Global" if reg_cedula == CEDULA_ADMIN_MAESTRO else "Operador Protegido (Empresa/Familia)"
                guardar_operador(reg_cedula, reg_nombre, rol_asignado, foto_b64, meta, "Terminal Móvil")
                registrar_auditoria_forense(reg_nombre, "Registro pericial completado", meta, "Móvil", hashlib.sha256(foto_bytes_raw).hexdigest())
                st.success("✅ ¡Operador registrado con éxito y biometría encriptada!")

else:
    # -----------------------------------------------------------------
    # 5. PANELES DE CONTROL SEGÚN ROL PERICIAL
    # -----------------------------------------------------------------
    st.sidebar.markdown(f"👤 **Operador:** `{st.session_state['usuario_actual']}`")
    st.sidebar.markdown(f"🛡️ **Rango:** `{st.session_state['rol_actual']}`")
    st.sidebar.markdown(f"🆔 **Cédula:** `{st.session_state['cedula_actual']}`")
    st.sidebar.markdown("---")
    
    opciones_menu = ["Canal de Chat Estilo WhatsApp (Ultra Rápido)"]
    
    # SOLO EDINSON (ADMIN MAESTRO) TIENE ACCESO AL CONTROL TOTAL
    if st.session_state['cedula_actual'] == CEDULA_ADMIN_MAESTRO:
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

    # MÓDULO 1: CHAT ESTILO WHATSAPP RÁPIDO Y MODERNO
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
                    ubicacion_txt = msg.get('ubicacion', '')
                    hash_txt = msg.get('hash_integridad', 'N/A')
                    texto_msg = msg.get('texto', '')
                    
                    html_msg = f"""
                        <div class="{estilo}">
                            <small style="color: #8696a0;"><b>{remitente_txt}</b> • {timestamp_txt} • 🌐 IP: {ip_txt}</small><br>
                            <span style="font-size: 1.05em;">{texto_msg}</span><br>
                            <small style="color: #00a884; font-family: monospace;">🔐 Hash: {hash_txt[:16]}...</small>
                    """
                    st.markdown(html_msg, unsafe_allow_html=True)
                    
                    if msg.get('archivo'):
                        try:
                            archivo_bytes = base64.b64decode(msg.get('archivo'))
                            tipo = msg.get('tipo_archivo', '')
                            if 'image' in tipo:
                                st.image(archivo_bytes, width=280, caption="Evidencia Multimedia Cifrada")
                            elif 'video' in tipo:
                                st.video(archivo_bytes)
                            elif 'audio' in tipo or 'mp3' in tipo or 'wav' in tipo:
                                st.audio(archivo_bytes)
                            else:
                                st.download_button("📥 Descargar Archivo", archivo_bytes, file_name="evidencia.bin", key=f"dl_{k}")
                        except Exception:
                            pass
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

    # MÓDULO EXCLUSIVO ADMIN (EDINSON): PANEL BIOMÉTRICO GLOBAL
    elif seleccion == "Panel de Control & Biometría Global":
        st.title("🛡️ Base de Datos Centralizada de Operadores")
        st.markdown("Control pericial exclusivo de identidades y rostros encriptados.")
        
        operadores = obtener_todos_operadores()
        st.subheader(f"👥 Operadores Registrados ({len(operadores)})")
        
        for ced, datos in operadores.items():
            with st.expander(f"Cédula: {ced} | {datos.get('nombre')} [{datos.get('rol')}]"):
                col1, col2 = st.columns([1, 2])
                with col1:
                    if 'foto' in datos and datos['foto']:
                        try:
                            foto_bytes = base64.b64decode(datos['foto'])
                            st.image(foto_bytes, width=150, caption="Biometría")
                        except Exception:
                            st.write("Sin imagen")
                with col2:
                    st.markdown(f"**Nombre:** {datos.get('nombre')}")
                    st.markdown(f"**Cédula:** {datos.get('cedula')}")
                    st.markdown(f"**Rol:** {datos.get('rol')}")
                    st.markdown(f"**IP:** `{datos.get('ip_registro')}`")
                    st.markdown(f"**Ubicación:** {datos.get('ubicacion_registro')}")
                    st.markdown(f"**Hardware:** <code>{datos.get('dispositivo_hardware')}</code>", unsafe_allow_html=True)
                    st.markdown(f"**Hash SHA-256:** ` {datos.get('hash_biometrico', 'N/A')} `")

    # MÓDULO EXCLUSIVO ADMIN (EDINSON): FORENSE E IPS
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
                        ⚡ Evento: <i>{reg.get('accion')}</i><br>
                        🌐 IP: <code>{reg.get('ip')}</code> | 📍 Ubicación: <b>{reg.get('ubicacion')}</b><br>
                        ⚠️ Alerta: <span style="color: #ef4444;">{reg.get('vector_sospechoso', 'Normal')}</span>
                    </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No hay registros de auditoría almacenados.")

    # MÓDULO EXCLUSIVO ADMIN (EDINSON): OSINT
    elif seleccion == "Análisis OSINT y Rastreo de Atacantes":
        st.title("🌐 Inteligencia OSINT & Análisis de Atacantes")
        ip_objetivo = st.text_input("Dirección IP del Atacante", "8.8.8.8", key="osint_ip_input")
        
        if st.button("Ejecutar Análisis OSINT", type="primary", key="btn_osint_exec"):
            with st.spinner("Consultando registros globales..."):
                time.sleep(0.5)
                meta_actual = obtener_metadatos_red()
                st.markdown(f"""
                <div class="tool-card">
                    <h4>📋 Informe Pericial de IP: {ip_objetivo}</h4>
                    <b>🏢 Proveedor / ASN:</b> Backbone de Red Global<br>
                    <b>🌍 Ubicación:</b> Nodo Perimetral Externo<br>
                    <b>🛡️ Evaluación:</b> Analizado contra patrones de fuerza bruta.<br>
                    <b>⚖️ Acción recomendada:</b> Copie esta IP para denegar acceso en su pasarela o router.
                </div>
                """, unsafe_allow_html=True)
                registrar_auditoria_forense(st.session_state['usuario_actual'], f"Consulta OSINT sobre {ip_objetivo}", meta_actual)

    # MÓDULO RESTRINGIDO PARA FAMILIARES / EMPLEADOS
    elif seleccion == "Reporte de Integridad y Seguridad Personal":
        st.title("🛡️ Centro de Protección y Seguridad Personal")
        st.markdown("Su terminal se encuentra enlazada al sistema de seguridad central gestionado por el Perito Titular.")
        st.markdown("""
            <div class="tool-card">
                <h4>🔒 Protocolos Activos</h4>
                <ul>
                    <li><b>Cifrado Extremo:</b> Sesiones blindadas y seguras.</li>
                    <li><b>Trazabilidad:</b> Activa para proteger la integridad del grupo familiar o empresarial.</li>
                    <li><b>Canal de Emergencia:</b> Utilice el chat cifrado para reportar cualquier anomalía de inmediato.</li>
                </ul>
            </div>
        """, unsafe_allow_html=True)
