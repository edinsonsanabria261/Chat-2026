import streamlit as st
from datetime import datetime

# Configuración inicial de la página
st.set_page_config(page_title="Centro Táctico Pericial", layout="wide")

st.sidebar.title("⚡ Centro Pericial")
st.sidebar.markdown(f"**Creador:** Edinson Carlos Marin Sanabria")
st.sidebar.markdown("---")

# Menú de navegación lateral
menu = st.sidebar.radio("Protocolo de Ingreso", ["Validación Biométrica (Peritaje)", "Registrar Nuevo Operador"])

# Base de datos simulada en sesión para pruebas inmediatas
if "usuarios" not in st.session_state:
    st.session_state.usuarios = {
        "2844102044": {
            "nombre": "Edinson Carlos Marin Sanabria",
            "rol": "Administrador General",
            "permisos": "Total"
        }
    }

if "logs_conexiones" not in st.session_state:
    st.session_state.logs_conexiones = []

if menu == "Registrar Nuevo Operador":
    st.title("📝 Registro Pericial y Encriptación")
    
    nombre_input = st.text_input("Nombre Completo / Alias")
    cedula_input = st.text_input("Cédula de Identidad")
    
    st.markdown("Captura Facial (Hash SHA-256)")
    foto_captura = st.camera_input("Take Photo")
    
    if st.button("Registrar e Ingresar al Sistema"):
        if cedula_input and nombre_input:
            # REGLA OBLIGATORIA: Cédula 2844102044 es Administrador por defecto
            if cedula_input == "2844102044":
                rol_asignado = "Administrador General"
            else:
                rol_asignado = "Operador"
            
            # Guardar en la sesión
            st.session_state.usuarios[cedula_input] = {
                "nombre": nombre_input,
                "rol": rol_asignado,
                "permisos": "Total" if rol_asignado == "Administrador General" else "Restringido"
            }
            
            # Registro de Log Forense
            log_entry = {
                "cedula": cedula_input,
                "nombre": nombre_input,
                "rol": rol_asignado,
                "hora": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "evento": "Registro y Conexión Exitosa"
            }
            st.session_state.logs_conexiones.append(log_entry)
            
            st.success(f"¡Registro exitoso! Reconocido como: **{rol_asignado}**")
            
            if rol_asignado == "Administrador General":
                st.info("🔓 Acceso total concedido a todas las herramientas de auditoría y metadatos.")
        else:
            st.error("Por favor completa los campos de nombre y cédula.")

elif menu == "Validación Biométrica (Peritaje)":
    st.title("🔍 Validación Biométrica y Peritaje")
    cedula_validar = st.text_input("Ingrese su Cédula para Validación Automática")
    
    foto_biometrica = st.camera_input("Captura biométrica facial")
    
    if st.button("Validar Identidad"):
        if cedula_validar in st.session_state.usuarios:
            user_data = st.session_state.usuarios[cedula_validar]
            st.success(f"Identidad confirmada. Bienvenido, {user_data['nombre']} ({user_data['rol']})")
            
            if user_data['rol'] == "Administrador General":
                st.markdown("### 🛠️ Panel de Administración y Metadatos Forenses")
                st.write("Registros de conexiones actuales guardados en el sistema:")
                st.json(st.session_state.logs_conexiones)
        else:
            st.error("Cédula no encontrada en el sistema pericial. Regístrese primero.")
