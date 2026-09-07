import streamlit as st
import json
import os
import hashlib
import urllib.parse

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="Nexus-Sec | Portal de Autenticación",
    page_icon="🛡️",
    layout="centered"
)

# --- ESTILOS CSS AVANZADOS ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    :root {
        --bg-deep: #050b14;
        --modal-bg: #0b1329;
        --accent-cyan: #06b6d4;
        --accent-glow: rgba(6, 182, 212, 0.25);
        --text-main: #f8fafc;
        --text-muted: #94a3b8;
    }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    body { background-color: var(--bg-deep); font-family: 'Inter', sans-serif; }
    .stApp { background: radial-gradient(circle at 50% 50%, #0a192f 0%, #050b14 100%); }
    .stTextInput input {
        background-color: rgba(15, 23, 42, 0.6) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        color: var(--text-main) !important;
        border-radius: 8px !important;
        padding: 10px !important;
    }
    .stTextInput input:focus {
        border-color: var(--accent-cyan) !important;
        box-shadow: 0 0 0 2px var(--accent-glow) !important;
    }
    .stButton button {
        width: 100%;
        border-radius: 8px !important;
        font-weight: 500 !important;
        font-size: 0.9rem !important;
        padding: 10px !important;
        transition: all 0.3s ease !important;
    }
</style>
""", unsafe_allow_html=True)

# --- BASE DE DATOS LOCAL Y HASHING ---
DB_FILE = "nexus_users_vault.json"

def cargar_base_datos():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def guardar_base_datos(db):
    with open(DB_FILE, "w") as f:
        json.dump(db, f, indent=4)

def hashear_password(password):
    return hashlib.sha256(password.encode('utf-8')).hexdigest()
