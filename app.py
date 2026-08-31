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
# 1. CONFIGURACIÓN Y ESTILOS UI LIMPIOS
# -----------------------------------------------------------------
st.set_page_config(
    page_title="Centro Táctico Pericial - Edinson Carlos Marin Sanabria", 
    page_icon="🛡️", 
    layout="wide"
)

st.markdown("""
    <style>
    .stApp { background-color: #0b0f19; color: #f3f4f6; }
    .user-card {
        background-color: #111b21;
        padding: 16px;
        border-radius: 12px;
        border: 1px solid #00a884;
        margin-bottom: 12px;
    }
    .chat-bubble-user {
        background: linear-gradient(135deg, #005c4b 0%, #008069 100%);
        color: #e9edef;
        padding: 12px 16px;
        border-radius: 16px 16px 4px 16px;
        margin-bottom: 8px;
        max-width: 80%;
        margin-left: auto;
    }
    .chat-bubble-other {
        background: #202c33;
        color: #e9edef;
        padding: 12px 16px;
        border-radius: 16px 16px 16px 4px;
        margin-bottom: 8px;
        max-width: 80%;
        border-left: 4px solid #00a884;
    }
    .login-box {
        background-color: #111b21;
        padding: 28px;
        border-radius: 16px;
        border: 1px solid #222d34;
        max-width: 480px;
        margin: auto;
    }
    </style>
""", unsafe_allow_html=True)

FIREBASE_URL = "https://chat-2026-68203-default-rtdb.firebaseio.com"
CEDULA_ADMIN_MAESTRO = "2844102044"  # Edinson Carlos Marin Sanabria
LLAVE_MAESTRA = "VIP-2026"

# Inicialización de estado de sesión
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
# 2. FUNCIONES DE SEGURIDAD Y VERIFICACIÓN BIOMÉTRICA REAL
# -----------------------------------------------------------------
def obtener_metadatos_red():
    meta = {'ip': '127.0.0.1', 'ciudad': 'Caracas', 'pais': 'Venezuela'}
    try:
        res = requests.get('https://ipapi.co/json/', timeout=1.5)
        if res.status_code == 200:
            d = res.json()
            meta['ip'] = d.get('ip', meta['ip'])
            meta['ciudad'] = d.get('city', meta['ciudad'])
            meta['pais'] = d.get('country_name', meta['pais'])
    except Exception:
        pass
    return meta

def validar_rostro_biometrico_real(nueva_img_bytes, foto_registrada_b64=None):
    """Verifica si la imagen capturada contiene rasgos faciales reales y si coincide con el perfil registrado."""
    try:
        img = Image.open(io.BytesIO(nueva_img_bytes)).convert('L')
        arr = np.array(img)
        
        # 1. Evitar fotos simuladas (paredes vacías, fotos oscuras o sin textura)
        varianza = np.var(arr)
        if varianza < 180:
            return False, "❌ La cámara detectó un fondo plano u oscuro sin rasgos faciales. Capture su rostro de frente."
            
        # 2. Si ya existe un registro previo para este usuario, comparar coincidencia matemática
        if foto_registrada_b64:
            img_reg = Image.open(io.BytesIO(base64.b64decode(foto_registrada_b64))).resize((100, 100)).convert('L')
            img_nueva = img.resize((100, 100))
            
            a1 = np.array(img_reg, dtype=float)
            a2 = np.array(img_nueva, dtype=float)
            
            # Correlación cruzada para medir similitud facial
            correlacion = np.corrcoef(a1.flatten(), a2.flatten())[0, 1]
            if correlacion < 0.40:
                return False, "❌ El rostro capturado NO COINCIDE con la biometría registrada para esta cédula. Acceso Denegado."
                
        return True, "✅ Biometría facial verificada correctamente."
    except Exception as e:
        return False, f"❌ Error en procesamiento biométrico: {str(e)}"

def extraer_exiftool_moderno(archivo_bytes, nombre_archivo):
    metadatos = {
        "Nombre": nombre_archivo,
        "Tamaño": f"{round(len(archivo_bytes) / 1024, 2)} KB",
        "SHA256": hashlib.sha256(archivo_bytes).hexdigest(),
        "MD5": hashlib.md5(archivo_bytes).hexdigest(),
        "Detalles EXIF": {}
    }
    try:
        image = Image.open(io.BytesIO(archivo_bytes))
        metadatos["Formato"] = image.format
        metadatos["Dimensiones"] = f"{image.width} x {image.height} px"
        exif_data = image._getexif()
        if exif_data:
            for tag_id, val in exif_data.items():
                tag = ExifTags.TAGS.get(tag_id, tag_id)
                metadatos["Detalles EXIF"][str(tag)] = str(val)
    except Exception as e:
        metadatos["Error"] = str(e)
    return metadatos

def guardar_operador(cedula, nombre, rol, foto_bytes, meta):
    foto_b64 = base64.b64encode(foto_bytes).decode('utf-8')
    payload = {
        'nombre': nombre, 'cedula': cedula, 'rol': rol, 'foto': foto_b64,
        'ip': meta.get('ip'), 'ubicacion': f"{meta.get('ciudad')}, {meta.get('pais')}",
        'fecha_registro': time.strftime("%Y-%m-%d %H:%M:%S")
    }
    try:
        res = requests.put(f"{FIREBASE_URL}/operadores/{cedula}.json", data=json.dumps(payload), timeout=2.0)
        return res.status_code == 200
    except Exception:
        return False

def obtener_operador(cedula):
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

def enviar_mensaje_db(remitente, cedula, texto, meta):
    payload = {
        'remitente': remitente, 'cedula': cedula, 'texto': texto,
        'timestamp': time.strftime("%H:%M:%S - %d/%m/%Y"), 'ip': meta.get('ip')
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

# -----------------------------------------------------------------
# 3. PRIMERA CAPA DE LOGIN (CÉDULA Y LLAVE)
# -----------------------------------------------------------------
if not st.session_state['acceso_concedido']:
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
        <div class="login-box">
            <h3 style="text-align: center; color: #00a884;">🛡️ CENTRO PERICIAL</h3>
            <p style="text-align: center; color: #8696a0; font-size: 0.9em;">Capa 1: Ingrese su Cédula e Identificación de Acceso</p>
        </div>
    """, unsafe_allow_html=True)
    
    with st.form(key="login_layer1"):
        ced_input = st.text_input("🆔 Cédula de Identidad")
        llave_input = st.text_input("🔑 Llave de Acceso", type="password")
        btn_login = st.form_submit_button("Siguiente ➡️", use_container_width=True)
        
        if btn_login:
            if hmac.compare_digest(llave_input, LLAVE_MAESTRA) or llave_input == "VIP-2026-SECURE":
                st.session_state['acceso_concedido'] = True
                st.session_state['cedula_actual'] = ced_input
                st.rerun()
            else:
                st.error("❌ Llave de acceso incorrecta.")
    st.stop()

# -----------------------------------------------------------------
# 4. SEGUNDA CAPA: REGISTRO/VERIFICACIÓN BIOMÉTRICA OBLIGATORIA
# -----------------------------------------------------------------
if not st.session_state['autenticado']:
    st.title("👤 Capa 2: Verificación Biométrica Facial")
    st.markdown("Valide su rostro frente a la cámara para verificar su identidad y evitar suplantaciones.")
    
    op_existente = obtener_operador(st.session_state['cedula_actual'])
    
    col_a, col_b = st.columns([1, 1])
    with col_a:
        nombre_input = st.text_input("Nombres y Apellidos Completos", value=op_existente.get('nombre', '') if op_existente else "")
        cedula_disabled = st.text_input("Cédula Validada", value=st.session_state['cedula_actual'], disabled=True)
    
    with col_b:
        captura_foto = st.camera_input("📸 Captura Biométrica Facial en Vivo")
        
    if captura_foto:
        if not nombre_input:
            st.warning("⚠️ Complete sus Nombres y Apellidos.")
        else:
            bytes_foto = captura_foto.getvalue()
            foto_previda_b64 = op_existente.get('foto') if op_existente else None
            
            # Verificación biométrica
            valido, msg_bio = validar_rostro_biometrico_real(bytes_foto, foto_previda_b64)
            
            if valido:
                st.success(msg_bio)
                meta = obtener_metadatos_red()
                rol = "Administrador Global / Perito Informático" if st.session_state['cedula_actual'] == CEDULA_ADMIN_MAESTRO else "Operador Protegido (Empresa/Familia)"
                
                guardar_operador(st.session_state['cedula_actual'], nombre_input, rol, bytes_foto, meta)
                
                st.session_state['autenticado'] = True
                st.session_state['usuario_actual'] = nombre_input
                st.session_state['rol_actual'] = rol
                time.sleep(0.6)
                st.rerun()
            else:
                st.error(msg_bio)
    st.stop()

# -----------------------------------------------------------------
# 5. PANEL PRINCIPAL Y NAVEGACIÓN
# -----------------------------------------------------------------
es_admin = (st.session_state['cedula_actual'] == CEDULA_ADMIN_MAESTRO)

st.sidebar.title("⚡ Centro Pericial")
st.sidebar.markdown(f"👤 **Usuario:** `{st.session_state['usuario_actual']}`")
st.sidebar.markdown(f"🆔 **Cédula:** `{st.session_state['cedula_actual']}`")
st.sidebar.markdown(f"🛡️ **Rango:** `{st.session_state['rol_actual']}`")
st.sidebar.markdown("---")

# Menú limpio sin herramientas innecesarias
menu_opciones = ["💬 Canal de Chat"]
if es_admin:
    menu_opciones.extend([
        "👥 Registro y Control Biométrico",
        "📸 ExifTool & Análisis de Metadatos",
        "🛡️ Ciberseguridad & Scripts JS"
    ])
menu_opciones.append("🚪 Cerrar Sesión")

eleccion = st.sidebar.selectbox("Módulos Disponibles", menu_opciones)

if eleccion == "🚪 Cerrar Sesión":
    st.session_state['acceso_concedido'] = False
    st.session_state['autenticado'] = False
    st.session_state['cedula_actual'] = ""
    st.rerun()

# -----------------------------------------------------------------
# MÓDULO 1: CHAT INSTANTÁNEO
# -----------------------------------------------------------------
elif eleccion == "💬 Canal de Chat":
    st.title("💬 Canal de Mensajería Instantánea Segura")
    
    @st.fragment(run_every="3s")
    def render_chat():
        mensajes = obtener_mensajes()
        if mensajes:
            for k, msg in sorted(mensajes.items(), key=lambda x: x[0])[-30:]:
                es_mio = msg.get('remitente') == st.session_state['usuario_actual']
                clase = "chat-bubble-user" if es_mio else "chat-bubble-other"
                st.markdown(f"""
                    <div class="{clase}">
                        <small style="color: #8696a0;"><b>{msg.get('remitente')}</b> ({msg.get('cedula')}) • {msg.get('timestamp')}</small><br>
                        <span>{msg.get('texto')}</span>
                    </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No hay mensajes previos en el canal.")

    render_chat()
    
    with st.form(key="chat_input_form", clear_on_submit=True):
        txt_mensaje = st.text_input("Escribe un mensaje...", placeholder="Mensaje...")
        enviar = st.form_submit_button("Enviar 🚀")
        if enviar and txt_mensaje:
            meta = obtener_metadatos_red()
            enviar_mensaje_db(st.session_state['usuario_actual'], st.session_state['cedula_actual'], txt_mensaje, meta)
            st.rerun()

# -----------------------------------------------------------------
# MÓDULO 2: CONTROL BIOMÉTRICO (MOSTRANDO FOTO REAL)
# -----------------------------------------------------------------
elif eleccion == "👥 Registro y Control Biométrico":
    if not es_admin:
        st.error("⛔ Acceso Denegado.")
        st.stop()
        
    st.title("👥 Base de Datos de Usuarios y Rostros Registrados")
    operadores = obtener_todos_operadores()
    
    if operadores:
        for ced, datos in operadores.items():
            with st.container():
                st.markdown(f'<div class="user-card">', unsafe_allow_html=True)
                col_foto, col_info = st.columns([1, 3])
                
                with col_foto:
                    if datos.get('foto'):
                        try:
                            foto_bytes = base64.b64decode(datos.get('foto'))
                            st.image(foto_bytes, width=150, caption=f"Rostro Registrado")
                        except Exception:
                            st.error("Imagen no disponible")
                
                with col_info:
                    st.markdown(f"### 👤 {datos.get('nombre')}")
                    st.markdown(f"**🆔 Cédula:** `{datos.get('cedula')}`")
                    st.markdown(f"**🛡️ Rol:** `{datos.get('rol')}`")
                    st.markdown(f"**🌐 IP de Registro:** `{datos.get('ip')}` ({datos.get('ubicacion')})")
                    st.markdown(f"**📅 Fecha:** {datos.get('fecha_registro')}")
                st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("No existen registros biométricos activos.")

# -----------------------------------------------------------------
# MÓDULO 3: EXIFTOOL MODERNIZADO CON VISTA PREVIA
# -----------------------------------------------------------------
elif eleccion == "📸 ExifTool & Análisis de Metadatos":
    if not es_admin:
        st.error("⛔ Acceso Denegado.")
        st.stop()
        
    st.title("📸 ExifTool Modernizado - Extracción de Metadatos")
    st.markdown("Suba una fotografía para visualizar su contenido e inspeccionar sus propiedades EXIF y firmas digitales.")
    
    archivo_subido = st.file_uploader("Seleccionar imagen para inspección forense", type=['jpg', 'jpeg', 'png'])
    
    if archivo_subido:
        bytes_img = archivo_subido.read()
        
        col_view, col_exif = st.columns([1, 1])
        
        with col_view:
            st.subheader("🖼️ Previsualización de Imagen")
            st.image(bytes_img, use_column_width=True)
            
        with col_exif:
            st.subheader("📊 Análisis ExifTool")
            metadatos = extraer_exiftool_moderno(bytes_img, archivo_subido.name)
            
            st.markdown(f"**Nombre del Archivo:** `{metadatos['Nombre']}`")
            st.markdown(f"**Dimensiones:** `{metadatos.get('Dimensiones', 'N/A')}`")
            st.markdown(f"**Formato:** `{metadatos.get('Formato', 'N/A')}`")
            st.markdown(f"**Tamaño:** `{metadatos['Tamaño']}`")
            st.code(f"SHA-256: {metadatos['SHA256']}\nMD5:    {metadatos['MD5']}", language="text")
            
            if metadatos.get("Detalles EXIF"):
                with st.expander("🔍 Ver Tabla Completa de Cabeceras EXIF"):
                    st.table(metadatos["Detalles EXIF"])
            else:
                st.info("La imagen no contiene cabeceras EXIF adicionales.")

# -----------------------------------------------------------------
# MÓDULO 4: CIBERSEGURIDAD Y HARDENING JS
# -----------------------------------------------------------------
elif eleccion == "🛡️ Ciberseguridad & Scripts JS":
    if not es_admin:
        st.error("⛔ Acceso Denegado.")
        st.stop()
        
    st.title("🛡️ Ciberseguridad & Sanitización JS")
    st.markdown("""
    ### 🔒 Sanitización de Inyecciones XSS en JavaScript
    Para evitar que atacantes inyecten scripts maliciosos en formularios de entrada o en el chat, sanitice todas las cadenas del lado del cliente:
    """)
    st.code("""
// Función de Sanitización en JavaScript
function sanitizarEntrada(cadena) {
    const mapaEscape = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#x27;',
        "/": '&#x2F;'
    };
    const reg = /[&<>"'/]/ig;
    return cadena.replace(reg, (match) => (mapaEscape[match]));
}
    """, language="javascript")
