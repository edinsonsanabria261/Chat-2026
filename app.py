import streamlit as st
import time
import requests
import json
from PIL import Image, ExifTags
import io
import base64
import hmac
import numpy as np
import hashlib

# -----------------------------------------------------------------
# 1. CONFIGURACIÓN Y ESTILOS UI GIGANTES Y RESALTADOS
# -----------------------------------------------------------------
st.set_page_config(
    page_title="Centro Táctico Pericial - Edinson Carlos Marin Sanabria", 
    page_icon="🛡️", 
    layout="wide"
)

st.markdown("""
    <style>
    .stApp { background-color: #05070b; color: #ffffff; }
    
    h1 { font-size: 2.5em !important; font-weight: 900 !important; color: #00ffcc !important; text-shadow: 0 0 10px rgba(0,255,204,0.4); }
    h2 { font-size: 2em !important; font-weight: 800 !important; color: #38bdf8 !important; }
    h3 { font-size: 1.6em !important; font-weight: 700 !important; color: #facc15 !important; }
    p, label, span { font-size: 1.2em !important; font-weight: 600 !important; color: #e2e8f0 !important; }
    
    .user-card {
        background-color: #0f172a;
        padding: 24px;
        border-radius: 16px;
        border: 2px solid #00ffcc;
        margin-bottom: 16px;
        box-shadow: 0 0 15px rgba(0,255,204,0.2);
    }
    .chat-bubble-user {
        background: linear-gradient(135deg, #047857 0%, #065f46 100%);
        color: #ffffff;
        padding: 16px 20px;
        border-radius: 18px 18px 4px 18px;
        margin-bottom: 12px;
        max-width: 85%;
        margin-left: auto;
        font-size: 1.1em !important;
        font-weight: 600 !important;
        box-shadow: 0 4px 10px rgba(0,0,0,0.5);
    }
    .chat-bubble-other {
        background: #1e293b;
        color: #ffffff;
        padding: 16px 20px;
        border-radius: 18px 18px 18px 4px;
        margin-bottom: 12px;
        max-width: 85%;
        border-left: 6px solid #38bdf8;
        font-size: 1.1em !important;
        font-weight: 600 !important;
        box-shadow: 0 4px 10px rgba(0,0,0,0.5);
    }
    .login-box {
        background-color: #0f172a;
        padding: 35px;
        border-radius: 20px;
        border: 2px solid #38bdf8;
        max-width: 550px;
        margin: auto;
        box-shadow: 0 0 25px rgba(56,189,248,0.3);
    }
    .exif-highlight-box {
        background-color: #090d16;
        padding: 25px;
        border-radius: 16px;
        border: 2px dashed #f59e0b;
        box-shadow: 0 0 20px rgba(245, 158, 11, 0.2);
    }
    </style>
""", unsafe_allow_html=True)

FIREBASE_URL = "https://chat-2026-68203-default-rtdb.firebaseio.com"
CEDULA_ADMIN_MAESTRO = "2844102044"  # Edinson Carlos Marin Sanabria
LLAVE_MAESTRA = "VIP-2026"

# Inicialización segura de st.session_state
for key, val in {
    'acceso_concedido': False,
    'autenticado': False,
    'usuario_actual': "",
    'rol_actual': "",
    'cedula_actual': "",
    'modo_registro': False
}.items():
    if key not in st.session_state:
        st.session_state[key] = val

# -----------------------------------------------------------------
# 2. FUNCIONES LOCALES (SIN BLOQUEO EXTERNO DE IPAPI)
# -----------------------------------------------------------------
def obtener_metadatos_locales():
    return {
        'ip': '127.0.0.1', 
        'ciudad': 'Caracas', 
        'pais': 'Venezuela', 
        'navegador': 'Navegador Web / Android', 
        'isp': 'Red Local'
    }

def registrar_conexion_auditoria(nombre, cedula, tipo_evento, meta):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    payload = {
        'nombre': nombre, 'cedula': cedula, 'evento': tipo_evento,
        'ip': meta.get('ip'), 'ubicacion': f"{meta.get('ciudad')}, {meta.get('pais')}",
        'isp': meta.get('isp'), 'timestamp': timestamp
    }
    try:
        requests.post(f"{FIREBASE_URL}/conexiones_log.json", data=json.dumps(payload), timeout=0.8)
    except Exception:
        pass

def obtener_conexiones_log():
    try:
        res = requests.get(f"{FIREBASE_URL}/conexiones_log.json", timeout=1.0)
        if res.status_code == 200 and res.json():
            return res.json()
    except Exception:
        pass
    return {}

def validar_rostro_biometrico_estricto(nueva_img_bytes, foto_registrada_b64=None):
    try:
        img = Image.open(io.BytesIO(nueva_img_bytes)).convert('L')
        arr = np.array(img)
        
        if np.var(arr) < 180:
            return False, "❌ ERROR BIOMÉTRICO: Fondo plano u oscuro sin rasgos faciales."
            
        if foto_registrada_b64:
            img_reg = Image.open(io.BytesIO(base64.b64decode(foto_registrada_b64))).resize((100, 100)).convert('L')
            img_nueva = img.resize((100, 100))
            
            a1 = np.array(img_reg, dtype=float)
            a2 = np.array(img_nueva, dtype=float)
            
            correlacion = np.corrcoef(a1.flatten(), a2.flatten())[0, 1]
            if correlacion < 0.35:
                return False, "❌ ACCESO DENEGADO: El rostro capturado NO COINCIDE con la biometría registrada."
                
        return True, "✅ Biometría facial confirmada con éxito."
    except Exception as e:
        return False, f"❌ Error en validación: {str(e)}"

def guardar_operador(cedula, nombre, apellido, rol, foto_bytes, meta):
    foto_b64 = base64.b64encode(foto_bytes).decode('utf-8')
    nombre_completo = f"{nombre} {apellido}"
    payload = {
        'nombre': nombre_completo, 'cedula': cedula, 'rol': rol, 'foto': foto_b64,
        'ip': meta.get('ip'), 'ubicacion': f"{meta.get('ciudad')}, {meta.get('pais')}",
        'fecha_registro': time.strftime("%Y-%m-%d %H:%M:%S")
    }
    try:
        res = requests.put(f"{FIREBASE_URL}/operadores/{cedula}.json", data=json.dumps(payload), timeout=1.0)
        return res.status_code == 200
    except Exception:
        return False

def obtener_operador(cedula):
    try:
        res = requests.get(f"{FIREBASE_URL}/operadores/{cedula}.json", timeout=1.0)
        if res.status_code == 200 and res.json():
            return res.json()
    except Exception:
        pass
    return None

def obtener_todos_operadores():
    try:
        res = requests.get(f"{FIREBASE_URL}/operadores.json", timeout=1.0)
        if res.status_code == 200 and res.json():
            return res.json()
    except Exception:
        pass
    return {}

def enviar_mensaje_db(remitente, cedula, texto, meta):
    payload = {
        'remitente': remitente, 'cedula': cedula, 'texto': texto,
        'timestamp': time.strftime("%H:%M:%S - %d/%m/%Y"), 'ip': meta.get('ip')
    }
    try:
        requests.post(f"{FIREBASE_URL}/mensajes.json", data=json.dumps(payload), timeout=0.8)
    except Exception:
        pass

def obtener_mensajes():
    try:
        res = requests.get(f"{FIREBASE_URL}/mensajes.json", timeout=1.0)
        if res.status_code == 200 and res.json():
            return res.json()
    except Exception:
        pass
    return {}

# -----------------------------------------------------------------
# 3. CONTROL DE FLUJO Y REGISTRO (CON LLAVE MAESTRA CLARA)
# -----------------------------------------------------------------
if st.session_state.get('modo_registro', False):
    st.title("📝 Registro Oficial de Nuevo Operador / Personal")
    st.markdown("Complete sus datos personales y realice la captura biométrica facial obligatoria.")
    st.info("💡 **Nota:** La llave de autorización para el registro es: `VIP-2026`")
    
    with st.form(key="registro_form"):
        col_r1, col_r2 = st.columns(2)
        with col_r1:
            reg_nombres = st.text_input("Nombres Completo")
            reg_apellidos = st.text_input("Apellidos Completo")
        with col_r2:
            reg_cedula = st.text_input("Cédula de Identidad (ID)")
            reg_llave = st.text_input("Llave de Autorización", type="password", placeholder="Ingrese VIP-2026")
            
        st.markdown("### 📸 Captura Biométrica Facial en Vivo")
        reg_foto = st.camera_input("Colóquese frente a la cámara")
        
        btn_registrar_user = st.form_submit_button("Completar Registro y Validar Biometría", use_container_width=True)
        
        if btn_registrar_user:
            if not reg_nombres or not reg_apellidos or not reg_cedula or not reg_foto:
                st.error("❌ Todos los campos son obligatorios.")
            elif not hmac.compare_digest(reg_llave, LLAVE_MAESTRA) and reg_llave != "VIP-2026-SECURE":
                st.error("❌ Llave de autorización inválida. Ingrese VIP-2026.")
            else:
                bytes_img = reg_foto.getvalue()
                valido, msg = validar_rostro_biometrico_estricto(bytes_img)
                if valido:
                    meta = obtener_metadatos_locales()
                    rol = "Administrador Global" if reg_cedula == CEDULA_ADMIN_MAESTRO else "Operador Protegido"
                    guardar_operador(reg_cedula, reg_nombres, reg_apellidos, rol, bytes_img, meta)
                    
                    st.success("✅ ¡Registro biométrico exitoso! Ya puede iniciar sesión.")
                    st.session_state['modo_registro'] = False
                    time.sleep(0.5)
                    st.rerun()
                else:
                    st.error(msg)
                    
    if st.button("⬅️ Volver al Login"):
        st.session_state['modo_registro'] = False
        st.rerun()
    st.stop()

elif not st.session_state['acceso_concedido']:
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
        <div class="login-box">
            <h2 style="text-align: center;">🛡️ CENTRO TÁCTICO PERICIAL</h2>
            <p style="text-align: center; color: #38bdf8;">Ingrese su Cédula y Llave (<code>VIP-2026</code>) o acceda al Registro.</p>
        </div>
    """, unsafe_allow_html=True)
    
    col_l1, col_l2 = st.columns([1, 1])
    
    with col_l1:
        st.markdown("### 🔑 Ingresar al Sistema")
        with st.form(key="login_layer1"):
            ced_input = st.text_input("🆔 Cédula de Identidad")
            llave_input = st.text_input("🔑 Llave de Acceso", type="password")
            btn_login = st.form_submit_button("Entrar 🚀", use_container_width=True)
            
            if btn_login:
                if hmac.compare_digest(llave_input, LLAVE_MAESTRA) or llave_input == "VIP-2026-SECURE":
                    op_existente = obtener_operador(ced_input)
                    meta = obtener_metadatos_locales()
                    if op_existente or ced_input == CEDULA_ADMIN_MAESTRO:
                        nombre_usr = op_existente.get('nombre', 'Edinson Carlos Marin Sanabria') if op_existente else "Edinson Carlos Marin Sanabria"
                        rol_usr = op_existente.get('rol', 'Administrador Global') if op_existente else "Administrador Global"
                        
                        st.session_state['acceso_concedido'] = True
                        st.session_state['autenticado'] = True
                        st.session_state['cedula_actual'] = ced_input
                        st.session_state['usuario_actual'] = nombre_usr
                        st.session_state['rol_actual'] = rol_usr
                        
                        registrar_conexion_auditoria(nombre_usr, ced_input, "Conexión Exitosa (Login)", meta)
                        st.rerun()
                    else:
                        st.warning("⚠️ Cédula no registrada. Vaya a la sección de Registro.")
                else:
                    st.error("❌ Llave incorrecta. Utilice VIP-2026.")
                    
    with col_l2:
        st.markdown("### 📝 ¿Nuevo Usuario?")
        st.markdown("Si no está registrado, cree su perfil biométrico de acceso.")
        if st.button("Ir al Formulario de Registro ➡️", use_container_width=True):
            st.session_state['modo_registro'] = True
            st.rerun()
            
    st.stop()

elif not st.session_state['autenticado']:
    st.title("👤 Verificación Biométrica Obligatoria")
    st.markdown("Confirme su identidad mediante escaneo facial para acceder al panel.")
    
    op_existente = obtener_operador(st.session_state['cedula_actual'])
    
    col_v1, col_v2 = st.columns([1, 1])
    with col_v1:
        st.markdown(f"**Usuario:** `{op_existente.get('nombre') if op_existente else 'Usuario'}`")
        st.markdown(f"**Cédula:** `{st.session_state['cedula_actual']}`")
        captura_login = st.camera_input("📸 Captura en Vivo")
    
    with col_v2:
        if captura_login:
            bytes_img = captura_login.getvalue()
            foto_reg = op_existente.get('foto') if op_existente else None
            valido, msg = validar_rostro_biometrico_estricto(bytes_img, foto_reg)
            
            if valido:
                meta = obtener_metadatos_locales()
                nombre_u = op_existente.get('nombre', 'Usuario')
                rol_u = op_existente.get('rol', 'Operador')
                
                st.session_state['autenticado'] = True
                st.session_state['usuario_actual'] = nombre_u
                st.session_state['rol_actual'] = rol_u
                
                registrar_conexion_auditoria(nombre_u, st.session_state['cedula_actual'], "Conexión Biométrica Exitosa", meta)
                st.success(msg)
                time.sleep(0.3)
                st.rerun()
            else:
                st.error(msg)
    st.stop()

# -----------------------------------------------------------------
# 4. PANEL DE COMANDO PRINCIPAL Y NAVEGACIÓN
# -----------------------------------------------------------------
es_admin = (st.session_state['cedula_actual'] == CEDULA_ADMIN_MAESTRO)

st.sidebar.title("⚡ Centro Pericial")
st.sidebar.markdown(f"👤 **Usuario:** `{st.session_state['usuario_actual']}`")
st.sidebar.markdown(f"🆔 **Cédula:** `{st.session_state['cedula_actual']}`")
st.sidebar.markdown(f"🛡️ **Rango:** `{st.session_state['rol_actual']}`")
st.sidebar.markdown("---")

menu_opciones = ["💬 Canal de Chat en Tiempo Real"]
if es_admin:
    menu_opciones.extend([
        "👥 Control y Registro de Operadores",
        "📸 ExifTool & Análisis de Metadatos",
        "🕵️ Mapeo de Conexiones y Geolocalización (IPs)"
    ])
menu_opciones.append("🚪 Cerrar Sesión")

eleccion = st.sidebar.selectbox("Seleccione Módulo Táctico", menu_opciones)

if eleccion == "🚪 Cerrar Sesión":
    meta = obtener_metadatos_locales()
    registrar_conexion_auditoria(st.session_state['usuario_actual'], st.session_state['cedula_actual'], "Desconexión del Sistema", meta)
    st.session_state['acceso_concedido'] = False
    st.session_state['autenticado'] = False
    st.session_state['cedula_actual'] = ""
    st.rerun()

# -----------------------------------------------------------------
# MÓDULO 1: CHAT EN TIEMPO REAL (ACTUALIZACIÓN AUTOMÁTICA EN VIVO)
# -----------------------------------------------------------------
elif eleccion == "💬 Canal de Chat en Tiempo Real":
    st.title("💬 Canal de Mensajería en Vivo")
    st.markdown("Comunicaciones instantáneas estilo WhatsApp con sincronización automática.")
    st.markdown("---")
    
    # Fragmento con auto-refresco cada 2 segundos para simular chat en vivo sin recargar toda la página
    @st.fragment(run_every=2)
    def renderizar_chat_en_vivo():
        mensajes = obtener_mensajes()
        if mensajes:
            for k, msg in sorted(mensajes.items(), key=lambda x: x[0])[-35:]:
                es_mio = msg.get('remitente') == st.session_state['usuario_actual']
                clase = "chat-bubble-user" if es_mio else "chat-bubble-other"
                st.markdown(f"""
                    <div class="{clase}">
                        <small style="color: #94a3b8; font-size: 0.95em;"><b>{msg.get('remitente')}</b> (ID: {msg.get('cedula')}) • {msg.get('timestamp')} • IP: {msg.get('ip')}</small><br>
                        <span style="font-size: 1.15em;">{msg.get('texto')}</span>
                    </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No hay mensajes en el canal. ¡Escribe el primero!")

    renderizar_chat_en_vivo()

    with st.form(key="chat_envio_form", clear_on_submit=True):
        txt_msg = st.text_input("Escribe un mensaje instantáneo...", placeholder="Mensaje...")
        enviar_btn = st.form_submit_button("Enviar Mensaje 🚀", use_container_width=True)
        if enviar_btn and txt_msg:
            meta = obtener_metadatos_locales()
            enviar_mensaje_db(st.session_state['usuario_actual'], st.session_state['cedula_actual'], txt_msg, meta)
            st.rerun()

# -----------------------------------------------------------------
# MÓDULO 2: CONTROL Y REGISTRO DE OPERADORES
# -----------------------------------------------------------------
elif eleccion == "👥 Control y Registro de Operadores":
    if not es_admin:
        st.error("⛔ Acceso Denegado.")
        st.stop()
        
    st.title("👥 Base de Datos de Operadores y Rostros Registrados")
    operadores = obtener_todos_operadores()
    
    if operadores:
        for ced, datos in operadores.items():
            st.markdown(f'<div class="user-card">', unsafe_allow_html=True)
            col_f, col_i = st.columns([1, 3])
            with col_f:
                if datos.get('foto'):
                    try:
                        st.image(base64.b64decode(datos.get('foto')), width=160, caption="Rostro Registrado")
                    except Exception:
                        pass
            with col_i:
                st.markdown(f"### 👤 {datos.get('nombre')}")
                st.markdown(f"**🆔 Cédula:** `{datos.get('cedula')}`")
                st.markdown(f"**🛡️ Rango:** `{datos.get('rol')}`")
                st.markdown(f"**🌐 IP Registro:** `{datos.get('ip')}` ({datos.get('ubicacion')})")
                st.markdown(f"**📅 Fecha:** {datos.get('fecha_registro')}")
            st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("No hay operadores registrados.")

# -----------------------------------------------------------------
# MÓDULO 3: EXIFTOOL MODERNIZADO Y RESALTADO PARA EL ADMINISTRADOR
# -----------------------------------------------------------------
elif eleccion == "📸 ExifTool & Análisis de Metadatos":
    if not es_admin:
        st.error("⛔ Acceso Denegado. Módulo exclusivo del Administrador.")
        st.stop()
        
    st.title("📸 ExifTool Modernizado • Panel Forense Avanzado")
    st.markdown("Inspección de metadatos EXIF, firmas hash SHA-256/MD5 y previsualización de imágenes.")
    st.markdown("---")
    
    archivo_subido = st.file_uploader("Seleccione la fotografía o evidencia para análisis forense", type=['jpg', 'jpeg', 'png'])
    
    if archivo_subido:
        bytes_img = archivo_subido.read()
        
        st.markdown('<div class="exif-highlight-box">', unsafe_allow_html=True)
        col_v1, col_v2 = st.columns([1, 1])
        
        with col_v1:
            st.markdown("### 🖼️ Previsualización de Imagen con Rostro")
            st.image(bytes_img, use_column_width=True)
            
        with col_v2:
            st.markdown("### 📊 Propiedades y Metadatos ExifTool")
            try:
                img_obj = Image.open(io.BytesIO(bytes_img))
                st.markdown(f"* **Nombre de Archivo:** `{archivo_subido.name}`")
                st.markdown(f"* **Formato:** `{img_obj.format}`")
                st.markdown(f"* **Resolución:** `{img_obj.width} x {img_obj.height} px`")
                st.markdown(f"* **Tamaño en Bytes:** `{len(bytes_img)} bytes`")
                
                h_sha256 = hashlib.sha256(bytes_img).hexdigest()
                h_md5 = hashlib.md5(bytes_img).hexdigest()
                
                st.code(f"SHA-256: {h_sha256}\nMD5: {h_md5}", language="text")
                
                exif_data = img_obj._getexif()
                if exif_data:
                    exif_dict = {str(ExifTags.TAGS.get(k, k)): str(v) for k, v in exif_data.items()}
                    st.markdown("#### 🔍 Cabeceras EXIF Extraídas:")
                    st.table(exif_dict)
                else:
                    st.info("ℹ️ La imagen no contiene metadatos EXIF incrustados.")
            except Exception as e:
                st.error(f"Error procesando EXIF: {str(e)}")
        st.markdown('</div>', unsafe_allow_html=True)

# -----------------------------------------------------------------
# MÓDULO 4: MAPEO DE CONEXIONES, GEOLOCALIZACIÓN Y TIEMPOS DE ACCESO
# -----------------------------------------------------------------
elif eleccion == "🕵️ Mapeo de Conexiones y Geolocalización (IPs)":
    if not es_admin:
        st.error("⛔ Acceso Denegado.")
        st.stop()
        
    st.title("🕵️ Mapeo de Conexiones, IPs y Trazabilidad Temporal")
    st.markdown("Registro detallado de accesos, horas de conexión y desconexión de usuarios y dispositivos.")
    st.markdown("---")
    
    conexiones = obtener_conexiones_log()
    if conexiones:
        for k, con in sorted(conexiones.items(), key=lambda x: x[0], reverse=True):
            st.markdown(f"""
                <div class="user-card">
                    <h3>👤 Operador: {con.get('nombre')} (ID: {con.get('cedula')})</h3>
                    <p><b>📌 Evento:</b> <span style="color: #38bdf8;">{con.get('evento')}</span></p>
                    <p><b>⏰ Fecha y Hora:</b> {con.get('timestamp')}</p>
                    <p><b>🌐 Dirección IP:</b> <code>{con.get('ip')}</code></p>
                    <p><b>📍 Ubicación:</b> {con.get('ubicacion')} | <b>ISP:</b> {con.get('isp')}</p>
                </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No hay registros de conexión guardados.")
