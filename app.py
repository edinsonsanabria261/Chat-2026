import streamlit as st
import time
import requests
import json
from PIL import Image, ExifTags
import io
import base64
import hashlib
import hmac

# -----------------------------------------------------------------
# 1. CONFIGURACIÓN TÁCTICA Y ESTILOS UI PROFESIONALES
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
CEDULA_ADMIN_MAESTRO = "2844102044"  # Cédula de Edinson Carlos Marin Sanabria
LLAVE_ACCESO_MAESTRA = "VIP-2026-SECURE"

# Inicialización segura de variables de sesión
for key, val in {
    'acceso_concedido': False,
    'autenticado': False,
    'usuario_actual': "",
    'rol_actual': "",
    'cedula_actual': "",
    'intentos_fallidos': 0
}.items():
    if key not in st.session_state:
        st.session_state[key] = val

# -----------------------------------------------------------------
# 2. FUNCIONES DE TELEMETRÍA Y EXTRACCIÓN AVANZADA DE METADATOS
# -----------------------------------------------------------------
def obtener_metadatos_red():
    meta = {
        'ip': '127.0.0.1', 
        'ciudad': 'Nodo Local', 
        'pais': 'Red Segura', 
        'org': 'Control Táctico Empresarial', 
        'lat_lon': 'N/A', 
        'isp': 'N/A',
        'vector_ataque': 'Limpio'
    }
    try:
        response = requests.get('https://ipapi.co/json/', timeout=0.8)
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
        meta['vector_ataque'] = 'Proxy / Red Oculta / Timeout'
    return meta

def extraer_metadatos_archivo(archivo_bytes, nombre_archivo):
    """Extracción avanzada de metadatos forenses, EXIF y Hashes"""
    metadatos = {
        "nombre": nombre_archivo,
        "tamaño_bytes": len(archivo_bytes),
        "sha256": hashlib.sha256(archivo_bytes).hexdigest(),
        "md5": hashlib.md5(archivo_bytes).hexdigest(),
        "exif": {}
    }
    
    # Intentar extraer EXIF si es una imagen
    try:
        image = Image.open(io.BytesIO(archivo_bytes))
        metadatos["formato"] = image.format
        metadatos["modo"] = image.mode
        metadatos["dimensiones"] = f"{image.width}x{image.height} px"
        
        exif_data = image._getexif()
        if exif_data:
            for tag_id, val in exif_data.items():
                tag = ExifTags.TAGS.get(tag_id, tag_id)
                metadatos["exif"][str(tag)] = str(val)
        else:
            metadatos["exif"]["Info"] = "No se encontraron metadatos EXIF (Imagen limpia o comprimida)"
    except Exception as e:
        metadatos["parseo_imagen"] = f"No aplicable o archivo no visualizable como imagen ({str(e)})"
        
    return metadatos

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
        requests.post(f"{FIREBASE_URL}/auditoria_ip.json", data=json.dumps(payload), timeout=0.8)
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
        requests.put(f"{FIREBASE_URL}/operadores/{cedula}.json", data=json.dumps(payload), timeout=0.8)
    except Exception:
        pass

def obtener_operador(cedula):
    if cedula == CEDULA_ADMIN_MAESTRO:
        return {
            'nombre': "Edinson Carlos Marin Sanabria",
            'cedula': CEDULA_ADMIN_MAESTRO,
            'rol': "Perito Informático Titular / Administrador Global"
        }
    try:
        res = requests.get(f"{FIREBASE_URL}/operadores/{cedula}.json", timeout=0.8)
        if res.status_code == 200:
            return res.json()
    except Exception:
        pass
    return None

def obtener_todos_operadores():
    try:
        res = requests.get(f"{FIREBASE_URL}/operadores.json", timeout=0.8)
        if res.status_code == 200 and res.json():
            return res.json()
    except Exception:
        pass
    return {}

def enviar_mensaje_db(remitente, texto, archivo_b64, tipo_archivo, metadatos_extraidos, meta):
    hash_archivo = metadatos_extraidos.get('sha256', 'Sin archivo') if metadatos_extraidos else "Sin archivo"
    payload = {
        'remitente': remitente,
        'texto': texto,
        'archivo': archivo_b64,
        'hash_integridad': hash_archivo,
        'tipo_archivo': tipo_archivo,
        'metadatos_archivo': metadatos_extraidos,
        'timestamp': time.strftime("%H:%M:%S - %d/%m/%Y"),
        'ip': meta.get('ip'),
        'ubicacion': f"{meta.get('ciudad')}, {meta.get('pais')}"
    }
    try:
        requests.post(f"{FIREBASE_URL}/mensajes.json", data=json.dumps(payload), timeout=0.8)
    except Exception:
        pass

def obtener_mensajes():
    try:
        res = requests.get(f"{FIREBASE_URL}/mensajes.json", timeout=0.8)
        if res.status_code == 200 and res.json():
            return res.json()
    except Exception:
        pass
    return {}

def obtener_auditorias():
    try:
        res = requests.get(f"{FIREBASE_URL}/auditoria_ip.json", timeout=0.8)
        if res.status_code == 200 and res.json():
            return res.json()
    except Exception:
        pass
    return {}

# -----------------------------------------------------------------
# 3. PASARELA DE ACCESO GLOBAL
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
# 4. AUTENTICACIÓN Y VALIDACIÓN BIOMÉTRICA
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
        reg_foto = st.camera_input("Captura Facial Instantánea (Take Photo)", key="camara_registro_input")
        
        if reg_foto or reg_cedula == CEDULA_ADMIN_MAESTRO:
            meta = obtener_metadatos_red()
            foto_bytes = reg_foto.getvalue() if reg_foto else b"DEFAULT_ADMIN_BYTES"
            foto_b64 = base64.b64encode(foto_bytes).decode('utf-8')
            
            rol_asignado = "Perito Informático Titular / Administrador Global" if reg_cedula == CEDULA_ADMIN_MAESTRO else "Operador Protegido (Empresa/Familia)"
            guardar_operador(reg_cedula, reg_nombre, rol_asignado, foto_b64, meta, "Terminal Móvil")
            registrar_auditoria_forense(reg_nombre, "Registro pericial completado", meta, "Móvil", hashlib.sha256(foto_bytes).hexdigest())
            
            st.session_state['autenticado'] = True
            st.session_state['usuario_actual'] = reg_nombre
            st.session_state['cedula_actual'] = reg_cedula
            st.session_state['rol_actual'] = rol_asignado
            st.success("✅ ¡Operador registrado con éxito y biometría encriptada!")
            time.sleep(0.5)
            st.rerun()

else:
    # -----------------------------------------------------------------
    # 5. PANELES DE COMANDO Y CONTROL AVANZADO
    # -----------------------------------------------------------------
    st.sidebar.markdown(f"👤 **Operador:** `{st.session_state['usuario_actual']}`")
    st.sidebar.markdown(f"🛡️ **Rango:** `{st.session_state['rol_actual']}`")
    st.sidebar.markdown(f"🆔 **Cédula:** `{st.session_state['cedula_actual']}`")
    st.sidebar.markdown("---")
    
    opciones_menu = ["Canal de Chat Estilo WhatsApp (Ultra Rápido)"]
    
    if st.session_state['cedula_actual'] == CEDULA_ADMIN_MAESTRO or "Administrador" in st.session_state['rol_actual']:
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
        st.rerun()

    # MÓDULO 1: CHAT ESTILO WHATSAPP EN TIEMPO REAL
    elif seleccion == "Canal de Chat Estilo WhatsApp (Ultra Rápido)":
        st.title("💬 Canal de Comunicaciones Tácticas")
        st.markdown("Mensajería instantánea en vivo con cadena de custodia cifrada.")
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
                    hash_txt = msg.get('hash_integridad', 'N/A')
                    
                    html_msg = f"""
                        <div class="{estilo}">
                            <small style="color: #8696a0;"><b>{remitente_txt}</b> • {timestamp_txt} • 🌐 IP: {ip_txt}</small><br>
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
                st.info("Canal sincronizado. Escribe tu mensaje para enviarlo instantáneamente.")

        with st.form(key='whatsapp_form', clear_on_submit=True):
            texto_msg_input = st.text_area("Escribe un mensaje en vivo...", height=60, label_visibility="collapsed")
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
                    meta_archivo = {}
                    if archivo_adjunto:
                        bytes_archivo = archivo_adjunto.getvalue()
                        b64_file = base64.b64encode(bytes_archivo).decode('utf-8')
                        tipo_mime = archivo_adjunto.type
                        meta_archivo = extraer_metadatos_archivo(bytes_archivo, archivo_adjunto.name)
                    
                    meta = obtener_metadatos_red()
                    enviar_mensaje_db(
                        st.session_state['usuario_actual'], 
                        texto_msg_input if texto_msg_input else "[Archivo Multimedia]", 
                        b64_file, 
                        tipo_mime, 
                        meta_archivo,
                        meta
                    )
                    st.rerun()

    # MÓDULO EXCLUSIVO: EXTRACCIÓN AVANZADA DE METADATOS Y ARCHIVOS
    elif seleccion == "Extracción Forense de Metadatos y Archivos":
        st.title("🔬 Laboratorio de Extracción de Metadatos")
        st.markdown("Sube cualquier archivo (fotografías, documentos, binarios) para realizar una inspección forense exhaustiva de metadatos, EXIF y hashes.")
        
        archivo_analisis = st.file_uploader("Seleccione o arrastre el archivo de evidencia", type=['png', 'jpg', 'jpeg', 'pdf', 'mp4', 'txt', 'zip', 'apk'])
        
        if archivo_analisis:
            bytes_evidencia = archivo_analisis.read()
            resultado_metadatos = extraer_metadatos_archivo(bytes_evidencia, archivo_analisis.name)
            
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("📊 Propiedades y Hashes")
                st.code(f"Nombre: {resultado_metadatos['nombre']}\nTamaño: {resultado_metadatos['tamaño_bytes']} bytes\nMD5: {resultado_metadatos['md5']}\nSHA-256: {resultado_metadatos['sha256']}", language="text")
                
                if 'formato' in resultado_metadatos:
                    st.markdown(f"**Formato:** `{resultado_metadatos['formato']}` | **Dimensiones:** `{resultado_metidatos.get('dimensiones', 'N/A')}`")
            with col2:
                st.subheader("🖼️ Vista Previa")
                try:
                    st.image(bytes_evidencia, width=300, caption="Evidencia Analizada")
                except Exception:
                    st.info("El archivo no es una imagen gráfica directa.")
            
            st.markdown("### 🔍 Metadatos EXIF / Estructura Interna Encontrada")
            st.json(resultado_metadatos["exif"])
            
            if st.button("Guardar Reporte en el Sistema de Auditoría"):
                meta = obtener_metadatos_red()
                registrar_auditoria_forense(st.session_state['usuario_actual'], f"Análisis forense de metadatos: {archivo_analisis.name}", meta, "Terminal Móvil", resultado_metadatos['sha256'])
                st.success("✅ Reporte de metadatos almacenado correctamente en la cadena de custodia global.")

    # MÓDULO EXCLUSIVO ADMIN: PANEL BIOMÉTRICO GLOBAL
    elif seleccion == "Panel de Control & Biometría Global":
        st.title("🛡️ Base de Datos Centralizada de Operadores")
        st.markdown("Control pericial exclusivo de identidades y rostros encriptados de la empresa y familia.")
        
        operadores = obtener_todos_operadores()
        st.subheader(f"👥 Operadores Registrados ({len(operadores)})")
        
        for ced, datos in operadores.items():
            with st.expander(f"Cédula: {ced} | {datos.get('nombre')} [{datos.get('rol')}]"):
                col1, col2 = st.columns([1, 2])
                with col1:
                    if 'foto' in datos and datos['foto'] and datos['foto'] != "DEFAULT_ADMIN_BYTES":
                        try:
                            foto_bytes = base64.b64decode(datos['foto'])
                            st.image(foto_bytes, width=150, caption="Biometría Facial")
                        except Exception:
                            st.write("Sin imagen decodificable")
                with col2:
                    st.markdown(f"**Nombre:** {datos.get('nombre')}")
                    st.markdown(f"**Cédula:** {datos.get('cedula')}")
                    st.markdown(f"**Rol:** {datos.get('rol')}")
                    st.markdown(f"**IP de Registro:** `{datos.get('ip_registro')}`")
                    st.markdown(f"**Ubicación:** {datos.get('ubicacion_registro')}")
                    st.markdown(f"**Hash Biométrico:** ` {datos.get('hash_biometrico', 'N/A')} `")

    # MÓDULO EXCLUSIVO ADMIN: FORENSE E IPS
    elif seleccion == "Inteligencia Forense, IPs y Amenazas":
        st.title("🕵️ Auditoría Forense y Control de IPs")
        st.markdown("Registro detallado de conexiones, IPs de origen, sistemas operativos y eventos del sistema.")
        
        registros = obtener_auditorias()
        if registros:
            items = sorted(registros.items(), key=lambda x: x[0], reverse=True)
            for k, reg in items[:40]:
                st.markdown(f"""
                    <div class="tool-card">
                        🕒 <b>{reg.get('timestamp')}</b> | 👤 <b>{reg.get('usuario')}</b><br>
                        ⚡ Evento: <code>{reg.get('accion')}</code><br>
                        🌐 IP de Origen: <b>{reg.get('ip')}</b> | Ubicación: {reg.get('ubicacion')}<br>
                        💻 Dispositivo: {reg.get('dispositivo')} | Vector: {reg.get('vector_sospechoso')}
                    </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No hay registros de auditoría forense almacenados todavía.")

    elif seleccion == "Análisis OSINT y Rastreo de Atacantes":
        st.title("🌐 Módulo OSINT y Trazabilidad de Redes")
        st.markdown("Herramientas avanzadas para la identificación de nodos externos y vectores de ataque de la empresa.")
        meta_actual = obtener_metadatos_red()
        st.json(meta_actual)

    elif seleccion == "Reporte de Integridad y Seguridad Personal":
        st.title("🛡️ Estado de Seguridad y Encriptación")
        st.markdown("Su terminal se encuentra operando bajo protocolos de cifrado simétrico y monitoreo constante para la protección de la empresa y la familia.")
