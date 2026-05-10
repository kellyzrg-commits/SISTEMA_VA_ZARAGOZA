import streamlit as st
import mysql.connector
from fpdf import FPDF
import pandas as pd
from datetime import datetime
import random

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="VA Zaragoza - Sistema Integral", layout="wide")

# CSS para igualar el diseño de tus capturas
st.markdown("""
    <style>
    .main-header {
        background-color: #1e3a8a;
        color: white;
        padding: 20px;
        border-radius: 12px;
        text-align: center;
        margin-bottom: 25px;
    }
    .category-box {
        background-color: #f8f9fa;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 10px;
        margin-bottom: 15px;
    }
    .canvas-bg {
        background-color: #ffffff;
        border: 3px dashed #cbd5e1;
        border-radius: 20px;
        height: 400px;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    .rect-preview {
        border: 5px solid #1e3a8a;
        background-color: rgba(30, 58, 138, 0.1);
        display: flex;
        align-items: center;
        justify-content: center;
        transition: 0.5s ease;
    }
    </style>
""", unsafe_allow_html=True)

# --- VARIABLES DE ESTADO ---
if 'prod_sel' not in st.session_state: st.session_state.prod_sel = None
if 'linea_sel' not in st.session_state: st.session_state.linea_sel = None

# --- MOTOR DE CÁLCULOS TÉCNICOS ---
def calcular_vaz_completo(prod, linea, anc, alt):
    # Precios base actualizados según tus capturas
    precios = {
        "Ventana Corrediza": {"2 Pulgadas": 1100, "3 Pulgadas": 1400},
        "Ventana Fija": {"2 Pulgadas": 950, "3 Pulgadas": 1200},
        "Puerta Pesada": {"2 Pulgadas": 1600, "3 Pulgadas": 1950},
        "Puerta Ligera": {"2 Pulgadas": 1300, "3 Pulgadas": 1550},
        "Mosquitero": {"Marco Fijo": 450, "Corredizo": 750},
        "Vidrio Templado": {"6mm": 1800, "10mm": 2800}
    }
    m2 = (anc * alt) / 1000000
    base = precios[prod].get(linea, 1000)
    return round((m2 * base) * 1.50, 2) # Incluye 50% mano de obra

# --- INTERFAZ ---
st.markdown('<div class="main-header"><h1>VIDRIOS Y ALUMINIOS ZARAGOZA</h1><p>Panel de Cotización Profesional</p></div>', unsafe_allow_html=True)

st.subheader("📁 Catálogo de Productos (Selecciona una categoría)")

# --- SECCIONES DESPLEGABLES (BASADAS EN TUS CAPTURAS) ---
c1, c2, c3 = st.columns(3)

with c1:
    with st.expander("🪟 VENTANAS", expanded=st.session_state.prod_sel in ["Ventana Corrediza", "Ventana Fija"]):
        st.write("**Selecciona el tipo:**")
        if st.button("Corrediza 2\"", key="v_c2"): 
            st.session_state.prod_sel, st.session_state.linea_sel = "Ventana Corrediza", "2 Pulgadas"
        if st.button("Corrediza 3\"", key="v_c3"): 
            st.session_state.prod_sel, st.session_state.linea_sel = "Ventana Corrediza", "3 Pulgadas"
        if st.button("Fija 2\"", key="v_f2"): 
            st.session_state.prod_sel, st.session_state.linea_sel = "Ventana Fija", "2 Pulgadas"
        if st.button("Fija 3\"", key="v_f3"): 
            st.session_state.prod_sel, st.session_state.linea_sel = "Ventana Fija", "3 Pulgadas"

with c2:
    with st.expander("🚪 PUERTAS", expanded=st.session_state.prod_sel in ["Puerta Pesada", "Puerta Ligera"]):
        st.write("**Selecciona la línea:**")
        if st.button("Línea Pesada 3\"", key="p_p3"): 
            st.session_state.prod_sel, st.session_state.linea_sel = "Puerta Pesada", "3 Pulgadas"
        if st.button("Línea Pesada 2\"", key="p_p2"): 
            st.session_state.prod_sel, st.session_state.linea_sel = "Puerta Pesada", "2 Pulgadas"
        if st.button("Línea Ligera", key="p_l"): 
            st.session_state.prod_sel, st.session_state.linea_sel = "Puerta Ligera", "2 Pulgadas"

with c3:
    with st.expander("🛡️ OTROS / ESPECIALES", expanded=st.session_state.prod_sel in ["Mosquitero", "Vidrio Templado"]):
        st.write("**Opciones adicionales:**")
        if st.button("Mosquitero Fijo", key="m_f"): 
            st.session_state.prod_sel, st.session_state.linea_sel = "Mosquitero", "Marco Fijo"
        if st.button("Mosquitero Corredizo", key="m_c"): 
            st.session_state.prod_sel, st.session_state.linea_sel = "Mosquitero", "Corredizo"
        if st.button("Templado 6mm", key="t6"): 
            st.session_state.prod_sel, st.session_state.linea_sel = "Vidrio Templado", "6mm"
        if st.button("Templado 10mm", key="t10"): 
            st.session_state.prod_sel, st.session_state.linea_sel = "Vidrio Templado", "10mm"

st.divider()

# --- CALCULADORA DINÁMICA ---
if st.session_state.prod_sel:
    st.info(f"⚙️ Configurando: **{st.session_state.prod_sel}** | **{st.session_state.linea_sel}**")
    
    col_f, col_v = st.columns([1, 1.2])
    
    with col_f:
        with st.container(border=True):
            cliente = st.text_input("Nombre del Cliente")
            ancho = st.number_input("Ancho (mm)", min_value=100, value=1200, step=10)
            alto = st.number_input("Alto (mm)", min_value=100, value=1500, step=10)
            
            total_final = calcular_vaz_completo(st.session_state.prod_sel, st.session_state.linea_sel, ancho, alto)
            
            st.markdown(f"""
                <div style="background-color:#1e3a8a; color:white; padding:20px; border-radius:10px; text-align:center;">
                    <p style="margin:0; font-size:14px; opacity:0.8;">PRECIO ESTIMADO NETO</p>
                    <h1 style="margin:0; color:white;">${total_final:,.2f}</h1>
                </div>
            """, unsafe_allow_html=True)
            
            if st.button("📝 Generar e Imprimir Cotización"):
                if cliente:
                    st.success(f"Cotización generada para {cliente}")
                else:
                    st.warning("Por favor, ingresa el nombre del cliente.")

    with col_v:
        # Lógica de escala para la ilustración dinámica
        escala = 350 / max(ancho, alto)
        w_px, h_px = ancho * escala, alto * escala
        
        st.markdown(f"""
            <div class="canvas-bg">
                <div class="rect-preview" style="width:{w_px}px; height:{h_px}px;">
                    <b style="color:#1e3a8a; font-size:18px;">{ancho} x {alto} mm</b>
                </div>
            </div>
        """, unsafe_allow_html=True)
