import streamlit as st
import mysql.connector
from fpdf import FPDF
import pandas as pd
from datetime import datetime
import random

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="VA Zaragoza - Panel de Control", layout="wide")

# --- CSS PERSONALIZADO ---
st.markdown("""
    <style>
    [data-testid="stSidebar"] {
        background-color: #1e3a8a;
        color: white;
    }
    .st-emotion-cache-10o099s { color: white !important; }
    .price-card {
        background-color: #1e3a8a;
        color: white;
        padding: 25px;
        border-radius: 15px;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .canvas-bg {
        background-color: white;
        border: 4px solid #1e3a8a;
        border-radius: 10px;
        height: 350px;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    </style>
""", unsafe_allow_html=True)

# --- MENÚ LATERAL (SIDEBAR) ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3233/3233483.png", width=100) # Logo genérico
    st.title("Menú VAZ")
    
    opcion_principal = st.selectbox(
        "📂 Categoría Principal",
        ["Ventanas", "Puertas", "Mosquiteros", "Vidrios Especiales", "Historial"]
    )
    
    st.divider()
    
    # SUBCATEGORÍAS DINÁMICAS (Lógica de "Hojas" y "Líneas")
    sub_opcion = None
    if opcion_principal == "Ventanas":
        st.subheader("⚙️ Configuración de Hoja")
        sub_opcion = st.radio("Tipo de Hoja:", ["Hoja Corrediza", "Hoja Fija", "Hoja Traslapo", "Hoja Cabezal"])
        linea = st.selectbox("Línea:", ["2 Pulgadas", "3 Pulgadas", "Eurovent"])
        
    elif opcion_principal == "Puertas":
        st.subheader("🚪 Estilo de Puerta")
        sub_opcion = st.radio("Línea:", ["Línea Pesada", "Línea Ligera", "Multi-panel"])
        linea = st.selectbox("Espesor:", ["2 Pulgadas", "3 Pulgadas"])
        
    elif opcion_principal == "Mosquiteros":
        sub_opcion = st.radio("Modelo:", ["Marco Fijo", "Corredizo Tradicional"])
        linea = "Nacional"

# --- LÓGICA DE CÁLCULO ---
def calcular_presupuesto(cat, sub, lin, anc, alt):
    m2 = (anc * alt) / 1000000
    base = 1200 # Precio base promedio
    if "3 Pulgadas" in lin: base += 300
    if "Eurovent" in lin: base += 800
    return round((m2 * base) * 1.5, 2)

# --- CONTENIDO PRINCIPAL ---
if opcion_principal != "Historial":
    st.header(f"✨ Cotizador: {opcion_principal}")
    st.caption(f"Configuración activa: {sub_opcion} | {linea if 'linea' in locals() else ''}")

    col_form, col_vis = st.columns([1, 1.2])

    with col_form:
        with st.container(border=True):
            cliente = st.text_input("Nombre del Cliente")
            c1, c2 = st.columns(2)
            ancho = c1.number_input("Ancho (mm)", value=1200, step=10)
            alto = c2.number_input("Alto (mm)", value=1500, step=10)
            
            total = calcular_presupuesto(opcion_principal, sub_opcion, linea if 'linea' in locals() else '', ancho, alto)
            
            st.markdown(f"""
                <div class="price-card">
                    <p style="margin:0; opacity:0.8;">COSTO TOTAL NETO</p>
                    <h1 style="margin:0; font-size:45px;">${total:,.2f}</h1>
                    <p style="margin:0; font-size:12px;">Incluye material y mano de obra</p>
                </div>
            """, unsafe_allow_html=True)
            
            if st.button("📝 Generar Cotización PDF", use_container_width=True):
                st.success(f"Documento listo para {cliente}")

    with col_vis:
        st.subheader("📐 Vista Previa de Estructura")
        # Escala dinámica para la ilustración
        max_dim = max(ancho, alto)
        scale = 300 / max_dim
        w_px, h_px = ancho * scale, alto * scale
        
        st.markdown(f"""
            <div class="canvas-bg">
                <div style="width:{w_px}px; height:{h_px}px; border:5px solid #1e3a8a; background:rgba(30,58,138,0.1); display:flex; align-items:center; justify-content:center;">
                    <b style="color:#1e3a8a;">{ancho} x {alto}</b>
                </div>
            </div>
        """, unsafe_allow_html=True)

else:
    st.header("📋 Historial de Presupuestos")
    # Simulación de tabla de base de datos
    df_fake = pd.DataFrame({
        "Folio": ["VAZ-001", "VAZ-002"],
        "Cliente": ["Juan Pérez", "María García"],
        "Total": ["$2,450.00", "$5,120.00"],
        "Fecha": ["2026-05-09", "2026-05-10"]
    })
    st.table(df_fake)
