import streamlit as st
import mysql.connector
from fpdf import FPDF
import pandas as pd
from datetime import datetime
import random

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="VA Zaragoza - Catálogo Pro", layout="wide")

# CSS para el diseño de tarjetas y submenús
st.markdown("""
    <style>
    .main-card {
        background-color: #1e3a8a;
        color: white;
        padding: 20px;
        border-radius: 12px;
        text-align: center;
        font-weight: bold;
        margin-bottom: 10px;
    }
    .sub-button-container {
        background-color: #f1f5f9;
        padding: 10px;
        border-radius: 0 0 12px 12px;
        border: 1px solid #e2e8f0;
        margin-top: -10px;
        margin-bottom: 20px;
    }
    .canvas-container {
        background-color: #ffffff;
        border: 2px dashed #cbd5e1;
        border-radius: 15px;
        display: flex;
        align-items: center;
        justify-content: center;
        height: 350px;
        position: relative;
    }
    .rect-vaz {
        border: 5px solid #1e3a8a;
        background-color: rgba(30, 58, 138, 0.05);
        display: flex;
        align-items: center;
        justify-content: center;
        transition: all 0.4s ease;
    }
    </style>
""", unsafe_allow_html=True)

# --- MOTOR DE CÁLCULO ---
def calcular_total(prod, sub, anc, alt):
    precios = {
        "Ventana": {"2 Pulgadas": 1100, "3 Pulgadas": 1400},
        "Puerta": {"2 Pulgadas": 1550, "3 Pulgadas": 1850},
        "Mosquitero": {"Fijo": 400, "Corredizo": 700}
    }
    m2 = (anc * alt) / 1000000
    base = precios[prod].get(sub, 1000)
    return round((m2 * base) * 1.50, 2)

# --- VARIABLES DE ESTADO ---
if 'menu_abierto' not in st.session_state: st.session_state.menu_abierto = None
if 'sub_elegido' not in st.session_state: st.session_state.sub_elegido = None

st.title("🏢 Catálogo Interactivo VA Zaragoza")

# --- SECCIÓN 1: MENÚ CON SUB-CATEGORÍAS ---
col1, col2, col3 = st.columns(3)

# VENTANAS
with col1:
    st.markdown('<div class="main-card">🪟 VENTANAS</div>', unsafe_allow_html=True)
    if st.button("Ver opciones de Ventana", use_container_width=True):
        st.session_state.menu_abierto = "Ventana"
    
    if st.session_state.menu_abierto == "Ventana":
        with st.container():
            st.markdown('<div class="sub-button-container">', unsafe_allow_html=True)
            if st.button("Línea 2\"", key="v2"): st.session_state.sub_elegido = ("Ventana", "2 Pulgadas")
            if st.button("Línea 3\"", key="v3"): st.session_state.sub_elegido = ("Ventana", "3 Pulgadas")
            st.markdown('</div>', unsafe_allow_html=True)

# PUERTAS
with col2:
    st.markdown('<div class="main-card">🚪 PUERTAS</div>', unsafe_allow_html=True)
    if st.button("Ver opciones de Puerta", use_container_width=True):
        st.session_state.menu_abierto = "Puerta"
    
    if st.session_state.menu_abierto == "Puerta":
        with st.container():
            st.markdown('<div class="sub-button-container">', unsafe_allow_html=True)
            if st.button("Línea 2\"", key="p2"): st.session_state.sub_elegido = ("Puerta", "2 Pulgadas")
            if st.button("Línea 3\"", key="p3"): st.session_state.sub_elegido = ("Puerta", "3 Pulgadas")
            st.markdown('</div>', unsafe_allow_html=True)

# MOSQUITEROS
with col3:
    st.markdown('<div class="main-card">🦟 MOSQUITEROS</div>', unsafe_allow_html=True)
    if st.button("Ver opciones de Mosquitero", use_container_width=True):
        st.session_state.menu_abierto = "Mosquitero"
    
    if st.session_state.menu_abierto == "Mosquitero":
        with st.container():
            st.markdown('<div class="sub-button-container">', unsafe_allow_html=True)
            if st.button("Tipo Fijo", key="mf"): st.session_state.sub_elegido = ("Mosquitero", "Fijo")
            if st.button("Tipo Corredizo", key="mc"): st.session_state.sub_elegido = ("Mosquitero", "Corredizo")
            st.markdown('</div>', unsafe_allow_html=True)

st.divider()

# --- SECCIÓN 2: CALCULADORA E ILUSTRACIÓN ---
if st.session_state.sub_elegido:
    prod, sub = st.session_state.sub_elegido
    st.subheader(f"Cotizando: {prod} - {sub}")
    
    c_izq, c_der = st.columns([1, 1.2])
    
    with c_izq:
        with st.form("calc_vaz"):
            cliente = st.text_input("Nombre del Cliente")
            ancho = st.number_input("Ancho (mm)", value=1000, step=50)
            alto = st.number_input("Alto (mm)", value=1200, step=50)
            
            res = calcular_total(prod, sub, ancho, alto)
            st.markdown(f"<h2 style='color:#1e3a8a;'>Total: ${res:,.2f}</h2>", unsafe_allow_html=True)
            
            if st.form_submit_button("💾 Guardar Presupuesto"):
                st.success(f"¡Listo! Folio VAZ-{random.randint(100,999)} creado.")

    with c_der:
        # Lógica de dibujo ajustable
        max_d = max(ancho, alto)
        scale = 280 / max_d
        w_px, h_px = ancho * scale, alto * scale
        
        st.markdown(f"""
            <div class="canvas-container">
                <div class="rect-vaz" style="width:{w_px}px; height:{h_px}px;">
                    <b style="color:#1e3a8a;">{ancho}x{alto}</b>
                </div>
            </div>
        """, unsafe_allow_html=True)
