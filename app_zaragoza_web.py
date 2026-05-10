import streamlit as st
import mysql.connector
from fpdf import FPDF
import pandas as pd
from datetime import datetime
import random

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="VA Zaragoza - Cotizador", layout="wide")

# CSS para igualar el diseño de "secciones" de tus capturas
st.markdown("""
    <style>
    .vaz-header {
        background-color: #1e3a8a;
        color: white;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        margin-bottom: 30px;
    }
    .stExpander {
        border: 1px solid #1e3a8a;
        border-radius: 10px;
        background-color: #f8f9fa;
        margin-bottom: 10px;
    }
    .stButton>button {
        background-color: white;
        color: #1e3a8a;
        border: 1px solid #1e3a8a;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background-color: #1e3a8a;
        color: white;
    }
    .preview-container {
        background-color: white;
        border: 2px dashed #cbd5e1;
        border-radius: 20px;
        height: 400px;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    .rect-blue {
        border: 5px solid #1e3a8a;
        background-color: rgba(30, 58, 138, 0.05);
        display: flex;
        align-items: center;
        justify-content: center;
    }
    </style>
""", unsafe_allow_html=True)

# --- ESTADOS ---
if 'sel' not in st.session_state: st.session_state.sel = {"prod": None, "sub": None}

# --- CÁLCULO ---
def calcular(p, s, a, h):
    precios = {
        "Ventanas": {"Corrediza 2\"": 1100, "Corrediza 3\"": 1400, "Fija 2\"": 900, "Fija 3\"": 1150},
        "Puertas": {"Pesada 3\"": 1900, "Pesada 2\"": 1600, "Ligera 2\"": 1300},
        "Otros": {"Mosquitero Fijo": 450, "Mosquitero Corredizo": 750, "Templado 6mm": 1800, "Templado 10mm": 2600}
    }
    m2 = (a * h) / 1000000
    costo = m2 * precios[p].get(s, 1000)
    return round(costo * 1.5, 2)

# --- UI ---
st.markdown('<div class="vaz-header"><h1>SISTEMA DE COTIZACIONES VA ZARAGOZA</h1></div>', unsafe_allow_html=True)

st.write("### 📂 Catálogo de Productos")
c1, c2, c3 = st.columns(3)

# SECCIÓN: VENTANAS
with c1:
    with st.expander("🪟 VENTANAS", expanded=st.session_state.sel["prod"] == "Ventanas"):
        if st.button("Corrediza 2\"", use_container_width=True): st.session_state.sel = {"prod": "Ventanas", "sub": "Corrediza 2\""}
        if st.button("Corrediza 3\"", use_container_width=True): st.session_state.sel = {"prod": "Ventanas", "sub": "Corrediza 3\""}
        if st.button("Fija 2\"", use_container_width=True): st.session_state.sel = {"prod": "Ventanas", "sub": "Fija 2\""}
        if st.button("Fija 3\"", use_container_width=True): st.session_state.sel = {"prod": "Ventanas", "sub": "Fija 3\""}

# SECCIÓN: PUERTAS
with c2:
    with st.expander("🚪 PUERTAS", expanded=st.session_state.sel["prod"] == "Puertas"):
        if st.button("Línea Pesada 3\"", use_container_width=True): st.session_state.sel = {"prod": "Puertas", "sub": "Pesada 3\""}
        if st.button("Línea Pesada 2\"", use_container_width=True): st.session_state.sel = {"prod": "Puertas", "sub": "Pesada 2\""}
        if st.button("Línea Ligera", use_container_width=True): st.session_state.sel = {"prod": "Puertas", "sub": "Ligera 2\""}

# SECCIÓN: OTROS
with c3:
    with st.expander("🛠️ OTROS", expanded=st.session_state.sel["prod"] == "Otros"):
        if st.button("Mosquitero Fijo", use_container_width=True): st.session_state.sel = {"prod": "Otros", "sub": "Mosquitero Fijo"}
        if st.button("Mosquitero Corredizo", use_container_width=True): st.session_state.sel = {"prod": "Otros", "sub": "Mosquitero Corredizo"}
        if st.button("Vidrio Templado 6mm", use_container_width=True): st.session_state.sel = {"prod": "Otros", "sub": "Templado 6mm"}
        if st.button("Vidrio Templado 10mm", use_container_width=True): st.session_state.sel = {"prod": "Otros", "sub": "Templado 10mm"}

st.divider()

# CALCULADORA
if st.session_state.sel["prod"]:
    st.subheader(f"⚙️ Ajustando: {st.session_state.sel['sub']}")
    izq, der = st.columns([1, 1.2])
    
    with izq:
        with st.container(border=True):
            cliente = st.text_input("Cliente")
            ancho = st.number_input("Ancho (mm)", min_value=100, value=1000, step=10)
            alto = st.number_input("Alto (mm)", min_value=100, value=1000, step=10)
            
            total = calcular(st.session_state.sel["prod"], st.session_state.sel["sub"], ancho, alto)
            
            st.markdown(f"""
                <div style="background:#1e3a8a; color:white; padding:15px; border-radius:10px; text-align:center;">
                    <p style="margin:0;">TOTAL ESTIMADO</p>
                    <h2 style="margin:0;">${total:,.2f} MXN</h2>
                </div>
            """, unsafe_allow_html=True)
            
            if st.button("💾 Guardar"):
                st.success(f"Guardado exitoso para {cliente}")

    with der:
        # Ilustración ajustable
        scale = 300 / max(ancho, alto)
        w, h = ancho * scale, alto * scale
        st.markdown(f"""
            <div class="preview-container">
                <div class="rect-blue" style="width:{w}px; height:{h}px;">
                    <b style="color:#1e3a8a;">{ancho}x{alto}</b>
                </div>
            </div>
        """, unsafe_allow_html=True)
