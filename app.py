import streamlit as st
import time
import requests
import json
from PIL import Image
import io
import base64

# -----------------------------------------------------------------
# 1. CONFIGURACIÓN VISUAL Y MODO OSCURO TÁCTICO
# -----------------------------------------------------------------
st.set_page_config(page_title="Centro de Inteligencia Operativa", page_icon="🛡️", layout="wide")

st.markdown("""
    <style>
    .stApp {
        background-color: #0b0f19;
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
        background-color: #1e293b;
        padding: 15px;
        border-radius: 8px;
        border: 1px solid #334155;
        margin-bottom: 10px;
    }
    .login-box {
        background-color: #1e293b;
        padding: 30px;
        border-radius: 12px;
        border: 1px solid #334155;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
    }
    </style>
""", unsafe_allow_html=True)

FIREBASE_URL = "https://chat-2026-68203-default-rtdb.firebaseio.com/"

# Cédula maestra configurada para ti (Administrador Absoluto)
CEDULA_ADMIN_MAESTRO = "12345678"  # Cámbiala por tu cédula real si es distinta

# Llave de Acceso Global que compartes con tus familiares para dejarles entrar
LLAVE_ACCESO_MAESTRA = "VIP-2026-SECURE"

# -----------------------------------------------------------------
# 2. FUNCIONES DE INTELIGENCIA Y FORENSE
# -----------------------------------------------------------------
def obtener_metadatos_red():
    try:
        response = requests.get('https://ipapi.co/json/', timeout=3)
        if response.status_code == 200:
            data = response.json()
            return {
                'ip': data.get('ip', 'Desconocida'),
                'ciudad': data.get('city', 'Desconocida'),
                'pais': data.get('country_name', 'Desconocida'),
                'org': data.get('org', 'Red Desconocida')
            }
    except:
        pass
    try:
        ip_alt = requests.get('https://api.ipify.org?format=json', timeout=3).json().get('ip', 'Desconocida')
        return {'ip': ip_alt, 'ciudad': 'Localizada por IP', 'pais': 'N/A', 'org': 'N/A'}
    except:
        return {'ip': 'Local/Desconocida', 'ciudad': 'N/A', 'pais': 'N/A', 'org': 'N/A'}

def registrar_auditoria(usuario, accion, meta):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    payload = {
        'usuario': usuario,
        'accion': accion,
        'ip': meta.get('ip'),
        'ubicacion': f"{meta.get('ciudad')}, {meta.get('pais')}",
        'proveedor': meta.get('org'),
        'timestamp': timestamp
    }
    requests.post(f"{FIREBASE_URL}/auditoria_ip.json", data=json.dumps(payload))

def guardar_operador(cedula, nombre, rol, foto_b64, meta):
    if cedula == CEDULA_ADMIN_MAESTRO:
        rol = "Administrador Principal"
        
    payload = {
        'nombre': nombre,
        'cedula': cedula,
        'rol': rol,
        'foto': foto_b64,
        'ip_registro': meta.get('ip'),
        'ubicacion_registro': f"{meta.get('ciudad')}, {meta.get('pais')}",
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
# 3. PASARELLA DE ACCESO GLOBAL (LLAVE MAESTRA INICIAL)
# -----------------------------------------------------------------
if 'acceso_concedido' not in st.session_state:
    st.session_state['acceso_concedido'] = False

if not st.session_state['acceso_concedido']:
    st.markdown("<br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
            <div class="login-box">
                <h2 style="text-align: center; color: #3b82f6;">🛡️ ACCESO RESTRINGIDO</h2>
                <p style="text-align: center; color: #94a3b8;">Plataforma cifrada. Ingrese la llave maestra proporcionada por el administrador para continuar.</p>
            </div>
        """, unsafe_allow_html=True)
        
        codigo_ingresado = st.text_input("🔑 Llave de Acceso / Código Secreto", type="password")
        
        if st.button("Verificar Credencial", type="primary", use_container_width=True):
            if codigo_ingresado == LLAVE_ACCESO_MAESTRA:
                st.session_state['acceso_concedido'] = True
                st.success("¡Acceso autorizado a la pasarela principal!")
                time.sleep(0.5)
                st.rerun()
            else:
                st.error("❌ Código incorrecto. Acceso denegado.")
    st.stop()

# -----------------------------------------------------------------
# 4. GESTIÓN DE SESIÓN INTERNA (BIOMETRÍA Y REGISTRO)
# -----------------------------------------------------------------
if 'autenticado' not in st.session_state:
    st.session_state['autenticado'] = False
    st.session_state['usuario_actual'] = ""
    st.session_state['rol_actual'] = ""
    st.session_state['cedula_actual'] = ""

st.sidebar.title("🛡️ Centro Táctico 2026")

if not st.session_state['autenticado']:
    modo_auth = st.sidebar.radio("Seleccione Operación", ["Iniciar Sesión (Biometría)", "Registrar Operador / Familiar"])
    
    if modo_auth == "Iniciar Sesión (Biometría)":
        st.title("🔐 Validación de Identidad y Acceso")
        st.write("Ingrese su cédula y escanee su rostro para acceder de forma segura.")
        
        cedula_ingreso = st.text_input("Cédula / Identificador Único")
        foto_camara = st.camera_input("Verificación Biométrica Facial")
        
        if st.button("Autorizar Ingreso", type="primary"):
            if not cedula_ingreso or not foto_camara:
                st.warning("Debe ingresar su cédula y capturar la biometría facial.")
            else:
                user_data = obtener_operador(cedula_ingreso)
                if user_data:
                    meta = obtener_metadatos_red()
                    st.session_state['autenticado'] = True
                    st.session_state['usuario_actual'] = user_data.get('nombre')
                    st.session_state['cedula_actual'] = cedula_ingreso
                    
                    if cedula_ingreso == CEDULA_ADMIN_MAESTRO or user_data.get('rol') == "Administrador Principal":
                        st.session_state['rol_actual'] = "Administrador Principal"
                    else:
                        st.session_state['rol_actual'] = "Familiar / Operador"
                        
                    registrar_auditoria(user_data.get('nombre'), "Acceso autorizado con éxito", meta)
                    st.success(f"¡Identidad verificada! Bienvenido, {user_data.get('nombre')}.")
                    st.rerun()
                else:
                    st.error("Cédula no encontrada en la base de datos central.")

    elif modo_auth == "Registrar Operador / Familiar":
        st.title("📝 Registro Biométrico y Extracción de Metadatos")
        st.write("Complete los datos para dar de alta a un usuario en el sistema seguro.")
        
        reg_nombre = st.text_input("Nombre Completo")
        reg_cedula = st.text_input("Cédula o ID Único")
        reg_foto = st.camera_input("Captura Facial Obligatoria")
        
        if st.button("Registrar y Extraer Metadatos", type="primary"):
            if not reg_nombre or not reg_cedula or not reg_foto:
                st.warning("Todos los campos y la captura facial son obligatorios.")
            else:
                meta = obtener_metadatos_red()
                bytes_img = reg_foto.getvalue()
                foto_b64 = base64.b64encode(bytes_img).decode('utf-8')
                
                rol_asignado = "Administrador Principal" if reg_cedula == CEDULA_ADMIN_MAESTRO else "Familiar / Operador"
                
                guardar_operador(reg_cedula, reg_nombre, rol_asignado, foto_b64, meta)
                registrar_auditoria(reg_nombre, f"Registro exitoso con IP {meta.get('ip')}", meta)
                st.success(f"¡Registro completado! Metadatos extraídos y almacenados en tu base de datos.")

else:
    # -----------------------------------------------------------------
    # 5. NAVEGACIÓN SEGÚN JERARQUÍA DE USUARIO
    # -----------------------------------------------------------------
    st.sidebar.markdown(f"👤 **Usuario:** `{st.session_state['usuario_actual']}`")
    st.sidebar.markdown(f"🔑 **Rol:** `{st.session_state['rol_actual']}`")
    
    opciones_menu = ["Canal de Chat Seguro"]
    
    # SOLO TÚ (Administrador Principal) verás los paneles de rastreo e inteligencia
    if st.session_state['rol_actual'] == "Administrador Principal":
        opciones_menu.extend(["Panel de Control & Rostros", "Auditoría Forense de Redes"])
    
    opciones_menu.append("Cerrar Sesión")
    seleccion = st.sidebar.selectbox("Navegación Táctica", opciones_menu)
    
    if seleccion == "Cerrar Sesión":
        st.session_state['autenticado'] = False
        st.rerun()

    # MÓDULO: CHAT SEGURO ESTILO WHATSAPP OSCURO
    elif seleccion == "Canal de Chat Seguro":
        st.title("💬 Canal de Comunicaciones Cifradas")
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
                st.info("Canal seguro abierto. Comience la transmisión de mensajes.")

        with st.form(key='chat_form_moderno', clear_on_submit=True):
            col_txt, col_btn = st.columns([5, 1])
            with col_txt:
                texto_msj = st.text_input("Mensaje cifrado...", label_visibility="collapsed")
            with col_btn:
                enviar_btn = st.form_submit_button("Enviar 🚀", use_container_width=True)
                
            if enviar_btn and texto_msj:
                meta_actual = obtener_metadatos_red()
                enviar_mensaje_db(st.session_state['usuario_actual'], texto_msj, meta_actual)
                st.rerun()

    # MÓDULO EXCLUSIVO ADMIN: PANEL DE CONTROL Y ROSTROS GUARDADOS
    elif seleccion == "Panel de Control & Rostros":
        st.title("🛡️ Panel de Control y Base de Datos Biométrica")
        st.write("Visualización exclusiva para el administrador de rostros, cédulas y metadatos de usuarios registrados.")
        
        operadores = obtener_todos_operadores()
        st.subheader(f"👥 Usuarios Registrados en la Base de Datos ({len(operadores)})")
        
        for ced, datos in operadores.items():
            with st.expander(f"Cédula: {ced} | {datos.get('nombre')} ({datos.get('rol')})"):
                col1, col2 = st.columns([1, 2])
                with col1:
                    if 'foto' in datos and datos['foto']:
                        try:
                            img_bytes = base64.b64decode(datos['foto'])
                            st.image(Image.open(io.BytesIO(img_bytes)), width=140, caption="Biometría Facial")
                        except:
                            st.write("Imagen no disponible")
                with col2:
                    st.markdown(f"**Nombre Completo:** {datos.get('nombre')}")
                    st.markdown(f"**Cédula / ID:** {datos.get('cedula')}")
                    st.markdown(f"**Rol Asignado:** {datos.get('rol')}")
                    st.markdown(f"**IP de Registro:** `{datos.get('ip_registro', 'N/A')}`")
                    st.markdown(f"**Ubicación de Registro:** {datos.get('ubicacion_registro', 'N/A')}")
                    st.markdown(f"**Fecha de Alta:** {datos.get('fecha_registro')}")

    # MÓDULO EXCLUSIVO ADMIN: AUDITORÍA FORENSE DE REDES
    elif seleccion == "Auditoría Forense de Redes":
        st.title("🕵️ Inteligencia de Rastreo y Conexiones")
        st.write("Registro detallado de direcciones IP, ubicaciones y actividad de acceso en tiempo real.")
        
        registros = obtener_auditorias()
        if registros:
            items_reg = sorted(registros.items(), key=lambda x: x[0], reverse=True)
            for key, reg in items_reg[:50]:
                st.markdown(f"""
                    <div class="metric-card">
                        🕒 <b>{reg.get('timestamp')}</b> | 👤 <b>{reg.get('usuario')}</b><br>
                        ⚡ Acción: <i>{reg.get('accion')}</i><br>
                        🌐 IP Pública: <code>{reg.get('ip')}</code> | 📍 Ubicación: <b>{reg.get('ubicacion')}</b> | 🏢 Red: {reg.get('proveedor', 'N/A')}
                    </div>
                """, unsafe_allow_html=True)
        else:
            st.write("No hay registros de auditoría almacenados.")
    
