import streamlit as st
import time
import requests
import json
from PIL import Image
import io
import base64
import numpy as np
import hashlib
import random

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
    
    .chat-bubble-user {
        background: linear-gradient(135deg, #00e676 0%, #00b0ff 100%);
        color: #000000;
        padding: 14px 18px;
        border-radius: 16px 16px 4px 16px;
        margin-bottom: 12px;
        max-width: 85%;
        margin-left: auto;
        font-weight: 700 !important;
        box-shadow: 0 4px 15px rgba(0,230,118,0.3);
    }
    
    .chat-bubble-other {
        background-color: #161b22;
        color: #ffffff;
        padding: 14px 18px;
        border-radius: 16px 16px 16px 4px;
        margin-bottom: 12px;
        max-width: 85%;
        border-left: 4px solid #38bdf8;
        border-top: 1px solid #30363d;
        border-right: 1px solid #30363d;
        border-bottom: 1px solid #30363d;
        font-weight: 600 !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.4);
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

for key, val in {
    'acceso_concedido': False,
    'autenticado': False,
    'usuario_actual': "",
    'rol_actual': "",
    'cedula_actual': "",
    'modo_registro': False,
    'estado_perfil': "Restringido",
    'cedula_verificada': False,
    'stickers_enviados_sesion': 0,
    'puntuacion_juego': 0
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

# Pipeline Seguro basado en Pillow y NumPy (Sin librerías externas pesadas)
def procesar_rostro_seguro(imagen_bytes):
    try:
        image_stream = io.BytesIO(imagen_bytes)
        pil_img = Image.open(image_stream).convert('RGB').resize((128, 128))
        img_arr = np.array(pil_img, dtype=np.float32) / 255.0
        
        if np.var(img_arr) < 0.001:
            return False, "❌ Alerta: Imagen estática o sin contraste detectada.", None
            
        vectores_rostro = img_arr.flatten()
        return True, "✅ Vectores biométricos extraídos correctamente.", vectores_rostro
    except Exception as e:
        return False, f"❌ Error en el pipeline biométrico: {str(e)}", None

def comparar_vectores_faciales(vec_nuevo, vec_registrado_b64):
    try:
        vec_reg = np.frombuffer(base64.b64decode(vec_registrado_b64), dtype=np.float32)
        if vec_nuevo.shape != vec_reg.shape:
            return False
        mse = np.mean((vec_nuevo - vec_reg) ** 2)
        return mse < 0.08
    except Exception:
        return False

def guardar_operador(cedula, nombre, apellido, rol, foto_bytes, vectores_arr, meta, estado="Restringido", cedula_verificada=False, telefono="", correo="", alias="", provisional=False):
    foto_b64 = base64.b64encode(foto_bytes).decode('utf-8') if foto_bytes else ""
    vector_b64 = base64.b64encode(vectores_arr.tobytes()).decode('utf-8') if vectores_arr is not None else ""
    nombre_completo = f"{nombre} {apellido}"
    
    payload = {
        'nombre': nombre_completo, 'cedula': cedula, 'rol': rol, 'foto': foto_b64,
        'vector_facial': vector_b64, 'ip': meta.get('ip'),
        'fecha_registro': time.strftime("%Y-%m-%d %H:%M:%S"),
        'estado_perfil': estado, 'cedula_verificada': cedula_verificada,
        'telefono': telefono, 'correo': correo, 'alias': alias, 'provisional': provisional, 'activo': True
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

def eliminar_cuenta_soft_delete(cedula, motivo=""):
    meta = obtener_metadatos_locales()
    try:
        requests.patch(f"{FIREBASE_URL}/operadores/{cedula}.json", data=json.dumps({'activo': False, 'estado_perfil': 'Cuenta Eliminada'}), timeout=1.0)
        return True
    except Exception:
        return False

def enviar_solicitud_cambio_cedula(cedula_actual, nueva_cedula, motivo):
    payload = {'cedula_actual': cedula_actual, 'nueva_cedula': nueva_cedula, 'motivo': motivo, 'estado': 'pendiente', 'timestamp': time.strftime("%Y-%m-%d %H:%M:%S")}
    try:
        requests.post(f"{FIREBASE_URL}/solicitudes_cambio_cedula.json", data=json.dumps(payload), timeout=1.0)
        return True
    except Exception:
        return False

def obtener_solicitudes_cambio_cedula():
    try:
        res = requests.get(f"{FIREBASE_URL}/solicitudes_cambio_cedula.json", timeout=1.0)
        if res.status_code == 200 and res.json():
            return res.json()
    except Exception:
        pass
    return {}

def actualizar_estado_solicitud_cedula(key_sol, nuevo_estado):
    try:
        requests.patch(f"{FIREBASE_URL}/solicitudes_cambio_cedula/{key_sol}.json", data=json.dumps({'estado': nuevo_estado}), timeout=1.0)
        return True
    except Exception:
        return False

def guardar_archivo_repositorio(cedula, nombre_archivo, archivo_bytes):
    b64_file = base64.b64encode(archivo_bytes).decode('utf-8')
    payload = {'nombre_archivo': nombre_archivo, 'archivo_b64': b64_file, 'timestamp': time.strftime("%Y-%m-%d %H:%M:%S")}
    try:
        requests.post(f"{FIREBASE_URL}/repositorio_verificaciones/{cedula}.json", data=json.dumps(payload), timeout=1.0)
        return True
    except Exception:
        return False

def enviar_solicitud_amistad(cedula_remitente, nombre_remitente, cedula_destino):
    payload = {'remitente_cedula': cedula_remitente, 'remitente_nombre': nombre_remitente, 'estado': 'pendiente', 'timestamp': time.strftime("%Y-%m-%d %H:%M:%S")}
    try:
        requests.post(f"{FIREBASE_URL}/solicitudes/{cedula_destino}.json", data=json.dumps(payload), timeout=1.0)
        return True
    except Exception:
        return False

def obtener_solicitudes(cedula):
    try:
        res = requests.get(f"{FIREBASE_URL}/solicitudes/{cedula}.json", timeout=1.0)
        if res.status_code == 200 and res.json():
            return res.json()
    except Exception:
        pass
    return {}

def actualizar_estado_solicitud(cedula_destino, key_solicitud, nuevo_estado):
    try:
        requests.patch(f"{FIREBASE_URL}/solicitudes/{cedula_destino}/{key_solicitud}.json", data=json.dumps({'estado': nuevo_estado}), timeout=1.0)
        return True
    except Exception:
        return False

def enviar_mensaje_privado(cedula_emisor, cedula_receptor, texto, tipo="texto", audio_b64=None):
    sala_id = "_".join(sorted([cedula_emisor, cedula_receptor]))
    meta = obtener_metadatos_locales()
    payload = {'remitente_cedula': cedula_emisor, 'receptor_cedula': cedula_receptor, 'texto': texto, 'tipo': tipo, 'audio_b64': audio_b64 if audio_b64 else "", 'timestamp': time.strftime("%H:%M:%S - %d/%m/%Y"), 'ip': meta.get('ip')}
    try:
        requests.post(f"{FIREBASE_URL}/chats_privados/{sala_id}.json", data=json.dumps(payload), timeout=0.8)
    except Exception:
        pass

def obtener_mensajes_privados(cedula_1, cedula_2):
    sala_id = "_".join(sorted([cedula_1, cedula_2]))
    try:
        res = requests.get(f"{FIREBASE_URL}/chats_privados/{sala_id}.json", timeout=1.0)
        if res.status_code == 200 and res.json():
            return res.json()
    except Exception:
        pass
    return {}

# -----------------------------------------------------------------
# MÓDULO: REGISTRO BIOMÉTRICO
# -----------------------------------------------------------------
if st.session_state.get('modo_registro', False):
    st.markdown("""
        <div style="text-align: center;">
            <div class="title-hud-badge">
                <h1>👁️ REGISTRO BIOMÉTRICO ASÍNCRONO</h1>
            </div>
            <p style="color: #38bdf8;">Registro por Reconocimiento Facial Activo</p>
        </div>
    """, unsafe_allow_html=True)
    st.markdown("---")
    
    tipo_registro_modo = st.radio("Seleccione la modalidad de registro:", ["📸 Flujo Con Cámara", "💻 Flujo Sin Cámara (Provisional)"])
    
    with st.form(key="registro_asincrono_form"):
        col_r1, col_r2 = st.columns(2)
        with col_r1:
            reg_nombres = st.text_input("Nombres")
            reg_apellidos = st.text_input("Apellidos")
            reg_telefono = st.text_input("Teléfono de Contacto")
        with col_r2:
            reg_cedula = st.text_input("Número de Documento / Cédula")
            reg_correo = st.text_input("Correo Electrónico")
            reg_alias = st.text_input("Alias Táctico")
            
        foto_en_reg_vivo = None
        if "Con Cámara" in tipo_registro_modo:
            st.markdown("### 📸 Captura Biométrica")
            foto_en_reg_vivo = st.camera_input("Selfie de Registro")
            
        btn_ejecutar_reg = st.form_submit_button("Completar Registro 🚀", use_container_width=True)
        
        if btn_ejecutar_reg:
            if not reg_nombres.strip() or not reg_apellidos.strip() or not reg_cedula.strip():
                st.error("❌ Error: Nombres, Apellidos y Cédula son obligatorios.")
            elif "Con Cámara" in tipo_registro_modo and not foto_en_reg_vivo:
                st.error("❌ Error: Se requiere captura facial.")
            else:
                meta = obtener_metadatos_locales()
                rol = "Administrador Global" if reg_cedula == CEDULA_ADMIN_MAESTRO else "Operador Protegido"
                
                if "Sin Cámara" in tipo_registro_modo:
                    guardar_operador(reg_cedula, reg_nombres.strip(), reg_apellidos.strip(), rol, b'', None, meta, estado="Restringido (Provisional)", provisional=True, telefono=reg_telefono, correo=reg_correo, alias=reg_alias)
                    st.warning("⚠️ Cuenta Provisional asignada.")
                    time.sleep(1.5)
                    st.session_state['modo_registro'] = False
                    st.rerun()
                else:
                    bytes_selfie = foto_en_reg_vivo.getvalue()
                    valido_bio, msg_bio, vectores_result = procesar_rostro_seguro(bytes_selfie)
                    
                    if not valido_bio:
                        st.error(msg_bio)
                    else:
                        estado_inicial = "Activo / Desbloqueado" if reg_cedula == CEDULA_ADMIN_MAESTRO else "Restringido"
                        cedula_aprobada = True if reg_cedula == CEDULA_ADMIN_MAESTRO else False
                        
                        guardar_operador(reg_cedula, reg_nombres.strip(), reg_apellidos.strip(), rol, bytes_selfie, vectores_result, meta, estado=estado_inicial, cedula_verificada=cedula_aprobada, telefono=reg_telefono, correo=reg_correo, alias=reg_alias)
                        st.success("✅ ¡Registro Exitoso!")
                        st.session_state['modo_registro'] = False
                        time.sleep(1.2)
                        st.rerun()
                        
    if st.button("⬅️ Volver al Login"):
        st.session_state['modo_registro'] = False
        st.rerun()
    st.stop()

# -----------------------------------------------------------------
# PANTALLA DE LOGIN
# -----------------------------------------------------------------
elif not st.session_state['acceso_concedido']:
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
        <div class="login-hud-box">
            <div style="font-size: 2.5em; margin-bottom: 10px;">👁️</div>
            <h2 style="color: #00ffcc; margin-bottom: 5px;">LOGIN SIN CREDENCIALES</h2>
            <p style="color: #38bdf8; font-size: 0.95em; margin-bottom: 25px;">Reconocimiento Facial Activo</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    col_l1, col_l2 = st.columns(2, gap="large")
    
    with col_l1:
        st.markdown("""
            <div class="cyber-card">
                <h3>📸 Inicio de Sesión Biométrico</h3>
                <p style="color: #94a3b8; font-size: 0.95em;">Colóquese frente a la cámara para acceder.</p>
        """, unsafe_allow_html=True)
        
        foto_login_inmediato = st.camera_input("Escaneo de Acceso")
        
        if foto_login_inmediato:
            bytes_login = foto_login_inmediato.getvalue()
            valido_login, msg_l, vectores_login = procesar_rostro_seguro(bytes_login)
            
            if not valido_login:
                st.error(msg_l)
            else:
                todos_ops = obtener_todos_operadores()
                usuario_encontrado = None
                
                for ced, dat in todos_ops.items():
                    vector_b64 = dat.get('vector_facial')
                    if vector_b64 and comparar_vectores_faciales(vectores_login, vector_b64):
                        usuario_encontrado = dat
                        break
                
                if usuario_encontrado:
                    meta = obtener_metadatos_locales()
                    st.session_state['acceso_concedido'] = True
                    st.session_state['autenticado'] = True
                    st.session_state['cedula_actual'] = usuario_encontrado.get('cedula')
                    st.session_state['usuario_actual'] = usuario_encontrado.get('nombre')
                    st.session_state['rol_actual'] = usuario_encontrado.get('rol')
                    
                    registrar_conexion_auditoria(usuario_encontrado.get('nombre'), usuario_encontrado.get('cedula'), "Login Exitoso", meta)
                    st.success(f"✅ Bienvenido, {usuario_encontrado.get('nombre')}.")
                    time.sleep(0.8)
                    st.rerun()
                else:
                    st.error("⛔ ALERTA: Rostro no reconocido.")
                
        st.markdown("</div>", unsafe_allow_html=True)
        
    with col_l2:
        st.markdown("""
            <div class="cyber-card">
                <h3>📝 Registro de Nuevo Operador</h3>
                <p style="color: #94a3b8; font-size: 0.95em;">Cree su perfil pericial.</p>
                <br>
        """, unsafe_allow_html=True)
        if st.button("Iniciar Registro ➡️", use_container_width=True):
            st.session_state['modo_registro'] = True
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

es_admin = (st.session_state['cedula_actual'] == CEDULA_ADMIN_MAESTRO)
op_actual_data = obtener_operador(st.session_state['cedula_actual'])
cedula_verificada_actual = (op_actual_data.get('cedula_verificada', False) if op_actual_data else False) or es_admin

st.sidebar.markdown("### ⚡ CENTRO TÁCTICO")
st.sidebar.markdown(f"👤 **Usuario:** `{st.session_state['usuario_actual']}`")
st.sidebar.markdown(f"🆔 **Cédula:** `{st.session_state['cedula_actual']}`")
st.sidebar.markdown("---")

menu_opciones = [
    "⚙️ Perfil y Gestión de Datos",
    "💬 Chats Personales y Solicitudes", 
    "📹 Videollamada Táctica P2P"
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
    st.markdown("<h2>⚙️ GESTIÓN DE PERFIL</h2>", unsafe_allow_html=True)
    with st.form("form_edicion_libre"):
        nuevo_tel = st.text_input("Teléfono", value=op_actual_data.get('telefono', ''))
        nuevo_correo = st.text_input("Correo", value=op_actual_data.get('correo', ''))
        if st.form_submit_button("Guardar Cambios 💾"):
            actualizar_campo_operador(st.session_state['cedula_actual'], 'telefono', nuevo_tel)
            actualizar_campo_operador(st.session_state['cedula_actual'], 'correo', nuevo_correo)
            st.success("Actualizado.")

elif eleccion == "💬 Chats Personales y Solicitudes":
    st.markdown("<h2>💬 MENSAJERÍA CIFRADA</h2>", unsafe_allow_html=True)
    st.info("Módulo de chat activo.")

elif eleccion == "📹 Videollamada Táctica P2P":
    st.markdown("<h2>📹 VIDEOLLAMADA</h2>", unsafe_allow_html=True)
    st.camera_input("Cámara P2P")

elif eleccion == "🛡️ Verificación Multicanal & Repositorio" and es_admin:
    st.markdown("<h2>🛡️ REPOSITORIO</h2>", unsafe_allow_html=True)

elif eleccion == "🚨 Operaciones de Alta Confidencialidad" and es_admin:
    st.markdown("<h2>🚨 ALTA CONFIDENCIALIDAD</h2>", unsafe_allow_html=True)

elif eleccion == "👥 Control y Registro de Operadores" and es_admin:
    st.markdown("<h2>👥 OPERADORES</h2>", unsafe_allow_html=True)

elif eleccion == "📸 ExifTool & Análisis de Metadatos" and es_admin:
    st.markdown("<h2>📸 EXIFTOOL</h2>", unsafe_allow_html=True)

elif eleccion == "🕵️ Mapeo de Conexiones y Geolocalización" and es_admin:
    st.markdown("<h2>🕵️ MAPEO DE IPs</h2>", unsafe_allow_html=True)
    for k, con in obtener_conexiones_log().items():
        st.write(con)
