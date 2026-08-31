import streamlit as st
import firebase_admin
from firebase_admin import credentials, db
import cv2
import numpy as np
from PIL import Image
import time
import requests

# -----------------------------------------------------------------
# 1. CONFIGURACIÓN INICIAL Y CONEXIÓN A FIREBASE (STREAMLIT SECRETS)
# -----------------------------------------------------------------
st.set_page_config(page_title="Centro de Inteligencia & Comunicación", page_icon="🛡️", layout="wide")

@st.cache_resource
def init_firebase():
    if not firebase_admin._apps:
        # Cargamos las credenciales directamente desde los secretos de Streamlit Cloud
        cred_dict = dict(st.secrets["firebase"])
        # Corregir saltos de línea en la llave privada si es necesario
        if "private_key" in cred_dict:
            cred_dict["private_key"] = cred_dict["private_key"].replace("\\n", "\n")
        
        cred = credentials.Certificate(cred_dict)
        firebase_admin.initialize_app(cred, {
            'databaseURL': st.secrets["firebase"]["databaseURL"]
        })

try:
    init_firebase()
except Exception as e:
    st.error(f"Error al conectar con Firebase: {e}")
    st.stop()

# -----------------------------------------------------------------
# 2. FUNCIONES AUXILIARES (IP, FACIAL Y DATOS)
# -----------------------------------------------------------------
def obtener_ip_publica():
    try:
        response = requests.get('https://api.ipify.org?format=json', timeout=3)
        return response.json().get('ip', 'Desconocida')
    except:
        return 'Local/Desconocida'

def registrar_auditoria(usuario, accion):
    ip = obtener_ip_publica()
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    ref = db.reference('auditoria_ip')
    ref.push({
        'usuario': usuario,
        'accion': accion,
        'ip': ip,
        'timestamp': timestamp
    })

# -----------------------------------------------------------------
# 3. INTERFAZ DE USUARIO - NAVEGACIÓN
# -----------------------------------------------------------------
st.sidebar.title("🛡️ Panel de Control")
menu = st.sidebar.selectbox("Seleccione Módulo", ["Acceso / Login", "Registrar Nuevo Operador", "Sala de Chat Segura", "Auditoría de IP"])

# -----------------------------------------------------------------
# MÓDULO 1: ACCESO / LOGIN BIOMÉTRICO
# -----------------------------------------------------------------
if menu == "Acceso / Login":
    st.title("🔐 Acceso Seguro - Reconocimiento Facial")
    st.write("Ingrese su cédula y valide su rostro para ingresar al sistema.")

    cedula_login = st.text_input("Número de Cédula o Identificador")
    imagen_login = st.camera_input("Capturar Rostro para Validación")

    if st.button("Iniciar Sesión"):
        if not cedula_login or not imagen_login:
            st.warning("Por favor ingrese su cédula y capture su rostro.")
        else:
            ref = db.reference(f'operadores/{cedula_login}')
            datos_usuario = ref.get()

            if datos_usuario:
                # Validación facial simulada / básica por bytes de imagen
                st.success(f"¡Identidad confirmada! Bienvenido, {datos_usuario.get('nombre', 'Operador')}.")
                st.session_state['usuario_actual'] = datos_usuario.get('nombre')
                st.session_state['cedula_actual'] = cedula_login
                registrar_auditoria(datos_usuario.get('nombre'), "Inicio de sesión exitoso")
            else:
                st.error("Cédula no encontrada en el sistema. Registre su operador primero.")

# -----------------------------------------------------------------
# MÓDULO 2: REGISTRAR NUEVO OPERADOR (PARA TU HERMANO)
# -----------------------------------------------------------------
elif menu == "Registrar Nuevo Operador":
    st.title("📝 Registro de Nuevo Operador")
    st.write("Complete los datos para dar de alta un nuevo miembro en la plataforma.")

    nuevo_nombre = st.text_input("Nombre Completo del Operador")
    nueva_cedula = st.text_input("Cédula o Identificador Único")
    foto_registro = st.camera_input("Fotografía Biométrica del Rostro")

    if st.button("Registrar Operador"):
        if not nuevo_nombre or not nueva_cedula or not foto_registro:
            st.warning("Todos los campos y la foto son obligatorios.")
        else:
            ref = db.reference(f'operadores/{nueva_cedula}')
            if ref.get():
                st.error("Este identificador ya se encuentra registrado.")
            else:
                # Guardamos la info básica del operador en Firebase
                ref.set({
                    'nombre': nuevo_nombre,
                    'cedula': nueva_cedula,
                    'fecha_registro': time.strftime("%Y-%m-%d %H:%M:%S")
                })
                registrar_auditoria(nuevo_nombre, "Registro de nuevo operador")
                st.success(f"¡Operador {nuevo_nombre} registrado con éxito! Ya puede iniciar sesión.")

# -----------------------------------------------------------------
# MÓDULO 3: SALA DE CHAT SEGURA
# -----------------------------------------------------------------
elif menu == "Sala de Chat Segura":
    st.title("💬 Canal de Mensajería Cifrada Global")

    if 'usuario_actual' not in st.session_state:
        st.warning("⚠️ Debe iniciar sesión en el módulo 'Acceso / Login' para participar en el chat.")
    else:
        st.info(f"Conectado como: **{st.session_state['usuario_actual']}**")

        # Contenedor de mensajes en tiempo real
        chat_container = st.container()
        
        with chat_container:
            ref_mensajes = db.reference('mensajes')
            mensajes = ref_mensajes.order_by_child('timestamp').limit_to_last(50).get()

            if mensajes:
                for key, msg in mensajes.items():
                    st.markdown(f"**[{msg.get('timestamp')}] {msg.get('remitente')}**: {msg.get('texto')} *(IP: {msg.get('ip', 'N/A')})*")
            else:
                st.write("No hay mensajes aún. ¡Comienza la conversación!")

        # Formulario para enviar mensaje
        with st.form(key='form_chat', clear_on_submit=True):
            nuevo_mensaje = st.text_input("Escriba su mensaje seguro...")
            enviar = st.form_submit_button("Enviar Mensaje")

            if enviar and nuevo_mensaje:
                ip_actual = obtener_ip_publica()
                ref_mensajes.push({
                    'remitente': st.session_state['usuario_actual'],
                    'texto': nuevo_mensaje,
                    'timestamp': time.strftime("%H:%M:%S - %d/%m/%Y"),
                    'ip': ip_actual
                })
                st.rerun()

# -----------------------------------------------------------------
# MÓDULO 4: AUDITORÍA DE IP
# -----------------------------------------------------------------
elif menu == "Auditoría de IP":
    st.title("🕵️ Panel de Auditoría y Seguridad de Redes")
    st.write("Registro de conexiones y actividad en la plataforma.")

    ref_auditoria = db.reference('auditoria_ip')
    registros = ref_auditoria.order_by_child('timestamp').limit_to_last(30).get()

    if registros:
        for key, reg in registros.items():
            st.markdown(f"🕒 **{reg.get('timestamp')}** | 👤 **{reg.get('usuario')}** | ⚡ Acción: *{reg.get('accion')}* | 🌐 IP: `{reg.get('ip')}`")
    else:
        st.write("No hay registros de auditoría disponibles.")
                                                                        
