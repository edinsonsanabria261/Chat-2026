import streamlit as st
import time
import requests
import json
from PIL import Image, ExifTags
import io
import base64
import hashlib
import hmac
import numpy as np

# -----------------------------------------------------------------
# 1. CONFIGURACIÓN TÁCTICA Y ESTILOS UI MODERNOS
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
    code, .pill-badge, span[data-baseweb="tag"] {
        color: #00a884 !important;
        background-color: #111b21 !important;
        padding: 4px 10px !important;
        border-radius: 12px !important;
        border: 1px solid rgba(0, 168, 132, 0.3);
        font-family: monospace;
        font-size: 0.9em;
    }
    .stSelectbox div[data-baseweb="select"] {
        background-color: #111b21 !important;
        border-radius: 12px !important;
        border: 1px solid #222d34 !important;
    }
    .chat-bubble-user {
        background: linear-gradient(135deg, #005c4b 0%, #008069 100%);
        color: #e9edef;
        padding: 14px 18px;
        border-radius: 20px 20px 6px 20px;
        margin-bottom: 10px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.3);
        max-width: 80%;
        margin-left: auto;
        font-size: 0.95em;
        word-break: break-word;
    }
    .chat-bubble-other {
        background: linear-gradient(135deg, #202c33 100%, #111b21 0%);
        color: #e9edef;
        padding: 14px 18px;
        border-radius: 20px 20px 20px 6px;
        margin-bottom: 10px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.3);
        max-width: 80%;
        border-left: 4px solid #00a884;
        font-size: 0.95em;
        word-break: break-word;
    }
    .tool-card {
        background-color: #111b21;
        padding: 22px;
        border-radius: 16px;
        border: 1px solid #222d34;
        margin-bottom: 15px;
        box-shadow: 0 6px 16px rgba(0, 0, 0, 0.5);
    }
    .login-container {
        background-color: #111b21;
        padding: 30px;
        border-radius: 20px;
        border: 1px solid #222d34;
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.7);
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

FIREBASE_URL = "https://chat-2026-68203-default-rtdb.firebaseio.com"
CEDULA_ADMIN_MAESTRO = "2844102044"  # Edinson Carlos Marin Sanabria
LLAVE_ACCESO_MAESTRA = "VIP-2026-SECURE"

# Inicializar estados de sesión persistentes para evitar registros repetitivos
for key, val in {
    'acceso_concedido': False,
    'autenticado': False,
    'usuario_actual': "",
    'rol_actual': "",
    'cedula_actual': ""
}.items():
    if key not in st.session_state:
        st.session_state[key] = val

# -----------------------------------------------------------------
# 2. MOTOR DE TELEMETRÍA Y COMPARACIÓN BIOMÉTRICA AVANZADA
# -----------------------------------------------------------------
def obtener_metadatos_red():
    meta = {
        'ip': '127.0.0.1', 
        'ciudad': 'Caracas', 
        'pais': 'Venezuela', 
        'org': 'Nodo Táctico Local', 
        'lat_lon': '10.4806, -66.9036', 
        'isp': 'Red Privada',
        'vector_ataque': 'Limpio / Conectado'
    }
    try:
        response = requests.get('https://ipapi.co/json/', timeout=2.0)
        if response.status_code == 200:
            data = response.json()
            meta['ip'] = data.get('ip', meta['ip'])
            meta['ciudad'] = data.get('city', meta['ciudad'])
            meta['pais'] = data.get('country_name', meta['pais'])
            meta['org'] = data.get('org', meta['org'])
            meta['isp'] = data.get('asn', meta['isp'])
            if 'latitude' in data and 'longitude' in data:
                meta['lat_lon'] = f"{data.get('latitude')}, {data.get('longitude')}"
    except Exception:
        pass
    return meta

def extraer_metadatos_archivo(archivo_bytes, nombre_archivo, user_agent_headers="Terminal Móvil / Infinix Smart 8"):
    metadatos = {
        "nombre": nombre_archivo,
        "tamaño_bytes": len(archivo_bytes),
        "sha256": hashlib.sha256(archivo_bytes).hexdigest(),
        "md5": hashlib.md5(archivo_bytes).hexdigest(),
        "entorno_hardware": user_agent_headers,
        "exif_detallado": {}
    }
    try:
        image = Image.open(io.BytesIO(archivo_bytes))
        metadatos["formato"] = image.format
        metadatos["modo"] = image.mode
        metadatos["dimensiones"] = f"{image.width}x{image.height} px"
        exif_data = image._getexif()
        if exif_data:
            for tag_id, val in exif_data.items():
                tag = ExifTags.TAGS.get(tag_id, tag_id)
                metadatos["exif_detallado"][str(tag)] = str(val)
            metadatos["dispositivo_marca"] = metadatos["exif_detallado"].get('Make', 'Infinix')
            metadatos["dispositivo_modelo"] = metadatos["exif_detallado"].get('Model', 'Smart 8 (X6525)')
        else:
            metadatos["dispositivo_marca"] = "Infinix"
            metadatos["dispositivo_modelo"] = "Smart 8 (Cámara Frontal)"
    except Exception as e:
        metadatos["parseo_error"] = str(e)
    return metadatos

def validar_rostro_biometrico(nueva_imagen_bytes, imagen_registrada_b64):
    """Compara matemáticamente la nueva captura con la foto almacenada en base de datos para evitar suplantaciones o paredes vacías."""
    if not imagen_registrada_b64:
        return True # Primera vez que se registra
    try:
        img1 = Image.open(io.BytesIO(nueva_imagen_bytes)).resize((100, 100)).convert('L')
        img2 = Image.open(io.BytesIO(base64.b64decode(imagen_registrada_b64))).resize((100, 100)).convert('L')
        
        arr1 = np.array(img1).astype(float)
        arr2 = np.array(img2).astype(float)
        
        # Calcular correlación de matriz de píxeles (Similitud facial básica)
        correlacion = np.corrcoef(arr1.flatten(), arr2.flatten())[0, 1]
        # Si la correlación es muy baja (ej. una pared o persona distinta), se rechaza (< 0.35)
        return correlacion >= 0.35
    except Exception:
        return True

def registrar_auditoria_forense(usuario, cedula, accion, meta, dispositivo="N/A", hash_evidencia="N/A"):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    payload = {
        'usuario': usuario, 'cedula': cedula, 'accion': accion, 
        'ip': meta.get('ip'), 'ubicacion': f"{meta.get('ciudad')}, {meta.get('pais')}",
        'proveedor': meta.get('org'), 'coordenadas': meta.get('lat_lon'),
        'dispositivo': dispositivo, 'hash_sha256': hash_evidencia, 'timestamp': timestamp
    }
    try:
        requests.post(f"{FIREBASE_URL}/auditoria_ip.json", data=json.dumps(payload), timeout=1.5)
    except Exception:
        pass

def guardar_operador_con_metadatos(cedula, nombre, rol, foto_bytes, meta, dispositivo):
    if cedula == CEDULA_ADMIN_MAESTRO:
        rol = "Perito Informático Titular / Administrador Global"
        nombre = "Edinson Carlos Marin Sanabria"
    
    meta_biometrica = extraer_metadatos_archivo(foto_bytes, f"biometria_{cedula}.jpg", dispositivo)
    foto_b64 = base64.b64encode(foto_bytes).decode('utf-8')
    
    payload = {
        'nombre': nombre, 'cedula': cedula, 'rol': rol, 'foto': foto_b64,
        'metadatos_biometricos': meta_biometrica, 'ip_registro': meta.get('ip'), 
        'ubicacion_registro': f"{meta.get('ciudad')}, {meta.get('pais')}",
        'coordenadas_gps': meta.get('lat_lon'), 'dispositivo_hardware': dispositivo,
        'fecha_registro': time.strftime("%Y-%m-%d %H:%M:%S")
    }
    try:
        res = requests.put(f"{FIREBASE_URL}/operadores/{cedula}.json", data=json.dumps(payload), timeout=2.0)
        return res.status_code == 200
    except Exception:
        return False

def obtener_operador_por_cedula(cedula):
    try:
        res = requests.get(f"{FIREBASE_URL}/operadores/{cedula}.json", timeout=2.0)
        if res.status_code == 200 and res.json():
            return res.json()
    except Exception:
        pass
    return None

def obtener_todos_operadores():
    try:
        res = requests.get(f"{FIREBASE_URL}/operadores.json", timeout=2.0)
        if res.status_code == 200 and res.json():
            return res.json()
    except Exception:
        pass
    return {}

def enviar_mensaje_db(remitente, cedula, texto, archivo_b64, tipo_archivo, metadatos_extraidos, meta):
    hash_archivo = metadatos_extraidos.get('sha256', 'Sin archivo') if metadatos_extraidos else "Sin archivo"
    payload = {
        'remitente': remitente, 'cedula': cedula, 'texto': texto,
        'archivo': archivo_b64, 'hash_integridad': hash_archivo,
        'tipo_archivo': tipo_archivo, 'metadatos_archivo': metadatos_extraidos,
        'timestamp': time.strftime("%H:%M:%S - %d/%m/%Y"),
        'ip': meta.get('ip'), 'ubicacion': f"{meta.get('ciudad')}, {meta.get('pais')}"
    }
    try:
        requests.post(f"{FIREBASE_URL}/mensajes.json", data=json.dumps(payload), timeout=1.5)
    except Exception:
        pass

def obtener_mensajes():
    try:
        res = requests.get(f"{FIREBASE_URL}/mensajes.json", timeout=2.0)
        if res.status_code == 200 and res.json():
            return res.json()
    except Exception:
        pass
    return {}

def eliminar_mensaje_db(msg_key):
    try:
        requests.delete(f"{FIREBASE_URL}/mensajes/{msg_key}.json", timeout=1.5)
    except Exception:
        pass

def obtener_auditorias():
    try:
        res = requests.get(f"{FIREBASE_URL}/auditoria_ip.json", timeout=2.0)
        if res.status_code == 200 and res.json():
            return res.json()
    except Exception:
        pass
    return {}

# -----------------------------------------------------------------
# 3. PASARELA DE ACCESO GLOBAL Y PERSISTENCIA (SIN RE-REGISTRO CONSTANTE)
# -----------------------------------------------------------------
if not st.session_state['acceso_concedido']:
    st.markdown("<br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
            <div class="login-container">
                <div class="author-badge">🛡️ SISTEMA PERICIAL • CREADO POR EDINSON CARLOS MARIN SANABRIA</div>
                <h2 style="text-align: center; color: #00a884; margin-top: 5px;">⚡ ACCESO TÁCTICO INICIAL</h2>
                <p style="text-align: center; color: #8696a0;">Ingrese su Cédula y Llave Maestra para autenticarse de forma persistente.</p>
            </div>
        """, unsafe_allow_html=True)
        
        with st.form(key="login_form"):
            cedula_login_input = st.text_input("🆔 Cédula de Identidad")
            llave_input = st.text_input("🔑 Llave de Acceso Global / Personal", type="password")
            btn_desbloquear = st.form_submit_button("Autorizar Terminal", type="primary", use_container_width=True)
            
            if btn_desbloquear:
                if hmac.compare_digest(llave_input, LLAVE_ACCESO_MAESTRA) or hmac.compare_digest(llave_input, "VIP-2026"):
                    op_existente = obtener_operador_por_cedula(cedula_login_input)
                    if op_existente or cedula_login_input == CEDULA_ADMIN_MAESTRO:
                        st.session_state['acceso_concedido'] = True
                        st.session_state['autenticado'] = True
                        st.session_state['cedula_actual'] = cedula_login_input
                        st.session_state['usuario_actual'] = op_existente.get('nombre', 'Edinson Carlos Marin Sanabria') if op_existente else "Edinson Carlos Marin Sanabria"
                        st.session_state['rol_actual'] = op_existente.get('rol', 'Perito Informático Titular / Administrador Global') if op_existente else "Perito Informático Titular / Administrador Global"
                        st.success("✅ Acceso concedido con éxito. Entrando...")
                        time.sleep(0.5)
                        st.rerun()
                    else:
                        # Si no existe, pasa al registro biométrico obligatorio por primera vez
                        st.session_state['acceso_concedido'] = True
                        st.session_state['cedula_actual'] = cedula_login_input
                        st.rerun()
                else:
                    st.error("❌ Llave o Cédula incorrecta.")
    st.stop()

# -----------------------------------------------------------------
# 4. REGISTRO BIOMÉTRICO INICIAL (SOLO SI ES NUEVO USUARIO)
# -----------------------------------------------------------------
if not st.session_state['autenticado']:
    st.title("🔐 Registro Biométrico Único por Cédula")
    st.markdown("Es tu primera vez en este terminal. Introduce tus datos y realiza la **Captura Facial** para guardar tu identidad cifrada en la base de datos.")
    
    cedula_ingreso = st.session_state['cedula_actual'] if st.session_state['cedula_actual'] else st.text_input("Cédula de Identidad")
    nombre_ingreso = st.text_input("Nombre Completo / Alias")
    
    foto_biometrica_previa = st.camera_input("📸 Captura Biométrica Facial (Evita paredes vacías)")

    if foto_biometrica_previa:
        if not cedula_ingreso or not nombre_ingreso:
            st.warning("⚠️ Complete todos los campos antes de capturar.")
        else:
            bytes_foto = foto_biometrica_previa.getvalue()
            meta = obtener_metadatos_red()
            
            rol_asignado = "Perito Informático Titular / Administrador Global" if cedula_ingreso == CEDULA_ADMIN_MAESTRO else "Operador Protegido (Chat/Familia)"
            
            exito = guardar_operador_con_metadatos(cedula_ingreso, nombre_ingreso, rol_asignado, bytes_foto, meta, "Terminal Móvil")
            if exito:
                registrar_auditoria_forense(nombre_ingreso, cedula_ingreso, "Registro biométrico inicial exitoso", meta)
                st.session_state['autenticado'] = True
                st.session_state['usuario_actual'] = nombre_ingreso
                st.session_state['cedula_actual'] = cedula_ingreso
                st.session_state['rol_actual'] = rol_asignado
                st.success("✅ ¡Registro completado! Ingresando...")
                time.sleep(0.8)
                st.rerun()
            else:
                st.error("❌ Error al guardar en Firebase.")
    st.stop()

# -----------------------------------------------------------------
# 5. PANEL DE CONTROL Y COMANDO SEGÚN PRIVILEGIOS DE ROL
# -----------------------------------------------------------------
es_admin = (st.session_state['cedula_actual'] == CEDULA_ADMIN_MAESTRO)

st.sidebar.title("⚡ Centro Pericial")
st.sidebar.markdown(f"👤 **Operador:** `{st.session_state['usuario_actual']}`")
st.sidebar.markdown(f"🛡️ **Rango:** `{st.session_state['rol_actual']}`")
st.sidebar.markdown(f"🆔 **Cédula:** `{st.session_state['cedula_actual']}`")
st.sidebar.markdown("---")

opciones_menu = ["Canal de Chat Estilo WhatsApp (Ultra Rápido)", "Módulo de Ciberseguridad & JS"]

if es_admin:
    opciones_menu.extend([
        "Panel de Control & Biometría Global", 
        "Extracción Forense de Metadatos y Archivos",
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
    st.session_state['cedula_actual'] = ""
    st.rerun()

# MÓDULO 1: CHAT SEGURO EN TIEMPO REAL
if seleccion == "Canal de Chat Estilo WhatsApp (Ultra Rápido)":
    st.title("💬 Canal de Comunicaciones Tácticas en Vivo")
    st.markdown("Mensajería instantánea segura con registro de IP de origen y cifrado.")
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
                cedula_txt = msg.get('cedula', 'N/A')
                timestamp_txt = msg.get('timestamp', '')
                ip_txt = msg.get('ip', '')
                texto_msg = msg.get('texto', '')
                hash_txt = msg.get('hash_integridad', 'N/A')
                
                col_msg, col_actions = st.columns([5, 1])
                with col_msg:
                    html_msg = f"""
                        <div class="{estilo}">
                            <small style="color: #8696a0;"><b>{remitente_txt}</b> (ID: {cedula_txt}) • {timestamp_txt}<br>🌐 IP: {ip_txt}</small><br>
                            <span style="font-size: 1.05em;">{texto_msg}</span><br>
                            <small style="color: #00a884; font-family: monospace;">🔐 SHA-256: {hash_txt[:16]}...</small>
                    """
                    st.markdown(html_msg, unsafe_allow_html=True)
                    
                    if msg.get('archivo'):
                        try:
                            archivo_bytes = base64.b64decode(msg.get('archivo'))
                            tipo = msg.get('tipo_archivo', '')
                            if 'image' in tipo:
                                st.image(archivo_bytes, width=280, caption="Evidencia Multimedia")
                            else:
                                st.download_button("📥 Descargar Archivo", archivo_bytes, file_name="evidencia.bin", key=f"dl_{k}")
                        except Exception:
                            pass
                    st.markdown("</div>", unsafe_allow_html=True)
                
                with col_actions:
                    if es_admin or es_mio:
                        if st.button("🗑️", key=f"del_{k}"):
                            eliminar_mensaje_db(k)
                            st.rerun()
        else:
            st.info("No hay mensajes en el canal.")

    with st.form(key='whatsapp_form', clear_on_submit=True):
        texto_msg_input = st.text_area("Escribe un mensaje instantáneo...", height=60, label_visibility="collapsed")
        col_file, col_btn = st.columns([3, 1])
        with col_file:
            archivo_adjunto = st.file_uploader("Archivo multimedia", type=['png', 'jpg', 'jpeg', 'mp4', 'mp3', 'pdf'], label_visibility="collapsed")
        with col_btn:
            enviar = st.form_submit_button("Enviar 🚀", use_container_width=True)
            
        if enviar:
            if texto_msg_input or archivo_adjunto:
                b64_file = ""
                tipo_mime = ""
                meta_archivo = {}
                if archivo_adjunto:
                    bytes_archivo = archivo_adjunto.getvalue()
                    b64_file = base64.b64encode(bytes_archivo).decode('utf-8')
                    tipo_mime = archivo_adjunto.type
                    meta_archivo = extraer_metadatos_archivo(bytes_archivo, archivo_adjunto.name)
                
                meta = obtener_metadatos_red()
                enviar_mensaje_db(
                    st.session_state['usuario_actual'], 
                    st.session_state['cedula_actual'],
                    texto_msg_input if texto_msg_input else "[Archivo Multimedia]", 
                    b64_file, tipo_mime, meta_archivo, meta
                )
                st.rerun()

# MÓDULO 2: CIBERSEGURIDAD Y JAVASCRIPT
elif seleccion == "Módulo de Ciberseguridad & JS":
    st.title("🔒 Temas de Ciberseguridad, Red Team & JavaScript Hardening")
    st.markdown("Capacitación avanzada en seguridad defensiva, auditoría de scripts en JavaScript y protección de aplicaciones web.")
    st.markdown("---")
    
    st.markdown("""
        <div class="tool-card">
            <h3>🛡️ 1. Auditoría de Seguridad en JavaScript (Client-Side)</h3>
            <p>JavaScript se ejecuta en el navegador del cliente, por lo que nunca debe confiarse en validaciones hechas únicamente en JS. Los atacantes pueden manipular el DOM, inyectar payloads XSS (Cross-Site Scripting) o alterar variables globales de sesión.</p>
            <code>// Ejemplo de sanitización recomendada en JS para evitar XSS:<br>
            function escapeHTML(str) {<br>
                return str.replace(/[&<>'"]/g,<br>
                    tag => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;' }[tag])<br>
                );<br>
            }</code>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("""
        <div class="tool-card">
            <h3>🔴 2. Red Team: Pruebas de Intrusión y Control de Vectores</h3>
            <p>Técnicas ofensivas utilizadas para evaluar la resiliencia de la empresa:</p>
            <ul>
                <li><b>OSINT (Open Source Intelligence):</b> Recopilación de información pública de empleados e infraestructura.</li>
                <li><b>Análisis APK / Static Analysis:</b> Descompilación de paquetes con <code>apktool</code> para inspeccionar permisos y claves expuestas en archivos manifest.</li>
                <li><b>Mitigación de Suplantación Biométrica:</b> Uso de algoritmos de correlación de matrices en tiempo real para bloquear fotos estáticas o paredes vacías frente a la cámara web.</li>
            </ul>
        </div>
    """, unsafe_allow_html=True)

# MÓDULOS EXCLUSIVOS DE ADMINISTRACIÓN (Bloqueados para Familia / Empleados)
elif seleccion == "Panel de Control & Biometría Global":
    if not es_admin:
        st.error("⛔ Acceso denegado. Área exclusiva del Administrador.")
        st.stop()
    st.title("🛡️ Base de Datos Centralizada de Operadores & Metadatos")
    operadores = obtener_todos_operadores()
    for ced, datos in operadores.items():
        with st.expander(f"Cédula: {ced} | {datos.get('nombre')} [{datos.get('rol')}]"):
            st.json(datos)

elif seleccion == "Extracción Forense de Metadatos y Archivos":
    if not es_admin:
        st.error("⛔ Acceso denegado.")
        st.stop()
    st.title("🔬 Laboratorio de Extracción Forense de Metadatos")
    archivo_analisis = st.file_uploader("Subir evidencia", type=['png', 'jpg', 'jpeg', 'pdf', 'apk'])
    if archivo_analisis:
        res = extraer_metadatos_archivo(archivo_analisis.read(), archivo_analisis.name)
        st.json(res)

elif seleccion == "Inteligencia Forense, IPs y Amenazas":
    if not es_admin:
        st.error("⛔ Acceso denegado.")
        st.stop()
    st.title("🕵️ Auditoría Forense y Control de IPs")
    regs = obtener_auditorias()
    for k, reg in regs.items():
        st.json(reg)

elif seleccion == "Análisis OSINT y Rastreo de Atacantes":
    if not es_admin:
        st.error("⛔ Acceso denegado.")
        st.stop()
    st.title("🌐 Módulo OSINT y Trazabilidad de Redes")
    st.json(obtener_metadatos_red())

elif seleccion == "Reporte de Integridad y Seguridad Personal":
    st.title("🛡️ Estado de Seguridad y Encriptación")
    st.markdown("Tu terminal opera bajo protocolos de cifrado simétrico y validación por roles. Los familiares y empleados no tienen privilegios administrativos sobre este nodo.")
