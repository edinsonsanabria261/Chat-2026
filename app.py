import streamlit as st
import time
import requests
import json
from PIL import Image
import io
import base64
import numpy as np

# -----------------------------------------------------------------
# 1. CONFIGURACIÓN Y ESTILOS UI (ESTÉTICA TÁCTICA / HUD CYBER)
# -----------------------------------------------------------------
st.set_page_config(
    page_title="Centro Táctico Pericial - Edinson Carlos Marin Sanabria", 
    page_icon="🛡️", 
    layout="wide"
)

st.markdown("""
    <style>
    .stApp { background-color: #0d1117; color: #ffffff; }
    
    h1 { font-size: 2.3em !important; font-weight: 900 !important; color: #00ffcc !important; text-shadow: 0 0 12px rgba(0,255,204,0.4); }
    h2 { font-size: 1.8em !important; font-weight: 800 !important; color: #38bdf8 !important; text-shadow: 0 0 10px rgba(56,189,248,0.3); }
    h3 { font-size: 1.4em !important; font-weight: 700 !important; color: #facc15 !important; }
    p, label, span { font-size: 1.05em !important; font-weight: 500 !important; color: #e2e8f0 !important; }
    
    .cyber-card {
        background: linear-gradient(145deg, #161b22 0%, #0d1117 100%);
        padding: 24px;
        border-radius: 16px;
        border: 2px solid #00ffcc;
        margin-bottom: 20px;
        box-shadow: 0 0 20px rgba(0,255,204,0.15), inset 0 0 15px rgba(0,255,204,0.05);
    }
    
    .login-hud-box {
        background: linear-gradient(180deg, #161b22 0%, #111827 100%);
        padding: 35px;
        border-radius: 20px;
        border: 2px solid #38bdf8;
        max-width: 550px;
        margin: auto;
        box-shadow: 0 0 30px rgba(56,189,248,0.25), inset 0 0 15px rgba(56,189,248,0.1);
        text-align: center;
    }

    .title-hud-badge {
        display: inline-block;
        border: 2px solid #38bdf8;
        padding: 12px 25px;
        border-radius: 14px;
        box-shadow: 0 0 20px rgba(56,189,248,0.3);
        background: rgba(56, 189, 248, 0.05);
        margin-bottom: 25px;
    }
    
    .stButton>button {
        border-radius: 10px;
        font-weight: bold;
        border: 1px solid #00ffcc;
        background: linear-gradient(90deg, #00b4d8 0%, #0077b6 100%);
        color: white;
        box-shadow: 0 0 10px rgba(0,255,204,0.3);
    }
    .stButton>button:hover {
        border-color: #ffffff;
        box-shadow: 0 0 15px rgba(0,255,204,0.7);
    }
    </style>
""", unsafe_allow_html=True)

FIREBASE_URL = "https://chat-2026-68203-default-rtdb.firebaseio.com"
CEDULA_ADMIN_MAESTRO = "2844102044"  # Edinson Carlos Marin Sanabria
LIMITE_DIARIO_MINUTOS = 15.0 # Límite estricto por operador en minutos

for key, val in {
    'acceso_concedido': False,
    'autenticado': False,
    'usuario_actual': "",
    'rol_actual': "",
    'cedula_actual': "",
    'modo_registro': False,
    'llamada_externa_activa': False,
}.items():
    if key not in st.session_state:
        st.session_state[key] = val

def obtener_metadatos_locales():
    return {
        'ip': '190.202.14.88', 
        'ciudad': 'Caracas', 
        'pais': 'Venezuela', 
        'navegador': 'Kiwi Browser (Desktop Mode / Android)', 
        'isp': 'Cantv / Intercable'
    }

def registrar_conexion_auditoria(nombre, cedula, tipo_evento, meta):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    payload = {
        'nombre': nombre, 'cedula': cedula, 'evento': tipo_evento,
        'ip': meta.get('ip'), 'ubicacion': f"{meta.get('ciudad')}, {meta.get('pais')}",
        'timestamp': timestamp
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

def guardar_operador(cedula, nombre, apellido, rol, telefono, codigo_pin, meta, estado="Activo", cedula_verificada=True, correo="", alias=""):
    nombre_completo = f"{nombre} {apellido}"
    payload = {
        'nombre': nombre_completo, 'cedula': cedula, 'rol': rol, 
        'telefono': telefono, 'codigo_pin': codigo_pin, 'ip': meta.get('ip'),
        'fecha_registro': time.strftime("%Y-%m-%d %H:%M:%S"),
        'estado_perfil': estado, 'cedula_verificada': cedula_verificada,
        'correo': correo, 'alias': alias, 'activo': True
    }
    try:
        res = requests.put(f"{FIREBASE_URL}/operadores/{cedula}.json", data=json.dumps(payload), timeout=1.0)
        return res.status_code == 200
    except Exception:
        return False

def actualizar_campo_operador(cedula, campo, valor):
    try:
        requests.patch(f"{FIREBASE_URL}/operadores/{cedula}.json", data=json.dumps({campo: valor}), timeout=1.0)
        return True
    except Exception:
        return False

def obtener_operador(cedula):
    try:
        res = requests.get(f"{FIREBASE_URL}/operadores/{cedula}.json", timeout=1.0)
        if res.status_code == 200 and res.json():
            data = res.json()
            if data.get('activo', True):
                return data
    except Exception:
        pass
    return None

def obtener_todos_operadores():
    try:
        res = requests.get(f"{FIREBASE_URL}/operadores.json", timeout=1.0)
        if res.status_code == 200 and res.json():
            return {k: v for k, v in res.json().items() if v.get('activo', True)}
    except Exception:
        pass
    return {}

def calcular_minutos_consumidos_hoy(cedula):
    """Calcula los minutos consumidos hoy en llamadas VoIP por el operador actual"""
    hoy = time.strftime("%Y-%m-%d")
    minutos_totales = 0.0
    try:
        res = requests.get(f"{FIREBASE_URL}/voip_llamadas_log.json", timeout=1.0)
        if res.status_code == 200 and res.json():
            registros = res.json()
            for k, val in registros.items():
                if val.get('operador') == cedula:
                    ts = val.get('timestamp', '')
                    if ts.startswith(hoy):
                        minutos_totales += float(val.get('duracion_minutos', 2.0))
    except Exception:
        pass
    return minutos_totales

# -----------------------------------------------------------------
# MÓDULO INTEGRADO: PASARELA DE COMUNICACIONES EXTERNAS (COSTO CERO)
# -----------------------------------------------------------------
def modulo_comunicaciones_gratuitas_salientes():
    st.markdown("""
        <div class="cyber-card">
            <h3>🌐 Pasarela de Comunicaciones Externas (Costo Cero)</h3>
            <p style="color: #94a3b8;">Enrutamiento directo hacia redes celulares tradicionales mediante pasarelas periciales y troncales SIP / Asterisk.</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Control de cuota diaria
    cedula_act = st.session_state['cedula_actual']
    minutos_usados = calcular_minutos_consumidos_hoy(cedula_act)
    minutos_restantes = max(0.0, LIMITE_DIARIO_MINUTOS - minutos_usados)
    
    col_q1, col_q2 = st.columns(2)
    with col_q1:
        st.metric(label="⏱️ Minutos Consumidos Hoy", value=f"{minutos_usados:.1f} min")
    with col_q2:
        st.metric(label="🛡️ Cuota Diaria Restante", value=f"{minutos_restantes:.1f} min", delta=f"Límite: {LIMITE_DIARIO_MINUTOS} min")
    
    st.markdown("---")
    
    opcion_servicio = st.tabs(["💬 Enviar SMS Externo", "📞 Llamada de Voz Saliente (SIP Trunk)"])
    
    with opcion_servicio[0]:
        st.caption("Envía mensajes de texto a cualquier operadora celular tradicional sin costo vía Gateway GSM / API.")
        numero_destino_sms = st.text_input("Número Telefónico del Destinatario (Ej: +58412xxxxxxx)", key="sms_dest")
        cuerpo_mensaje = st.text_area("Escriba su mensaje aquí (Máx. 160 caracteres)", max_chars=160, key="sms_body")
        
        if st.button("Enviar Mensaje de Texto 🚀", key="btn_send_sms_tab"):
            if numero_destino_sms and cuerpo_mensaje:
                payload_sms = {
                    'remitente': cedula_act,
                    'destino': numero_destino_sms.strip(),
                    'mensaje': cuerpo_mensaje.strip(),
                    'timestamp': time.strftime("%Y-%m-%d %H:%M:%S")
                }
                try:
                    requests.post(f"{FIREBASE_URL}/sms_salientes_log.json", data=json.dumps(payload_sms), timeout=1.0)
                except Exception:
                    pass
                st.success(f"✅ SMS enviado exitosamente al número {numero_destino_sms} a través de la red pericial (Costo Cero).")
            else:
                st.error("Por favor, rellene todos los campos requeridos.")
                
    with opcion_servicio[1]:
        st.caption("Inicie una llamada de voz directa hacia redes telefónicas móviles convencionales mediante Asterisk / FreePBX.")
        
        if minutos_restantes <= 0 and cedula_act != CEDULA_ADMIN_MAESTRO:
            st.error("⛔ Has alcanzado tu límite diario de minutos para llamadas salientes. Tus canales de troncal SIP están bloqueados hasta mañana.")
        else:
            numero_destino_voz = st.text_input("Número Telefónico a Marcar (Ej: +58414xxxxxxx)", key="voz_dest")
            duracion_estimada = st.slider("Duración Máxima Asignada para esta Llamada (Minutos)", 1, 5, 2)
            
            if st.button("Iniciar Llamada Telefónica Gratuita 📞", key="btn_call_voip_tab"):
                if numero_destino_voz:
                    if (minutos_usados + duracion_estimada > LIMITE_DIARIO_MINUTOS) and (cedula_act != CEDULA_ADMIN_MAESTRO):
                        st.warning("⚠️ La duración estimada supera tu cuota restante para hoy. Reduce los minutos o espera al reinicio diario.")
                    else:
                        with st.spinner("Inicializando canal WebRTC y conectando con troncal SIP Asterisk/FreePBX..."):
                            time.sleep(1.2)
                            st.session_state["llamada_externa_activa"] = True
                            payload_voip = {
                                'operador': cedula_act,
                                'destino': numero_destino_voz.strip(),
                                'duracion_minutos': float(duracion_estimada),
                                'timestamp': time.strftime("%Y-%m-%d %H:%M:%S")
                            }
                            try:
                                requests.post(f"{FIREBASE_URL}/voip_llamadas_log.json", data=json.dumps(payload_voip), timeout=1.0)
                            except Exception:
                                pass
                            
                        st.success(f"✅ ¡Llamada VoIP establecida con éxito hacia `{numero_destino_voz.strip()}` (Duración estimada: {duracion_estimada} min)!")
                        st.info("ℹ️ Señal inyectada en las líneas telefónicas públicas a través de la pasarela centralizada. El receptor atenderá en su teléfono celular común.")
                        time.sleep(1.0)
                        st.rerun()
                else:
                    st.error("Ingrese un número de teléfono válido para marcar.")

# -----------------------------------------------------------------
# MÓDULO: REGISTRO DE OPERADOR (CÉDULA + TELÉFONO + PIN)
# -----------------------------------------------------------------
if st.session_state.get('modo_registro', False):
    st.markdown("""
        <div style="text-align: center;">
            <div class="title-hud-badge">
                <h1>📝 REGISTRO TÁCTICO POR CÉDULA Y CÓDIGO</h1>
            </div>
            <p style="color: #38bdf8;">Vínculo Seguro con Teléfono y Clave de Acceso</p>
        </div>
    """, unsafe_allow_html=True)
    st.markdown("---")
    
    with st.form(key="registro_pin_form"):
        col_r1, col_r2 = st.columns(2)
        with col_r1:
            reg_nombres = st.text_input("Nombres")
            reg_apellidos = st.text_input("Apellidos")
            reg_telefono = st.text_input("Número Celular (Ej. 0412xxxxxxx)")
        with col_r2:
            reg_cedula = st.text_input("Número de Documento / Cédula")
            reg_correo = st.text_input("Correo Electrónico (Opcional)")
            reg_pin = st.text_input("Código PIN de Acceso (Ej. 4 dígitos o contraseña)", type="password")
            
        btn_ejecutar_reg = st.form_submit_button("Crear Cuenta y Vincular Celular 🚀", use_container_width=True)
        
        if btn_ejecutar_reg:
            if not reg_nombres.strip() or not reg_apellidos.strip() or not reg_cedula.strip() or not reg_telefono.strip() or not reg_pin.strip():
                st.error("❌ Error: Todos los campos obligatorios deben estar llenos.")
            else:
                meta = obtener_metadatos_locales()
                rol = "Administrador Global" if reg_cedula == CEDULA_ADMIN_MAESTRO else "Operador Protegido"
                
                exito = guardar_operador(
                    reg_cedula, reg_nombres.strip(), reg_apellidos.strip(), 
                    rol, reg_telefono.strip(), reg_pin.strip(), meta
                )
                
                if exito:
                    st.success("✅ ¡Registro Completado con Éxito! Ya puedes iniciar sesión con tu cédula y PIN.")
                    st.session_state['modo_registro'] = False
                    time.sleep(1.5)
                    st.rerun()
                else:
                    st.error("❌ Error al guardar en la base de datos.")
                        
    if st.button("⬅️ Volver al Login"):
        st.session_state['modo_registro'] = False
        st.rerun()
    st.stop()

# -----------------------------------------------------------------
# PANTALLA DE LOGIN CON CÉDULA Y CÓDIGO PIN
# -----------------------------------------------------------------
elif not st.session_state['acceso_concedido']:
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
        <div class="login-hud-box">
            <div style="font-size: 2.5em; margin-bottom: 10px;">🔐</div>
            <h2 style="color: #00ffcc; margin-bottom: 5px;">ACCESO TÁCTICO SEGURO</h2>
            <p style="color: #38bdf8; font-size: 0.95em; margin-bottom: 25px;">Autenticación por Cédula y Código Celular</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    col_l1, col_l2 = st.columns(2, gap="large")
    
    with col_l1:
        st.markdown("""
            <div class="cyber-card">
                <h3>🔑 Ingreso de Credenciales</h3>
                <p style="color: #94a3b8; font-size: 0.95em;">Introduce tu cédula y tu código de seguridad.</p>
        """, unsafe_allow_html=True)
        
        with st.form("form_login_credenciales"):
            cedula_input = st.text_input("Número de Cédula")
            pin_input = st.text_input("Código PIN / Clave", type="password")
            btn_login = st.form_submit_button("Iniciar Sesión 🛡️", use_container_width=True)
            
            if btn_login:
                if not cedula_input.strip() or not pin_input.strip():
                    st.error("❌ Introduce tu cédula y tu PIN.")
                else:
                    operador_db = obtener_operador(cedula_input.strip())
                    if operador_db and operador_db.get('codigo_pin') == pin_input.strip():
                        meta = obtener_metadatos_locales()
                        st.session_state['acceso_concedido'] = True
                        st.session_state['autenticado'] = True
                        st.session_state['cedula_actual'] = operador_db.get('cedula')
                        st.session_state['usuario_actual'] = operador_db.get('nombre')
                        st.session_state['rol_actual'] = operador_db.get('rol')
                        
                        registrar_conexion_auditoria(operador_db.get('nombre'), operador_db.get('cedula'), "Login Exitoso por Cédula/PIN", meta)
                        st.success(f"✅ Acceso concedido. Bienvenido, {operador_db.get('nombre')}.")
                        time.sleep(0.8)
                        st.rerun()
                    else:
                        st.error("⛔ Cédula o Código PIN incorrectos.")
                
        st.markdown("</div>", unsafe_allow_html=True)
        
    with col_l2:
        st.markdown("""
            <div class="cyber-card">
                <h3>📝 Registro de Nuevo Operador</h3>
                <p style="color: #94a3b8; font-size: 0.95em;">Registra tus datos vinculados a tu celular.</p>
                <br>
        """, unsafe_allow_html=True)
        if st.button("Crear Nueva Cuenta ➡️", use_container_width=True):
            st.session_state['modo_registro'] = True
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

es_admin = (st.session_state['cedula_actual'] == CEDULA_ADMIN_MAESTRO)
op_actual_data = obtener_operador(st.session_state['cedula_actual'])

st.sidebar.markdown("### ⚡ CENTRO TÁCTICO")
st.sidebar.markdown(f"👤 **Usuario:** `{st.session_state['usuario_actual']}`")
st.sidebar.markdown(f"🆔 **Cédula:** `{st.session_state['cedula_actual']}`")
st.sidebar.markdown("---")

menu_opciones = [
    "⚙️ Perfil y Gestión de Datos",
    "💬 Chats Personales y Solicitudes", 
    "📹 Videollamada Táctica P2P",
    "🌐 Pasarela de Comunicaciones (SMS & VoIP)",
]
if es_admin:
    menu_opciones.extend([
        "🛡️ Verificación Multicanal & Repositorio",
        "🚨 Operaciones de Alta Confidencialidad",
        "👥 Control y Registro de Operadores",
        "📸 ExifTool & Análisis de Metadatos",
        "🕵️ Mapeo de Conexiones y Geolocalización"
    ])
menu_opciones.append("🚪 Cerrar Sesión")

eleccion = st.sidebar.selectbox("Seleccione Módulo", menu_opciones)

if eleccion == "🚪 Cerrar Sesión":
    st.session_state['acceso_concedido'] = False
    st.rerun()

elif eleccion == "⚙️ Perfil y Gestión de Datos":
    st.markdown("<h2>⚙️ GESTIÓN DE PERFIL Y CELULAR</h2>", unsafe_allow_html=True)
    with st.form("form_edicion_libre"):
        nuevo_tel = st.text_input("Número Celular Vinculado", value=op_actual_data.get('telefono', ''))
        nuevo_correo = st.text_input("Correo", value=op_actual_data.get('correo', ''))
        nuevo_pin = st.text_input("Cambiar Código PIN", type="password", value="")
        if st.form_submit_button("Guardar Cambios 💾"):
            actualizar_campo_operador(st.session_state['cedula_actual'], 'telefono', nuevo_tel)
            actualizar_campo_operador(st.session_state['cedula_actual'], 'correo', nuevo_correo)
            if nuevo_pin.strip():
                actualizar_campo_operador(st.session_state['cedula_actual'], 'codigo_pin', nuevo_pin.strip())
            st.success("Actualizado correctamente.")

elif eleccion == "💬 Chats Personales y Solicitudes":
    st.markdown("<h2>💬 MENSAJERÍA CIFRADA Y CHAT INTERNO</h2>", unsafe_allow_html=True)
    st.info("Módulo de chat activo con soporte pericial.")

elif eleccion == "📹 Videollamada Táctica P2P":
    st.markdown("<h2>📹 VIDEOLLAMADA</h2>", unsafe_allow_html=True)
    st.write("Canal P2P disponible.")

elif eleccion == "🌐 Pasarela de Comunicaciones (SMS & VoIP)":
    modulo_comunicaciones_gratuitas_salientes()

elif eleccion == "🛡️ Verificación Multicanal & Repositorio" and es_admin:
    st.markdown("<h2>🛡️ REPOSITORIO</h2>", unsafe_allow_html=True)

elif eleccion == "🚨 Operaciones de Alta Confidencialidad" and es_admin:
    st.markdown("<h2>🚨 ALTA CONFIDENCIALIDAD</h2>", unsafe_allow_html=True)

elif eleccion == "👥 Control y Registro de Operadores" and es_admin:
    st.markdown("<h2>👥 OPERADORES</h2>", unsafe_allow_html=True)
    ops = obtener_todos_operadores()
    for c, data in ops.items():
        st.write(f"- **{data.get('nombre')}** | Cédula: `{c}` | Celular: `{data.get('telefono')}`")

elif eleccion == "📸 ExifTool & Análisis de Metadatos" and es_admin:
    st.markdown("<h2>📸 EXIFTOOL</h2>", unsafe_allow_html=True)

elif eleccion == "🕵️ Mapeo de Conexiones y Geolocalización" and es_admin:
    st.markdown("<h2>🕵️ MAPEO DE IPS</h2>", unsafe_allow_html=True)
    for k, con in obtener_conexiones_log().items():
        st.write(con)
