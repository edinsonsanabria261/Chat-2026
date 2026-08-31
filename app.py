import streamlit as st
import time
import requests
import json
from PIL import Image
import io
import base64

# -----------------------------------------------------------------
# 1. CONFIGURACIÓN VISUAL Y MODO OSCURO TÁCTICO
# -----------------------------------------------------------------
st.set_page_config(page_title="Centro de Inteligencia Operativa", page_icon="🛡️", layout="wide")

st.markdown("""
    <style>
    .stApp {
        background-color: #0b0f19;
        color: #e2e8f0;
    }
    .chat-bubble-user {
        background: #1e293b;
        color: #f8fafc;
        padding: 12px 16px;
        border-radius: 12px;
        margin-bottom: 10px;
        border-left: 4px solid #3b82f6;
    }
    .chat-bubble-other {
        background: #0f172a;
        color: #cbd5e1;
        padding: 12px 16px;
        border-radius: 12px;
        margin-bottom: 10px;
        border-left: 4px solid #10b981;
    }
    .metric-card {
        background-color: #1e293b;
        padding: 15px;
        border-radius: 8px;
        border: 1px solid #334155;
    }
    </style>
""", unsafe_allow_html=True)

FIREBASE_URL = "https://chat-2026-68203-default-rtdb.firebaseio.com/"

# -----------------------------------------------------------------
# 2. FUNCIONES DE INTELIGENCIA Y FORENSE (REDS / IP / METADATOS)
# -----------------------------------------------------------------
def obtener_metadatos_red():
    try:
        response = requests.get('https://ipapi.co/json/', timeout=3)
        if response.status_code == 200:
            data = response.json()
            return {
                'ip': data.get('ip', 'Desconocida'),
                'ciudad': data.get('city', 'Desconocida'),
                'pais': data.get('country_name', 'Desconocida'),
                'org': data.get('org', 'Red Desconocida')
            }
    except:
        pass
    try:
        ip_alt = requests.get('https://api.ipify.org?format=json', timeout=3).json().get('ip', 'Desconocida')
        return {'ip': ip_alt, 'ciudad': 'Localizada por IP', 'pais': 'N/A', 'org': 'N/A'}
    except:
        return {'ip': 'Local/Desconocida', 'ciudad': 'N/A', 'pais': 'N/A', 'org': 'N/A'}

def registrar_auditoria(usuario, accion, meta):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    payload = {
        'usuario': usuario,
        'accion': accion,
        'ip': meta.get('ip'),
        'ubicacion': f"{meta.get('ciudad')}, {meta.get('pais')}",
        'proveedor': meta.get('org'),
        'timestamp': timestamp
    }
    requests.post(f"{FIREBASE_URL}/auditoria_ip.json", data=json.dumps(payload))

def guardar_operador(cedula, nombre, rol, foto_b64):
    payload = {
        'nombre': nombre,
        'cedula': cedula,
        'rol': rol,
        'foto': foto_b64,
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

def enviar_mensaje_db(remitente, texto, meta):
    payload = {
        'remitente': remitente,
        'texto': texto,
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
# 3. GESTIÓN DE SESIÓN Y CONTROL DE ACCESO
# -----------------------------------------------------------------
if 'autenticado' not in st.session_state:
    st.session_state['autenticado'] = False
    st.session_state['usuario_actual'] = ""
    st.session_state['rol_actual'] = ""
    st.session_state['cedula_actual'] = ""

st.sidebar.title("🛡️ Centro Táctico 2026")

if not st.session_state['autenticado']:
    modo_auth = st.sidebar.radio("Seleccione Operación", ["Iniciar Sesión (Biometría)", "Registrar Operador / Familiar"])
    
    if modo_auth == "Iniciar Sesión (Biometría)":
        st.title("🔐 Validación de Identidad y Acceso")
        st.write("Ingrese sus credenciales y escanee su rostro para descifrar el acceso al sistema.")
        
        cedula_ingreso = st.text_input("Cédula / Identificador Único")
        foto_camara = st.camera_input("Verificación Biométrica Facial")
        
        if st.button("Autorizar Ingreso", type="primary"):
            if not cedula_ingreso or not foto_camara:
                st.warning("Debe ingresar su cédula y capturar la biometría facial.")
            else:
                user_data = obtener_operador(cedula_ingreso)
                if user_data:
                    meta = obtener_metadatos_red()
                    st.session_state['autenticado'] = True
                    st.session_state['usuario_actual'] = user_data.get('nombre')
                    st.session_state['rol_actual'] = user_data.get('rol', 'Operador')
                    st.session_state['cedula_actual'] = cedula_ingreso
                    registrar_auditoria(user_data.get('nombre'), "Acceso autorizado con éxito", meta)
                    st.success(f"¡Bienvenido, {user_data.get('nombre')}! Acceso concedido.")
                    st.rerun()
                else:
                    st.error("Identificador no registrado en la base de datos central.")

    elif modo_auth == "Registrar Operador / Familiar":
        st.title("📝 Alta de Nuevo Operador o Familiar")
        st.write("Registre los datos tácticos y biométricos para otorgar permisos.")
        
        reg_nombre = st.text_input("Nombre Completo")
        reg_cedula = st.text_input("Cédula o ID")
        reg_rol = st.selectbox("Rol Asignado", ["Familiar / Operador", "Administrador Principal"])
        reg_foto = st.camera_input("Captura Facial de Registro")
        
        if st.button("Registrar en Base de Datos", type="primary"):
            if not reg_nombre or not reg_cedula or not reg_foto:
                st.warning("Complete todos los campos requeridos y capture su rostro.")
            else:
                # Convertir imagen a Base64 para guardarla de forma segura
                bytes_img = reg_foto.getvalue()
                foto_b64 = base64.b64encode(bytes_img).decode('utf-8')
                
                guardar_operador(reg_cedula, reg_nombre, reg_rol, foto_b64)
                meta = obtener_metadatos_red()
                registrar_auditoria(reg_nombre, f"Registro nuevo rol: {reg_rol}", meta)
                st.success(f"¡Operador {reg_nombre} registrado correctamente en el sistema!")

else:
    # -----------------------------------------------------------------
    # 4. NAVEGACIÓN INTERNA SEGÚN ROL DE USUARIO
    # -----------------------------------------------------------------
    st.sidebar.markdown(f"👤 **Operador:** `{st.session_state['usuario_actual']}`")
    st.sidebar.markdown(f"🔑 **Rol:** `{st.session_state['rol_actual']}`")
    
    opciones_menu = ["Canal de Chat Seguro"]
    
    # Si es Administrador, tiene acceso total al panel de inteligencia forense
    if st.session_state['rol_actual'] == "Administrador Principal":
        opciones_menu.extend(["Panel de Control (Admin)", "Auditoría de Redes & IPs"])
    
    opciones_menu.append("Cerrar Sesión")
    seleccion = st.sidebar.selectbox("Navegación Táctica", opciones_menu)
    
    if seleccion == "Cerrar Sesión":
        st.session_state['autenticado'] = False
        st.rerun()

    # MÓDULO: CHAT SEGURO ESTILO WHATSAPP OSCURO
    elif seleccion == "Canal de Chat Seguro":
        st.title("💬 Canal de Comunicaciones Cifradas")
        st.markdown("---")
        
        # Contenedor estilo chat moderno
        chat_box = st.container()
        
        with chat_box:
            mensajes = obtener_mensajes()
            if mensajes:
                items_msg = sorted(mensajes.items(), key=lambda x: x[0])
                for key, msg in items_msg[-40:]:
                    es_mio = msg.get('remitente') == st.session_state['usuario_actual']
                    clase_css = "chat-bubble-user" if es_mio else "chat-bubble-other"
                    
                    st.markdown(f"""
                        <div class="{clase_css}">
                            <small style="color: #94a3b8;"><b>{msg.get('remitente')}</b> • {msg.get('timestamp')} • 🌐 IP: {msg.get('ip')} ({msg.get('ubicacion')})</small><br>
                            <span style="font-size: 1.1em;">{msg.get('texto')}</span>
                        </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("Canal seguro abierto. Comience la transmisión de mensajes.")

        # Formulario de envío fijo abajo
        with st.form(key='chat_form_moderno', clear_on_submit=True):
            col_txt, col_btn = st.columns([5, 1])
            with col_txt:
                texto_msj = st.text_input("Mensaje cifrado...", label_visibility="collapsed")
            with col_btn:
                enviar_btn = st.form_submit_button("Enviar 🚀", use_container_width=True)
                
            if enviar_btn and texto_msj:
                meta_actual = obtener_metadatos_red()
                enviar_mensaje_db(st.session_state['usuario_actual'], texto_msj, meta_actual)
                st.rerun()

    # MÓDULO EXCLUSIVO ADMIN: PANEL DE CONTROL Y GESTIÓN
    elif seleccion == "Panel de Control (Admin)":
        st.title("🛡️ Panel de Control y Auditoría Administrativa")
        st.write("Gestión centralizada de operadores, rostros guardados y metadatos del sistema.")
        
        operadores = obtener_todos_operadores()
        st.subheader(f"👥 Operadores y Familiares Registrados ({len(operadores)})")
        
        for ced, datos in operadores.items():
            with st.expander(f"ID: {ced} - {datos.get('nombre')} ({datos.get('rol')})"):
                col1, col2 = st.columns([1, 2])
                with col1:
                    if 'foto' in datos and datos['foto']:
                        try:
                            img_bytes = base64.b64decode(datos['foto'])
                            st.image(Image.open(io.BytesIO(img_bytes)), width=150, caption="Biometría Facial")
                        except:
                            st.write("Imagen no disponible")
                with col2:
                    st.markdown(f"**Nombre Completo:** {datos.get('nombre')}")
                    st.markdown(f"**Cédula / ID:** {datos.get('cedula')}")
                    st.markdown(f"**Rol en Sistema:** {datos.get('rol')}")
                    st.markdown(f"**Fecha de Alta:** {datos.get('fecha_registro')}")

    # MÓDULO EXCLUSIVO ADMIN: AUDITORÍA DE REDES E IPS
    elif seleccion == "Auditoría de Redes & IPs":
        st.title("🕵️ Inteligencia de Conexiones y Geolocalización")
        st.write("Registro detallado de direcciones IP, ubicaciones y dispositivos conectados.")
        
        registros = obtener_auditorias()
        if registros:
            items_reg = sorted(registros.items(), key=lambda x: x[0], reverse=True)
            for key, reg in items_reg[:50]:
                st.markdown(f"""
                    <div class="metric-card">
                        🕒 <b>{reg.get('timestamp')}</b> | 👤 <b>{reg.get('usuario')}</b><br>
                        ⚡ Acción: <i>{reg.get('accion')}</i><br>
                        🌐 IP Pública: <code>{reg.get('ip')}</code> | 📍 Ubicación: <b>{reg.get('ubicacion')}</b>
                    </div>
                    <br>
                """, unsafe_allow_html=True)
        else:
            st.write("No hay registros de auditoría almacenados.")
    
