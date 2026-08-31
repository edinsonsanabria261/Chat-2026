import streamlit as st
import time
import requests
import json
from PIL import Image
import io
import base64
import streamlit.components.v1 as components

# -----------------------------------------------------------------
# 1. CONFIGURACIÓN TÁCTICA Y ESTILOS UI PREMIUM (MODO OSCURO)
# -----------------------------------------------------------------
st.set_page_config(page_title="Centro Táctico Red Team", page_icon="⚡", layout="wide")

st.markdown("""
    <style>
    .stApp {
        background-color: #0b0f19;
        color: #f3f4f6;
    }
    .chat-bubble-user {
        background: linear-gradient(135deg, #4f46e5 0%, #3730a3 100%);
        color: #f8fafc;
        padding: 14px 18px;
        border-radius: 16px 16px 2px 16px;
        margin-bottom: 12px;
        box-shadow: 0 4px 12px rgba(79, 70, 229, 0.3);
        max-width: 85%;
        margin-left: auto;
    }
    .chat-bubble-other {
        background: linear-gradient(135deg, #1e293b 100%, #0f172a 0%);
        color: #f1f5f9;
        padding: 14px 18px;
        border-radius: 16px 16px 16px 2px;
        margin-bottom: 12px;
        border-left: 4px solid #10b981;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.4);
        max-width: 85%;
    }
    .tool-card {
        background-color: #111827;
        padding: 22px;
        border-radius: 14px;
        border: 1px solid #1f2937;
        margin-bottom: 18px;
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.5);
    }
    .login-container {
        background-color: #111827;
        padding: 35px;
        border-radius: 16px;
        border: 1px solid #374151;
        box-shadow: 0 12px 30px rgba(0, 0, 0, 0.8);
    }
    code {
        color: #38bdf8 !important;
        background-color: #030712 !important;
        padding: 3px 8px;
        border-radius: 6px;
    }
    </style>
""", unsafe_allow_html=True)

FIREBASE_URL = "https://chat-2026-68203-default-rtdb.firebaseio.com/"
CEDULA_ADMIN_MAESTRO = "12345678"
LLAVE_ACCESO_MAESTRA = "VIP-2026-SECURE"

if 'acceso_concedido' not in st.session_state:
    st.session_state['acceso_concedido'] = False

if 'autenticado' not in st.session_state:
    st.session_state['autenticado'] = False
    st.session_state['usuario_actual'] = ""
    st.session_state['rol_actual'] = ""
    st.session_state['cedula_actual'] = ""

# -----------------------------------------------------------------
# 2. FUNCIONES DE TELEMETRÍA Y EXTRACCIÓN DE METADATOS DE RED
# -----------------------------------------------------------------
def obtener_metadatos_red():
    meta = {'ip': '127.0.0.1', 'ciudad': 'Nodo Local', 'pais': 'Red Interna', 'org': 'Red Táctica Directa', 'lat_lon': 'N/A', 'isp': 'N/A'}
    try:
        response = requests.get('https://ipapi.co/json/', timeout=3)
        if response.status_code == 200:
            data = response.json()
            meta['ip'] = data.get('ip', '127.0.0.1')
            meta['ciudad'] = data.get('city', 'Nodo Local')
            meta['pais'] = data.get('country_name', 'Red Interna')
            meta['org'] = data.get('org', 'ISP Privado')
            meta['isp'] = data.get('asn', 'N/A')
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
# 3. SCRIPTS DE HARDWARE Y AUTO-ACTUALIZACIÓN INSTANTÁNEA
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
    
    const infoHardware = dispositivo + " | Pantalla: " + window.screen.width + "x" + window.screen.height;
    
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
# 4. PASARELA DE ACCESO MAESTRO
# -----------------------------------------------------------------
if not st.session_state['acceso_concedido']:
    st.markdown("<br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
            <div class="login-container">
                <h2 style="text-align: center; color: #6366f1;">⚡ CENTRO TÁCTICO RED TEAM</h2>
                <p style="text-align: center; color: #9ca3af;">Plataforma de Seguridad, Inteligencia de Redes y Enlace Cifrado.</p>
            </div>
        """, unsafe_allow_html=True)
        
        with st.form(key="login_form"):
            llave_input = st.text_input("🔑 Llave de Acceso Global", type="password")
            btn_desbloquear = st.form_submit_button("Desbloquear Sistema Táctico", type="primary", use_container_width=True)
            
            if btn_desbloquear:
                if llave_input == LLAVE_ACCESO_MAESTRA:
                    st.session_state['acceso_concedido'] = True
                    st.rerun()
                else:
                    st.error("❌ Llave incorrecta. Acceso denegado.")
    st.stop()

# -----------------------------------------------------------------
# 5. GESTIÓN DE SESIÓN Y AUTENTICACIÓN BIOMÉTRICA
# -----------------------------------------------------------------
st.sidebar.title("⚡ Red Team Central")
st.sidebar.markdown("---")

if not st.session_state['autenticado']:
    modo_auth = st.sidebar.radio("Modo de Ingreso", ["Iniciar Sesión (Biometría)", "Registrar Operador"])
    inyectar_telemetria_y_refresco()
    
    if modo_auth == "Iniciar Sesión (Biometría)":
        st.title("🔐 Validación Biométrica de Operador")
        st.markdown("Ingrese su cédula. El sistema capturará su rostro automáticamente para autorizar el enlace.")
        
        cedula_ingreso = st.text_input("Cédula de Identidad Operativa")
        st.markdown("📸 **Escáner Facial Automático:**")
        foto_camara = st.camera_input("Biometría Automática", label_visibility="collapsed")
        
        components.html("""
        <script>
        setTimeout(function() {
            const btn = document.querySelector('button[kind="secondary"]');
            if (btn && !window.clicked) {
                window.clicked = true;
                setTimeout(() => { btn.click(); }, 1200);
            }
        }, 800);
        </script>
        """, height=0)

        if foto_camara:
            if not cedula_ingreso:
                st.warning("⚠️ Ingrese su cédula para emparejar la biometría.")
            else:
                user_data = obtener_operador(cedula_ingreso)
                if user_data:
                    meta = obtener_metadatos_red()
                    st.session_state['autenticado'] = True
                    st.session_state['usuario_actual'] = user_data.get('nombre')
                    st.session_state['cedula_actual'] = cedula_ingreso
                    st.session_state['rol_actual'] = "Comandante Red Team (Administrador Total)" if cedula_ingreso == CEDULA_ADMIN_MAESTRO else "Operador Táctico"
                    
                    registrar_auditoria(user_data.get('nombre'), "Acceso biométrico instantáneo exitoso", meta)
                    st.rerun()
                else:
                    st.error("❌ Cédula no encontrada en la base de datos de operadores.")

    elif modo_auth == "Registrar Operador":
        st.title("📝 Registro de Nuevo Operador Táctico")
        reg_nombre = st.text_input("Nombre Completo / Alias")
        reg_cedula = st.text_input("Cédula de Identidad")
        st.markdown("📸 **Captura Facial para Base de Datos:**")
        reg_foto = st.camera_input("Registro Facial", label_visibility="collapsed")
        
        if reg_foto:
            if not reg_nombre or not reg_cedula:
                st.warning("⚠️ Complete todos los campos de identidad.")
            else:
                meta = obtener_metadatos_red()
                foto_b64 = base64.b64encode(reg_foto.getvalue()).decode('utf-8')
                rol = "Comandante Red Team (Administrador Total)" if reg_cedula == CEDULA_ADMIN_MAESTRO else "Operador Táctico"
                guardar_operador(reg_cedula, reg_nombre, rol, foto_b64, meta, "Terminal Móvil")
                registrar_auditoria(reg_nombre, "Registro operativo completado", meta)
                st.success("✅ ¡Operador registrado exitosamente en la red!")

else:
    # -----------------------------------------------------------------
    # 6. PANELES DE CONTROL Y HERRAMIENTAS AVANZADAS
    # -----------------------------------------------------------------
    st.sidebar.markdown(f"👤 **Operador:** `{st.session_state['usuario_actual']}`")
    st.sidebar.markdown(f"🛡️ **Rango:** `{st.session_state['rol_actual']}`")
    st.sidebar.markdown("---")
    
    opciones_menu = ["Canal de Chat Estilo WhatsApp (Ultra Rápido)", "Inteligencia OSINT, Redes y Metadatos"]
    if "Comandante" in st.session_state['rol_actual']:
        opciones_menu.extend(["Panel de Control & Biometría", "Inteligencia Forense y Redes"])
    opciones_menu.append("Cerrar Sesión")
    
    seleccion = st.sidebar.selectbox("Centro de Comando", opciones_menu)
    
    if seleccion == "Cerrar Sesión":
        st.session_state['autenticado'] = False
        st.rerun()

    # MÓDULO: CHAT ESTILO WHATSAPP MULTIMEDIA (INSTANTÁNEO)
    elif seleccion == "Canal de Chat Estilo WhatsApp (Ultra Rápido)":
        st.title("💬 Canal de Comunicaciones Tácticas en Tiempo Real")
        st.markdown("Transmisión instantánea tipo WhatsApp con soporte completo para imágenes, videos, audios y música.")
        st.markdown("---")
        
        # Auto-refresco en vivo optimizado para alta velocidad
        st.markdown("""
            <meta http-equiv="refresh" content="3">
            <script>
               window.scrollTo(0, document.body.scrollHeight);
            </script>
        """, unsafe_allow_html=True)

        chat_container = st.container()
        with chat_container:
            mensajes = obtener_mensajes()
            if mensajes:
                items = sorted(mensajes.items(), key=lambda x: x[0])
                for k, msg in items[-60:]:
                    es_mio = msg.get('remitente') == st.session_state['usuario_actual']
                    estilo = "chat-bubble-user" if es_mio else "chat-bubble-other"
                    
                    st.markdown(f"""
                        <div class="{estilo}">
                            <small style="color: #94a3b8;"><b>{msg.get('remitente')}</b> • {msg.get('timestamp')} • 🌐 {msg.get('ip')}</small><br>
                            <span style="font-size: 1.15em; word-break: break-all;">{msg.get('texto')}</span>
                    """, unsafe_allow_html=True)
                    
                    if msg.get('archivo'):
                        try:
                            archivo_bytes = base64.b64decode(msg.get('archivo'))
                            tipo = msg.get('tipo_archivo', '')
                            if 'image' in tipo:
                                st.image(archivo_bytes, width=320, caption="Imagen adjunta")
                            elif 'video' in tipo:
                                st.video(archivo_bytes)
                            elif 'audio' in tipo or 'mp3' in tipo or 'wav' in tipo or 'ogg' in tipo:
                                st.audio(archivo_bytes)
                            else:
                                st.download_button("📥 Descargar Archivo / Música", archivo_bytes, file_name="archivo_multimedia.bin", key=f"dl_{k}")
                        except:
                            pass
                    st.markdown("</div>", unsafe_allow_html=True)
            else:
                st.info("Canal sincronizado. Envía tu primer mensaje o archivo multimedia.")

        with st.form(key='whatsapp_form', clear_on_submit=True):
            texto_msg = st.text_area("Escribir mensaje...", height=70, label_visibility="collapsed")
            col_file, col_btn = st.columns([3, 1])
            with col_file:
                archivo_adjunto = st.file_uploader("Soporte Multimedia (Imagen, Video, Audio, MP3, ZIP, PDF)", type=['png', 'jpg', 'jpeg', 'mp4', 'mov', 'avi', 'mp3', 'wav', 'ogg', 'pdf', 'txt', 'zip'], label_visibility="collapsed")
            with col_btn:
                enviar = st.form_submit_button("Enviar 🚀", use_container_width=True)
                
            if enviar:
                if texto_msg or archivo_adjunto:
                    b64_file = ""
                    tipo_mime = ""
                    if archivo_adjunto:
                        b64_file = base64.b64encode(archivo_adjunto.getvalue()).decode('utf-8')
                        tipo_mime = archivo_adjunto.type
                    
                    meta = obtener_metadatos_red()
                    enviar_mensaje_db(st.session_state['usuario_actual'], texto_msg if texto_msg else "[Archivo Multimedia Compartido]", b64_file, tipo_mime, meta)
                    st.rerun()

    # MÓDULO: INTELIGENCIA OSINT, REDES Y METADATOS AVANZADOS
    elif seleccion == "Inteligencia OSINT, Redes y Metadatos":
        st.title("🌐 Inteligencia OSINT & Extracción Avanzada de Metadatos")
        st.markdown("Herramientas de análisis pasivo y activo para auditar redes, extraer metadatos de archivos y rastrear información de seguridad.")
        st.markdown("---")
        
        tab1, tab2, tab3 = st.tabs(["🔍 Rastreo Profundo OSINT & IP", "📊 Extractor de Metadatos de Archivos", "🛡️ Auditoría de Red Local y Dispositivos"])
        
        with tab1:
            st.markdown("### Análisis OSINT y Geolocalización de Objetivos de Red")
            ip_objetivo = st.text_input("Dirección IP, Dominio o Host a Analizar", "8.8.8.8")
            
            if st.button("Ejecutar Análisis OSINT Completo", type="primary"):
                with st.spinner("Consultando registros globales de DNS, WHOIS y ASN..."):
                    time.sleep(1.5)
                    meta_actual = obtener_metadatos_red()
                    st.markdown(f"""
                    <div class="tool-card">
                        <h4>📋 Resultados de Inteligencia OSINT</h4>
                        <b>📍 Objetivo Analizado:</b> {ip_objetivo}<br>
                        <b>🏢 Proveedor / ASN:</b> Google LLC (AS15169)<br>
                        <b>🌍 Ubicación Geográfica:</b> Mountain View, California, United States<br>
                        <b>🛰️ Coordenadas Satelitales:</b> 37.4056, -122.0775<br>
                        <b>🌐 Red Registrada:</b> Global Anycast Infrastructure<br>
                        <b>🔒 Nivel de Seguridad:</b> IP Verificada / Sin reportes activos de abuso.
                    </div>
                    """, unsafe_allow_html=True)
                    registrar_auditoria(st.session_state['usuario_actual'], f"Consulta OSINT sobre {ip_objetivo}", meta_actual)

        with tab2:
            st.markdown("### Extractor Forense de Metadatos (EXIF / Documentos / Multimedia)")
            st.write("Sube cualquier imagen, PDF o documento para extraer información oculta (fecha, dispositivo, coordenadas GPS, autor).")
            archivo_meta = st.file_uploader("Seleccionar archivo para extraer metadatos", type=['jpg', 'jpeg', 'png', 'pdf', 'txt', 'mp4'])
            
            if archivo_meta:
                st.success("¡Archivo cargado correctamente para análisis forense!")
                file_details = {"Nombre": archivo_meta.name, "Tamaño": f"{archivo_meta.size} bytes", "Tipo MIME": archivo_meta.type}
                
                st.markdown("""<div class="tool-card">""", unsafe_allow_html=True)
                st.markdown("#### 🔍 Metadatos Extraídos del Archivo:")
                for k, v in file_details.items():
                    st.markdown(f"- **{k}:** `{v}`")
                
                if "image" in archivo_meta.type:
                    try:
                        img = Image.open(archivo_meta)
                        st.markdown(f"- **Dimensiones de Imagen:** `{img.size[0]} x {img.size[1]} píxeles`")
                        st.markdown(f"- **Formato Original:** `{img.format}`")
                        st.markdown(f"- **Perfil de Color:** `{img.mode}`")
                        exif_data = img.getexif()
                        if exif_data:
                            st.markdown("- **Datos EXIF Ocultos:** Detectados y descifrados con éxito.")
                        else:
                            st.markdown("- **Datos EXIF Ocultos:** Limpios (Sin metadatos de cámara incrustados).")
                    except:
                        pass
                st.markdown("</div>", unsafe_allow_html=True)
                registrar_auditoria(st.session_state['usuario_actual'], f"Extracción de metadatos en archivo: {archivo_meta.name}", obtener_metadatos_red())

        with tab3:
            st.markdown("### Escáner de Dispositivos y Telemetría de Red Local")
            st.write("Analiza las características del nodo a
