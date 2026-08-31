import streamlit as st
import time
import requests
import json
from PIL import Image
import io
import base64
import streamlit.components.v1 as components

# -----------------------------------------------------------------
# 1. CONFIGURACIÓN TÁCTICA Y MODO OSCURO PROFUNDO
# -----------------------------------------------------------------
st.set_page_config(page_title="Centro Táctico Red Team", page_icon="⚡", layout="wide")

st.markdown("""
    <style>
    .stApp {
        background-color: #030712;
        color: #f3f4f6;
    }
    .chat-bubble-user {
        background: #1e1b4b;
        color: #e0e7ff;
        padding: 14px 18px;
        border-radius: 12px;
        margin-bottom: 10px;
        border-left: 4px solid #6366f1;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    .chat-bubble-other {
        background: #111827;
        color: #e5e7eb;
        padding: 14px 18px;
        border-radius: 12px;
        margin-bottom: 10px;
        border-left: 4px solid #10b981;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    .tool-box {
        background-color: #0f172a;
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #3b82f6;
        margin-bottom: 15px;
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.15);
    }
    .login-box {
        background-color: #0f172a;
        padding: 30px;
        border-radius: 12px;
        border: 1px solid #2563eb;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.7);
    }
    code {
        color: #38bdf8 !important;
        background-color: #0f172a !important;
        padding: 2px 6px;
        border-radius: 4px;
    }
    </style>
""", unsafe_allow_html=True)

FIREBASE_URL = "https://chat-2026-68203-default-rtdb.firebaseio.com/"
CEDULA_ADMIN_MAESTRO = "12345678"  # Cambia por tu cédula si es distinta
LLAVE_ACCESO_MAESTRA = "VIP-2026-SECURE"

# -----------------------------------------------------------------
# 2. FUNCIONES DE TELEMETRÍA Y GESTIÓN DE DATOS EN TIEMPO REAL
# -----------------------------------------------------------------
def obtener_metadatos_red():
    meta = {'ip': '127.0.0.1', 'ciudad': 'Nodo Local', 'pais': 'Red Interna', 'org': 'Red Táctica Directa', 'lat_lon': 'N/A'}
    try:
        response = requests.get('https://ipapi.co/json/', timeout=2)
        if response.status_code == 200:
            data = response.json()
            meta['ip'] = data.get('ip', '127.0.0.1')
            meta['ciudad'] = data.get('city', 'Nodo Local')
            meta['pais'] = data.get('country_name', 'Red Interna')
            meta['org'] = data.get('org', 'ISP Privado')
            if 'latitude' in data and 'longitude' in data:
                meta['lat_lon'] = f"{data.get('latitude')}, {data.get('longitude')}"
    except:
        pass
    return meta

def registrar_auditoria(usuario, accion, meta, dispositivo="N/A"):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    payload = {
        'usuario': usuario, 'accion': accion, 'ip': meta.get('ip'),
        'ubicacion': f"{meta.get('ciudad')}, {meta.get('pais')}",
        'proveedor': meta.get('org'), 'coordenadas': meta.get('lat_lon'),
        'dispositivo': dispositivo, 'timestamp': timestamp
    }
    requests.post(f"{FIREBASE_URL}/auditoria_ip.json", data=json.dumps(payload))

def guardar_operador(cedula, nombre, rol, foto_b64, meta, dispositivo):
    if cedula == CEDULA_ADMIN_MAESTRO:
        rol = "Comandante Red Team (Administrador Total)"
    payload = {
        'nombre': nombre, 'cedula': cedula, 'rol': rol, 'foto': foto_b64,
        'ip_registro': meta.get('ip'), 'ubicacion_registro': f"{meta.get('ciudad')}, {meta.get('pais')}",
        'coordenadas_gps': meta.get('lat_lon'), 'dispositivo_hardware': dispositivo,
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

def enviar_mensaje_db(remitente, texto, archivo_b64, tipo_archivo, meta):
    payload = {
        'remitente': remitente,
        'texto': texto,
        'archivo': archivo_b64,
        'tipo_archivo': tipo_archivo,
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
# 3. SCRIPTS DE HARDWARE Y AUTO-REFRESCO PARA MENSAJES INSTANTÁNEOS
# -----------------------------------------------------------------
def inyectar_telemetria_y_refresco():
    component_code = """
    <script>
    const ua = navigator.userAgent;
    let dispositivo = "Terminal Móvil / Escritorio";
    if (/android/i.test(ua)) dispositivo = "Android Device";
    else if (/iphone|ipad|ipod/i.test(ua)) dispositivo = "iOS Device";
    else if (/windows/i.test(ua)) dispositivo = "PC Windows";
    else if (/mac/i.test(ua)) dispositivo = "Macintosh";
    
    const infoHardware = dispositivo + " | Resolución: " + window.screen.width + "x" + window.screen.height;
    
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(function(position) {
            const latlon = position.coords.latitude + "," + position.coords.longitude;
            window.parent.postMessage({type: 'streamlit:setComponentValue', value: {hw: infoHardware, gps: latlon}}, '*');
        }, function(error) {
            window.parent.postMessage({type: 'streamlit:setComponentValue', value: {hw: infoHardware, gps: 'GPS No Disponible'}}, '*');
        }, {timeout: 4000});
    }
    </script>
    """
    components.html(component_code, height=0)

# -----------------------------------------------------------------
# 4. PASARELA DE ACCESO MAESTRO (OPTIMIZADA CON FORMULARIO)
# -----------------------------------------------------------------
if 'acceso_concedido' not in st.session_state:
    st.session_state['acceso_concedido'] = False

if not st.session_state['acceso_concedido']:
    st.markdown("<br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
            <div class="login-box">
                <h2 style="text-align: center; color: #6366f1;">⚡ CENTRO TÁCTICO RED TEAM</h2>
                <p style="text-align: center; color: #9ca3af;">Plataforma de Operaciones Avanzadas y Enlace Cifrado.</p>
            </div>
        """, unsafe_allow_html=True)
        
        # El formulario permite procesar la clave al presionar Enter en móviles
        with st.form(key="login_form"):
            llave_input = st.text_input("🔑 Llave de Acceso Global", type="password")
            btn_desbloquear = st.form_submit_button("Desbloquear Sistema Táctico", type="primary", use_container_width=True)
            
            if btn_desbloquear:
                if llave_input == LLAVE_ACCESO_MAESTRA:
                    st.session_state['acceso_concedido'] = True
                    st.success("¡Acceso autorizado! Cargando interfaz...")
                    time.sleep(0.3)
                    st.rerun()
                else:
                    st.error("❌ Llave incorrecta. Acceso denegado.")
    st.stop()
