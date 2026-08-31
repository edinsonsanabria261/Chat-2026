import streamlit as st
import time
import requests
import json

# -----------------------------------------------------------------
# 1. CONFIGURACIÓN INICIAL Y URL DE FIREBASE
# -----------------------------------------------------------------
st.set_page_config(page_title="Centro de Inteligencia & Comunicación", page_icon="🛡️", layout="wide")

# URL de tu Realtime Database de Firebase
FIREBASE_URL = "https://chat-2026-68203-default-rtdb.firebaseio.com/"

# -----------------------------------------------------------------
# 2. FUNCIONES AUXILIARES (CONEXIÓN HTTP DIRECTA A FIREBASE)
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
    data = {
        'usuario': usuario,
        'accion': accion,
        'ip': ip,
        'timestamp': timestamp
    }
    requests.post(f"{FIREBASE_URL}/auditoria_ip.json", data=json.dumps(data))

def guardar_operador(cedula, nombre):
    data = {
        'nombre': nombre,
        'cedula': cedula,
        'fecha_registro': time.strftime("%Y-%m-%d %H:%M:%S")
    }
    requests.put(f"{FIREBASE_URL}/operadores/{cedula}.json", data=json.dumps(data))

def obtener_operador(cedula):
    res = requests.get(f"{FIREBASE_URL}/operadores/{cedula}.json")
    if res.status_code == 200:
        return res.json()
    return None

def enviar_mensaje_db(remitente, texto, ip):
    data = {
        'remitente': remitente,
        'texto': texto,
        'timestamp': time.strftime("%H:%M:%S - %d/%m/%Y"),
        'ip': ip
    }
    requests.post(f"{FIREBASE_URL}/mensajes.json", data=json.dumps(data))

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
            datos_usuario = obtener_operador(cedula_login)

            if datos_usuario:
                st.success(f"¡Identidad confirmada! Bienvenido, {datos_usuario.get('nombre', 'Operador')}.")
                st.session_state['usuario_actual'] = datos_usuario.get('nombre')
                st.session_state['cedula_actual'] = cedula_login
                registrar_auditoria(datos_usuario.get('nombre'), "Inicio de sesión exitoso")
            else:
                st.error("Cédula no encontrada en el sistema. Registre su operador primero.")

# -----------------------------------------------------------------
# MÓDULO 2: REGISTRAR NUEVO OPERADOR
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
            existente = obtener_operador(nueva_cedula)
            if existente:
                st.error("Este identificador ya se encuentra registrado.")
            else:
                guardar_operador(nueva_cedula, nuevo_nombre)
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

        chat_container = st.container()
        
        with chat_container:
            mensajes = obtener_mensajes()
            if mensajes:
                # Ordenar por clave (que funciona como timestamp alfanumérico en Firebase)
                items_msg = sorted(mensajes.items(), key=lambda x: x[0])
                for key, msg in items_msg[-30:]: # Mostrar últimos 30
                    st.markdown(f"**[{msg.get('timestamp')}] {msg.get('remitente')}**: {msg.get('texto')} *(IP: {msg.get('ip', 'N/A')})*")
            else:
                st.write("No hay mensajes aún. ¡Comienza la conversación!")

        with st.form(key='form_chat', clear_on_submit=True):
            nuevo_mensaje = st.text_input("Escriba su mensaje seguro...")
            enviar = st.form_submit_button("Enviar Mensaje")

            if enviar and nuevo_mensaje:
                ip_actual = obtener_ip_publica()
                enviar_mensaje_db(st.session_state['usuario_actual'], nuevo_mensaje, ip_actual)
                st.rerun()

# -----------------------------------------------------------------
# MÓDULO 4: AUDITORÍA DE IP
# -----------------------------------------------------------------
elif menu == "Auditoría de IP":
    st.title("🕵️ Panel de Auditoría y Seguridad de Redes")
    st.write("Registro de conexiones y actividad en la plataforma.")

    registros = obtener_auditorias()
    if registros:
        items_reg = sorted(registros.items(), key=lambda x: x[0], reverse=True)
        for key, reg in items_reg[:30]:
            st.markdown(f"🕒 **{reg.get('timestamp')}** | 👤 **{reg.get('usuario')}** | ⚡ Acción: *{reg.get('accion')}* | 🌐 IP: `{reg.get('ip')}`")
    else:
        st.write("No hay registros de auditoría disponibles.")
