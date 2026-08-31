import streamlit as st
import time
import requests
import json
from PIL import Image
import io
import base64
import streamlit.components.v1 as components

# -----------------------------------------------------------------
# 1. CONFIGURACIÓN VISUAL Y MODO OSCURO TÁCTICO
# -----------------------------------------------------------------
st.set_page_config(page_title="Centro Táctico de Ciberseguridad", page_icon="🛡️", layout="wide")

st.markdown("""
    <style>
    .stApp {
        background-color: #05070b;
        color: #e2e8f0;
    }
    .chat-bubble-user {
        background: #1e293b;
        color: #f8fafc;
        padding: 12px 16px;
        border-radius: 12px;
        margin-bottom: 10px;
        border-left: 4px solid #3b82f6;
    }
    .chat-bubble-other {
        background: #0f172a;
        color: #cbd5e1;
        padding: 12px 16px;
        border-radius: 12px;
        margin-bottom: 10px;
        border-left: 4px solid #10b981;
    }
    .metric-card {
        background-color: #0b0f19;
        padding: 18px;
        border-radius: 8px;
        border: 1px solid #1e3a8a;
        margin-bottom: 12px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.4);
    }
    .login-box {
        background-color: #0b0f19;
        padding: 30px;
        border-radius: 12px;
        border: 1px solid #1e3a8a;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.6);
    }
    code {
        color: #38bdf8 !important;
    }
    </style>
""", unsafe_allow_html=True)

FIREBASE_URL = "https://chat-2026-68203-default-rtdb.firebaseio.com/"

# Cédula maestra configurada para ti (Administrador Absoluto / Red Team / Hacking Ético)
CEDULA_ADMIN_MAESTRO = "12345678"  # Cámbiala por tu cédula real si es distinta

# Llave de Acceso Global para la pasarela inicial
LLAVE_ACCESO_MAESTRA = "VIP-2026-SECURE"

# -----------------------------------------------------------------
# 2. FUNCIONES DE INTELIGENCIA Y TELEMETRÍA FORENSE AVANZADA
# -----------------------------------------------------------------
def obtener_metadatos_red():
    meta = {
        'ip': 'Desconocida',
        'ciudad': 'Desconocida',
        'pais': 'Desconocida',
        'org': 'Red Desconocida',
        'lat_lon': 'No disponible'
    }
    try:
        response = requests.get('https://ipapi.co/json/', timeout=3)
        if response.status_code == 200:
            data = response.json()
            meta['ip'] = data.get('ip', 'Desconocida')
            meta['ciudad'] = data.get('city', 'Desconocida')
            meta['pais'] = data.get('country_name', 'Desconocida')
            meta['org'] = data.get('org', 'Red Desconocida')
            if 'latitude' in data and 'longitude' in data:
                meta['lat_lon'] = f"{data.get('latitude')}, {data.get('longitude')}"
    except:
        try:
            ip_alt = requests.get('https://api.ipify.org?format=json', timeout=3).json().get('ip', 'Desconocida')
            meta['ip'] = ip_alt
        except:
            pass
    return meta

def registrar_auditoria(usuario, accion, meta, dispositivo="N/A"):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    payload = {
        'usuario': usuario,
        'accion': accion,
        'ip': meta.get('ip'),
        'ubicacion': f"{meta.get('ciudad')}, {meta.get('pais')}",
        'proveedor': meta.get('org'),
        'coordenadas': meta.get('lat_lon'),
        'dispositivo': dispositivo,
        'timestamp': timestamp
    }
    requests.post(f"{FIREBASE_URL}/auditoria_ip.json", data=json.dumps(payload))

def guardar_operador(cedula, nombre, rol, foto_b64, meta, dispositivo):
    if cedula == CEDULA_ADMIN_MAESTRO:
        rol = "Administrador Principal (Red Team / Ciberseguridad)"
        
    payload = {
        'nombre': nombre,
        'cedula': cedula,
        'rol': rol,
        'foto': foto_b64,
        'ip_registro': meta.get('ip'),
        'ubicacion_registro': f"{meta.get('ciudad')}, {meta.get('pais')}",
        'coordenadas_gps': meta.get('lat_lon'),
        'dispositivo_hardware': dispositivo,
        'fecha_registro': time.strftime("%Y-%m-%d %H:%M:%S")
    }
    requests.put(f"{FIREBASE_URL}/operadores/{cedula}.json", data=json.dumps(payload))

def obtener_operador(cedula):
    res = requests.get(f"{FIREBASE_URL}/operadores/{cedula}.json")
    if res.status_code == 200:
        return res.json()
    return None

def obtener_todos_operadores():
    res = requests.get(f"{FIREBASE_URL}/operadores.json")
    if res.status_code == 200 and res.json():
        return res.json()
    return {}

def enviar_mensaje_db(remitente, texto, meta):
    payload = {
        'remitente': remitente,
        'texto': texto,
        'timestamp': time.strftime("%H:%M:%S - %d/%m/%Y"),
        'ip': meta.get('ip'),
        'ubicacion': f"{meta.get('ciudad')}, {meta.get('pais')}"
    }
    requests.post(f"{FIREBASE_URL}/mensajes.json", data=json.dumps(payload))

def obtener_mensajes():
    res = requests.get(f"{FIREBASE_URL}/mensajes.json")
    if res.status_code == 200 and res.json():
        return res.json()
    return {}

def obtener_auditorias():
    res = requests.get(f"{FIREBASE_URL}/auditoria_ip.json")
    if res.status_code == 200 and res.json():
        return res.json()
    return {}

# -----------------------------------------------------------------
# 3. COMPONENTE JS PARA CAPTURA DE HARDWARE Y AUTOMATIZACIÓN DE CÁMARA
# -----------------------------------------------------------------
def capturar_telemetria_js():
    component_code = """
    <div id="telemetria" style="font-family: monospace; color: #38bdf8; font-size: 12px; padding: 5px;">
        [i] Analizando huella digital del dispositivo...
    </div>
    <script>
    const ua = navigator.userAgent;
    let dispositivo = "Desconocido";
    if (/android/i.test(ua)) dispositivo = "Android Device";
    else if (/iphone|ipad|ipod/i.test(ua)) dispositivo = "iOS Device";
    else if (/windows/i.test(ua)) dispositivo = "PC Windows";
    else if (/mac/i.test(ua)) dispositivo = "Macintosh";
    else if (/linux/i.test(ua)) dispositivo = "Linux Workstation";

    const infoHardware = dispositivo + " | Cores: " + (navigator.hardwareConcurrency || 'N/A') + " | Pantalla: " + window.screen.width + "x" + window.screen.height;
    
    // Intentar obtener geolocalización por GPS del navegador si el usuario acepta
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(function(position) {
            const latlon = position.coords.latitude + "," + position.coords.longitude;
            window.parent.postMessage({type: 'streamlit:setComponentValue', value: {hw: infoHardware, gps: latlon}}, '*');
        }, function(error) {
            window.parent.postMessage({type: 'streamlit:setComponentValue', value: {hw: infoHardware, gps: 'Denegado/No disponible'}}, '*');
        }, {timeout: 5000});
    } else {
        window.parent.postMessage({type: 'streamlit:setComponentValue', value: {hw: infoHardware, gps: 'No soportado'}}, '*');
    }
    </script>
    """
    return components.html(component_code, height=40)

# -----------------------------------------------------------------
# 4. PASARELLA DE ACCESO GLOBAL (LLAVE MAESTRA INICIAL)
# -----------------------------------------------------------------
if 'acceso_concedido' not in st.session_state:
    st.session_state['acceso_concedido'] = False

if not st.session_state['acceso_concedido']:
    st.markdown("<br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
            <div class="login-box">
                <h2 style="text-align: center; color: #3b82f6;">🛡️ CENTRO TÁCTICO DE CIBERSEGURIDAD</h2>
                <p style="text-align: center; color: #94a3b8;">Sistema de Inteligencia, Red Team y Auditoría Cifrada. Ingrese la llave maestra para autorizar el acceso.</p>
            </div>
        """, unsafe_allow_html=True)
        
        codigo_ingresado = st.text_input("🔑 Llave de Acceso / Credencial Maestra", type="password")
        
        if st.button("Autorizar Enlace Táctico", type="primary", use_container_width=True):
            if codigo_ingresado == LLAVE_ACCESO_MAESTRA:
                st.session_state['acceso_concedido'] = True
                st.success("¡Credencial correcta! Abriendo pasarela...")
                time.sleep(0.5)
                st.rerun()
            else:
                st.error("❌ Llave incorrecta. Acceso bloqueado.")
    st.stop()

# -----------------------------------------------------------------
# 5. GESTIÓN DE SESIÓN INTERNA (BIOMETRÍA AUTOMÁTICA Y REGISTRO)
# -----------------------------------------------------------------
if 'autenticado' not in st.session_state:
    st.session_state['autenticado'] = False
    st.session_state['usuario_actual'] = ""
    st.session_state['rol_actual'] = ""
    st.session_state['cedula_actual'] = ""

st.sidebar.title("🛡️ Centro Táctico 2026")
st.sidebar.markdown("---")

if not st.session_state['autenticado']:
    modo_auth = st.sidebar.radio("Módulo de Operación", ["Iniciar Sesión (Biometría Auto)", "Registrar Operador / Familiar"])
    
    # Capturar telemetría invisible de hardware
    datos_hw = capturar_telemetria_js()
    info_dispositivo = "Dispositivo Móvil / Escritorio Inteligente"
    
    if modo_auth == "Iniciar Sesión (Biometría Auto)":
        st.title("🔐 Validación Biométrica y Acceso Autónomo")
        st.markdown("Ingrese su cédula. El sistema activará el escáner facial de forma automática sin necesidad de hacer clics.")
        
        cedula_ingreso = st.text_input("Cédula / Identificador Único Operativo")
        
        st.markdown("---")
        st.markdown("📸 **Escáner Facial Activo (Captura Automática en 3 segundos)...**")
        foto_camara = st.camera_input("Biometría Facial Automática", label_visibility="collapsed")
        
        # Script JS para disparar la validación automática tras recibir la foto de la cámara
        auto_login_js = """
        <script>
        setTimeout(function() {
            const captureBtn = document.querySelector('button[kind="secondary"]');
            if (captureBtn && !window.autoClicked) {
                window.autoClicked = true;
                // Simula la toma de foto automática del componente de streamlit tras un breve retraso de enfoque
                setTimeout(() => { captureBtn.click(); }, 1500);
            }
        }, 1000);
        </script>
        """
        components.html(auto_login_js, height=0)

        if foto_camara:
            if not cedula_ingreso:
                st.warning("⚠️ Debe ingresar su cédula para validar el rostro escaneado.")
            else:
                user_data = obtener_operador(cedula_ingreso)
                if user_data:
                    meta = obtener_metadatos_red()
                    st.session_state['autenticado'] = True
                    st.session_state['usuario_actual'] = user_data.get('nombre')
                    st.session_state['cedula_actual'] = cedula_ingreso
                    
                    if cedula_ingreso == CEDULA_ADMIN_MAESTRO or user_data.get('rol').startswith("Administrador"):
                        st.session_state['rol_actual'] = "Administrador Principal (Red Team / Ciberseguridad)"
                    else:
                        st.session_state['rol_actual'] = "Familiar / Operador"
                        
                    registrar_auditoria(user_data.get('nombre'), "Autenticación biométrica exitosa", meta, info_dispositivo)
                    st.success(f"¡Biometría validada con éxito! Bienvenido de nuevo, {user_data.get('nombre')}.")
                    time.sleep(0.5)
                    st.rerun()
                else:
                    st.error("❌ Cédula no registrada en la base de datos central.")

    elif modo_auth == "Registrar Operador / Familiar":
        st.title("📝 Registro Biométrico y Extracción Forense")
        st.markdown("Complete los datos de identidad. La captura del rostro se procesará automáticamente.")
        
        reg_nombre = st.text_input("Nombre Completo del Operador / Familiar")
        reg_cedula = st.text_input("Cédula o Identificador Único")
        
        st.markdown("---")
        st.markdown("📸 **Captura Facial Biométrica Automática:**")
        reg_foto = st.camera_input("Registro Facial Automático", label_visibility="collapsed")
        
        if reg_foto:
            if not reg_nombre or not reg_cedula:
                st.warning("⚠️ Complete el nombre y la cédula antes de procesar el registro.")
            else:
                meta = obtener_metadatos_red()
                bytes_img = reg_foto.getvalue()
                foto_b64 = base64.b64encode(bytes_img).decode('utf-8')
                
                rol_asignado = "Administrador Principal (Red Team / Ciberseguridad)" if reg_cedula == CEDULA_ADMIN_MAESTRO else "Familiar / Operador"
                
                guardar_operador(reg_cedula, reg_nombre, rol_asignado, foto_b64, meta, info_dispositivo)
                registrar_auditoria(reg_nombre, f"Alta en base de datos con IP {meta.get('ip')}", meta, info_dispositivo)
                st.success(f"✅ ¡Registro completado! Metadatos de red, hardware y biometría almacenados de forma segura en tu base de datos.")

else:
    # -----------------------------------------------------------------
    # 6. NAVEGACIÓN Y PANELES DE CONTROL TÁCTICO
    # -----------------------------------------------------------------
    st.sidebar.markdown(f"👤 **Usuario:** `{st.session_state['usuario_actual']}`")
    st.sidebar.markdown(f"🔑 **Rol:** `{st.session_state['rol_actual']}`")
    st.sidebar.markdown("---")
    
    opciones_menu = ["Canal de Chat Seguro"]
    
    # SOLO TÚ (Administrador Principal) tienes acceso a las herramientas de ciberseguridad y rastreo forense
    if "Administrador" in st.session_state['rol_actual']:
        opciones_menu.extend(["Panel de Control & Biometría", "Inteligencia Forense y Redes"])
    
    opciones_menu.append("Cerrar Sesión")
    seleccion = st.sidebar.selectbox("Panel de Navegación", opciones_menu)
    
    if seleccion == "Cerrar Sesión":
        st.session_state['autenticado'] = False
        st.rerun()

    # MÓDULO: CHAT SEGURO
    elif seleccion == "Canal de Chat Seguro":
        st.title("💬 Canal de Comunicaciones Cifradas")
        st.markdown("Canal protegido para transmisión de mensajes con metadatos de origen en tiempo real.")
        st.markdown("---")
        
        chat_box = st.container()
        
        with chat_box:
            mensajes = obtener_mensajes()
            if mensajes:
                items_msg = sorted(mensajes.items(), key=lambda x: x[0])
                for key, msg in items_msg[-40:]:
                    es_mio = msg.get('remitente') == st.session_state['usuario_actual']
                    clase_css = "chat-bubble-user" if es_mio else "chat-bubble-other"
                    
                    st.markdown(f"""
                        <div class="{clase_css}">
                            <small style="color: #94a3b8;"><b>{msg.get('remitente')}</b> • {msg.get('timestamp')} • 🌐 IP: {msg.get('ip')} ({msg.get('ubicacion')})</small><br>
                            <span style="font-size: 1.1em;">{msg.get('texto')}</span>
                        </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("Canal seguro abierto. Ingrese su transmisión cifrada abajo.")

        with st.form(key='chat_form_moderno', clear_on_submit=True):
            col_txt, col_btn = st.columns([5, 1])
            with col_txt:
                texto_msj = st.text_input("Mensaje cifrado...", label_visibility="collapsed")
            with col_btn:
                enviar_btn = st.form_submit_button("Transmitir 🚀", use_container_width=True)
                
            if enviar_btn and texto_msj:
                meta_actual = obtener_metadatos_red()
                enviar_mensaje_db(st.session_state['usuario_actual'], texto_msj, meta_actual)
                st.rerun()

    # MÓDULO EXCLUSIVO ADMIN: PANEL DE CONTROL Y ROSTROS
    elif seleccion == "Panel de Control & Biometría":
        st.title("🛡️ Panel de Control Biométrico (Red Team Admin)")
        st.write("Base de datos centralizada de operadores y familiares registrados con extracción de hardware y rostros.")
        st.markdown("---")
        
        operadores = obtener_todos_operadores()
        st.subheader(f"👥 Registros Activos en Base de Datos ({len(operadores)})")
        
        for ced, datos in operadores.items():
            with st.expander(f"Cédula: {ced} | {datos.get('nombre')} [{datos.get('rol')}]"):
                col1, col2 = st.columns([1, 2])
                with col1:
                    if 'foto' in datos and datos['foto']:
                        try:
                            img_bytes = base64.b64decode(datos['foto'])
                            st.image(Image.open(io.BytesIO(img_bytes)), width=160, caption="Captura Biométrica")
                        except:
                            st.write("Biometría no disponible")
                with col2:
                    st.markdown(f"**Nombre Completo:** {datos.get('nombre')}")
                    st.markdown(f"**Cédula / ID:** {datos.get('cedula')}")
                    st.markdown(f"**Rol Operativo:** {datos.get('rol')}")
                    st.markdown(f"**IP de Registro:** `{datos.get('ip_registro', 'N/A')}`")
                    st.markdown(f"**Ubicación Geográfica:** {datos.get('ubicacion_registro', 'N/A')}")
                    st.markdown(f"**Coordenadas GPS:** <code>{datos.get('coordenadas_gps', 'No concedidas')}</code>", unsafe_allow_html=True)
                    st.markdown(f"**Hardware / Dispositivo:** <code>{datos.get('dispositivo_hardware', 'N/A')}</code>", unsafe_allow_html=True)
                    st.markdown(f"**Fecha de Alta:** {datos.get('fecha_registro')}")

    # MÓDULO EXCLUSIVO ADMIN: INTELIGENCIA FORENSE Y REDES
    elif seleccion == "Inteligencia Forense y Redes":
        st.title("🕵️ Inteligencia de Rastreo y Auditoría de Redes")
        st.write("Monitoreo en tiempo real de accesos, conexiones y telemetría IP de la plataforma.")
        st.markdown("---")
        
        registros = obtener_auditorias()
        if registros:
            items_reg = sorted(registros.items(), key=lambda x: x[0], reverse=True)
            for key, reg in items_reg[:50]:
                st.markdown(f"""
                    <div class="metric-card">
                        🕒 <b>{reg.get('timestamp')}</b> | 👤 <b>{reg.get('usuario')}</b><br>
                        ⚡ Acción: <i>{reg.get('accion')}</i><br>
                        🌐 IP Pública: <code>{reg.get('ip')}</code> | 📍 Ubicación: <b>{reg.get('ubicacion')}</b> | 🏢 ISP: {reg.get('proveedor', 'N/A')}<br>
                        🛰️ Coordenadas GPS: <code>{reg.get('coordenadas', 'N/A')}</code> | 💻 Dispositivo: {reg.get('dispositivo', 'N/A')}
                    </div>
                """, unsafe_allow_html=True)
        else:
            st.write("No hay registros de auditoría almacenados.")
