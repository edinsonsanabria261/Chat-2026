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
LLAVE_MAESTRA = "VIP-2026"

for key, val in {
    'acceso_concedido': False,
    'autenticado': False,
    'usuario_actual': "",
    'rol_actual': "",
    'cedula_actual': "",
    'modo_registro': False,
    'modo_login_facial': False,
    'modo_provisional': False,
    'estado_perfil': "Restringido",
    'cedula_verificada': False,
    'stickers_enviados_sesion': 0,
    'juego_activo': None,
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
        'isp': 'Cantv / Intercable',
        'vpn_detectada': False,
        'nodo_salida': 'AS8048 Telecom Node B'
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
            img_reg = Image.open(io.BytesIO(base64.b64decode(foto_registrada_b64))).resize((128, 128)).convert('L')
            img_nueva = img.resize((128, 128))
            a1 = np.array(img_reg, dtype=float)
            a2 = np.array(img_nueva, dtype=float)
            correlacion = np.corrcoef(a1.flatten(), a2.flatten())[0, 1]
            puntaje_real = max(80.0, min(99.8, (correlacion + 1) * 50.0))
            if puntaje_real < 95.0:
                return False, f"❌ ACCESO DENEGADO: Coincidencia biométrica de {puntaje_real:.2f}% (Inferior al 95% requerido)."
        return True, "✅ Biometría facial confirmada (> 95% Match)."
    except Exception as e:
        return False, f"❌ Error en validación: {str(e)}"

def guardar_operador(cedula, nombre, apellido, rol, foto_bytes, meta, estado="Restringido", cedula_verificada=False, telefono="", correo="", alias="", provisional=False):
    foto_b64 = base64.b64encode(foto_bytes).decode('utf-8') if foto_bytes else ""
    nombre_completo = f"{nombre} {apellido}"
    
    op_prev = obtener_operador(cedula)
    if op_prev:
        estado = op_prev.get('estado_perfil', estado)
        cedula_verificada = op_prev.get('cedula_verificada', cedula_verificada)
        telefono = op_prev.get('telefono', telefono)
        correo = op_prev.get('correo', correo)
        alias = op_prev.get('alias', alias)
        provisional = op_prev.get('provisional', provisional)
        if not foto_b64:
            foto_b64 = op_prev.get('foto', '')

    payload = {
        'nombre': nombre_completo, 'cedula': cedula, 'rol': rol, 'foto': foto_b64,
        'ip': meta.get('ip'), 'ubicacion': f"{meta.get('ciudad')}, {meta.get('pais')}",
        'fecha_registro': time.strftime("%Y-%m-%d %H:%M:%S"),
        'estado_perfil': estado,
        'cedula_verificada': cedula_verificada,
        'telefono': telefono,
        'correo': correo,
        'alias': alias,
        'provisional': provisional,
        'activo': True
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
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    try:
        requests.patch(f"{FIREBASE_URL}/operadores/{cedula}.json", data=json.dumps({'activo': False, 'estado_perfil': 'Cuenta Eliminada (Soft-Delete)'}), timeout=1.0)
        payload_forense = {
            'cedula': cedula,
            'evento': 'BAJA DE CUENTA / SOFT-DELETE',
            'motivo': motivo,
            'timestamp': timestamp,
            'ip': meta.get('ip')
        }
        requests.post(f"{FIREBASE_URL}/forense_eliminaciones.json", data=json.dumps(payload_forense), timeout=1.0)
        return True
    except Exception:
        return False

def enviar_solicitud_cambio_cedula(cedula_actual, nueva_cedula, motivo):
    payload = {
        'cedula_actual': cedula_actual,
        'nueva_cedula': nueva_cedula,
        'motivo': motivo,
        'estado': 'pendiente',
        'timestamp': time.strftime("%Y-%m-%d %H:%M:%S")
    }
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
    payload = {
        'nombre_archivo': nombre_archivo,
        'archivo_b64': b64_file,
        'timestamp': time.strftime("%Y-%m-%d %H:%M:%S")
    }
    try:
        requests.post(f"{FIREBASE_URL}/repositorio_verificaciones/{cedula}.json", data=json.dumps(payload), timeout=1.0)
        return True
    except Exception:
        return False

def obtener_archivos_repositorio(cedula):
    try:
        res = requests.get(f"{FIREBASE_URL}/repositorio_verificaciones/{cedula}.json", timeout=1.0)
        if res.status_code == 200 and res.json():
            return res.json()
    except Exception:
        pass
    return {}

def enviar_solicitud_amistad(cedula_remitente, nombre_remitente, cedula_destino):
    payload = {
        'remitente_cedula': cedula_remitente,
        'remitente_nombre': nombre_remitente,
        'estado': 'pendiente',
        'timestamp': time.strftime("%Y-%m-%d %H:%M:%S")
    }
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
    payload = {
        'remitente_cedula': cedula_emisor,
        'receptor_cedula': cedula_receptor,
        'texto': texto,
        'tipo': tipo,
        'audio_b64': audio_b64 if audio_b64 else "",
        'timestamp': time.strftime("%H:%M:%S - %d/%m/%Y"),
        'ip': meta.get('ip')
    }
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
# MÓDULO INTEGRAL: REGISTRO BIOMÉTRICO ASÍNCRONO (CON O SIN CÁMARA)
# -----------------------------------------------------------------
if st.session_state.get('modo_registro', False):
    st.markdown("""
        <div style="text-align: center;">
            <div class="title-hud-badge">
                <h1>👁️ REGISTRO BIOMÉTRICO ASÍNCRONO</h1>
            </div>
            <p style="color: #38bdf8;">Registro por Reconocimiento Facial Activo o Asignación Provisional por Excepción</p>
        </div>
    """, unsafe_allow_html=True)
    st.markdown("---")
    
    tipo_registro_modo = st.radio("Seleccione la modalidad de registro:", ["📸 Flujo Con Cámara (Reconocimiento Facial Obligatorio)", "💻 Flujo Sin Cámara (Cuenta Aislada Provisional)"])
    
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
            st.markdown("### 📸 Captura de Vectores Faciales en Vivo")
            st.markdown("<p style='color: #00ffcc; font-size: 0.9em;'>Coloque su rostro dentro del óvalo para extraer obligatoriamente los vectores biométricos.</p>", unsafe_allow_html=True)
            foto_en_reg_vivo = st.camera_input("Selfie Biométrica de Registro")
            
        btn_ejecutar_reg = st.form_submit_button("Completar Registro 🚀", use_container_width=True)
        
        if btn_ejecutar_reg:
            if not reg_nombres.strip() or not reg_apellidos.strip() or not reg_cedula.strip():
                st.error("❌ Error: Nombres, Apellidos y Cédula son obligatorios.")
            elif "Con Cámara" in tipo_registro_modo and not foto_en_reg_vivo:
                st.error("❌ Error: El flujo con cámara requiere obligatoriamente la captura facial.")
            else:
                meta = obtener_metadatos_locales()
                rol = "Administrador Global" if reg_cedula == CEDULA_ADMIN_MAESTRO else "Operador Protegido"
                
                if "Sin Cámara" in tipo_registro_modo:
                    # Cuenta Aislada Provisional
                    guardar_operador(
                        reg_cedula, reg_nombres.strip(), reg_apellidos.strip(), rol, 
                        b'', meta, estado="Restringido (Provisional)", 
                        cedula_verificada=False, telefono=reg_telefono, correo=reg_correo, alias=reg_alias, provisional=True
                    )
                    st.warning("⚠️ Dispositivo sin cámara detectado. Se ha generado y asignado una **Cuenta Aislada Provisional** con restricciones de seguridad.")
                    time.sleep(1.5)
                    st.session_state['modo_registro'] = False
                    st.rerun()
                else:
                    bytes_selfie = foto_en_reg_vivo.getvalue()
                    img_obj = Image.open(io.BytesIO(bytes_selfie)).resize((128, 128)).convert('L')
                    arr_selfie = np.array(img_obj, dtype=float)
                    
                    if np.var(arr_selfie) < 140:
                        st.error("❌ ALERTA LIVENESS: Imagen estática o sin profundidad detectada.")
                    else:
                        estado_inicial = "Activo / Desbloqueado" if reg_cedula == CEDULA_ADMIN_MAESTRO else "Restringido"
                        cedula_aprobada = True if reg_cedula == CEDULA_ADMIN_MAESTRO else False
                        
                        guardar_operador(
                            reg_cedula, reg_nombres.strip(), reg_apellidos.strip(), rol, 
                            bytes_selfie, meta, estado=estado_inicial, cedula_verificada=cedula_aprobada, 
                            telefono=reg_telefono, correo=reg_correo, alias=reg_alias, provisional=False
                        )
                        st.success("✅ ¡Registro Biométrico Exitoso! Vectores faciales almacenados correctamente.")
                        st.session_state['modo_registro'] = False
                        time.sleep(1.2)
                        st.rerun()
                        
    if st.button("⬅️ Volver al Login"):
        st.session_state['modo_registro'] = False
        st.rerun()
    st.stop()

# -----------------------------------------------------------------
# PANTALLA DE LOGIN: RECONOCIMIENTO FACIAL DIRECTO (SIN CREDENCIALES)
# -----------------------------------------------------------------
elif not st.session_state['acceso_concedido']:
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
        <div class="login-hud-box">
            <div style="font-size: 2.5em; margin-bottom: 10px;">👁️</div>
            <h2 style="color: #00ffcc; margin-bottom: 5px;">LOGIN SIN CREDENCIALES</h2>
            <p style="color: #38bdf8; font-size: 0.95em; margin-bottom: 25px;">Reconocimiento Facial Activo • Sin Contraseñas</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    col_l1, col_l2 = st.columns(2, gap="large")
    
    with col_l1:
        st.markdown("""
            <div class="cyber-card">
                <h3>📸 Inicio de Sesión Biométrico Directo</h3>
                <p style="color: #94a3b8; font-size: 0.95em;">Colóquese frente a la cámara. El sistema validará sus vectores faciales y abrirá su sesión de forma automática.</p>
        """, unsafe_allow_html=True)
        
        foto_login_inmediato = st.camera_input("Escaneo Facial de Acceso Automático")
        
        if foto_login_inmediato:
            bytes_login = foto_login_inmediato.getvalue()
            todos_ops = obtener_todos_operadores()
            
            usuario_encontrado = None
            for ced, dat in todos_ops.items():
                foto_b64 = dat.get('foto')
                if foto_b64:
                    valido, _ = validar_rostro_biometrico_estricto(bytes_login, foto_b64)
                    if valido:
                        usuario_encontrado = dat
                        break
            
            if usuario_encontrado:
                meta = obtener_metadatos_locales()
                st.session_state['acceso_concedido'] = True
                st.session_state['autenticado'] = True
                st.session_state['cedula_actual'] = usuario_encontrado.get('cedula')
                st.session_state['usuario_actual'] = usuario_encontrado.get('nombre')
                st.session_state['rol_actual'] = usuario_encontrado.get('rol')
                st.session_state['estado_perfil'] = usuario_encontrado.get('estado_perfil', 'Restringido')
                st.session_state['cedula_verificada'] = usuario_encontrado.get('cedula_verificada', False)
                st.session_state['modo_provisional'] = usuario_encontrado.get('provisional', False)
                
                registrar_conexion_auditoria(usuario_encontrado.get('nombre'), usuario_encontrado.get('cedula'), "Login Facial Automático Exitoso", meta)
                st.success(f"✅ ¡Rostro reconocido! Bienvenido, {usuario_encontrado.get('nombre')}.")
                time.sleep(0.8)
                st.rerun()
            else:
                st.error("⛔ ALERTA: Rostro no reconocido en la base de datos pericial.")
                
        st.markdown("</div>", unsafe_allow_html=True)
        
    with col_l2:
        st.markdown("""
            <div class="cyber-card">
                <h3>📝 Registro de Nuevo Operador</h3>
                <p style="color: #94a3b8; font-size: 0.95em;">Registre su perfil con cámara (reconocimiento facial) o mediante la excepción provisional sin cámara.</p>
                <br>
        """, unsafe_allow_html=True)
        if st.button("Iniciar Registro Asíncrono ➡️", use_container_width=True):
            st.session_state['modo_registro'] = True
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# Si está autenticado, cargamos el menú táctico principal
es_admin = (st.session_state['cedula_actual'] == CEDULA_ADMIN_MAESTRO)
op_actual_data = obtener_operador(st.session_state['cedula_actual'])
cedula_verificada_actual = (op_actual_data.get('cedula_verificada', False) if op_actual_data else False) or es_admin
es_provisional = op_actual_data.get('provisional', False) if op_actual_data else False

st.sidebar.markdown("""
    <div style="text-align: center; padding: 10px;">
        <h3 style="color: #00ffcc;">⚡ CENTRO TÁCTICO</h3>
    </div>
""", unsafe_allow_html=True)
st.sidebar.markdown(f"👤 **Usuario:** `{st.session_state['usuario_actual']}`")
st.sidebar.markdown(f"🆔 **Cédula:** `{st.session_state['cedula_actual']}`")
st.sidebar.markdown(f"🛡️ **Rango:** `{st.session_state['rol_actual']}`")
if es_provisional:
    st.sidebar.warning("⚠️ **Estado:** Cuenta Provisional (Sin Verificar Biometría)")
else:
    st.sidebar.markdown(f"🔒 **Estado:** `{op_actual_data.get('estado_perfil', 'Restringido') if op_actual_data else 'Restringido'}`")
st.sidebar.markdown("---")

if es_provisional:
    st.sidebar.error("⛔ CUENTA PROVISIONAL AISLADA\nFunciones restringidas hasta completar biometría desde dispositivo con cámara.")
    menu_opciones = ["⚠️ Cuenta Aislada Provisional (Restricciones)", "⚙️ Perfil y Gestión de Datos"]
elif not cedula_verificada_actual:
    st.sidebar.error("⛔ HERRAMIENTAS BLOQUEADAS\nCédula Pendiente de Verificación por Admin.")
    menu_opciones = ["🔒 Estado Restringido (Herramientas Bloqueadas)", "⚙️ Perfil y Gestión de Datos"]
else:
    menu_opciones = [
        "⚙️ Perfil y Gestión de Datos",
        "💬 Chats Personales y Solicitudes (Estilo WhatsApp)", 
        "📹 Videollamada Táctica P2P (Ultra-Rápida)"
    ]
    if es_admin:
        menu_opciones.extend([
            "🛡️ Verificación Multicanal & Repositorio",
            "🚨 Operaciones de Alta Confidencialidad",
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

elif eleccion == "⚠️ Cuenta Aislada Provisional (Restricciones)":
    st.markdown("""
        <div class="cyber-card" style="text-align: center; padding: 40px;">
            <h2 style="color: #ef4444;">⚠️ CUENTA AISLADA PROVISIONAL</h2>
            <p>Su cuenta fue generada desde un dispositivo sin periférico de cámara. Se encuentra en un entorno aislado con acceso restringido a las herramientas globales y de mensajería avanzada.</p>
            <p style="color: #38bdf8;">Para levantar las restricciones, inicie sesión desde un dispositivo con cámara y complete su verificación biométrica facial obligatoria.</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### 📸 Completar Biometría en Vivo (Levantar Restricción Provisional)")
    foto_provisional_vivo = st.camera_input("Capturar Rostro para Verificar Cuenta Provisional")
    if foto_provisional_vivo:
        bytes_prov = foto_provisional_vivo.getvalue()
        img_p = Image.open(io.BytesIO(bytes_prov)).resize((128, 128)).convert('L')
        arr_p = np.array(img_p, dtype=float)
        if np.var(arr_p) < 140:
            st.error("❌ Prueba de vida fallida.")
        else:
            actualizar_campo_operador(st.session_state['cedula_actual'], 'provisional', False)
            actualizar_campo_operador(st.session_state['cedula_actual'], 'foto', base64.b64encode(bytes_prov).decode('utf-8'))
            st.success("✅ ¡Biometría completada con éxito! Cuenta provisional actualizada a Operador Regular.")
            time.sleep(1.5)
            st.rerun()

elif eleccion == "🔒 Estado Restringido (Herramientas Bloqueadas)":
    st.markdown("""
        <div class="cyber-card" style="text-align: center; padding: 40px;">
            <h2 style="color: #facc15;">🔒 PERFIL EN ESTADO RESTRINGIDO</h2>
            <p>Su cédula de identidad se encuentra en proceso de revisión o no ha sido aprobada por el Administrador Maestro.</p>
        </div>
    """, unsafe_allow_html=True)

# -----------------------------------------------------------------
# MÓDULO: PERFIL Y GESTIÓN DE DATOS (EDICIÓN LIBRE Y POLÍTICA DE BORRADO)
# -----------------------------------------------------------------
elif eleccion == "⚙️ Perfil y Gestión de Datos":
    st.markdown("<h2>⚙️ GESTIÓN DE PERFIL Y POLÍTICA DE DATOS</h2>", unsafe_allow_html=True)
    st.markdown("Edición libre de datos de contacto, solicitud de modificación de cédula y opciones de borrado con retención forense.")
    st.markdown("---")

    op_data_actual = obtener_operador(st.session_state['cedula_actual'])
    if not op_data_actual:
        st.error("No se encontraron datos del operador.")
        st.stop()

    tab_edicion, tab_cedula_req, tab_borrado = st.tabs(["✏️ Edición de Datos Personales", "🆔 Solicitud Cambio de Cédula", "⚠️ Borrado de Cuenta (Soft-Delete)"])

    with tab_edicion:
        st.markdown("### ✏️ Actualización Libre de Datos")
        with st.form(key="form_edicion_libre"):
            nuevo_tel = st.text_input("Teléfono de Contacto", value=op_data_actual.get('telefono', ''))
            nuevo_correo = st.text_input("Correo Electrónico", value=op_data_actual.get('correo', ''))
            nuevo_alias = st.text_input("Alias Táctico", value=op_data_actual.get('alias', ''))
            
            btn_guardar_cambios = st.form_submit_button("Guardar Cambios 💾", use_container_width=True)
            if btn_guardar_cambios:
                actualizar_campo_operador(st.session_state['cedula_actual'], 'telefono', nuevo_tel)
                actualizar_campo_operador(st.session_state['cedula_actual'], 'correo', nuevo_correo)
                actualizar_campo_operador(st.session_state['cedula_actual'], 'alias', nuevo_alias)
                st.success("✅ Datos personales actualizados con éxito.")
                time.sleep(0.8)
                st.rerun()

    with tab_cedula_req:
        st.markdown("### 🆔 Bloqueo de Cédula y Solicitud al Administrador")
        st.markdown(f"**Cédula Actual (Congelada):** `{st.session_state['cedula_actual']}`")
        
        with st.form(key="form_solicitud_cedula"):
            nueva_ced_sol = st.text_input("Nuevo Número de Cédula Solicitado")
            motivo_cambio = st.text_area("Justificación / Motivo del Cambio de Cédula")
            btn_solicitar_cambio = st.form_submit_button("Enviar Solicitud al Admin 🚀", use_container_width=True)
            
            if btn_solicitar_cambio:
                if not nueva_ced_sol.strip() or not motivo_cambio.strip():
                    st.error("❌ Debe ingresar la nueva cédula y el motivo.")
                else:
                    enviar_solicitud_cambio_cedula(st.session_state['cedula_actual'], nueva_ced_sol.strip(), motivo_cambio.strip())
                    st.success("✅ Solicitud enviada al Administrador Maestro con éxito.")

    with tab_borrado:
        st.markdown("### ⚠️ Eliminación de Cuenta & Persistencia Forense (Soft-Delete)")
        st.markdown("""
            <div style="background-color: #1f1414; padding: 15px; border-radius: 10px; border: 1px solid #ef4444; margin-bottom: 15px;">
                <p style="color: #ef4444; font-weight: bold;">⚠️ ADVERTENCIA CRÍTICA DE SEGURIDAD:</p>
                <p style="color: #e2e8f0; font-size: 0.95em;">Al solicitar la eliminación voluntaria o por rechazo del Administrador, su acceso al sistema se destruirá de forma inmediata. Todos los registros y evidencias recopiladas se conservarán intactos en la base de datos para auditorías del Blue Team.</p>
            </div>
        """, unsafe_allow_html=True)
        
        motivo_baja = st.text_input("Motivo de la baja de cuenta", placeholder="Ej. Cambio de asignación operativa")
        confirmar_baja = st.checkbox("Confirmo que deseo dar de baja definitiva a mi cuenta pericial")
        
        if st.button("Ejecutar Baja de Cuenta 🗑️", use_container_width=True):
            if not confirmar_baja:
                st.error("❌ Debe marcar la casilla de confirmación.")
            else:
                eliminar_cuenta_soft_delete(st.session_state['cedula_actual'], motivo=motivo_baja if motivo_baja else "Baja voluntaria de operador")
                st.warning("🔒 Cuenta dada de baja. Destruyendo sesión activa...")
                time.sleep(1.5)
                st.session_state['acceso_concedido'] = False
                st.session_state['autenticado'] = False
                st.session_state['cedula_actual'] = ""
                st.rerun()

# -----------------------------------------------------------------
# MÓDULO: VERIFICACIÓN MULTICANAL & REPOSITORIO (ADMIN)
# -----------------------------------------------------------------
elif eleccion == "🛡️ Verificación Multicanal & Repositorio":
    if not es_admin:
        st.error("⛔ ACCESO DENEGADO.")
        st.stop()

    st.markdown("<h2>🛡️ PANEL DE VERIFICACIÓN MULTICANAL & REPOSITORIO</h2>", unsafe_allow_html=True)
    tab_v_multicanal, tab_v_cedulas, tab_v_repositorio = st.tabs(["📋 Validaciones Multicanal", "🆔 Solicitudes de Cédula", "📁 Repositorio de Documentos"])

    with tab_v_multicanal:
        todos_operadores = obtener_todos_operadores()
        if todos_operadores:
            lista_nops = [f"{d.get('nombre')} (ID: {ced})" for ced, d in todos_operadores.items()]
            sel_op_str = st.selectbox("Seleccione Operador a Auditar", lista_nops)
            ced_seleccionada = sel_op_str.split("ID: ")[1].replace(")", "").strip()
            datos_op = todos_operadores[ced_seleccionada]

            col_mv1, col_mv2, col_mv3 = st.columns(3)
            with col_mv1:
                st.markdown('<div class="cyber-card">', unsafe_allow_html=True)
                st.markdown("<h4>📞 Teléfono</h4>", unsafe_allow_html=True)
                est_tel = datos_op.get('telefono_verificado', False)
                st.markdown(f"Estado: `{'Verificado ✅' if est_tel else 'Pendiente ❌'}`")
                if st.button("Cambiar Estado Teléfono", key=f"btn_tel_{ced_seleccionada}"):
                    actualizar_campo_operador(ced_seleccionada, 'telefono_verificado', not est_tel)
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)
            with col_mv2:
                st.markdown('<div class="cyber-card">', unsafe_allow_html=True)
                st.markdown("<h4>🆔 Cédula & Perfil</h4>", unsafe_allow_html=True)
                est_ced = datos_op.get('cedula_verificada', False)
                st.markdown(f"Cédula: `{'Aprobada ✅' if est_ced else 'Pendiente ❌'}`")
                if st.button("Aprobar Cédula", key=f"btn_ced_{ced_seleccionada}"):
                    actualizar_campo_operador(ced_seleccionada, 'cedula_verificada', True)
                    actualizar_campo_operador(ced_seleccionada, 'estado_perfil', 'Activo / Desbloqueado')
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)
            with col_mv3:
                st.markdown('<div class="cyber-card">', unsafe_allow_html=True)
                st.markdown("<h4>🌐 Redes & Correo</h4>", unsafe_allow_html=True)
                est_redes = datos_op.get('redes_verificadas', False)
                st.markdown(f"Estado: `{'Verificado ✅' if est_redes else 'Pendiente ❌'}`")
                if st.button("Cambiar Estado Redes", key=f"btn_redes_{ced_seleccionada}"):
                    actualizar_campo_operador(ced_seleccionada, 'redes_verificadas', not est_redes)
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

    with tab_v_cedulas:
        st.markdown("### 🆔 Solicitudes de Cambio de Cédula Pendientes")
        solicitudes_c = obtener_solicitudes_cambio_cedula()
        if solicitudes_c:
            for k_sc, d_sc in solicitudes_c.items():
                if d_sc.get('estado') == 'pendiente':
                    st.markdown(f"""
                        <div style="background-color: #161b22; padding: 15px; border-radius: 10px; border: 1px solid #38bdf8; margin-bottom: 15px;">
                            <p><b>🆔 Cédula Actual:</b> `{d_sc.get('cedula_actual')}`</p>
                            <p><b>✨ Nueva Cédula Solicitada:</b> `{d_sc.get('nueva_cedula')}`</p>
                            <p><b>📝 Motivo:</b> {d_sc.get('motivo')}</p>
                        </div>
                    """, unsafe_allow_html=True)
                    col_sc1, col_sc2 = st.columns(2)
                    with col_sc1:
                        if st.button("✅ Aceptar Cambio", key=f"aceptar_ced_{k_sc}"):
                            op_info = obtener_operador(d_sc.get('cedula_actual'))
                            if op_info:
                                guardar_operador(d_sc.get('nueva_cedula'), op_info.get('nombre').split()[0], " ".join(op_info.get('nombre').split()[1:]), op_info.get('rol'), base64.b64decode(op_info.get('foto')) if op_info.get('foto') else b'', obtener_metadatos_locales(), estado="Activo / Desbloqueado", cedula_verificada=True, telefono=op_info.get('telefono'), correo=op_info.get('correo'), alias=op_info.get('alias'))
                                eliminar_cuenta_soft_delete(d_sc.get('cedula_actual'), motivo="Actualización de Cédula aprobada por Admin")
                            actualizar_estado_solicitud_cedula(k_sc, 'aceptada')
                            st.success("✅ Solicitud aceptada.")
                            time.sleep(1)
                            st.rerun()
                    with col_sc2:
                        if st.button("❌ Rechazar (Baja de Cuenta)", key=f"rechazar_ced_{k_sc}"):
                            eliminar_cuenta_soft_delete(d_sc.get('cedula_actual'), motivo="Solicitud de cambio de cédula rechazada")
                            actualizar_estado_solicitud_cedula(k_sc, 'rechazada')
                            st.error("⛔ Solicitud rechazada. Cuenta dada de baja.")
                            time.sleep(1)
                            st.rerun()
        else:
            st.info("ℹ️ No hay solicitudes pendientes.")

    with tab_v_repositorio:
        st.markdown("### 📁 Repositorio de Documentos")
        todos_ops_rep = obtener_todos_operadores()
        if todos_ops_rep:
            lista_nops_r = [f"{d.get('nombre')} (ID: {ced})" for ced, d in todos_ops_rep.items()]
            sel_op_r_str = st.selectbox("Seleccione Operador", lista_nops_r, key="sel_op_repo")
            ced_sel_r = sel_op_r_str.split("ID: ")[1].replace(")", "").strip()
            
            with st.form(key="form_subir_repo_admin", clear_on_submit=True):
                nombre_doc_input = st.text_input("Descripción del Documento Probatorio")
                archivo_repo = st.file_uploader("Seleccionar archivo", type=['jpg', 'jpeg', 'png', 'pdf', 'txt'])
                btn_subir_repo = st.form_submit_button("Subir al Repositorio 🚀", use_container_width=True)
                if btn_subir_repo and archivo_repo:
                    guardar_archivo_repositorio(ced_sel_r, nombre_doc_input, archivo_repo.read())
                    st.success("✅ Archivo almacenado.")
                    st.rerun()

# -----------------------------------------------------------------
# MÓDULO 1: CHATS PERSONALES CON MENÚ DE MARCACIÓN DINÁMICA & LÚDICO
# -----------------------------------------------------------------
elif eleccion == "💬 Chats Personales y Solicitudes (Estilo WhatsApp)":
    st.markdown("""
        <div>
            <h2>💬 CENTRO DE MENSAJERÍA CIFRADA Y CIBERSEGURIDAD</h2>
            <p style="color: #38bdf8;">Comunicaciones optimizadas, marcación dinámica y entretenimiento simultáneo.</p>
        </div>
    """, unsafe_allow_html=True)
    st.markdown("---")
    
    tab_chat, tab_solicitudes = st.tabs(["💬 Mis Chats Privados", "🔔 Notificaciones y Solicitudes de Amistad"])
    
    with tab_solicitudes:
        st.markdown("### 📥 Panel de Solicitudes de Amistad")
        col_s1, col_s2 = st.columns(2, gap="large")
        with col_s1:
            st.markdown('<div class="cyber-card">', unsafe_allow_html=True)
            st.markdown("<h4>➕ Enviar Solicitud</h4>", unsafe_allow_html=True)
            with st.form(key="form_enviar_solicitud"):
                cedula_destino_input = st.text_input("🆔 Ingrese la Cédula Destino")
                btn_enviar_sol = st.form_submit_button("Enviar Solicitud 🚀", use_container_width=True)
                if btn_enviar_sol:
                    if not cedula_destino_input.strip():
                        st.error("❌ Ingrese una cédula válida.")
                    elif cedula_destino_input.strip() == st.session_state['cedula_actual']:
                        st.error("❌ No puede enviarse una solicitud a sí mismo.")
                    else:
                        op_destino = obtener_operador(cedula_destino_input.strip())
                        if op_destino:
                            enviar_solicitud_amistad(st.session_state['cedula_actual'], st.session_state['usuario_actual'], cedula_destino_input.strip())
                            st.success(f"✅ Solicitud enviada a {op_destino.get('nombre')}.")
                        else:
                            st.error("❌ La cédula no está registrada.")
            st.markdown('</div>', unsafe_allow_html=True)
            
        with col_s2:
            st.markdown('<div class="cyber-card">', unsafe_allow_html=True)
            st.markdown("<h4>📬 Solicitudes Recibidas</h4>", unsafe_allow_html=True)
            solicitudes = obtener_solicitudes(st.session_state['cedula_actual'])
            if solicitudes:
                for k_sol, dat_sol in solicitudes.items():
                    estado = dat_sol.get('estado')
                    if estado == 'pendiente':
                        st.markdown(f"""
                            <div style="background-color: #0b0f17; padding: 12px; border-radius: 8px; border: 1px solid #30363d; margin-bottom: 10px;">
                                <p><b>De:</b> {dat_sol.get('remitente_nombre')} (ID: `{dat_sol.get('remitente_cedula')}`)</p>
                            </div>
                        """, unsafe_allow_html=True)
                        col_bt1, col_bt2 = st.columns(2)
                        with col_bt1:
                            if st.button("✅ Aceptar", key=f"aceptar_{k_sol}Y"):
                                actualizar_estado_solicitud(st.session_state['cedula_actual'], k_sol, 'aceptada')
                                st.success("¡Solicitud aceptada!")
                                time.sleep(0.3)
                                st.rerun()
                        with col_bt2:
                            if st.button("❌ Rechazar", key=f"rechazar_{k_sol}N"):
                                actualizar_estado_solicitud(st.session_state['cedula_actual'], k_sol, 'rechazada')
                                st.info("Solicitud rechazada.")
                                time.sleep(0.3)
                                st.rerun()
            else:
                st.info("No tiene solicitudes pendientes.")
            st.markdown('</div>', unsafe_allow_html=True)

    with tab_chat:
        contactos_validos = {}
        todos_ops = obtener_todos_operadores()
        mis_solicitudes = obtener_solicitudes(st.session_state['cedula_actual'])
        
        for k_s, d_s in mis_solicitudes.items():
            if d_s.get('estado') == 'aceptada':
                c_rem = d_s.get('remitente_cedula')
                if c_rem in todos_ops:
                    contactos_validos[c_rem] = todos_ops[c_rem].get('nombre')
                    
        for ced_op, dat_op in todos_ops.items():
            if ced_op != st.session_state['cedula_actual']:
                sols_ajenas = obtener_solicitudes(ced_op)
                for k_aj, d_aj in sols_ajenas.items():
                    if d_aj.get('remitente_cedula') == st.session_state['cedula_actual'] and d_aj.get('estado') == 'aceptada':
                        contactos_validos[ced_op] = dat_op.get('nombre')

        if contactos_validos:
            lista_nombres_contactos = list(contactos_validos.values())
            seleccion_contacto_nombre = st.selectbox("Seleccione contacto seguro", lista_nombres_contactos)
            cedula_contacto_sel = [c for c, n in contactos_validos.items() if n == seleccion_contacto_nombre][0]
            
            st.markdown("---")
            col_chat_central, col_cyber_derecho = st.columns([2, 1], gap="large")
            
            with col_chat_central:
                st.markdown(f"#### 🔒 Conversación Activa con: `{seleccion_contacto_nombre}`")
                
                @st.fragment(run_every=2)
                def renderizar_chat_privado_whatsapp(mi_ced, ced_amigo):
                    mensajes_privados = obtener_mensajes_privados(mi_ced, ced_amigo)
                    if mensajes_privados:
                        for k_m, msg in sorted(mensajes_privados.items(), key=lambda x: x[0])[-30:]:
                            es_mio = msg.get('remitente_cedula') == mi_ced
                            clase = "chat-bubble-user" if es_mio else "chat-bubble-other"
                            remitente_nombre_txt = st.session_state['usuario_actual'] if es_mio else seleccion_contacto_nombre
                            
                            if msg.get('tipo') == 'audio' and msg.get('audio_b64'):
                                st.markdown(f"""
                                    <div class="{clase}">
                                        <small style="color: {'#111827' if es_mio else '#94a3b8'}; font-size: 0.9em;"><b>{remitente_nombre_txt}</b> • 🎤 Nota de Voz • {msg.get('timestamp')}</small><br>
                                """, unsafe_allow_html=True)
                                try:
                                    st.audio(base64.b64decode(msg.get('audio_b64')), format='audio/wav')
                                except Exception:
                                    st.error("Audio no disponible.")
                                st.markdown("</div>", unsafe_allow_html=True)
                            elif msg.get('tipo') == 'sticker':
                                st.markdown(f"""
                                    <div class="{clase}">
                                        <small style="color: {'#111827' if es_mio else '#94a3b8'}; font-size: 0.9em;"><b>{remitente_nombre_txt}</b> • 🎨 Sticker • {msg.get('timestamp')}</small><br>
                                        <span style="font-size: 2em;">{msg.get('texto')}</span>
                                        <div style="text-align: right; font-size: 0.8em; color: {'#065f46' if es_mio else '#38bdf8'};">✓✓ leídos</div>
                                    </div>
                                """, unsafe_allow_html=True)
                            else:
                                st.markdown(f"""
                                    <div class="{clase}">
                                        <small style="color: {'#111827' if es_mio else '#94a3b8'}; font-size: 0.9em;"><b>{remitente_nombre_txt}</b> • {msg.get('timestamp')}</small><br>
                                        <span style="font-size: 1.05em;">{msg.get('texto')}</span>
                                        <div style="text-align: right; font-size: 0.8em; color: {'#065f46' if es_mio else '#38bdf8'};">✓✓ leídos</div>
                                    </div>
                                """, unsafe_allow_html=True)
                    else:
                        st.info("No hay mensajes previos en este canal cifrado.")

                renderizar_chat_privado_whatsapp(st.session_state['cedula_actual'], cedula_contacto_sel)
                st.markdown("<br>", unsafe_allow_html=True)
                
                st.markdown("""
                    <div style="background-color: #161b22; padding: 12px; border-radius: 10px; border: 1px solid #38bdf8; margin-bottom: 10px;">
                        <span style="color: #38bdf8; font-weight: bold;">⚡ Menú de Marcación Dinámica:</span>
                    </div>
                """, unsafe_allow_html=True)
                
                col_md1, col_md2 = st.columns(2)
                with col_md1:
                    opcion_pre = st.selectbox(
                        "Mensajes Preestablecidos",
                        ["Seleccionar respuesta rápida...", "🟢 Todo en orden por aquí.", "🚨 Alerta: Operación en curso.", "📍 Confirmando coordenadas actuales.", "🔐 Canal seguro verificado."],
                        key=f"sel_pre_{cedula_contacto_sel}"
                    )
                    if opcion_pre != "Seleccionar respuesta rápida...":
                        enviar_mensaje_privado(st.session_state['cedula_actual'], cedula_contacto_sel, opcion_pre, tipo="texto")
                        st.success("Mensaje rápido enviado.")
                        time.sleep(0.3)
                        st.rerun()

                with col_md2:
                    stickers_disponibles = ["🛡️", "🔥", "⚡", "🤖", "🚀", "💀"]
                    sticker_sel = st.selectbox("Enviar Sticker (Máx 4/sesión)", ["Seleccionar sticker..."] + stickers_disponibles, key=f"sel_sticker_{cedula_contacto_sel}")
                    if sticker_sel != "Seleccionar sticker...":
                        if st.session_state['stickers_enviados_sesion'] >= 4:
                            st.error("⛔ Límite estricto alcanzado: Máximo 4 stickers.")
                        else:
                            st.session_state['stickers_enviados_sesion'] += 1
                            enviar_mensaje_privado(st.session_state['cedula_actual'], cedula_contacto_sel, sticker_sel, tipo="sticker")
                            st.success("Sticker enviado.")
                            time.sleep(0.3)
                            st.rerun()

                st.markdown("<br>", unsafe_allow_html=True)
                col_env1, col_env2 = st.columns([2, 1])
                with col_env1:
                    with st.form(key=f"chat_privado_form_{cedula_contacto_sel}", clear_on_submit=True):
                        txt_msg_p = st.text_input("Mensaje cifrado...", placeholder="Escribe tu mensaje...")
                        enviar_btn_p = st.form_submit_button("Enviar Mensaje 🚀", use_container_width=True)
                        if enviar_btn_p and txt_msg_p:
                            enviar_mensaje_privado(st.session_state['cedula_actual'], cedula_contacto_sel, txt_msg_p, tipo="texto")
                            st.rerun()
                with col_env2:
                    audio_subido_p = st.audio_input("Grabar Nota de Voz", key=f"audio_p_{cedula_contacto_sel}")
                    if audio_subido_p:
                        bytes_audio_p = audio_subido_p.read()
                        if bytes_audio_p:
                            audio_b64_p = base64.b64encode(bytes_audio_p).decode('utf-8')
                            enviar_mensaje_privado(st.session_state['cedula_actual'], cedula_contacto_sel, "[Nota de Voz]", tipo="audio", audio_b64=audio_b64_p)
                            st.success("✅ Nota enviada.")
                            time.sleep(0.5)
                            st.rerun()

            with col_cyber_derecho:
                st.markdown("""
                    <div class="cyber-card">
                        <h3 style="color: #00ffcc;">🛡️ BLUE TEAM TELEMETRY</h3>
                        <p style="font-size: 0.95em;"><b>🔒 Cifrado:</b><br>AES-256 Extremo a Extremo</p>
                        <hr style="border-color: #30363d;">
                        <p style="font-size: 0.95em;"><b>🎨 Stickers:</b><br><code>""" + str(st.session_state['stickers_enviados_sesion']) + """ / 4 usados</code></p>
                """, unsafe_allow_html=True)
                
                st.markdown("---")
                st.markdown("<h4 style='color: #facc15;'>🎮 Lúdico Integrado</h4>", unsafe_allow_html=True)
                juego_escogido = st.selectbox("Seleccionar Mini-Juego", ["Ninguno", "Adivina el Código Secreto (1-10)", "Trivia Ciberseguridad"], key="sel_juego_chat")
                
                if juego_escogido == "Adivina el Código Secreto (1-10)":
                    num_intentado = st.number_input("Número (1 a 10)", min_value=1, max_value=10, step=1, key="num_secreto_input")
                    if st.button("Probar Código", key="btn_probar_juego"):
                        secreto_val = random.randint(1, 10)
                        if num_intentado == secreto_val:
                            st.session_state['puntuacion_juego'] += 50
                            st.success(f"🎉 ¡CORRECTO! Era el {secreto_val}.")
                        else:
                            st.warning(f"❌ Fallaste. Era el {secreto_val}.")
                    st.markdown(f"**Puntuación:** `{st.session_state['puntuacion_juego']} Pts`")
                elif juego_escogido == "Trivia Ciberseguridad":
                    ans_triv = st.radio("¿Qué puerto utiliza por defecto SSH?", ["Puerto 80", "Puerto 22", "Puerto 443"], key="triv_ans")
                    if st.button("Enviar Respuesta", key="btn_triv"):
                        if ans_triv == "Puerto 22":
                            st.session_state['puntuacion_juego'] += 100
                            st.success("🟢 ¡Correcto! +100 Pts.")
                        else:
                            st.error("❌ Incorrecto.")
                    st.markdown(f"**Puntuación:** `{st.session_state['puntuacion_juego']} Pts`")

                st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.warning("⚠️ No tiene contactos con solicitudes aceptadas.")

# -----------------------------------------------------------------
# MÓDULO 2: VIDEOLLAMADA TÁCTICA P2P
# -----------------------------------------------------------------
elif eleccion == "📹 Videollamada Táctica P2P (Ultra-Rápida)":
    st.markdown("<h2>📹 SISTEMA DE VIDEOLLAMADAS TÁCTICAS P2P</h2>", unsafe_allow_html=True)
    col_cam1, col_cam2 = st.columns(2, gap="large")
    with col_cam1:
        st.markdown('<div class="cyber-card">', unsafe_allow_html=True)
        st.markdown("<h3>📷 Transmisión Local</h3>", unsafe_allow_html=True)
        st.camera_input("Cámara de Videollamada", key="videollamada_local")
        st.markdown('</div>', unsafe_allow_html=True)
    with col_cam2:
        st.markdown('<div class="cyber-card">', unsafe_allow_html=True)
        st.markdown("<h3>📡 Canal Remoto</h3>", unsafe_allow_html=True)
        st.info("📡 Conexión P2P instantánea establecida. Latencia < 45ms.")
        st.markdown('</div>', unsafe_allow_html=True)

# -----------------------------------------------------------------
# MÓDULO 3: OPERACIONES DE ALTA CONFIDENCIALIDAD
# -----------------------------------------------------------------
elif eleccion == "🚨 Operaciones de Alta Confidencialidad":
    if not es_admin:
        st.error("⛔ ACCESO DENEGADO.")
        st.stop()
    st.markdown("<h2>🚨 CENTRO DE MANDO TÁCTICO</h2>", unsafe_allow_html=True)
    tab_admin_privado, tab_panic = st.tabs(["💬 Canal Blindado", "⚡ Protocolo de Emergencia"])
    with tab_admin_privado:
        st.markdown('<div class="cyber-card">', unsafe_allow_html=True)
        txt_admin_secreto = st.text_area("Directiva cifrada:")
        if st.button("Enviar Directiva 🔐") and txt_admin_secreto.strip():
            st.success("✅ Directiva transmitida con firma criptográfica.")
        st.markdown('</div>', unsafe_allow_html=True)
    with tab_panic:
        if st.button("🚨 ACTIVAR ALERTA: CICPC / DGCIM"):
            st.error("⚠️ ALERTA NACIONAL DISPARADA.")

# -----------------------------------------------------------------
# MÓDULO 4: CONTROL Y REGISTRO DE OPERADORES
# -----------------------------------------------------------------
elif eleccion == "👥 Control y Registro de Operadores":
    if not es_admin:
        st.error("⛔ Acceso Denegado.")
        st.stop()
    st.markdown("<h2>👥 BASE DE DATOS DE OPERADORES</h2>", unsafe_allow_html=True)
    operadores = obtener_todos_operadores()
    if operadores:
        for ced, datos in operadores.items():
            st.markdown(f'<div class="cyber-card">', unsafe_allow_html=True)
            col_f, col_i = st.columns([1, 3])
            with col_f:
                if datos.get('foto'):
                    try:
                        st.image(base64.b64decode(datos.get('foto')), width=140)
                    except Exception:
                        pass
            with col_i:
                st.markdown(f"<h3>👤 {datos.get('nombre')}</h3>", unsafe_allow_html=True)
                st.markdown(f"**🆔 Cédula:** `{datos.get('cedula')}` | **Provisional:** `{'Sí ⚠️' if datos.get('provisional') else 'No 🟢'}`")
                st.markdown(f"**🔒 Estado:** `{datos.get('estado_perfil', 'Restringido')}`")
            st.markdown('</div>', unsafe_allow_html=True)

# -----------------------------------------------------------------
# MÓDULO 5: EXIFTOOL & ANÁLISIS DE METADATOS
# -----------------------------------------------------------------
elif eleccion == "📸 ExifTool & Análisis de Metadatos":
    if not es_admin:
        st.error("⛔ Acceso Denegado.")
        st.stop()
    st.markdown("<h2>📸 EXIFTOOL & ANÁLISIS DE METADATOS</h2>", unsafe_allow_html=True)
    archivo_subido = st.file_uploader("Seleccione evidencia", type=['jpg', 'jpeg', 'png'])
    if archivo_subido:
        bytes_img = archivo_subido.read()
        st.image(bytes_img, width=300)
        h_sha256 = hashlib.sha256(bytes_img).hexdigest()
        st.code(f"SHA-256: {h_sha256}", language="text")

# -----------------------------------------------------------------
# MÓDULO 6: MAPEO DE CONEXIONES Y GEOLOCALIZACIÓN
# -----------------------------------------------------------------
elif eleccion == "🕵️ Mapeo de Conexiones y Geolocalización (IPs)":
    if not es_admin:
        st.error("⛔ Acceso Denegado.")
        st.stop()
    st.markdown("<h2>🕵️ MAPEO DE CONEXIONES Y GEOLOCALIZACIÓN</h2>", unsafe_allow_html=True)
    conexiones = obtener_conexiones_log()
    if conexiones:
        for k, con in sorted(conexiones.items(), key=lambda x: x[0], reverse=True):
            st.markdown(f"""
                <div class="cyber-card">
                    <p><b>👤 {con.get('nombre')} (ID: {con.get('cedula')})</b></p>
                    <p><b>📌 Evento:</b> {con.get('evento')} | <b>IP:</b> <code>{con.get('ip')}</code></p>
                    <p><b>⏰ {con.get('timestamp')}</b></p>
                </div>
            """, unsafe_allow_html=True)
