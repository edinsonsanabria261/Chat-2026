import streamlit as st

# Configuración inicial del layout táctico
st.markdown("""
    <style>
    .tactical-header { background-color: #0e1117; padding: 10px; border-radius: 8px; border: 1px solid #262730; }
    </style>
""", unsafe_allow_html=True)

# Menú superior desplegable estilo selector táctico
with st.container():
    st.markdown("### 🎛️ Centro de Control Táctico - Red Team")
    
    # Menú desplegable solicitado con flecha para selección rápida
    menu_opcion = st.selectbox(
        "Menú de Acceso Rápido (Seleccione acción o contacto):",
        ["💬 Mensajería General", "📞 Llamada de Voz P2P Directa", "📹 Videollamada Táctica con Operador", "👥 Lista de Contactos / Cédulas", "⚙️ Configuración y Seguridad"],
        index=0
    )

if "Videollamada" in menu_opcion:
    st.subheader("🌐 Módulo de Videollamadas y Llamadas P2P")
    
    # Simulación de lista de contactos activos extraídos de Firebase/Base de datos
    contactos_activos = {
        "Operador Alpha (Edinson Marín)": "Sala-Edinson-P2P",
        "Unidad Táctica 01": "Sala-Tactica-01",
        "Unidad Táctica 02": "Sala-Tactica-02",
        "Personal de Campo / Cédula V-...": "Sala-Campo-Secure"
    }
    
    tipo_llamada = st.radio("Seleccione el canal de comunicación:", ["Videollamada WebRTC HD", "Llamada de Voz IP P2P", "Enlace Externo / Celular"])
    
    if tipo_llamada != "Enlace Externo / Celular":
        contacto_seleccionado = st.selectbox("Elija al operador o destino:", list(contactos_activos.keys()))
        room_id = contactos_activos[contacto_seleccionado]
        st.info(f"Conectando directamente con: **{contacto_seleccionado}** (ID de Canal: `{room_id}`)")
        
        if st.button("🚀 Iniciar Conexión P2P"):
            st.success(Link de transmisión seguro establecido para {contacto_seleccionado}. Cero operadoras telefónicas.)
            # Aquí se renderiza el componente iframe o WebRTC correspondiente
    else:
        numero_destino = st.text_input("Ingrese número celular o contacto externo:")
        if st.button("📞 Marcar vía Red Celular"):
            st.markdown(f'<meta http-equiv="refresh" content="0;url=tel:{numero_destino}">', unsafe_allow_html=True)

elif "Mensajería" in menu_opcion:
    st.subheader("💬 Canal General Táctico & P2P")
    st.write("Sincronización en tiempo real mediante Firebase. En línea.")
    # Sección de notas de voz y chat ya funcional en tus capturas
    mensaje_usuario = st.text_input("Escribe un mensaje instantáneo...")
    if st.button("Enviar"):
        st.toast("Mensaje enviado al canal seguro.")

elif "Contactos" in menu_opcion:
    st.subheader("👥 Directorio de Operadores y Cédulas")
    st.info("Gestión de accesos, permisos de red team y estados de operadores.")
    # Listado de control de personal
