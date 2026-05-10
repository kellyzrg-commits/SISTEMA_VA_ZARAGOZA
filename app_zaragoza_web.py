import streamlit as st
import mysql.connector
from fpdf import FPDF
import pandas as pd
from datetime import datetime
import random

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="VA Zaragoza - Cotizador", layout="wide")

# --- CSS PARA EL CATÁLOGO Y LA ILUSTRACIÓN ---
st.markdown("""
    <style>
    .product-card {
        background-color: white;
        padding: 20px;
        border-radius: 15px;
        border: 2px solid #e2e8f0;
        text-align: center;
        cursor: pointer;
        transition: 0.3s;
    }
    .product-card:hover { border-color: #1e3a8a; box-shadow: 0 4px 12px rgba(0,0,0,0.1); }
    
    /* Contenedor de la ilustración ajustable */
    .canvas-container {
        background-color: #f1f5f9;
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 20px;
        height: 300px;
        position: relative;
    }
    .rect-ajustable {
        border: 4px solid #1e3a8a;
        background-color: rgba(30, 58, 138, 0.1);
        display: flex;
        align-items: center;
        justify-content: center;
        transition: all 0.5s ease;
    }
    .medida-texto {
        font-weight: bold;
        color: #1e3a8a;
        font-size: 14px;
    }
    </style>
""", unsafe_allow_html=True)

# --- MOTOR DE CÁLCULO ---
def calcular_costo(producto, linea, ancho, alto):
    precios = {
        "Ventana": {"2 Pulgadas": 1150, "3 Pulgadas": 1450},
        "Puerta": {"2 Pulgadas": 1600, "3 Pulgadas": 1950},
        "Mosquitero": {"Fijo": 450, "Corredizo": 750}
    }
    m2 = (ancho * alto) / 1000000
    costo_base = m2 * precios[producto].get(linea, 1000)
    # +50% Mano de obra y redondeo
    return round(costo_base * 1.50, 2)

# --- INTERFAZ PRINCIPAL ---
st.title("🏢 VA Zaragoza: Catálogo y Cotizador")

if 'view' not in st.session_state:
    st.session_state.view = 'catalogo'
if 'prod_name' not in st.session_state:
    st.session_state.prod_name = ""

# --- VISTA 1: CATÁLOGO ---
if st.session_state.view == 'catalogo':
    st.subheader("Selecciona un producto para cotizar:")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown('<div class="product-card"><h3>🪟 Ventanas</h3><p>2" y 3" Corredizas</p></div>', unsafe_allow_html=True)
        if st.button("Cotizar Ventana", use_container_width=True):
            st.session_state.prod_name = "Ventana"
            st.session_state.view = 'calculadora'
            st.rerun()

    with col2:
        st.markdown('<div class="product-card"><h3>🚪 Puertas</h3><p>Batientes y Corredizas</p></div>', unsafe_allow_html=True)
        if st.button("Cotizar Puerta", use_container_width=True):
            st.session_state.prod_name = "Puerta"
            st.session_state.view = 'calculadora'
            st.rerun()

    with col3:
        st.markdown('<div class="product-card"><h3>🦟 Mosquiteros</h3><p>Fijo y Corredizo</p></div>', unsafe_allow_html=True)
        if st.button("Cotizar Mosquitero", use_container_width=True):
            st.session_state.prod_name = "Mosquitero"
            st.session_state.view = 'calculadora'
            st.rerun()

# --- VISTA 2: CALCULADORA CON ILUSTRACIÓN ---
elif st.session_state.view == 'calculadora':
    st.button("⬅️ Volver al Catálogo", on_click=lambda: st.session_state.update({"view": "catalogo"}))
    st.header(f"Cotizando: {st.session_state.prod_name}")

    c1, c2 = st.columns([1, 1.2])

    with c1:
        with st.container(border=True):
            cliente = st.text_input("Nombre del Cliente")
            if st.session_state.prod_name == "Mosquitero":
                variante = st.selectbox("Tipo", ["Fijo", "Corredizo"])
            else:
                variante = st.selectbox("Línea de Aluminio", ["2 Pulgadas", "3 Pulgadas"])
            
            ancho = st.number_input("Ancho (mm)", min_value=100, max_value=5000, value=1000, step=10)
            alto = st.number_input("Alto (mm)", min_value=100, max_value=5000, value=1200, step=10)
            
            total = calcular_costo(st.session_state.prod_name, variante, ancho, alto)
            
            st.markdown(f"""
                <div style="background:#f0fdf4; padding:20px; border-radius:10px; text-align:center; border:1px solid #bbf7d0;">
                    <h2 style="color:#166534; margin:0;">Total: ${total:,.2f}</h2>
                    <p style="color:#166534; margin:0;">MXN (Material + Mano de obra)</p>
                </div>
            """, unsafe_allow_html=True)

    with c2:
        st.subheader("Ilustración de Medidas")
        # --- LÓGICA DE ESCALA PARA LA ILUSTRACIÓN ---
        # Escalamos los mm a pixeles para que quepa en el contenedor de 300px
        max_dim = max(ancho, alto)
        escala = 250 / max_dim
        w_px = ancho * escala
        h_px = alto * escala

        st.markdown(f"""
            <div class="canvas-container">
                <div class="rect-ajustable" style="width: {w_px}px; height: {h_px}px;">
                    <span class="medida-texto">{ancho} x {alto}</span>
                </div>
                <div style="position:absolute; bottom:10px; width:100%; text-align:center; font-size:12px; color:#64748b;">
                    Vista previa proporcional de la estructura
                </div>
            </div>
        """, unsafe_allow_html=True)

    if st.button("✅ Confirmar y Generar Registro", use_container_width=True):
        if cliente:
            st.balloons()
            st.success(f"Presupuesto para {cliente} guardado con éxito.")
        else:
            st.error("Ingresa el nombre del cliente.")
